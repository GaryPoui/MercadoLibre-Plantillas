# Implementation Plan: MVP Excel

**Branch**: codex/mvp-excel | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

## Summary
Implementar la especificación activa: cargar XLSX/CSV, elegir hojas/bloques/mapear,
revisar/corregir, perfiles/reglas versionados, historial persistente, comparar catálogo
local por cuenta y exportar exactamente la revisión. Integración real ML es posterior.

## Technical Context
**Language/Version**: Python3.12 y JavaScript nativo.
**Primary Dependencies**: FastAPI, uvicorn, openpyxl, defusedxml, python-multipart.
**Storage**: SQLite + originales fuera de OneDrive en LOCALAPPDATA/MercadoLibrePlantillas;
MLPL_DATA_DIR configurable. Un proceso; transacciones cortas explícitas.
**Testing**: pytest/httpx; recorrido Playwright; casos privados opcionales.
**Target Platform**: Windows/Linux, loopback127.0.0.1:8765, operador autenticado.
**Project Type**: web local modular con frontend mismo origen, sin build.
**Performance Goals**: medir1000filas controladas; no inventar volumen negocio.
**Constraints**: 10MiB archivo/12MiB cuerpo,30hojas,20kfilas/100columnas/500kceldas,
ZIP100MiB/2000entradas, profundidad fórmulas64; sin macros/enlaces/IA.
**Scale/Scope**: un operador y proceso; sin React/Postgres/Redis hasta justificar.

## Constitution Check
I: originales intactos, parámetros por perfil, fixture sintético rotulado.
II: sin movimientos; Full bloqueado en comparación.
III: catálogo controlado, sin éxito remoto ficticio ni escrituras ML.
IV: contraseña inicial local, sesiones opacas8h, CSRF/Host/Origin, BD privada.
V: módulos y pruebas de identidad, ceros, referencias rotas, versiones y aislamiento.
Gate pre/post diseño: PASS. Dos pendientes del checklist de proveedores futuros
ya autorizados como no bloqueantes; no se marcan como pruebas pasadas.

## Project Structure
app/main.py HTTP/auth/composición; app/store.py SQLite; app/engine.py lectura/reglas/export;
app/static/ panel; tests/ contratos y escenarios; scripts/ arranque y QA;
docs/memory/ índice30líneas y notas<=120palabras por hito.

## Complexity Tracking
Sin violaciones. MVP de conversión autónoma, no despliegue público ni OAuth.
Hitos: M0 base; M1 diseño; M2 motor; M3 aplicación/panel; M4 verificación/entrega.
