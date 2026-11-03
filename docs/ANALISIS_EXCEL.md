# Guía para analizar los Excel del usuario

Estado al 2026-11-02: referencia Google Sheets de 17 pestañas recibida y perfilada en
lectura; ver [hallazgos](REFERENCIA_EXCEL.md). Pendientes listas originales de proveedores
y salidas aprobadas. No asumir que una referencia fija un único contrato universal.

El usuario delegó usar estas referencias y decidir la versión inicial sin nuevas
respuestas. Ver [base v0.1](BASE_INICIAL_V0.md) y [casos](CASOS_REFERENCIA_V0.md).
Las listas originales futuras amplían perfiles; no bloquean el plan del conversor
inicial. Los parámetros observados se usan como referencia editable y versionada.

## Método

1. Guardar el original en `data/private/`, registrar nombre, tamaño y huella, y trabajar
   sin modificarlo. No ejecutar macros ni recuperar enlaces externos.
2. Inventariar hojas, tablas, rangos usados, filas de títulos/encabezados, filtros,
   celdas combinadas, filas ocultas y hojas de cálculo auxiliares.
3. Comparar valores visibles, tipos, formatos y fórmulas. Identificar celdas cuyo
   resultado guardado falta o puede estar desactualizado.
4. Identificar códigos de producto, proveedor y publicación; revisar ceros iniciales,
   duplicados, variaciones y posibles claves de unión entre hojas o archivos.
5. Determinar con evidencias qué significa cada importe: costo, precio de venta,
   impuesto, descuento, margen, moneda y redondeo. No deducir reglas solo por el título.
6. Determinar qué representa cada cantidad: existencia física, disponible, reserva,
   Full, depósito, stock del proveedor o asignación comercial.
7. Perfilar vacíos, negativos, separadores decimales, fechas, unidades, errores y
   discrepancias entre hojas. Registrar cuántas filas afecta cada problema.
8. Proponer un mapeo reversible y mostrar ejemplos anonimizados del resultado.
   Preguntar únicamente por significados que no se puedan resolver con evidencias.
9. Actualizar `specs/001-importacion-excel/spec.md`, su checklist y el alcance.
   Después elaborar el plan técnico y las tareas.

Para Google Sheets, conservar metadatos y snapshots API privados, indicando rangos y
campos consultados. No describirlos como originales Excel ni atribuirles una huella
del archivo remoto. Distinguir valor ingresado, efectivo y mostrado. La cuadrícula
asignada no equivale al rango de productos y una lectura no constituye una revisión
atómica de todo el libro. Registrar lo no expuesto (ocultas, combinadas, validaciones).

## Conversión y correcciones

- Comparar una lista original con una salida aprobada; acordar qué incluye la similitud.
- Mantener perfiles por proveedor/estructura y plantillas de salida con versiones.
- Registrar si una corrección afecta una fila, una regla o la plantilla; no generalizarla
  a otros proveedores o al historial sin confirmación.
- Construir casos anonimizados con pérdida de ceros, encabezados múltiples, códigos
  compuestos, referencia rota atrapada, diferencias de formato numérico y cambio de estructura.
- Comprobar la salida reabriéndola y contrastando columnas, identidad, filas y reglas
  representativas antes de declarar conversión correcta.

## Registro esperado por archivo

| Elemento | Qué registrar |
| --- | --- |
| Origen | Archivo, fecha recibida, proveedor/uso si se conoce |
| Estructura | Hojas, filas de encabezado, rangos y cantidad de registros |
| Identidad | Claves candidatas y porcentaje de vacíos/duplicados |
| Importes | Moneda, impuesto, fórmulas, escala y significado confirmado |
| Cantidades | Unidades, ubicación, reservas y autoridad del dato |
| Calidad | Problemas, filas afectadas y criterio de aceptación/rechazo |
| Mapeo | Columna de origen, significado, transformación y validación |
| Evidencia | Ejemplos anonimizados y preguntas pendientes |

Conservar el informe detallado en `data/private/` si contiene información comercial real.
Versionar en la especificación solo el contrato y ejemplos anonimizados necesarios.

## Resultado de esta etapa

Contrato de importación basado en archivos reales, perfil de mapeo por formato, casos
de aceptación representativos y decisiones pendientes visibles. No implementar reglas
de precio ni sincronización basándose en supuestos no confirmados.
