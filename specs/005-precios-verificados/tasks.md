# Tareas: Propuestas y simulación de precios

## Phase 1: Contrato local
- [x] T001 Registrar alcance local y condiciones remotas diferidas en spec/plan/modelo/contratos.

## Phase 2: Reglas y persistencia
- [x] T002 Implementar reglas explícitas, snapshots, conflictos, ejecución simulada e idempotencia/reconciliación de reintentos en app/local_pricing.py y app/local_core.py.

## Phase 3: API y experiencia
- [x] T003 Exponer rutas autenticadas en app/local_api.py y formularios/tablas en app/static/local.*.

## Phase 4: Verificar y entregar
- [x] T004 Probar aislamiento, concurrencia, conflictos, historia e idempotencia en tests/test_local_ops.py; Chrome local, memoria y commit/push.

T001→T002→T003→T004. Requisitos remotos no se marcan como cumplidos por probar simulador.

## Diferido por instrucción del usuario (fuera de esta entrega local)
- [ ] R001 contratos/capacidades reales, lectura previa, aplicación/verificación de precios, espera y recuperación de red.

Cobertura y evidencia: [analysis.md](analysis.md). No activar con referencias sintéticas.
