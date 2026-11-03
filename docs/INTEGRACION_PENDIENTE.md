# Evidencia y condiciones de integración

Fecha de consulta: 2026-11-03. Estado: contratos y capacidades sin validar por cuenta.

Se intentó leer estas páginas oficiales:

- [Autenticación y autorización](https://developers.mercadolibre.com.ar/autenticacion-y-autorizacion).
- [API de precios](https://developers.mercadolibre.com.ar/es_ar/api-de-precios).
- [Stock distribuido](https://developers.mercadolibre.com.ar/stock-distribuido).

La lectura directa devolvió403 en las tres. Los resultados de búsqueda no sustituyen
la revisión de las páginas completas ni prueban permisos de una cuenta. No se adoptan
plazos, límites, endpoints de escritura o funciones habilitadas a partir de snippets.

Antes del plan de integración real de004: contrastar autorización, requisitos de retorno, permisos,
renovación, revocación e identidad con documentación accesible y aplicación real.
Antes de005: comprobar edición de precios por destino, moneda, automatizaciones,
variaciones, control de conflictos y lectura de verificación.
Antes de006: comprobar ubicaciones, productos de usuario, modelos de stock, Full,
estados de ventas, notificaciones y reconciliación. No ejecutar escrituras para
descubrir permisos sobre productos sin un alcance controlado y autorizado.

Las especificaciones contienen condiciones verificables de negocio sin declarar
habilitados esos contratos. Las credenciales permanecerán fuera del repositorio.

Actualización: usuario sin cuenta autoriza el resto. Las partes locales004–007 usan
referencias/capturas manuales y simulador; las condiciones anteriores siguen pendientes.
Ver [operación local](OPERACION_LOCAL.md). No se incorpora ningún conector de red ficticio.
