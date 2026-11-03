# Feature Specification: Alertas y operación

**Feature Directory**: `specs/007-alertas-operacion`
**Created**: 2026-11-03
**Status**: Parte local implementada y verificada; integración externa diferida por el usuario
**Input**: Continuar los specs faltantes del sistema ampliable de listas y Mercado Libre.

## Clarifications — continuación sin cuenta Mercado Libre

El usuario indica que todavía no tiene cuenta y solicita avanzar con todo el resto.
Esta entrega implementa la parte local utilizable y las pruebas controladas, sin OAuth,
credenciales, consultas ni escrituras remotas. Toda cuenta/publicación capturada es una
referencia local; simular nunca equivale a publicar ni verificar Mercado Libre.
Las cláusulas que requieren cuenta/contrato externo permanecen diferidas, no cumplidas.
No se envía correo: se prepara un aviso descargable con destinatario explícito.
Reglas de precios, moneda, unidades, depósitos, márgenes y mínimos se ingresan explícitamente.
Política local versionada y confirmada: reservar al registrar, descontar al despachar,
cancelar solo reservas y reponer únicamente devoluciones recibidas confirmadas.
Los eventos de prueba/locales no se presentan como ventas consultadas a Mercado Libre.
Full solo admite capturas observadas identificadas como manuales; ajustes/ventas locales
no modifican su cantidad. Las asignaciones comparten una única existencia física.

## Requisitos de esta entrega local

- **LFR-001**: Consolidar evidencia local de listas pendientes, mínimos explícitos, Full desconocido, diferencias y fallos del simulador con origen, gravedad, fechas y ciclo.
- **LFR-002**: Reconocer sin resolver la causa; cerrar por recuperación observada y reabrir al reaparecer. Consultar repetidamente no duplica alertas.
- **LFR-003**: Preparar avisos descargables .eml con destinatario explícito y deduplicación por alerta/ciclo/destinatario; nunca enviar ni declarar entrega.
- **LFR-004**: Auditar por cuenta/recurso/acción/estado/fechas con paginación; exportar el estado local y propuestas históricas con origen y fecha, sin releer Excel ni declarar sincronización.

## User Scenarios & Testing

### User Story 1 - Atender problemas desde el panel (Priority: P1)

Como operador quiero ver alertas accionables con su cuenta y recurso.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** un faltante o error repetido, **When** consulto alertas, **Then** veo un problema consolidado con su estado y origen.
2. **Given** un problema resuelto, **When** se reconcilia, **Then** su alerta se cierra conservando el historial.

### User Story 2 - Recibir avisos y recuperar tareas (Priority: P2)

Como operador quiero elegir avisos y reintentar sin ejecutar acciones duplicadas.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** correo configurado y destinatario confirmado, **When** ocurre una alerta nueva, **Then** se registra su intento de entrega sin exponer credenciales.
2. **Given** una operación fallida, **When** solicito reintento, **Then** se respetan sus controles de idempotencia, conflicto y verificación.

### Edge Cases

- Destinatario retirado; servicio caído; tormenta de errores; alerta reabierta; datos antiguos; permiso insuficiente para reintentar.

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar alertas de datos pendientes, fallos de conexión/sincronización, conflictos y mínimos definidos, con cuenta/proveedor/recurso cuando corresponda.
- **FR-002**: El sistema DEBE conservar origen, primera/última ocurrencia, severidad y estado abierta/reconocida/resuelta; consolidar repeticiones del mismo problema.
- **FR-003**: El sistema DEBE no confundir reconocer una alerta con resolver su causa; cerrar por evidencia de recuperación o decisión auditada.
- **FR-004**: El sistema DEBE configurar mínimos por producto/ubicación sin valores comerciales predeterminados; Full y propio permanecen separados.
- **FR-005**: El sistema DEBE enviar correo solo a destinatarios y mediante servicio configurados explícitamente; habilitación y prueba controlada previas.
- **FR-006**: El sistema DEBE deduplicar entregas, registrar fallos y reintentos limitados; un correo fallido no impide mostrar la alerta en el panel.
- **FR-007**: El sistema DEBE mostrar auditoría de cambios, versiones, operaciones e intentos con filtros por cuenta, recurso, fecha y estado, sin secretos.
- **FR-008**: El sistema DEBE permitir reintentos solo para operaciones elegibles y revalidar autoridad/capacidades; nunca saltar conflictos desde una alerta.
- **FR-009**: El sistema DEBE exportar estados actuales con captura/fecha y distinguir pendientes, verificados y desactualizados sin releer listas silenciosamente.
- **FR-010**: El sistema DEBE mantener modo local hasta especificar autenticación, roles, alojamiento, secretos y respaldos de un despliegue distinto.

### Key Entities

- Alerta; ocurrencia; reconocimiento; suscripción; entrega de correo; entrada de auditoría; solicitud de recuperación.

## Success Criteria

- **SC-001**: Eventos repetidos del mismo problema mantienen una alerta y no duplican avisos entregados.
- **SC-002**: Fallo de correo conserva la alerta y permite inspeccionar entrega sin mostrar secretos.
- **SC-003**: Exportación distingue operación verificada de resultado incierto o pendiente.

## Assumptions and Dependencies

- Depende de004/005/006 para alertas de integración; puede mostrar pendientes de listas antes.
- Transporte de correo no implementado. Faltan servicio, prueba de entrega y política de retención; destinatarios y mínimos locales se ingresan explícitamente.

## Condiciones previas a implementación

Verificar documentación oficial vigente y capacidades por cuenta antes del plan de escrituras.
La consulta2026-11-03 a documentación oficial de autorización/precios/stock devolvió403;
no se certifican contratos ni permisos a partir de snippets. Falta evidencia de cuentas reales.
Referencia de investigación: [contratos externos](../../docs/INTEGRACION_PENDIENTE.md).
