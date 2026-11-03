# Investigación de habilidades y método de desarrollo

Fecha de consulta: 2 de noviembre de 2026 (Argentina).
Alcance: selección de habilidades, análisis de problemas y criterios de arquitectura.
Este informe no implementa una aplicación ni cierra el contrato del importador.

## Resultado propuesto

Mantener Spec Kit como proceso principal y sumar habilidades puntuales. No existe
evidencia comparativa que permita declarar una habilidad universalmente «la mejor».
La selección se basa en adecuación al proyecto, instrucciones inspeccionadas,
compatibilidad, dependencias y posibilidad de verificar resultados, no en estrellas.

Los documentos existentes confirman Excel, varias cuentas, stock propio y Full e
integración bidireccional. El stack sigue siendo una propuesta. La prioridad nueva
es convertir listas de proveedores a formatos de referencia y conservar correcciones
validadas como conocimiento reutilizable. Esta necesidad debe incorporarse a la
especificación por el responsable del replanteamiento.

## Método y fuentes de habilidades

Se leyeron el contexto, constitución, alcance y especificación del importador, así
como las habilidades locales de especificación, aclaración, planificación y análisis.
La consulta externa se restringió a repositorios de sus mantenedores, el estándar
Agent Skills y documentación original de patrones arquitectónicos.

El formato Agent Skills separa instrucciones, referencias y posibles ejecutables.
Por ello, instalar una carpeta no equivale a revisar sus scripts ni demuestra que
funcione en este entorno. Antes de instalar: inspeccionar contenido y licencia,
conservar procedencia y revisión, evitar sobrescribir habilidades existentes y no
ejecutar instaladores del proyecto remoto sin necesidad.
[Especificación oficial Agent Skills](https://agentskills.io/specification).

## Evaluación comparada

| Habilidad o conjunto | Utilidad concreta | Decisión propuesta |
| --- | --- | --- |
| Spec Kit local | Requisitos, aclaraciones, plan, tareas y consistencia | Conservar como flujo principal; ya disponible |
| `systematic-debugging` de Superpowers | Reproducir errores, rastrear datos y contrastar hipótesis antes de corregir | Incorporar de forma selectiva para etapas posteriores |
| `verification-before-completion` de Superpowers | Exigir evidencia antes de declarar trabajo terminado | Incorporar selectivamente si se acepta su alcance amplio |
| `brainstorming` y `writing-plans` de Superpowers | Alternativas y descomposición del trabajo | No instalar ahora: se superponen con Spec Kit y agregan dependencias |
| `security-best-practices` de OpenAI | Revisión de prácticas por lenguaje y framework | Opcional para futuras revisiones de seguridad explícitas |
| `security-threat-model` de OpenAI | Amenazas, límites de confianza y mitigaciones basadas en el repositorio | Opcional cuando se solicite modelado de amenazas |
| Frameworks completos y catálogos generales | Muchas especializaciones y automatismos | No instalar por volumen; seleccionar capacidades demostrables |

### Spec Kit: mantener una sola fuente de proceso

El repositorio de GitHub proporciona el marco de desarrollo guiado por
especificaciones. La instalación local ya tiene habilidades y scripts adaptados al
proyecto. Reinstalar el conjunto upstream podría perder estas adaptaciones. El
análisis cruzado corresponde a una etapa con especificación, plan y tareas; no debe
presentarse una revisión documental previa como si fuera ese control terminado.
[Repositorio oficial de Spec Kit](https://github.com/github/spec-kit).

### Investigación de causa y verificación

`systematic-debugging` ordena reproducir el problema, reunir evidencias, contrastar
patrones, formular hipótesis y verificar la corrección. Resulta útil para diferencias
de precios o stock, errores de interpretación y reintentos. Sus ejemplos de consola
son ilustrativos: no deben copiarse comandos que impriman variables sensibles.
Debe conservarse la carpeta completa porque referencia materiales auxiliares.
[Instrucciones del mantenedor](https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md).

`verification-before-completion` vincula cada afirmación de éxito con una comprobación
reciente e incluye revisar resultados de agentes. Puede reforzar la verificación de
exportaciones e instalaciones. Su alcance es amplio: no exige inventar una batería
de pruebas para documentación ni demuestra por sí sola que un cambio remoto se haya
aplicado. La evidencia debe corresponder al resultado afirmado.
[Instrucciones del mantenedor](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md).

### Evitar dos metodologías simultáneas

La versión consultada de `brainstorming` solicita explorar el contexto, discutir
alternativas y aprobar diseño antes de implementar; después deriva a `writing-plans`.
Es útil como referencia conceptual, pero introduciría otra secuencia encima de
especificar y aclarar. No se aplica en esta investigación como habilidad activa.
[Fuente inspeccionada](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md).

`writing-plans` define tareas comprobables, estructura y dependencias hacia otras
habilidades de Superpowers. El proyecto ya exige plan y tareas en su directorio de
especificación. Instalarla aisladamente sin resolver dependencias no garantiza un
proceso coherente. Se retiene el criterio de tareas con resultado verificable dentro
del proceso existente.
[Fuente inspeccionada](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

### Seguridad especializada, cuando corresponda

`security-best-practices` contiene orientación para Python, JavaScript/TypeScript y
Go, con referencias por tecnología. Es compatible con parte del stack propuesto,
pero su descripción limita el uso a solicitudes explícitas de seguridad; no debe
activarse para cualquier tarea de arquitectura ni declarar vulnerabilidades en una
aplicación inexistente.
[Fuente oficial](https://github.com/openai/skills/blob/main/skills/.curated/security-best-practices/SKILL.md).

`security-threat-model` requiere anclar amenazas a evidencias y validar supuestos
con el usuario. También tiene un activador explícito y un paso de aclaraciones.
Puede servir después para archivos de entrada, credenciales OAuth y aislamiento de
cuentas, pero no debe generar ahora un informe que afirme controles implementados.
[Fuente oficial](https://github.com/openai/skills/blob/main/skills/.curated/security-threat-model/SKILL.md).

## Criterios para el replanteamiento

Estas son recomendaciones de esta investigación, no decisiones técnicas cerradas:

1. Describir usuarios, entradas, salidas, reglas y excepciones antes de elegir el
   stack. Separar conversión de planillas de sincronización con Mercado Libre.
2. Conservar originales, mapeos, versiones de formato y correcciones aprobadas.
   La retroalimentación debe producir reglas trazables y reversibles. Una corrección
   de un proveedor no debe propagarse automáticamente a otro ni alterar cargas viejas.
3. Distinguir dato observado, significado confirmado y sugerencia. Un encabezado
   parecido no demuestra equivalencia comercial. Conservar ceros iniciales, vacíos
   y fórmulas sin inventar resultados ni evaluar contenido activo.
4. Diseñar módulos con límites claros: recepción y perfilado, mapeo, normalización,
   revisión, exportación, catálogo, inventario e integración. El monolito modular
   sigue siendo una opción a comparar, no una aprobación implícita.
5. Definir pruebas por riesgo: pérdida de identidad, alteración del original, fórmula
   interpretada como valor, confusión entre vacíos y cero, mezcla de cuentas,
   doble descuento y exportación incompatible con la plantilla.

### Representar arquitectura y decisiones

Para comunicar el sistema, empezar por contexto y componentes principales, ampliando
solo donde ayude a entender una decisión. C4 ofrece niveles de abstracción sin
imponer herramienta ni notación. Aplicación propuesta: mostrar proveedor, operador,
planillas, sistema central y Mercado Libre antes de diagramar infraestructura.
[Sitio del autor de C4](https://c4model.com/).

Registrar decisiones significativas de forma breve: contexto, alternativas,
decisión, estado y consecuencias. Mantener el historial cuando una decisión cambie,
en vez de reescribir el pasado. Aplicación propuesta: distinguir «evaluado»,
«propuesto» y «aceptado» en los futuros documentos técnicos.
[Michael Nygard: Architecture Decision Records](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

### Consistencia y operaciones externas

Evaluar outbox transaccional si actualizar estado central y encolar trabajo constituye
una escritura dual. El patrón no elimina duplicados; los consumidores deben manejar
repeticiones y el orden exige tratamiento explícito. Aplicación propuesta: conservar
intención e intentos de sincronización y verificar el resultado remoto antes de
marcar éxito. La fuente es un patrón general; no prueba las capacidades de Mercado
Libre ni obliga a contratar servicios de AWS.
[AWS: transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html).

## Instalación y límites de esta entrega

Este informe no instala habilidades. Para una instalación selectiva, las rutas
concretas comprobadas son:

- Repositorio `obra/superpowers`, `skills/systematic-debugging`.
- Repositorio `obra/superpowers`, `skills/verification-before-completion`.
- Opcional: repositorio `openai/skills`, `skills/.curated/security-best-practices`.
- Opcional: repositorio `openai/skills`, `skills/.curated/security-threat-model`.

El responsable de la instalación debe fijar revisión, registrar hashes y comprobar
referencias locales. No se ha ejecutado ningún script remoto ni validado un sistema
con estas habilidades. Las fuentes externas cambian; registrar fecha y revisión de
lo instalado evita confundir esta evaluación con versiones posteriores.
