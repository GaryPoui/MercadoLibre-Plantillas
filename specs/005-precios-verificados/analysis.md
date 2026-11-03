# Revisión final de consistencia: Precios simulados

2026-11-03. Alcance local autorizado, separado de los FR/SC remotos originales.
Prerrequisitos spec/plan/modelo/contratos/tareas presentes. Checklist documental5/5.

| Requisito local | Tareas | Evidencia |
| --- | --- | --- |
| LFR001 | T001–T004 | Modelo/reglas, API/panel, tests y recorrido Chrome |
| LFR002 | T001–T004 | reglas/moneda/semántica, revisiones, conflictos, timeout, reconciliación y límites de intentos |
| LFR003 | T001–T004 | Casos de fallo, aislamiento e historia en test_local_ops.py |
| LFR004 | T001–T004 | Autenticación/CSRF, exportación/operación local y comprobación en Chrome |

Sin requisitos locales sin tarea ni contradicciones críticas con la constitución.
Los cuatro requisitos locales no sustituyen los diez FR y tres SC originales.
Pendiente por instrucción del usuario: contratos/capacidades reales, lectura previa, aplicación/verificación de precios, espera y recuperación de red.

Ver [cobertura requisito por requisito y verificación](../../docs/VALIDACION_OPERACION_LOCAL.md).
117 tests totales, ambos recorridos Chrome aprobados, privados ausentes. No se
certifican autorizaciones, consultas, escrituras ni entregas externas mediante simulación.
