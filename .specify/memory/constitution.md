# MercadoLibre-Plantillas Constitution

## Core Principles

### I. Especificaciones basadas en datos reales

Cada funcionalidad DEBE describir su alcance, escenarios de aceptación y supuestos antes
de implementarse. Los formatos de importación, las claves de vinculación y las reglas
comerciales DEBEN derivarse de los Excel del usuario y decisiones documentadas.
Los ejemplos ficticios DEBEN identificarse como tales y NO DEBEN fijar el contrato real.
Los archivos originales DEBEN conservarse sin modificaciones durante su análisis.

### II. Integridad del inventario compartido

Cada existencia física DEBE representarse una sola vez, aunque se venda por varias cuentas.
Los movimientos de ventas DEBEN ser idempotentes y las reservas/asignaciones NO DEBEN
superar la disponibilidad definida. El stock propio y Full DEBEN mantenerse separados.
Full DEBE tratarse como información gestionada por Mercado Libre, sin escrituras directas.
Las ventas, cancelaciones y ajustes DEBEN tener trazabilidad suficiente para conciliar cantidades.

### III. Sincronización verificable y recuperable

Cada campo sincronizado DEBE tener una autoridad documentada. Los cambios simultáneos
DEBEN generar conflictos explícitos, sin una regla universal de último cambio ganador.
Los cambios remotos DEBEN validarse y verificarse; un envío aceptado NO equivale por sí solo
a sincronización confirmada. Las tareas DEBEN soportar duplicados, reintentos y conciliación.
Las capacidades de cada cuenta y los contratos externos DEBEN comprobarse contra
documentación oficial vigente antes de implementar escrituras.

### IV. Seguridad y aislamiento por cuenta

Las credenciales DEBEN permanecer en el servidor, fuera de archivos versionados, exportaciones
y registros visibles. Cada operación DEBE identificar la cuenta y el recurso correspondiente.
El acceso al panel y sus acciones DEBEN estar autenticados y autorizados antes de uso real.
Las pruebas de escritura DEBEN empezar con recursos controlados y cambios acotados.
Los errores DEBEN poder investigarse sin revelar tokens ni datos privados innecesarios.

### V. Alcance incremental y validación proporcional

El desarrollo DEBE avanzar por funcionalidades comprobables, manteniendo un backend modular
y adaptadores separados de las reglas de negocio. La complejidad adicional DEBE justificarse
por un requisito real. Las pruebas DEBEN cubrir riesgos comerciales: doble descuento,
sobreasignación, aislamiento de cuentas, errores de importación y recuperación de operaciones.
Los cambios de documentación y preparación DEBEN verificarse con controles de estructura
y consistencia; no requieren pruebas de aplicación inexistente.

## Restricciones del producto

- Requisitos confirmados: Excel, varias cuentas, stock propio y Full, sincronización bidireccional.
- La persistencia central conserva estado e historial; Excel sirve para importar y exportar.
- El MVP devuelve una descarga actualizada; modificar un Excel local automáticamente queda fuera.
- El MVP incluye catálogo, precios, inventario, ventas, alertas y auditoría.
- La importación inicial muestra diferencias; la automatización exige reglas definidas y acotadas.
- El stack de referencia es FastAPI, React/TypeScript, PostgreSQL y workers con Redis/Celery.
  Es una propuesta del chat anterior, pendiente de evaluación en el plan, no una decisión del usuario.
- No se fijan aún columnas, fórmulas de precios, monedas, impuestos, volúmenes ni depósitos reales.

## Flujo de desarrollo

1. Leer CONTEXTO_PROYECTO.md y la especificación activa.
2. Analizar los Excel y registrar evidencias, mapeos y preguntas pendientes.
3. Completar la especificación y resolver decisiones que afecten el contrato de datos.
4. Elaborar plan, investigación técnica, modelo y contratos con Spec Kit.
5. Derivar tareas y comprobar su consistencia antes de implementar.
6. Implementar por escenarios; validar y registrar limitaciones reales antes de declarar terminado.

No se cerrará el contrato del importador ni se declarará listo para desarrollo hasta revisar
los archivos prometidos por el usuario. Esta regla no impide preparar documentación y herramientas.

## Governance

Esta constitución guía los planes, tareas y revisiones del proyecto. Las instrucciones explícitas
del usuario prevalecen y los cambios de alcance se documentan. Toda modificación DEBE incluir
el motivo, su impacto sobre especificaciones y una nueva versión: MAJOR para principios
incompatibles, MINOR para ampliaciones y PATCH para aclaraciones. Cada plan DEBE verificar
el cumplimiento o justificar sus excepciones. Mantener separadas decisiones confirmadas,
propuestas técnicas y hechos externos verificados. La información histórica del chat no sustituye
la documentación vigente ni autoriza acciones externas.

**Version**: 1.0.0 | **Ratified**: 2026-10-14 | **Last Amended**: 2026-10-14
