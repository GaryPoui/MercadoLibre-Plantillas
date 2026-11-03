# Verificación de la ampliación local 004–007

Fecha: 2026-11-03. Rama: codex/mvp-excel. Autorización: avanzar con el resto mientras
el usuario no tiene cuenta de Mercado Libre. No acredita integración externa.

## Evidencia ejecutada

- `python -m pytest -q`: 117 pruebas aprobadas (89 previas, 28 nuevas), cero fallos.
  Un aviso conocido de deprecación de TestClient/httpx; no se cambian dependencias aquí.
- `node --check` para app.js, local.js y ambos recorridos; `git diff --check` sin errores.
- `scripts/browser-smoke.cjs`: regresión completa XLSX/CSV, corrección, perfiles,
  unificación, proveedores, activación/restauración y descarga histórica, Chrome.
- `scripts/local-browser-smoke.cjs`: cinco secciones nuevas, alta de cuenta/producto,
  captura y vínculos, regla/propuesta, timeout posterior y recuperación sin repetir
  cambio, asignación/reserva/despacho, duplicado de venta, Full manual, conciliación,
  alerta/reconocimiento, aviso .eml no enviado, filtros y exportación.
- Ambos recorridos usan servidor y carpeta temporal independientes de los datos de uso.
  Chrome1440px y390px: sin errores JS y sin desborde horizontal de página en las cinco
  secciones. Las tablas anchas conservan desplazamiento propio y foco de teclado.
  Capturas de inventario/alertas revisadas; no es certificación completa de accesibilidad.
- Se mantienen sesión, CSRF y validación Host/Origin. Modelos de entrada rechazan
  campos extra de credenciales y cantidades de tipo incorrecto; /remote/execute bloqueado.

Los tests cubren dos cuentas con igual publicación, SKU exacto, historia de capturas,
retiro de vínculos, revisiones obsoletas, moneda/semántica incompatibles, escenarios
de fallo y reintentos limitados, diez eventos duplicados, asignaciones concurrentes,
cambios de cantidad, cancelación, devolución parcial, eventos fuera de orden y
conflicto de secuencia. Ajustes/asignaciones no invaden stock protegido. Full no
genera movimientos propios. Auditoría conserva estado histórico y admite cursor.
Avisos se deduplican y rechazan inyección de cabeceras; exportación conserva fuentes.

## Consistencia y trazabilidad

Cada spec define cuatro requisitos LFR de entrega local y cuatro tareas T001–T004
(contrato, reglas, API/panel, verificación/entrega). Hay16 requisitos locales con16
tareas, cuatro checklists documentales5/5 y ningún requisito local sin tarea.
Planes/modelos/contratos conservan SQLite/FastAPI existentes sin migración destructiva.
Constitución: unidades/reglas declaradas, originales intactos, físico único,
transacciones/idempotencia, Full separado, autenticación y resultados no remotos explícitos.
No se modificó la constitución. No se detectaron contradicciones críticas en el alcance local.

| Spec | Requisitos originales | Cobertura y condición pendiente |
| --- | --- | --- |
| 004 | FR001–005 | OAuth, credenciales, renovación y lectura paginada remotos pendientes; no se simula autorización |
| 004 | FR006–007 | Identidades compuestas y vínculos explícitos locales con historia; lectura real pendiente |
| 004 | FR008 | Capacidad remota desconocida y opción de simulación separada; descubrimiento real pendiente |
| 004 | FR009 | Deshabilitar referencia conserva historia; revocación externa pendiente |
| 004 | FR010 | Cero acceso/escritura remota; comparación anterior sigue identificada como prueba |
| 005 | FR001–002 | Regla, moneda, semántica y versión explícitas en cálculo local |
| 005 | FR003–004 | Capturas/vínculos/revisiones y confirmación local; autorización/capacidad/estado remoto pendientes |
| 005 | FR005 | Restricciones reales no inferidas; escrituras externas bloqueadas |
| 005 | FR006–007 | Estados/causas/intentos del simulador; cero resultados remotos verificados. Comprobación remota pendiente |
| 005 | FR008 | Tres intentos manuales y comprobación de incertidumbre local; espera/planificación de red pendiente |
| 005 | FR009–010 | Conflicto de captura/regla/vínculo/vigencia y cancelación previa local; sincronización/reversión remotas pendientes |
| 006 | FR001,003–005,007–008 | Físico único, política confirmada/versionada, asignaciones/reservas atómicas, transiciones e idempotencia locales |
| 006 | FR002 | Full observado manualmente y separado; lectura autorizada pendiente |
| 006 | FR006 | Secuencias y duplicados de ventas manuales; validación/consulta de notificaciones remotas pendiente |
| 006 | FR009–010 | Conteos/diferencias sin corrección silenciosa; conciliación periódica y verificación de stock remoto pendientes |
| 007 | FR001–004 | Evidencia local, gravedad, ciclos, reconocimiento, recuperación y mínimos explícitos; fallos de conexión real pendientes |
| 007 | FR005–006 | Aviso .eml deduplicado preparado/no enviado; transporte, fallos de entrega y reintentos de correo pendientes |
| 007 | FR007–008 | Auditoría con filtros y reintentos elegibles del simulador sin saltar conflictos; revalidación externa pendiente |
| 007 | FR009–010 | Exportación con fuentes/fechas, propuestas históricas identificadas y despliegue restringido al equipo |

SC de duplicados/concurrencia/Full y ausencia de vínculos inferidos se prueban
localmente; SC que exigen tokens, consultas remotas o entrega de correo siguen pendientes.
Las capturas manuales y pruebas sintéticas no cumplen esos criterios externos.

## Reproducción del navegador

Iniciar backend con MLPL_DATA_DIR temporal vacío, sin afectar la carpeta habitual.
Configurar MLPL_SMOKE_URL al puerto de prueba, MLPL_SMOKE_PASSWORD con una clave
aleatoria solo de prueba, MLPL_SMOKE_ALLOW_WRITE=1 y MLPL_SMOKE_BROWSER_CHANNEL=chrome.
Ejecutar primero browser-smoke.cjs y luego local-browser-smoke.cjs en ese mismo backend.
El segundo requiere la lista ficticia activada por el primero. Ningún recorrido carga
muestras en la instancia del usuario. Las referencias comerciales privadas siguen ausentes.
