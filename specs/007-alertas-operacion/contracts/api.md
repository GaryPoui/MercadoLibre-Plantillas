# Contratos locales

Router /api/ops autenticado; CSRF en todas las mutaciones. GET /state devuelve datos
locales y remote_enabled=false. POST /accounts, /products, /listings, /links,
/supplier-links crea referencias explícitas. POST /price-rules, /price-previews y
/price-previews/{id}/simulate; /jobs/{id}/retry y /price-previews/{id}/cancel conservan intentos y snapshots.
POST /locations, /lots, /adjustments, /allocations, /inventory-policy, /order-events,
/full-captures, /reconciliations; /lots/{id}/settings exige revisión esperada.
GET /alerts, POST /alerts/{id}/ack, /alerts/{id}/notices; GET /notices/{id}/download
prepara .eml sin enviar. GET /audit con filtros/paginación; /export genera XLSX seguro.
POST /remote/execute siempre bloqueado. Modelos extra=forbid; errores422/409/404/401/403.
GET /audit filtra action, resource, account_id, status, since/until con zona horaria;
before es cursor exclusivo y limit1..200. El contexto conserva estado al momento del evento.
Revisiones de escritura: expected_revision obligatorio al modificar un registro existente.
Cantidades enteras en unidad indivisible declarada; importes decimales no negativos.
