"""Authenticated local-only operations API; no credentials or transports accepted."""
from typing import Literal

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictBool

from .local_catalog import LocalCatalog
from .local_inventory import LocalInventory
from .local_operations import LocalOperations
from .local_pricing import LocalPricing


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Revision(Input):
    expected_revision: StrictInt | None = Field(default=None, ge=1)


class Account(Revision):
    id: str | None = None
    name: str = Field(min_length=1, max_length=100)
    active: StrictBool = True


class Product(Input):
    sku: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=200)
    unit: str = Field(min_length=1, max_length=60)


class Listing(Revision):
    account_id: str
    listing_id: str = Field(min_length=1, max_length=100)
    variation_id: str = Field(default="", max_length=100)
    user_product_id: str = Field(default="", max_length=100)
    currency: str = Field(pattern=r"^[A-Za-z]{3}$")
    price_kind: str = Field(min_length=1, max_length=100)
    price: str = Field(min_length=1, max_length=100)
    logistics: Literal["own", "full"]
    simulated_editable: StrictBool


class Link(Revision):
    product_id: str
    listing_record_id: str


class SupplierLink(Revision):
    product_id: str
    scope_id: str
    supplier_sku: str = Field(min_length=1, max_length=200)


class Rule(Revision):
    account_id: str
    scope_id: str
    factor: str = Field(min_length=1, max_length=100)
    charge: str = Field(min_length=1, max_length=100)
    digits: StrictInt = Field(ge=0, le=6)
    target_price_kind: str = Field(min_length=1, max_length=100)
    confirmed: StrictBool


class PricePreview(Input):
    account_id: str
    scope_id: str


class Execute(Input):
    scenario: Literal["success", "reject", "accepted_unchanged", "timeout_before", "timeout_after"]
    confirmed: Literal[True]


class Location(Input):
    name: str = Field(min_length=1, max_length=100)
    kind: Literal["own", "full"]
    account_id: str | None = None


class Lot(Input):
    product_id: str
    location_id: str
    initial_quantity: StrictInt | None = Field(default=None, ge=0, le=10**9)
    safety: StrictInt | None = Field(default=None, ge=0, le=10**9)
    minimum: StrictInt | None = Field(default=None, ge=0, le=10**9)


class LotSettings(Revision):
    safety: StrictInt | None = Field(default=None, ge=0, le=10**9)
    minimum: StrictInt | None = Field(default=None, ge=0, le=10**9)


class Adjustment(Revision):
    lot_id: str
    delta: StrictInt = Field(ge=-10**9, le=10**9)
    reason: str = Field(min_length=1, max_length=500)
    event_id: str = Field(min_length=1, max_length=200)


class Allocation(Revision):
    lot_id: str
    account_id: str
    quantity: StrictInt = Field(ge=0, le=10**9)


class Policy(Revision):
    confirmed: StrictBool


class OrderEvent(Input):
    account_id: str
    lot_id: str
    order_ref: str = Field(min_length=1, max_length=200)
    event_id: str = Field(min_length=1, max_length=200)
    sequence: StrictInt = Field(ge=1, le=10**9)
    status: Literal["reserved", "shipped", "cancelled", "returned"]
    quantity: StrictInt = Field(ge=1, le=10**9)
    returned_total: StrictInt = Field(default=0, ge=0, le=10**9)
    receipt_confirmed: StrictBool = False


class FullCapture(Input):
    lot_id: str
    quantity: StrictInt = Field(ge=0, le=10**9)
    reference: str = Field(min_length=1, max_length=300)
    event_id: str = Field(min_length=1, max_length=200)


class Reconciliation(Input):
    lot_id: str
    observed_quantity: StrictInt = Field(ge=0, le=10**9)
    reference: str = Field(min_length=1, max_length=300)


class Notice(Input):
    recipient: str = Field(min_length=1, max_length=200)


def install_local_api(app, store, require_session):
    def authenticated(request: Request):
        return require_session(request)

    router = APIRouter(prefix="/api/ops", dependencies=[Depends(authenticated)])
    catalog, pricing, inventory, operations = LocalCatalog(store), LocalPricing(store), LocalInventory(store), LocalOperations(store)

    @router.get("/state")
    def state():
        return operations.state()

    @router.post("/accounts")
    def accounts(body: Account):
        return catalog.save_account(body.model_dump())

    @router.post("/products")
    def products(body: Product):
        return catalog.create_product(body.model_dump())

    @router.post("/listings")
    def listings(body: Listing):
        return catalog.save_listing(body.model_dump())

    @router.post("/links")
    def links(body: Link):
        return catalog.link(body.model_dump())

    @router.post("/supplier-links")
    def supplier_links(body: SupplierLink):
        return catalog.link(body.model_dump(), supplier=True)

    @router.post("/links/{kind}/{ident}/retire")
    def retire_link(kind: Literal["product_link", "supplier_link"], ident: str, body: Revision):
        return catalog.retire_link(kind, ident, body.expected_revision)

    @router.post("/price-rules")
    def rules(body: Rule):
        return pricing.rule(body.model_dump())

    @router.post("/price-previews")
    def previews(body: PricePreview):
        return pricing.preview(body.model_dump())

    @router.post("/price-previews/{ident}/simulate")
    def simulate(ident: str, body: Execute):
        return pricing.simulate(ident, body.scenario, body.confirmed)

    @router.post("/jobs/{ident}/retry")
    def retry(ident: str, body: Execute):
        return pricing.retry(ident, body.scenario)

    @router.post("/price-previews/{ident}/cancel")
    def cancel(ident: str):
        return pricing.cancel(ident)

    @router.post("/locations")
    def locations(body: Location):
        return inventory.location(body.model_dump())

    @router.post("/lots")
    def lots(body: Lot):
        return inventory.lot(body.model_dump())

    @router.post("/lots/{ident}/settings")
    def settings(ident: str, body: LotSettings):
        return inventory.settings(ident, body.model_dump())

    @router.post("/adjustments")
    def adjustments(body: Adjustment):
        return inventory.adjustment(body.model_dump())

    @router.post("/allocations")
    def allocations(body: Allocation):
        return inventory.allocation(body.model_dump())

    @router.post("/inventory-policy")
    def policy(body: Policy):
        return inventory.policy(body.model_dump())

    @router.post("/order-events")
    def orders(body: OrderEvent):
        return inventory.order_event(body.model_dump())

    @router.post("/full-captures")
    def full(body: FullCapture):
        return inventory.full_capture(body.model_dump())

    @router.post("/reconciliations")
    def reconciliations(body: Reconciliation):
        return inventory.reconcile(body.model_dump())

    @router.get("/alerts")
    def alerts():
        operations.refresh_alerts()
        return store.list("ops_alert")

    @router.post("/alerts/{ident}/ack")
    def ack(ident: str):
        return operations.acknowledge(ident)

    @router.post("/alerts/{ident}/notices")
    def notices(ident: str, body: Notice):
        return operations.prepare_notice(ident, body.recipient)

    @router.get("/notices/{ident}/download")
    def notice_download(ident: str):
        return Response(operations.notice_bytes(ident), media_type="message/rfc822",
                        headers={"Content-Disposition": 'attachment; filename="aviso_preparado.eml"'})

    @router.get("/audit")
    def audit(action: str = "", resource: str = "", account_id: str = "", status: str = "", since: str | None = None,
              until: str | None = None, before: int | None = Query(default=None, ge=1),
              limit: int = Query(default=100, ge=1, le=200)):
        return operations.audit_rows(action=action, resource=resource, account_id=account_id, status=status,
                                     since=since, until=until, before=before, limit=limit)

    @router.get("/export")
    def export():
        return Response(operations.export(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": 'attachment; filename="estado_local.xlsx"'})

    @router.post("/remote/execute")
    def remote_disabled():
        raise HTTPException(409, "La integración real está deshabilitada. No se guardan credenciales ni se hacen llamadas a Mercado Libre.")

    app.include_router(router)
