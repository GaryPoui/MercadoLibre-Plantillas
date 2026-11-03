"""Bounded local spreadsheet interpretation and immutable review export.

No Excel expression is executed by Python or by the exported workbook. The small
parser below constructs its own expression tree and accepts only listed operators.
"""

from __future__ import annotations

import copy
import csv
import io
import math
import re
import zipfile
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path

from defusedxml import ElementTree as SafeXML
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import column_index_from_string, get_column_letter

MAX_FILE = 10 * 1024 * 1024
MAX_ZIP = 100 * 1024 * 1024
MAX_ROWS, MAX_COLUMNS, MAX_CELLS, MAX_SHEETS = 20000, 100, 500000, 30
MAX_DEPTH = 64
ALLOWED_MAPPING = {"code", "description", "base", "listing", "quantity", "logistics"}
CELL = re.compile(r"\$?([A-Za-z]{1,3})\$?([1-9][0-9]*)\Z")
COLUMN = re.compile(r"[A-Z]{1,2}\Z")


def _scalar(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        if not value.is_finite() or abs(value) > Decimal("1e100"):
            raise FormulaProblem("Resultado numérico fuera del límite")
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Valor numérico no finito")
    if isinstance(value, str) and re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", value):
        raise ValueError("El texto contiene caracteres de control no admitidos")
    return value


def _display(value, number_format="General"):
    if value is None:
        return ""
    # Preserve identifiers explicitly displayed using a plain leading-zero mask.
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if re.fullmatch(r"0+", number_format) and value == int(value):
            return str(int(value)).zfill(len(number_format))
    return str(_scalar(value))


def _cell(value=None, formula=None, cached=None, number_format="General", display=None):
    return {"value": _scalar(value), "formula": formula, "cached": _scalar(cached),
            "display": _display(value if formula is None else cached, number_format)
            if display is None else display, "number_format": number_format}


def _bounds(rows, columns, cells):
    if rows > MAX_ROWS or columns > MAX_COLUMNS or cells > MAX_CELLS:
        raise ValueError("Límite excedido: 20000 filas, 100 columnas y 500000 celdas")


def read_workbook(content: bytes, filename: str) -> dict:
    """Read XLSX/UTF-8 CSV without macros, active links or formula evaluation."""
    if not isinstance(content, bytes) or not content:
        raise ValueError("El archivo está vacío")
    if len(content) > MAX_FILE:
        raise ValueError("Límite de archivo excedido: 10 MiB")
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("El CSV debe estar codificado en UTF-8") from exc
        if "\x00" in text:
            raise ValueError("El CSV contiene caracteres no admitidos")
        try:
            dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        rows, count = [], 0
        try:
            for row in csv.reader(io.StringIO(text, newline=""), dialect, strict=True):
                count += len(row)
                _bounds(len(rows) + 1, len(row), count)
                # CSV values remain text, including apparent numbers/expressions.
                rows.append([_cell(v if v != "" else None) for v in row])
        except csv.Error as exc:
            raise ValueError("No se pudo interpretar el CSV") from exc
        return {"sheets": [{"name": "CSV", "rows": rows, "merges": []}]}
    if suffix != ".xlsx":
        raise ValueError("Formato no admitido; use XLSX o CSV UTF-8")
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            infos = archive.infolist()
            if len(infos) > 2000 or sum(i.file_size for i in infos) > MAX_ZIP:
                raise ValueError("Límite ZIP excedido: 100 MiB o 2000 entradas")
            names = [i.filename for i in infos]
            if len(set(names)) != len(names):
                raise ValueError("El XLSX contiene entradas duplicadas")
            actual_cells = 0
            for info in infos:
                name = info.filename.lower()
                if info.flag_bits & 1:
                    raise ValueError("No se admiten archivos protegidos")
                if "vbaproject" in name or name.startswith("xl/externallinks/"):
                    raise ValueError("No se admiten macros ni vínculos de libro externos")
                if name.endswith(".xml") or name.endswith(".rels"):
                    root = SafeXML.fromstring(archive.read(info))
                    if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                        # Inspect actual cell coordinates before openpyxl creates objects.
                        for element in root.iter():
                            if element.tag.rsplit("}", 1)[-1] == "c":
                                actual_cells += 1
                                match = CELL.fullmatch(element.attrib.get("r", ""))
                                if not match:
                                    raise ValueError("Coordenada XLSX inválida")
                                _bounds(int(match[2]), column_index_from_string(match[1]), actual_cells)
                            elif element.tag.rsplit("}", 1)[-1] == "mergeCell":
                                from openpyxl.worksheet.cell_range import CellRange
                                area = CellRange(element.attrib.get("ref", ""))
                                _bounds(area.max_row, area.max_col, (area.max_row-area.min_row+1)*(area.max_col-area.min_col+1))
        source = load_workbook(io.BytesIO(content), data_only=False, keep_links=False)
        cached = load_workbook(io.BytesIO(content), data_only=True, keep_links=False)
        try:
            if len(source.worksheets) > MAX_SHEETS:
                raise ValueError("Límite excedido: 30 hojas")
            sheets, total = [], 0
            for ws in source.worksheets:
                total += ws.max_row * ws.max_column
                _bounds(ws.max_row, ws.max_column, total)
                rows = []
                for row in ws.iter_rows():
                    values = []
                    for c in row:
                        formula = c.value if c.data_type == "f" else None
                        if formula is not None and not isinstance(formula, str):
                            formula = "=UNSUPPORTED()"
                        val = None if formula else c.value
                        result = cached[ws.title].cell(c.row, c.column).value if formula else None
                        item = _cell(val, formula, result, c.number_format)
                        if c.data_type == "e": item["error"] = True
                        values.append(item)
                    while values and all(values[-1].get(k) is None for k in ("value", "formula", "cached")):
                        values.pop()
                    rows.append(values)
                while rows and not rows[-1]:
                    rows.pop()
                sheets.append({"name": ws.title, "rows": rows,
                               "merges": [str(m) for m in ws.merged_cells.ranges]})
            return {"sheets": sheets}
        finally:
            source.close()
            cached.close()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("El XLSX está dañado, protegido o contiene XML no seguro") from exc


class FormulaProblem(ValueError):
    def __init__(self, message, recoverable=False):
        super().__init__(message)
        self.recoverable = recoverable


TOKEN = re.compile(
    r'\s*(?:(?P<num>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)'
    r'|(?P<string>"(?:[^"]|"")*")|(?P<sheet>\'(?:[^\']|\'\')*\')'
    r'|(?P<name>\$?[A-Za-z_][A-Za-z0-9_.$]*)'
    r'|(?P<op><=|>=|<>|[+\-*/^%=<>(),:!;]))'
)


class Parser:
    """Closed expression grammar; never uses eval/exec or Python AST execution."""
    def __init__(self, text):
        if len(text) > 4096:
            raise FormulaProblem("Fórmula demasiado larga")
        self.tokens, pos = [], 0
        text = text.strip()
        if text.startswith("="):
            text = text[1:]
        while pos < len(text):
            match = TOKEN.match(text, pos)
            if not match:
                raise FormulaProblem("Referencia rota, externa o expresión no admitida")
            self.tokens.append((match.lastgroup, match.group(match.lastgroup)))
            pos = match.end()
        self.index = 0

    def peek(self, text=None):
        token = self.tokens[self.index] if self.index < len(self.tokens) else (None, None)
        return token[1] == text if text is not None else token

    def take(self, text=None):
        token = self.peek()
        if token[0] is None or (text is not None and token[1] != text):
            raise FormulaProblem("Sintaxis de fórmula inválida")
        self.index += 1
        return token

    def parse(self):
        node = self.expression(0)
        if self.index != len(self.tokens):
            raise FormulaProblem("Sintaxis de fórmula no admitida")
        return node

    def expression(self, depth, minimum=0):
        if depth >= MAX_DEPTH:
            raise FormulaProblem("Fórmula excede profundidad 64")
        kind, text = self.take()
        if text in ("+", "-"):
            left = ("unary", text, self.expression(depth + 1, 4))
        elif text == "(":
            left = self.expression(depth + 1)
            self.take(")")
        elif kind == "num":
            left = ("literal", Decimal(text))
        elif kind == "string":
            left = ("literal", text[1:-1].replace('""', '"'))
        elif kind in ("name", "sheet"):
            if self.peek("("):
                if kind != "name":
                    raise FormulaProblem("Función inválida")
                self.take("(")
                args = []
                if not self.peek(")"):
                    while True:
                        args.append(self.expression(depth + 1))
                        if not self.peek(",") and not self.peek(";"):
                            break
                        self.take()
                self.take(")")
                allowed = {"IF": (3, 3), "IFERROR": (2, 2), "SUM": (1, 100),
                           "ROUND": (2, 2), "VLOOKUP": (4, 4)}
                bounds = allowed.get(text.upper())
                if bounds is None or not bounds[0] <= len(args) <= bounds[1]:
                    raise FormulaProblem("Función o argumentos no admitidos: " + text.upper())
                left = ("call", text.upper(), args)
            else:
                sheet = None
                if self.peek("!"):
                    sheet = text[1:-1].replace("''", "'") if kind == "sheet" else text
                    self.take("!")
                    text = self.take()[1]
                match = CELL.fullmatch(text)
                if match:
                    left = ("ref", sheet, text.replace("$", "").upper())
                    if self.peek(":"):
                        self.take(":")
                        end = self.take()[1]
                        if not CELL.fullmatch(end):
                            raise FormulaProblem("Rango inválido")
                        left = ("range", sheet, text.replace("$", "").upper(), end.replace("$", "").upper())
                elif sheet is not None or kind == "sheet":
                    raise FormulaProblem("Referencia inválida")
                elif text.upper() in ("TRUE", "FALSE"):
                    left = ("literal", text.upper() == "TRUE")
                else:
                    left = ("parameter", text)
        else:
            raise FormulaProblem("Expresión no admitida")
        priorities = {"=": 1, "<>": 1, "<": 1, ">": 1, "<=": 1, ">=": 1,
                      "+": 2, "-": 2, "*": 3, "/": 3, "^": 4}
        while True:
            op = self.peek()[1]
            if op == "%":
                self.take()
                left = ("binary", "/", left, ("literal", Decimal(100)))
                continue
            priority = priorities.get(op, -1)
            if priority < minimum:
                break
            self.take()
            right = self.expression(depth + 1, priority + (0 if op == "^" else 1))
            left = ("binary", op, left, right)
        return left


def _number(value):
    if value is None or value == "":
        raise FormulaProblem("Dependencia vacía; no equivale a cero")
    if isinstance(value, bool):
        return Decimal(int(value))
    if isinstance(value, str):
        # No guessing locale/thousands: only explicit machine decimal syntax.
        if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", value.strip()):
            raise FormulaProblem("Valor numérico ambiguo o no válido", True)
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise FormulaProblem("Valor numérico no válido", True) from exc
    if not result.is_finite() or abs(result) > Decimal("1e100"):
        raise FormulaProblem("Valor numérico fuera del límite")
    return result


class FormulaEngine:
    def __init__(self, sheets, parameters, overrides, formulas, selected, product_rows, numeric_columns=None):
        self.sheets = {s["name"]: s for s in sheets}
        self.parameters, self.overrides, self.formulas = parameters, overrides, formulas
        self.selected, self.product_rows = selected, product_rows
        self.numeric_columns = numeric_columns or {}
        self.cache, self.active, self.parsed = {}, set(), {}

    def cell(self, sheet, coordinate, depth=0):
        key = (sheet, coordinate)
        if depth >= MAX_DEPTH:
            raise FormulaProblem("Dependencias exceden profundidad 64")
        if key in self.active:
            raise FormulaProblem("Dependencia circular")
        if key in self.cache:
            result = self.cache[key]
            if isinstance(result, FormulaProblem):
                raise result
            return result
        if sheet not in self.sheets:
            raise FormulaProblem("Hoja referenciada inexistente")
        match = CELL.fullmatch(coordinate)
        row, col = int(match[2]), column_index_from_string(match[1])
        if row > MAX_ROWS or col > MAX_COLUMNS:
            raise FormulaProblem("Referencia fuera de límites")
        rows = self.sheets[sheet]["rows"]
        source = rows[row - 1][col - 1] if row <= len(rows) and col <= len(rows[row - 1]) else {}
        value, formula = source.get("value"), source.get("formula")
        if sheet == self.selected:
            if coordinate in self.overrides:
                value, formula = self.overrides[coordinate], None
            elif row in self.product_rows and match[1] in self.formulas:
                formula = self.formulas[match[1]].replace("{row}", str(row))
        if source.get("error") and not (sheet == self.selected and coordinate in self.overrides):
            raise FormulaProblem("Celda de origen con error; resultado no certificado")
        self.active.add(key)
        try:
            if formula:
                if formula not in self.parsed:
                    self.parsed[formula] = Parser(formula).parse()
                with localcontext() as ctx:
                    ctx.prec = 28
                    value = self.evaluate(self.parsed[formula], sheet, depth + 1)
                if value is None:
                    raise FormulaProblem("Dependencia vacía; resultado no certificado")
            if sheet == self.selected and row in self.product_rows and match[1] in self.numeric_columns:
                try:
                    numeric = _number(value)
                except FormulaProblem as exc:
                    raise FormulaProblem(str(exc)) from exc
                if numeric < 0 or (self.numeric_columns[match[1]] == "quantity" and numeric != int(numeric)):
                    raise FormulaProblem("Importe negativo o cantidad no entera")
            self.cache[key] = value
            return value
        except FormulaProblem as exc:
            self.cache[key] = exc
            raise
        except (ArithmeticError, TypeError, ValueError) as exc:
            problem = FormulaProblem("Cálculo inválido o fuera del límite")
            self.cache[key] = problem
            raise problem from exc
        finally:
            self.active.remove(key)

    def range_cells(self, node, sheet):
        _, other, start, end = node
        sheet = other or sheet
        a, b = CELL.fullmatch(start), CELL.fullmatch(end)
        c1, c2 = column_index_from_string(a[1]), column_index_from_string(b[1])
        r1, r2 = int(a[2]), int(b[2])
        if r1 > r2 or c1 > c2 or r2 > MAX_ROWS or c2 > MAX_COLUMNS or (r2-r1+1)*(c2-c1+1) > MAX_CELLS:
            raise FormulaProblem("Rango fuera de límites")
        if sheet not in self.sheets:
            raise FormulaProblem("Hoja referenciada inexistente")
        return sheet, r1, r2, c1, c2

    def evaluate(self, node, sheet, depth):
        if depth >= MAX_DEPTH:
            raise FormulaProblem("Expresión excede profundidad 64")
        tag = node[0]
        ev = lambda n: self.evaluate(n, sheet, depth + 1)
        if tag == "literal":
            return node[1]
        if tag == "parameter":
            if node[1] not in self.parameters:
                raise FormulaProblem("Parámetro no definido: " + node[1])
            return self.parameters[node[1]]
        if tag == "ref":
            return self.cell(node[1] or sheet, node[2], depth + 1)
        if tag == "range":
            raise FormulaProblem("Un rango necesita SUM o VLOOKUP")
        if tag == "unary":
            value = _number(ev(node[2]))
            return value if node[1] == "+" else -value
        if tag == "binary":
            op, left, right = node[1], ev(node[2]), ev(node[3])
            if op in ("=", "<>", "<", ">", "<=", ">="):
                if left is None or right is None:
                    raise FormulaProblem("Dependencia vacía en comparación")
                if isinstance(left, (int, float, Decimal)) or isinstance(right, (int, float, Decimal)):
                    left, right = _number(left), _number(right)
                return {"=": lambda: left == right, "<>": lambda: left != right,
                        "<": lambda: left < right, ">": lambda: left > right,
                        "<=": lambda: left <= right, ">=": lambda: left >= right}[op]()
            left, right = _number(left), _number(right)
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "/":
                if right == 0:
                    raise FormulaProblem("División por cero", True)
                return left / right
            if op == "^":
                if abs(right) > 100 or right != int(right):
                    raise FormulaProblem("Exponente no admitido")
                return left ** int(right)
        if tag == "call":
            name, args = node[1], node[2]
            if name == "IF" and len(args) == 3:
                condition = ev(args[0])
                if condition is None:
                    raise FormulaProblem("Condición vacía")
                return ev(args[1] if condition else args[2])
            if name == "IFERROR" and len(args) == 2:
                try:
                    return ev(args[0])
                except FormulaProblem as exc:
                    if not exc.recoverable:
                        raise
                    return ev(args[1])
            if name == "ROUND" and len(args) == 2:
                places = _number(ev(args[1]))
                if places != int(places) or abs(places) > 20:
                    raise FormulaProblem("Precisión ROUND no admitida")
                return _number(ev(args[0])).quantize(Decimal(1).scaleb(-int(places)), rounding=ROUND_HALF_UP)
            if name == "SUM" and args:
                total = Decimal(0)
                for arg in args:
                    if arg[0] == "range":
                        sn, r1, r2, c1, c2 = self.range_cells(arg, sheet)
                        for row in range(r1, r2 + 1):
                            for col in range(c1, c2 + 1):
                                value = self.cell(sn, f"{get_column_letter(col)}{row}", depth + 1)
                                if value is not None and value != "":
                                    total += _number(value)
                    else:
                        total += _number(ev(arg))
                return total
            if name == "VLOOKUP" and len(args) == 4 and args[1][0] == "range":
                exact = ev(args[3])
                if exact not in (False, Decimal(0)):
                    raise FormulaProblem("VLOOKUP solo admite coincidencia exacta")
                key, index = ev(args[0]), _number(ev(args[2]))
                sn, r1, r2, c1, c2 = self.range_cells(args[1], sheet)
                if key is None or index != int(index) or index < 1 or index > c2-c1+1:
                    raise FormulaProblem("Clave o columna VLOOKUP inválida")
                for row in range(r1, r2 + 1):
                    candidate = self.cell(sn, f"{get_column_letter(c1)}{row}", depth + 1)
                    if candidate == key or (isinstance(candidate, (int, float, Decimal)) and isinstance(key, (int, float, Decimal)) and _number(candidate) == _number(key)):
                        value = self.cell(sn, f"{get_column_letter(c1+int(index)-1)}{row}", depth + 1)
                        if value is None:
                            raise FormulaProblem("Resultado VLOOKUP vacío")
                        return value
                raise FormulaProblem("VLOOKUP sin coincidencia", True)
            raise FormulaProblem("Función o argumentos no admitidos: " + name)
        raise FormulaProblem("Expresión no admitida")


def _column(value):
    if not isinstance(value, str) or not COLUMN.fullmatch(value) or column_index_from_string(value) > MAX_COLUMNS:
        raise ValueError("Columna inválida; use letras A a CV")
    return value


def _config(workbook, config):
    if not isinstance(config, dict):
        raise ValueError("La configuración debe ser un objeto")
    config = copy.deepcopy(config)
    sheet_kind = config.get("sheet_kind", "catalog")
    if sheet_kind not in {"catalog", "operational"}:
        raise ValueError("Tipo de hoja inválido; use catalog u operational")
    sheets = workbook.get("sheets", [])
    selected = next((s for s in sheets if s["name"] == config.get("sheet")), None)
    if selected is None:
        raise ValueError("Seleccione una hoja existente")
    headers = config.get("header_rows", [1])
    start = config.get("data_start", 2)
    if (not isinstance(headers, list) or not headers or len(headers) > 20
            or any(type(r) is not int or r < 1 or r > max(len(selected["rows"]), 1) for r in headers)
            or len(set(headers)) != len(headers) or type(start) is not int
            or start <= max(headers) or start > MAX_ROWS):
        raise ValueError("Filas de cabecera o inicio de datos inválidas")
    mapping = config.get("mapping", {})
    if not isinstance(mapping, dict) or not mapping or set(mapping) - ALLOWED_MAPPING:
        raise ValueError("Mapeo inválido; campos admitidos: code, description, base, listing, quantity, logistics")
    for col in mapping.values(): _column(col)
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("Cada campo debe tener una columna de origen diferente")
    params = config.get("parameters", {})
    formulas = config.get("formulas", {})
    overrides = config.get("overrides", {})
    if not isinstance(params, dict) or not isinstance(formulas, dict) or not isinstance(overrides, dict):
        raise ValueError("Parámetros, fórmulas y correcciones deben ser objetos")
    for name, value in params.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) or CELL.fullmatch(name) or name.upper() in {"TRUE", "FALSE"}:
            raise ValueError("Nombre de parámetro inválido")
        _number(value)
    for col, formula in formulas.items():
        _column(col)
        if not isinstance(formula, str) or not formula.startswith("=") or len(formula) > 4096:
            raise ValueError("Regla de fórmula inválida")
        # Unknown or unsafe formulas remain reviewable as pending, never executed.
    for coordinate, value in overrides.items():
        match = CELL.fullmatch(coordinate)
        if not match or "$" in coordinate or coordinate != coordinate.upper():
            raise ValueError("Coordenada de corrección inválida")
        _column(match[1])
        if int(match[2]) >= start and int(match[2]) <= len(selected["rows"]):
            if isinstance(value, (list, dict)) or len(str(value)) > 32767:
                raise ValueError("Valor de corrección no admitido")
            _scalar(value)
        else:
            raise ValueError("Las correcciones solo afectan filas de datos existentes")
    config.update(header_rows=sorted(headers), data_start=start, sheet_kind=sheet_kind, mapping=mapping,
                  parameters=params, formulas=formulas, overrides=overrides)
    return selected, config


def build_review(workbook: dict, config: dict) -> dict:
    """Produce a standalone JSON-serializable review; never mutates workbook/config."""
    selected, config = _config(workbook, config)
    source_rows = selected["rows"]
    width = max([len(r) for r in source_rows] + [column_index_from_string(c) for c in config["formulas"]] + [0])
    for col in config["mapping"].values():
        if column_index_from_string(col) > width:
            raise ValueError("El mapeo apunta fuera de las columnas de la hoja")
    product_rows, kinds = set(), {}
    for number, row in enumerate(source_rows, 1):
        effective = []
        for i, c in enumerate(row, 1):
            coordinate = f"{get_column_letter(i)}{number}"
            effective.append({"value": config["overrides"][coordinate]} if coordinate in config["overrides"] else c)
        nonempty = [i for i, c in enumerate(effective, 1) if c.get("value") not in (None, "") or c.get("formula")]
        if number in config["header_rows"]:
            kind = "header"
        elif config["sheet_kind"] == "operational":
            kind = "context" if nonempty else "empty"
        elif number < config["data_start"]:
            kind = "context" if nonempty else "empty"
        else:
            codecol = config["mapping"].get("code")
            codeindex = column_index_from_string(codecol) if codecol else None
            # A single descriptive cell is a block label; codes/formulas are products.
            only = effective[nonempty[0]-1] if len(nonempty) == 1 else {}
            descriptive = isinstance(only.get("value"), str) and not only.get("formula")
            baseindex = column_index_from_string(config["mapping"]["base"]) if "base" in config["mapping"] else None
            kind = "empty" if not nonempty else "context" if len(nonempty) == 1 and descriptive and nonempty[0] not in {codeindex, baseindex} else "product"
        if kind == "product": product_rows.add(number)
        kinds[number] = kind
    params = {k: _number(v) for k, v in config["parameters"].items()}
    numeric_columns = {col: field for field, col in config["mapping"].items() if field in {"base", "quantity"}}
    engine = FormulaEngine(workbook["sheets"], params, config["overrides"], config["formulas"], selected["name"], product_rows, numeric_columns)
    headers = []
    for index in range(1, width + 1):
        labels = []
        for number in config["header_rows"]:
            row = source_rows[number - 1]
            value = row[index - 1].get("display") or row[index - 1].get("value") if index <= len(row) else None
            if value is not None and str(value) not in labels: labels.append(str(value))
        headers.append({"column": get_column_letter(index), "label": " / ".join(labels)})
    rows = []
    for number, original in enumerate(source_rows, 1):
        values, issues, evidence = {}, [], {}
        kind = kinds[number]
        for index in range(1, width + 1):
            col, coordinate = get_column_letter(index), f"{get_column_letter(index)}{number}"
            cell = original[index - 1] if index <= len(original) else _cell()
            evidence[col] = copy.deepcopy(cell)
            try:
                values[col] = _scalar(engine.cell(selected["name"], coordinate))
            except FormulaProblem as exc:
                values[col] = None
                issues.append({"column": col, "message": str(exc)})
        mapped = {}
        for field, col in (config["mapping"].items() if kind == "product" else []):
            value = values.get(col)
            if field in {"code", "listing"} and value is not None:
                source = evidence[col]
                value = _display(value, source.get("number_format", "General"))
                if field == "listing" and "\n" in value:
                    issues.append({"column": col, "message": "Varios identificadores; vinculación pendiente"})
            mapped[field] = value
        status = "usable"
        if kind == "product":
            for field in ("code", "base"):
                col = config["mapping"].get(field)
                if col and mapped.get(field) in (None, ""):
                    issues.append({"column": col, "message": "Falta código" if field == "code" else "Falta valor base; no equivale a cero"})
            for field in ("base", "quantity"):
                value, col = mapped.get(field), config["mapping"].get(field)
                if col and value not in (None, ""):
                    try:
                        number_value = _number(value)
                        if number_value < 0 or (field == "quantity" and number_value != int(number_value)):
                            issues.append({"column": col, "message": "Importe negativo o cantidad no entera"})
                            values[col] = None
                        mapped[field] = _scalar(number_value)
                    except FormulaProblem as exc:
                        issues.append({"column": col, "message": str(exc)})
                        values[col] = None
            if "logistics" in mapped and mapped["logistics"] not in (None, "", "own", "full"):
                issues.append({"column": config["mapping"]["logistics"], "message": "Logística inválida; use own o full"})
            if issues: status = "pending"
        rows.append({"row_number": number, "kind": kind, "values": values,
                     "mapped": mapped, "issues": issues, "status": status, "evidence": evidence})
    codes = {}
    for row in rows:
        if row["kind"] == "product" and row["mapped"].get("code") not in (None, ""):
            codes.setdefault(row["mapped"]["code"], []).append(row)
    for group in codes.values():
        if len(group) > 1:
            for row in group:
                row["issues"].append({"column": config["mapping"]["code"], "message": "Código repetido; filas conservadas sin fusionar"})
                row["status"] = "pending"
    summary = dict(usable=0, pending=0, rejected=0, context=0, empty=0, total=len(rows))
    for row in rows:
        if row["kind"] in {"context", "header"}: summary["context"] += 1
        elif row["kind"] == "empty": summary["empty"] += 1
        else: summary[row["status"]] += 1
    return {"sheet": selected["name"], "headers": headers, "rows": rows,
            "summary": summary, "config": config, "merges": copy.deepcopy(selected.get("merges", []))}


def _write_safe(ws, row, col, value):
    c = ws.cell(row, col)
    c.value = value
    # Explicit string type prevents Excel/LibreOffice formula injection, including
    # user overrides that start with =,+,-,@ and historical formula evidence.
    if isinstance(value, str): c.data_type = "s"
    return c


def export_review(review: dict) -> bytes:
    """Export only stored reviewed values. No read_workbook/build_review calls."""
    book = Workbook()
    data = book.active
    data.title = "Datos"
    report = book.create_sheet("Informe")
    report.append(["Hoja origen", "Fila", "Tipo", "Estado", "Columna", "Motivo",
                   "Original", "Fórmula histórica", "Resultado guardado", "Valor revisado"])
    for row in review["rows"]:
        number = row["row_number"]
        for col, value in row["values"].items():
            c = _write_safe(data, number, column_index_from_string(col), value)
            fmt = row.get("evidence", {}).get(col, {}).get("number_format", "General")
            c.number_format = fmt
            if row["kind"] == "header":
                c.font = Font(bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor="19394A")
        # One entry per source row even when it has no issue; all issues retained.
        issues = row["issues"] or [{"column": "", "message": "Sin incidencias"}]
        for issue in issues:
            col = issue["column"]
            ev = row.get("evidence", {}).get(col, {})
            items = [review["sheet"], number, row["kind"], row["status"], col,
                     issue["message"], ev.get("value"), ev.get("formula"), ev.get("cached"), row["values"].get(col)]
            target = report.max_row + 1
            for index, value in enumerate(items, 1): _write_safe(report, target, index, value)
    for merged in review.get("merges", []):
        # Restore header/context layout only; never hide product values in merges.
        try:
            from openpyxl.worksheet.cell_range import CellRange
            area = CellRange(merged)
            if all(r["kind"] in {"header", "context", "empty"} for r in review["rows"] if area.min_row <= r["row_number"] <= area.max_row):
                data.merge_cells(merged)
        except ValueError:
            continue
    report.freeze_panes = "A2"
    report.auto_filter.ref = report.dimensions
    data.freeze_panes = f"A{review['config']['data_start']}"
    for ws in (data, report):
        for column in ws.columns:
            ws.column_dimensions[get_column_letter(column[0].column)].width = min(52, max(14, max(len(str(c.value or "")) for c in column) + 2))
    # openpyxl writes current timestamps into core properties and ZIP members.
    # Normalize both so repeated downloads of the same persisted review are exact.
    fixed = datetime(2000, 1, 1)
    book.properties.created = fixed
    book.properties.modified = fixed
    buffer = io.BytesIO()
    book.save(buffer)
    book.close()
    normalized = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as original:
        with zipfile.ZipFile(normalized, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for name in sorted(original.namelist()):
                payload = original.read(name)
                if name == "docProps/core.xml":
                    payload = re.sub(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms:(?:created|modified)>)",
                                     rb"\g<1>2000-01-01T00:00:00Z\g<2>", payload)
                info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                target.writestr(info, payload)
    return normalized.getvalue()
