# Tasks: MVP Excel

**Input**: spec.md, plan.md, research.md, data-model.md, contracts/api.md.
Pruebas requeridas por riesgos de integridad; cada hito memoria/commit/push.

## Phase 1: Setup
- [X] T001 Crear entorno aislado y dependencias fijadas en requirements.txt y pyproject.toml.
- [X] T002 Registrar memorias por hito y autorización vigente en docs/memory/INDEX.md y AGENTS.md.

## Phase 2: Foundational
- [ ] T003 Crear persistencia SQLite, originales privados, sesiones y concurrencia en app/store.py y tests/test_store.py (FR-010/012/018/020/024).
- [ ] T004 Crear API autenticada, límites de cuerpo y controles Host/Origin/CSRF en app/main.py y tests/test_api.py (FR-024).

## Phase 3: US1 Interpretar y revisar
- [X] T005 [US1] Leer XLSX/CSV con tipos, fórmulas, origen y límites en app/engine.py (FR-001/002/003/013/016/021).
- [X] T006 [US1] Probar ceros iniciales, vacío/cero, corruptos, ZIP, encabezados múltiples, auxiliares en tests/test_engine.py (SC-001/002/009).
- [ ] T007 [US1] Construir mapeo y revisión con estados, errores y contexto en app/engine.py y app/static/app.js (FR-004/005/007/009).

## Phase 4: US4 Convertir/exportar
- [X] T008 [US4] Evaluar aritmética permitida con ciclos, dependencias y parámetros sin eval en app/engine.py y tests/test_formulas.py (FR-014/021/022).
- [X] T009 [US4] Exportar XLSX de revisión sin reprocesar con informe completo y texto seguro en app/engine.py y tests/test_engine.py (FR-011/014/015/023,SC-004/005/006).

## Phase 5: US3 Historial
- [ ] T010 [US3] Persistir cargas/huellas/revisiones y listar/restaurar/exportar en app/main.py, app/store.py y tests/test_api.py (FR-010/011/012/020/023,SC-008/010).

## Phase 6: US5 Correcciones/perfiles
- [ ] T011 [US5] Corregir celdas solo en nueva revisión; rechazar padre obsoleto en app/main.py y tests/test_api.py (FR-017/020).
- [ ] T012 [US5] Guardar versiones de perfiles/parámetros, retirar y reutilizar en app/main.py y app/static/app.js; tests/test_api.py (FR-018/019/022,SC-007/008/010).

## Phase 7: US2 Comparación controlada
- [ ] T013 [US2] Catálogo local por cuenta, vínculos inequívocos y Full/capacidades bloqueados en app/main.py y tests/test_catalog.py (FR-006/007/008/009,SC-003/005).

## Phase 8: Panel y entrega
- [ ] T014 [P] [US1] Panel de carga, mapeo, filtro, errores y edición en app/static/index.html, app/static/styles.css, app/static/app.js.
- [ ] T015 [US3] Historial, perfiles, comparación y descargas en app/static/app.js; comprobar con scripts/browser-smoke.cjs.
- [ ] T016 Arranque local, fixture sintético rotulado y guía en scripts/start.ps1, app/main.py y README.md.
- [ ] T017 Verificar CAS-01..09 privados cuando disponibles,1000filas y salida inmutable en scripts/verify_private.py y tests/; registrar resultado en docs/VALIDACION_MVP.md.
- [ ] T018 Revisar accesibilidad/UI, tests completos y estado remoto; memoria final en docs/memory/, commit/push.

## Dependencies
T001/002 → T003/004 → T005/006/007 → T008/009 → T010/011/012 → T013 → T015/016/017/018.
T014 puede avanzar tras definir el contrato HTTP, en archivos separados del motor.
Cada historia se prueba con fixture controlado; cuentas reales no son prerequisito.

## Implementation Strategy
M1 diseño y análisis; M2 motor verificado; M3 API/panel persistente; M4 pruebas y entrega.
No marcar tareas hasta observar resultado. Si aparece fallo de integridad, resolver
antes de seguir. Revisión de25%/50%/100% de tarea no es hito publicable por sí misma.
