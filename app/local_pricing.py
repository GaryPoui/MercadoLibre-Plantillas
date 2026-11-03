"""Versioned local price proposals and fault-controlled simulation, never remote IO."""
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP, localcontext

from .local_core import LocalCore, amount, text, key
from .store import Conflict, now
from .suppliers import Missing


class LocalPricing(LocalCore):
    def rule(self, payload):
        if payload["confirmed"] is not True:
            raise ValueError("Confirmá explícitamente el significado comercial de la regla.")
        with self.store.connect(write=True) as db:
            self.account(db, payload["account_id"])
            scope = self.store._get(db, "supplier_scope", payload["scope_id"])
            if scope is None:
                raise Missing("No existe el alcance de proveedor.")
            ident = "ops-price-rule-"+key(payload["account_id"], scope["id"])
            previous = self.find(db, "price_rule", ident)
            if previous:
                self.expected(previous, payload.get("expected_revision"))
            values = {"account_id": payload["account_id"], "scope_id": scope["id"],
                      "factor": str(amount(payload["factor"])), "charge": str(amount(payload["charge"])),
                      "digits": payload["digits"], "rounding": "ROUND_HALF_UP",
                      "target_price_kind": text(payload["target_price_kind"], "significado del precio de destino", 100),
                      "confirmed": True, "source": "operator_confirmed"}
            version = self.put(db, "price_rule_version", values)
            values["version_id"] = version["id"]
            row = self.save(db, {**previous, **values}) if previous else self.put(db, "price_rule", values, ident)
            self.audit(db, "price_rule_confirmed", row)
            return row

    def preview(self, payload):
        with self.store.connect(write=True) as db:
            self.account(db, payload["account_id"])
            scope = self.store._get(db, "supplier_scope", payload["scope_id"])
            if scope is None or not scope["current_version_id"]:
                raise Missing("Activá una lista vigente antes de preparar precios.")
            supplier = self.store._get(db, "supplier", scope["supplier_id"])
            if supplier["retired"]:
                raise Conflict("El proveedor está retirado.")
            version = self.store._get(db, "supplier_version", scope["current_version_id"])
            rule = self.find(db, "price_rule", "ops-price-rule-"+key(payload["account_id"], scope["id"]))
            links = self.records(db, "product_link")
            sources = self.records(db, "supplier_link")
            rows = []
            for listing in self.records(db, "listing"):
                if listing["account_id"] != payload["account_id"]:
                    continue
                reasons, proposed, product_link, source_link = [], None, None, None
                candidates = [r for r in links if r["active"] and r["listing_record_id"] == listing["id"]]
                if len(candidates) != 1:
                    reasons.append("Publicación sin vínculo inequívoco a producto interno.")
                else:
                    product_link = candidates[0]
                    matches = [r for r in sources if r["active"] and r["scope_id"] == scope["id"] and r["product_id"] == product_link["product_id"]]
                    if len(matches) != 1:
                        reasons.append("Sin SKU inequívoco en el alcance del proveedor.")
                    else:
                        source_link = matches[0]
                        values = [r for r in version["rows"] if r["sku"] == source_link["supplier_sku"]]
                        if len(values) != 1 or values[0]["status"] != "ready":
                            reasons.append("SKU ausente, pendiente o ambiguo en la versión vigente.")
                        elif rule:
                            with localcontext() as context:
                                context.prec = 60
                                target = amount(values[0]["price"])*amount(rule["factor"])+amount(rule["charge"])
                                target = amount(target).quantize(Decimal(1).scaleb(-rule["digits"]), rounding=ROUND_HALF_UP)
                            proposed = str(target)
                if not rule:
                    reasons.append("Falta una regla comercial confirmada explícitamente.")
                elif listing["price_kind"] != rule["target_price_kind"]:
                    reasons.append("El significado del precio de destino no coincide con la regla.")
                if not scope["currency"] or listing["currency"] != scope["currency"]:
                    reasons.append("Moneda distinta o desconocida; no se convierte automáticamente.")
                if not listing["simulated_editable"]:
                    reasons.append("La captura no habilita edición en el simulador.")
                rows.append({"listing_id": listing["id"], "listing_ref": listing["listing_id"],
                             "variation_id": listing["variation_id"], "expected_revision": listing["revision"],
                             "previous_price": listing["price"], "proposed_price": proposed,
                             "product_link": product_link, "supplier_link": source_link,
                             "status": "blocked" if reasons else "unchanged" if amount(listing["price"]) == amount(proposed) else "ready",
                             "reasons": reasons})
            row = self.put(db, "price_preview", {"account_id": payload["account_id"], "scope_id": scope["id"],
                "supplier_version_id": version["id"], "rule": rule, "rows": rows,
                "source": "local_simulator", "remote_verified": False})
            self.audit(db, "price_preview_prepared", row)
            return row

    def _valid(self, db, preview):
        scope = self.store._get(db, "supplier_scope", preview["scope_id"])
        supplier = self.store._get(db, "supplier", scope["supplier_id"]) if scope else None
        current = self.find(db, "price_rule", preview["rule"]["id"]) if preview["rule"] else None
        account = self.get(db, "account", preview["account_id"])
        return (account["active"] and scope and supplier and not supplier["retired"]
                and scope["current_version_id"] == preview["supplier_version_id"]
                and current and current["version_id"] == preview["rule"]["version_id"])

    def _run(self, db, job, scenario):
        preview = self.get(db, "price_preview", job["preview_id"])
        job["attempts"].append({"number": len(job["attempts"])+1, "scenario": scenario, "at": now()})
        valid = self._valid(db, preview)
        for row in job["rows"]:
            if row["status"] not in {"ready", "failed", "uncertain"}:
                continue
            listing = self.get(db, "listing", row["listing_id"])
            links_ok = all(link and (current := self.find(db, kind, link["id"])) and current["active"] and current["revision"] == link["revision"]
                           for kind, link in (("product_link", row["product_link"]), ("supplier_link", row["supplier_link"])))
            if not valid or not links_ok or not listing["simulated_editable"]:
                row.update(status="conflict", reasons=["Cambió cuenta, vínculo, regla o versión vigente. Prepará otra comparación."])
                continue
            if row["status"] == "uncertain" and listing["last_job_id"] == job["id"] and listing["revision"] == row["expected_revision"]+1 and amount(listing["price"]) == amount(row["proposed_price"]):
                row.update(status="simulated_verified", reasons=["Resultado comprobado en captura simulada antes de reintentar; no se volvió a aplicar."])
                continue
            if listing["revision"] != row["expected_revision"] or amount(listing["price"]) != amount(row["previous_price"]):
                row.update(status="conflict", reasons=["La captura de destino cambió después de la comparación."])
                continue
            if scenario in {"reject", "timeout_before"}:
                row.update(status="failed", reasons=["Fallo transitorio simulado; no se cambió la captura."])
                continue
            if scenario == "accepted_unchanged":
                row.update(status="uncertain", reasons=["Respuesta aceptada simulada sin cambio comprobado."])
                continue
            listing = self.save(db, {**listing, "price": row["proposed_price"], "last_job_id": job["id"], "source": "simulated_capture"})
            self.put(db, "listing_snapshot", {"listing": listing, "complete": True, "source": "simulated_capture"})
            if scenario == "timeout_after":
                row.update(status="uncertain", reasons=["Timeout simulado después del cambio; requiere reconciliar antes de repetir."])
            elif amount(self.get(db, "listing", listing["id"])["price"]) == amount(row["proposed_price"]):
                row.update(status="simulated_verified", reasons=["Precio comprobado únicamente en simulación local."])
        states = {r["status"] for r in job["rows"]}
        job["status"] = next((s for s in ("conflict", "uncertain", "failed") if s in states),
                             "simulated" if "simulated_verified" in states else "no_changes" if "unchanged" in states else "blocked")
        job["remote_verified"] = False
        result = self.save(db, job)
        self.audit(db, "price_simulation_attempt", result)
        return result

    def simulate(self, ident, scenario, confirmed):
        if not confirmed:
            raise ValueError("Confirmá que querés ejecutar solamente una simulación local.")
        with self.store.connect(write=True) as db:
            preview = self.get(db, "price_preview", ident)
            job_id = "ops-price-job-"+key(ident)
            previous = self.find(db, "price_job", job_id)
            if previous:
                if previous["status"] == "cancelled":
                    raise Conflict("La propuesta fue cancelada.")
                return previous
            job = self.put(db, "price_job", {"preview_id": ident, "account_id": preview["account_id"],
                "scope_id": preview["scope_id"], "rows": deepcopy(preview["rows"]), "attempts": [],
                "status": "prepared", "source": "local_simulator", "remote_verified": False}, job_id)
            return self._run(db, job, scenario)

    def retry(self, ident, scenario):
        with self.store.connect(write=True) as db:
            job = self.get(db, "price_job", ident)
            if job["status"] not in {"failed", "uncertain"} or len(job["attempts"]) >= 3:
                raise Conflict("Solo se reintentan fallos o resultados inciertos, hasta tres intentos. Los conflictos exigen otra propuesta.")
            return self._run(db, job, scenario)

    def cancel(self, preview_id):
        with self.store.connect(write=True) as db:
            preview = self.get(db, "price_preview", preview_id)
            ident = "ops-price-job-"+key(preview_id)
            previous = self.find(db, "price_job", ident)
            if previous and previous["attempts"]:
                raise Conflict("Ya hubo intentos: conservá el resultado y prepará otra propuesta; no se borra lo enviado al simulador.")
            if previous:
                return previous
            row = self.put(db, "price_job", {"preview_id": preview_id, "account_id": preview["account_id"],
                "scope_id": preview["scope_id"], "rows": deepcopy(preview["rows"]), "attempts": [],
                "status": "cancelled", "source": "local_simulator", "remote_verified": False}, ident)
            self.audit(db, "price_proposal_cancelled", row)
            return row
