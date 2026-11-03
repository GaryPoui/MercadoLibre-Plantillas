# Feature Specification: Panel y carga guiada

**Feature Branch**: `codex/mvp-excel`
**Feature Directory**: `specs/002-experiencia-panel`
**Created**: 2026-11-03
**Status**: Implementada y verificada2026-11-03; próximos módulos no implementados
**Input**: Mejorar diseño y experiencia de carga conservando el MVP, y continuar los specs faltantes.

## Clarifications

Se adopta una interfaz de trabajo clara con inicio, carga guiada, SKU/precio prioritarios,
búsqueda y estados explicados. Decisiones visuales delegadas. No exige conectar cuentas
ni implementar todas las entregas futuras en este cambio. Sin preguntas comerciales nuevas:
no se introducen fórmulas, monedas ni claves de unión. Se conserva la selección explícita.

## User Scenarios & Testing

### User Story 1 - Saber por dónde empezar (Priority: P1)
Como operador quiero ver los datos reales de mi espacio y una acción para cargar una lista.
**Why this priority**: Evita una pantalla vacía y explica qué ya se puede usar.
**Independent Test**: Abrir un espacio vacío y otro con cargas, revisar contadores e historial.
**Acceptance Scenarios**:
1. **Given** un espacio vacío, **When** ingreso, **Then** veo una invitación a cargar una lista y contadores cero.
2. **Given** cargas guardadas, **When** abro Inicio, **Then** veo cantidades reales y las últimas cargas sin datos ficticios.

### User Story 2 - Cargar y revisar sin perderme (Priority: P1)
Como operador quiero distinguir archivo, correspondencias y resultado, dando prioridad al SKU y precio.
**Why this priority**: Es el trabajo principal de conversión.
**Independent Test**: Recorrer XLSX/CSV, elegir columnas, corregir y descargar con el panel nuevo.
**Acceptance Scenarios**:
1. **Given** una carga nueva, **When** elijo columnas, **Then** cada opción indica letra y encabezado y los pasos muestran mi progreso.
2. **Given** una revisión, **When** guardo, **Then** puedo ir a la lista unificada o descargar sin perder el resultado.
3. **Given** una operación en curso, **When** intento repetirla, **Then** el formulario indica actividad y evita otro envío desde ese formulario.

### User Story 3 - Revisar precios en cualquier pantalla (Priority: P2)
Como operador quiero leer SKU y precio y filtrar pendientes desde teclado o pantalla pequeña.
**Why this priority**: La revisión debe ser práctica sin ocultar errores.
**Independent Test**: Filtrar, limpiar búsqueda y recorrer el panel a390px y1440px.
**Acceptance Scenarios**:
1. **Given** filas listas y pendientes, **When** filtro o limpio, **Then** la tabla y el conteo filtrado coinciden.
2. **Given** una pantalla pequeña, **When** navego, **Then** no se desborda la página y las tablas permiten desplazamiento.

### Edge Cases
- Fallo de carga: mostrar error y conservar el archivo/criterios seleccionados cuando sea posible.
- Sesión vencida: mostrar acceso sin dejar resultados comerciales visibles.
- Espacio sin proveedores identificados: no inventar nombres ni contarlos como identificados.
- Encabezados múltiples/largos o vacíos: mostrar letra siempre, sin seleccionar por posición.

## Requirements
### Functional Requirements
- **FR-001**: Mostrar Inicio con cargas, productos revisados, pendientes y proveedores identificados a partir de datos persistidos.
- **FR-002**: Proveer navegación clara entre Inicio, carga, lista unificada, historial y perfiles; catálogo controlado identificado como herramienta de prueba.
- **FR-003**: Mostrar tres pasos de carga con estado actual; preservar selección, revisiones, perfiles y descargas existentes.
- **FR-004**: Mostrar letra y nombre de columna en el mapeo; priorizar SKU y precio sin aceptar sugerencias como confirmaciones automáticas.
- **FR-005**: Permitir abrir la lista unificada desde el resultado y limpiar filtros; distinguir sin resultados de espacio vacío.
- **FR-006**: Mostrar actividad, estados vacíos y errores legibles; acceso por teclado, foco visible y estados con texto.
- **FR-007**: Mantener autenticación, datos e historial y operar a390px sin desbordamiento de página.

### Key Entities
- Resumen del espacio: contadores reales, cargas recientes y pendientes.
- Paso de carga: archivo, correspondencias, resultado; estado efímero de navegación.
- Revisión/perfil: entidades existentes; no migrarlas para un cambio visual.

## Success Criteria
- **SC-001**: Contadores coinciden con API en espacio vacío y con datos controlados.
- **SC-002**: Recorrido anterior XLSX/CSV/corrección/perfiles/exportación sigue funcionando.
- **SC-003**: Inicio, mapeo y lista unificada se usan a390px y1440px sin errores JS ni desbordamiento horizontal de página.
- **SC-004**: Todos los campos conservan etiquetas; el flujo y filtros son accesibles por teclado.

## Assumptions
Modo local, un operador. No se certifica WCAG por este recorrido. Se conservan límites de001.
Los specs003..007 describen funcionalidades futuras y sus condiciones previas, no capacidades entregadas.
