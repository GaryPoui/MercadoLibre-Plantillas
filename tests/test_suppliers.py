"""Synthetic supplier data only. No remote accounts or commercial rules."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from io import BytesIO
from threading import Barrier

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.engine import read_workbook, build_review
from app.main import create_app
from app.store import Store, Conflict
from app.suppliers import Suppliers, export_version
from test_api import authenticated_client


@pytest.fixture
def service(tmp_path):
    return Suppliers(Store(tmp_path))


def supplier(service, name="Proveedor ficticio", **extra):
    return service.save_supplier({"name": name, "aliases": [], "retired": False,
                                  "expected_revision": None, **extra})


def scope(service, provider, **extra):
    return service.save_scope(provider["id"], {"name": "Lista sintética", "currency": "ZZZ",
                                             "price_kind": "Importe ficticio de prueba",
                                             "expected_revision": None, **extra})


def review(service, body="001,10\n002,20", name="Proveedor ficticio"):
    raw = ("SKU,Precio\n"+body+"\n").encode()
    wb = read_workbook(raw, "sintetico.csv")
    src = service.store.create_import("sintetico.csv", raw, wb)
    result = build_review(wb, {"sheet": "CSV", "header_rows": [1], "data_start": 2,
                              "mapping": {"code": "A", "base": "B"}, "supplier": name})
    return service.store.create_review(src["id"], result)


def activate(service, sc, rv, mode="complete"):
    pv = service.preview(sc["id"], [rv["id"]], mode)
    assert pv["can_activate"], pv["blockers"]
    return service.activate(pv["id"])


def test_stable_identity_rename_aliases_and_retirement(service):
    provider = supplier(service)
    sc = scope(service, provider)
    rv = review(service)
    old = activate(service, sc, rv)
    content = export_version(old)
    renamed = service.save_supplier({"name": "Renombrado ficticio", "aliases": [], "retired": False,
                                    "expected_revision": 1}, provider["id"])
    assert renamed["id"] == provider["id"] and provider["name"] in renamed["aliases"]
    assert service.preview(sc["id"], [rv["id"]], "partial")["can_activate"]
    assert export_version(service.store.get("supplier_version", old["id"])) == content
    retired = service.save_supplier({**renamed, "expected_revision": 2, "retired": True}, provider["id"])
    with pytest.raises(Conflict):
        service.preview(sc["id"], [rv["id"]], "complete")
    assert service.store.get("supplier_version", old["id"])["rows"] == old["rows"]
    assert retired["retired"]


def test_name_alias_collision_and_stale_edits_are_blocked(service):
    a = supplier(service, aliases=["Alias explícito"])
    with pytest.raises(Conflict):
        supplier(service, "  ALIAS   explícito ")
    with pytest.raises(Conflict):
        service.save_supplier({**a, "expected_revision": 3}, a["id"])
    with pytest.raises(ValueError):
        supplier(service, " ")


def test_changes_keep_zero_identity_history_and_latest_once(service):
    p = supplier(service)
    sc = scope(service, p)
    first = activate(service, sc, review(service))
    second_review = review(service, "001,0\n002,20\n003,30")
    draft = service.preview(sc["id"], [second_review["id"]], "complete")
    assert [d["kind"] for d in draft["differences"]] == ["changed", "unchanged", "added"]
    second = service.activate(draft["id"])
    rows = service.current()["rows"]
    assert [(r["sku"], r["price"]) for r in rows] == [("001", 0), ("002", 20), ("003", 30)]
    assert second["parent_id"] == first["id"]
    assert service.store.get("supplier_version", first["id"]) == first
    assert len(service.versions(sc["id"])) == 2


@pytest.mark.parametrize("mode", ["partial", "complete"])
def test_invalid_price_retains_prior_and_absence_never_zeros(service, mode):
    p = supplier(service)
    sc = scope(service, p)
    prior = activate(service, sc, review(service))
    rv = review(service, "001,-1\n003,30")
    pv = service.preview(sc["id"], [rv["id"]], mode)
    rows = {r["sku"]: r for r in pv["rows"]}
    assert rows["001"]["price"] == 10 and rows["001"]["status"] == "pending"
    assert rows["001"]["review_id"] == prior["review_ids"][0]
    assert rows["001"]["attempted_review_id"] == rv["id"]
    assert rows["002"]["price"] == 20 and rows["002"]["status"] == "pending"
    assert rows["003"]["status"] == "ready"
    assert rows["002"]["update_state"] == ("absent" if mode == "complete" else "not_updated_partial")
    service.activate(pv["id"])
    assert service.current()["summary"]["pending"] == 2


def test_duplicates_preserve_candidates_and_prior_without_arbitration(service):
    p = supplier(service)
    sc = scope(service, p)
    activate(service, sc, review(service, "001,10"))
    pv = service.preview(sc["id"], [review(service, "001,5\n001,50")["id"]], "complete")
    assert pv["differences"][0]["kind"] == "ambiguous"
    assert [r["price"] for r in pv["rows"]] == [5, 50, 10]
    assert all(r["status"] == "pending" for r in pv["rows"])
    assert pv["can_activate"]  # Only the retained prior price is certified.


def test_last_certified_price_survives_ambiguous_then_invalid_upload(service):
    p = supplier(service)
    sc = scope(service, p)
    first = activate(service, sc, review(service, "001,10"))
    activate(service, sc, review(service, "001,5\n001,50"))
    third = activate(service, sc, review(service, "001,-1"), "partial")
    assert len(third["rows"]) == 1
    assert third["rows"][0]["price"] == 10
    assert third["rows"][0]["review_id"] == first["review_ids"][0]
    assert third["rows"][0]["status"] == "pending"


def test_restore_preview_is_stale_after_another_activation(service):
    p = supplier(service)
    sc = scope(service, p)
    first = activate(service, sc, review(service))
    restore = service.restore_preview(first["id"])
    activate(service, sc, review(service, "001,50"))
    with pytest.raises(Conflict):
        service.activate(restore["id"])


def test_first_activation_needs_metadata_and_valid_product(service):
    p = supplier(service)
    sc = scope(service, p, currency="", price_kind="")
    pv = service.preview(sc["id"], [review(service)["id"]], "complete")
    assert not pv["can_activate"]
    with pytest.raises(Conflict):
        service.activate(pv["id"])
    sc = service.save_scope(p["id"], {**sc, "currency": "ZZZ", "price_kind": "Ficticio", "expected_revision": 1}, sc["id"])
    bad = service.preview(sc["id"], [review(service, "001,\n002,-1")["id"]], "partial")
    assert not bad["can_activate"]
    with pytest.raises(Conflict):
        service.activate(bad["id"])


def test_currency_semantics_cannot_change_after_activation(service):
    p = supplier(service)
    sc = scope(service, p)
    activate(service, sc, review(service))
    sc = service.list()[0]["scopes"][0]
    with pytest.raises(Conflict):
        service.save_scope(p["id"], {**sc, "currency": "YYY", "expected_revision": sc["revision"]}, sc["id"])


def test_two_simultaneous_activations_have_one_winner(service):
    p = supplier(service)
    sc = scope(service, p)
    rv = review(service)
    drafts = [service.preview(sc["id"], [rv["id"]], "complete") for _ in range(2)]
    barrier = Barrier(2)
    def run(draft):
        barrier.wait()
        try:
            service.activate(draft["id"])
            return "activated"
        except Conflict:
            return "conflict"
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(run, drafts))
    assert sorted(outcomes) == ["activated", "conflict"]
    assert len(service.versions(sc["id"])) == 1


def test_supplier_or_scope_edit_invalidates_pending_preview(service):
    p = supplier(service)
    sc = scope(service, p)
    draft = service.preview(sc["id"], [review(service)["id"]], "complete")
    service.save_supplier({**p, "name": "Nuevo nombre", "expected_revision": 1}, p["id"])
    with pytest.raises(Conflict):
        service.activate(draft["id"])


def test_sources_and_bindings_isolate_providers_and_scopes(service):
    a, b = supplier(service), supplier(service, "Otro ficticio")
    sa, sb = scope(service, a), scope(service, b)
    ra, rb = review(service, "001,10"), review(service, "001,99", "Otro ficticio")
    activate(service, sa, ra)
    activate(service, sb, rb)
    assert [r["price"] for r in service.current()["rows"]] == [99, 10]
    assert all(r["id"] != ra["id"] for r in service.sources(sb["id"]))
    with pytest.raises(Conflict):
        service.preview(sb["id"], [ra["id"]], "complete")
    other_scope = scope(service, a, name="Otro alcance")
    with pytest.raises(Conflict):
        service.preview(other_scope["id"], [ra["id"]], "complete")


def test_restore_creates_new_version_and_historical_export_is_stable(service):
    p = supplier(service)
    sc = scope(service, p)
    one = activate(service, sc, review(service))
    original = export_version(one)
    two = activate(service, sc, review(service, "001,50\n002,60"))
    pv = service.restore_preview(one["id"])
    assert service.current()["rows"][0]["price"] == 50
    restored = service.activate(pv["id"])
    assert restored["id"] not in {one["id"], two["id"]}
    assert restored["restore_of"] == one["id"]
    assert restored["parent_id"] == two["id"] and restored["rows"] == one["rows"]
    assert export_version(service.store.get("supplier_version", one["id"])) == original
    reopened = Suppliers(Store(service.store.directory))
    assert reopened.current() == service.current()
    book = load_workbook(BytesIO(original))
    assert book["Datos"]["A2"].value == "001"
    assert book["Datos"]["K2"].value == "ZZZ"


def test_different_sheets_same_import_can_form_one_list(service):
    p = supplier(service)
    sc = scope(service, p)
    wb = read_workbook(b"SKU,Precio\n001,10\n", "x.csv")
    second = deepcopy(wb["sheets"][0])
    second["name"] = "Segunda"
    second["rows"][1][0]["value"] = "002"
    wb["sheets"].append(second)
    src = service.store.create_import("sintetico.csv", b"synthetic-original", wb)
    ids, parent = [], None
    for name in ("CSV", "Segunda"):
        result = build_review(wb, {"sheet": name, "mapping": {"code": "A", "base": "B"}, "supplier": p["name"]})
        rv = service.store.create_review(src["id"], result, parent)
        ids.append(rv["id"])
        parent = rv["id"]
    pv = service.preview(sc["id"], ids, "complete")
    assert len(pv["rows"]) == 2 and pv["can_activate"]
    with pytest.raises(ValueError):
        service.preview(sc["id"], [ids[0], ids[0]], "complete")


def test_authenticated_api_activation_export_and_csrf(tmp_path):
    with TestClient(create_app(data_dir=tmp_path)) as c:
        assert c.get("/api/suppliers").status_code == 401
        assert c.get("/api/standardized?source=current").status_code == 401
        assert c.get("/api/supplier-versions/missing/export").status_code == 401
    with authenticated_client(tmp_path) as c:
        assert c.get("/api/supplier-scopes/missing/sources").status_code == 404
        assert c.get("/api/standardized?source=invalid").status_code == 422
        payload = {"name": "Proveedor API ficticio"}
        assert c.post("/api/suppliers", json=payload, headers={"X-CSRF-Token": ""}).status_code == 403
        p = c.post("/api/suppliers", json=payload).json()
        sc = c.post(f"/api/suppliers/{p['id']}/scopes", json={"name": "Lista", "currency": "ZZZ", "price_kind": "Ficticio"}).json()
        uploaded = c.post("/api/imports", files={"file": ("x.csv", b"SKU,Precio\n001,0\n")}).json()
        rv = c.post(f"/api/imports/{uploaded['id']}/reviews", json={"sheet": "CSV", "mapping": {"code": "A", "base": "B"}, "supplier": p["name"]}).json()
        pv = c.post(f"/api/supplier-scopes/{sc['id']}/preview", json={"mode": "complete", "review_ids": [rv['id']]}).json()
        assert c.get("/api/standardized?source=current").json()["rows"] == []
        response = c.post(f"/api/supplier-previews/{pv['id']}/activate", json={})
        assert response.status_code == 200, response.text
        version = response.json()
        assert c.post(f"/api/supplier-previews/{pv['id']}/activate", json={}).status_code == 409
        assert c.get("/api/standardized?source=current").json()["rows"][0]["price"] == 0
        assert c.get(f"/api/supplier-versions/{version['id']}/export").status_code == 200
        assert c.get("/api/standardized/export?source=current").status_code == 200
