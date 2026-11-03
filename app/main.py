"""Local HTTP application. No Mercado Libre credentials, network calls or writes."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import io
import json
from pathlib import Path
import re
import time
from urllib.parse import urlsplit
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from openpyxl import Workbook
from pydantic import BaseModel, ConfigDict, Field

from . import engine
from .store import Store, Conflict, default_directory
from .standardize import consolidate, export_standardized
from .suppliers import Suppliers, Missing, export_version
from .local_api import install_local_api

MAX_BODY = 12 * 1024 * 1024
MAX_FILE = 10 * 1024 * 1024
COOKIE = "mlpl_session"
STATIC = Path(__file__).parent / "static"


class BodyLimitMiddleware:
    """Count actual bytes, including bodies without Content-Length, before parsing."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        length = headers.get(b"content-length", b"0")
        if length.isdigit() and int(length) > MAX_BODY:
            return await JSONResponse({"detail": "La carga supera el límite de 12 MiB."}, 413)(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > MAX_BODY:
                return await JSONResponse({"detail": "La carga supera el límite de 12 MiB."}, 413)(scope, receive, send)
            chunks.append(message)
            if not message.get("more_body", False):
                break
        position = 0

        async def replay():
            nonlocal position
            if position < len(chunks):
                item = chunks[position]
                position += 1
                return item
            return await receive()

        return await self.app(scope, replay, send)


class PasswordInput(BaseModel):
    password: str = Field(min_length=1, max_length=256)


class ProfileInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    supplier: str = Field(default="", max_length=100)
    config: dict
    profile_id: str | None = None


class CellChange(BaseModel):
    row_number: int = Field(ge=1, le=20000)
    column: str = Field(pattern=r"^[A-Z]{1,2}$")
    value: str | int | float | None


class Corrections(BaseModel):
    changes: list[CellChange] = Field(min_length=1, max_length=1000)
    reason: str = Field(default="Corrección local", max_length=500)


class CatalogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    account_id: str = Field(min_length=1, max_length=100)
    product_key: str = Field(min_length=1, max_length=200)
    listing_id: str = Field(min_length=1, max_length=100)
    variation_id: str = Field(default="", max_length=100)
    price: str | int | float | None = None
    quantity: str | int | float | None = None
    logistics: str = Field(default="own", pattern="^(own|full)$")
    writable_verified: bool = False


class CatalogInput(BaseModel):
    entries: list[CatalogEntry] = Field(max_length=20000)


class CompareInput(BaseModel):
    account_id: str = Field(min_length=1, max_length=100)


class SupplierInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    aliases: list[str] = Field(default_factory=list, max_length=30)
    retired: bool = False
    expected_revision: int | None = Field(default=None, ge=1)


class ScopeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    currency: str = Field(default="", pattern=r"^(?:[A-Za-z]{3})?$", max_length=3)
    price_kind: str = Field(default="", max_length=100)
    expected_revision: int | None = Field(default=None, ge=1)


class SupplierPreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_ids: list[str] = Field(min_length=1, max_length=100)
    mode: Literal["complete", "partial"]


def json_fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def schema_for(workbook, config):
    sheets = workbook.get("sheets", [])
    chosen = next((s for s in sheets if s["name"] == config.get("sheet")), None)
    if chosen is None:
        raise ValueError("La hoja seleccionada no existe.")
    selected = []
    headers = config.get("header_rows", [1])
    if not isinstance(headers, list) or not headers or len(headers) > 20:
        raise ValueError("Elegí entre una y veinte filas de encabezado.")
    for row in headers:
        if type(row) is not int or row < 1 or row > len(chosen["rows"]):
            raise ValueError("Fila de encabezado fuera del rango del archivo.")
        selected.append([c.get("value") for c in chosen["rows"][row-1]])
    return json_fingerprint(selected)


def import_metadata(record):
    fields = {k: v for k, v in record.items() if k != "workbook"}
    fields["sheets"] = []
    for sheet in record["workbook"]["sheets"]:
        fields["sheets"].append({
            "name": sheet["name"], "rows": len(sheet["rows"]),
            "columns": max((len(r) for r in sheet["rows"]), default=0),
            "preview": [[c.get("value") if c.get("formula") is None else c.get("formula")
                         for c in row] for row in sheet["rows"][:12]]})
    return fields


def number_text(value):
    if value is None or value == "":
        return None
    try:
        parsed = Decimal(str(value))
        if not parsed.is_finite() or parsed < 0:
            raise ValueError
    except (ValueError, InvalidOperation):
        raise HTTPException(422, "El catálogo necesita importes/cantidades decimales no negativos y sin símbolo.")
    return str(parsed)


def compare_review(review, entries, account_id):
    scoped = [e for e in entries if e["account_id"] == account_id]
    differences = []
    for row in review["rows"]:
        if row["kind"] != "product":
            continue
        mapped = row.get("mapped", {})
        key = str(mapped.get("code") or "")
        listing = str(mapped.get("listing") or "")
        candidates = [e for e in scoped if e["product_key"] == key]
        if listing:
            candidates = [e for e in candidates if e["listing_id"] == listing]
        candidate = candidates[0] if len(candidates) == 1 else None
        reasons = []
        status = "ready"
        if not key or not candidates:
            status = "unlinked"
            reasons.append("Sin vínculo inequívoco en la cuenta seleccionada.")
        elif len(candidates) != 1:
            status = "ambiguous"
            reasons.append("Más de un destino posible; no se elige por descripción.")
        elif candidate["logistics"] == "full":
            status = "full"
            reasons.append("Full es de solo lectura.")
        elif not candidate["writable_verified"]:
            status = "unverified"
            reasons.append("Capacidad de edición no verificada en este catálogo controlado.")
        if row["status"] != "usable":
            status = "invalid"
            reasons.append("La fila tiene datos pendientes o rechazados.")
        blocked = status != "ready"
        differences.append({"row_number": row["row_number"], "product_key": key,
                            "account_id": account_id, "listing_id": candidate["listing_id"] if candidate else None,
                            "current_price": candidate.get("price") if candidate else None,
                            "proposed_price": mapped.get("base"),
                            "current_quantity": candidate.get("quantity") if candidate else None,
                            "proposed_quantity": mapped.get("quantity"),
                            "status": status, "blocked": blocked, "reasons": reasons,
                            "eligible": not blocked, "reason": reasons[0] if reasons else "Comparación local válida; no aplicada."})
    return {"account_id": account_id, "source": "controlled_local_catalog", "differences": differences,
            "remote_writes": 0}


def create_app(data_dir: Path | None = None):
    app = FastAPI(title="MercadoLibre · Plantillas", docs_url=None, redoc_url=None)
    store = Store(Path(data_dir) if data_dir else default_directory())
    app.state.store = store
    suppliers = Suppliers(store)
    login_failures = defaultdict(list)

    @app.middleware("http")
    async def local_access(request: Request, call_next):
        host = request.headers.get("host", "").split(":", 1)[0].lower()
        if host not in {"localhost", "127.0.0.1", "testserver"}:
            return JSONResponse({"detail": "Host no permitido en modo local."}, 400)
        origin = request.headers.get("origin")
        if origin and (urlsplit(origin).netloc.lower() != request.headers.get("host", "").lower()
                       or urlsplit(origin).scheme not in {"http", "https"}):
            return JSONResponse({"detail": "Origen no permitido."}, 403)
        if request.url.path.startswith("/api/") and request.method not in {"GET", "HEAD", "OPTIONS"}:
            if request.url.path not in {"/api/auth/setup", "/api/auth/login"}:
                session = store.session(request.cookies.get(COOKIE))
                if not session:
                    return JSONResponse({"detail": "Iniciá sesión para continuar."}, 401)
                if not hmac.compare_digest(request.headers.get("x-csrf-token", ""), session["csrf"]):
                    return JSONResponse({"detail": "La sesión necesita validación de origen (CSRF)."}, 403)
        response = await call_next(request)
        response.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
                                 "Referrer-Policy": "no-referrer", "Cache-Control": "no-store",
                                 "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"})
        return response

    app.add_middleware(BodyLimitMiddleware)

    @app.exception_handler(Conflict)
    async def conflict_error(request, error):
        return JSONResponse({"detail": str(error)}, 409)

    @app.exception_handler(Missing)
    async def missing_supplier_record(request, error):
        return JSONResponse({"detail": str(error)}, 404)

    @app.exception_handler(ValueError)
    async def invalid_error(request, error):
        return JSONResponse({"detail": str(error)}, 422)

    def require_session(request):
        session = store.session(request.cookies.get(COOKIE))
        if not session:
            raise HTTPException(401, "Iniciá sesión para continuar.")
        return session

    def get_record(kind, ident):
        record = store.get(kind, ident)
        if record is None:
            raise HTTPException(404, "No se encontró el registro.")
        return record

    def session_response():
        token, csrf = store.new_session()
        response = JSONResponse({"configured": True, "authenticated": True, "csrf": csrf})
        response.set_cookie(COOKIE, token, httponly=True, samesite="strict", max_age=8*3600, path="/")
        return response

    @app.get("/api/auth/status")
    def auth_status(request: Request):
        session = store.session(request.cookies.get(COOKIE))
        return {"configured": store.configured(), "authenticated": bool(session),
                "csrf": session["csrf"] if session else None}

    @app.post("/api/auth/setup")
    def setup(payload: PasswordInput):
        if len(payload.password) < 12:
            raise HTTPException(422, "La contraseña necesita al menos 12 caracteres.")
        store.configure(payload.password)
        return session_response()

    @app.post("/api/auth/login")
    def login(payload: PasswordInput, request: Request):
        key = request.client.host if request.client else "local"
        recent = [x for x in login_failures[key] if x > time.time()-300]
        login_failures[key] = recent
        if len(recent) >= 5:
            raise HTTPException(429, "Demasiados intentos. Esperá cinco minutos.")
        if not store.verify_password(payload.password):
            login_failures[key].append(time.time())
            raise HTTPException(401, "Contraseña incorrecta o acceso sin configurar.")
        login_failures.pop(key, None)
        return session_response()

    @app.post("/api/auth/logout")
    def logout(request: Request):
        store.logout(request.cookies.get(COOKIE))
        response = JSONResponse({"authenticated": False})
        response.delete_cookie(COOKIE, path="/")
        return response

    @app.post("/api/imports")
    async def upload(request: Request, file: UploadFile = File(...)):
        require_session(request)
        filename = re.sub(r"[^\w.() -]", "_", Path((file.filename or "archivo").replace("\\", "/")).name)[:160]
        if Path(filename).suffix.lower() not in {".xlsx", ".csv"}:
            await file.close()
            raise HTTPException(422, "Formatos admitidos: XLSX y CSV UTF-8. No se ejecutan macros.")
        content = bytearray()
        try:
            while chunk := await file.read(65536):
                content.extend(chunk)
                if len(content) > MAX_FILE:
                    raise HTTPException(413, "El archivo supera el límite de 10 MiB.")
        finally:
            await file.close()
        workbook = engine.read_workbook(bytes(content), filename)
        return import_metadata(store.create_import(filename, bytes(content), workbook))

    @app.get("/api/imports")
    def list_imports(request: Request):
        require_session(request)
        return [{k: v for k, v in r.items() if k != "workbook"} for r in store.list("import")]

    @app.get("/api/imports/{ident}")
    def get_import(ident: str, request: Request):
        require_session(request)
        metadata = import_metadata(get_record("import", ident))
        metadata["reviews"] = [{k: r[k] for k in ("id", "created_at", "parent_id", "profile_version_id", "summary")}
                               for r in store.list("review") if r["import_id"] == ident]
        return metadata

    @app.post("/api/imports/{ident}/reviews")
    def make_review(ident: str, config: dict, request: Request):
        require_session(request)
        source = get_record("import", ident)
        config = deepcopy(config)
        profile_id = config.get("profile_version_id")
        if profile_id:
            if not isinstance(profile_id, str):
                raise HTTPException(422, "Identificador de perfil inválido.")
            profile = get_record("profile", profile_id)
            if profile["retired"]:
                raise Conflict("Perfil retirado: elegí una versión activa o guardá otra versión.")
            if config.get("supplier", profile["supplier"]) != profile["supplier"]:
                raise Conflict("El perfil pertenece a otro proveedor.")
            merged = deepcopy(profile["config"])
            merged.update(config)
            # A chosen profile's structural signature cannot be overridden by the client.
            if profile["config"].get("_schema"):
                merged["_schema"] = profile["config"]["_schema"]
            config = merged
        fingerprint = schema_for(source["workbook"], config)
        if config.get("_schema") and config["_schema"] != fingerprint:
            raise Conflict("Cambió la estructura del archivo; revisá el perfil antes de reutilizarlo.")
        config["_schema"] = fingerprint
        result = engine.build_review(source["workbook"], config)
        return store.create_review(ident, result, config.get("parent_id"), profile_id)

    @app.get("/api/reviews/{ident}")
    def get_review(ident: str, request: Request):
        require_session(request)
        return get_record("review", ident)

    @app.post("/api/reviews/{ident}/corrections")
    def correct_review(ident: str, payload: Corrections, request: Request):
        require_session(request)
        previous = get_record("review", ident)
        source = get_record("import", previous["import_id"])
        if source["latest_review_id"] != ident:
            raise Conflict("La revisión ya tiene una versión posterior.")
        config = deepcopy(previous["config"])
        overrides = dict(config.get("overrides", {}))
        for change in payload.changes:
            if len(str(change.value or "")) > 32767:
                raise HTTPException(422, "La celda supera el tamaño permitido.")
            overrides[f"{change.column}{change.row_number}"] = change.value
        config["overrides"] = overrides
        config["correction_reason"] = payload.reason
        config["parent_id"] = ident
        result = engine.build_review(source["workbook"], config)
        return store.create_review(source["id"], result, ident, previous.get("profile_version_id"))

    @app.get("/api/reviews/{ident}/export")
    def download(ident: str, request: Request):
        require_session(request)
        review = get_record("review", ident)
        content = engine.export_review(review)
        return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f'attachment; filename="revision_{ident}.xlsx"'})

    @app.get("/api/profiles")
    def list_profiles(request: Request):
        require_session(request)
        return store.list("profile")

    @app.post("/api/profiles")
    def save_profile(payload: ProfileInput, request: Request):
        require_session(request)
        config = deepcopy(payload.config)
        # A correction belongs to a review, not to a reusable supplier rule.
        for key in ("overrides", "parent_id", "correction_reason", "profile_version_id"):
            config.pop(key, None)
        if not config.get("sheet") or not isinstance(config.get("mapping"), dict):
            raise HTTPException(422, "El perfil necesita hoja y correspondencias de columnas.")
        return store.create_profile(payload.name.strip(), payload.supplier.strip(), config, payload.profile_id)

    @app.post("/api/profiles/{ident}/retire")
    def retire_profile(ident: str, request: Request):
        require_session(request)
        get_record("profile", ident)
        return store.retire(ident)

    @app.get("/api/catalog")
    def list_catalog(request: Request):
        require_session(request)
        return store.catalog()

    @app.get("/api/standardized")
    def standardized(request: Request, source: Literal["reviews", "current"] = "reviews"):
        require_session(request)
        if source == "current":
            return suppliers.current()
        return consolidate(store.latest_sources())

    @app.get("/api/standardized/export")
    def standardized_export(request: Request, source: Literal["reviews", "current"] = "reviews"):
        require_session(request)
        snapshot = suppliers.current() if source == "current" else consolidate(store.latest_sources())
        content = export_version(snapshot) if source == "current" else export_standardized(snapshot)
        return Response(content,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": 'attachment; filename="lista_unificada.xlsx"'})

    @app.get("/api/suppliers")
    def list_suppliers(request: Request):
        require_session(request)
        return suppliers.list()

    @app.post("/api/suppliers")
    def create_supplier(payload: SupplierInput, request: Request):
        require_session(request)
        return suppliers.save_supplier(payload.model_dump())

    @app.put("/api/suppliers/{ident}")
    def update_supplier(ident: str, payload: SupplierInput, request: Request):
        require_session(request)
        return suppliers.save_supplier(payload.model_dump(), ident)

    @app.post("/api/suppliers/{ident}/scopes")
    def create_scope(ident: str, payload: ScopeInput, request: Request):
        require_session(request)
        return suppliers.save_scope(ident, payload.model_dump())

    @app.put("/api/supplier-scopes/{ident}")
    def update_scope(ident: str, payload: ScopeInput, request: Request):
        require_session(request)
        scope = get_record("supplier_scope", ident)
        return suppliers.save_scope(scope["supplier_id"], payload.model_dump(), ident)

    @app.get("/api/supplier-scopes/{ident}/sources")
    def supplier_sources(ident: str, request: Request):
        require_session(request)
        return suppliers.sources(ident)

    @app.post("/api/supplier-scopes/{ident}/preview")
    def supplier_preview(ident: str, payload: SupplierPreviewInput, request: Request):
        require_session(request)
        return suppliers.preview(ident, payload.review_ids, payload.mode)

    @app.get("/api/supplier-previews/{ident}")
    def get_supplier_preview(ident: str, request: Request):
        require_session(request)
        return get_record("supplier_preview", ident)

    @app.post("/api/supplier-previews/{ident}/activate")
    def activate_supplier_preview(ident: str, request: Request):
        require_session(request)
        return suppliers.activate(ident)

    @app.get("/api/supplier-scopes/{ident}/versions")
    def supplier_versions(ident: str, request: Request):
        require_session(request)
        return suppliers.versions(ident)

    @app.get("/api/supplier-versions/{ident}")
    def supplier_version(ident: str, request: Request):
        require_session(request)
        return get_record("supplier_version", ident)

    @app.get("/api/supplier-versions/{ident}/export")
    def supplier_version_export(ident: str, request: Request):
        require_session(request)
        return Response(export_version(get_record("supplier_version", ident)),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f'attachment; filename="lista_{ident}.xlsx"'})

    @app.post("/api/supplier-versions/{ident}/restore-preview")
    def restore_supplier_version(ident: str, request: Request):
        require_session(request)
        return suppliers.restore_preview(ident)

    @app.post("/api/catalog")
    def replace_catalog(payload: CatalogInput, request: Request):
        require_session(request)
        entries = []
        for entry in payload.entries:
            row = entry.model_dump()
            row["price"] = number_text(row["price"])
            row["quantity"] = number_text(row["quantity"])
            entries.append(row)
        store.set_catalog(entries)
        return {"entries": entries, "source": "controlled_local_catalog", "remote_writes": 0}

    @app.post("/api/reviews/{ident}/compare")
    def compare(ident: str, payload: CompareInput, request: Request):
        require_session(request)
        return compare_review(get_record("review", ident), store.catalog(), payload.account_id)

    @app.get("/api/demo.xlsx")
    def demo(request: Request):
        require_session(request)
        book = Workbook()
        sheet = book.active
        sheet.title = "Muestra"
        sheet.append(["SKU", "PRODUCTO", "PRECIO DE LISTA", "VALOR", "NOTA"])
        sheet.append(["001-EJEMPLO", "Producto sintético A", 100, 150, "Muestra ficticia, no proveedor real"])
        sheet.append(["002-EJEMPLO", "Producto sintético B", 200, None, "Valor ausente para revisar"])
        sheet.append(["003-EJEMPLO", "Producto sintético C", 0, 0, "Cero explícito"])
        buffer = io.BytesIO()
        book.save(buffer)
        book.close()
        return Response(buffer.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": 'attachment; filename="muestra_sintetica.xlsx"'})

    @app.get("/api/health")
    def health():
        return {"status": "ok", "mode": "local", "remote_writes": False}

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    STATIC.mkdir(parents=True, exist_ok=True)
    install_local_api(app, store, require_session)
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


app = create_app()
