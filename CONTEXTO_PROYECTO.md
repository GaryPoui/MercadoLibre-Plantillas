# Contexto del proyecto MercadoLibre-Plantillas

Actualizado: 14 de octubre de 2026.
Fuente leída: https://chatgpt.com/share/6acfcefd-0afc-83e8-a5c2-25ed84c8181a ("Investigar API Mercado Libre").
El usuario pidió leer ese chat e incorporar su contexto. Este archivo conserva el resumen para futuras sesiones del proyecto.

## Objetivo y decisiones confirmadas por el usuario

Desarrollar un sistema de integración con Mercado Libre: ingresar listas de precios, aplicar sus cambios en las publicaciones, recibir cambios de ventas y stock, reflejarlos en el sistema/planillas y notificar faltantes o problemas. La investigación inicial debe servir de base para el desarrollo.

El usuario confirmó explícitamente:
- Origen de listas: Excel.
- Inventario mixto: depósitos propios y Mercado Libre Full.
- Varias cuentas vendedoras.
- Sincronización bidireccional, automática y con reglas de conflicto.

## Arquitectura propuesta en el chat

Estas son propuestas del asistente previo; no se ha verificado una implementación ni una aprobación independiente de cada tecnología:
- Monolito modular: backend Python/FastAPI y panel React/TypeScript.
- PostgreSQL como persistencia central; SQLAlchemy y Alembic.
- Redis y Celery para eventos, tareas y reintentos.
- openpyxl/pandas para importar/exportar Excel; contemplar xlsx, xls y CSV con lectores compatibles.
- Docker Compose para el entorno.
- OAuth por cuenta, credenciales separadas y renovación segura de tokens.

Excel es un medio de importación/exportación; la base central conserva estado e historial. Para el MVP, el retorno a Excel consiste en descargar un archivo actualizado. Modificar automáticamente un archivo local requiere un agente o una carpeta conectada y queda para una etapa posterior.

## MVP propuesto

1. Conectar varias cuentas mediante OAuth y consultar sus publicaciones.
2. Importar Excel con mapeo de columnas, validación, detección de duplicados y vinculación de productos.
3. Catálogo unificado con SKU interno y vínculos por vendedor, item, User Product y variación.
4. Comparar y previsualizar precios/stock, aplicar cambios válidos y verificar el resultado remoto.
5. Inventario propio editable según las capacidades de cada cuenta; Full consultado por separado.
6. Ventas y webhooks, movimientos de inventario idempotentes y conciliación periódica.
7. Exportar Excel con precios, stock y estados de sincronización.
8. Alertas en el panel y por correo: agotamiento, mínimos y errores.
9. Panel con filtros, operaciones, estado de cuentas, auditoría, conflictos y reintentos.

Fuera del MVP propuesto: crear publicaciones automáticamente, reclamos/mensajes, publicidad, cálculo avanzado de comisiones, agente para Excel local, reposición predictiva y otros marketplaces. Telegram/WhatsApp son opciones posteriores.

## Reglas de dominio propuestas

- Precio objetivo: Excel o reglas internas. Detectar cambios externos y conflictos antes de sobrescribir.
- Stock físico propio: inventario central con movimientos y reservas.
- Stock Full y estados de órdenes: autoridad de Mercado Libre.
- Vinculación ambigua de SKU/publicaciones: resolver explícitamente.
- Un depósito compartido entre cuentas representa un único inventario; no duplicar existencias ni descontar dos veces una venta.
- MVP con asignación conservadora por cuenta, reservas y margen de seguridad, sin sobreasignación.
- Eventos duplicados deben ser idempotentes. Evitar ciclos de actualización.
- Registrar intentos y resultados; no considerar sincronizada una operación sin verificar el estado final.
- Primera importación con vista previa; automatización posterior mediante reglas autorizadas.

## Integración externa pendiente de verificar

El chat describe stock tradicional vía /items, stock por User Products y depósitos, control de versiones y conflictos 409; Full solo lectura; restricciones de edición cuando hay automatización de precios; webhooks que notifican recursos para luego consultarlos; colas, reconciliación, recuperación de eventos y manejo de límites 429.

Estos detalles, fechas, permisos, endpoints y tiempos de respuesta provienen de la investigación del chat y NO fueron contrastados de nuevo al guardar este contexto. Antes de implementar, comprobar documentación oficial vigente y capacidades de las cuentas. Tampoco se revisaron aquí los videos citados.

Referencias del chat:
- https://developers.mercadolibre.com.ar/es_ar/api-de-precios
- https://developers.mercadolibre.com.ar/stock-distribuido
- https://developers.mercadolibre.com.ar/automatizaciones-de-precios
- https://developers.mercadolibre.com.ar/es_ar/atributos-y-variaciones/productos-recibe-notificaciones
- https://developers.mercadolibre.com.ar/es_ar/metricas/gestiona-ventas
- https://www.youtube.com/watch?v=3r7rVef3Crg
- https://www.youtube.com/watch?v=P2jt16ZYwsc

## Modelo y API propia propuestos

Entidades: productos, cuentas ML, publicaciones/variaciones, ubicaciones, inventario, reservas/asignaciones por cuenta, movimientos, órdenes, eventos recibidos, importaciones, tareas de sincronización, alertas y auditoría.

Rutas conceptuales bajo /api/v1: accounts, accounts/connect, products, inventory, imports/excel, imports/{id}/preview, imports/{id}/apply, sync, sync/jobs/{id}, webhooks/mercadolibre, alerts y exports/inventory. Son rutas de nuestro backend, no endpoints oficiales de Mercado Libre.

## Orden y criterios de aceptación propuestos

Orden: infraestructura/OAuth/lectura → Excel y precios → inventario y eventos → panel, alertas, exportación y estabilización.

Validar al menos dos cuentas con credenciales separadas; archivos con errores/duplicados; vínculos sin ambigüedad; precio final remoto; restricciones de automatización; Full y stock propio; eventos repetidos sin doble descuento; inventario compartido; tokens vencidos y fallos temporales; exportación actualizada; alertas y auditoría.

## Estado al incorporar este contexto

El chat contiene investigación y diseño, no evidencia de un sistema desarrollado. No aporta credenciales, identificadores reales de cuentas, Excel de ejemplo ni despliegue. Quedan por definir los archivos reales, depósitos/cuentas, reglas comerciales, alertas, alojamiento y capacidades habilitadas. La solicitud actual solo autoriza incorporar contexto; no implica ejecutar todas las propuestas del chat.

## Ampliación confirmada el 2 de noviembre de 2026

El usuario solicita leer el planteamiento, investigar profundamente habilidades de
desarrollo/análisis y diseño web, instalarlas, usar subagentes y replantear la base.
Prohíbe por ahora escribir código de la aplicación. La preparación documental y las
habilidades sí están autorizadas.

Aporta como referencia el libro Google Sheets identificado en el informe privado
`data/private/ANALISIS_MISTICA.md`, con 17 pestañas. La nueva necesidad es convertir
futuras listas de proveedores a formatos similares a los ejemplos y retroalimentar
el sistema con cargas y correcciones. Se propone materializarlo en perfiles y reglas
confirmadas con historial, no en aprendizaje automático indiscriminado.

Se leyeron las cuadrículas completas a través del conector; snapshots y fórmulas reales
quedan en `data/private/`. No se modificó la referencia, no se convirtieron listas y
no se conectaron cuentas. Aún falta definir salidas aprobadas y reglas comerciales.

El resumen histórico anterior se mantiene como tal: el enlace remoto no volvió a
cargar durante esta revisión. Las páginas oficiales de precios/stock de Mercado Libre
devolvieron 403; no se consideran verificadas sus capacidades vigentes.

Continuar desde `docs/REPLANTEAMIENTO_BASE.md`, `docs/REFERENCIA_EXCEL.md`,
`docs/HABILIDADES.md` y la especificación activa ampliada. El stack sigue pendiente
del plan. La siguiente fase será aclarar el contrato con casos entrada/salida reales;
la implementación continúa sin iniciar.

## Investigación de sistemas similares, 2 de noviembre de 2026

El usuario aporta `https://github.com/GaryPoui/AnalizadorPlanillas.git` como referencia
de funciones similares y aclara que este desarrollo será diferente. Solicita analizar
también otros sistemas y sumar documentación para mejorar los specs posteriores.
Esto autoriza investigación y documentación, no modificar el ejemplo ni implementar.

Se revisó estáticamente AnalizadorPlanillas en el commit
`6fd377c6e959feaa5c7e4c3c06354bd164ff6295`, con evidencia de backend, interfaz y
pruebas seleccionadas; no se ejecutó. Se investigaron fuentes oficiales de OpenRefine,
Flatfile, Dromo, Akeneo PIM, Odoo y Real Trends sin probar sus servicios ni subir datos.

La síntesis y matriz de insumos está en `docs/SISTEMAS_REFERENCIA.md`; las fichas están
en `docs/referencias/`. Distinguir declarado, observado en código, propuesto y probado.
La investigación no convierte funciones ajenas en requisitos aprobados ni adopta las
12 columnas, reglas comerciales, stack o IA del ejemplo. Se proponen casos sobre
exportar exactamente lo revisado, alcance de correcciones, calidad frente a cobertura,
filas excluidas, identidad y compatibilidad de perfiles. El contrato sigue abierto.

## Decisiones delegadas para avanzar con las referencias, 2 de noviembre de 2026

El usuario indicó: usar las planillas ya entregadas; recibir después originales de
proveedores; preparar los casos de resultado esperado; basar las reglas en los Excel
con posibilidad de modificarlas; tomar estas decisiones sin esperar más respuestas.

Se adopta `docs/BASE_INICIAL_V0.md` como contrato inicial de referencia para planificar,
no como contrato definitivo de todos los proveedores. Se prepararon nueve casos y dos
filas detalladas de entrada/salida del perfil simple; valores y fórmulas comerciales
están en `data/private/base-inicial/`. Índice anonimizado: `docs/CASOS_REFERENCIA_V0.md`.
Los cálculos seleccionados se contrastaron aritméticamente sin ejecutar fórmulas Excel.

Se decidió iniciar por AD y mantener perfiles separados para otras estructuras,
salida XLSX e informe, cálculos/formatos editables y versionados, corrección local por
defecto y reutilización de mapeos compatibles. Las fórmulas rotas y datos ambiguos
quedan pendientes, sin inventar valores. Los parámetros observados son una referencia
histórica configurable, no tarifas vigentes ni autorización para publicar.

Esta instrucción explícita sustituye el bloqueo anterior de esperar nuevas listas o
aprobación manual de cada decisión para planificar. Se aplica la prioridad del usuario
prevista en la constitución; no se declara compatibilidad con archivos no recibidos ni
preparación para producción. Se mantiene la restricción de no implementar aplicación.
La siguiente fase permitida es el plan inicial con Spec Kit.

## Autorización de implementación y persistencia por hitos

El usuario solicita ejecutar Spec Kit hasta un MVP y crear memoria, commit y push por
avance. Esta instrucción revoca la restricción previa de no escribir aplicación.
Se empieza por el MVP de la especificación activa: conversor/revisor Excel autónomo.
Las integraciones reales de precios/stock/ventas se mantienen como siguientes entregas,
sin afirmar cuentas conectadas ni habilitar escrituras con capacidades desconocidas.
Memoria compacta: `docs/memory/INDEX.md`; notas por hito, hasta120 palabras, sin datos.

## Entrega del MVP local, 3 de noviembre de 2026

Implementada la especificación001 con FastAPI, motorXLSX/CSV, SQLite local fuera de
OneDrive y panel web. Incluye autenticación, correcciones/revisiones, perfiles/reglas
versionados, historial, exportación determinista y comparación por cuenta contra
catálogo controlado.66tests,9casos privados y recorrido Chrome aprobados; detalles
en `docs/VALIDACION_MVP.md`. Instalación y uso en README. Memorias compactas en docs/memory/.
No se conectaron cuentas ni se implementaron escriturasML/ventas/inventario transaccional.
Estas son próximas funcionalidades del objetivo general, no capacidades del MVP actual.
