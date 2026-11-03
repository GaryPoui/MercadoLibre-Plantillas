# Sistemas de referencia e insumos para futuros specs

Investigación: 2 de noviembre de 2026 (Argentina).
Estado: preparación documental; no selección de producto ni aprobación de alcance.

## Resultado de la investigación

Se estudió el repositorio del usuario como ejemplo funcional y se contrastó con seis
sistemas documentados por sus responsables. Ninguno se adopta como arquitectura,
plantilla universal o contrato comercial. La finalidad es plantear mejores preguntas,
reconocer riesgos y preparar escenarios de aceptación para los specs posteriores.

La distinción principal es entre **datos originales**, **revisión de una carga**,
**perfil reutilizable** y **plantilla de salida**. Un historial de archivos o una
memoria de columnas no equivale a reglas comerciales confirmadas con versiones.
Esta es una síntesis de diseño de la investigación, no una capacidad probada del sistema.

## Documentos y referentes

| Referente | Para qué se estudió | Documento de evidencia |
| --- | --- | --- |
| AnalizadorPlanillas / PriceBot, aportado por el usuario | Conversión de listas, extracción, mapeo, informes y exportación | [Análisis del backend y flujo](referencias/ANALIZADOR_PLANILLAS.md) y [pruebas e interfaz](referencias/ANALIZADOR_PRUEBAS_UX.md) |
| OpenRefine | Limpieza visible, facetas, historial y operaciones reutilizables | [Comparativa de importadores](referencias/COMPARATIVA_IMPORTADORES.md#openrefine-limpieza-explícita-y-operaciones-reproducibles) |
| Flatfile | Extracción, mapeo, validación y preparación antes del destino | [Comparativa de importadores](referencias/COMPARATIVA_IMPORTADORES.md#flatfile-separar-extracción-mapeo-y-revisión) |
| Dromo | Revisión embebida, memoria de mapeos, errores y sesiones | [Comparativa de importadores](referencias/COMPARATIVA_IMPORTADORES.md#dromo-importador-embebido-con-memoria-configurable) |
| Akeneo PIM | Perfiles de importación/exportación y calidad de catálogo | [Catálogo y operación](referencias/COMPARATIVA_CATALOGO_OPERACION.md#1-akeneo-pim-perfiles-y-calidad-del-catálogo) |
| Odoo | Identidad estable, relaciones y comprobación previa a importar | [Catálogo y operación](referencias/COMPARATIVA_CATALOGO_OPERACION.md#2-odoo-comprobar-identificar-y-reimportar) |
| Real Trends | Intercambio Excel y contexto de cuenta de Mercado Libre | [Catálogo y operación](referencias/COMPARATIVA_CATALOGO_OPERACION.md#3-real-trends-excel-y-contexto-de-cuenta) |

Las fichas contienen fuentes primarias junto a las afirmaciones. El repositorio del
usuario se fijó en `6fd377c6e959feaa5c7e4c3c06354bd164ff6295`; sus enlaces señalan
archivos y líneas de esa revisión. Las páginas de productos son documentación viva:
la fecha de consulta no garantiza que describan el mismo comportamiento en otra fecha,
edición, región o cuenta.

## Cómo se obtuvo la evidencia

- Repositorio: lectura estática de documentación, árbol, backend, frontend y pruebas
  seleccionadas mediante GitHub. No se ejecutó código ni se declararon tests aprobados.
- Otros sistemas: lectura de manuales y documentación oficial. No se abrieron cuentas,
  contrataron servicios ni subieron datos de proveedores.
- Proyecto propio: contraste con constitución, alcance, referencia Excel y borrador
  activo. Las observaciones se relacionan abajo con requisitos existentes.

Las conclusiones de una lectura estática tienen límites: un camino observado permite
explicar una decisión, pero no establece rendimiento real ni demuestra todos los casos.
Una función descrita por un fabricante no se presenta como probada. No encontrar
evidencia de una capacidad en estas fuentes no demuestra que el producto carezca de ella.

## Lecciones prioritarias

**Revisar y descargar deben referirse al mismo resultado.** En PriceBot se observan
reprocesamiento al descargar y alcance distinto entre filas combinadas e informe.
La propuesta es que una revisión identifique el conjunto de archivos y las versiones
utilizadas y que su exportación no vuelva a interpretar silenciosamente los originales.
Ver [flujo y descarga](referencias/ANALIZADOR_PLANILLAS.md#7-exportar-lo-revisado-y-no-volver-a-interpretar-silenciosamente)
y [comportamiento de la interfaz](referencias/ANALIZADOR_PRUEBAS_UX.md#exportación-y-consistencia-con-lo-revisado).

**La calidad necesita varias medidas.** No confundir formato válido con exactitud
respecto del original o cobertura de productos. Un porcentaje interno no acredita
precio ni SKU correctos. Las filas excluidas y pendientes deben poder conciliarse;
mostrar una muestra de errores no debe hacer inaccesibles los restantes.
Ver [métricas del referente](referencias/ANALIZADOR_PLANILLAS.md#4-separar-aceptación-exactitud-y-cobertura).

**Las correcciones necesitan alcance.** OpenRefine distingue operaciones reutilizables
de edición individual; Flatfile y Dromo documentan memorias y sesiones con alcances
propios. La propuesta es separar corrección puntual, correspondencia de columnas y
regla comercial, y confirmar proveedor, estructura y versión antes de reutilizar.
Ver [comparativa de importadores](referencias/COMPARATIVA_IMPORTADORES.md).

**Aceptar XLSX no demuestra fidelidad al Excel.** Importar valores y exportarlos a
XLSX no garantiza conservar fórmulas, formatos, auxiliares o encabezados multinivel.
El contrato deberá distinguir exactitud de datos, estructura de salida y presentación.
Ningún referente estudiado prueba por sí solo compatibilidad con las 17 hojas recibidas.
Ver [referencia real](REFERENCIA_EXCEL.md) y [comparativa](referencias/COMPARATIVA_IMPORTADORES.md).

**Catálogo y cuentas son problemas diferentes.** Las convenciones de identidad de un
PIM o ERP no determinan el SKU del proveedor ni el vínculo a publicaciones. Poder
cambiar de cuenta de Mercado Libre tampoco prueba un inventario compartido correcto,
reservas, tratamiento de Full o sincronización verificada.
Ver [catálogo y operación](referencias/COMPARATIVA_CATALOGO_OPERACION.md).

## Matriz de insumos para Spec Kit

Todas las filas siguientes son **candidatas para aclaración y diseño**. Los FR/SC
indicados ya existen en el borrador; la relación no declara que estén implementados
ni incorpora silenciosamente nuevas condiciones. Los escenarios se convertirán en
aceptación formal solo después de contrastarlos con datos y decisiones del usuario.

| ID | Lección y referente | Requisito relacionado | Caso candidato para especificar | Decisión pendiente |
| --- | --- | --- | --- | --- |
| REF-01 | Evitar aplanar hojas heterogéneas; PriceBot y Flatfile | FR-001/004/016/021 | Libro con dos hojas de cabeceras diferentes y títulos intercalados; cada valor mantiene origen | Selección de hojas/bloques y qué se exporta |
| REF-02 | Heurística de nombre no confirma significado; PriceBot/Odoo | FR-001/013 | Costo, precio de lista y precio final presentes juntos; mostrar alternativas sin elegir por posición | Semántica y prioridad de cada importe |
| REF-03 | Predeterminado comercial no es dato recibido; PriceBot | FR-003/013 | Moneda ausente/desconocida, cero explícito e importe textual ambiguo quedan diferenciados | Monedas, unidades, escala y redondeo |
| REF-04 | Duplicado técnico no implica identidad; PriceBot/Odoo/Akeneo | FR-002/005 | Mismo código/precio con distinta presentación o publicación; ninguna fusión silenciosa | Claves y relación proveedor/producto/destino |
| REF-05 | Puntuación interna no equivale a exactitud; PriceBot | SC-001/004/006 | Filas válidas en formato con SKU o precio equivocado fallan al comparar con salida aprobada | Corpus de referencia y medidas de aceptación |
| REF-06 | Filtro/exclusión cambia alcance; OpenRefine/Dromo/Akeneo | FR-004/011/016 | Se excluyen filas o columnas: el informe indica cuántas, cuáles y por qué | Bloquear salida o permitir parcial; campos críticos |
| REF-07 | Descarga debe corresponder a revisión; PriceBot | FR-010/011/015/020, SC-004/008 | Dos archivos procesados, uno corregido; descarga corresponde al conjunto revisado sin reprocesar | Unidad de revisión y de exportación |
| REF-08 | Corrección local frente a regla; OpenRefine | FR-017/018/020 | Editar una celda no cambia la próxima lista; confirmar regla sí permite proponer reutilización | Quién confirma y con qué alcance |
| REF-09 | Memoria de columnas no es historial comercial; Flatfile/Dromo | FR-018/019/020, SC-007/008 | Mismas cabeceras pero distinta unidad o proveedor: no aplicar regla anterior como válida | Criterio de compatibilidad y revisión |
| REF-10 | Formato admitido no implica fidelidad; OpenRefine/Flatfile/Dromo | FR-013/014/021, SC-006 | Fórmula rota con resultado cero y auxiliar de envío; no copiarlas como regla aprobada | Valores, fórmulas, estilos y auxiliares exigidos |
| REF-11 | Cuenta activa visible; Real Trends | FR-006/007/008/009, SC-003 | Mismo producto en dos cuentas; solo se comparan destinos elegidos y Full se distingue | Capacidades verificadas y autoridad de cada campo |
| REF-12 | Probar antes de aplicar; Odoo, flujo de importadores | FR-009/012/015, SC-005 | Cargar, revisar y exportar sin escrituras externas, incluso al repetir o fallar un archivo | Posterior política de aplicación/automatización |

Las preguntas nuevas de mayor valor son: qué constituye una revisión cuando hay
varios archivos; qué nivel de salida parcial se permite; qué debe significar una
medida de calidad; y qué invalida un perfil aunque sus encabezados no cambien.
Se suman a las decisiones comerciales ya pendientes, sin pedir resolverlas en esta etapa.

## Qué no se adopta por estudiar estos sistemas

No se fijan las 12 columnas de PriceBot, monedas por defecto, reglas numéricas,
deduplicación por código/precio, servicios de IA, stack, despliegue o arquitectura
multiagente. Tampoco se incorporan PDF/OCR, imágenes, ERP completo, mensajes de
Mercado Libre ni módulos nuevos por aparecer en los referentes.

No se recomienda contratar una plataforma. Si después se evalúa un componente,
primero debe cumplir los casos aprobados con muestras anonimizadas y condiciones
de uso de datos conocidas. La documentación comercial no reemplaza comprobar
capacidades de las cuentas reales ni los contratos oficiales de Mercado Libre.

## Aplicación al flujo del proyecto

1. **Antes de aclarar:** leer esta síntesis, la ficha del referente pertinente y el
   análisis Excel real. Elegir qué decisiones requieren respuesta del negocio.
2. **Al especificar:** incorporar únicamente comportamientos confirmados y casos
   representativos. Conservar como propuesta lo que proviene de otros productos.
3. **Al planificar:** comparar opciones técnicas con estos casos y registrar decisión,
   alternativas y límites; no copiar el stack del ejemplo por familiaridad.
4. **Al generar tareas y analizar:** relacionar tareas con FR/SC y con los riesgos
   aceptados. No presentar esta investigación como `speckit-analyze`, que requiere
   plan y tareas finales aún inexistentes.
5. **Al verificar posteriormente:** contrastar original → revisión → exportación;
   separar pruebas de conversión de pruebas de integración externa.

La investigación no cierra por sí sola el contrato ni habilita implementación. Por
delegación posterior, la [base inicial](BASE_INICIAL_V0.md) y los casos preparados
permiten ahora el plan v0.1; no demuestran compatibilidad con proveedores no recibidos.
