"""Run real-reference checks locally without printing or copying commercial data.

The input is captured Google Sheets data, not original supplier XLSX files. XLSX is
reconstructed in memory; cached results remain independent expectations and are not
injected as computed values. No macros or external links are executed; formulas use
the engine's bounded evaluator rather than Python evaluation or an Excel process.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
from io import BytesIO
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def reconstruct(directory):
    from openpyxl import Workbook

    book = Workbook()
    book.remove(book.active)
    seen = set()
    for path in sorted(directory.glob("snapshot-*.json")):
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        for captured in document.get("sheets", []):
            title = captured["properties"]["title"]
            if title in seen:
                continue
            seen.add(title)
            sheet = book.create_sheet(title)
            for block in captured.get("data", []):
                row_offset = block.get("startRow", 0)
                col_offset = block.get("startColumn", 0)
                for row_number, row in enumerate(block.get("rowData", []), row_offset + 1):
                    for column, captured_cell in enumerate(row.get("values", []), col_offset + 1):
                        entered = captured_cell.get("userEnteredValue")
                        original = entered or captured_cell.get("effectiveValue", {})
                        if not original:
                            continue
                        cell = sheet.cell(row_number, column)
                        if "formulaValue" in original:
                            cell.value = original["formulaValue"]
                        elif "stringValue" in original:
                            cell.value = original["stringValue"]
                            cell.data_type = "s"
                        elif "numberValue" in original:
                            cell.value = original["numberValue"]
                        elif "boolValue" in original:
                            cell.value = original["boolValue"]
                        elif "errorValue" in original:
                            displayed = captured_cell.get("formattedValue")
                            if not displayed:
                                raise ValueError("unrepresentable_source_error")
                            cell.value = displayed
                            cell.data_type = "e"
                        pattern = captured_cell.get("effectiveFormat", {}).get("numberFormat", {}).get("pattern")
                        if pattern:
                            cell.number_format = pattern
    if not book.sheetnames:
        raise ValueError("missing_snapshots")
    stream = BytesIO()
    book.save(stream)
    book.close()
    return stream.getvalue()


def equal_number(actual, expected):
    try:
        return abs(Decimal(str(actual)) - Decimal(str(expected))) <= Decimal("0.000001")
    except (InvalidOperation, TypeError, ValueError):
        return False


def source_rows(case):
    return sorted({cell["row"] for cell in case["source_cells"]})


def run(directory):
    expected_path = directory / "base-inicial" / "casos-esperados-v0.json"
    if not expected_path.exists():
        return {"status": "skipped", "reason": "private_reference_unavailable", "passed": 0,
                "failed": 0, "not_covered": 0}, 0

    from app.engine import build_review, export_review, read_workbook
    from openpyxl import load_workbook

    expected = json.loads(expected_path.read_text(encoding="utf-8-sig"))
    workbook = read_workbook(reconstruct(directory), "private-reference-reconstructed.xlsx")
    reviews = {}

    def review(sheet, **custom):
        config = {"sheet": sheet, "header_rows": [1], "data_start": 2,
                  "mapping": {"listing": "A", "code": "B", "description": "C", "base": "F"},
                  "parameters": {}, "formulas": {}, **custom}
        key = json.dumps(config, sort_keys=True)
        if key not in reviews:
            reviews[key] = build_review(workbook, config)
        return reviews[key]

    outcomes = []
    for case in expected["cases"]:
        case_id = case["id"]
        try:
            if case_id == "CAS-01":
                result = review(case["source_sheet"])
                rows = {row["row_number"]: row for row in result["rows"]}
                checks = [check for check in expected["manual_arithmetic_checks"]
                          if check["source"] == case["source_sheet"]]
                assert checks
                for check in checks:
                    row = rows[check["row"]]
                    for column, value in check["arithmetic_expected"].items():
                        assert equal_number(row["values"].get(column), value)
                    codes = [c["cell"].get("userEnteredValue", {}).get("stringValue")
                             for c in case["source_cells"] if c["row"] == check["row"] and c["col"] == 2]
                    assert codes and row["mapped"]["code"] == codes[0]
                exported = load_workbook(BytesIO(export_review(result)), data_only=False, keep_links=False)
                try:
                    assert set(exported.sheetnames) == {"Datos", "Informe"}
                    for check in checks:
                        for column, value in check["arithmetic_expected"].items():
                            assert equal_number(exported["Datos"][f"{column}{check['row']}"].value, value)
                finally:
                    exported.close()
            elif case_id in {"CAS-02", "CAS-03", "CAS-05"}:
                result = review(case["source_sheet"])
                rows = {row["row_number"]: row for row in result["rows"]}
                for number in source_rows(case):
                    row = rows[number]
                    assert row["status"] in {"pending", "rejected"}
                    assert row["issues"]
                    if case_id == "CAS-02":
                        assert row["mapped"].get("base") is None
                    if case_id == "CAS-03":
                        assert equal_number(row["mapped"].get("base"), "0")
            elif case_id == "CAS-04":
                result = review(case["source_sheet"])
                for row in result["rows"]:
                    if row["row_number"] in source_rows(case):
                        assert row["status"] in {"pending", "rejected"}
                        assert row["issues"]
                        assert "\n" in str(row["values"].get("A", ""))
            elif case_id == "CAS-06":
                result = review(case["source_sheet"], header_rows=[1, 2], data_start=3,
                                mapping={"listing": "A", "code": "B", "description": "C", "base": "I"})
                rows = {row["row_number"]: row for row in result["rows"]}
                assert rows[1]["kind"] == rows[2]["kind"] == "header"
                assert any(rows[number]["kind"] == "context" for number in source_rows(case) if number > 2)
                assert sum(result["summary"].get(k, 0) for k in ("usable", "pending", "rejected", "context", "empty")) == result["summary"]["total"]
            elif case_id == "CAS-07":
                result = review(case["source_sheet"], sheet_kind="operational",
                                mapping={"description": "B"})
                rows = {row["row_number"]: row for row in result["rows"]}
                for source in case["source_cells"]:
                    if source["col"] != 4:
                        continue
                    original = source["cell"].get("userEnteredValue", {})
                    value = original.get("stringValue", original.get("numberValue"))
                    assert rows[source["row"]]["values"]["D"] == value
                    assert rows[source["row"]]["kind"] == "context"
                    assert "quantity" not in rows[source["row"]]["mapped"]
            elif case_id == "CAS-08":
                result = review(case["source_sheet"])
                rows = {row["row_number"]: row for row in result["rows"]}
                selected = [rows[n] for n in source_rows(case)]
                assert len(selected) >= 2
                assert len({row["mapped"]["code"] for row in selected}) == 1
                assert len({row["values"]["A"] for row in selected}) > 1
            elif case_id == "CAS-09":
                result = review(case["source_sheet"], sheet_kind="operational",
                                mapping={"description": "A"}, data_start=2)
                selected = [row for row in result["rows"] if row["row_number"] in source_rows(case)]
                if any(row["kind"] == "product" or row["mapped"] for row in selected):
                    outcomes.append({"case": case_id, "status": "not_covered"})
                    continue
            else:
                outcomes.append({"case": case_id, "status": "not_covered"})
                continue
            outcomes.append({"case": case_id, "status": "passed"})
        except Exception:
            # Do not include exception text: a cell value or formula may be sensitive.
            outcomes.append({"case": case_id, "status": "failed"})

    totals = {status: sum(x["status"] == status for x in outcomes)
              for status in ("passed", "failed", "not_covered")}
    complete = totals["failed"] == totals["not_covered"] == 0
    return {"status": "passed" if complete else "incomplete", "basis": "reconstructed_snapshots",
            **totals, "cases": outcomes}, 0 if complete else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-dir", type=Path, default=ROOT / "data" / "private")
    args = parser.parse_args()
    try:
        report, code = run(args.private_dir)
    except Exception:
        report, code = {"status": "failed", "reason": "private_verification_failed"}, 1
    print(json.dumps(report, ensure_ascii=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
