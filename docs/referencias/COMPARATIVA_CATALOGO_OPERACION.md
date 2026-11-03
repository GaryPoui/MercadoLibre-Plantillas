# Referentes de catálogo, importación y operación

Fecha de investigación: **2026-11-02** (Argentina).

Objetivo: identificar patrones útiles para MercadoLibre-Plantillas a partir de tres productos con documentación oficial. No se evaluaron cuentas operativas, no se importaron archivos en estos sistemas y no se comprobaron resultados remotos. Las funciones citadas son capacidades declaradas por sus autores; los patrones transferibles son propuestas propias para discusión. No implican contratación, adopción de estos productos ni requisitos aprobados.

## Comparación

| Referente | Foco observado | Patrón que conviene evaluar | Límite para este proyecto |
| --- | --- | --- | --- |
| Akeneo PIM | Catálogo e intercambio estructurado de información de productos | Perfiles explícitos de entrada/salida y errores localizables | No demuestra gestión transaccional de existencias ni integración Mercado Libre |
| Odoo | Importación/exportación de registros relacionados | Identidad estable y separación entre probar e importar | Su esquema e identificadores no determinan los códigos de nuestros proveedores |
| Real Trends | Operación de publicaciones y cuentas de Mercado Libre | Excel como intercambio y cuenta activa visible | Cambiar de cuenta no prueba inventario físico compartido ni prevención de sobreventa |

## 1. Akeneo PIM: perfiles y calidad del catálogo

La documentación describe perfiles con código, tipo de trabajo y configuración; admite importaciones CSV/XLSX. También documenta opciones para omitir la fila completa o solo un valor inválido y conservar un reporte de errores. Estas modalidades deben entenderse según la oferta y versión disponibles; aquí no se probaron. [Fuente oficial: Import your data](https://help.akeneo.com/import-export-data/import-your-data).

En exportación, distingue etiquetas para lectura humana de códigos para reimportación: una salida con etiquetas no sirve para volver a importar bajo ese mecanismo. Permite configurar contenido y ciertos identificadores. [Fuente oficial: Export your products & product models](https://help.akeneo.com/en_US/import-export-data/export-your-products-product-models).

**Transferencia propuesta:** separar perfil del proveedor y plantilla de salida; conservar versión, significado y decisiones confirmadas. Un Excel visualmente semejante al ejemplo puede requerir una representación distinta de la usada para relacionar registros. La política de rechazo debe quedar explícita antes de convertir, sin adoptar silenciosamente importaciones parciales.

**Límite:** Akeneo documenta que para XLSX procesa únicamente la primera hoja y que no distingue mayúsculas de minúsculas en sus identificadores. Por tanto, su importación directa no sirve como modelo literal para interpretar las 17 pestañas del libro de referencia; tampoco corresponde fusionar códigos que solo difieren en mayúsculas sin una decisión del negocio. [Fuente oficial: límites e identificadores de importación](https://help.akeneo.com/import-export-data/import-your-data).

Las páginas revisadas describen intercambio de catálogo, no un contrato de sincronización Mercado Libre. No demuestran reconocimiento arbitrario de nuevos encabezados sin supervisión.

## 2. Odoo: comprobar, identificar y reimportar

La documentación de Odoo 19 indica un paso **Test** antes de **Import**, permite relacionar manualmente columnas y aconseja conservar el External ID para actualizar registros y reconstruir relaciones. Advierte que identificadores duplicados generan conflictos y que cambiar o quitar un ID puede crear duplicados. Es documentación de esa versión, no una prueba ejecutada en nuestra instalación. [Fuente oficial verificada: texto fuente de Export and import data](https://raw.githubusercontent.com/odoo/documentation/19.0/content/applications/essentials/export_import_data.rst).

**Acceso a la evidencia:** las páginas HTML de Odoo devolvieron tiempo de espera al abrirlas directamente; el buscador devolvió fragmentos oficiales. Para confirmar las afirmaciones se leyó posteriormente el texto completo del repositorio oficial `odoo/documentation`, rama `19.0`: pasos Test/Import en líneas 103–110, External ID y conflictos en 153–167 y riesgo de duplicados en 486–489. No se presenta como acceso exitoso al HTML ni como prueba funcional.

**Transferencia propuesta:** una carga debe producir primero un resultado revisable. Identificar por separado el registro de origen, el producto del catálogo y su destino comercial. Conservar la relación elegida para futuras cargas, sin tratar el nombre del producto como clave suficiente.

**Límite:** External ID es una convención de Odoo. No obliga a pedir esa columna en Excel ni prueba que el SKU de un proveedor sea único. La validación de formato tampoco confirma el significado de un precio, una moneda o un stock. No se evaluaron módulos de inventario ni conectores de Mercado Libre.

## 3. Real Trends: Excel y contexto de cuenta

El sitio oficial mexicano describe un recorrido de descarga del Excel de publicaciones, edición y carga para actualizar precios y stock. También declara sincronización entre Mercado Libre y su Tienda. El alcance regional y las restricciones efectivas deben comprobarse antes de atribuir esas funciones a una cuenta argentina. [Fuente oficial: preguntas frecuentes de Real Trends México](https://www.real-trends.com/mx/).

Su centro de ayuda en español documenta Multicuenta: conectar cada cuenta, vincular mediante invitación aceptada y cambiar entre ellas. La evidencia respalda una operación de cuentas vinculadas; no demuestra un stock único compartido entre vendedores. [Fuente oficial: Qué es y para qué me sirve Multicuenta](https://ayuda.real-trends.com/es/articles/2741036-que-es-y-para-que-me-sirve-multicuenta).

**Transferencia propuesta:** mostrar la cuenta activa y el alcance de la operación durante toda la revisión. Mantener un archivo de intercambio con identificación del destino y ofrecer un recorrido de descarga/corrección/nueva carga que conserve trazabilidad.

**Límite:** no se comprobó cómo estos recorridos tratan Full, depósitos compartidos, reservas, concurrencia, reintentos o escrituras verificadas. La sincronización Mercado Libre–Tienda no equivale a sincronización entre varios vendedores. No se adopta publicación automática ni gestión de mensajes, fuera del MVP actual.

## Aplicación al replanteamiento

Los tres referentes sugieren separar identidad, perfil, validación y destino. La propuesta para discutir es que cada nueva plantilla o corrección mejore un perfil versionado y revisable, con alcance conocido, en lugar de modificar reglas generales sin evidencia. Esto no demuestra aprendizaje automático ni justifica incorporarlo todavía.

Antes de aprobar estos patrones se necesitan ejemplos reales completos, interpretación de los campos, casos de repetición y una definición de salida aceptable. El proyecto mantiene sus propias restricciones: originales conservados, datos privados fuera de Git, stock propio y Full separados, cuentas aisladas y resultados remotos verificados. Ninguna capacidad comercial documentada en otro producto sustituye esas comprobaciones.
