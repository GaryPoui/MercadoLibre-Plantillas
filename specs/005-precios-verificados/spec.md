# Feature Specification: Precios y sincronización verificada

**Feature Directory**: `specs/005-precios-verificados`
**Created**: 2026-11-03
**Status**: Especificada; no implementada; plan técnico posterior
**Input**: Continuar los specs faltantes del sistema ampliable de listas y Mercado Libre.

## User Scenarios & Testing

### User Story 1 - Revisar cambios antes de aplicarlos (Priority: P1)

Como operador quiero comparar precios autorizados con valores remotos y confirmar destinos.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** una lista vigente vinculada, **When** previsualizo, **Then** veo cuenta, destino, precio anterior/propuesto y restricciones.
2. **Given** un precio remoto cambió después, **When** confirmo la vista previa, **Then** se bloquea ese destino con conflicto visible.

### User Story 2 - Aplicar y verificar (Priority: P1)

Como operador quiero conocer el resultado de cada cambio y recuperar errores.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** un envío aceptado, **When** consulto el estado, **Then** no figura verificado hasta comprobar el precio final remoto.
2. **Given** un timeout después del envío, **When** reintento, **Then** primero se consulta el estado remoto para evitar repetir un cambio incierto.

### Edge Cases

- Respuesta aceptada sin cambio; cambio concurrente; lote parcial; timeout; límite de uso; cancelación a mitad; cero explícito sujeto a restricciones del destino.

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE derivar precio objetivo de una versión vigente y regla autorizada; mantener moneda, semántica y versión de regla visibles.
- **FR-002**: El sistema DEBE no derivar precio de venta de costos sin una regla comercial explícita; bloquear moneda desconocida o incompatible.
- **FR-003**: El sistema DEBE previsualizar por cuenta/destino, indicar captura usada y no habilitar vínculos ambiguos ni capacidades no verificadas.
- **FR-004**: El sistema DEBE exigir confirmación explícita para el lote, con revisión exacta de alcance; revalidar versión vigente y estado remoto antes de cada escritura.
- **FR-005**: El sistema DEBE bloquear o aislar restricciones de automatización de precios, variaciones y recursos no editables según contrato vigente verificado.
- **FR-006**: El sistema DEBE registrar estados pendiente, enviando, resultado incierto, conflicto, fallido y verificado, con intentos y causas sin secretos.
- **FR-007**: El sistema DEBE no marcar aplicado/verificado por un envío aceptado; consultar resultado remoto y compararlo con el valor solicitado.
- **FR-008**: El sistema DEBE reintentar fallos transitorios con límites y espera; un estado incierto se reconcilia antes de volver a escribir.
- **FR-009**: El sistema DEBE evitar ciclos ante cambios externos: generar conflicto según autoridad definida, sin último cambio ganador universal.
- **FR-010**: El sistema DEBE permitir cancelar cambios todavía no enviados; una reversión es una propuesta nueva que también requiere verificación.

### Key Entities

- Objetivo de precio; vista previa versionada; lote confirmado; operación por destino; intento; conflicto; verificación.

## Success Criteria

- **SC-001**: Ningún destino ambiguo, restringido o con conflicto se escribe en los escenarios de aceptación.
- **SC-002**: Una respuesta aceptada sin evidencia remota produce cero operaciones marcadas como verificadas.
- **SC-003**: Reintentos tras timeout no duplican la aplicación sin reconciliar el resultado previo.

## Assumptions and Dependencies

- Requiere003/004. No implementada; escrituras dependen de capacidades reales y reglas comerciales definidas por el operador.
- Sin precio de venta predeterminado, tarifas supuestas ni credenciales de producción en pruebas.

## Condiciones previas a implementación

Verificar documentación oficial vigente y capacidades por cuenta antes del plan de escrituras.
La consulta2026-11-03 a documentación oficial de autorización/precios/stock devolvió403;
no se certifican contratos ni permisos a partir de snippets. Falta evidencia de cuentas reales.
Referencia de investigación: [contratos externos](../../docs/INTEGRACION_PENDIENTE.md).
