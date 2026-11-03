# Tasks: Proveedores y listas vigentes

## Phase 1: Diseño
- [X] T001 Documentar decisiones, modelo y contratos; analizar cobertura de FR001/010 en specs/003-proveedores-listas-vigentes/.

## Phase 2: US1 Identidad
- [X] T002 Crear proveedores/alias/alcances, retiro y revisiones esperadas en app/suppliers.py, app/main.py y tests/test_suppliers.py (FR-001, FR-002, FR-010).

## Phase 3: US2 Versiones vigentes
- [X] T003 Implementar preview/diferencias/snapshot, activación atómica/bindings y conservación de precios/ausentes/alternativas; probar dos activaciones concurrentes en tests/test_suppliers.py (FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, SC-001, SC-003).

## Phase 4: US3 Historia
- [X] T004 Implementar consulta/exportación/restauración y vista de vigentes autenticadas en app/main.py y app/standardize.py; probar historia y persistencia (FR-009, SC-001, SC-002).

## Phase 5: Interfaz
- [X] T005 Crear gestión de proveedores/alcances, selección de revisiones, diferencias, activación e historial en app/static/; ampliar scripts/browser-smoke.cjs (FR-001 a FR-010).

## Phase 6: Entrega
- [X] T006 Suite completa, Chrome, capturas móvil/escritorio, guía/memoria, reinicio sin pérdida de BD y commit/push.

Dependencias secuenciales. Pruebas significativas cubren aislamiento, precios, historia y carreras.
