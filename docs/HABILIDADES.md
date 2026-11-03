# Habilidades integradas en el proyecto

Instalación: 2026-11-02. Ubicación compartida y versionable: `.agents/skills/`.
No se instalaron frameworks ni dependencias de la aplicación. Las nuevas habilidades
podrán aparecer en el catálogo en el siguiente turno; sus archivos ya son legibles.

## Selección efectiva

| Habilidad | Función y activación | Procedencia |
| --- | --- | --- |
| `speckit-*` | Proceso principal de requisitos, aclaración, plan, tareas y consistencia | Ya instaladas; revisión documentada en [SPECKIT.md](SPECKIT.md) |
| `normalizar-excel-proveedor` | Listas y correcciones de este proyecto, con perfiles y plantillas trazables | Propia; [instrucciones](../.agents/skills/normalizar-excel-proveedor/SKILL.md) |
| `frontend-design` | Composición visual cuando se autorice construir o modificar la interfaz | [Anthropic](https://github.com/anthropics/skills/tree/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design) |
| `web-design-guidelines` | Revisar interfaz existente contra pautas actuales | [Vercel](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/web-design-guidelines) |
| `verification-before-completion` | Contrastar afirmaciones de finalización con evidencia proporcional al resultado | [Superpowers](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/verification-before-completion) |

Se usó el instalador oficial local `skill-installer` para descargar únicamente las
carpetas seleccionadas y fijar revisiones. Se inspeccionaron sus instrucciones antes
de instalarlas. La habilidad propia se redactó con `skill-creator`. No se ejecutaron
scripts de los repositorios descargados: las tres habilidades externas son documentos.

La verificación oficial `quick_validate.py` pasó para las cuatro habilidades nuevas.
Ese control comprueba estructura y metadatos; no demuestra la calidad de una interfaz
o una conversión aún no implementadas. El validador necesitó PyYAML 6.0.3, instalado
en una carpeta temporal aislada, sin modificar dependencias del producto.

## Integración y prioridades

El pedido del usuario y las instrucciones del proyecto prevalecen. Spec Kit mantiene
un único flujo. Las pautas de diseño no eligen stack, no autorizan código ni requieren
abrir Figma. Para este panel, legibilidad, revisión y corrección de datos determinan
la estética. La habilidad de verificación usa evidencia documental en esta etapa;
no corresponde ejecutar pruebas de una aplicación inexistente.

`web-design-guidelines` pide leer reglas remotas en cada revisión desde
[su fuente](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md).
Su instrucción es fija, pero las reglas pueden cambiar; registrar fecha y fuente
de cada auditoría futura. No enviar planillas privadas para cumplir esa lectura.

Los datos comerciales permanecen en `data/private/`. Instalar una habilidad no
autoriza enviar archivos a nuevos proveedores, conectar cuentas ni publicar cambios.

## Revisiones y huellas de entrada

| Archivo | Revisión upstream | SHA-256 local |
| --- | --- | --- |
| frontend-design/SKILL.md | `ca45fc496a3436251f191354091d557da31c15b5` | `D91970639E9F5C37682AC7AB60094D35F1C7C1F38D731BD56396563AEE10C1D3` |
| web-design-guidelines/SKILL.md | `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` | `F4647CA866A3ACCF763777F83E7682954F0187CD6BEA7EEA0399796652414E8F` |
| verification-before-completion/SKILL.md | `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b` | `2BEFE7FC55BCADAA3D97DD9E8EFEB633D2561C0EBE74C5A8B17C4D9E7E4520B3` |

Conservar versiones y revisar diferencias antes de actualizar. La habilidad propia
queda bajo el historial Git del proyecto; no se le atribuye revisión upstream.

Anthropic incluye LICENSE.txt (Apache-2.0), conservada íntegra. Se incorporó la licencia
MIT de la raíz de Superpowers a la carpeta de verificación, tomada de la misma revisión.
Vercel declara MIT en su README; no se encontró archivo de licencia en la carpeta
elegida ni en la raíz durante la revisión. Se conserva esa limitación sin inventar texto.

## Evaluadas y pospuestas

- React best practices: útil si el plan selecciona React; no instalada para anticipar el stack.
- Composition patterns: esperar componentes y una necesidad concreta.
- Systematic debugging: buena referencia de investigación de causas, pero su fase de
  implementación invoca test-driven-development y verification-before-completion.
  No instalarla aislada dejando esa dependencia incompleta ni agregar toda la suite
  para suplirla. Su recomendación en el informe de investigación es preliminar;
  este registro contiene la selección final.
- Brainstorming y writing-plans de Superpowers: solapan el proceso de Spec Kit.
- Skills especializadas de seguridad: evaluadas para futuras revisiones solicitadas;
  no instaladas ni ejecutadas ahora.

Ver comparaciones y fuentes en [sistemas](INVESTIGACION_SISTEMAS.md) y
[diseño](INVESTIGACION_DISENO_WEB.md). No existe una clasificación universal demostrada
de las «mejores» habilidades: esta selección responde al alcance y contexto actuales.
