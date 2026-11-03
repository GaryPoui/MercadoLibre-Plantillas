# Referente del usuario: AnalizadorPlanillas / PriceBot

Fecha de revisión: 2026-11-02, Argentina.
Repositorio aportado: [GaryPoui/AnalizadorPlanillas](https://github.com/GaryPoui/AnalizadorPlanillas).
Revisión inspeccionada: `6fd377c6e959feaa5c7e4c3c06354bd164ff6295`, commit del
2026-10-14. Se fijó esta revisión para que los enlaces permitan repetir la lectura.

## Propósito y método de esta revisión

El usuario lo aporta como ejemplo de funciones parecidas y aclara que el nuevo
desarrollo será diferente. Se estudian flujos, decisiones y límites; no se incorpora
su código ni se adoptan sus reglas comerciales o plantilla como contrato del proyecto.

Se revisaron README, roadmap, dependencias, backend principal y autenticación, y por
separado frontend y pruebas seleccionadas. Se consultaron mediante el conector GitHub
los metadatos, commit, árbol y archivos de texto. Las copias de apoyo leídas se
guardan en `data/private/referencias/analizador/`, excluidas de Git. No se descargaron
los datasets de precios, no se ejecutaron instaladores, servidor, pruebas o llamadas
a modelos, ni se revisaron los manuales binarios DOCX o todas las utilidades temporales.

Niveles de evidencia usados: **declarado** en documentación, **observado en código**
y **propuesta para nuestro proyecto**. Observado no equivale a probado en ejecución.
No se presenta esto como auditoría de seguridad ni revisión exhaustiva del repositorio.

## Flujo observado y alcance

El README presenta un convertidor de listas de proveedores a una plantilla de compras
de 12 columnas. Incluye entradas más amplias que nuestro alcance actual. La declaración
de formatos no implica que debamos aceptar PDF, imágenes o Word en nuestro MVP.
[Descripción y plantilla](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/README.md#L1-L96).

En el backend, `orchestrator` llama sucesivamente a extracción, transformación y
verificación y devuelve filas, informe, metadatos, mapeo, consumo y registro de pasos.
Esta separación es transferible como responsabilidad conceptual. Los nombres de
«agentes» representan funciones del servicio en el flujo inspeccionado; no demuestran
por sí mismos procesos autónomos o una arquitectura distribuida.
[Orquestación](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L3502-L3606).

Para planillas, extrae con pandas, recorre hojas y conserva filas estructuradas más
texto; para entradas sin mapeo suficiente dispone de un camino de interpretación
por texto/IA. La separación entre lectura estructurada y asistencia es aprovechable,
pero la IA no debe convertirse en autoridad comercial.
[Lectura](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L2157-L2236),
[selección del camino estructurado](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L2868-L2881).

## Patrones aprovechables y decisiones que requieren otro diseño

| Evidencia del referente | Qué aporta | Implicación propuesta para este proyecto |
| --- | --- | --- |
| Extracción → transformación → verificación → salida | Permite explicar dónde falla una carga | Definir resultados y errores de cada etapa sin fijar todavía clases o servicios |
| Camino estructurado antes de asistencia por IA | Evita interpretar como texto lo que ya tiene estructura | Evaluar lectura determinista por hoja/bloque y asistencia solo como propuesta revisable |
| Informe con filas enviadas a revisión y advertencias | Da información adicional al resultado final | Conservar todas las incidencias y procedencia, aun si la vista muestra solo una página |
| Historial opcional de resultados | Permite comparar extracciones | Versionar también perfil, reglas y plantilla; guardar resultados no equivale a aprender correcciones |
| Consumo y método de extracción en el resultado | Hace visible cuándo intervino un servicio externo | Si después se aprueba IA, definir límites, errores parciales y autorización de uso de datos |
| Plantilla fija de 12 columnas | Da una salida predecible para ese negocio | Nuestro contrato debe admitir los perfiles de salida que se confirmen con los Excel reales |

Las fuentes de cada fila se desarrollan abajo y en el
[análisis complementario de pruebas y UX](ANALIZADOR_PRUEBAS_UX.md).

### 1. Conservar estructura y procedencia antes de normalizar

La lectura `read_excel` usa los encabezados predeterminados y concatena registros de
todas las hojas en `structured_rows`. En esa representación no se añaden campos de
hoja/fila/celda a cada registro. El mapeador toma las claves de la primera fila para
seleccionar columnas del conjunto. Esto requiere un diseño diferente para nuestra
referencia, que mezcla hojas, cabeceras de varias filas, familias y auxiliares.
[Extracción y concatenación](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L2173-L2222),
[claves y mapeo](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L2751-L2825).

**Propuesta:** pedir como caso de aceptación hojas con estructuras distintas y
origen recuperable para cada valor. Mantener valor ingresado, fórmula, resultado
disponible y presentación cuando sean relevantes; no tomar una tabla aplanada como
equivalente al libro original. Ya se relaciona con FR-004, FR-016 y FR-021.

### 2. Mapeo sugerido no equivale a significado confirmado

`pick_column` busca patrones de texto y devuelve la primera coincidencia. Entre
los patrones para precio aparecen términos amplios; el camino estructurado se acepta
si identificó código **o** precio, no necesariamente ambos. Es una heurística del
ejemplo, no prueba de que haya seleccionado costo, precio final o moneda correctos.
[Mapeador](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L2751-L2783),
[condición de aceptación](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L2868-L2874).

**Propuesta:** mostrar alternativas cuando haya varios importes y preservar el mapeo
confirmado por proveedor y estructura. Añadir al corpus futuro una lista con costo,
precio de lista y precio de venta presentes a la vez. Relación: FR-001/013/019.

### 3. No trasladar predeterminados comerciales

Hay inferencia de moneda con retorno ARS por defecto, asignación ARS si falta la
columna y sustitución de monedas no reconocidas durante la verificación. Los precios
se redondean a dos decimales. La descarga incorpora un identificador de proveedor
predeterminado cuando no se informó uno. Se observan estas decisiones en código;
no se aprueban para el nuevo proyecto y no se reproducen sus valores de ejemplo.
[Inferencia](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L1184-L1190),
[mapeo](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L2806-L2820),
[validación y redondeo](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L3408-L3449),
[descarga](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L3674-L3683).

**Propuesta:** ausencia o moneda desconocida queda pendiente; escala y redondeo
dependen del contrato confirmado. Esta diferencia viene de la constitución actual,
no es una nueva regla comercial deducida del referente. Relación: FR-003/013.

### 4. Separar aceptación, exactitud y cobertura

El informe calcula `quality_score` como filas válidas sobre filas emitidas. Además
calcula `source_acceptance_score` sobre las filas que recibió el verificador: no sobre
todos los productos del original. Un porcentaje alto no acredita extracción completa,
identidad correcta, precio correcto ni equivalencia con una salida aprobada. El código
también limita los detalles incluidos en el informe a las primeras incidencias.
[Cálculo y detalle](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L3464-L3496).

**Propuesta:** distinguir filas leídas, clasificadas, propuestas, pendientes, rechazadas
y exportadas; medir exactitud de campos contra casos aprobados. No llamar «precisión»
a una puntuación interna de validación. Relación: SC-001/004/006 y FR-004/011.

### 5. No adoptar la deduplicación como identidad comercial

Una rutina agrupa por código y precio normalizados y conserva la fila con más datos.
Es una estrategia del extractor. En nuestro proyecto, dos filas pueden representar
presentaciones, variantes o destinos distintos; compartir código/precio no autoriza
fusionarlas. La clasificación requiere proveedor, unidad y contexto confirmado.
[Clave y deduplicación](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L1208-L1243).

**Propuesta:** contabilizar cada fila y explicar cada exclusión; conservar duplicados
pendientes de revisión según FR-005. No convertir esta clave en el identificador
central de catálogo ni de publicación.

### 6. Historial y caché son distintos de correcciones reutilizables

El historial se habilita por configuración y guarda una copia fechada de las filas,
informe, método y consumo. La caché inspeccionada es en memoria, está deshabilitada
por defecto y usa modelo/texto como base de su clave. Ninguna de estas piezas, por sí
sola, demuestra confirmación, alcance o retirada de una regla por proveedor.
[Historial](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L988-L1021),
[caché](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L1145-L1165),
[clave](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L2827-L2835),
[contenido guardado](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L3584-L3592).

**Propuesta:** especificar por separado repetición de carga, reutilización de perfil,
corrección local y regla confirmada. Relación: FR-012 y FR-017 a FR-020. No se concluye
ausencia de cualquier mecanismo posible fuera de los archivos inspeccionados.

### 7. Exportar lo revisado y no volver a interpretar silenciosamente

El endpoint de descarga vuelve a invocar `orchestrator` con el archivo y construye
una salida fija XLS/XLSX. El frontend y el tratamiento de lotes se analizan por
separado. Si una interpretación depende de IA, configuración o datos cambiantes,
reprocesar para descargar no garantiza obtener el mismo resultado revisado.
[Reprocesamiento y exportación](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L3657-L3735).

**Propuesta:** incluir un escenario donde la descarga corresponde exactamente a una
revisión y versiones identificadas. Una reconversión debe ser una nueva revisión
explícita. Es un insumo para aclarar FR-010/011/015/020 y SC-004/008, sin imponer ahora
identificadores de API, almacenamiento o librerías.

## Diferencias de alcance que deben mantenerse

Este referente convierte listas a una plantilla de compras. El nuevo proyecto además
contempla identidad por cuenta/publicación, inventario compartido, Full y sincronización
verificada. La revisión del árbol y las rutas principales no aporta evidencia de esos
contratos de Mercado Libre; no se deducen a partir de la existencia de autenticación,
lotes o archivos Excel. La autenticación local del ejemplo tampoco prueba aislamiento
de credenciales de varias cuentas vendedoras.
[Rutas principales](https://github.com/GaryPoui/AnalizadorPlanillas/blob/6fd377c6e959feaa5c7e4c3c06354bd164ff6295/pricebot/api/main.py#L3634-L3767),
[revisión complementaria](ANALIZADOR_PRUEBAS_UX.md).

## Uso en Spec Kit

Este informe aporta evidencia y contraejemplos; no es una especificación aprobada.
Usar la [matriz de insumos](../SISTEMAS_REFERENCIA.md) para decidir qué aclarar y qué
convertir después en escenarios de aceptación. Las tecnologías y las 12 columnas
del referente no sustituyen las decisiones pendientes del proyecto.
