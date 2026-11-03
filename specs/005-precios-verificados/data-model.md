# Modelo local: Propuestas y simulación de precios

Tipos records con prefijo ops_: account, product, listing, listing_snapshot, product_link,
supplier_link, price_rule/version, price_preview/job, location, lot, allocation, order,
event, movement, inventory_policy/version, full_capture, reconciliation, alert, notice.
IDs estables, revisiones esperadas y origen local/manual/simulado. Auditoría existente
con contexto separado por ID. Ninguna credencial ni estado OAuth en estos registros.
Snapshots/exportaciones usan valores guardados; las mutaciones conservan intentos.
