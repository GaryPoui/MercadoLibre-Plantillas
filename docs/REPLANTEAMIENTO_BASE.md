# Replanteamiento de la base del proyecto

Fecha: 2 de noviembre de 2026 (Argentina). Estado: propuesta documental para aclarar;
no autoriza ni inicia implementación, despliegue ni escrituras externas.

**Actualización posterior:** el usuario delegó avanzar con estas referencias y reglas
editables. La [base inicial v0.1](BASE_INICIAL_V0.md) y sus casos sustituyen los bloqueos
de este diagnóstico que exigían nuevas listas o respuestas antes de planificar.
El resto conserva la investigación y sus límites; no se autoriza código.

## Problema y resultado esperado

Las listas de proveedores llegan con estructuras diferentes. El operador necesita
convertirlas a una salida familiar, similar a los ejemplos aportados, sin perder
identificadores ni confundir costo, precio, cantidad, venta o fórmula. Cada corrección
confirmada debe poder ayudar en cargas futuras sin ocultar su origen y alcance.

La integración con varias cuentas de Mercado Libre sigue siendo el objetivo general.
La conversión de archivos debe entregar valor por sí sola, antes de conectar cuentas.
Convertir una planilla, guardar una regla y publicar un cambio son acciones diferentes.

## Qué está confirmado y qué se propone

Confirmado en esta sesión: investigar, documentar, instalar habilidades, trabajar con
subagentes y replantear la base; no escribir código de la aplicación. Se aporta un
libro Google Sheets como referencia de los formatos deseados. Se requiere incorporar
futuras listas de proveedores y correcciones como retroalimentación.

Confirmado previamente: varias cuentas, Excel, inventario propio y Full y sincronización
bidireccional. Las tecnologías del chat anterior continúan como candidatas.

Propuesta de esta revisión: perfiles por proveedor y versión de estructura, plantillas
de salida versionadas, correcciones reutilizables confirmadas y exportación independiente
de Mercado Libre. El mecanismo preciso de aprendizaje no está decidido. No se promete
entrenamiento automático de modelos ni una regla universal a partir de una corrección.

## Evidencia que cambia el planteamiento

La referencia contiene 17 pestañas y varias familias: listas comerciales, cálculo de
costos/envío, tareas y reposición/ventas. Se leyeron valores ingresados, resultados y
representación visible de las celdas de todas sus cuadrículas. No se modificó el libro.

El perfilado contó 3.537 filas con algún dato, incluidas cabeceras y auxiliares;
NO es un conteo de productos. Se observaron 28.122 celdas con fórmula y 65 celdas con
error de cálculo. Además, se detectaron 570 fórmulas con referencias rotas, cuyos
errores pueden quedar ocultos por un resultado cero. Las diferencias entre hojas
impiden fijar un único mapeo por posición.
Los números reflejan esta lectura, no un límite de capacidad ni una auditoría funcional.

Hay diferencias entre el dato numérico y su presentación, códigos con formatos
heterogéneos, encabezados de más de una fila y dependencias entre hojas. Las fórmulas
son evidencia del uso actual, no reglas comerciales aprobadas ni tarifas vigentes.
El análisis y las coordenadas comerciales permanecen en `data/private/`.
Ver [resumen del análisis](REFERENCIA_EXCEL.md).

## Flujo propuesto del producto

1. Recibir la lista y preservar su original; identificar proveedor y uso cuando se conozcan.
2. Mostrar hojas y bloques detectados; distinguir productos, títulos, notas y auxiliares.
3. Sugerir un perfil compatible o construir un mapeo revisable; mostrar dudas y evidencia.
4. Interpretar sin perder el dato original; separar vacíos, cero, texto, número y fórmula.
5. Revisar errores y comparar la salida propuesta con una plantilla elegida y versionada.
6. Corregir una fila o confirmar una regla con alcance explícito; conservar ambas decisiones.
7. Exportar un archivo separado y un informe; identificar pendientes sin inventar resultados.
8. En una fase posterior, comparar con cuentas seleccionadas y aplicar solo cambios
   autorizados según capacidades verificadas y reglas de conflicto.

## Retroalimentación controlada

El sistema debe distinguir tres acciones: corregir un valor en una carga, confirmar una
regla reutilizable y corregir la plantilla de salida. Cada una tiene efectos diferentes.

Una regla propuesta conserva evidencia de origen, autor de la confirmación, fecha,
proveedor, estructura compatible, campo afectado, versión y estado. Estados conceptuales:
propuesta, confirmada y retirada. El plan decidirá su representación técnica.

Al volver a cargar una estructura compatible, el sistema puede sugerir/reutilizar el
perfil confirmado y mostrar qué reglas intervienen. Si cambian encabezados, tipos,
unidades o dependencias relevantes, debe señalar la incompatibilidad. La corrección
no se extiende a otro proveedor ni cambia resultados históricos sin una nueva revisión.
Debe poder desactivarse y recuperarse una versión anterior para una nueva conversión.

La automatización futura requiere una política definida. Una sugerencia de IA conserva
su condición de sugerencia hasta ser confirmada; ni su confianza estimada ni una
descripción parecida resuelven por sí solas identidad, impuestos o precio de venta.
No se subirán listas comerciales a servicios adicionales por instalar una habilidad.

## Límites de responsabilidad propuestos

| Área | Responsabilidad | Evita |
| --- | --- | --- |
| Recepción y análisis | Original, procedencia, hojas, bloques, calidad | Perder evidencia |
| Perfiles y correcciones | Correspondencias, reglas y versiones | Contaminar proveedores o historial |
| Interpretación y revisión | Datos de trabajo y diferencias trazables | Confundir valor, fórmula y presentación |
| Plantillas y exportación | Contrato de salida y comprobación de compatibilidad | Copiar errores como reglas |
| Catálogo y vínculos | Identidades internas y destinos por cuenta/variación | Fusionar productos por nombre |
| Inventario | Existencia compartida, reservas, propio y Full | Sobreasignar o descontar dos veces |
| Sincronización | Intenciones, intentos, conflictos y resultado verificado | Declarar éxito solo por envío |

Esto es un mapa conceptual, no un modelo de datos final ni una selección de servicios.
El monolito modular es una opción razonable a evaluar; no hay evidencia de volumen
que justifique microservicios. FastAPI, React, PostgreSQL y workers siguen pendientes
del plan. No se instalaron dependencias del producto.

## Diseño web

Priorizar el trabajo del operador: selección de archivo, mapeo comprensible, explicación
de errores, comparación origen/salida, confirmación de reglas y descarga. Mostrar siempre
proveedor, perfil/versión y, cuando corresponda, cuenta y logística. Los estados necesitan
texto, no solo colores. Conservar el progreso y permitir volver a corregir.

Se propone accesibilidad WCAG 2.2 AA como objetivo de diseño pendiente de formalizar,
sin afirmar conformidad. No se elige todavía paleta, tipografía, biblioteca ni framework.
Ver [investigación de diseño](INVESTIGACION_DISENO_WEB.md).

## Decisiones pendientes, ordenadas por impacto

1. Salida deseada: elegir una o varias hojas representativas y precisar qué significa
   «similar»: columnas, orden, estilos, fórmulas y hojas auxiliares.
2. Significado y vigencia de los importes: qué valor es entrada, cuál es salida,
   moneda por campo y reglas aprobadas por proveedor/producto/presentación.
3. Identidad: código proveedor, SKU interno, publicación, catálogo y variación;
   tratamiento de una celda con varios identificadores y de códigos faltantes.
4. Alcance de una corrección: fila, proveedor, versión de plantilla o regla general;
   quién puede confirmarla y qué automatización futura se desea.
5. Recepción de listas originales de proveedores para contrastar entrada y salida.
6. Volumen real, formatos recibidos, frecuencia, cuentas y depósitos habilitados.

Se registran para la siguiente conversación; esta entrega no exige resolverlas para
continuar documentando ni inventa respuestas. La disponibilidad de una referencia
no equivale a haber recibido una pareja entrada/salida validada.

## Hoja de ruta documental

- Ahora: contexto leído, investigación y habilidades selectivas, referencia perfilada,
  especificación ampliada, límites y pendientes visibles.
- Después: recibir nuevas listas y correcciones, aclarar las decisiones anteriores y
  fijar casos anonimizados de entrada/salida aprobados.
- Luego: plan técnico, decisiones justificadas, contratos y tareas con Spec Kit;
  analizar su consistencia antes de implementar.
- Implementación posterior: conversión autónoma primero; catálogo y cuentas de lectura;
  precios verificables; inventario/ventas; panel y operación incremental.

No se crean `plan.md` ni `tasks.md` finales en esta etapa porque faltan decisiones del
contrato y el usuario pidió preparación sin código. Las investigaciones no se presentan
como un plan aprobado ni como la ejecución de `speckit-analyze`.

## Fuentes y límites de investigación

Se añadió una [investigación de sistemas similares](SISTEMAS_REFERENCIA.md) por pedido
del usuario: AnalizadorPlanillas como ejemplo funcional y seis referentes externos.
La matriz REF-01 a REF-12 relaciona evidencia con requisitos y preguntas futuras;
no cambia el alcance aprobado ni decide stack, reglas comerciales o formato de salida.

Las fuentes primarias, comparaciones y rutas de habilidades están en
[sistemas](INVESTIGACION_SISTEMAS.md), [diseño](INVESTIGACION_DISENO_WEB.md) y
[registro de habilidades](HABILIDADES.md).

Google distingue dato ingresado, valor efectivo y valor mostrado en
[CellData](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/cells).
La documentación de [openpyxl](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html)
explica lectura y resultados guardados de fórmulas; se evaluará el lector cuando lleguen
los archivos originales. No se trasladan automáticamente resultados de Sheets a un
contrato Excel ni se fuerza el recálculo de fórmulas durante el análisis.

El enlace del chat histórico no pudo abrirse (timeout); se leyó completo el resumen
local `CONTEXTO_PROYECTO.md`, sin afirmar lectura íntegra del chat remoto. Los enlaces
oficiales de Mercado Libre sobre precios y stock distribuido devolvieron 403 en esta
consulta. Sus contratos siguen pendientes de verificar, junto con capacidades de las
cuentas. No se efectuaron conexiones ni cambios comerciales.
