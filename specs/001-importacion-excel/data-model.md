# Modelo persistente
- User: único operador, salt/hash PBKDF2, nunca contraseña plana.
- Session: hash token, csrf,expires; cookie opaca,revocable8h.
- Import: UUID,filename seguro,sha256,original privado,workbook JSON,created_at,
  duplicate_of y latest_review_id. Duplicar conserva carga separada.
- ProfileVersion: id,profile_id,version,name,supplier,config JSON,retired,fecha;
  inmutable salvo retiro. Revisión conserva snapshot de config.
- Review: UUID,import_id,parent_id,profile_version_id,config,rows,summary,fecha;
  inmutable. Corrección/regla crea revisión nueva; padre obsoleto409.
- CatalogEntry: account_id,product_key,listing_id,variation_id,price,quantity,
  logistics own/full,writable_verified=false. Manual/controlado,no ML real.
- Audit: ids/acción/fecha sin logs comerciales.

Filas1-based, columnasletras. Row.kind product/header/context/empty; status
usable/pending/rejected; issues con column/message. Identidad no por descripción.
Original no mutable. Sin movimientos de inventario ni escritura externa.

Proyección StandardizedRow (no tabla nueva): sku,price,description,supplier,filename,
sheet,row_number,review_id,status,issues. Se deriva en un snapshot de la última
revisión por carga; conserva todas las alternativas de cada proveedor/SKU. No es
una identidad de producto global ni cambia el catálogo controlado.
