"""Synthetic, controlled catalog; no Mercado Libre connection is made."""
from test_api import authenticated_client, make_review, synthetic_xlsx, upload


def entry(account, listing, *, logistics="own", verified=True, code="001-A"):
    return {"account_id": account, "product_key": code, "listing_id": listing,
            "price": "80", "quantity": 2, "logistics": logistics,
            "writable_verified": verified}


def test_comparison_is_account_scoped_and_protects_full_and_unverified(tmp_path):
    with authenticated_client(tmp_path) as client:
        catalog = [entry("one", "own"), entry("two", "other-account"),
                   entry("one", "full", logistics="full", code="002-B"),
                   entry("one", "unverified", verified=False, code="003-C")]
        response = client.post("/api/catalog", json={"entries": catalog})
        assert response.status_code in (200, 201)
        saved_catalog = client.get("/api/catalog").json()
        workbook = synthetic_xlsx([["001-A", "Sintético A", 100, 4],
                                   ["002-B", "Sintético B", 120, 3],
                                   ["003-C", "Sintético C", 140, 2],
                                   ["004-D", "Sin vínculo", 160, 1]])
        review = make_review(client, upload(client, workbook))
        response = client.post(f"/api/reviews/{review['id']}/compare", json={"account_id": "one"})
        assert response.status_code == 200, response.text
        differences = response.json()["differences"]
        assert differences and all(d["account_id"] == "one" for d in differences)
        assert not any(d.get("listing_id") == "other-account" for d in differences)
        own = [d for d in differences if d.get("listing_id") == "own"]
        assert own and all(d["eligible"] for d in own)
        for code in ("002-B", "003-C", "004-D"):
            blocked = [d for d in differences if d["product_key"] == code]
            assert blocked and all(not d["eligible"] for d in blocked)
            assert all(d.get("reason") for d in blocked)
        assert client.get("/api/catalog").json() == saved_catalog


def test_ambiguous_catalog_links_remain_blocked(tmp_path):
    with authenticated_client(tmp_path) as client:
        response = client.post("/api/catalog", json={"entries": [entry("one", "first"), entry("one", "second")]})
        assert response.status_code in (200, 201)
        review = make_review(client)
        response = client.post(f"/api/reviews/{review['id']}/compare", json={"account_id": "one"})
        assert response.status_code == 200
        differences = response.json()["differences"]
        assert differences and all(not d["eligible"] for d in differences)
        assert all(d.get("reason") for d in differences)
