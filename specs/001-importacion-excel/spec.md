# Feature Specification: Importación de Excel y revisión de diferencias

**Feature Directory**: `specs/001-importacion-excel`

**Created**: 2026-10-14

**Status**: Draft — pendiente de contrastar con los Excel reales

**Input**: Preparar el proyecto con Spec Kit para un integrador de listas Excel, varias cuentas de Mercado Libre, inventario propio y Full y sincronización bidireccional. Los Excel de referencia se recibirán después.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entender y validar una lista de productos (Priority: P1)

Como operador quiero cargar una lista, elegir sus hojas y relacionar sus columnas con los datos del sistema para conocer qué filas se pueden utilizar y cuáles necesitan corrección.

**Why this priority**: Los datos reales determinan las reglas de importación y evitan aplicar precios o cantidades mal interpretados.

**Independent Test**: Cargar un archivo de referencia sin cuentas conectadas y revisar sus registros válidos, duplicados y rechazados, sin modificar el original.

**Acceptance Scenarios**:

1. **Given** un archivo con varias hojas, **When** el operador selecciona una hoja y asigna sus columnas, **Then** ve los registros interpretados y la selección utilizada.
2. **Given** filas válidas y filas con campos inválidos, **When** se valida la lista, **Then** cada fila recibe un estado y los errores indican hoja, fila, campo y motivo.
3. **Given** códigos repetidos o con ceros iniciales, **When** se interpreta el archivo, **Then** los códigos mantienen su identidad y los duplicados quedan señalados sin fusionarse automáticamente.

### User Story 2 - Revisar cambios por producto y cuenta (Priority: P2)

Como operador quiero comparar la lista validada con el catálogo conocido para revisar qué precios o existencias cambiarían, en qué cuenta y con qué restricciones.

**Why this priority**: Una lista puede afectar varios vendedores o publicaciones y debe mostrar el alcance antes de escribir.

**Independent Test**: Usar un catálogo controlado de dos cuentas y comprobar la vista previa de diferencias sin realizar cambios en Mercado Libre.

**Acceptance Scenarios**:

1. **Given** un producto vinculado a dos cuentas, **When** se selecciona una cuenta como destino, **Then** la vista previa incluye únicamente sus vínculos y muestra los valores anteriores y propuestos.
2. **Given** una fila sin vínculo o con varias coincidencias posibles, **When** se comparan los datos, **Then** la fila queda pendiente de resolución y no genera una actualización automática.
3. **Given** una cantidad de Full o un precio que la cuenta no permite editar, **When** se construye la vista previa, **Then** se muestra la restricción y no se propone una escritura no permitida.
4. **Given** una cantidad vacía, **When** se importa la fila, **Then** el sistema la diferencia de un cero explícito y no propone agotar el producto por ausencia de dato.

### User Story 3 - Conservar el resultado de la revisión (Priority: P3)

Como operador quiero recuperar el resultado de una importación y descargar su informe para corregir errores y continuar después sin repetir la interpretación del archivo.

**Why this priority**: La revisión debe ser trazable y reutilizable cuando se agregue la sincronización.

**Independent Test**: Consultar una importación completada y descargar un informe con estados por fila y diferencias por destino.

**Acceptance Scenarios**:

1. **Given** una importación revisada, **When** se consulta su detalle, **Then** aparecen su archivo de origen, mapeo, fecha, estado y resumen de filas.
2. **Given** una revisión con errores y diferencias, **When** se descarga el informe, **Then** conserva los códigos y detalla las filas afectadas y sus motivos.
3. **Given** dos cargas del mismo archivo, **When** se revisa el historial, **Then** el sistema identifica la repetición y esta funcionalidad no aplica cambios remotos ni duplica movimientos de inventario.

### Edge Cases

- Archivo corrupto, protegido o de un formato no admitido: rechazo legible sin importación parcial silenciosa.
- Hojas vacías, encabezados repetidos, columnas sin título, filas ocultas y celdas combinadas: indicar qué se puede interpretar y qué requiere selección/corrección.
- Coma o punto decimal, separadores de miles, porcentajes y monedas mezcladas: no convertir valores ambiguos sin una regla explícita.
- Fórmulas sin resultados guardados: señalarlas, sin inventar ni recalcular silenciosamente sus valores.
- Costos, precios finales, impuestos y descuentos: no confundirlos; aplicar solo reglas documentadas después del análisis real.
- Valores negativos, cantidades fraccionarias o unidades desconocidas: validar según el contrato pendiente, sin truncar ni aceptar por defecto.
- SKU interno diferente del código de proveedor o del identificador de publicación: mantener sus roles separados.
- Una publicación con variaciones o el mismo SKU en varios vendedores: resolver por destino y vínculo explícito.
- Cambio remoto posterior a la captura usada en la comparación: advertir que la vista previa puede quedar desactualizada; revalidar antes de aplicar en la futura funcionalidad de sincronización.
- Archivos grandes: definir y comunicar el límite con evidencia de los Excel reales; no fijar aquí un volumen comercial ficticio.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir elegir archivo, hoja y correspondencia de columnas, mostrando la interpretación antes de aceptarla.
- **FR-002**: DEBE conservar los códigos de producto como identificadores, incluidos ceros iniciales, y mantener el archivo original sin modificaciones.
- **FR-003**: DEBE diferenciar valores ausentes, ceros explícitos y valores inválidos.
- **FR-004**: DEBE validar cada fila y reportar origen, campo, valor interpretado y motivo de rechazo sin mostrar datos privados innecesarios.
- **FR-005**: DEBE señalar duplicados y vínculos ambiguos sin resolverlos por coincidencia de descripción solamente.
- **FR-006**: DEBE permitir seleccionar destinos por cuenta y publicación; una comparación no puede incluir cuentas ajenas a la selección.
- **FR-007**: DEBE mostrar valores actuales y propuestos, identidad del producto, destino, estado del vínculo y restricciones por diferencia.
- **FR-008**: DEBE separar stock propio y Full y marcar Full como no editable.
- **FR-009**: DEBE bloquear propuestas con errores de validación, vínculo ambiguo o capacidades de escritura no verificadas.
- **FR-010**: DEBE guardar el resultado de revisión con origen, mapeo, momento, estados y resumen de cantidades de filas.
- **FR-011**: DEBE permitir descargar el informe de revisión con errores y diferencias, conservando identificadores.
- **FR-012**: DEBE identificar cargas repetidas y mantener una revisión por carga; esta funcionalidad NO aplica cambios remotos ni movimientos de inventario.
- **FR-013**: DEBE documentar, antes de implementar el importador, los formatos admitidos, campos obligatorios, unidades, monedas, reglas numéricas, manejo de fórmulas y límites, basados en los archivos del usuario.

### Key Entities *(include if feature involves data)*

- **Importación**: archivo recibido, huella para detectar repetición, selección de hojas, momento, estado y resumen de revisión.
- **Perfil de mapeo**: significado de columnas, formato de origen y reglas de interpretación explícitas.
- **Fila interpretada**: origen, identificadores, valores originales e interpretados, estado y motivos.
- **Producto interno**: identidad comercial consolidada; no presupone que el código de proveedor sea el SKU interno.
- **Cuenta y vínculo de publicación**: destino comercial y relación explícita con producto/variación.
- **Diferencia propuesta**: dato, valor conocido, valor propuesto, destino y elegibilidad; no representa una operación aplicada.
- **Informe**: representación descargable del resultado de revisión.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cada fila de los archivos de aceptación queda contabilizada como utilizable, pendiente o rechazada; ninguna desaparece sin explicación.
- **SC-002**: En los casos de códigos con ceros iniciales, duplicados y campos vacíos, el 100% conserva su identidad o recibe una advertencia explícita; ningún vacío se convierte en cero automáticamente.
- **SC-003**: En una comparación con dos cuentas, el 100% de las diferencias pertenece a los destinos elegidos; no aparecen escrituras para Full ni vínculos ambiguos habilitados.
- **SC-004**: El operador puede descargar un informe que concuerda con los estados y totales de la revisión en todos los archivos de aceptación.
- **SC-005**: Cargar, comparar y descargar, incluso repitiendo un archivo, produce cero cambios remotos y cero movimientos de inventario.

## Assumptions

- Esta es la primera funcionalidad del MVP, centrada en lectura y revisión. La aplicación de cambios tendrá su propia especificación.
- Se toma xlsx como candidato inicial; xls/CSV se incorporarán si los archivos reales lo requieren. Ningún formato está validado todavía.
- Se pueden usar ejemplos identificados como ficticios para diseñar escenarios, pero los archivos reales definirán los casos de aceptación finales.
- La comparación requiere un catálogo previamente disponible; puede validarse con datos controlados. La conexión de cuentas se especificará por separado.
- Los Excel aún no fueron entregados. El contrato definitivo de columnas, monedas, fórmulas, unidades y límites está pendiente del análisis descrito en docs/ANALISIS_EXCEL.md.
- La asignación inicial de columnas es manual y explícita; detectar encabezados puede ayudar, pero no sustituye la confirmación del significado.
- No se ejecutan macros ni vínculos externos contenidos en archivos.
- Fuera de esta funcionalidad: escritura en Mercado Libre, procesamiento de ventas, alertas comerciales y modificación automática del Excel local.
