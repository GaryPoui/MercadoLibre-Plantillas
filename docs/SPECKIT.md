# Trabajar con Spec Kit

## Instalación del proyecto

Inicializado el 2026-10-14 con el repositorio oficial `github/spec-kit`, integración
`codex` y scripts PowerShell. Habilidades instaladas en `.agents/skills/`.
Versión declarada por la CLI: `1.2.1.dev0`; revisión fijada:
`51b6d170aa7368205bee629d75a7059185272d19`.
Es una revisión de desarrollo, no se presenta como una versión estable publicada.
La revisión fija permite reproducir esta preparación. Actualizarla deliberadamente,
revisando diferencias de scripts y habilidades antes de sustituirla.

La CLI se ejecuta con `scripts/specify.ps1`, usando uv/uvx disponible en este equipo.
No se instaló una CLI global ni dependencias de la aplicación.

```powershell
.\scripts\specify.ps1 --help
.\scripts\specify.ps1 version
```

La referencia de comandos está en la [documentación oficial](https://github.github.io/spec-kit/reference/core.html).

## Flujo con Codex

Las habilidades pueden requerir abrir un nuevo chat del proyecto para aparecer en
el catálogo de Codex. Los archivos ya están instalados y pueden leerse desde el proyecto.

1. `$speckit-constitution`: mantener principios. La versión inicial 1.0.0 ya está redactada.
2. `$speckit-specify`: crear o ajustar una funcionalidad. El primer borrador es importación Excel.
3. `$speckit-clarify`: resolver incertidumbres; próximo paso después de analizar los archivos.
4. `$speckit-plan`: decisiones técnicas, investigación, modelo y contratos.
5. `$speckit-tasks`: tareas ejecutables y sus dependencias.
6. `$speckit-analyze`: revisar consistencia de especificación, plan y tareas.
7. `$speckit-implement`: implementar y verificar los escenarios definidos.

Se puede pedir el trabajo en lenguaje natural; los nombres ayudan a indicar la fase.

## Estado actual

- Constitución: redactada, versión 1.0.0.
- Funcionalidad activa: `specs/001-importacion-excel`.
- Especificación: borrador ampliado el 2026-11-02 tras perfilar una referencia de 17 pestañas;
  aclarado para plan v0.1 por delegación del usuario, con casos de referencia y reglas
  modificables. La llegada de originales de proveedores deja de bloquear ese plan.
- Plan, investigación, modelo, contratos y18tareas: completados para el MVP local.
- Implementación: terminada y verificada2026-11-03; ver [validación](VALIDACION_MVP.md).
- Conexión real a Mercado Libre: no iniciada; funcionalidad posterior.

La referencia local `.specify/feature.json` faltaba al comenzar esta revisión y se
restableció mediante `Save-FeatureJson`, función oficial de los scripts existentes.
Se comprobó su resolución con `check-prerequisites.ps1 -Json -PathsOnly` y la plantilla
con `resolve-template.ps1`. No se modificaron scripts ni plantillas oficiales.
El archivo de referencia local sigue excluido de Git por la configuración de Spec Kit.

La carpeta de funcionalidad se guarda en `.specify/feature.json`. Esta versión no requiere
una rama con el mismo nombre. No se instaló la extensión Git: se utiliza Git normal y
ramas `codex/` cuando se necesiten. La entrega del MVP vive en `codex/mvp-excel`.

## Comprobaciones de preparación

```powershell
# Resolver la funcionalidad activa, sin exigir un plan que todavía no existe.
.\.specify\scripts\powershell\check-prerequisites.ps1 -Json -PathsOnly

# Resolver una plantilla a través del mecanismo oficial.
.\.specify\scripts\powershell\resolve-template.ps1 spec-template -Json

git diff --check
git check-ignore data/private/archivo.xlsx
```

No ejecutar de nuevo `init --force` como operación rutinaria: puede sobrescribir archivos
administrados. Mantener habilidades y plantillas oficiales versionadas; los documentos
del producto viven en `docs/`, `specs/` y `.specify/memory/`.
