# Entregas y especificaciones

Actualizado: 2026-11-03. La rama de trabajo continúa siendo `codex/mvp-excel`.
La especificación activa se obtiene de `.specify/feature.json`; no del nombre de rama.

| Orden | Especificación | Estado y resultado |
| --- | --- | --- |
| 001 | [Conversión y lista unificada](../specs/001-importacion-excel/spec.md) | Implementada: XLSX/CSV, revisión, perfiles, historial y salida común SKU/precio |
| 002 | [Experiencia del panel](../specs/002-experiencia-panel/spec.md) | Implementada: Inicio, carga guiada, mapeo comprensible y diseño responsivo |
| 003 | [Proveedores y listas vigentes](../specs/003-proveedores-listas-vigentes/spec.md) | Implementada: identidad estable, comparación, activación, historial y restauración |
| 004 | [Cuentas y catálogo ML](../specs/004-cuentas-catalogo-ml/spec.md) | Especificada: autorización por cuenta, lectura y vínculos confirmados |
| 005 | [Precios verificados](../specs/005-precios-verificados/spec.md) | Especificada: vista previa, conflictos, aplicación y verificación remota |
| 006 | [Inventario y ventas](../specs/006-inventario-ventas/spec.md) | Especificada: existencias compartidas, reservas, Full separado e idempotencia |
| 007 | [Alertas y operación](../specs/007-alertas-operacion/spec.md) | Especificada: problemas accionables, auditoría, correo configurado y recuperación |

## Qué sigue después de proveedores

003 distingue una última revisión **por carga** de una versión vigente **por proveedor
y alcance**. La vista de revisiones conserva alternativas de archivos; la de vigentes
reúne solo versiones activadas, con comparación e historial. No se eligen precios por
fecha, nombre de archivo o valor menor.

003 tiene plan, modelo, contratos, tareas y pruebas de listas completas/parciales,
ausentes, duplicados, restauración, concurrencia y aislamiento. Sus pruebas utilizan
datos sintéticos; las referencias privadas no están disponibles en este equipo.

La siguiente entrega es004: conectar cuentas y leer catálogo. Su plan debe comenzar
verificando documentación accesible y requisitos de la aplicación real. Requiere
aplicación registrada y cuentas autorizadas para comprobar la integración.
005/006 necesitan capacidades reales y reglas comerciales/de inventario antes de
habilitar escrituras. 007 puede empezar por incidencias de listas; correo y alertas
comerciales requieren configuración explícita.

## Límites de esta entrega

Los documentos004..007 especifican comportamiento futuro; no implican que el sistema
ya tenga esas capacidades. Sus checklists evalúan calidad documental, no verifican
integraciones. No se preparan planes técnicos ficticios basados en permisos desconocidos.
No se cambia la constitución ni se incorporan datos de negocio a los specs.
