# Plan: Propuestas y simulación de precios

**Branch**: codex/mvp-excel | **Date**: 2026-11-03

## Summary
Implementar reglas explícitas, snapshots, conflictos, ejecución simulada e idempotencia/reconciliación de reintentos. Sin red externa; SQLite/FastAPI y UI existentes.

## Technical Context
Python3.12; records JSON y transacciones BEGIN IMMEDIATE existentes. app/local_core.py
comparte validación/idempotencia/auditoría; app/local_pricing.py separa reglas.
app/local_api.py instala router autenticado/CSRF bajo /api/ops; app/static/local.js y
local.html presentan formularios ordinarios y tablas. Pruebas en tests/test_local_ops.py.
Sin migración destructiva ni dependencias nuevas. Decimal para precios y enteros en la
unidad indivisible declarada para stock. Secretos no aceptados por los modelos.

## Constitution Check
Originales/revisiones intactos; sin fórmulas comerciales por defecto. Operaciones de
inventario atómicas, Full separado e idempotencia por cuenta/recurso/evento. Estados de
simulación explícitos; ninguna operación marcada como remota. Auth/CSRF existentes.
PASS para alcance local. Condiciones remotas continúan fuera de alcance por instrucción.

## Project Structure
Módulo local_pricing, base local_core, local_api, frontend local y pruebas de riesgos.

## Dependencies
003 →004 local →005 local →006 local →007 local. Las pruebas de cada fase preceden
al cierre. Conexión real se retomará con cuenta y verificación de documentación.
