# Feature Specification: Inventario compartido, Full y ventas

**Feature Directory**: `specs/006-inventario-ventas`
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

- **LFR-001**: Mantener una existencia propia por producto/ubicación, con conteo y margen explícitos; asignaciones y reservas comparten el mismo físico y no pueden superarlo.
- **LFR-002**: Confirmar/versionar política de reserva al registrar y descuento al despachar. Cancelar libera reservas; devoluciones recibidas confirmadas reponen solo su incremento acumulado.
- **LFR-003**: Registrar ventas manuales por cuenta/referencia con eventos idempotentes y secuencias; movimientos atómicos, duplicados/fuera de orden sin doble descuento y transiciones incompatibles bloqueadas.
- **LFR-004**: Full solo conserva observaciones manuales con origen/fecha y cuenta; nunca admite ajustes/asignaciones propias ni descuenta dos veces. Conteos de conciliación guardan diferencias sin ajustes automáticos.

## User Scenarios & Testing

### User Story 1 - Conocer existencias separadas (Priority: P1)

Como operador quiero ver inventario físico propio y Full con origen y antigüedad.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** una existencia compartida entre cuentas, **When** consulto disponibilidad, **Then** aparece una sola existencia física con asignaciones separadas.
2. **Given** stock Full, **When** consulto o ajusto, **Then** Full se muestra como solo lectura y no se modifica por un ajuste propio.

### User Story 2 - Procesar ventas sin duplicación (Priority: P1)

Como operador quiero registrar ventas y cancelaciones una sola vez y conciliar desvíos.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** el mismo evento repetido, **When** se procesa varias veces, **Then** solo se genera un efecto de inventario.
2. **Given** eventos fuera de orden, **When** se procesa el estado actual, **Then** no se revierte un estado más nuevo por uno viejo.

### Edge Cases

- Reserva concurrente; depósito compartido; stock físico menor que reservas; venta Full; devolución parcial; evento viejo; caída antes/después de confirmar movimiento.

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE representar cada existencia propia una sola vez por producto/ubicación, con historial de movimientos.
- **FR-002**: El sistema DEBE mantener Full separado, como fuente externa de solo lectura; no descontar además una venta Full del inventario propio.
- **FR-003**: El sistema DEBE definir y versionar la política de reserva/descuento y su reversión para cada estado de venta antes de activar procesamiento.
- **FR-004**: El sistema DEBE las asignaciones publicables entre cuentas y reservas no deben superar disponibilidad física menos margen confirmado.
- **FR-005**: El sistema DEBE aplicar movimientos y reservas de manera atómica, con claves de idempotencia que incluyen cuenta y recurso relevante.
- **FR-006**: El sistema DEBE no confiar en contenido de notificación como movimiento definitivo; validar origen/recurso, consultar estado autorizado y tolerar duplicados/fuera de orden.
- **FR-007**: El sistema DEBE procesar cancelación, devolución parcial y modificación de venta mediante transiciones auditadas, sin reposición doble.
- **FR-008**: El sistema DEBE confirmar unidades, presentaciones, depósitos y claves antes de calcular cantidades; listas de precios no equivalen a inventario.
- **FR-009**: El sistema DEBE conciliar periódicamente con capturas remotas y mostrar discrepancias; no corregir existencias silenciosamente.
- **FR-010**: El sistema DEBE verificar cualquier escritura permitida de stock propio contra resultado remoto; recursos/cuentas sin capacidad verificada permanecen bloqueados.

### Key Entities

- Ubicación; existencia propia; captura Full; reserva; asignación; venta; transición; movimiento; evento; conciliación.

## Success Criteria

- **SC-001**: Repetir un evento diez veces produce un solo movimiento comercial por transición.
- **SC-002**: Concurrencia entre dos cuentas nunca supera disponibilidad asignable en los casos de prueba.
- **SC-003**: Venta Full, cancelación y devolución parcial conservan cantidades trazables sin doble efecto.

## Assumptions and Dependencies

- Requiere004; usar infraestructura de operaciones de005. Eventos y conciliación remotos no implementados.
- La política exacta de estados de venta, unidades, margen y depósitos es una condición previa a activación, no un valor inventado.

## Condiciones previas a implementación

Verificar documentación oficial vigente y capacidades por cuenta antes del plan de escrituras.
La consulta2026-11-03 a documentación oficial de autorización/precios/stock devolvió403;
no se certifican contratos ni permisos a partir de snippets. Falta evidencia de cuentas reales.
Referencia de investigación: [contratos externos](../../docs/INTEGRACION_PENDIENTE.md).
