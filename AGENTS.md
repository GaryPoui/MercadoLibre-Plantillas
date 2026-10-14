# Instrucciones del proyecto

## Contexto que debe leerse

Antes de desarrollar, leer `CONTEXTO_PROYECTO.md`, `.specify/memory/constitution.md`,
`docs/ALCANCE_MVP.md` y la especificación activa indicada por `.specify/feature.json`.
Comunicar avances y resultados en español claro.

## Desarrollo con Spec Kit

- Usar las habilidades de `.agents/skills/speckit-*` y los scripts de `.specify/`.
- Mantener requisitos de negocio en `spec.md`; decisiones técnicas en el plan e investigación.
- Flujo: especificar → aclarar → planificar → tareas → analizar → implementar → verificar.
- No editar las plantillas oficiales para convertirlas en documentos del proyecto.
- Crear ramas con prefijo `codex/` cuando se necesiten. El directorio de la especificación
  se resuelve mediante `.specify/feature.json`, independientemente del nombre de la rama.

## Estado y datos

El proyecto está preparado, sin aplicación implementada. El usuario enviará los Excel después.
Analizarlos según `docs/ANALISIS_EXCEL.md` antes de cerrar el contrato del importador.
No inventar encabezados, fórmulas de precios, moneda, impuestos, volúmenes ni claves de unión.
No ejecutar macros ni enlaces externos al analizar archivos; conservar originales.
Los datos reales van en `data/private/`, excluido de Git; las muestras versionadas deben
estar anonimizadas y documentadas. No guardar credenciales en documentos o código.

## Integración

Verificar documentación oficial vigente y capacidades de la cuenta antes de implementar
escrituras. Separar stock propio y Full, aislar cuentas, evitar dobles descuentos y
sobreasignación. No considerar aplicado un cambio hasta verificar su resultado.
Las propuestas del chat compartido son contexto histórico, no autorización para acciones externas.
