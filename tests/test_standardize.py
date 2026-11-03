"""Synthetic lists only: identity, certification and consistent output."""
from copy import deepcopy
from io import BytesIO

from openpyxl import load_workbook

from app.engine import read_workbook, build_review
from app.standardize import consolidate, export_standardized


def source(csv, mapping, supplier="Proveedor ficticio", ident="revision-1"):
    workbook = read_workbook(csv.encode(), "sintetico.csv")
    review = build_review(workbook, {"sheet": "CSV", "header_rows": [1], "data_start": 2,
                                   "mapping": mapping, "supplier": supplier})
    review["id"] = ident
    return {"filename": "sintetico.csv"}, review


def test_different_layouts_produce_same_sku_price_and_keep_origin():
    a = source("SKU,Precio,Nombre\n001-A,0,Uno\n", {"code": "A", "base": "B", "description": "C"})
    b = source("Nombre,Codigo,Importe\nDos,002-B,250\n", {"code": "B", "base": "C", "description": "A"}, ident="revision-2")
    before = deepcopy([a, b])
    result = consolidate([a, b])
    assert result["summary"] == {"total": 2, "ready": 2, "pending": 0, "unreviewed_imports": 0}
    assert [(r["sku"], r["price"]) for r in result["rows"]] == [("001-A", 0), ("002-B", 250)]
    assert result["rows"][1]["review_id"] == "revision-2"
    assert result["rows"][1]["row_number"] == 2
    assert before == [a, b]
    content = export_standardized(result)
    assert content == export_standardized(result)
    ws = load_workbook(BytesIO(content))["Datos"]
    assert [ws.cell(1, c).value for c in (1, 2, 4)] == ["SKU", "Precio", "Proveedor"]
    assert ws["A2"].value == "001-A" and ws["B2"].value == 0


def test_missing_and_negative_prices_are_not_certified_and_rows_stay_visible():
    pair = source("SKU,Precio\n001,-1\n002,\n003,ambigua\n", {"code": "A", "base": "B"})
    rows = consolidate([pair])["rows"]
    assert len(rows) == 3
    assert all(r["status"] == "pending" and r["price"] is None for r in rows)


def test_missing_mapping_and_supplier_cannot_silently_be_ready():
    pair = source("SKU,Precio\n001,20\n", {"description": "A"}, supplier="")
    row = consolidate([pair])["rows"][0]
    assert row["status"] == "pending" and row["sku"] is None and row["price"] is None
    assert any("Proveedor" in issue for issue in row["issues"])


def test_duplicate_supplier_sku_conserves_alternatives_not_cross_supplier_identity():
    a = source("SKU,Precio\n001,10\n", {"code": "A", "base": "B"})
    b = source("SKU,Precio\n001,15\n", {"code": "A", "base": "B"}, ident="revision-2")
    c = source("SKU,Precio\n001,20\n", {"code": "A", "base": "B"}, supplier="Otro proveedor")
    rows = consolidate([a, b, c])["rows"]
    assert [r["status"] for r in rows] == ["pending", "pending", "ready"]
    assert [r["price"] for r in rows] == [10, 15, 20]


def test_unreviewed_and_operational_do_not_become_products():
    pair = source("SKU,Precio\n001,10\n", {"code": "A", "base": "B"})
    pair[1]["rows"][1]["kind"] = "context"
    result = consolidate([pair, ({"filename": "sin revisar.csv"}, None)])
    assert result["rows"] == [] and result["summary"]["unreviewed_imports"] == 1


def test_common_export_preserves_text_as_text():
    pair = source("SKU,Precio\n=1+1,10\n", {"code": "A", "base": "B"}, supplier="=WEBSERVICE()")
    ws = load_workbook(BytesIO(export_standardized(consolidate([pair]))))["Datos"]
    assert ws["A2"].value == "=1+1" and ws["A2"].data_type == "s"
    assert ws["D2"].data_type == "s"
