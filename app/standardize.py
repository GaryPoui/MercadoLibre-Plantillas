"""Common supplier rows from persisted reviews; no identity or price arbitration."""
from collections import defaultdict
from decimal import Decimal, InvalidOperation

from openpyxl.utils import get_column_letter

from .engine import export_review


FIELDS = [
    ("sku", "SKU"), ("price", "Precio"), ("description", "Descripción"),
    ("supplier", "Proveedor"), ("filename", "Archivo"), ("sheet", "Hoja"),
    ("row_number", "Fila de origen"), ("review_id", "Revisión"),
    ("status", "Estado"), ("issues", "Incidencias"),
]


def consolidate(sources):
    rows, unreviewed = [], 0
    groups = defaultdict(list)
    for source, review in sources:
        if review is None:
            unreviewed += 1
            continue
        supplier = str(review.get("config", {}).get("supplier") or "").strip()
        for row in review["rows"]:
            if row["kind"] != "product":
                continue
            mapped = row.get("mapped", {})
            issues = [issue["message"] for issue in row.get("issues", [])]
            sku = mapped.get("code")
            if sku is None or not str(sku).strip():
                issues.append("Falta SKU; asigná la columna de código.")
                sku = None
            else:
                sku = str(sku)  # Preserve zeros, case, punctuation and whitespace.
            price = mapped.get("base")
            try:
                if price is None or isinstance(price, bool) or str(price).strip() == "":
                    raise ValueError
                numeric = Decimal(str(price))
                if not numeric.is_finite() or numeric < 0:
                    raise ValueError
                # Only reviewed/certified cell values may become the common price.
                base_column = review.get("config", {}).get("mapping", {}).get("base")
                if not base_column or row.get("values", {}).get(base_column) is None:
                    raise ValueError
            except (InvalidOperation, ValueError):
                price = None
                issues.append("Falta precio válido; revisá la columna de precio.")
            if not supplier:
                issues.append("Proveedor sin identificar; completalo en una nueva revisión.")
            if row.get("status") != "usable" and not issues:
                issues.append("La fila de origen necesita revisión.")
            result = {
                "sku": sku, "price": price, "description": mapped.get("description"),
                "supplier": supplier, "filename": source["filename"],
                "sheet": review["sheet"], "row_number": row["row_number"],
                "review_id": review["id"], "status": "pending" if issues else "ready",
                "issues": list(dict.fromkeys(issues)),
            }
            rows.append(result)
            if supplier and sku:
                groups[(supplier, sku)].append(result)
    for group in groups.values():
        if len(group) > 1:
            for row in group:
                row["status"] = "pending"
                row["issues"].append("SKU repetido para este proveedor; alternativas conservadas, sin elegir precio.")
    ready = sum(row["status"] == "ready" for row in rows)
    return {"rows": rows, "summary": {
        "total": len(rows), "ready": ready, "pending": len(rows) - ready,
        "unreviewed_imports": unreviewed,
    }}


def export_standardized(snapshot, fields=None):
    """Use the existing safe deterministic writer; no reread or recalculation."""
    def cells(values):
        return {get_column_letter(i): value for i, value in enumerate(values, 1)}

    fields = FIELDS if fields is None else fields
    rows = [{"row_number": 1, "kind": "header", "status": "usable",
             "values": cells([label for _, label in fields]), "issues": []}]
    for number, row in enumerate(snapshot["rows"], 2):
        values = []
        for field, _ in fields:
            value = row.get(field)
            if field == "issues":
                value = " | ".join(value)
            elif field == "status":
                value = "Listo" if value == "ready" else "Pendiente"
            values.append(value)
        rows.append({"row_number": number, "kind": "product",
                     "status": "usable" if row["status"] == "ready" else "pending",
                     "values": cells(values),
                     "issues": [{"column": "J", "message": issue} for issue in row["issues"]]})
    return export_review({"sheet": "Lista unificada", "rows": rows,
                          "config": {"data_start": 2}})
