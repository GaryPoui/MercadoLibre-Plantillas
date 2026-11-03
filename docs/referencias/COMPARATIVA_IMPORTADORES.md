# Comparativa documental de importadores y preparación de datos

Fecha de consulta: **2026-11-02**, Argentina.

## Alcance y grado de verificación

Se comparan OpenRefine, Flatfile y Dromo como referencias de producto para nuestro
flujo de listas de proveedores. Se consultó documentación pública de sus responsables,
disponible en la fecha indicada. **Documentado** significa que el fabricante o
mantenedor describe esa función; **no significa probado en este proyecto**.
No se instalaron ni contrataron productos, no se crearon cuentas y no se subieron
planillas. No se midieron rendimiento, precisión, accesibilidad ni compatibilidad
con los ejemplos reales. No es una clasificación ni una decisión de proveedor.

El contexto local exige convertir listas a plantillas similares a las referencias,
conservar originales y reutilizar correcciones confirmadas sin propagación indebida.
La referencia tiene múltiples estructuras y fórmulas; aún faltan parejas de entrada
y salida aprobadas. Por eso interesan tanto las funciones como sus límites.
Ver [replanteamiento](../REPLANTEAMIENTO_BASE.md) y
[análisis de referencia](../REFERENCIA_EXCEL.md).

## Comparación de capacidades documentadas

| Aspecto | OpenRefine | Flatfile | Dromo |
| --- | --- | --- | --- |
| Entrada tabular | CSV/TSV y Excel XLS/XLSX, entre otros [O1](https://openrefine.org/docs/manual/starting) | CSV nativo; Excel mediante extractor [F1](https://support.flatfile.com/articles/7898986828-why-can-t-i-extract-excel-files) | CSV, TSV, XLS y XLSX [D1](https://developer.dromo.io/faqs) |
| Mapeo y preparación | Edición de columnas y transformaciones del proyecto [O2](https://openrefine.org/docs/manual/transforming) | Selección de hoja y correspondencia origen/destino con revisión [F2](https://support.flatfile.com/articles/8569925090-mapping-data) | Selección de columnas y memoria configurable por tipo de importación [D2](https://developer.dromo.io/reference/settings/settings) |
| Revisar calidad | Facetas por valores, vacíos y errores [O3](https://openrefine.org/docs/manual/facets) | Mensajes de validación y transformaciones mediante hooks [F3](https://flatfile.com/docs/plugins/record-hook) | Validadores por campo y errores explicativos [D3](https://developer.dromo.io/reference/fields/field-validators) |
| Reutilizar trabajo | Extraer/aplicar operaciones JSON; algunas ediciones no son extraíbles [O4](https://openrefine.org/docs/manual/running/) | Historial de mapeo por entorno y esquema [F4](https://support.flatfile.com/articles/8421984657-how-does-flatfile-ensure-mapping-is-as-accurate-as-possible) | `autoMapHeaders` con el mismo `importIdentifier` [D2](https://developer.dromo.io/reference/settings/settings) |
| Recuperar trabajo | Historial Undo/Redo persistido con el proyecto [O4](https://openrefine.org/docs/manual/running/) | Prepare permite revertir cambios de su versión de trabajo [F5](https://support.flatfile.com/articles/3401719421-prepare) | Guardar/restaurar sesiones con configuración y persistencia de servidor [D4](https://developer.dromo.io/guides/saving-progress) |
| Salida | CSV/TSV, XLS/XLSX, exportación personalizada y archivo de proyecto [O5](https://openrefine.org/docs/manual/exporting) | Plugin de exportación de Workbook a XLSX [F6](https://flatfile.com/docs/plugins/export-workbook) | Resultados estructurados y descarga Excel para corregir errores [D1](https://developer.dromo.io/faqs) |

Las celdas describen capacidades puntuales, no equivalencias de alcance: un historial
de correspondencias, un historial de cambios y una sesión reanudable son mecanismos
distintos. Ninguno acredita por sí solo las reglas comerciales de este negocio.

## OpenRefine: limpieza explícita y operaciones reproducibles

### Entrada y conservación

Al iniciar un proyecto, OpenRefine copia los datos a su espacio de trabajo y mantiene
la fuente original. Admite varias fuentes y, cuando se combinan archivos, añade
procedencia y alinea columnas por nombre. Su documentación describe colaboración
mediante intercambio de proyectos, no acceso concurrente al mismo proyecto local.
[O1: inicio de proyectos](https://openrefine.org/docs/manual/starting).

### Mapeo, diagnóstico y correcciones

El modelo de trabajo permite limpiar valores, transformar columnas y reorganizar
datos; no debe confundirse con un importador embebido que imponga automáticamente
nuestro contrato de salida.
[O2: transformación](https://openrefine.org/docs/manual/transforming).

Las facetas permiten explorar distribuciones, valores vacíos y errores para localizar
grupos problemáticos. Son un patrón útil para revisar el alcance antes de corregir.
Su presencia no demuestra validación de moneda, impuestos ni identidad del producto;
esas son reglas que este proyecto deberá definir.
[O3: facetas](https://openrefine.org/docs/manual/facets).

### Reutilización e historial

Undo/Redo registra cambios desde la creación. Las operaciones extraíbles se guardan
como JSON y pueden aplicarse en otro proyecto; una edición individual de celda no
es una receta reutilizable. Si se retrocede y se ejecuta una operación nueva, la
rama posterior se elimina del historial activo. Esta distinción aporta un precedente
concreto para separar corrección local y transformación generalizable.
[O4: historial y reutilización](https://openrefine.org/docs/manual/running/).

### Exportación y límites relevantes

La exportación puede depender de la vista y filtros actuales. La salida tabular
personalizada permite ordenar columnas y reutilizar opciones; el archivo de proyecto
incluye datos e historial, incluso información anterior a una anonimización. Compartir
solo una salida limpia tiene implicaciones distintas de compartir todo el proyecto.
[O5: exportación](https://openrefine.org/docs/manual/exporting).

OpenRefine trabaja con valores: no conserva fórmulas de hoja de cálculo para mostrar
sus resultados, ni colores o formatos de texto. Por ello, **no acredita la
reproducción fiel de nuestras plantillas con fórmulas y presentación**. Esta limitación
está documentada; la incompatibilidad concreta con cada hoja no se probó.
[O6: modelo de datos](https://openrefine.org/docs/manual/exploring).

## Flatfile: separar extracción, mapeo y revisión

### Entrada y extracción

La documentación de soporte distingue CSV nativo y un extractor Excel desplegado
en servidor para el flujo embebido; no basta con dibujar una zona de carga.
[F1: habilitar Excel](https://support.flatfile.com/articles/7898986828-why-can-t-i-extract-excel-files).

El extractor documenta XLS, XLSX y otras variantes, detección de encabezados y opciones
`raw` y `rawNumbers`. Por defecto puede tomar representación formateada y decimales
mostrados; obtener el valor subyacente exige configurar las opciones correspondientes.
También permite elegir filas específicas de encabezado. **Aceptar una extensión no
equivale a preservar fórmulas, estilos o macros**: esas propiedades no quedaron
demostradas con esta consulta.
[F7: extractor Excel](https://flatfile.com/docs/plugins/xlsx-extractor).

También existen opciones para propagar valores de filas/encabezados y tratar
combinaciones copiando valores, conservando la esquina o agrupando filas/columnas.
No son operaciones neutras: en nuestras listas podrían convertir notas o vacíos en
datos repetidos. Su configuración debe quedar ligada al perfil confirmado.
[F7: opciones avanzadas y celdas combinadas](https://flatfile.com/docs/plugins/xlsx-extractor).

### Mapeo y validación

En archivos con varias hojas, el usuario elige la hoja y el destino. La interfaz
presenta propuestas, ejemplos y correspondencias de categorías. Las columnas no
mapeadas quedan excluidas; una opción de categoría puede mantenerse o descartarse,
produciendo un vacío. Son decisiones que nuestro producto debe hacer visibles y
contabilizar, en lugar de interpretar la exclusión como desaparición aceptable.
[F2: mapeo](https://support.flatfile.com/articles/8569925090-mapping-data).

Los record hooks ejecutan lógica sobre registros añadidos o actualizados y pueden
anotar errores o transformar valores; requieren configurar la lógica pertinente.
No contienen de antemano el significado de nuestros costos o cantidades.
[F3: record hooks](https://flatfile.com/docs/plugins/record-hook).

### Qué se recuerda y qué se puede deshacer

Flatfile describe una memoria de correspondencias segregada por entorno y esquema,
guardada tras completar el mapeo; permite eliminar esa memoria. La documentación
también señala que una opción nueva sustituye la historia anterior. Esto ayuda a
predecir mapeos; **no equivale a un archivo inmutable de versiones de reglas de negocio**.
[F4: memoria de mapeo](https://support.flatfile.com/articles/8421984657-how-does-flatfile-ensure-mapping-is-as-accurate-as-possible).

Prepare modifica una copia de trabajo, permite deshacer y conserva versiones. No
mapea automáticamente al esquema destino ni admite fórmulas de Excel como VLOOKUP.
Es una etapa diferente del mapeo y la validación posterior; no debe atribuirse su
historial a toda operación de la plataforma sin comprobarlo.
[F5: Prepare](https://support.flatfile.com/articles/3401719421-prepare).

### Salida y automatización

Existe un plugin de servidor que exporta las hojas de un Workbook a un XLSX
descargable. La documentación consultada **no demuestra reconstrucción de una
plantilla arbitraria con todas las fórmulas y formatos del original**.
[F6: exportar Workbook](https://flatfile.com/docs/plugins/export-workbook).

Automap puede detener el mapeo automático completo si una sola columna no alcanza
la confianza requerida. El caso de varias hojas necesita lógica adicional y el
plugin está destinado al servidor. Este límite interesa para nuestras 17 pestañas:
un mecanismo de confianza no reemplaza selección de bloques, semántica y revisión.
[F8: Automap, límites](https://flatfile.com/docs/plugins/automap).

## Dromo: importador embebido con memoria configurable

### Flujo, validación y recuperación de errores

El flujo documentado acepta CSV/TSV/XLS/XLSX, mapea columnas, permite correcciones
y devuelve datos estructurados. La revisión puede descargarse como Excel anotado
para corregir y volver a cargar. El procesamiento en navegador depende de sus
recursos; no se toman las afirmaciones comerciales de capacidad como límites
validados para nuestro proyecto.
[D1: preguntas frecuentes](https://developer.dromo.io/faqs).

Los validadores incluyen obligatoriedad, unicidad —también combinada entre campos—,
expresiones y mensajes personalizados. Una clave compuesta puede servir para
detectar duplicados, pero solo después de confirmar qué identifica un producto.
[D3: validadores](https://developer.dromo.io/reference/fields/field-validators).

### Reutilización, datos excluidos y efecto de los valores por defecto

`autoMapHeaders` recuerda correspondencias del mismo `importIdentifier`. Requiere
`MAPPINGS_ONLY` o `FULL_DATA`: el primero almacena mapeos **y valores únicos de
campos select**; el segundo almacena todos los datos. La política predeterminada
de errores es `REMOVE_INVALID_ROWS`, con aviso de descarte; existe `BLOCK_SUBMIT`.
Estas opciones requieren una decisión expresa en nuestro diseño: privacidad y
contabilización de filas no quedan resueltas por instalar un SDK.
[D2: configuración](https://developer.dromo.io/reference/settings/settings).

La guía documenta cómo capturar columnas no mapeadas. Esto ofrece un patrón para
conservar auxiliares, pero debe configurarse y verificarse; no acredita conservación
automática de todas las propiedades de un libro.
[D5: columnas no mapeadas](https://developer.dromo.io/guides/accessing-unmapped-columns).

### Sesiones, historial y salida

Guardar progreso requiere `FULL_DATA`; captura etapa, mapeos, transformaciones,
filas y archivo en servidor. La guía distingue identificador de sesión y token
temporal, y documenta vencimiento. **Una sesión recuperable no constituye un
registro permanente e inmutable de correcciones confirmadas**: esta última capacidad
no se verificó. Nuestro historial necesitaría requisitos y pruebas propios.
[D4: guardar/restaurar](https://developer.dromo.io/guides/saving-progress).

El callback de finalización devuelve datos y metadatos; `beforeFinish` permite
controlar la finalización. Esta salida estructurada no demuestra que se genere
una plantilla comercial con fórmulas, estilos y hojas auxiliares como las nuestras.
[D6: resultados](https://developer.dromo.io/reference/results).

## Aplicación al planteamiento del proyecto

Las siguientes son **inferencias de diseño**, no funciones probadas ni adopciones:

1. Separar recepción, extracción de bloques, mapeo, corrección y exportación.
   Los tres referentes distinguen datos de entrada y estado de trabajo; nuestro
   original debe seguir disponible para explicar cualquier transformación.
2. Mostrar columnas y filas excluidas, junto con sus motivos. El descarte es una
   decisión visible; no equivale a corregir un dato y debe cuadrar con los totales.
3. Mantener tres memorias distintas: historial de una carga, perfil reutilizable
   y plantilla de salida. Recordar una correspondencia no acredita una regla fiscal.
4. Definir el alcance de memoria con proveedor, contrato y versión compatibles.
   Un nombre de archivo o identificador de importación aislado no protege contra
   cambios de significado con las mismas cabeceras.
5. Mantener la IA como propuesta revisable. No copiar afirmaciones de precisión
   del fabricante ni convertirlas en criterio de aceptación del sistema.
6. Probar por separado integridad del dato y fidelidad del Excel. Importar XLSX,
   devolver JSON y descargar XLSX no prueban que fórmulas y presentación coincidan.
7. No adoptar servicios de almacenamiento ni enviar ejemplos por esta investigación.
   Una futura evaluación de servicio debe comprobar qué sale del equipo, qué se
   conserva y cómo se retira; no asumir que «solo mapeos» significa ausencia de datos.

## Prueba comparativa pendiente si se evalúan herramientas

Sin ejecutarla ahora, la evaluación futura debería usar muestras anonimizadas y
un contrato de salida aprobado con estos casos: ceros iniciales, vacío frente a cero,
importe textual frente a numérico, encabezados múltiples, notas entre productos,
hojas auxiliares, fórmula sin resultado y referencia rota oculta por cero; además,
dos cargas compatibles y una que cambia unidad sin cambiar encabezado.

Para cada caso se comprobarían conteos, valores, exclusiones, evidencia del mapeo,
confirmación/retirada de reglas, reproducción histórica y estructura de salida.
Quedan sin verificar soporte concreto de libros protegidos, formato y fórmulas de
nuestras plantillas, comportamiento con macros/enlaces, capacidades de cuenta,
permisos, retención y rendimiento real. **Ausencia de evidencia aquí no significa
ausencia de la función en el producto.**

La conclusión documental es aprovechar patrones de interacción y trazabilidad,
manteniendo abierto el mecanismo técnico. No se recomienda comprar, sustituir
Spec Kit ni iniciar la integración con ningún referente en esta etapa.
