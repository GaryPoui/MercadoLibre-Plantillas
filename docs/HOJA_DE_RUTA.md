# Entregas y especificaciones

Actualizado: 2026-11-03. La rama de trabajo continúa siendo `codex/mvp-excel`.
La especificación activa se obtiene de `.specify/feature.json`; no del nombre de rama.

| Orden | Especificación | Estado y resultado |
| --- | --- | --- |
| 001 | [Conversión y lista unificada](../specs/001-importacion-excel/spec.md) | Implementada: XLSX/CSV, revisión, perfiles, historial y salida común SKU/precio |
| 002 | [Experiencia del panel](../specs/002-experiencia-panel/spec.md) | Implementada: Inicio, carga guiada, mapeo comprensible y diseño responsivo |
| 003 | [Proveedores y listas vigentes](../specs/003-proveedores-listas-vigentes/spec.md) | Especificada: identidad estable, comparación de versiones y activación explícita |
| 004 | [Cuentas y catálogo ML](../specs/004-cuentas-catalogo-ml/spec.md) | Especificada: autorización por cuenta, lectura y vínculos confirmados |
| 005 | [Precios verificados](../specs/005-precios-verificados/spec.md) | Especificada: vista previa, conflictos, aplicación y verificación remota |
| 006 | [Inventario y ventas](../specs/006-inventario-ventas/spec.md) | Especificada: existencias compartidas, reservas, Full separado e idempotencia |
| 007 | [Alertas y operación](../specs/007-alertas-operacion/spec.md) | Especificada: problemas accionables, auditoría, correo configurado y recuperación |

## Qué sigue después del diseño

La siguiente implementación es003. Resuelve una limitación actual: hoy el consolidado
conserva una última revisión **por carga**, por lo que dos cargas del mismo proveedor
pueden aparecer como alternativas repetidas. El futuro conjunto vigente **por proveedor
y alcance** permitirá comparar y activar la nueva lista sin perder el historial.
No se reemplazan precios automáticamente por fecha, nombre de archivo o valor menor.

Antes de implementar003: elaborar su plan técnico, modelo, contratos y tareas; analizar
consistencia, ejecutar pruebas con al menos dos versiones y registrar las limitaciones
de los archivos reales disponibles. La especificación ya distingue lista completa y
actualización parcial, productos ausentes, duplicados y concurrencia de activaciones.

004 requiere aplicación registrada y cuentas autorizadas. 005 y006 necesitan evidencia
de capacidades reales y reglas comerciales/de inventario antes de habilitar escrituras.
007 puede empezar por incidencias de listas; correo y alertas comerciales requieren
configuración explícita. La falta de credenciales no impide avanzar con003.

## Límites de esta entrega

Los documentos003..007 especifican comportamiento futuro; no implican que el sistema
ya tenga esas capacidades. Sus checklists evalúan calidad documental, no verifican
integraciones. No se preparan planes técnicos ficticios basados en permisos desconocidos.
No se cambia la constitución ni se incorporan datos de negocio a los specs.
