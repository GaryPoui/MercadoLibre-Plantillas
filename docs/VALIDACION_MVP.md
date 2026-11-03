# Verificación del MVP Excel local

Fecha: 2026-11-03 (Argentina). Rama: `codex/mvp-excel`.
Alcance: especificación001, conversión/revisión autónoma; no integración real Mercado Libre.

| Comprobación ejecutada | Resultado |
| --- | --- |
| pytest completo | 66 pruebas aprobadas |
| Motor/fórmulas | 52 pruebas aprobadas, incluidas en las66 |
| API/persistencia/catálogo | 14 pruebas aprobadas, incluidas en las66 |
| Casos privados CAS-01 a CAS-09 | 9 aprobados; capturas reconstruidas en memoria, no originales de proveedores |
| Ensayo de1000filas sintéticas | Aprobado,0.651s en este equipo; XLSX reabierto e identidad verificada |
| Chrome headless, interfaz real | XLSX/CSV, mapeo, cero, regla configurable, corrección, exportación por revisión, historial, perfiles/versiones/retiro y Full bloqueado |
| Paginación |60productos sintéticos,61filas incluyendo cabecera; navegación y filtro sin ocultar incidencias |
| Vista móvil390px | Sin desbordamiento horizontal de la página; tablas desplazables |
| JavaScript | Sin errores de ejecución en el recorrido probado |
| Revisión de formato | git diff --check sin errores |

Se usaron estados privados temporales para el navegador; no se configuró una contraseña
para el usuario ni se publicaron credenciales de prueba. Las capturas visuales muestran
solo información sintética y no se incorporan al repositorio.

## Fallos corregidos durante la verificación

- Descargas de una misma revisión diferían por timestamps del ZIP: normalización de
  metadatos y prueba que confirma bytes reproducibles tras reiniciar.
- Respuesta tardía de carga de catálogo podía sobrescribir un borrador en edición:
  protección por generación de solicitud y versión de edición; recorrido completo repetido.
- Cero explícito, referencias rotas y dependencias vacías conservan estados diferentes;
  la ausencia no se transforma en un precio certificado.

## Límites reales

XLSX/CSV UTF-8; fórmulas de un conjunto limitado, no motor Excel general. Expresiones
externas, funciones no admitidas y referencias rotas quedan pendientes. No se ejecutan
macros ni enlaces, ni se usan servicios IA o datos comerciales predeterminados.

El XLSX contiene valores de la revisión e informe, con formatos equivalentes por tipo;
no promete reconstrucción exacta de todo estilo, gráfico o fórmula activa original.
La clasificación de títulos y perfiles ayuda, pero no demuestra reconocimiento universal
de proveedores todavía no recibidos. El operador elige hojas y correspondencias.

Modo local127.0.0.1, un operador y proceso; no certificado para acceso público/LAN.
Catálogo de comparación introducido manualmente: sus capacidades no son verificaciones
de una cuenta Mercado Libre. No hay movimientos de stock, reservas, ventas o webhooks.

La suite emite un aviso de deprecación de Starlette sobre TestClient/httpx; las pruebas
pasan con las versiones fijadas. No implica un fallo del recorrido. Futuras actualizaciones
de dependencias deben repetir estas comprobaciones.

La verificación visual y el recorrido de teclado implícito de los controles no constituyen
una auditoría completa ni certificación WCAG. No se ejecutó auditoría de seguridad externa.
