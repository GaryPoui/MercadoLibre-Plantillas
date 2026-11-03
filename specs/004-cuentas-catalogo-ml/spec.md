# Feature Specification: Cuentas y catálogo de Mercado Libre

**Feature Directory**: `specs/004-cuentas-catalogo-ml`
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

- **LFR-001**: Registrar referencias habilitables de cuenta sin credenciales ni afirmar conexión.
- **LFR-002**: Mantener productos internos con SKU y unidad declarados; capturas manuales por cuenta/publicación/variante con historial y capacidad remota desconocida.
- **LFR-003**: Confirmar explícitamente producto↔publicación y producto↔SKU de un alcance vigente. No inferir equivalencia; retirar vínculos conserva historia y bloquea propuestas dependientes.
- **LFR-004**: Autenticar el acceso, proteger mutaciones y detectar revisiones concurrentes. La comparación controlada anterior sigue identificada como prueba.

## User Scenarios & Testing

### User Story 1 - Conectar cuentas separadas (Priority: P1)

Como operador quiero autorizar cada vendedor y ver su estado sin compartir credenciales.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** dos vendedores autorizados, **When** consulto uno, **Then** solo aparecen sus recursos.
2. **Given** autorización cancelada o vencida, **When** intento leer, **Then** veo un estado recuperable sin revelar credenciales.

### User Story 2 - Relacionar publicaciones (Priority: P1)

Como operador quiero vincular un producto interno con los destinos exactos de una cuenta.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** un SKU ambiguo con variaciones, **When** reviso coincidencias, **Then** solo un vínculo confirmado habilita comparaciones futuras.
2. **Given** una actualización interrumpida del catálogo, **When** reintento, **Then** se conserva la última captura completa con su antigüedad.

### Edge Cases

- Paginación incompleta; restricciones regionales; múltiples variaciones; permisos retirados; dos renovaciones simultáneas; catálogo desactualizado.

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE autorizar por vendedor mediante el flujo oficial vigente y comprobar que la identidad recibida corresponde a la cuenta esperada.
- **FR-002**: El sistema DEBE proteger credenciales en servidor, separadas por cuenta, fuera del repositorio, exportaciones y registros visibles.
- **FR-003**: El sistema DEBE validar la continuidad y origen de la autorización y rechazar retornos repetidos, vencidos o de otra sesión.
- **FR-004**: El sistema DEBE renovar credenciales sin carreras entre solicitudes; si la autorización es revocada, detener consultas y pedir reconexión.
- **FR-005**: El sistema DEBE leer catálogo paginado y registrar fecha, completitud y errores; no presentar una captura parcial como catálogo completo.
- **FR-006**: El sistema DEBE conservar cuenta, publicación, producto de usuario y variación cuando existan; ausencia no autoriza inventar identificadores.
- **FR-007**: El sistema DEBE separar SKU de proveedor, producto interno y SKU/publicación remotos; resolver coincidencias ambiguas explícitamente.
- **FR-008**: El sistema DEBE mostrar capacidades por cuenta/recurso como conocidas, desconocidas o restringidas, basadas en evidencia verificable.
- **FR-009**: El sistema DEBE desconectar una cuenta detiene nuevas consultas y revoca acceso local a sus credenciales sin borrar auditoría.
- **FR-010**: El sistema DEBE operar esta entrega solo en lectura remota; el catálogo controlado existente continúa identificado como prueba.

### Key Entities

- Cuenta autorizada; estado de conexión; captura de catálogo; producto interno; vínculo confirmado; evidencia de capacidades.

## Success Criteria

- **SC-001**: En pruebas de dos cuentas, ninguna consulta ni vínculo usa la credencial de otra.
- **SC-002**: Token vencido, cancelación y retorno repetido se recuperan o rechazan sin secretos visibles.
- **SC-003**: Todos los destinos ambiguos permanecen sin vínculo automático.

## Assumptions and Dependencies

- Requiere003 para identidades de proveedor estables. Integración remota no implementada: falta app registrada, cuentas autorizadas y configuración de retorno admitida.
- Antes del plan técnico de integración verificar documentación oficial vigente y capacidades reales; no inferirlas de catálogos sintéticos.

## Condiciones previas a implementación

Verificar documentación oficial vigente y capacidades por cuenta antes del plan de escrituras.
La consulta2026-11-03 a documentación oficial de autorización/precios/stock devolvió403;
no se certifican contratos ni permisos a partir de snippets. Falta evidencia de cuentas reales.
Referencia de investigación: [contratos externos](../../docs/INTEGRACION_PENDIENTE.md).
