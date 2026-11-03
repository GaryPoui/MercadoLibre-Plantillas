# API local v1 y contrato engine

GET /api/standardized -> {rows, summary:{total,ready,pending,unreviewed_imports}}.
Filas: sku,price,description,supplier,filename,sheet,row_number,review_id,status,issues.
GET /api/standardized/export -> XLSX seguro y determinista del snapshot actual.
Ambas rutas autenticadas. Una fila por producto de la última revisión de cada carga;
no se incluyen revisiones históricas duplicadas ni se aplica deduplicación silenciosa.
Auth: GET /api/auth/status -> {configured,authenticated,csrf?}.
POST /api/auth/setup o /login {password}; POST /logout. Cookie HttpOnly strict,
X-CSRF-Token obligatorio para mutaciones autenticadas; Host/Origin permitidos.
POST /api/imports multipart file -> {id,filename,sha256,duplicate_of,sheets:[{name,rows,columns,preview}]}.
GET /api/imports -> array historial; GET /api/imports/{id} -> metadata/hojas.
POST /api/imports/{id}/reviews config -> Review, incluyendo id,import_id,parent_id,created_at.
GET /api/reviews/{id} -> revisión inmutable completa.
POST /api/reviews/{id}/corrections {changes:[{row_number,column,value}],reason} -> revisión nueva.
GET /api/reviews/{id}/export -> XLSX de esa revisión sin reprocesar; original conserva fórmulas,
salida usa valores certificados y pendientes vacíos con informe completo.
GET /api/profiles -> array; POST /api/profiles {name,supplier,config,profile_id?} -> nueva versión;
POST /api/profiles/{version_id}/retire -> marca retirada, historial intacto.
GET /api/catalog -> array controlado; POST /api/catalog {entries:[...]} reemplaza catálogo local.
POST /api/reviews/{id}/compare {account_id} -> {differences:[...]} solo cuenta elegida;
Full/unverified/ambiguous/unlinked bloqueados. Sin escrituras ML.
GET /api/demo.xlsx -> fixture sintético rotulado; no privados.
Errores400/401/403/404/409/413/422 legibles, nunca rutas/secretos.

## Engine: interfaz compartida
read_workbook(content:bytes,filename:str)->{sheets:[{name,rows:[[{value,formula,cached,display}]],merges:[]}]}.
build_review(workbook,config)->{sheet,headers:[{column,label}],rows:[{row_number,kind,
values:{A:value},mapped:{code:value},issues:[{column,message}],status}],
summary:{usable,pending,rejected,context,empty,total},config}.
export_review(review)->bytes. Export no llama lectura ni build_review.
Config: {sheet,header_rows:[1],data_start:2,mapping:{code:'B',description:'C',base:'F'},
parameters:{factor:'1.21'},formulas:{E:'=D{row}*factor'},overrides:{B2:'001-X'}}.
Formulas por columna, marcador {row} sustituido por número actual. Parámetros numéricos
nombrados permitidos. Sin valores comerciales predeterminados. mapping puede incluir
listing,quantity,logistics además de code/description/base. Correcciones quedan overrides.
Headers mismas posiciones, cabeceras múltiples concatenadas, contexto no producto.
XLSX/CSV UTF8; otros rechazados. XLSX revisado exporta hojas Datos e Informe, con
cabeceras del perfil, contexto y posiciones, fórmulas seguras como valores de revisión.
