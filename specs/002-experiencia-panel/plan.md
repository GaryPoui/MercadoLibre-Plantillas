# Implementation Plan: Panel y carga guiada

**Branch**: codex/mvp-excel | **Date**: 2026-11-03 | **Spec**: [spec.md](spec.md)

## Summary
Rediseñar frontend existente, agregar Inicio con datos de APIs actuales y pasos visibles.
Conservar rutas/IDs críticos y reglas del motor. Sin migración, dependencias o escrituras externas.

## Technical Context
JavaScript nativo, HTML semántico y CSS servido por FastAPI. SQLite/motor de001 intactos.
Inicio consulta imports/standardized/profiles con Promise.all; no cache persistente nueva.
CSS en archivo existente, tokens: tinta #172B4D, acción #2156D9, base #F5F7FB,
blanco #FFFFFF, línea #DFE5EF, pendiente #9A5B00. Segoe UI Variable/Text en Windows,
system-ui como respaldo. Tabla SKU/precio como foco, resto discreto y plegable.
Pruebas: pytest existente, browser-smoke ampliado, capturas escritorio/móvil/vacío/mapeo.

## Constitution Check
I: no interpretar nuevos datos ni inventar reglas. II/III: sin movimientos/escrituras.
IV: mismas sesiones/API/CSRF; borrar resumen visible al logout o expiración.
V: cambio frontend acotado, sin framework nuevo. PASS pre-diseño.

## Project Structure
app/static/index.html: Inicio, guía de pasos, navegación y ayudas.
app/static/styles.css: sistema visual responsivo; foco y reduced-motion.
app/static/app.js: contadores, pasos, encabezados de columnas y filtros.
scripts/browser-smoke.cjs: regresión y controles UI; docs/memory: entrega.

## Complexity Tracking
No infraestructura adicional. T001→T002→T003→T004; luego entrega.
Los specs003..007 son trabajos futuros, sin tareas implementadas marcadas.

## Validación posterior
73tests y Chrome ampliado aprobados; capturas revisadas. Sin cambio del motor/BD.
Constitución: PASS posterior. Siguientes specs son documentación de entregas futuras.
