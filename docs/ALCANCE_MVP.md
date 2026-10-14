# Alcance y decisiones principales

## Confirmado por el usuario

Listas Excel, varias cuentas vendedoras, inventario propio y Mercado Libre Full,
sincronización bidireccional con reglas de conflicto. Los Excel reales se entregarán
después de preparar el proyecto y determinarán la base de trabajo.

## MVP de referencia

| Área | Resultado esperado |
| --- | --- |
| Cuentas | Conexión, lectura y credenciales separadas por vendedor |
| Excel | Mapeo, validación, diferencias y exportación actualizada |
| Catálogo | Productos internos y vínculos a publicaciones/variaciones por cuenta |
| Precios | Cambios válidos, restricciones visibles y resultado remoto verificado |
| Stock | Propio y Full separados; inventario físico compartido sin duplicación |
| Ventas | Movimientos idempotentes, reservas y conciliación |
| Operación | Panel, alertas de faltantes/errores, auditoría y reintentos |

El retorno al Excel en el MVP es una descarga actualizada. El agente para modificar
archivos locales automáticamente queda para una etapa posterior. También quedan fuera
publicación automática de nuevos productos, publicidad, reclamos/mensajes, predicción
de reposición, otros marketplaces y rentabilidad avanzada.

## Autoridad de los datos propuesta

| Dato | Autoridad propuesta | Regla |
| --- | --- | --- |
| Precio objetivo | Lista o regla interna | Detectar cambios externos antes de sobrescribir |
| Stock propio | Inventario central | Movimientos, reservas y asignación por cuenta |
| Full | Mercado Libre | Consulta y conciliación; sin edición directa |
| Estado de orden | Mercado Libre | Procesamiento idempotente |
| Vinculación | Catálogo central | Resolver coincidencias ambiguas explícitamente |

Estas reglas se revisarán con el funcionamiento real del negocio. No representan aún
el contrato de importación ni una política de sobrescritura habilitada.

## Propuesta técnica a evaluar en el plan

Monolito modular con FastAPI, React/TypeScript, PostgreSQL, SQLAlchemy/Alembic,
Redis/Celery, lectores Excel y Docker Compose. Separar adaptadores de Mercado Libre,
importador, catálogo, inventario, sincronización y alertas. La propuesta proviene del chat
previo; no se instalaron estas dependencias ni se creó una aplicación en esta preparación.

## Secuencia de especificaciones

1. `001-importacion-excel`: interpretar archivos y revisar diferencias (borrador existente).
2. Conexión de cuentas y lectura de catálogo: OAuth y vínculos por vendedor.
3. Aplicación y verificación de precios: conflictos, restricciones y reintentos.
4. Inventario compartido, Full y ventas: eventos, reservas y conciliación.
5. Panel operativo, alertas y exportación de estado actualizado.

La numeración posterior es orientativa; crear cada especificación cuando su alcance esté
definido. La conexión/lectura de catálogo precederá a las pruebas de comparación real.

## Pendientes antes del plan del importador

- Excel reales: hojas, encabezados, ejemplos, fórmulas y formatos.
- Identidad del producto y relación entre códigos internos, proveedores y publicaciones.
- Significado de costos/precios, moneda, impuestos, descuentos y redondeos.
- Significado de cantidades, depósitos, unidades y stock compartido.
- Cuentas/logística habilitada, volúmenes y frecuencia de actualización.

Los permisos y endpoints de Mercado Libre deben verificarse en fuentes oficiales antes
de su implementación. No hay cuentas conectadas ni escrituras remotas realizadas.
