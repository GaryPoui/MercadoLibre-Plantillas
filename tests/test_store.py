"""Persistence contracts exercised via public API, independent of table layout."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from openpyxl import load_workbook

from test_api import CONFIG, authenticated_client, make_review, synthetic_xlsx, upload


def test_restart_preserves_import_review_profile_and_revocation(tmp_path):
    with authenticated_client(tmp_path) as client:
        imported = upload(client)
        review = make_review(client, imported)
        response = client.post("/api/profiles", json={"name": "Perfil sintético", "supplier": "synthetic-a", "config": CONFIG})
        assert response.status_code in (200, 201)
        profile = response.json()
        export = client.get(f"/api/reviews/{review['id']}/export").content
    with authenticated_client(tmp_path) as restarted:
        assert restarted.get(f"/api/imports/{imported['id']}").json()["sha256"] == imported["sha256"]
        assert restarted.get(f"/api/reviews/{review['id']}").json() == review
        assert restarted.get(f"/api/reviews/{review['id']}/export").content == export
        assert profile in restarted.get("/api/profiles").json()


def test_profile_versions_retirement_and_provider_isolation(tmp_path):
    with authenticated_client(tmp_path) as client:
        first = client.post("/api/profiles", json={"name": "A", "supplier": "synthetic-a", "config": CONFIG}).json()
        other = client.post("/api/profiles", json={"name": "B", "supplier": "synthetic-b", "config": CONFIG}).json()
        changed = {**CONFIG, "parameters": {"factor": "1.5"}}
        response = client.post("/api/profiles", json={"name": "A", "supplier": "synthetic-a", "profile_id": first["profile_id"], "config": changed})
        assert response.status_code in (200, 201), response.text
        second = response.json()
        assert second["version"] == first["version"] + 1
        assert second["profile_id"] == first["profile_id"] != other["profile_id"]
        assert second["id"] != first["id"]
        response = client.post(f"/api/profiles/{second['id']}/retire")
        assert response.status_code in (200, 204)
        profiles = {p["id"]: p for p in client.get("/api/profiles").json()}
        assert profiles[first["id"]]["config"] == CONFIG
        assert profiles[other["id"]] == other
        assert profiles[second["id"]]["retired"] is True
        response = client.post("/api/profiles", json={"name": "B", "supplier": "synthetic-b", "profile_id": first["profile_id"], "config": changed})
        assert response.status_code in (400, 409, 422)


def test_failed_correction_leaves_existing_snapshot_and_latest_parent_usable(tmp_path):
    with authenticated_client(tmp_path) as client:
        review = make_review(client)
        url = f"/api/reviews/{review['id']}/corrections"
        invalid = {"changes": [{"row_number": 999999, "column": "C", "value": "150"}], "reason": "Fuera del origen"}
        assert client.post(url, json=invalid).status_code in (400, 422)
        assert client.get(f"/api/reviews/{review['id']}").json() == review
        valid = {"changes": [{"row_number": 2, "column": "C", "value": "125"}], "reason": "Corrección sintética"}
        assert client.post(url, json=valid).status_code in (200, 201)


def test_simultaneous_corrections_have_one_winner(tmp_path):
    with authenticated_client(tmp_path) as client:
        review = make_review(client)
        url = f"/api/reviews/{review['id']}/corrections"

        def correct(value):
            return client.post(url, json={"changes": [{"row_number": 2, "column": "C", "value": value}],
                                          "reason": "Edición concurrente sintética"})

        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(correct, ["151", "152"]))
        assert sum(r.status_code in (200, 201) for r in responses) == 1
        assert sum(r.status_code == 409 for r in responses) == 1
        assert client.get(f"/api/reviews/{review['id']}").json() == review


def test_reusing_profile_requires_supplier_and_compatible_structure(tmp_path):
    with authenticated_client(tmp_path) as client:
        first = make_review(client)
        response = client.post("/api/profiles", json={"name": "Perfil sintético", "supplier": "synthetic-a", "config": first["config"]})
        assert response.status_code in (200, 201)
        profile = response.json()
        imported = upload(client)
        endpoint = f"/api/imports/{imported['id']}/reviews"
        assert client.post(endpoint, json={"profile_version_id": profile["id"], "supplier": "synthetic-b"}).status_code == 409
        assert client.post(endpoint, json={"profile_version_id": profile["id"], "supplier": "synthetic-a"}).status_code in (200, 201)
        book = load_workbook(BytesIO(synthetic_xlsx()), keep_links=False)
        book.active["A1"] = "Otro significado sintético"
        altered = BytesIO()
        book.save(altered)
        book.close()
        incompatible = upload(client, altered.getvalue())
        response = client.post(f"/api/imports/{incompatible['id']}/reviews", json={"profile_version_id": profile["id"], "supplier": "synthetic-a"})
        assert response.status_code == 409
        assert client.post(f"/api/profiles/{profile['id']}/retire").status_code in (200, 204)
        fresh = upload(client)
        assert client.post(f"/api/imports/{fresh['id']}/reviews", json={"profile_version_id": profile["id"], "supplier": "synthetic-a"}).status_code == 409


def test_local_correction_does_not_become_profile_rule(tmp_path):
    with authenticated_client(tmp_path) as client:
        original = make_review(client)
        response = client.post(f"/api/reviews/{original['id']}/corrections", json={"changes": [{"row_number": 2, "column": "C", "value": "999"}], "reason": "Solo esta fila sintética"})
        assert response.status_code in (200, 201)
        corrected = response.json()
        response = client.post("/api/profiles", json={"name": "Perfil sin corrección puntual", "supplier": "synthetic-a", "config": corrected["config"]})
        assert response.status_code in (200, 201)
        profile = response.json()
        imported = upload(client)
        response = client.post(f"/api/imports/{imported['id']}/reviews", json={"profile_version_id": profile["id"], "supplier": "synthetic-a"})
        assert response.status_code in (200, 201)
        row = next(row for row in response.json()["rows"] if row["row_number"] == 2)
        assert float(row["mapped"]["base"]) == 100
