# Feature Specification: Proveedores y listas vigentes

**Feature Directory**: `specs/003-proveedores-listas-vigentes`
**Created**: 2026-11-03
**Status**: Implementada y verificada2026-11-03; sin integración externa
**Input**: Continuar los specs faltantes del sistema ampliable de listas y Mercado Libre.

## Clarifications — 2026-11-03

Continuación autorizada por el usuario. Proveedor/alcance se eligen explícitamente al
preparar una versión; no se migran automáticamente nombres de cargas anteriores.
Los alias son confirmados por el operador. Retiro impide nuevas activaciones sin
borrar versiones. Una lista completa conserva ausentes pendientes de revisión;
una parcial conserva ausentes marcados como no actualizados. Ninguna elimina por
ausencia. Una fila nueva inválida no reemplaza el último precio válido; duplicados
conservan alternativas pendientes y la vista previa conserva el precio anterior.
La primera activación necesita al menos un producto certificado. Moneda y significado
de precio se declaran por alcance; su ausencia permite revisar pero bloquea activar.
Tras activar, no se cambia esa semántica: otro significado requiere otro alcance.
Restaurar requiere una vista previa nueva contra la versión vigente y confirmación.
El consolidado de revisiones existente continúa disponible; la vista de vigentes es
independiente y muestra únicamente versiones activadas, sin unir proveedores/alcances.
Inicio usa los productos y pendientes de versiones vigentes cuando existen; antes
de la primera activación conserva el resumen de revisiones cargadas.

## User Scenarios & Testing

### User Story 1 - Identificar proveedores (Priority: P1)

Como operador quiero crear un proveedor estable y asociar sus archivos sin depender del nombre del archivo.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** dos proveedores con un código igual, **When** asocio sus listas, **Then** cada código conserva su proveedor y no se fusiona.
2. **Given** un proveedor existente, **When** cambio su nombre visible, **Then** sus listas y vínculos conservan la misma identidad.

### User Story 2 - Reemplazar una lista vigente (Priority: P1)

Como operador quiero comparar una nueva lista con la vigente y aceptar su activación.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** una lista vigente y otra revisada, **When** previsualizo la actualización, **Then** veo altas, cambios de precio, ausencias y pendientes antes de activar.
2. **Given** una nueva lista con errores, **When** la reviso, **Then** la vigente sigue activa hasta una confirmación válida.
3. **Given** un producto ausente, **When** activo otra lista, **Then** no se interpreta ausencia como precio cero ni stock agotado.

### User Story 3 - Recuperar antecedentes (Priority: P2)

Como operador quiero consultar o restaurar una versión anterior sin borrar historial.

**Why this priority**: Evita pérdida de trazabilidad y permite una entrega comprobable.
**Independent Test**: Recorrer los casos siguientes con datos controlados y verificar estados e historial.
**Acceptance Scenarios**:

1. **Given** versiones guardadas, **When** restauro una, **Then** se registra un cambio nuevo con autor/fecha y resultados anteriores intactos.

### Edge Cases

- Carga repetida por huella; dos archivos del mismo alcance; duplicados con presentación distinta; cambio de proveedor; actualización parcial; listas con varias hojas; dos activaciones simultáneas.

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE asignar identificador estable de proveedor independiente de su nombre, con alias confirmados y retiro sin borrado de antecedentes.
- **FR-002**: El sistema DEBE asociar cada carga a proveedor y alcance de lista explícitos; un libro puede aportar varias hojas revisadas al mismo conjunto.
- **FR-003**: El sistema DEBE mantener una versión vigente por proveedor/alcance; las cargas históricas no generan conflictos permanentes con la versión nueva.
- **FR-004**: El sistema DEBE mostrar diferencias por SKU dentro del mismo proveedor/alcance y distinguir alta, cambio, sin cambio, ausente y ambiguo.
- **FR-005**: El sistema DEBE activar únicamente tras vista previa y confirmación explícita; rechazar activación si cambió la versión vigente desde la comparación.
- **FR-006**: El sistema DEBE conservar alternativas duplicadas pendientes, sin elegir menor precio ni unir proveedores por código coincidente.
- **FR-007**: El sistema DEBE no sustituir un precio vigente válido por uno pendiente; en actualización parcial conservar el anterior y marcarlo como no actualizado, con origen visible.
- **FR-008**: El sistema DEBE no retirar productos ausentes automáticamente; distinguir listas completas de parciales con elección explícita antes de activar.
- **FR-009**: El sistema DEBE conservar originales/revisiones, auditar activación/restauración y exportar exactamente una versión seleccionada.
- **FR-010**: El sistema DEBE comparar importes solo con moneda y significado compatibles confirmados; si faltan, mostrar diferencia sin habilitar uso automático.

### Key Entities

- Proveedor estable; alias; alcance de lista; conjunto de revisiones; versión vigente; diferencia; activación auditada.

## Success Criteria

- **SC-001**: Dos versiones del mismo proveedor muestran el precio vigente una sola vez y permiten consultar ambos antecedentes.
- **SC-002**: Dos proveedores con SKU coincidente siguen siendo dos identidades; precio cero y ausencia se distinguen.
- **SC-003**: Activaciones concurrentes rechazan la segunda vista previa obsoleta sin pérdida de versiones.

## Assumptions and Dependencies

- Requiere001 y usa002. Se adopta activación explícita conservadora; no automatiza reglas comerciales.
- No se aprueba deduplicación de productos entre proveedores ni se determina moneda/impuestos por posición.
