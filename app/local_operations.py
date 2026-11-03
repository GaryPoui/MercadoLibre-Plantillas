"""Actionable local alerts, audit and prepared notices. No mail is sent."""
import json
import re
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime

from openpyxl.utils import get_column_letter

from .engine import export_review
from .local_core import LocalCore, key
from .local_inventory import LocalInventory
from .store import Conflict, now


class LocalOperations(LocalCore):
    def refresh_alerts(self):
        with self.store.connect(write=True) as db:
            observations = []
            def observe(kind, resource, message, evidence, **context):
                if context.get("lot_id"):
                    lot = self.get(db, "lot", context["lot_id"])
                    product = self.get(db, "product", lot["product_id"])
                    location = self.get(db, "location", lot["location_id"])
                    message = f"{product['sku']} / {location['name']}: "+message
                    if location["account_id"]:
                        context["account_id"] = location["account_id"]
                if context.get("account_id"):
                    message = self.get(db, "account", context["account_id"])["name"]+": "+message
                observations.append({"kind": kind, "resource_id": resource, "message": message,
                                     "severity": "error" if kind.startswith("price_") or kind == "inventory_difference" else "warning",
                                     "fingerprint": key(evidence), **context})
            for raw, in db.execute("SELECT payload FROM records WHERE kind='supplier_scope'"):
                scope = json.loads(raw)
                if scope["current_version_id"]:
                    version = self.store._get(db, "supplier_version", scope["current_version_id"])
                    pending = version["summary"]["pending"]
                    if pending:
                        observe("supplier_pending", scope["id"], f"Lista vigente con {pending} filas pendientes: {scope['name']}.", version["id"], scope_id=scope["id"])
            inventory = LocalInventory(self.store)
            for lot in self.records(db, "lot"):
                totals = inventory.totals(db, lot)
                if lot["kind"] == "full" and totals["on_hand"] is None:
                    observe("full_unknown", lot["id"], "Full sin observación registrada; cantidad desconocida.", lot["revision"], lot_id=lot["id"])
                if lot["minimum"] is not None and totals["on_hand"] is not None:
                    available = max(0, totals["on_hand"]-totals["reserved"]-(lot["safety"] or 0))
                    if available <= lot["minimum"]:
                        observe("stock_minimum", lot["id"], f"Cantidad disponible {available}, mínimo declarado {lot['minimum']} ({lot['unit']}).",
                                [lot["revision"], available, lot["minimum"]], lot_id=lot["id"], product_id=lot["product_id"])
            seen = set()
            for record in self.records(db, "reconciliation"):
                if record["lot_id"] in seen:
                    continue
                seen.add(record["lot_id"])
                if record["difference"] != 0:
                    observe("inventory_difference", record["lot_id"], "Último conteo con diferencia o base desconocida; requiere revisar y volver a conciliar.", record["id"], lot_id=record["lot_id"])
            for job in self.records(db, "price_job"):
                if job["status"] in {"failed", "uncertain", "conflict", "blocked"}:
                    observe("price_"+job["status"], job["id"], "Propuesta de precios local requiere atención: "+job["status"]+". No hay verificación remota.",
                            job["revision"], account_id=job["account_id"])
            active = set()
            for observation in observations:
                ident = "ops-alert-"+key(observation["kind"], observation["resource_id"])
                active.add(ident)
                old = self.find(db, "alert", ident)
                if old is None:
                    self.put(db, "alert", {**observation, "status": "open", "first_seen": now(), "last_seen": now(),
                        "occurrences": 1, "cycle": 1, "source": "local_evidence"}, ident)
                elif old["fingerprint"] != observation["fingerprint"] or old["status"] == "resolved":
                    reopened = old["status"] == "resolved"
                    self.save(db, {**old, **observation, "status": "open" if reopened else old["status"],
                        "occurrences": old["occurrences"]+1, "cycle": old["cycle"]+int(reopened), "last_seen": now()})
            for old in self.records(db, "alert"):
                if old["id"] not in active and old["status"] != "resolved":
                    row = self.save(db, {**old, "status": "resolved", "resolved_at": now()})
                    self.audit(db, "local_alert_resolved", row)

    def acknowledge(self, ident):
        self.refresh_alerts()
        with self.store.connect(write=True) as db:
            row = self.get(db, "alert", ident)
            if row["status"] == "resolved":
                return row
            if row["status"] != "acknowledged":
                row = self.save(db, {**row, "status": "acknowledged"})
                self.audit(db, "local_alert_acknowledged", row)
            return row

    def prepare_notice(self, ident, recipient):
        if len(recipient) > 200 or not re.fullmatch(r"[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+", recipient):
            raise ValueError("Indicá un destinatario de correo válido, sin saltos de línea.")
        with self.store.connect(write=True) as db:
            alert = self.get(db, "alert", ident)
            notice_id = "ops-notice-"+key(ident, alert["cycle"], recipient.casefold())
            old = self.find(db, "notice", notice_id)
            if old:
                return old
            row = self.put(db, "notice", {"alert_id": ident, "cycle": alert["cycle"], "recipient": recipient,
                "message": alert["message"], "status": "prepared_not_sent", "sent": False, "source": "local_preparation"}, notice_id)
            self.audit(db, "notice_prepared_not_sent", row)
            return row

    def notice_bytes(self, ident):
        with self.store.connect() as db:
            row = self.get(db, "notice", ident)
        mail = EmailMessage()
        mail["To"] = row["recipient"]
        mail["Subject"] = "Aviso preparado: alerta de Mesa de listas"
        mail["Date"] = format_datetime(datetime.fromisoformat(row["created_at"]))
        mail.set_content("Aviso local preparado, NO enviado por el sistema.\n\n"+row["message"]+"\n\nOrigen: evidencia local; sin conexión a Mercado Libre.\n")
        return mail.as_bytes()

    def state(self):
        self.refresh_alerts()
        with self.store.connect() as db:
            db.execute("BEGIN")
            kinds = ("account", "product", "listing", "product_link", "supplier_link", "price_rule", "price_preview", "price_job",
                     "location", "lot", "allocation", "order", "movement", "full_capture", "reconciliation", "alert", "notice")
            data = {kind: self.records(db, kind) for kind in kinds}
            inventory = LocalInventory(self.store)
            data["lot"] = [{**lot, **inventory.totals(db, lot)} for lot in data["lot"]]
            data["inventory_policy"] = self.find(db, "inventory_policy", "ops-inventory-policy")
            return {**data, "mode": "local", "remote_enabled": False, "mail_transport_enabled": False, "captured_at": now()}

    def audit_rows(self, *, action="", resource="", account_id="", status="", since=None, until=None, before=None, limit=100):
        conditions, params = [], []
        if action:
            conditions.append("a.action LIKE ?")
            params.append("%"+action+"%")
        if resource:
            conditions.append("a.resource_id=?")
            params.append(resource)
        if account_id:
            conditions.append("json_extract(c.payload,'$.account_id')=?")
            params.append(account_id)
        if status:
            conditions.append("json_extract(c.payload,'$.status')=?")
            params.append(status)
        for operator, date in ((">=", since), ("<=", until)):
            if date:
                parsed = datetime.fromisoformat(date.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError("La fecha de auditoría necesita zona horaria.")
                conditions.append("a.at"+operator+"?")
                from datetime import timezone
                params.append(parsed.astimezone(timezone.utc).isoformat())
        if before is not None:
            conditions.append("a.id<?")
            params.append(before)
        where = " WHERE "+" AND ".join(conditions) if conditions else ""
        with self.store.connect() as db:
            records = db.execute("SELECT a.id,a.action,a.resource_id,a.at,c.payload FROM audit a LEFT JOIN records c ON c.id='ops-audit-'||a.id"+where+" ORDER BY a.id DESC LIMIT ?", (*params, limit)).fetchall()
        rows = [{"id": r[0], "action": r[1], "resource_id": r[2], "at": r[3], "context": json.loads(r[4]) if r[4] else {}} for r in records]
        return {"rows": rows, "next_cursor": rows[-1]["id"] if len(rows) == limit else None}

    def export(self):
        snapshot = self.state()
        headings = ["Área", "Recurso", "Estado", "Cantidad o precio", "Origen", "Cuenta", "Fecha", "Detalle"]
        entries = []
        for lot in snapshot["lot"]:
            entries.append(["Inventario "+lot["kind"], lot["id"], "observado_no_verificado" if lot["kind"] == "full" else "local",
                lot["on_hand"], lot["source"], "", lot["observed_at"], f"Unidad {lot['unit']}; reservado {lot['reserved']}; asignado {lot['allocated']}; libre {lot['available']}"])
        for order in snapshot["order"]:
            entries.append(["Venta local", order["id"], order["status"], order["quantity"], order["source"], order["account_id"], order.get("updated_at", order["created_at"]), order["order_ref"]])
        for job in snapshot["price_job"]:
            for entry in job["rows"]:
                entries.append(["Precio simulado", job["id"], entry["status"], entry["proposed_price"], job["source"], job["account_id"], job.get("updated_at", job["created_at"]), " | ".join(entry["reasons"])])
        for preview in snapshot["price_preview"]:
            for entry in preview["rows"]:
                entries.append(["Propuesta local histórica", preview["id"], entry["status"], entry["proposed_price"], preview["source"], preview["account_id"], preview["created_at"],
                    f"Versión proveedor {preview['supplier_version_id']}; captura destino revisión {entry['expected_revision']}. Revalidar antes de simular. "+" | ".join(entry["reasons"])])
        for alert in snapshot["alert"]:
            entries.append(["Alerta", alert["id"], alert["status"], alert["occurrences"], alert["source"], alert.get("account_id", ""), alert["last_seen"], alert["message"]])
        rows = [{"row_number": 1, "kind": "header", "status": "usable", "issues": [],
                 "values": {get_column_letter(i): v for i, v in enumerate(headings, 1)}}]
        for number, values in enumerate(entries, 2):
            rows.append({"row_number": number, "kind": "product", "status": "usable", "issues": [],
                         "values": {get_column_letter(i): v for i, v in enumerate(values, 1)}})
        return export_review({"sheet": "Estado local "+snapshot["captured_at"], "rows": rows, "config": {"data_start": 2}})
