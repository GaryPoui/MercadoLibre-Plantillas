# Modelo

Supplier: id,name,aliases,retired,revision,created_at,updated_at. Nombre/alias normalizados
para evitar identidad ambigua entre proveedores. Edición exige revision esperada.
Scope: id,supplier_id,name,currency,price_kind,current_version_id,revision. Semántica
inmutable desde primera activación; nombre editable con control de revision.
Preview: id,scope_id,parent_id,supplier_revision,scope_revision,review_ids,mode,rows,
differences,can_activate,blockers,summary,created_at,restore_of. Inmutable.
Version: copia exacta de rows/semántica/origen del preview, id nuevo, parent_id,
preview_id,created_at,author=operador_local. Inmutable. Restore crea versión nueva.
Binding: id prefijado por import_id,supplier_id,scope_id. Valida aislamiento al activar.
Rows incluyen currency,price_kind,scope,update_state,price_certified,attempted_review_id.
Audit registra crear/editar/activar/restaurar; solo IDs/acción/fecha.
