"""Explicit local supplier identities and immutable, reviewed price-list versions."""
from collections import defaultdict
from copy import deepcopy
from decimal import Decimal

from .standardize import consolidate, export_standardized, FIELDS
from .store import Conflict, uid, now
from .engine import _scalar


class Missing(ValueError):
    pass


def normalized(value):
    return " ".join(value.casefold().split())


def summary(rows):
    ready = sum(r["status"] == "ready" for r in rows)
    return {"total": len(rows), "ready": ready, "pending": len(rows)-ready,
            "unreviewed_imports": 0}


def grouped(rows):
    groups = defaultdict(list)
    for r in rows:
        key = ("sku", r["sku"]) if r["sku"] else ("missing", r["review_id"], r["row_number"])
        groups[key].append(r)
    return groups


def merge_rows(previous, incoming, mode):
    old, new = grouped(previous), grouped(incoming)
    rows, differences = [], []
    for key in dict.fromkeys([*new, *old]):
        before, after = old.get(key, []), new.get(key, [])
        certified = [r for r in before if r.get("price_certified")]
        # A retained certified price remains authoritative through later bad uploads;
        # ambiguous candidates must never displace it or become the fallback themselves.
        prior = certified[0] if len(certified) == 1 else before[0] if len(before) == 1 else None
        candidate = after[0] if len(after) == 1 else None
        if not after:
            kind = "absent"
            for entry in before:
                kept = deepcopy(entry)
                kept.update(status="pending", update_state="not_updated_partial" if mode == "partial" else "absent")
                warning = "No actualizado por lista parcial." if mode == "partial" else "Ausente en lista completa; conservado para revisión."
                kept["issues"] = list(dict.fromkeys([*kept["issues"], warning]))
                rows.append(kept)
        elif len(after) > 1:
            kind = "ambiguous"
            for entry in after:
                entry = deepcopy(entry)
                entry.update(status="pending", update_state="ambiguous", price_certified=False)
                rows.append(entry)
            if prior and prior.get("price_certified"):
                kept = deepcopy(prior)
                kept.update(status="pending", update_state="previous_price")
                kept["issues"] = [*kept["issues"], "Se conserva precio anterior: alternativas nuevas ambiguas."]
                rows.append(kept)
        elif candidate["status"] != "ready":
            kind = "invalid"
            if prior and prior.get("price_certified"):
                kept = deepcopy(prior)
                kept.update(status="pending", update_state="not_updated_invalid",
                            attempted_review_id=candidate["review_id"])
                kept["issues"] = list(dict.fromkeys([*candidate["issues"], "Precio anterior conservado; la fila nueva necesita revisión."]))
                rows.append(kept)
            else:
                entry = deepcopy(candidate)
                entry.update(update_state="invalid", price_certified=False)
                rows.append(entry)
        else:
            if not before:
                kind = "added"
            elif prior and prior.get("price_certified"):
                kind = "unchanged" if Decimal(str(prior["price"])) == Decimal(str(candidate["price"])) else "changed"
            else:
                kind = "changed"
            entry = deepcopy(candidate)
            entry.update(update_state=kind, price_certified=True)
            rows.append(entry)
        differences.append({"sku": (after or before)[0]["sku"], "kind": kind,
                            "previous_price": prior["price"] if prior else None,
                            "proposed_price": candidate["price"] if candidate else None,
                            "previous_rows": deepcopy(before), "candidate_rows": deepcopy(after)})
    return rows, differences


class Suppliers:
    def __init__(self, store):
        self.store = store

    def get(self, db, kind, ident):
        record = self.store._get(db, kind, ident)
        if record is None:
            raise Missing("No se encontró el registro de proveedor o lista.")
        return record

    def all(self, db, kind):
        import json
        return [json.loads(r[0]) for r in db.execute(
            "SELECT payload FROM records WHERE kind=? ORDER BY rowid DESC", (kind,))]

    def update(self, db, record):
        import json
        db.execute("UPDATE records SET payload=? WHERE id=?",
                   (json.dumps(record, ensure_ascii=False, allow_nan=False), record["id"]))

    def audit(self, db, action, ident):
        db.execute("INSERT INTO audit(action,resource_id,at) VALUES(?,?,?)", (action, ident, now()))

    def list(self):
        with self.store.connect() as db:
            db.execute("BEGIN")
            suppliers = self.all(db, "supplier")
            scopes = self.all(db, "supplier_scope")
            for supplier in suppliers:
                supplier["scopes"] = [s for s in scopes if s["supplier_id"] == supplier["id"]]
                for scope in supplier["scopes"]:
                    version = self.get(db, "supplier_version", scope["current_version_id"]) if scope["current_version_id"] else None
                    scope["current_summary"] = version["summary"] if version else None
            return suppliers

    def save_supplier(self, payload, ident=None):
        name = payload["name"].strip()
        aliases = list(dict.fromkeys(a.strip() for a in payload["aliases"] if a.strip()))
        if not name:
            raise ValueError("Indicá un nombre de proveedor.")
        for text in [name, *aliases]:
            _scalar(text)
            if len(text) > 100:
                raise ValueError("Los nombres y alias admiten hasta 100 caracteres.")
        with self.store.connect(write=True) as db:
            previous = self.get(db, "supplier", ident) if ident else None
            if previous and previous["revision"] != payload["expected_revision"]:
                raise Conflict("El proveedor cambió; recargá antes de guardar.")
            if previous and previous["name"] != name:
                aliases = list(dict.fromkeys([*aliases, previous["name"]]))
            if len(aliases) > 30:
                raise ValueError("Conservá hasta 30 alias por proveedor.")
            names = {normalized(n) for n in [name, *aliases]}
            for other in self.all(db, "supplier"):
                if other["id"] != ident and names.intersection(normalized(n) for n in [other["name"], *other["aliases"]]):
                    raise Conflict("El nombre o alias ya identifica a otro proveedor.")
            record = {"id": ident or uid(), "name": name, "aliases": aliases,
                      "retired": payload["retired"], "revision": previous["revision"]+1 if previous else 1,
                      "created_at": previous["created_at"] if previous else now(), "updated_at": now()}
            if previous:
                self.update(db, record)
            else:
                self.store._put(db, "supplier", record)
            self.audit(db, "supplier_saved", record["id"])
            return record

    def save_scope(self, supplier_id, payload, ident=None):
        name, currency, meaning = payload["name"].strip(), payload["currency"].strip().upper(), payload["price_kind"].strip()
        if not name:
            raise ValueError("Indicá un nombre para el alcance de la lista.")
        for text in (name, currency, meaning):
            _scalar(text)
        with self.store.connect(write=True) as db:
            supplier = self.get(db, "supplier", supplier_id)
            if supplier["retired"]:
                raise Conflict("El proveedor está retirado.")
            previous = self.get(db, "supplier_scope", ident) if ident else None
            if previous and (previous["supplier_id"] != supplier_id or previous["revision"] != payload["expected_revision"]):
                raise Conflict("El alcance cambió; recargá antes de guardar.")
            if previous and previous["current_version_id"] and (previous["currency"] != currency or previous["price_kind"] != meaning):
                raise Conflict("La moneda y significado de una lista activada son inmutables; creá otro alcance.")
            if any(s["id"] != ident and s["supplier_id"] == supplier_id and normalized(s["name"]) == normalized(name)
                   for s in self.all(db, "supplier_scope")):
                raise Conflict("El proveedor ya tiene un alcance con ese nombre.")
            record = {"id": ident or uid(), "supplier_id": supplier_id, "name": name,
                      "currency": currency, "price_kind": meaning, "current_version_id": previous["current_version_id"] if previous else None,
                      "revision": previous["revision"]+1 if previous else 1}
            if previous:
                self.update(db, record)
            else:
                self.store._put(db, "supplier_scope", record)
            self.audit(db, "scope_saved", record["id"])
            return record

    def validate_source(self, db, scope, supplier, review):
        source = self.get(db, "import", review["import_id"])
        binding = self.store._get(db, "supplier_binding", "binding-"+source["id"])
        if binding and (binding["supplier_id"] != supplier["id"] or binding["scope_id"] != scope["id"]):
            raise Conflict("El archivo ya está asociado a otro proveedor o alcance.")
        raw = str(review["config"].get("supplier") or "").strip()
        if not binding and raw and normalized(raw) not in {normalized(s) for s in [supplier["name"], *supplier["aliases"]]}:
            raise Conflict("La revisión identifica otro proveedor; confirmá un alias o corregí su proveedor.")
        return source

    def sources(self, scope_id):
        with self.store.connect() as db:
            db.execute("BEGIN")
            scope = self.get(db, "supplier_scope", scope_id)
            supplier = self.get(db, "supplier", scope["supplier_id"])
            result, seen = [], set()
            for review in self.all(db, "review"):
                key = (review["import_id"], review["sheet"])
                if key in seen:
                    continue
                seen.add(key)
                if review["config"].get("sheet_kind") == "operational":
                    continue
                try:
                    source = self.validate_source(db, scope, supplier, review)
                except Conflict:
                    continue
                result.append({"id": review["id"], "import_id": review["import_id"], "filename": source["filename"],
                               "sheet": review["sheet"], "created_at": review["created_at"], "summary": review["summary"]})
            return result

    def preview(self, scope_id, review_ids, mode):
        with self.store.connect(write=True) as db:
            scope = self.get(db, "supplier_scope", scope_id)
            supplier = self.get(db, "supplier", scope["supplier_id"])
            if supplier["retired"]:
                raise Conflict("El proveedor está retirado.")
            sources, seen = [], set()
            for ident in review_ids:
                review = self.get(db, "review", ident)
                key = (review["import_id"], review["sheet"])
                if key in seen:
                    raise ValueError("Elegí solo una revisión por archivo y hoja.")
                seen.add(key)
                if review["config"].get("sheet_kind") == "operational":
                    raise ValueError("Las hojas operativas no forman parte de una lista de productos.")
                source = self.validate_source(db, scope, supplier, review)
                copy = deepcopy(review)
                copy["config"]["supplier"] = supplier["name"]
                sources.append((source, copy))
            incoming = consolidate(sources)["rows"]
            for row in incoming:
                row.update(supplier_id=supplier["id"], scope_id=scope["id"], scope=scope["name"],
                           currency=scope["currency"], price_kind=scope["price_kind"])
            previous = self.get(db, "supplier_version", scope["current_version_id"]) if scope["current_version_id"] else None
            rows, differences = merge_rows(previous["rows"] if previous else [], incoming, mode)
            return self._save_preview(db, scope, supplier, rows, differences, review_ids, mode)

    def _save_preview(self, db, scope, supplier, rows, differences, review_ids, mode, restore_of=None):
        blockers = []
        if not scope["currency"] or not scope["price_kind"]:
            blockers.append("Completá moneda y significado del precio del alcance antes de activar.")
        if not any(row.get("price_certified") for row in rows):
            blockers.append("La lista necesita al menos un producto con SKU y precio certificados.")
        preview = {"id": uid(), "scope_id": scope["id"], "supplier_id": supplier["id"],
                   "supplier_revision": supplier["revision"], "scope_revision": scope["revision"],
                   "parent_id": scope["current_version_id"], "supplier_name": supplier["name"],
                   "currency": scope["currency"], "price_kind": scope["price_kind"], "scope": scope["name"],
                   "rows": rows, "differences": differences, "review_ids": review_ids, "mode": mode,
                   "can_activate": not blockers, "blockers": blockers, "summary": summary(rows),
                   "created_at": now(), "restore_of": restore_of}
        self.store._put(db, "supplier_preview", preview)
        return preview

    def activate(self, preview_id):
        with self.store.connect(write=True) as db:
            preview = self.get(db, "supplier_preview", preview_id)
            scope = self.get(db, "supplier_scope", preview["scope_id"])
            supplier = self.get(db, "supplier", scope["supplier_id"])
            if supplier["retired"] or supplier["revision"] != preview["supplier_revision"] or scope["revision"] != preview["scope_revision"] or scope["current_version_id"] != preview["parent_id"]:
                raise Conflict("La lista vigente o el proveedor cambió; generá una vista previa nueva.")
            if not preview["can_activate"]:
                raise Conflict("La vista previa tiene bloqueos; corregí los datos antes de activar.")
            for review_id in preview["review_ids"]:
                review = self.get(db, "review", review_id)
                source = self.validate_source(db, scope, supplier, review)
                ident = "binding-"+source["id"]
                if not self.store._get(db, "supplier_binding", ident):
                    self.store._put(db, "supplier_binding", {"id": ident, "supplier_id": supplier["id"], "scope_id": scope["id"]})
            version = {**deepcopy(preview), "id": uid(), "preview_id": preview["id"],
                       "created_at": now(), "author": "operador_local"}
            self.store._put(db, "supplier_version", version)
            scope.update(current_version_id=version["id"], revision=scope["revision"]+1)
            self.update(db, scope)
            self.audit(db, "supplier_list_restored" if preview["restore_of"] else "supplier_list_activated", version["id"])
            return version

    def restore_preview(self, version_id):
        with self.store.connect(write=True) as db:
            target = self.get(db, "supplier_version", version_id)
            scope = self.get(db, "supplier_scope", target["scope_id"])
            supplier = self.get(db, "supplier", scope["supplier_id"])
            if supplier["retired"]:
                raise Conflict("El proveedor está retirado.")
            current = self.get(db, "supplier_version", scope["current_version_id"])
            _, differences = merge_rows(current["rows"], target["rows"], "complete")
            return self._save_preview(db, scope, supplier, deepcopy(target["rows"]), differences,
                                      target["review_ids"], target["mode"], target["id"])

    def versions(self, scope_id):
        with self.store.connect() as db:
            self.get(db, "supplier_scope", scope_id)
            return [{k: v[k] for k in ("id", "scope_id", "parent_id", "created_at", "summary", "mode", "restore_of", "author")}
                    for v in self.all(db, "supplier_version") if v["scope_id"] == scope_id]

    def current(self):
        with self.store.connect() as db:
            db.execute("BEGIN")
            rows = []
            for scope in self.all(db, "supplier_scope"):
                if scope["current_version_id"]:
                    version = self.get(db, "supplier_version", scope["current_version_id"])
                    rows.extend({**r, "version_id": version["id"]} for r in version["rows"])
            return {"rows": rows, "summary": summary(rows), "source": "current_supplier_lists"}


def export_version(version):
    fields = [*FIELDS, ("currency", "Moneda declarada"), ("price_kind", "Significado del precio"),
              ("scope", "Alcance"), ("update_state", "Actualización"),
              ("attempted_review_id", "Revisión nueva pendiente")]
    return export_standardized(version, fields=fields)
