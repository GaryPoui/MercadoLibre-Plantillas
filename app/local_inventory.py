"""Transactional own inventory; observed Full snapshots are never adjusted by sales."""
from .local_core import LocalCore, key, text, integer
from .store import Conflict


class LocalInventory(LocalCore):
    def location(self, payload):
        with self.store.connect(write=True) as db:
            name = text(payload["name"], "nombre de ubicación", 100)
            if any(r["name"].casefold() == name.casefold() for r in self.records(db, "location")):
                raise Conflict("Ya existe esa ubicación.")
            if payload["kind"] == "full":
                self.account(db, payload["account_id"])
            elif payload["account_id"]:
                raise ValueError("Un depósito propio compartido no pertenece exclusivamente a una cuenta.")
            row = self.put(db, "location", {"name": name, "kind": payload["kind"], "account_id": payload["account_id"]})
            self.audit(db, "inventory_location_created", row)
            return row

    def totals(self, db, lot):
        if lot["kind"] == "full":
            capture = self.get(db, "full_capture", lot["capture_id"]) if lot["capture_id"] else None
            return {"on_hand": capture["quantity"] if capture else None, "reserved": 0, "allocated": 0,
                    "available": capture["quantity"] if capture else None, "source": "manual_full_observation",
                    "observed_at": capture["created_at"] if capture else None}
        reserved = sum(o["quantity"] for o in self.records(db, "order") if o["lot_id"] == lot["id"] and o["status"] == "reserved")
        allocated = sum(a["quantity"] for a in self.records(db, "allocation") if a["lot_id"] == lot["id"])
        return {"on_hand": lot["on_hand"], "reserved": reserved, "allocated": allocated,
                "available": max(0, lot["on_hand"]-lot["safety"]-reserved-allocated),
                "source": "local_own_ledger", "observed_at": lot.get("updated_at", lot["created_at"])}

    def check(self, db, lot):
        if lot["kind"] == "full":
            raise Conflict("Full es observado: no admite ajustes, reservas ni asignaciones propias.")
        totals = self.totals(db, lot)
        if lot["on_hand"] < 0 or totals["reserved"]+totals["allocated"] > max(0, lot["on_hand"]-lot["safety"]):
            raise Conflict("El movimiento superaría la existencia disponible menos margen y reservas/asignaciones.")

    def movement(self, db, lot, delta, reason, event_ref, reserved_delta=0):
        return self.put(db, "movement", {"lot_id": lot["id"], "product_id": lot["product_id"],
            "location_id": lot["location_id"], "delta": delta, "reserved_delta": reserved_delta,
            "reason": reason, "event_ref": event_ref, "source": "local_own_ledger"})

    def lot(self, payload):
        with self.store.connect(write=True) as db:
            product = self.get(db, "product", payload["product_id"])
            location = self.get(db, "location", payload["location_id"])
            ident = "ops-lot-"+key(product["id"], location["id"])
            if self.find(db, "lot", ident):
                raise Conflict("Esa existencia ya está representada; usá ajustes y no la dupliques.")
            if location["kind"] == "own":
                quantity, safety = integer(payload["initial_quantity"]), integer(payload["safety"])
            else:
                if payload["initial_quantity"] is not None or payload["safety"] is not None:
                    raise ValueError("Para Full cargá una observación separada; no existe cantidad propia inicial ni margen propio.")
                quantity, safety = None, None
            minimum = integer(payload["minimum"]) if payload["minimum"] is not None else None
            row = self.put(db, "lot", {"product_id": product["id"], "location_id": location["id"],
                "kind": location["kind"], "unit": product["unit"], "on_hand": quantity,
                "safety": safety, "minimum": minimum, "capture_id": None}, ident)
            if row["kind"] == "own":
                self.movement(db, row, quantity, "Conteo inicial declarado por operador", row["id"])
            self.audit(db, "inventory_lot_created", row)
            return row

    def settings(self, ident, payload):
        with self.store.connect(write=True) as db:
            row = self.get(db, "lot", ident)
            self.expected(row, payload["expected_revision"])
            row["minimum"] = integer(payload["minimum"]) if payload["minimum"] is not None else None
            if row["kind"] == "own":
                row["safety"] = integer(payload["safety"])
                self.check(db, row)
            elif payload["safety"] is not None:
                raise Conflict("Full no usa margen propio.")
            row = self.save(db, row)
            self.audit(db, "inventory_settings_changed", row)
            return row

    def adjustment(self, payload):
        with self.store.connect(write=True) as db:
            event_id, prior = self.idempotent(db, "adjustment", (payload["lot_id"], payload["event_id"]), payload)
            if prior:
                return prior["result"]
            lot = self.get(db, "lot", payload["lot_id"])
            self.expected(lot, payload["expected_revision"])
            if lot["kind"] != "own":
                raise Conflict("No se ajusta Full desde inventario propio.")
            lot["on_hand"] += integer(payload["delta"], negative=True)
            self.check(db, lot)
            row = self.save(db, lot)
            move = self.movement(db, row, payload["delta"], text(payload["reason"], "motivo del ajuste", 500), payload["event_id"])
            self.audit(db, "inventory_adjusted", move)
            return self.event(db, event_id, payload, row)

    def allocation(self, payload):
        with self.store.connect(write=True) as db:
            self.account(db, payload["account_id"])
            lot = self.get(db, "lot", payload["lot_id"])
            if lot["kind"] != "own":
                raise Conflict("Full no admite asignaciones propias.")
            ident = "ops-allocation-"+key(lot["id"], payload["account_id"])
            previous = self.find(db, "allocation", ident)
            if previous:
                self.expected(previous, payload.get("expected_revision"))
            values = {"lot_id": lot["id"], "account_id": payload["account_id"], "quantity": integer(payload["quantity"])}
            row = self.save(db, {**previous, **values}) if previous else self.put(db, "allocation", values, ident)
            self.check(db, lot)
            self.audit(db, "inventory_allocated", row)
            return row

    def policy(self, payload):
        if payload["confirmed"] is not True:
            raise ValueError("Confirmá la política local antes de registrar ventas.")
        with self.store.connect(write=True) as db:
            previous = self.find(db, "inventory_policy", "ops-inventory-policy")
            if previous:
                self.expected(previous, payload.get("expected_revision"))
            values = {"reserve": "on_register", "decrement": "on_ship", "returns": "confirmed_received", "confirmed": True}
            version = self.put(db, "inventory_policy_version", values)
            values["version_id"] = version["id"]
            row = self.save(db, {**previous, **values}) if previous else self.put(db, "inventory_policy", values, "ops-inventory-policy")
            self.audit(db, "inventory_policy_confirmed", row)
            return row

    def order_event(self, payload):
        with self.store.connect(write=True) as db:
            order_ref, event_ref = text(payload["order_ref"], "referencia de venta"), text(payload["event_id"], "identificador de evento")
            event_id, prior = self.idempotent(db, "order", (payload["account_id"], order_ref, event_ref), payload)
            if prior:
                return prior["result"]
            account = self.get(db, "account", payload["account_id"])
            lot = self.get(db, "lot", payload["lot_id"])
            location = self.get(db, "location", lot["location_id"])
            if lot["kind"] == "full" and location["account_id"] != account["id"]:
                raise Conflict("La observación Full pertenece a otra referencia de cuenta.")
            policy = self.find(db, "inventory_policy", "ops-inventory-policy")
            if not policy:
                raise Conflict("Definí y confirmá la política local de ventas primero.")
            ident = "ops-order-"+key(account["id"], order_ref)
            previous = self.find(db, "order", ident)
            if previous and previous["lot_id"] != lot["id"]:
                raise Conflict("Una venta no puede cambiar de producto/ubicación implícitamente.")
            if previous and payload["sequence"] < previous["sequence"]:
                return self.event(db, event_id, payload, {"status": "ignored_old", "order": previous})
            if previous and payload["sequence"] == previous["sequence"]:
                if any(previous[k] != payload[k] for k in ("status", "quantity", "returned_total")):
                    raise Conflict("Dos estados distintos usan la misma secuencia de venta.")
                return self.event(db, event_id, payload, {"status": "ignored_same", "order": previous})
            target, quantity, returned = payload["status"], integer(payload["quantity"]), integer(payload["returned_total"])
            if quantity <= 0:
                raise ValueError("La venta necesita cantidad positiva.")
            if previous is None and (target != "reserved" or not account["active"]):
                raise Conflict("Una venta local empieza reservada en una referencia de cuenta activa.")
            old_status = previous["status"] if previous else None
            allowed = {None: {"reserved"}, "reserved": {"reserved", "shipped", "cancelled"}, "shipped": {"returned"}, "returned": {"returned"}, "cancelled": set()}
            if target not in allowed[old_status]:
                raise Conflict("Transición de venta no permitida; no se repone una venta despachada como cancelación.")
            if previous and old_status != "reserved" and quantity != previous["quantity"]:
                raise Conflict("No se cambia la cantidad de una venta ya despachada.")
            if previous and old_status == "reserved" and target != "reserved" and quantity != previous["quantity"]:
                raise Conflict("Ajustá la reserva en un evento separado antes de despachar o cancelar.")
            if returned > quantity or (previous and returned < previous["returned_total"]) or (target != "returned" and returned != 0):
                raise Conflict("Cantidad devuelta incompatible con el historial de la venta.")
            return_delta = returned-(previous["returned_total"] if previous else 0)
            if return_delta and not payload["receipt_confirmed"]:
                raise Conflict("Confirmá la recepción física antes de reponer una devolución.")
            if target == "returned" and returned <= 0:
                raise ValueError("Indicá la devolución acumulada recibida.")
            reserved_delta = (quantity if target == "reserved" else 0)-(previous["quantity"] if old_status == "reserved" else 0)
            delta = -quantity if target == "shipped" else return_delta if target == "returned" else 0
            if lot["kind"] == "own":
                allocation_id = "ops-allocation-"+key(lot["id"], account["id"])
                allocation = self.find(db, "allocation", allocation_id)
                if reserved_delta > 0:
                    if not account["active"] or not allocation or allocation["quantity"] < reserved_delta:
                        raise Conflict("La reserva supera la asignación disponible de esta cuenta.")
                    self.save(db, {**allocation, "quantity": allocation["quantity"]-reserved_delta})
                elif target in {"reserved", "cancelled"} and reserved_delta < 0 and account["active"] and allocation:
                    self.save(db, {**allocation, "quantity": allocation["quantity"]-reserved_delta})
                lot["on_hand"] += delta
            values = {"account_id": account["id"], "lot_id": lot["id"], "product_id": lot["product_id"], "order_ref": order_ref,
                      "sequence": payload["sequence"], "status": target, "quantity": quantity, "returned_total": returned,
                      "policy_version_id": previous["policy_version_id"] if previous else policy["version_id"],
                      "source": "manual_local_order", "logistics": lot["kind"]}
            row = self.save(db, {**previous, **values}) if previous else self.put(db, "order", values, ident)
            if lot["kind"] == "own":
                self.check(db, lot)
                lot = self.save(db, lot)
                self.movement(db, lot, delta, "Venta local: "+target, event_ref, reserved_delta)
            self.audit(db, "local_order_"+target, row)
            return self.event(db, event_id, payload, {"status": "processed", "order": row})

    def full_capture(self, payload):
        with self.store.connect(write=True) as db:
            lot = self.get(db, "lot", payload["lot_id"])
            if lot["kind"] != "full":
                raise Conflict("Esta operación solo registra observaciones Full separadas.")
            event_id, prior = self.idempotent(db, "full_capture", (lot["id"], payload["event_id"]), payload)
            if prior:
                return prior["result"]
            row = self.put(db, "full_capture", {"lot_id": lot["id"], "quantity": integer(payload["quantity"]),
                "reference": text(payload["reference"], "origen de la observación", 300), "source": "manual_full_observation", "remote_verified": False})
            self.save(db, {**lot, "capture_id": row["id"]})
            self.audit(db, "full_observation_saved", row)
            return self.event(db, event_id, payload, row)

    def reconcile(self, payload):
        with self.store.connect(write=True) as db:
            lot = self.get(db, "lot", payload["lot_id"])
            quantity = integer(payload["observed_quantity"])
            book = self.totals(db, lot)["on_hand"]
            row = self.put(db, "reconciliation", {"lot_id": lot["id"], "book_quantity": book,
                "observed_quantity": quantity, "difference": quantity-book if book is not None else None,
                "reference": text(payload["reference"], "origen del conteo", 300), "source": "manual_observation"})
            self.audit(db, "inventory_reconciled_without_adjustment", row)
            return row
