# MercadoLibre-Plantillas

Integrador de listas Excel, precios, inventario mixto y varias cuentas de Mercado Libre,
con sincronización bidireccional. Preparado para desarrollo guiado por Spec Kit.

## Estado

Preparación documental ampliada el 2026-11-02. Se analizó una referencia Google Sheets
con 17 pestañas y se integraron habilidades selectivas. El sistema deberá convertir
listas de proveedores y reutilizar correcciones confirmadas con historial. Faltan
originales de proveedores; el usuario autorizó avanzar con las referencias existentes
y decisiones iniciales delegadas. No hay aplicación ni cuentas conectadas.

## Documentos principales

- [Base inicial v0.1](docs/BASE_INICIAL_V0.md) y [casos preparados](docs/CASOS_REFERENCIA_V0.md): decisiones delegadas, salida esperada y reglas editables.
- [Sistemas de referencia e insumos para specs](docs/SISTEMAS_REFERENCIA.md): análisis de AnalizadorPlanillas y seis referentes externos, con evidencia y escenarios candidatos.
- [Replanteamiento de la base](docs/REPLANTEAMIENTO_BASE.md): prioridad de conversión, retroalimentación y decisiones pendientes.
- [Referencia Excel analizada](docs/REFERENCIA_EXCEL.md): hallazgos y límites sin datos comerciales.
- [Habilidades instaladas](docs/HABILIDADES.md): uso, versiones, verificación y selección final.
- [Investigación de sistemas](docs/INVESTIGACION_SISTEMAS.md) y [diseño web](docs/INVESTIGACION_DISENO_WEB.md): fuentes primarias y evaluación.
- [Contexto del chat original](CONTEXTO_PROYECTO.md): decisiones confirmadas y propuestas previas.
- [Alcance del MVP](docs/ALCANCE_MVP.md): módulos, reglas y secuencia de trabajo.
- [Constitución](.specify/memory/constitution.md): principios de desarrollo, versión 1.0.0.
- [Primera especificación](specs/001-importacion-excel/spec.md): importación y revisión de Excel.
- [Checklist de la especificación](specs/001-importacion-excel/checklists/requirements.md).
- [Análisis de Excel](docs/ANALISIS_EXCEL.md): cómo determinar el contrato con los archivos reales.
- [Guía de Spec Kit](docs/SPECKIT.md): herramientas, comandos y estado de cada fase.

## Próximo paso

Elaborar el plan inicial con Spec Kit usando la base v0.1 y los casos preparados.
Incorporar después listas originales y correcciones sin bloquear este avance. Los
perfiles y cálculos serán modificables con versiones. Continúa la etapa sin código.
Los originales y reportes privados se guardan en `data/private/`, excluido de Git.

Las habilidades de Spec Kit están en `.agents/skills/`. El flujo es
`$speckit-specify` → `$speckit-clarify` → `$speckit-plan` → `$speckit-tasks`
→ `$speckit-analyze` → `$speckit-implement`.
