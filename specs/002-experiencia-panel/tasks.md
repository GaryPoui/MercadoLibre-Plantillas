# Tasks: Experiencia del panel

## Phase 1: Especificación y base
- [X] T001 Documentar diseño, contratos, cobertura de FR001/007 y mapa de entregas futuras en specs/002-experiencia-panel/ y docs/HOJA_DE_RUTA.md.

## Phase 2: US1 Inicio
- [X] T002 [US1] Crear Inicio con métricas/cargas reales y estados vacíos/error en app/static/index.html y app/static/app.js (FR001/002/006, SC001).

## Phase 3: US2 Carga guiada
- [X] T003 [US2] Diseñar navegación, progreso y mapeo letra/encabezado; conservar operaciones en app/static/ (FR003/004/006, SC002/004).

## Phase 4: US3 Revisión
- [X] T004 [US3] Mejorar tablas, SKU/precio, filtros y descarga, diseño responsivo/foco en app/static/ (FR005/006/007, SC003/004).

## Phase 5: Verificación y entrega
- [X] T005 Ampliar scripts/browser-smoke.cjs para Inicio, progreso, columnas, filtros, vacío y móvil; ejecutar pytest y capturas (SC001/004).
- [X] T006 Actualizar README, validación, docs/memory; reiniciar servidor conservando datos, commit/push (FR007).

Dependencias: T001→T002→T003→T004→T005→T006. Tests previos de001 permanecen.
