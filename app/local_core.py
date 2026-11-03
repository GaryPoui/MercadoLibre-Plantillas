"""Shared persistence for local operations. This module has no network capability."""
import hashlib
import json
from decimal import Decimal, InvalidOperation

from .engine import _scalar
from .store import Conflict, uid, now
from .suppliers import Missing


def key(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def text(value, label="dato", limit=200):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"Completá {label} (hasta {limit} caracteres).")
    return _scalar(value.strip())


def amount(value):
    try:
        if isinstance(value, bool):
            raise ValueError
        result = Decimal(str(value))
        if not result.is_finite() or result < 0 or result > Decimal('1e20'):
            raise ValueError
        return result
    except (ValueError, InvalidOperation):
        raise ValueError("Ingresá un importe decimal no negativo, sin símbolo ni separador de miles.")


def integer(value, *, negative=False):
    if type(value) is not int or abs(value) > 10**9 or (value < 0 and not negative):
        raise ValueError("Ingresá una cantidad entera válida en la unidad declarada.")
    return value


class LocalCore:
    def __init__(self, store):
        self.store = store

    def get(self, db, kind, ident):
        row = self.store._get(db, "ops_"+kind, ident)
        if row is None:
            raise Missing("No se encontró el registro local.")
        return row

    def records(self, db, kind):
        return [json.loads(row[0]) for row in db.execute(
            "SELECT payload FROM records WHERE kind=? ORDER BY rowid DESC", ("ops_"+kind,))]

    def find(self, db, kind, ident):
        return self.store._get(db, "ops_"+kind, ident)

    def put(self, db, kind, values, ident=None):
        row = {**values, "id": ident or uid(), "revision": 1, "created_at": now()}
        self.store._put(db, "ops_"+kind, row)
        return row

    def save(self, db, row):
        row = {**row, "revision": row["revision"]+1, "updated_at": now()}
        db.execute("UPDATE records SET payload=? WHERE id=?",
                   (json.dumps(row, ensure_ascii=False, allow_nan=False), row["id"]))
        return row

    def expected(self, row, revision):
        if row["revision"] != revision:
            raise Conflict("El registro cambió; actualizá la pantalla antes de continuar.")

    def audit(self, db, action, row):
        at = now()
        cursor = db.execute("INSERT INTO audit(action,resource_id,at) VALUES(?,?,?)", (action, row["id"], at))
        context = {k: row[k] for k in ("account_id", "product_id", "location_id", "lot_id", "scope_id", "status") if k in row}
        self.put(db, "audit_context", {**context, "audit_id": cursor.lastrowid}, "ops-audit-"+str(cursor.lastrowid))

    def account(self, db, ident):
        row = self.get(db, "account", ident)
        if not row["active"]:
            raise Conflict("La referencia de cuenta local está desactivada.")
        return row

    def idempotent(self, db, namespace, ident, payload):
        event_id = "ops-event-"+key(namespace, ident)
        prior = self.find(db, "event", event_id)
        if prior and prior["fingerprint"] != key(payload):
            raise Conflict("La clave del evento ya se usó con otros datos.")
        return event_id, prior

    def event(self, db, ident, payload, result):
        self.put(db, "event", {"fingerprint": key(payload), "result": result}, ident)
        return result
