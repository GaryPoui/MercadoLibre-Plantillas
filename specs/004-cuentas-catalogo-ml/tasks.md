# Tareas: Catálogo local y vínculos

## Phase 1: Contrato local
- [x] T001 Registrar alcance local y condiciones remotas diferidas en spec/plan/modelo/contratos.

## Phase 2: Reglas y persistencia
- [x] T002 Implementar identidades de cuenta local, producto/unidad, publicación/captura manual y vínculos confirmados en app/local_catalog.py y app/local_core.py.

## Phase 3: API y experiencia
- [x] T003 Exponer rutas autenticadas en app/local_api.py y formularios/tablas en app/static/local.*.

## Phase 4: Verificar y entregar
- [x] T004 Probar aislamiento, concurrencia, conflictos, historia e idempotencia en tests/test_local_ops.py; Chrome local, memoria y commit/push.

T001→T002→T003→T004. Requisitos remotos no se marcan como cumplidos por probar simulador.

## Diferido por instrucción del usuario (fuera de esta entrega local)
- [ ] R001 OAuth, identidad de cuenta, renovación/revocación, lectura paginada y capacidades remotas.

Cobertura y evidencia: [analysis.md](analysis.md). No activar con referencias sintéticas.
