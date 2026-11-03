# Investigación de habilidades y diseño del panel operativo

Fecha de consulta: 2 de noviembre de 2026 (Argentina). Alcance: investigación y propuesta; no se implementó una interfaz ni se instaló software desde este informe. La instalación efectiva se registra por separado.

## Criterio de selección

Se priorizaron repositorios del autor original, instrucciones legibles, propósito acotado, licencia identificable y correspondencia con el trabajo real: interpretar archivos, revisar diferencias, resolver errores y conservar decisiones. Popularidad y cantidad de descargas no prueban calidad para este proyecto. No existe evidencia aquí de una habilidad universalmente superior.

Se leyeron el contexto, la constitución, el alcance y la especificación del importador. Las recomendaciones siguientes son decisiones de diseño propuestas; no fijan encabezados Excel, reglas comerciales ni tecnologías de la aplicación.

## Habilidades evaluadas

| Habilidad y fuente primaria | Aporte y límite | Recomendación |
| --- | --- | --- |
| [frontend-design, Anthropic](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | Orienta identidad visual, tipografía, composición y revisión contra el encargo. Su énfasis estético requiere interpretar el contexto: un panel de operaciones necesita legibilidad y previsibilidad. No resuelve contratos de datos ni certifica accesibilidad. | Incorporar como apoyo de diseño, subordinada a los flujos y datos reales. |
| [web-design-guidelines, Vercel](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) | Revisa interfaces existentes y pide consultar sus reglas actualizadas. Devuelve hallazgos por archivo y línea. No constituye un proceso de descubrimiento de negocio. | Incorporar para revisiones futuras; hoy no hay interfaz que auditar. |
| [react-best-practices, Vercel](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) | Guía de rendimiento para React y Next.js: solicitudes independientes, carga, renderizado y tamaño del paquete. Incluye recomendaciones dependientes de servidor/framework. | Preparar su uso condicional si el plan elige React. No adoptar Next.js ni servicios de Vercel por instalarla. |
| [composition-patterns, Vercel](https://github.com/vercel-labs/agent-skills/tree/main/skills/composition-patterns) | Apoya APIs de componentes reutilizables y separación del estado; contiene indicaciones particulares de React 19. | Posponer hasta que exista una necesidad concreta de componentes compartidos. |

Lecturas directas: [frontend-design/SKILL.md](https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md), [web-design-guidelines/SKILL.md](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/web-design-guidelines/SKILL.md), [react-best-practices/SKILL.md](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/react-best-practices/SKILL.md) y [composition-patterns/SKILL.md](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/composition-patterns/SKILL.md).

Identidades upstream observadas mediante GitHub API: `anthropics/skills` en `ca45fc496a3436251f191354091d557da31c15b5`; `vercel-labs/agent-skills` en `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62`. Son referencias de esta investigación, no evidencia de instalación. Conservar la referencia y licencia al incorporar cada carpeta. Anthropic incluye [LICENSE.txt Apache-2.0](https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/LICENSE.txt); Vercel declara MIT en su [README](https://github.com/vercel-labs/agent-skills#license). No se encontró un archivo `LICENSE` en la raíz de Vercel ni `LICENSE.txt` dentro de web-design-guidelines durante esta revisión; no inventar uno ni atribuirle un texto no presente.

## Integración proporcional

Spec Kit conserva la responsabilidad de especificar escenarios y aceptación. El diseño se alimentará de esa especificación y de ejemplos anonimizados. frontend-design ayuda a componer las pantallas; web-design-guidelines revisa su calidad; las reglas React solo aplican si coinciden con la tecnología elegida.

La habilidad de Vercel incorpora una dependencia documental externa: [Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md). Sus reglas abarcan semántica, foco, formularios, estados, localización y rendimiento. Conviene registrar la fecha de la consulta y tratar sus indicaciones como recomendaciones revisables. Por ejemplo, un umbral genérico para virtualizar listas no sustituye medir el volumen real ni comprobar navegación asistida.

No se recomienda instalar ahora habilidades de despliegue, transiciones decorativas o aplicaciones móviles: no responden al alcance autorizado. Las habilidades Figma disponibles se reservan para una solicitud concreta de diseño en Figma. La documentación de [React Aria](https://react-aria.adobe.com/quality) es una alternativa de referencia para interacciones accesibles si se elige React, no una dependencia aprobada. Describe soporte de teclado, foco, lectores de pantalla e internacionalización; aun utilizando componentes de ese tipo deben verificarse etiquetas, contraste e integración real.

## Propuesta de experiencia operativa

Esta sección es una síntesis propia para el proyecto, pendiente de contrastar con los ejemplos y el operador.

1. **Cargar y reconocer.** Mostrar archivo y hojas detectadas; distinguir original, interpretación y salida propuesta. Informar los formatos admitidos cuando se confirmen con evidencia. Subir un archivo no equivale a publicar cambios.
2. **Relacionar columnas.** Presentar columna de origen, ejemplos seguros, destino sugerido y motivo de la sugerencia. Permitir dejar una columna sin usar. Una coincidencia dudosa queda pendiente. La pantalla no debe convertir una inferencia en significado comercial confirmado.
3. **Revisar calidad.** Resumen de filas utilizables, pendientes y rechazadas, con filtros y acceso a la ubicación de origen. Cada error debe decir qué ocurrió y cómo resolverlo. Distinguir ausencia, cero y dato inválido; conservar códigos como texto cuando corresponda.
4. **Comparar la conversión.** Enseñar origen y resultado propuesto con el perfil y versión utilizados. La similitud con los ejemplos exige definir si incluye estructura, presentación, fórmulas o todas ellas; no prometer equivalencia antes de inspeccionar el libro completo.
5. **Corregir y conservar.** Separar la corrección de una fila de una regla reutilizable del proveedor. Antes de guardar una regla, mostrar a qué archivos y campos se aplicará. Registrar origen, cambio, autor, alcance y versión; permitir desactivarla y revisar conversiones afectadas.
6. **Exportar y consultar historial.** Identificar plantilla de salida y versión, conservar el original y ofrecer el informe de incidencias. La descarga confirma generación del archivo; la sincronización con Mercado Libre tendrá estados propios cuando se implemente.

Una interfaz posterior de sincronización deberá mantener la cuenta y logística visibles, separar stock propio de Full y mostrar valor previo, propuesto, enviado y verificado. Los estados concretos se definirán en su especificación; no confundir propuesta, envío aceptado y resultado remoto confirmado.

## Accesibilidad y verificación futura

Se propone WCAG 2.2 nivel AA como objetivo de diseño, pendiente de incorporarlo formalmente a la especificación. [WCAG 2.2](https://www.w3.org/TR/WCAG22/) incluye criterios verificables sobre teclado, contraste, foco, mensajes y prevención de errores. No se declara conformidad de un sistema todavía inexistente.

Para comparar datos, emplear tablas con títulos y asociaciones de encabezados: [WAI Tables Tutorial](https://www.w3.org/WAI/tutorials/tables/). Si se requiere edición tipo planilla, el patrón [APG Grid](https://www.w3.org/WAI/ARIA/apg/patterns/grid/) exige administrar el foco y la navegación entre celdas; una tabla con controles simples puede ser una primera opción menos compleja. Validar con teclado y lector de pantalla, particularmente si hay paginación o virtualización.

Los [tutoriales de notificaciones](https://www.w3.org/WAI/tutorials/forms/notifications/) recomiendan informar el resultado general y el detalle junto al control, con mensajes claros y acciones de corrección. Aplicación propuesta: resumen de errores enlazado a su fila, progreso anunciado sin interrupciones constantes y conservación del trabajo al fallar una validación. La [validación accesible](https://www.w3.org/WAI/tutorials/forms/validation/) complementa la validación del servidor; la comprobación visual del navegador no asegura integridad de los datos.

Revisar pantallas vacías, carga, archivo no interpretable, permiso insuficiente, perfil desactualizado, conflictos y resultados parciales. Verificar foco visible, zoom, contraste y significado textual de los estados, sin depender exclusivamente del color. La estética se evalúa junto con completar la tarea sin errores; una captura atractiva no basta.

## Evidencia pendiente

Después de esta investigación se perfiló el contenido celular completo de las 17 hojas;
ver [hallazgos](REFERENCIA_EXCEL.md). Faltan propiedades estructurales no expuestas en
esas lecturas, significado comercial confirmado, entradas originales de proveedores,
operaciones más frecuentes, volumen y expectativas de salida. No se fijan paleta,
fuentes, biblioteca de componentes, tamaño de página ni reglas de transformación sin
estos insumos. El próximo resultado de diseño deberá ser un flujo revisable con
contenido representativo y anonimizado, antes de escribir la interfaz. La selección
final instalada se registra en [HABILIDADES.md](HABILIDADES.md).
