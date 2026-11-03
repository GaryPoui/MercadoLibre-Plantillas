# Base inicial para especificar y planificar

Fecha: 2026-11-02. Versión: 0.1. Decisiones iniciales tomadas por delegación del usuario.

## Autorización y alcance

El usuario indicó usar los Excel ya compartidos, recibir después listas originales
de proveedores para mejorar el sistema, preparar los ejemplos y tomar decisiones sin
esperar nuevas respuestas. Pidió basar las reglas en las planillas y permitir cambiarlas.
Esto resuelve el bloqueo documental por falta de nuevos archivos: podemos planificar
una primera versión basada en referencias. No demuestra compatibilidad con proveedores
todavía no recibidos ni autoriza código de aplicación o escrituras en Mercado Libre.

La referencia de trabajo es la captura ya analizada, no una lectura actualizada del
documento remoto. Se conserva esa procedencia al usarla como base. Los archivos de
aceptación iniciales son casos de referencia, no listas de proveedores simuladas.

## Decisiones para la versión inicial

| Aspecto | Decisión inicial |
| --- | --- |
| Primer recorrido completo | Hoja AD: cabecera simple, identidad textual, importes y cálculos visibles |
| Otras estructuras | Perfiles separados por hoja/familia; no forzar ALBA, FIME o LAMY a las posiciones de AD |
| Salida | XLSX separado con la estructura de columnas, encabezados y bloques del perfil seleccionado; informe de revisión separado |
| Semejanza | Misma organización de datos y significado de campos; estilos equivalentes por tipo, sin exigir copia exacta de colores, logo o tamaños |
| Fórmulas | Conservar expresión y resultado disponible en la revisión; en la salida funcional, solo fórmulas compatibles con dependencias válidas dentro del libro generado |
| Fórmula inválida | Campo derivado pendiente/vacío y explicación en el informe; conservar expresión y resultado histórico en la revisión, sin presentar ese resultado como certificado |
| Columna VALOR | Valor base comercial del perfil; no recalcularlo automáticamente desde costo ni tratarlo como precio remoto confirmado |
| Columna de promoción | Campo calculado independiente según la regla observada; no habilita promociones ni publicación remota |
| Moneda | Conservar lo explícito; el símbolo $ o la región no resuelven una moneda desconocida |
| Identidad | Código de origen como texto y vínculo separado; no generar SKU comercial ni fusionar por descripción/código/precio |
| Errores parciales | Se permite descarga de revisión con todas las filas contabilizadas; errores y dependencias quedan pendientes, nunca como datos certificados |
| Lotes | Cada archivo conserva su revisión; una salida de lote identifica todos los orígenes y usa exactamente sus resultados revisados |
| Mercado Libre | Conversión autónoma sin escrituras. La cuenta y sus capacidades se resolverán en su funcionalidad |

La salida funcional no es una copia probatoria del original: el original y la revisión
retienen evidencia, mientras que la salida solo usa cálculos respaldados. Una dependencia
rota invalida también los resultados derivados de ella, aunque su valor guardado parezca
correcto. No activar ni ejecutar fórmulas externas, macros ni vínculos al preparar casos.

## Reglas comerciales editables

Se adopta la aritmética observada como **configuración de referencia**, no como tarifas,
obligaciones fiscales o rentabilidad vigentes. Los valores y fórmulas reales permanecen
en `data/private/`; no se fija un porcentaje universal en código o documentación pública.

Cada regla debe identificar origen, perfil, campo, expresión, parámetros y excepciones
de fila/presentación. Si dos filas usan variantes, conservarlas o señalar la diferencia;
no reemplazarlas por la fórmula más frecuente. Las celdas con importes manuales no se
reconstruyen como fórmulas por semejanza con las demás.

Parámetros modificables cuando aparezcan en el perfil: descuentos y su secuencia,
factores de costo, conversión de presentación, multiplicador de promoción, porcentaje
de comisión, cargos fijos y tramos, base de cálculo, envío, otros descuentos/cargos y
redondeo de presentación. No asignar nombre fiscal a un factor si no está respaldado.

La precisión interna conserva el dato disponible; no redondear todos los importes a
enteros porque la celda se muestre así. Se conserva el formato numérico observado por
campo como presentación; un cambio de redondeo de cálculo es una regla nueva explícita.

Cambiar una regla requiere ver las filas afectadas, crear una versión nueva y poder
volver a una previa. Los resultados anteriores mantienen su versión; para aplicar una
regla nueva a un archivo viejo se genera otra revisión. No hace falta solicitar una
decisión al usuario para redactar esta política: queda fijada como base delegada.

## Qué aprende el sistema

1. Conserva historial de cada carga, revisión, corrección y exportación.
2. Reutiliza mapeos estructurales compatibles dentro del mismo perfil/proveedor.
   El perfil inicial se prepara ahora por delegación; no se reinicia el cuestionario
   en cada carga compatible.
3. Una corrección de un valor afecta por defecto solo a esa revisión. No se transforma
   en fórmula general ni modifica otros proveedores.
4. Una acción explícita de guardar regla o modificar perfil crea una versión reutilizable
   con alcance visible. No se necesita aprobar cada celda de una lista reconocida.
5. Un cambio de estructura, unidad, presentación o significado invalida la reutilización
   automática afectada; la fila o campo queda pendiente, manteniendo lo demás revisable.

La delegación actual permite elegir esta política. No implica que una corrección futura
deba generalizarse automáticamente ni que el sistema entrene un modelo.

## Ejemplos preparados y comprobación

Se prepararon nueve casos a partir de celdas existentes, con dos filas de salida
detalladas del primer perfil. Las comprobaciones aritméticas independientes de tres
perfiles concuerdan con los resultados guardados dentro de la precisión del snapshot.
No se ejecutaron las expresiones Excel ni un conversor.

Datos y salidas esperadas: `data/private/base-inicial/casos-esperados-v0.json` y
`data/private/base-inicial/ENTRADA_SALIDA_V0.md`. Las huellas de las 17 capturas se
conservan en `data/private/base-inicial/FUENTES.json`.

Ver [índice anonimizado de casos](CASOS_REFERENCIA_V0.md). Esta comprobación valida
la coherencia de ejemplos seleccionados, no todas las fórmulas ni el libro completo.

## Preparación para Spec Kit

Quedan resueltos por decisión delegada la referencia inicial, el primer perfil, la
política de salida, el tratamiento de errores y el alcance del aprendizaje. Puede
continuarse al plan de la conversión versión inicial, con implementación aún pendiente.

Se difieren los formatos desconocidos de nuevos proveedores, cuentas/depósitos reales,
capacidades de Mercado Libre y exigencias de fidelidad exacta que todavía no se recibieron.
No bloquean el plan del conversor de referencia; no deben presentarse como resueltos.
Los límites operativos se propondrán y justificarán en el plan con las capturas disponibles,
sin atribuir al negocio volúmenes inventados.

Esta decisión posterior sustituye las condiciones anteriores que exigían nuevas listas
y una respuesta manual del usuario antes de planificar. Se aplica la prioridad de
instrucciones explícitas prevista en la gobernanza de la constitución; no se afirma
un contrato definitivo de proveedores ni preparación para uso productivo.

## Cobertura de aclaraciones

Cero preguntas adicionales: se integraron las cuatro instrucciones del usuario y se
tomaron las decisiones delegadas. El alcance, flujo, correcciones, salida y criterios
de aceptación quedan resueltos para el plan inicial, sin afirmar validación productiva.

| Categoría | Estado después de la aclaración |
| --- | --- |
| Alcance y comportamiento | Resuelto: conversión de referencia y revisión, sin escrituras |
| Dominio y datos | Resuelto para referencia; identidad remota, stock y nuevos formatos diferidos |
| Interacción | Resuelto: revisión, descarga de pendientes y reglas editables/versionadas |
| Calidad no funcional | Integridad y privacidad claras; límites, rendimiento y recuperación operativa al plan |
| Dependencias externas | Diferido: conversor autónomo; Mercado Libre fuera de esta entrega |
| Errores y excepciones | Resuelto: dependencia inválida no certifica derivados, vacíos y ceros separados |
| Restricciones y alternativas | Claro: sin código; fuentes reales; no copiar sistema de ejemplo |
| Terminología | Resuelto: perfil, corrección local, regla, revisión y salida separados |
| Señales de finalización | Resuelto: CAS-01 a CAS-09 y SC-001 a SC-010 |
| Supuestos pendientes | Diferidos expresamente los de nuevos proveedores y uso productivo |

La revisión del checklist pasó de 17/21 a 19/21 elementos: los dos cambios son elección
de plantilla/semejanza y alcance de reutilización. No hay regresiones documentales.
Los dos elementos todavía abiertos se reservan para el contrato final con originales.
