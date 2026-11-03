# MercadoLibre-Plantillas

Integrador de listas Excel, precios, inventario mixto y varias cuentas de Mercado Libre,
con sincronización bidireccional como objetivo general. Primer MVP local desarrollado con Spec Kit.

## Estado

MVP Excel local implementado y verificado el 2026-11-03: carga XLSX/CSV, selección de
hojas y columnas, revisión y corrección, perfiles y cálculos versionados, historial,
exportación reproducible y comparación por cuenta contra un catálogo controlado.
No hay conexión ni escrituras reales en Mercado Libre. No es un despliegue público.

## Iniciar en Windows

Requiere Python 3.12. Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.\scripts\start.ps1
```

Abrir [la aplicación local](http://127.0.0.1:8765) y crear una contraseña de al menos
12 caracteres en el primer acceso. No existe una contraseña compartida o publicada.
Si el puerto está ocupado: `./scripts/start.ps1 -Port 8780`.
En Linux: `.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765`.

Los datos se guardan fuera del repositorio y OneDrive, en
`%LOCALAPPDATA%\MercadoLibrePlantillas`; `MLPL_DATA_DIR` permite elegir otra carpeta local.
Para respaldar, detener el servidor y copiar esa carpeta completa a un destino privado.
La sesión, los originales y las revisiones nunca se guardan en Git.

## Primer recorrido

1. Descargar la muestra sintética o cargar un XLSX/CSV propio.
2. Elegir hoja, filas de encabezado e inicio; asignar código, descripción y valor base.
3. Crear revisión; consultar errores, origen y valores. Corregir una fila crea otra revisión.
4. Guardar un perfil para futuras listas compatibles; cambiar reglas crea una versión.
5. Descargar la revisión XLSX: hojas Datos e Informe, valores calculados y pendientes
   explícitos, sin volver a procesar el original. Consultar versiones anteriores en Historial.

Las hojas de tareas o métricas se pueden clasificar como operativas. La comparación
usa exclusivamente el catálogo controlado guardado en este equipo y nunca publica.
Formatos iniciales: XLSX y CSV UTF-8; no XLS, XLSM, PDF ni macros. Las fórmulas fuera
del conjunto admitido y las dependencias inválidas quedan pendientes.

## Verificación

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\python scripts/verify_private.py
```

La segunda comprobación es opcional: necesita las capturas privadas locales y las
reconstruye en memoria; no descarga ni publica datos. Ver [resultados y límites](docs/VALIDACION_MVP.md).

## Documentos principales

- [Base inicial v0.1](docs/BASE_INICIAL_V0.md) y [casos preparados](docs/CASOS_REFERENCIA_V0.md): decisiones delegadas, salida esperada y reglas editables.
- [Sistemas de referencia e insumos para specs](docs/SISTEMAS_REFERENCIA.md): análisis de AnalizadorPlanillas y seis referentes externos, con evidencia y escenarios candidatos.
- [Replanteamiento de la base](docs/REPLANTEAMIENTO_BASE.md): prioridad de conversión, retroalimentación y decisiones pendientes.
- [Referencia Excel analizada](docs/REFERENCIA_EXCEL.md): hallazgos y límites sin datos comerciales.
- [Habilidades instaladas](docs/HABILIDADES.md): uso, versiones, verificación y selección final.
- [Investigación de sistemas](docs/INVESTIGACION_SISTEMAS.md) y [diseño web](docs/INVESTIGACION_DISENO_WEB.md): fuentes primarias y evaluación.
- [Contexto del chat original](CONTEXTO_PROYECTO.md): decisiones confirmadas y propuestas previas.
- [Alcance del MVP](docs/ALCANCE_MVP.md): módulos, reglas y secuencia de trabajo.
- [Constitución](.specify/memory/constitution.md): principios de desarrollo, versión 1.0.0.
- [Primera especificación](specs/001-importacion-excel/spec.md): importación y revisión de Excel.
- [Checklist de la especificación](specs/001-importacion-excel/checklists/requirements.md).
- [Análisis de Excel](docs/ANALISIS_EXCEL.md): cómo determinar el contrato con los archivos reales.
- [Guía de Spec Kit](docs/SPECKIT.md): herramientas, comandos y estado de cada fase.

## Próximo paso

Probar las nuevas listas de proveedores cuando lleguen y ampliar perfiles a partir
de evidencia. OAuth, inventario transaccional, ventas y sincronización real de Mercado
Libre siguen como próximas funcionalidades, con sus propias especificaciones.
Los originales y reportes privados se guardan en `data/private/`, excluido de Git.

Las habilidades de Spec Kit están en `.agents/skills/`. El flujo es
`$speckit-specify` → `$speckit-clarify` → `$speckit-plan` → `$speckit-tasks`
→ `$speckit-analyze` → `$speckit-implement`.
