# Tareas: Alertas y auditoría locales

## Phase 1: Contrato local
- [x] T001 Registrar alcance local y condiciones remotas diferidas en spec/plan/modelo/contratos.

## Phase 2: Reglas y persistencia
- [x] T002 Implementar alertas deduplicadas, reconocimiento/recuperación, mínimos explícitos, auditoría/exportaciones y avisos descargables en app/local_operations.py y app/local_core.py.

## Phase 3: API y experiencia
- [x] T003 Exponer rutas autenticadas en app/local_api.py y formularios/tablas en app/static/local.*.

## Phase 4: Verificar y entregar
- [x] T004 Probar aislamiento, concurrencia, conflictos, historia e idempotencia en tests/test_local_ops.py; Chrome local, memoria y commit/push.

T001→T002→T003→T004. Requisitos remotos no se marcan como cumplidos por probar simulador.

## Diferido por instrucción del usuario (fuera de esta entrega local)
- [ ] R001 servicio de correo explícitamente configurado, prueba de entrega, fallos/reintentos de transporte y evidencias remotas.

Cobertura y evidencia: [analysis.md](analysis.md). No activar con referencias sintéticas.
