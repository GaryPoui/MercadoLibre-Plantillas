# MercadoLibre-Plantillas

Integrador de listas Excel, precios, inventario mixto y varias cuentas de Mercado Libre,
con sincronización bidireccional. Preparado para desarrollo guiado por Spec Kit.

## Estado

Herramientas y documentación preparadas. Los Excel reales están pendientes de recibir;
todavía no se implementó la aplicación ni se conectaron cuentas de Mercado Libre.

## Documentos principales

- [Contexto del chat original](CONTEXTO_PROYECTO.md): decisiones confirmadas y propuestas previas.
- [Alcance del MVP](docs/ALCANCE_MVP.md): módulos, reglas y secuencia de trabajo.
- [Constitución](.specify/memory/constitution.md): principios de desarrollo, versión 1.0.0.
- [Primera especificación](specs/001-importacion-excel/spec.md): importación y revisión de Excel.
- [Checklist de la especificación](specs/001-importacion-excel/checklists/requirements.md).
- [Análisis de Excel](docs/ANALISIS_EXCEL.md): cómo determinar el contrato con los archivos reales.
- [Guía de Spec Kit](docs/SPECKIT.md): herramientas, comandos y estado de cada fase.

## Próximo paso

Recibir los Excel, analizar sus hojas/códigos/importes/stock y ajustar la especificación
con evidencias. Después elaborar el plan técnico, los contratos y las tareas.
Los originales y reportes privados se guardan en `data/private/`, excluido de Git.

Las habilidades de Spec Kit están en `.agents/skills/`. El flujo es
`$speckit-specify` → `$speckit-clarify` → `$speckit-plan` → `$speckit-tasks`
→ `$speckit-analyze` → `$speckit-implement`.
