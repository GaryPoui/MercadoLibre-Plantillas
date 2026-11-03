# Alcance y decisiones principales

Ampliación2026-11-03: operación local004–007 autorizada mientras falta cuentaML.
Catálogo/vínculos, precios simulados, inventario/ventas manuales y alertas/auditoría
disponibles; conexión/verificación remotas y envío de correo pendientes. Ver
[operación local](OPERACION_LOCAL.md) y [validación](VALIDACION_OPERACION_LOCAL.md).

## Confirmado por el usuario

Listas Excel, varias cuentas vendedoras, inventario propio y Mercado Libre Full,
sincronización bidireccional con reglas de conflicto. El 2026-11-02 se aportó una
referencia Google Sheets de 17 pestañas y se añadió conversión de listas de proveedores
a formatos similares, con retroalimentación mediante futuras cargas y correcciones.
Faltan listas originales, pero el usuario delegó avanzar con las referencias existentes,
preparar casos y basar las reglas en las planillas con cambios posteriores. La base
inicial está en [BASE_INICIAL_V0.md](BASE_INICIAL_V0.md). La autorización posterior
permitió implementar el conversor/revisor local, ver [validación](VALIDACION_MVP.md).
El alcance general de integración descrito abajo todavía no está implementado completo.

## MVP de referencia

| Área | Resultado esperado |
| --- | --- |
| Cuentas | Conexión, lectura y credenciales separadas por vendedor |
| Excel | Conversión a plantillas versionadas, mapeo, validación, diferencias y exportación |
| Correcciones | Perfiles por proveedor/formato e historial de reglas confirmadas |
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

La numeración definitiva y el estado de cada entrega están en
[HOJA_DE_RUTA.md](HOJA_DE_RUTA.md). 001 está implementada; 002 mejora el panel;
003 gestiona listas vigentes; 004..007 cubren integración y operación futuras.
La secuencia orientativa histórica siguiente se conserva como antecedente.

1. `001-importacion-excel`: interpretar, convertir, revisar y exportar sin cuentas conectadas; perfiles y correcciones con alcance explícito (borrador ampliado).
2. Conexión de cuentas y lectura de catálogo: OAuth y vínculos por vendedor.
3. Aplicación y verificación de precios: conflictos, restricciones y reintentos.
4. Inventario compartido, Full y ventas: eventos, reservas y conciliación.
5. Panel operativo, alertas y exportación de estado actualizado.

La numeración posterior es orientativa; crear cada especificación cuando su alcance esté
definido. La conexión/lectura de catálogo precederá a las pruebas de comparación real.

## Base inicial y pendientes de ampliación

La base v0.1 y sus nueve casos permiten planificar el conversor de referencia ahora.
Los puntos siguientes se contrastarán al ampliar perfiles y preparar integración/uso
productivo; no exigen respuestas adicionales para el plan inicial delegado.

- Parejas de Excel originales de proveedores y salidas aprobadas; la referencia ya fue perfilada, ver [análisis](REFERENCIA_EXCEL.md).
- Plantilla(s) elegidas, alcance de semejanza y reglas de reutilización de correcciones.
- Identidad del producto y relación entre códigos internos, proveedores y publicaciones.
- Significado de costos/precios, moneda, impuestos, descuentos y redondeos.
- Significado de cantidades, depósitos, unidades y stock compartido.
- Cuentas/logística habilitada, volúmenes y frecuencia de actualización.

Los permisos y endpoints de Mercado Libre deben verificarse en fuentes oficiales antes
de su implementación. No hay cuentas conectadas ni escrituras remotas realizadas.

El [replanteamiento](REPLANTEAMIENTO_BASE.md) documenta prioridades, propuestas y
pendientes. No se traslada una fórmula observada al producto como regla comercial aprobada.
