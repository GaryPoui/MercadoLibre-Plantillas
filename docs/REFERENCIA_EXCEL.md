# Referencia de planillas y consecuencias para el sistema

Revisión inicial: 2026-11-02. Se recibió un enlace a un libro de Google Sheets con 17 pestañas. Se leyeron sus metadatos, una muestra inicial y después el contenido celular de la cuadrícula completa declarada de cada pestaña. Esto permite perfilar valores, fórmulas y errores, pero no constituye una auditoría de todas las propiedades del libro ni se recibió todavía un conjunto de Excel de entrada de proveedores con sus salidas corregidas.

Las capturas y el informe con coordenadas, fórmulas e información comercial se conservan en `data/private/referencia-mistica-inicial.json`, `data/private/snapshot-<sheetId>.json` y `data/private/ANALISIS_MISTICA.md`, excluidos de Git. El documento remoto se mantuvo intacto. Las capturas no sustituyen un original Excel ni una exportación completa de formatos, validaciones y otras propiedades.

## Lo que aporta la referencia

El perfil celular contabilizó 3537 filas con algún valor, incluidas cabeceras y auxiliares, y 28122 celdas con fórmula. No es un recuento de productos. Se encontraron 65 errores efectivos de división por cero y 570 fórmulas con referencias rotas, estas últimas concentradas en una hoja y susceptibles de quedar ocultas por funciones que devuelven cero. Estos datos describen el estado recibido, no una validación de las reglas comerciales.

- Hay varias estructuras de listas comerciales, junto con tareas, tablas auxiliares y métricas de ventas/reposición. No todas las pestañas deben importarse como catálogo.
- Los encabezados cambian de posición y pueden ocupar varias filas. Hay familias, subfamilias, notas y presentaciones intercaladas entre productos.
- Los identificadores pueden ser textos con ceros iniciales, guiones o puntos, números o varios valores en una misma celda. Algunos códigos se repiten con destinos distintos; otros destinos aparecen asociados con códigos distintos. Las relaciones requieren revisión explícita.
- Costos, valores comerciales, promociones, comisiones, envíos y márgenes son conceptos distintos. Las expresiones observadas varían entre hojas y entre filas: no fundamentan una fórmula universal ni prueban tarifas vigentes.
- Hay errores visibles y referencias rotas ocultas por funciones que devuelven cero. Un resultado numérico aparentemente válido no demuestra que su fórmula sea correcta.
- Existen diferencias entre el valor guardado y su presentación, y entre un importe textual y uno numérico. Deben conservarse ambos para revisar escala y separadores.
- Las unidades vendidas, el peso y las presentaciones no equivalen a stock disponible. La muestra no permite definir todavía el contrato de inventario.

## Ajustes necesarios al planteamiento

El primer resultado del producto debe ser convertir una lista de proveedor a un perfil de salida seleccionado y revisable, conservando la procedencia de cada dato. El sistema necesita interpretar estructuras heterogéneas, mostrar propuestas y errores, recibir correcciones y reutilizar únicamente las reglas confirmadas dentro de su alcance.

La retroalimentación debe ser explícita y versionada: una corrección puntual no se convierte por sí sola en regla para todos los proveedores. Cada perfil debe poder revisarse, reproducirse y revertirse. Si cambia la estructura del archivo o aparecen ambigüedades, la reutilización debe quedar pendiente de revisión.

La referencia define una familia de formatos a estudiar. Todavía debe elegirse qué significa «similar» para cada salida: columnas, orden, hojas, fórmulas, estilos, unidades y campos obligatorios. No corresponde copiar errores de los ejemplos ni reparar fórmulas sin mostrar la propuesta.

## Pendiente para cerrar el contrato

Actualización por instrucción posterior: la [base inicial](BASE_INICIAL_V0.md) autoriza
planificar con los ejemplos existentes y casos preparados por delegación. Los pendientes
siguientes corresponden a ampliación y validación productiva, no bloquean ese plan.

Se necesitan archivos de entrada de proveedores y salidas corregidas representativas; confirmar los significados comerciales, el formato de salida por perfil, las unidades y monedas, las reglas de identidad y los criterios para reutilizar correcciones. Se perfiló el contenido celular completo devuelto; queda pendiente revisar propiedades como celdas combinadas/ocultas/validaciones y verificar las dependencias y el significado comercial. No se implementó el importador ni se realizaron escrituras en Mercado Libre.

