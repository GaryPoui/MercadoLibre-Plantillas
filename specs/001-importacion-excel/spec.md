# Feature Specification: Importación de Excel y revisión de diferencias

**Feature Directory**: `specs/001-importacion-excel`

**Created**: 2026-10-14

**Status**: MVP local implementado y verificado2026-11-03; nuevos proveedores e integración realML pendientes de sus respectivas validaciones

**Input**: Preparar un integrador de listas Excel, varias cuentas de Mercado Libre, inventario propio y Full y sincronización bidireccional. Ampliación del 2026-11-02: convertir listas de proveedores a formatos similares a las referencias aportadas y reutilizar correcciones confirmadas. Esta etapa solo autoriza análisis, documentación y habilidades; no implementación.

## Clarifications

Autorización posterior: el usuario solicita ejecutar Spec Kit hasta MVP, implementar,
verificar y subir commits con memoria por hito. Sustituye las restricciones históricas
de no escribir aplicación. MVP de esta especificación: conversión/revisión local,
comparación con catálogo controlado y exportación de valores certificados con informe.
La revisión conserva fórmula y resultado histórico; no se promete reproducción exacta
de estilos ni fórmulas activas en la descarga. Integración real ML es entrega posterior.

### Session 2026-11-02

- Decisión explícita: usar las planillas ya entregadas; los originales de proveedores llegarán después y ampliarán los perfiles, sin bloquear el plan inicial.
- Delegación: preparar las filas de entrada/salida y resolver decisiones iniciales sin nuevas preguntas; se eligió un perfil simple y nueve casos de referencia con procedencia privada.
- Decisión explícita: partir de las reglas observadas en las planillas y permitir modificarlas posteriormente; no adoptar errores como reglas válidas ni atribuir vigencia fiscal a factores históricos.
- Decisión delegada: correcciones de fila locales por defecto; reutilizar perfiles compatibles y versionar cambios explícitos de reglas/plantillas, sin alterar historial ni extenderlos a otros proveedores.

Estas decisiones derivan de las cuatro indicaciones del usuario, no de respuestas a
preguntas inventadas. Se hicieron cero preguntas adicionales. Contrato inicial y
alcance en [BASE_INICIAL_V0.md](../../docs/BASE_INICIAL_V0.md).

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

### User Story 4 - Convertir una lista al formato de referencia (Priority: P1)

Como operador quiero elegir una plantilla de referencia para transformar una lista de
proveedor a una salida familiar, revisar la correspondencia y descargar el resultado
sin necesitar cuentas de Mercado Libre conectadas.

**Why this priority**: La conversión es el primer resultado útil solicitado y permite
contrastar una entrada real con la salida esperada antes de sincronizar.

**Independent Test**: Con los casos iniciales derivados de las referencias por delegación
del usuario, convertir la lista y comparar estructura, identificadores y resultados
esperados de la versión 0.1; ampliar después con originales de proveedores.

**Acceptance Scenarios**:

1. **Given** una plantilla de salida confirmada, **When** se elige para la conversión,
   **Then** se muestra su versión, las columnas relacionadas y los campos pendientes.
2. **Given** una lista con títulos, bloques y hojas auxiliares, **When** se interpreta,
   **Then** se clasifican esas filas y se conserva su trazabilidad sin contarlas como productos.
3. **Given** un mapeo revisado, **When** se exporta, **Then** se genera un archivo separado
   que cumple el contrato aprobado, manteniendo intacto el original y reportando pendientes.
4. **Given** fórmulas o reglas ambiguas en el ejemplo, **When** se propone la salida,
   **Then** no se adoptan como reglas aprobadas ni se inventan resultados.

### User Story 5 - Reutilizar correcciones con alcance explícito (Priority: P2)

Como operador quiero que las correcciones confirmadas ayuden en las próximas listas
del mismo proveedor y formato, con historial para revisar o retirar una regla.

**Why this priority**: La retroalimentación reduce trabajo repetido y necesita evitar
que una corrección local altere otros proveedores o conversiones anteriores.

**Independent Test**: Corregir una primera carga, confirmar una regla y cargar una
segunda lista compatible y otra incompatible; comprobar alcance e historial.

**Acceptance Scenarios**:

1. **Given** una corrección de una fila, **When** se guarda sin confirmar generalización,
   **Then** solo afecta la carga correspondiente y la regla reutilizable queda propuesta.
2. **Given** una regla confirmada para un proveedor y formato, **When** se recibe una
   lista compatible, **Then** el sistema muestra el perfil/versión y las reglas usadas.
3. **Given** una lista de otro proveedor o con estructura incompatible, **When** se carga,
   **Then** la corrección anterior no se aplica como válida y se solicita revisar el mapeo.
4. **Given** una regla retirada, **When** se consulta el historial o se elige una versión
   previa para reconvertir, **Then** se conservan origen, autor, fecha, cambio y alcance,
   sin modificar conversiones históricas.
5. **Given** una regla de cálculo inicial basada en la referencia, **When** se modifica
   un factor, tramo, base o redondeo, **Then** se muestran filas afectadas, se crea una
   versión nueva y la revisión anterior conserva sus resultados y parámetros.

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
- Un identificador compuesto o multilínea no implica una única publicación ni permite inferir la cuenta.
- Una fórmula con error atrapado puede mostrar cero; detectar referencias rotas y no considerar ese cero una tarifa confirmada.
- Dos hojas con nombres visualmente similares pueden representar usos distintos; no fusionarlas por normalización del título.
- Una nueva lista puede tener las mismas cabeceras y cambiar unidades o significado; la compatibilidad del perfil no depende solo de los títulos.

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
- **FR-014**: DEBE permitir elegir una plantilla de salida y su versión, cuyo contrato defina columnas, orden, presentación y tratamiento de fórmulas/auxiliares según lo confirmado por el operador.
- **FR-015**: DEBE convertir y exportar listas revisadas sin conexión a Mercado Libre, con trazabilidad de origen a salida y sin modificar originales.
- **FR-016**: DEBE distinguir productos, encabezados, categorías, notas y tablas auxiliares; contabilizar las filas excluidas con su motivo.
- **FR-017**: DEBE diferenciar corrección de fila, regla reutilizable y cambio de plantilla; no generalizar una corrección sin confirmación de su alcance.
- **FR-018**: DEBE conservar proveedor, formato compatible, versión, evidencia, autor, fecha, cambio y estado de cada regla reutilizable y permitir retirarla o usar una versión previa en una nueva conversión.
- **FR-019**: DEBE detectar incompatibilidades relevantes de estructura o significado y exigir revisar el perfil antes de reutilizarlo como válido; no extender reglas a otros proveedores automáticamente.
- **FR-020**: DEBE mantener los resultados históricos vinculados a sus versiones; cambios de reglas o plantilla no los reescriben sin una nueva revisión/conversión.
- **FR-021**: DEBE mostrar por separado dato ingresado, resultado disponible y presentación cuando difieran de manera relevante, señalando errores de fórmula y referencias rotas detectadas sin recalcular silenciosamente.
- **FR-022**: DEBE permitir cambiar reglas de cálculo y parámetros por perfil, incluidas bases, secuencias de descuentos, presentaciones, factores, cargos, tramos y redondeos presentes en la referencia, mostrando su alcance y creando versiones sin reescribir resultados históricos.
- **FR-023**: DEBE exportar exactamente los resultados de la revisión elegida y sus orígenes, sin reinterpretar silenciosamente los archivos al descargar. Los campos con dependencia inválida quedan pendientes, con evidencia e incidencia; no se certifican sus valores históricos como correctos.
- **FR-024**: DEBE proteger el panel local y sus datos mediante autenticación, sesiones revocables y controles de origen; las importaciones, reglas y revisiones persisten al reiniciar. El modo inicial se limita al equipo local y no se declara despliegue productivo público.

### Key Entities *(include if feature involves data)*

- **Importación**: archivo recibido, huella para detectar repetición, selección de hojas, momento, estado y resumen de revisión.
- **Perfil de mapeo**: significado de columnas, formato de origen y reglas de interpretación explícitas.
- **Fila interpretada**: origen, identificadores, valores originales e interpretados, estado y motivos.
- **Producto interno**: identidad comercial consolidada; no presupone que el código de proveedor sea el SKU interno.
- **Cuenta y vínculo de publicación**: destino comercial y relación explícita con producto/variación.
- **Diferencia propuesta**: dato, valor conocido, valor propuesto, destino y elegibilidad; no representa una operación aplicada.
- **Informe**: representación descargable del resultado de revisión.
- **Plantilla de salida**: estructura de referencia y versión de su contrato confirmado; no presupone una única hoja universal.
- **Corrección y regla**: cambio local o reutilizable, evidencia, autor, fecha, alcance, versión y estado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cada fila de los archivos de aceptación queda contabilizada como utilizable, pendiente o rechazada; ninguna desaparece sin explicación.
- **SC-002**: En los casos de códigos con ceros iniciales, duplicados y campos vacíos, el 100% conserva su identidad o recibe una advertencia explícita; ningún vacío se convierte en cero automáticamente.
- **SC-003**: En una comparación con dos cuentas, el 100% de las diferencias pertenece a los destinos elegidos; no aparecen escrituras para Full ni vínculos ambiguos habilitados.
- **SC-004**: El operador puede descargar un informe que concuerda con los estados y totales de la revisión en todos los archivos de aceptación.
- **SC-005**: Cargar, comparar y descargar, incluso repitiendo un archivo, produce cero cambios remotos y cero movimientos de inventario.
- **SC-006**: En cada pareja de aceptación aprobada, el 100% de las columnas y transformaciones exigidas por la plantilla coincide con la salida esperada; todo pendiente queda identificado.
- **SC-007**: En escenarios de corrección local, proveedor distinto y estructura incompatible, se producen cero generalizaciones fuera del alcance confirmado.
- **SC-008**: Cada conversión de aceptación identifica las versiones de perfil, reglas y plantilla utilizadas y permite consultar el resultado histórico sin alteraciones tras cambiar una regla.
- **SC-009**: En los casos iniciales CAS-01 a CAS-09, el 100% de las identidades, estados, exclusiones y cálculos especificados coincide con el expediente de referencia, sin convertir errores o ausencias en valores certificados.
- **SC-010**: Cambiar y retirar una regla de cálculo produce una nueva revisión reproducible y cero modificaciones en las revisiones anteriores; una descarga mantiene el mismo conjunto de orígenes y resultados revisados.

## Assumptions

- Esta es la primera funcionalidad del MVP, centrada en lectura y revisión. La aplicación de cambios tendrá su propia especificación.
- Se elige XLSX como salida inicial; la entrada de referencia procede de snapshots Google Sheets y casos documentales. El lector de archivos y la exportación se verificarán durante implementación; XLS/CSV y estructuras nuevas se evaluarán cuando corresponda.
- Se pueden usar ejemplos identificados como ficticios para diseñar escenarios, pero los archivos reales definirán los casos de aceptación finales.
- La comparación requiere un catálogo previamente disponible; puede validarse con datos controlados. La conexión de cuentas se especificará por separado.
- Se recibió una referencia Google Sheets con 17 pestañas. El usuario autorizó usarla como base inicial y recibir después listas originales; su ausencia deja de bloquear el plan v0.1. Ver docs/BASE_INICIAL_V0.md y docs/CASOS_REFERENCIA_V0.md; no se declara compatibilidad con proveedores no recibidos.
- Los perfiles iniciales se eligen por delegación del usuario. Las cargas compatibles reutilizan el perfil mostrando versión y alcance; una estructura o significado incompatible queda pendiente de revisión, sin cuestionario obligatorio por cada carga reconocida.
- No se ejecutan macros ni vínculos externos contenidos en archivos.
- Fuera de esta funcionalidad: escritura en Mercado Libre, procesamiento de ventas, alertas comerciales y modificación automática del Excel local.
- Retroalimentar significa conservar y reutilizar correcciones confirmadas; no presupone entrenamiento de un modelo ni autoriza enviar datos a nuevos servicios externos.
- La prioridad de implementación propuesta es historias 1 y 4; luego 3 y 5. La historia 2 requiere catálogo y puede abordarse después de validar la conversión autónoma. Se conservan los números de historia para mantener trazabilidad del borrador anterior.

## Base inicial y decisiones diferidas

Se eligió AD como primer recorrido; cada estructura distinta conserva su propio perfil.
La semejanza exige columnas, encabezados, bloques y significado del perfil, con formato
equivalente por tipo y sin réplica visual exacta. Las fórmulas funcionales requieren
dependencias válidas; la revisión conserva evidencia aun cuando la salida deje el
derivado pendiente. VALOR se conserva como base del perfil, promoción como otro campo;
no se deducen precio remoto, moneda ausente, SKU interno ni stock de métricas de ventas.

Reglas, excepciones y formatos son modificables/versionados según FR-022. La precisión
del dato se distingue de su formato visible; no hay un redondeo universal inventado.
Los casos reales seleccionados y sus resultados están documentados en el expediente
privado, con índice anonimizado. La revisión admite pendientes con informe completo.

Puede elaborarse el plan inicial con esta base. Se difieren los nuevos formatos de
proveedores, la política de sincronización, capacidades de cuentas, depósitos y
requisitos productivos de escala. La implementación continúa sin autorizarse en esta
sesión y requiere su propio flujo; no se afirma un contrato definitivo de proveedores.

## Investigación de referencia para las siguientes aclaraciones

El usuario aportó AnalizadorPlanillas como ejemplo funcional y pidió comparar otros
sistemas. Consultar [síntesis y matriz REF-01 a REF-12](../../docs/SISTEMAS_REFERENCIA.md)
antes de las siguientes aclaraciones. Allí se relacionan evidencias con estos FR/SC
y se proponen casos; no se incorporan automáticamente al contrato ni se copia la
plantilla del referente. La investigación por sí sola no aprueba reglas; las decisiones
de esta aclaración se basan en la delegación posterior del usuario y la referencia real.
