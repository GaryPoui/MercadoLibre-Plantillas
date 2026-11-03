---
name: normalizar-excel-proveedor
description: Analizar listas de proveedores de este proyecto y proponer su conversión a las plantillas de referencia, conservando perfiles y correcciones confirmadas. Usar al recibir un Excel, una referencia de Google Sheets o una corrección de su mapeo; no autoriza sincronizar Mercado Libre.
---

# Conversión de listas de proveedores

Leer `CONTEXTO_PROYECTO.md`, `docs/ANALISIS_EXCEL.md`,
`docs/REPLANTEAMIENTO_BASE.md` y la especificación resuelta por `.specify/feature.json`.
Leer también `docs/BASE_INICIAL_V0.md`: el usuario delegó preparar y planificar la
versión inicial con sus referencias existentes, sin esperar nuevas listas o respuestas.
Consultar `docs/REFERENCIA_EXCEL.md` para los hallazgos de referencia. Los valores,
coordenadas y fórmulas comerciales están en `data/private/ANALISIS_MISTICA.md` y los
snapshots privados, si están disponibles. No tratar esos snapshots como el libro vigente.

## Al recibir una lista

- Usar las herramientas de hojas disponibles: Google Drive/Sheets para un enlace
  conectado, o la habilidad Spreadsheets para archivos locales. La referencia es de
  lectura salvo pedido explícito de edición. Mantener intacto el original.
- Registrar procedencia, fecha, tamaño cuando se exponga y huella del archivo local.
  Una lectura API es un snapshot, no un original `.xlsx`; no inventar una huella remota.
- Inventariar hojas, encabezados, bloques, auxiliares y fórmulas. Comparar valor
  original, calculado/guardado y mostrado; no ejecutar macros ni vínculos externos.
- Buscar un perfil confirmado compatible. No usar solo nombre de archivo o posición
  de columnas; si cambia estructura o significado, señalar la revisión necesaria.
- Separar producto, proveedor, presentación/unidad y destinos de publicación. Mantener
  ceros iniciales y códigos alfanuméricos; una descripción similar no prueba identidad.
- Identificar la plantilla de salida y su versión. «Similar al ejemplo» no aprueba
  fórmulas, comisiones, impuestos ni la propagación de errores observados.
- Presentar mapeo, evidencia, filas pendientes y diferencias. Si falta una decisión
  comercial que impide convertir correctamente, explicar el punto y pedir solo ese dato.
- Cuando se autorice convertir, producir una salida separada y verificarla contra el
  contrato confirmado: estructura, códigos, conteos y valores/reglas representativos.
  La falta de datos no se resuelve con ceros ni cifras inventadas.

## Al recibir una corrección

Determinar si corrige una fila, un perfil reutilizable o una plantilla. Si el alcance
no es deducible, conservarla solo en la carga y dejar propuesta la generalización.
Registrar antes/después, fuente, alcance, autor, fecha y versión; no extender la regla
a otros proveedores ni reescribir conversiones anteriores. Una regla retirada debe
dejar historial y permitir una nueva conversión con una versión previa.

## Memoria y entrega

Documentar evidencias reales en `data/private/`; versionar únicamente requisitos,
reglas confirmadas sin información privada y muestras anonimizadas con procedencia.
Mantener pendientes en la especificación activa y sincronizar su checklist usando
Spec Kit. La versión inicial cuenta con casos entrada/salida documentales derivados
de la referencia por delegación; no bloquear su plan esperando otros archivos. No
presentarlos como originales de proveedores ni como contrato definitivo para formatos
no recibidos. Ampliar los perfiles cuando lleguen nuevas evidencias.

Explicar en español qué se observó, qué se confirmó, qué se propone y qué falta.
No prometer aprendizaje de modelos: la retroalimentación acordada se materializa en
perfiles y correcciones trazables. Exportar no equivale a publicar en Mercado Libre.
