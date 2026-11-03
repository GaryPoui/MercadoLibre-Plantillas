"""Risk-focused offline operations tests. All values and identities are synthetic."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from threading import Barrier

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.main import create_app
from app.store import Store, Conflict
from app.local_catalog import LocalCatalog
from app.local_pricing import LocalPricing
from app.local_inventory import LocalInventory
from app.local_operations import LocalOperations
from app.local_api import Account, Product, Listing, Link, SupplierLink, Rule, Location, Lot, Allocation, Adjustment, Policy, OrderEvent, FullCapture
from app.suppliers import Suppliers
from app.engine import read_workbook, build_review
from test_api import authenticated_client


@pytest.fixture
def env(tmp_path):
    store = Store(tmp_path)
    cat, price, inv, ops = LocalCatalog(store), LocalPricing(store), LocalInventory(store), LocalOperations(store)
    a = cat.save_account(Account(name="Referencia sintética A").model_dump())
    b = cat.save_account(Account(name="Referencia sintética B").model_dump())
    product = cat.create_product(Product(sku="0001-INTERNO", name="Producto ficticio", unit="unidad sintética indivisible").model_dump())
    return {"store": store, "cat": cat, "price": price, "inv": inv, "ops": ops, "a": a, "b": b, "product": product}


def source(env, value=100):
    service = Suppliers(env["store"])
    provider = service.save_supplier({"name": "Proveedor ficticio", "aliases": [], "retired": False})
    scope = service.save_scope(provider["id"], {"name": "Lista ficticia", "currency": "ZZZ", "price_kind": "Base sintética"})
    raw = f"SKU,Precio\n0001-PROV,{value}\n".encode()
    wb = read_workbook(raw, "ficticio.csv")
    imported = env["store"].create_import("ficticio.csv", raw, wb)
    reviewed = build_review(wb, {"sheet": "CSV", "mapping": {"code": "A", "base": "B"}, "supplier": provider["name"]})
    review = env["store"].create_review(imported["id"], reviewed)
    pv = service.preview(scope["id"], [review["id"]], "complete")
    service.activate(pv["id"])
    return scope


def listing(env, account="a", reference="PUBLICACION-FICTICIA", price="80", **extra):
    return env["cat"].save_listing(Listing(account_id=env[account]["id"], listing_id=reference, price=price,
        currency="ZZZ", price_kind="Precio sintético final", logistics="own", simulated_editable=True, **extra).model_dump())


def pricing_setup(env):
    scope = source(env)
    dest = listing(env)
    env["cat"].link(Link(product_id=env["product"]["id"], listing_record_id=dest["id"]).model_dump())
    env["cat"].link(SupplierLink(product_id=env["product"]["id"], scope_id=scope["id"], supplier_sku="0001-PROV").model_dump(), supplier=True)
    env["price"].rule(Rule(account_id=env["a"]["id"], scope_id=scope["id"], factor="1.5", charge="2", digits=2,
        target_price_kind="Precio sintético final", confirmed=True).model_dump())
    preview = env["price"].preview({"account_id": env["a"]["id"], "scope_id": scope["id"]})
    return scope, dest, preview


def own_setup(env, quantity=10):
    location = env["inv"].location(Location(name="Depósito ficticio compartido", kind="own").model_dump())
    lot = env["inv"].lot(Lot(product_id=env["product"]["id"], location_id=location["id"], initial_quantity=quantity, safety=1, minimum=2).model_dump())
    env["inv"].policy(Policy(confirmed=True).model_dump())
    return lot


def allocate(env, lot, account="a", quantity=6):
    return env["inv"].allocation(Allocation(lot_id=lot["id"], account_id=env[account]["id"], quantity=quantity).model_dump())


def event(env, lot, *, account="a", order="PEDIDO-SINTETICO", event_id="evento-1", sequence=1, status="reserved", quantity=2, returned=0, receipt=False):
    return OrderEvent(account_id=env[account]["id"], lot_id=lot["id"], order_ref=order, event_id=event_id, sequence=sequence,
                      status=status, quantity=quantity, returned_total=returned, receipt_confirmed=receipt).model_dump()


def test_catalog_does_not_infer_identity_and_isolates_same_listing_reference(env):
    one, two = listing(env), listing(env, account="b", price="99")
    assert one["id"] != two["id"]
    assert one["remote_capability"] == "unknown" and not env["a"]["remote_connected"]
    scope = source(env)
    preview = env["price"].preview({"account_id": env["a"]["id"], "scope_id": scope["id"]})
    assert len(preview["rows"]) == 1 and preview["rows"][0]["status"] == "blocked"
    assert preview["rows"][0]["listing_id"] == one["id"]


def test_listing_requires_revision_and_keeps_manual_snapshot(env):
    one = listing(env)
    with pytest.raises(Conflict):
        listing(env, price="12")
    newer = listing(env, price="12", expected_revision=one["revision"])
    assert newer["revision"] == 2
    with env["store"].connect() as db:
        assert len(env["cat"].records(db, "listing_snapshot")) == 2


def test_link_to_supplier_requires_exact_sku_and_conflicts_are_explicit(env):
    scope = source(env)
    with pytest.raises(Conflict):
        env["cat"].link(SupplierLink(product_id=env["product"]["id"], scope_id=scope["id"], supplier_sku="0001-INTERNO").model_dump(), supplier=True)
    one = listing(env)
    link = env["cat"].link(Link(product_id=env["product"]["id"], listing_record_id=one["id"]).model_dump())
    with pytest.raises(Conflict):
        env["cat"].retire_link("product_link", link["id"], 99)


def test_rule_explicit_and_simulation_never_verifies_remote(env):
    scope, dest, preview = pricing_setup(env)
    assert preview["rows"][0]["proposed_price"] == "152.00"
    job = env["price"].simulate(preview["id"], "success", True)
    assert job["status"] == "simulated" and job["remote_verified"] is False
    assert job["rows"][0]["status"] == "simulated_verified"
    assert env["price"].simulate(preview["id"], "success", True) == job
    with env["store"].connect() as db:
        assert env["cat"].get(db, "listing", dest["id"])["price"] == "152.00"
    with pytest.raises(ValueError):
        env["price"].simulate(preview["id"], "success", False)


def test_edit_after_preview_conflicts_without_overwrite(env):
    _, dest, preview = pricing_setup(env)
    listing(env, price="90", expected_revision=dest["revision"])
    job = env["price"].simulate(preview["id"], "success", True)
    assert job["status"] == "conflict"
    with env["store"].connect() as db:
        assert env["cat"].get(db, "listing", dest["id"])["price"] == "90"
    with pytest.raises(Conflict):
        env["price"].retry(job["id"], "success")


def test_link_retirement_invalidates_prepared_price(env):
    _, _, preview = pricing_setup(env)
    link = preview["rows"][0]["product_link"]
    env["cat"].retire_link("product_link", link["id"], link["revision"])
    assert env["price"].simulate(preview["id"], "success", True)["status"] == "conflict"


def test_uncertain_after_write_reconciles_without_second_change(env):
    _, dest, preview = pricing_setup(env)
    job = env["price"].simulate(preview["id"], "timeout_after", True)
    assert job["status"] == "uncertain"
    with env["store"].connect() as db:
        revision = env["cat"].get(db, "listing", dest["id"])["revision"]
    result = env["price"].retry(job["id"], "success")
    assert result["status"] == "simulated"
    with env["store"].connect() as db:
        assert env["cat"].get(db, "listing", dest["id"])["revision"] == revision


@pytest.mark.parametrize("fault", ["reject", "timeout_before", "accepted_unchanged"])
def test_failed_or_unconfirmed_results_are_not_success(env, fault):
    _, dest, preview = pricing_setup(env)
    job = env["price"].simulate(preview["id"], fault, True)
    assert job["status"] in {"failed", "uncertain"}
    with env["store"].connect() as db:
        assert env["cat"].get(db, "listing", dest["id"])["revision"] == 1
    assert env["price"].retry(job["id"], "success")["status"] == "simulated"


def test_retry_limit_and_cancelled_preview_cannot_execute(env):
    _, _, preview = pricing_setup(env)
    job = env["price"].simulate(preview["id"], "reject", True)
    env["price"].retry(job["id"], "reject")
    env["price"].retry(job["id"], "reject")
    with pytest.raises(Conflict):
        env["price"].retry(job["id"], "success")
    scope = env["store"].get("supplier_scope", preview["scope_id"])
    other = env["price"].preview({"account_id": env["a"]["id"], "scope_id": scope["id"]})
    env["price"].cancel(other["id"])
    with pytest.raises(Conflict):
        env["price"].simulate(other["id"], "success", True)


def test_currency_mismatch_and_unconfirmed_rule_are_blocked(env):
    scope, dest, _ = pricing_setup(env)
    with pytest.raises(ValueError):
        env["price"].rule(Rule(account_id=env["a"]["id"], scope_id=scope["id"], factor="1", charge="0", digits=2, target_price_kind="Precio sintético final", confirmed=False).model_dump())
    payload = Listing(account_id=env["a"]["id"], listing_id=dest["listing_id"], price="80", currency="YYY",
                      price_kind="Precio sintético final", logistics="own", simulated_editable=True, expected_revision=1).model_dump()
    env["cat"].save_listing(payload)
    pv = env["price"].preview({"account_id": env["a"]["id"], "scope_id": scope["id"]})
    assert pv["rows"][0]["status"] == "blocked"


def test_shared_inventory_allocations_are_not_duplicated_between_accounts(env):
    lot = own_setup(env)
    allocate(env, lot, quantity=6)
    allocate(env, lot, account="b", quantity=3)
    with pytest.raises(Conflict):
        allocate(env, lot, account="b", quantity=4)
    assert len(env["ops"].state()["lot"]) == 1
    assert env["ops"].state()["lot"][0]["allocated"] == 9


def test_concurrent_allocations_cannot_overcommit(env):
    lot = own_setup(env)
    barrier = Barrier(2)
    def run(account):
        barrier.wait()
        try:
            allocate(env, lot, account=account, quantity=8)
            return "ok"
        except Conflict:
            return "conflict"
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(run, ["a", "b"])) == ["conflict", "ok"]
    assert env["ops"].state()["lot"][0]["allocated"] == 8


def test_reservation_dispatch_duplicate_and_partial_return(env):
    lot = own_setup(env)
    allocate(env, lot)
    payload = event(env, lot)
    first = env["inv"].order_event(payload)
    for _ in range(10):
        assert env["inv"].order_event(payload) == first
    assert env["ops"].state()["lot"][0]["reserved"] == 2
    shipment = event(env, lot, event_id="despacho", sequence=2, status="shipped")
    env["inv"].order_event(shipment)
    env["inv"].order_event(shipment)
    assert env["ops"].state()["lot"][0]["on_hand"] == 8
    with pytest.raises(Conflict):
        env["inv"].order_event(event(env, lot, event_id="devolucion", sequence=3, status="returned", returned=1))
    env["inv"].order_event(event(env, lot, event_id="devolucion", sequence=3, status="returned", returned=1, receipt=True))
    assert env["ops"].state()["lot"][0]["on_hand"] == 9
    env["inv"].order_event(event(env, lot, event_id="devolucion2", sequence=4, status="returned", returned=2, receipt=True))
    assert env["ops"].state()["lot"][0]["on_hand"] == 10


def test_order_modification_cancel_and_old_event_do_not_double_effect(env):
    lot = own_setup(env)
    allocate(env, lot)
    env["inv"].order_event(event(env, lot))
    env["inv"].order_event(event(env, lot, event_id="modificada", sequence=2, quantity=3))
    old = env["inv"].order_event(event(env, lot, event_id="viejo", sequence=1, quantity=2))
    assert old["status"] == "ignored_old"
    cancelled = event(env, lot, event_id="cancelada", sequence=3, status="cancelled", quantity=3)
    env["inv"].order_event(cancelled)
    env["inv"].order_event(cancelled)
    state = env["ops"].state()
    assert state["lot"][0]["on_hand"] == 10 and state["lot"][0]["reserved"] == 0
    assert state["allocation"][0]["quantity"] == 6


def test_reused_event_with_different_payload_and_equal_sequence_conflict(env):
    lot = own_setup(env)
    allocate(env, lot)
    env["inv"].order_event(event(env, lot))
    with pytest.raises(Conflict):
        env["inv"].order_event(event(env, lot, quantity=3))
    with pytest.raises(Conflict):
        env["inv"].order_event(event(env, lot, event_id="otro", quantity=3))


def test_reservations_cannot_exceed_account_allocation(env):
    lot = own_setup(env)
    allocate(env, lot, quantity=2)
    env["inv"].order_event(event(env, lot))
    with pytest.raises(Conflict):
        env["inv"].order_event(event(env, lot, order="OTRA", event_id="nueva"))
    assert env["ops"].state()["lot"][0]["reserved"] == 2


def test_adjustments_are_idempotent_and_cannot_cut_reserved_or_allocated(env):
    lot = own_setup(env)
    allocate(env, lot)
    payload = Adjustment(lot_id=lot["id"], delta=2, reason="Ajuste sintético", event_id="ajuste-1", expected_revision=lot["revision"]).model_dump()
    row = env["inv"].adjustment(payload)
    assert env["inv"].adjustment(payload) == row
    with pytest.raises(Conflict):
        env["inv"].adjustment({**payload, "delta": 3})
    with pytest.raises(Conflict):
        env["inv"].adjustment({**payload, "event_id": "ajuste-negativo", "delta": -10, "expected_revision": row["revision"]})
    assert env["ops"].state()["lot"][0]["on_hand"] == 12


def test_full_observations_not_changed_by_orders_or_adjustments(env):
    loc = env["inv"].location(Location(name="Full ficticio", kind="full", account_id=env["a"]["id"]).model_dump())
    lot = env["inv"].lot(Lot(product_id=env["product"]["id"], location_id=loc["id"]).model_dump())
    capture = env["inv"].full_capture(FullCapture(lot_id=lot["id"], quantity=20, reference="Observación ficticia", event_id="captura").model_dump())
    env["inv"].policy(Policy(confirmed=True).model_dump())
    env["inv"].order_event(event(env, lot))
    env["inv"].order_event(event(env, lot, event_id="despacho", sequence=2, status="shipped"))
    with pytest.raises(Conflict):
        allocate(env, lot)
    with pytest.raises(Conflict):
        env["inv"].adjustment(Adjustment(lot_id=lot["id"], delta=-1, reason="No permitido", event_id="x", expected_revision=2).model_dump())
    state = env["ops"].state()
    assert state["lot"][0]["on_hand"] == 20 and state["movement"] == []
    assert not capture["remote_verified"]


def test_alert_refresh_deduplicates_acknowledges_resolves_and_reopens(env):
    lot = own_setup(env, quantity=3)
    state = env["ops"].state()
    alert = next(r for r in state["alert"] if r["kind"] == "stock_minimum")
    for _ in range(4):
        env["ops"].state()
    assert env["ops"].state()["alert"][0]["occurrences"] == 1
    assert env["ops"].acknowledge(alert["id"])["status"] == "acknowledged"
    adjusted = env["inv"].adjustment(Adjustment(lot_id=lot["id"], delta=10, expected_revision=1, event_id="sumar", reason="Conteo ficticio").model_dump())
    assert env["ops"].state()["alert"][0]["status"] == "resolved"
    env["inv"].adjustment(Adjustment(lot_id=lot["id"], delta=-10, expected_revision=adjusted["revision"], event_id="restar", reason="Conteo ficticio").model_dump())
    reopened = env["ops"].state()["alert"][0]
    assert reopened["status"] == "open" and reopened["cycle"] == 2


def test_reconciliation_never_adjusts_stock_silently(env):
    lot = own_setup(env)
    row = env["inv"].reconcile({"lot_id": lot["id"], "observed_quantity": 7, "reference": "Conteo ficticio"})
    state = env["ops"].state()
    assert row["difference"] == -3 and state["lot"][0]["on_hand"] == 10
    assert any(a["kind"] == "inventory_difference" and a["status"] == "open" for a in state["alert"])


def test_prepared_mail_is_not_sent_and_is_deduplicated(env):
    own_setup(env, quantity=2)
    alert = env["ops"].state()["alert"][0]
    notice = env["ops"].prepare_notice(alert["id"], "ficticio@example.invalid")
    assert env["ops"].prepare_notice(alert["id"], "ficticio@example.invalid") == notice
    assert not notice["sent"] and notice["status"] == "prepared_not_sent"
    content = env["ops"].notice_bytes(notice["id"])
    assert content == env["ops"].notice_bytes(notice["id"])
    assert b"To: ficticio@example.invalid" in content
    with pytest.raises(ValueError):
        env["ops"].prepare_notice(alert["id"], "x@example.invalid\nBcc: otra@example.invalid")


def test_audit_filters_export_and_persistence(env):
    lot = own_setup(env)
    allocate(env, lot)
    env["inv"].order_event(event(env, lot))
    filtered = env["ops"].audit_rows(account_id=env["a"]["id"], action="local_order")
    assert len(filtered["rows"]) == 1
    first = env["ops"].audit_rows(limit=2)
    second = env["ops"].audit_rows(limit=2, before=first["next_cursor"])
    assert not {r["id"] for r in first["rows"]}.intersection(r["id"] for r in second["rows"])
    book = load_workbook(BytesIO(env["ops"].export()))
    assert book["Datos"]["A2"].value.startswith("Inventario")
    assert book["Datos"]["D2"].value == 10
    reopened = LocalOperations(Store(env["store"].directory))
    assert reopened.state()["order"] == env["ops"].state()["order"]


def test_ops_api_auth_csrf_remote_block_and_strict_inputs(tmp_path):
    with TestClient(create_app(data_dir=tmp_path)) as c:
        assert c.get('/api/ops/state').status_code == 401
        assert c.get('/api/ops/export').status_code == 401
    with authenticated_client(tmp_path) as c:
        assert c.post('/api/ops/accounts', json={"name": "A"}, headers={"X-CSRF-Token": ""}).status_code == 403
        assert c.post('/api/ops/accounts', json={"name": "A", "token": "never-store-this"}).status_code == 422
        assert c.post('/api/ops/remote/execute', json={}).status_code == 409
        account = c.post('/api/ops/accounts', json={"name": "A ficticia"})
        assert account.status_code == 200
        assert c.post('/api/ops/products', json={"sku": "001", "name": "Ficticio", "unit": "unidad"}).status_code == 200
        assert c.get('/api/ops/state').json()['remote_enabled'] is False
        assert c.get('/api/ops/audit?limit=500').status_code == 422


def test_editing_listing_cannot_silently_create_a_different_identity(env):
    original = listing(env)
    payload = Listing(account_id=env['a']['id'], listing_id='OTRA-REFERENCIA', price='90',
        currency='ZZZ', price_kind='Precio sintético final', logistics='own', simulated_editable=True,
        expected_revision=original['revision']).model_dump()
    with pytest.raises(Conflict):
        env['cat'].save_listing(payload)
    assert len(env['ops'].state()['listing']) == 1


def test_audit_status_is_historical_even_after_next_transition(env):
    lot = own_setup(env)
    allocate(env, lot)
    env['inv'].order_event(event(env, lot))
    env['inv'].order_event(event(env, lot, sequence=2, event_id='despacho', status='shipped'))
    reserved = env['ops'].audit_rows(status='reserved', account_id=env['a']['id'])['rows']
    shipped = env['ops'].audit_rows(status='shipped', account_id=env['a']['id'])['rows']
    assert [r['action'] for r in reserved] == ['local_order_reserved']
    assert [r['action'] for r in shipped] == ['local_order_shipped']
    assert env['ops'].audit_rows(status='returned')['rows'] == []


def test_severity_and_historical_preview_export_are_explicit(env):
    scope, dest, preview = pricing_setup(env)
    job = env['price'].simulate(preview['id'], 'accepted_unchanged', True)
    alert = next(a for a in env['ops'].state()['alert'] if a['resource_id'] == job['id'])
    assert alert['severity'] == 'error' and alert['source'] == 'local_evidence'
    book = load_workbook(BytesIO(env['ops'].export()))
    entries = list(book['Datos'].values)
    assert any(row[0] == 'Propuesta local histórica' and 'Revalidar' in row[7] for row in entries)
    assert any(row[0] == 'Precio simulado' and row[2] == 'uncertain' for row in entries)
