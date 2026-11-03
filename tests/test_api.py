"""API acceptance cases. Every workbook here is synthetic, not provider evidence."""
from contextlib import contextmanager
from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook, load_workbook

from app.main import create_app


PASSWORD = "synthetic-test-password-2026"
CONFIG = {
    "sheet": "Lista sintética",
    "header_rows": [1],
    "data_start": 2,
    "mapping": {"code": "A", "description": "B", "base": "C", "quantity": "D"},
    "parameters": {},
    "formulas": {},
}


def synthetic_xlsx(rows=None):
    book = Workbook()
    sheet = book.active
    sheet.title = CONFIG["sheet"]
    sheet.append(["Código", "Descripción", "Base", "Cantidad"])
    for row in rows or [["001-A", "Producto sintético", 100, 4]]:
        sheet.append(row)
    stream = BytesIO()
    book.save(stream)
    book.close()
    return stream.getvalue()


@contextmanager
def authenticated_client(path):
    with TestClient(create_app(data_dir=path)) as client:
        status = client.get("/api/auth/status").json()
        endpoint = "/api/auth/login" if status["configured"] else "/api/auth/setup"
        response = client.post(endpoint, json={"password": PASSWORD})
        assert response.status_code in (200, 201), response.text
        status = client.get("/api/auth/status").json()
        assert status["authenticated"] is True
        assert status.get("csrf")
        client.headers["X-CSRF-Token"] = status["csrf"]
        yield client


def upload(client, content=None):
    response = client.post(
        "/api/imports",
        files={"file": ("synthetic.xlsx", content or synthetic_xlsx(),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code in (200, 201), response.text
    return response.json()


def make_review(client, imported=None, config=None):
    imported = imported or upload(client)
    response = client.post(f"/api/imports/{imported['id']}/reviews", json=config or CONFIG)
    assert response.status_code in (200, 201), response.text
    return response.json()


def test_auth_setup_csrf_and_revoked_session(tmp_path):
    with TestClient(create_app(data_dir=tmp_path)) as client:
        status = client.get("/api/auth/status").json()
        assert status["configured"] is False and status["authenticated"] is False
        assert client.get("/api/imports").status_code == 401
        assert client.post("/api/auth/setup", json={"password": "short"}).status_code in (400, 422)
        response = client.post("/api/auth/setup", json={"password": PASSWORD})
        assert response.status_code in (200, 201)
        cookie = response.headers.get("set-cookie", "").lower()
        assert "httponly" in cookie and "samesite=strict" in cookie
        captured = dict(client.cookies)
        assert client.post("/api/catalog", json={"entries": []}).status_code == 403
        csrf = client.get("/api/auth/status").json()["csrf"]
        assert client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf}).status_code in (200, 204)
        client.cookies.update(captured)
        assert client.get("/api/imports").status_code == 401
        assert client.post("/api/auth/login", json={"password": "wrong"}).status_code == 401


def test_host_and_cross_origin_mutations_are_rejected(tmp_path):
    with authenticated_client(tmp_path) as client:
        assert client.get("/api/auth/status", headers={"Host": "attacker.invalid"}).status_code == 400
        response = client.post("/api/catalog", json={"entries": []},
                               headers={"Origin": "https://attacker.invalid"})
        assert response.status_code == 403


def test_import_duplicate_is_separate_and_preserves_identifiers(tmp_path):
    with authenticated_client(tmp_path) as client:
        content = synthetic_xlsx()
        first, second = upload(client, content), upload(client, content)
        assert first["id"] != second["id"]
        assert second["duplicate_of"] == first["id"]
        assert first["sha256"] == second["sha256"]
        assert first["sheets"][0]["name"] == CONFIG["sheet"]
        assert first["sheets"][0]["preview"]
        review = make_review(client, first)
        products = [row for row in review["rows"] if row["kind"] == "product"]
        assert products[0]["mapped"]["code"] == "001-A"
        assert len(client.get("/api/imports").json()) == 2


def test_invalid_extensions_and_corruption_are_legible(tmp_path):
    with authenticated_client(tmp_path) as client:
        for name, data in [("macro.xlsm", b"not allowed"), ("broken.xlsx", b"not a zip")]:
            response = client.post("/api/imports", files={"file": (name, data)})
            assert response.status_code in (400, 422)
            assert str(tmp_path) not in response.text
            assert "Traceback" not in response.text
        assert client.get("/api/imports").json() == []


def test_oversized_body_rejected_before_import(tmp_path):
    with authenticated_client(tmp_path) as client:
        response = client.post("/api/imports", content=b"x" * (13 * 1024 * 1024),
                               headers={"Content-Type": "application/octet-stream"})
        assert response.status_code == 413
        assert client.get("/api/imports").json() == []


def test_corrections_create_snapshot_and_stale_parent_conflicts(tmp_path):
    with authenticated_client(tmp_path) as client:
        old = make_review(client)
        export_url = f"/api/reviews/{old['id']}/export"
        original_export = client.get(export_url).content
        change = {"changes": [{"row_number": 2, "column": "C", "value": "150"}],
                  "reason": "Corrección sintética local"}
        response = client.post(f"/api/reviews/{old['id']}/corrections", json=change)
        assert response.status_code in (200, 201), response.text
        new = response.json()
        assert new["id"] != old["id"] and new["parent_id"] == old["id"]
        assert client.get(f"/api/reviews/{old['id']}").json() == old
        assert client.get(export_url).content == original_export
        assert client.post(f"/api/reviews/{old['id']}/corrections", json=change).status_code == 409
        book = load_workbook(BytesIO(client.get(f"/api/reviews/{new['id']}/export").content),
                             data_only=False, keep_links=False)
        assert set(book.sheetnames) == {"Datos", "Informe"}
        assert str(book["Datos"]["A2"].value) == "001-A"
        assert float(book["Datos"]["C2"].value) == 150
        book.close()
