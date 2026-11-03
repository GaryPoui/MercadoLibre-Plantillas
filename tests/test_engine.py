"""Synthetic fixtures only; no provider data or commercial parameters."""
import copy
import io
import zipfile

import pytest
from openpyxl import Workbook, load_workbook

from app.engine import build_review, export_review, read_workbook


def xlsx(rows, title="Lista", extras=None):
    book = Workbook()
    ws = book.active
    ws.title = title
    for row in rows: ws.append(row)
    for name, data in (extras or {}).items():
        sheet = book.create_sheet(name)
        for row in data: sheet.append(row)
    buffer = io.BytesIO()
    book.save(buffer)
    return buffer.getvalue()


def config(**changes):
    result = {"sheet": "Lista", "header_rows": [1], "data_start": 2,
              "mapping": {"code": "A", "description": "B", "base": "C"}}
    result.update(changes)
    return result


def test_identity_absence_zero_and_rows_are_not_lost():
    wb = read_workbook(xlsx([["Código", "Descripción", "Base"],
                             ["001-X", "Uno", 0], ["002-X", "Dos", None],
                             [None, None, 5], [], [None, "Familia"]]), "lista.xlsx")
    review = build_review(wb, config())
    assert review["rows"][1]["mapped"]["code"] == "001-X"
    assert review["rows"][1]["mapped"]["base"] == 0
    assert review["rows"][1]["status"] == "usable"
    assert review["rows"][2]["values"]["C"] is None
    assert review["rows"][2]["status"] == "pending"
    assert review["rows"][3]["kind"] == "product"
    assert review["rows"][3]["status"] == "pending"
    assert review["rows"][4]["kind"] == "empty"
    assert review["rows"][5]["kind"] == "context"
    assert sum(review["summary"][k] for k in ("usable", "pending", "rejected", "context", "empty")) == review["summary"]["total"] == 6


def test_multiline_listing_duplicates_remain_separate():
    wb = read_workbook(xlsx([["SKU", "Producto", "Base", "Destino"],
                             ["A", "Uno", 2, "ID-1\nID-2"], ["A", "Uno", 3, "ID-3"]]), "x.xlsx")
    review = build_review(wb, config(mapping={"code": "A", "description": "B", "base": "C", "listing": "D"}))
    assert len(review["rows"]) == 3
    assert all(r["status"] == "pending" for r in review["rows"][1:])
    assert review["rows"][1]["values"]["D"] == "ID-1\nID-2"


def test_multiple_headers_context_and_export_positions():
    wb = read_workbook(xlsx([["Identidad", None, "Precio"], ["Código", "Descripción", "Base"],
                             [None, "Familia"], ["001", "Uno", 3]]), "x.xlsx")
    review = build_review(wb, config(header_rows=[1, 2], data_start=4))
    assert review["headers"][0]["label"] == "Identidad / Código"
    assert review["rows"][2]["kind"] == "context"
    exported = load_workbook(io.BytesIO(export_review(review)), data_only=False)
    assert exported["Datos"]["A1"].value == "Identidad"
    assert exported["Datos"]["A2"].value == "Código"
    assert exported["Datos"]["B3"].value == "Familia"
    assert exported["Datos"]["A4"].value == "001"
    assert exported["Informe"].max_row == 5


def test_correction_new_revision_does_not_mutate_old_review_or_original():
    wb = read_workbook(xlsx([["Código", "Descripción", "Base", "Derivado"], ["001", "Uno", 3, "=C2*2"]]), "x.xlsx")
    original = copy.deepcopy(wb)
    first = build_review(wb, config())
    second = build_review(wb, config(overrides={"C2": 7}))
    assert first["rows"][1]["values"]["D"] == 6
    assert second["rows"][1]["values"]["D"] == 14
    assert wb == original
    loaded = load_workbook(io.BytesIO(export_review(first)), data_only=False)
    assert loaded["Datos"]["D2"].value == 6
    assert loaded["Datos"]["D2"].data_type != "f"


def test_export_uses_snapshot_without_rebuilding(monkeypatch):
    review = build_review(read_workbook(xlsx([["Código", "Descripción", "Base"], ["001", "Uno", 3]]), "x.xlsx"), config())
    def fail(*args, **kwargs): raise AssertionError("No reprocesar")
    monkeypatch.setattr("app.engine.read_workbook", fail)
    monkeypatch.setattr("app.engine.build_review", fail)
    loaded = load_workbook(io.BytesIO(export_review(review)))
    assert loaded["Datos"]["C2"].value == 3


def test_export_deterministic_even_when_creation_time_changes(monkeypatch):
    review = build_review(read_workbook(xlsx([["Código", "Descripción", "Base"], ["001", "Uno", 3]]), "x.xlsx"), config())
    first = export_review(review)
    # Force openpyxl's saved core timestamp to a different year, without sleeping.
    from datetime import datetime, timezone
    from types import SimpleNamespace
    class Later(datetime):
        @classmethod
        def now(cls, tz=None): return cls(2040, 3, 4, tzinfo=tz)
    monkeypatch.setattr("openpyxl.writer.excel.datetime", SimpleNamespace(datetime=Later, timezone=timezone))
    assert first == export_review(copy.deepcopy(review))
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        assert all(i.date_time == (2000, 1, 1, 0, 0, 0) for i in archive.infolist())


def test_operational_sheet_never_becomes_catalog():
    wb = read_workbook(xlsx([["Tarea", "Estado", "Prioridad"], ["Revisar listas", False, "Alta"]]), "x.xlsx")
    review = build_review(wb, config(sheet_kind="operational"))
    assert review["rows"][1]["kind"] == "context"
    assert review["rows"][1]["mapped"] == {}
    assert review["summary"]["usable"] == 0


def test_csv_text_and_overrides_cannot_inject_export_formulas():
    wb = read_workbook(b'codigo,descripcion,base\n001,=WEBSERVICE("url"),2\n', "x.csv")
    review = build_review(wb, config(sheet="CSV", overrides={"B2": "=1+1"}))
    loaded = load_workbook(io.BytesIO(export_review(review)), data_only=False)
    assert loaded["Datos"]["A2"].value == "001"
    assert loaded["Datos"]["B2"].value == "=1+1"
    assert loaded["Datos"]["B2"].data_type == "s"


def test_reader_preserves_formula_cached_metadata_and_zero_format():
    book = Workbook()
    ws = book.active
    ws.title = "Lista"
    ws.append(["SKU", "Producto", "Base"])
    ws.append([7, "Uno", "=2+2"])
    ws["A2"].number_format = "0000"
    buffer = io.BytesIO()
    book.save(buffer)
    wb = read_workbook(buffer.getvalue(), "x.xlsx")
    assert wb["sheets"][0]["rows"][1][0]["display"] == "0007"
    cell = wb["sheets"][0]["rows"][1][2]
    assert cell["formula"] == "=2+2" and cell["cached"] is None
    review = build_review(wb, config())
    assert review["rows"][1]["mapped"]["code"] == "0007"
    assert review["rows"][1]["mapped"]["base"] == 4


@pytest.mark.parametrize("filename,data", [("x.xls", b"legacy"), ("x.xlsx", b"bad"), ("x.csv", b"\xff"), ("x.csv", b"")])
def test_unsupported_corrupt_or_empty_rejected(filename, data):
    with pytest.raises(ValueError): read_workbook(data, filename)


def test_zip_and_upload_limits(monkeypatch):
    with pytest.raises(ValueError, match="10 MiB"):
        read_workbook(b"a" * (10*1024*1024+1), "x.csv")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/vbaProject.bin", b"not executed")
    with pytest.raises(ValueError, match="macros"):
        read_workbook(buffer.getvalue(), "x.xlsx")
    monkeypatch.setattr("app.engine.MAX_ZIP", 10)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive: archive.writestr("x", b"a"*11)
    with pytest.raises(ValueError, match="ZIP"):
        read_workbook(buffer.getvalue(), "x.xlsx")


def test_oversized_coordinate_and_dtd_rejected():
    for xml in ('<worksheet><c r="A20001"/></worksheet>', '<!DOCTYPE x [<!ENTITY a "x">]><worksheet>&a;</worksheet>'):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive: archive.writestr("xl/worksheets/sheet1.xml", xml)
        with pytest.raises(ValueError): read_workbook(buffer.getvalue(), "x.xlsx")


@pytest.mark.parametrize("changes", [{"sheet": "missing"}, {"mapping": {"bad": "A"}},
    {"mapping": {"code": "A", "base": "A"}}, {"mapping": {"code": "ZZ"}},
    {"header_rows": [0]}, {"header_rows": [1,1]}, {"data_start": 1},
    {"overrides": {"A1": "bad"}}, {"parameters": {"A1": 2}}, {"parameters": {"factor": "NaN"}}])
def test_invalid_config_rejected(changes):
    wb = read_workbook(xlsx([["Código", "Descripción", "Base"], ["001", "Uno", 3]]), "x.xlsx")
    with pytest.raises(ValueError): build_review(wb, config(**changes))
