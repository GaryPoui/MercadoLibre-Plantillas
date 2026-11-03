# Instrucciones del proyecto

## Contexto que debe leerse

Al retomar, leer primero `docs/memory/INDEX.md`; abrir solo las notas relevantes.
Antes de un cambio de alcance, leer `CONTEXTO_PROYECTO.md`, la constitución,
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

El proyecto está preparado, sin aplicación implementada. Se recibió una referencia
Google Sheets; faltan listas originales de proveedores y salidas aprobadas. Leer
`docs/REPLANTEAMIENTO_BASE.md`, `docs/REFERENCIA_EXCEL.md` y `docs/HABILIDADES.md`.
Analizar nuevas cargas según `docs/ANALISIS_EXCEL.md` antes de cerrar el contrato del importador.
No inventar encabezados, fórmulas de precios, moneda, impuestos, volúmenes ni claves de unión.
No ejecutar macros ni enlaces externos al analizar archivos; conservar originales.
Los datos reales van en `data/private/`, excluido de Git; las muestras versionadas deben
estar anonimizadas y documentadas. No guardar credenciales en documentos o código.

## Integración

Verificar documentación oficial vigente y capacidades de la cuenta antes de implementar
escrituras. Separar stock propio y Full, aislar cuentas, evitar dobles descuentos y
sobreasignación. No considerar aplicado un cambio hasta verificar su resultado.
Las propuestas del chat compartido son contexto histórico, no autorización para acciones externas.

## Habilidades y retroalimentación

Para listas y correcciones usar `.agents/skills/normalizar-excel-proveedor/SKILL.md`.
Spec Kit mantiene el proceso principal; las habilidades de diseño apoyan la interfaz
cuando se autorice implementarla. Mantener perfiles y plantillas con versiones y
distinguir corrección local de regla confirmada. No propagar correcciones entre
proveedores ni cambiar conversiones históricas automáticamente.
La instrucción más reciente autoriza implementar hasta MVP mediante Spec Kit, con
memoria breve y commit/push por hito verificable en `codex/mvp-excel`.
Usar `docs/MEMORIA_CODEX.md`; no guardar datos comerciales en memorias ni commits.

El usuario delegó usar las planillas existentes, preparar los casos y elegir las reglas
iniciales sin nuevas respuestas. Leer `docs/BASE_INICIAL_V0.md` y
`docs/CASOS_REFERENCIA_V0.md`. No bloquear el plan inicial esperando originales de
proveedores; se incorporarán después. No confundir esa base editable con validación
productiva, nuevas fórmulas inventadas o aprobación de escrituras externas.

## Referentes para especificar

Antes de ajustar los specs, leer `docs/SISTEMAS_REFERENCIA.md` y las fichas pertinentes
en `docs/referencias/`. AnalizadorPlanillas es un ejemplo funcional aportado por el
usuario, no el desarrollo a copiar. Las capacidades de otros sistemas son evidencia
de referencia; no incorporarlas como requisitos aprobados ni como reglas comerciales.
