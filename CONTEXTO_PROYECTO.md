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
