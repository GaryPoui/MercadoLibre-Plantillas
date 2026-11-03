"""Closed formula grammar tested using fabricated arithmetic, not provider prices."""
import io

import pytest
from openpyxl import Workbook, load_workbook

from app.engine import build_review, export_review, read_workbook


def review_formula(expression, base=4, extras=None, **changes):
    book = Workbook()
    ws = book.active
    ws.title = "Lista"
    ws.append(["Código", "Descripción", "Base", "Cálculo", "Dependiente"])
    ws.append(["001-X", "Producto sintético", base, expression, "=D2+1"])
    for name, rows in (extras or {}).items():
        sheet = book.create_sheet(name)
        for row in rows: sheet.append(row)
    buffer = io.BytesIO()
    book.save(buffer)
    cfg = {"sheet": "Lista", "header_rows": [1], "data_start": 2,
           "mapping": {"code": "A", "description": "B", "base": "C"}}
    cfg.update(changes)
    return build_review(read_workbook(buffer.getvalue(), "synthetic.xlsx"), cfg)


@pytest.mark.parametrize("formula,expected", [("=C2*2+1", 9), ("=(C2+2)/3", 2),
    ('=IF(C2>=4,C2*2,0)', 8), ('=IF(C2<>4,99,7)', 7), ('=ROUND(2.345,2)', 2.35),
    ('=ROUND(-2.345,2)', -2.35), ('=SUM(C2:D1)', None), ('=SUM(C2,2,3)', 9),
    ('=C2*25%', 1), ('=IFERROR(1/0,8)', 8), ('=IF(FALSE,1/0,5)', 5)])
def test_arithmetic_and_allowed_functions(formula, expected):
    row = review_formula(formula)["rows"][1]
    assert row["values"]["D"] == expected
    if expected is None: assert row["status"] == "pending"


@pytest.mark.parametrize("formula", ["=IFERROR(VLOOKUP(C2,#REF!,2,0),0)",
    "=IFERROR('missing'!A1,0)", "=IFERROR(UNKNOWN(3),0)", "=D2+1", "=E2+1",
    "=[remote.xlsx]Sheet!A1", '=__import__("os")', '=C2.__class__', '=A20001+1'])
def test_unsafe_broken_and_cyclic_dependencies_never_certified(formula):
    review = review_formula(formula)
    row = review["rows"][1]
    assert row["values"]["D"] is None and row["values"]["E"] is None
    assert row["status"] == "pending"
    book = load_workbook(io.BytesIO(export_review(review)), data_only=False)
    assert book["Datos"]["D2"].value is None
    assert book["Datos"]["E2"].value is None
    assert all(c.data_type != "f" for sheet in book for rows in sheet for c in rows)


def test_empty_is_not_zero_and_iferror_cannot_hide_absent_input():
    absent = review_formula("=IFERROR(C2*2,0)", base=None)["rows"][1]
    zero = review_formula("=C2*2", base=0)["rows"][1]
    assert absent["values"]["D"] is None
    assert zero["values"]["D"] == 0 and zero["status"] == "usable"
    summed_absent = review_formula("=IFERROR(SUM(C2:C2),0)", base=None)["rows"][1]
    assert summed_absent["values"]["D"] is None


@pytest.mark.parametrize("base", [-1, "1,000.00", "NaN"])
def test_invalid_base_also_invalidates_derived_values(base):
    row = review_formula("=IFERROR(C2*2,0)", base=base)["rows"][1]
    assert row["values"]["C"] is None
    assert row["values"]["D"] is None
    assert row["values"]["E"] is None


def test_vlookup_exact_and_cross_sheet_sum():
    extras = {"Auxiliar con espacio": [[1, 11], [4, 20], [5, 30]]}
    result = review_formula("=VLOOKUP(C2,'Auxiliar con espacio'!$A$1:$B$3,2,FALSE)", extras=extras)
    assert result["rows"][1]["values"]["D"] == 20
    result = review_formula("=SUM('Auxiliar con espacio'!B1:B3)", extras=extras)
    assert result["rows"][1]["values"]["D"] == 61
    approximate = review_formula("=VLOOKUP(C2,'Auxiliar con espacio'!A1:B3,2,TRUE)", extras=extras)
    assert approximate["rows"][1]["values"]["D"] is None


def test_parameter_template_override_and_prior_result_immutable():
    first = review_formula("=C2*2", parameters={"factor": "1.5"}, formulas={"D": "=C{row}*factor"})
    second = review_formula("=C2*2", parameters={"factor": "2.5"}, formulas={"D": "=C{row}*factor"}, overrides={"C2": 6})
    assert first["rows"][1]["values"]["D"] == 6
    assert second["rows"][1]["values"]["D"] == 15
    assert second["rows"][1]["values"]["E"] == 16
    assert first["config"]["parameters"]["factor"] == "1.5"


def test_complexity_depth_bounded_and_unknown_parameter_pending():
    deep = review_formula("=" + "("*70 + "1" + ")"*70)
    assert deep["rows"][1]["values"]["D"] is None
    unknown = review_formula("=C2*missing")
    assert unknown["rows"][1]["status"] == "pending"
    hidden_unknown = review_formula("=IF(TRUE,2,WEBSERVICE(3))")
    assert hidden_unknown["rows"][1]["values"]["D"] is None
