"""Local catalog identities and explicitly confirmed links; no OAuth claims."""
from .local_core import LocalCore, key, text, amount
from .store import Conflict
from .suppliers import Missing


class LocalCatalog(LocalCore):
    def save_account(self, payload):
        name = text(payload["name"], "nombre de cuenta local", 100)
        with self.store.connect(write=True) as db:
            previous = self.get(db, "account", payload["id"]) if payload.get("id") else None
            if previous:
                self.expected(previous, payload.get("expected_revision"))
            if any(a["name"].casefold() == name.casefold() and a["id"] != payload.get("id") for a in self.records(db, "account")):
                raise Conflict("Ya existe una referencia local con ese nombre.")
            values = {"name": name, "active": payload["active"], "source": "local_reference", "remote_connected": False}
            row = self.save(db, {**previous, **values}) if previous else self.put(db, "account", values)
            self.audit(db, "local_account_saved", row)
            return row

    def create_product(self, payload):
        values = {"sku": text(payload["sku"], "SKU interno"), "name": text(payload["name"], "nombre de producto"),
                  "unit": text(payload["unit"], "unidad indivisible", 60)}
        with self.store.connect(write=True) as db:
            if any(p["sku"] == values["sku"] for p in self.records(db, "product")):
                raise Conflict("Ese SKU interno ya existe; usá su identidad existente.")
            row = self.put(db, "product", values)
            self.audit(db, "local_product_created", row)
            return row

    def save_listing(self, payload):
        with self.store.connect(write=True) as db:
            self.account(db, payload["account_id"])
            listing_id = text(payload["listing_id"], "referencia de publicación", 100)
            ident = "ops-listing-"+key(payload["account_id"], listing_id, payload["variation_id"])
            previous = self.find(db, "listing", ident)
            if previous:
                self.expected(previous, payload.get("expected_revision"))
            elif payload.get("expected_revision") is not None:
                raise Conflict("La identidad de la captura cambió. Creá una referencia nueva explícitamente.")
            values = {k: payload[k] for k in ("account_id", "variation_id", "user_product_id", "currency", "price_kind", "logistics", "simulated_editable")}
            values.update(listing_id=listing_id, price=str(amount(payload["price"])),
                          currency=text(payload["currency"], "moneda", 3).upper(),
                          price_kind=text(payload["price_kind"], "significado del precio", 100),
                          source="manual_snapshot", remote_capability="unknown", last_job_id=None)
            row = self.save(db, {**previous, **values}) if previous else self.put(db, "listing", values, ident)
            self.put(db, "listing_snapshot", {"listing": row, "complete": True, "source": "manual_snapshot"})
            self.audit(db, "local_listing_captured", row)
            return row

    def link(self, payload, *, supplier=False):
        with self.store.connect(write=True) as db:
            product = self.get(db, "product", payload["product_id"])
            if supplier:
                scope = self.store._get(db, "supplier_scope", payload["scope_id"])
                if scope is None or not scope["current_version_id"]:
                    raise Missing("Activá primero una lista vigente del proveedor.")
                version = self.store._get(db, "supplier_version", scope["current_version_id"])
                sku = text(payload["supplier_sku"], "SKU del proveedor")
                if not any(r["sku"] == sku for r in version["rows"]):
                    raise Conflict("El SKU no pertenece a la lista vigente elegida.")
                kind, ident = "supplier_link", "ops-supplier-link-"+key(scope["id"], sku)
                values = {"scope_id": scope["id"], "supplier_sku": sku, "product_id": product["id"], "active": True}
                if any(r["active"] and r["product_id"] == product["id"] and r["scope_id"] == scope["id"] and r["id"] != ident for r in self.records(db, kind)):
                    raise Conflict("El producto ya tiene otro SKU en ese alcance; retiralo explícitamente antes de cambiarlo.")
            else:
                listing = self.get(db, "listing", payload["listing_record_id"])
                self.account(db, listing["account_id"])
                kind, ident = "product_link", "ops-product-link-"+key(listing["id"])
                values = {"listing_record_id": listing["id"], "account_id": listing["account_id"], "product_id": product["id"], "active": True}
            previous = self.find(db, kind, ident)
            if previous:
                self.expected(previous, payload.get("expected_revision"))
                self.put(db, "link_history", {"kind": kind, "previous": previous})
            row = self.save(db, {**previous, **values}) if previous else self.put(db, kind, values, ident)
            self.audit(db, "local_link_confirmed", row)
            return row

    def retire_link(self, kind, ident, expected_revision):
        with self.store.connect(write=True) as db:
            row = self.get(db, kind, ident)
            self.expected(row, expected_revision)
            self.put(db, "link_history", {"kind": kind, "previous": row})
            row = self.save(db, {**row, "active": False})
            self.audit(db, "local_link_retired", row)
            return row
