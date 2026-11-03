# Verificación del MVP Excel local

Ampliación vigente: [validación local 004–007](VALIDACION_OPERACION_LOCAL.md),
117 pruebas y dos recorridos Chrome. Las verificaciones siguientes conservan la
historia de entregas anteriores; no certifican integración real con Mercado Libre.

Fecha: 2026-11-03 (Argentina). Rama: `codex/mvp-excel`.
Alcance: especificación001, conversión/revisión autónoma; no integración real Mercado Libre.

| Comprobación ejecutada | Resultado |
| --- | --- |
| pytest completo | 66 pruebas aprobadas |
| Motor/fórmulas | 52 pruebas aprobadas, incluidas en las66 |
| API/persistencia/catálogo | 14 pruebas aprobadas, incluidas en las66 |
| Casos privados CAS-01 a CAS-09 | 9 aprobados; capturas reconstruidas en memoria, no originales de proveedores |
| Ensayo de1000filas sintéticas | Aprobado,0.651s en este equipo; XLSX reabierto e identidad verificada |
| Chrome headless, interfaz real | XLSX/CSV, mapeo, cero, regla configurable, corrección, exportación por revisión, historial, perfiles/versiones/retiro y Full bloqueado |
| Paginación |60productos sintéticos,61filas incluyendo cabecera; navegación y filtro sin ocultar incidencias |
| Vista móvil390px | Sin desbordamiento horizontal de la página; tablas desplazables |
| JavaScript | Sin errores de ejecución en el recorrido probado |
| Revisión de formato | git diff --check sin errores |

Se usaron estados privados temporales para el navegador; no se configuró una contraseña
para el usuario ni se publicaron credenciales de prueba. Las capturas visuales muestran
solo información sintética y no se incorporan al repositorio.

## Fallos corregidos durante la verificación

- Descargas de una misma revisión diferían por timestamps del ZIP: normalización de
  metadatos y prueba que confirma bytes reproducibles tras reiniciar.
- Respuesta tardía de carga de catálogo podía sobrescribir un borrador en edición:
  protección por generación de solicitud y versión de edición; recorrido completo repetido.
- Cero explícito, referencias rotas y dependencias vacías conservan estados diferentes;
  la ausencia no se transforma en un precio certificado.

## Límites reales

XLSX/CSV UTF-8; fórmulas de un conjunto limitado, no motor Excel general. Expresiones
externas, funciones no admitidas y referencias rotas quedan pendientes. No se ejecutan
macros ni enlaces, ni se usan servicios IA o datos comerciales predeterminados.

El XLSX contiene valores de la revisión e informe, con formatos equivalentes por tipo;
no promete reconstrucción exacta de todo estilo, gráfico o fórmula activa original.
La clasificación de títulos y perfiles ayuda, pero no demuestra reconocimiento universal
de proveedores todavía no recibidos. El operador elige hojas y correspondencias.

Modo local127.0.0.1, un operador y proceso; no certificado para acceso público/LAN.
Catálogo de comparación introducido manualmente: sus capacidades no son verificaciones
de una cuenta Mercado Libre. No hay movimientos de stock, reservas, ventas o webhooks.

La suite emite un aviso de deprecación de Starlette sobre TestClient/httpx; las pruebas
pasan con las versiones fijadas. No implica un fallo del recorrido. Futuras actualizaciones
de dependencias deben repetir estas comprobaciones.

La verificación visual y el recorrido de teclado implícito de los controles no constituyen
una auditoría completa ni certificación WCAG. No se ejecutó auditoría de seguridad externa.

## Revalidación al retomar la rama

2026-11-03: leídos el contexto, la memoria y los artefactos de Spec Kit en
`codex/mvp-excel`. Las 18 tareas ya estaban completadas. Se creó el entorno `.venv`
con Python 3.12.14 y se instalaron las versiones fijadas sin modificar dependencias.

- Suite completa: 66 pruebas aprobadas; persiste el aviso de TestClient documentado.
- Recorrido Chrome contra un servidor con datos temporales separados: aprobado,
  incluidos XLSX/CSV, factor cero, paginación, corrección, exportación, perfiles,
  versiones, retiro, historial, comparación Full y vista móvil; sin errores JavaScript.
- Casos privados: omitidos explícitamente (`private_reference_unavailable`);
  esta copia solo contiene `data/private/.gitkeep`. Los nueve resultados anteriores
  son evidencia histórica, no una comprobación repetida en este equipo.
- Servidor de uso iniciado en `http://127.0.0.1:8765`: salud correcta y acceso inicial
  sin configurar, listo para que el operador cree su contraseña. No se trasladaron
  datos ni credenciales del recorrido de prueba al servidor de uso.

No se detectaron fallos que exigieran cambios en la aplicación durante esta revisión.
El proceso de prueba se detuvo después del recorrido; el servidor de uso queda activo.

## Ampliación: listas estandarizadas por SKU y precio

2026-11-03: el usuario priorizó reunir todas las listas en un formato común.
Se añadieron FR-025/027, SC-011/012 y tareas T019/022 a la especificación activa.
El análisis cruzado cubrió los tres requisitos nuevos con cuatro tareas, sin
conflictos críticos ni requisitos nuevos sin tarea. Los dos pendientes históricos
de originales de proveedores siguen abiertos y no se presentan como validados.

- 73 pruebas aprobadas: seis casos de normalización y uno de API/persistencia
  añadidos a las 66 existentes. Continúa el aviso no bloqueante de TestClient.
- Dos formatos sintéticos distintos generan SKU/precio comunes, conservando ceros
  iniciales, cero explícito, proveedor, archivo, hoja, fila y revisión.
- La API rechaza acceso sin sesión; las correcciones sustituyen únicamente la
  revisión actual de su carga. Se verificó persistencia tras reabrir y conservación
  de la descarga histórica. Las descargas estándar son reproducibles.
- Precios negativos, ausentes o inválidos y SKU repetidos quedan pendientes; las
  alternativas permanecen visibles. El mismo SKU de otro proveedor no se fusiona.
- Chrome: recorrido anterior más dos listas/proveedores, sugerencias SKU/precio,
  columnas de precio ambiguas sin selección automática, descarga y vista móvil.
  Sin errores JavaScript ni desbordamiento horizontal de la página a390px.

El consolidado es una proyección de la última revisión de cada carga, con una hoja
por carga. No resuelve equivalencias entre códigos de proveedores diferentes, no
elige precios ganadores ni convierte monedas. La descarga incluye también pendientes.
Las listas sin revisar se contabilizan sin incorporarse como productos interpretados.
Las referencias privadas siguen ausentes; se usaron exclusivamente datos sintéticos.

## Panel002 y hoja de ruta

2026-11-03: rediseñado el panel con Inicio, resumen real, últimos archivos, carga en
tres pasos, mapeo letra/encabezado, foco SKU/precio y datos opcionales desplegables.
La lista unificada conserva filtro, descarga y procedencia con mejor jerarquía visual.
No se modificaron persistencia, motor, endpoints ni reglas comerciales.

- Suite de regresión: 73 pruebas aprobadas; aviso TestClient conocido.
- Chrome, recorrido completo anterior más Inicio vacío/con datos, contadores contra
  API, tres pasos, etiquetas de columna, limpieza de filtros y navegación por teclado.
- Fallo503 sintético en el resumen: no se muestran contadores obsoletos y se puede
  recuperar al volver a Inicio sin tocar archivos.
- Capturas revisadas de Inicio, mapeo y tabla en escritorio1440px y móvil390px.
  Sin errores de ejecución JS ni desbordamiento horizontal de la página en el recorrido.
- Corregidos ayuda de perfil residual al cambiar archivo, avisos ajenos a la vista
  nueva y un detalle visual del indicador de guardado.
- Análisis de002: siete requisitos, cuatro criterios y seis tareas con cobertura;
  sin conflictos críticos con la constitución ni requisitos sin tarea. Checklist5/5.
- Specs003..007 creados con historias, aceptación, requisitos, casos límite,
  dependencias y calidad documental. No se presentan como implementados.

La verificación de teclado es un recorrido, no una certificación de accesibilidad.
La configuración activa de Spec Kit es local en `.specify/feature.json`, ignorada por
el diseño existente de Spec Kit; la memoria y hoja de ruta versionadas indican002.
Las fuentes oficialesML no pudieron leerse por403; los contratos/capacidades no se
declaran verificados. No hay nuevas escrituras externas ni datos de prueba en la BD de uso.

## Entrega003: proveedores y listas vigentes

2026-11-03: proveedores con identidad estable, alias, edición y retiro; alcances con
moneda/significado declarados; comparación de revisiones, activación local, versiones
inmutables, descarga y restauración mediante otra vista previa.

- Suite completa: 89 pruebas aprobadas (73 anteriores y16 de esta entrega).
  Persiste el aviso de TestClient documentado, sin fallos.
- Probadas activaciones simultáneas: una gana y la otra recibe conflicto, sin
  sobrescritura ni versiones huérfanas. Ediciones/retiro invalidan previews viejos.
- Precio cero, ceros iniciales, ausencias, inválidos y duplicados conservan estados
  distintos. Un último precio certificado sobrevive a una lista ambigua y otra inválida.
- Probados aislamiento por proveedor/alcance, asociación de varias hojas de un libro,
  metadatos obligatorios para activar, semántica inmutable y restauración obsoleta.
- Exportación histórica reproducible, consulta de vigentes y persistencia tras reabrir.
  Las nuevas rutas mantienen autenticación y CSRF; no hay escrituras Mercado Libre.
- Chrome: crear proveedor/alcance, seleccionar revisión, comparar, activar, actualizar
  de cero a12, restaurar y conservar descarga histórica. Tabla de vigentes contiene
  una fila por el SKU único del caso, sin las cargas históricas duplicadas.
- Respuesta tardía de una comparación se descarta al cambiar la selección; el usuario
  debe comparar otra vez. Inicio usa vigentes después de activar, evitando pendientes
  causados por alternativas históricas. Recorrido a390px sin desbordamiento de página.
- Capturas de escritorio/móvil revisadas. El recorrido anterior de motor/panel sigue
  aprobado. Las referencias privadas continúan ausentes; fixtures solo sintéticos.

Spec Kit: checklist5/5, diez requisitos y tres criterios cubiertos por seis tareas;
sin hallazgos críticos en análisis de consistencia. Persistencia usa tipos nuevos en
la tabla existente, sin migración destructiva. Los originales y revisiones no se alteran.
La activación declara vigente una lista local; no demuestra publicación ni sincronía remota.
