# Entregas y especificaciones

Actualizado: 2026-11-03. La rama de trabajo continúa siendo `codex/mvp-excel`.
La especificación activa se obtiene de `.specify/feature.json`; no del nombre de rama.

| Orden | Especificación | Estado y resultado |
| --- | --- | --- |
| 001 | [Conversión y lista unificada](../specs/001-importacion-excel/spec.md) | Implementada: XLSX/CSV, revisión, perfiles, historial y salida común SKU/precio |
| 002 | [Experiencia del panel](../specs/002-experiencia-panel/spec.md) | Implementada: Inicio, carga guiada, mapeo comprensible y diseño responsivo |
| 003 | [Proveedores y listas vigentes](../specs/003-proveedores-listas-vigentes/spec.md) | Implementada: identidad estable, comparación, activación, historial y restauración |
| 004 | [Cuentas y catálogo ML](../specs/004-cuentas-catalogo-ml/spec.md) | Parte local implementada: referencias, productos y vínculos confirmados. OAuth/lectura remota pendientes |
| 005 | [Precios verificados](../specs/005-precios-verificados/spec.md) | Parte local implementada: reglas, propuestas, conflictos y simulador recuperable. Aplicación/verificación remota pendientes |
| 006 | [Inventario y ventas](../specs/006-inventario-ventas/spec.md) | Parte local implementada: físico compartido, asignaciones, reservas, ventas manuales y Full observado. Eventos/conciliación remotos pendientes |
| 007 | [Alertas y operación](../specs/007-alertas-operacion/spec.md) | Parte local implementada: alertas, auditoría/exportación y avisos .eml no enviados. Correo/transporte remoto pendientes |

## Qué sigue después de proveedores

003 distingue una última revisión **por carga** de una versión vigente **por proveedor
y alcance**. La vista de revisiones conserva alternativas de archivos; la de vigentes
reúne solo versiones activadas, con comparación e historial. No se eligen precios por
fecha, nombre de archivo o valor menor.

003 tiene plan, modelo, contratos, tareas y pruebas de listas completas/parciales,
ausentes, duplicados, restauración, concurrencia y aislamiento. Sus pruebas utilizan
datos sintéticos; las referencias privadas no están disponibles en este equipo.

El usuario indicó que todavía no tiene cuenta y autorizó avanzar con el resto.
004–007 tienen planes, modelos, contratos y tareas para la operación local descrita
en [la guía](OPERACION_LOCAL.md). Los parámetros comerciales se ingresan y confirman
en la aplicación. Ninguna referencia manual demuestra capacidad ni autorización remota.

## Límites de esta entrega

Las cláusulas de OAuth, lectura/escritura y verificación remota, webhooks, conciliación
periódica y correo real siguen diferidas. Para retomarlas hacen falta una aplicación,
cuentas y documentación oficial accesible; no se completan probando el simulador.
La [validación](VALIDACION_MVP.md) y el análisis de cada spec distinguen cobertura local
y requisitos pendientes. Las referencias privadas siguen pendientes de validación aquí.
