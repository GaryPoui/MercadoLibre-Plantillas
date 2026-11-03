# API local autenticada

GET/POST /api/suppliers; PUT /api/suppliers/{id} {name,aliases,retired,expected_revision}.
POST /api/suppliers/{id}/scopes {name,currency,price_kind}; PUT /api/supplier-scopes/{id}
{name,currency,price_kind,expected_revision}. GET suppliers incluye scopes y vigentes.
GET /api/supplier-scopes/{id}/sources -> revisiones disponibles por archivo/hoja.
POST /api/supplier-scopes/{id}/preview {review_ids,mode:complete|partial}.
GET /api/supplier-previews/{id}; POST /api/supplier-previews/{id}/activate {}.
GET /api/supplier-scopes/{id}/versions -> metadatos; GET /api/supplier-versions/{id}.
GET /api/supplier-versions/{id}/export -> XLSX inmutable con moneda/significado/origen.
POST /api/supplier-versions/{id}/restore-preview {} -> preview nuevo contra vigente.
GET /api/standardized?source=current y /export?source=current -> solo vigentes.
source=reviews (default) conserva001. Cambiar semántica vigente, vista previa obsoleta,
proveedor retirado, binding ajeno o reutilizar preview activado ->409. Inválidos ->422;
recurso inexistente ->404. Auth/CSRF de001 aplica; cero escrituras ML.
