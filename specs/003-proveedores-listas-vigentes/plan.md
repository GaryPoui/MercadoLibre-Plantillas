# Implementation Plan: Proveedores y listas vigentes

**Branch**: codex/mvp-excel | **Date**: 2026-11-03

## Summary
Identidades estables, alcances y versiones vigentes sobre SQLite existente. Preparar
snapshot inmutable y diferencias, activar con control de concurrencia, restaurar por
otra vista previa. Conservación segura de precios previos y origen.

## Technical Context
Python3.12/FastAPI, SQLite records JSON existente, frontend nativo. Sin dependencias
ni llamadas externas. app/suppliers.py contiene servicio/reglas; usa Store.connect y
transacciones BEGIN IMMEDIATE. Tipos nuevos supplier, supplier_scope, supplier_preview,
supplier_version, supplier_binding sin cambiar tablas anteriores. Hashes/sesiones intactos.
Lectura de versiones vigentes dentro de una transacción de lectura. Previews/versiones
no mutables; comparación usa Decimal. Exportador seguro existente con columnas extendidas.

## Constitution Check
I: moneda/significado explícitos, originales intactos, sin fórmulas nuevas. II/III:
sin movimientos/escrituras externas; activación local no es éxito remoto. IV: auth/CSRF
existentes, secretos fuera de registros. V: pruebas de concurrencia, historia y aislamiento.
PASS antes/después del diseño. Sin excepciones.

## Project Structure
app/suppliers.py servicio y versiones; app/main.py contratos; app/standardize.py export
campos adicionales; app/static/ gestión y selector de vigentes; tests/test_suppliers.py
contratos, precios, restauración, concurrencia; scripts/browser-smoke.cjs regresión/UI.

## Complexity Tracking
No tablas nuevas ni migración destructiva. Creación de proveedor/alcance no activa datos.
T001→T002→T003→T004→T005→T006. Mantener pruebas001/002.

## Validación posterior
89pruebas y Chrome ampliado aprobados; capturas revisadas. Constitución PASS.
No hay datos sintéticos en la BD de uso, migraciones destructivas ni escriturasML.
