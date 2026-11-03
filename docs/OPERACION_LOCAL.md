# Trabajar sin cuenta de Mercado Libre

Estas pantallas funcionan con datos guardados en este equipo. Una referencia de cuenta
no autoriza Mercado Libre; una captura manual no demuestra el estado remoto. No hay
conexión, renovación de credenciales, webhooks, sincronización automática ni envío de correo.
El catálogo de comparación de prueba anterior sigue disponible por separado.

## Preparar productos y listas

1. Cargá y revisá el Excel del proveedor. Confirmá sus columnas SKU y precio; guardá
   el perfil para repetir el proceso. Los originales y las correcciones conservan historia.
2. En Proveedores y listas, creá el alcance con moneda y significado del precio,
   compará la revisión y activá la versión que deba usarse. Las filas pendientes no
   se convierten silenciosamente en precios válidos.
3. En Catálogo local, creá una referencia de cuenta y cada producto interno con SKU,
   nombre y unidad indivisible. Las cantidades son enteras en esa unidad; no hay
   conversión automática de cajas, bultos o unidades.
4. Capturá manualmente la publicación: cuenta, referencia, variante si existe,
   moneda, significado del precio y logística. No inventes referencias remotas.
5. Confirmá por separado publicación↔producto y producto↔SKU del proveedor. Un
   código coincidente entre proveedores o una descripción similar no confirma equivalencia.

Las cuentas se pueden deshabilitar sin borrar historia. Una captura se edita eligiéndola
en el formulario; se conservan sus versiones. Retirar un vínculo bloquea propuestas
que dependían de él. Si otra pantalla cambia un registro, actualizá antes de guardar.

## Proponer y simular precios

Ingresá y confirmá una regla por cuenta/lista: base × multiplicador + cargo, con
decimales explícitos y redondeo de mitades hacia arriba. No hay tarifas, impuestos,
conversión de monedas ni multiplicadores de negocio preestablecidos.

Prepará una propuesta y revisá sus valores y bloqueos. La propuesta conserva la
versión del proveedor, la regla, la captura y los vínculos usados. Su simulación
revalida esas referencias; un cambio posterior produce conflicto y exige otra propuesta.

El simulador modifica únicamente la captura local cuando está habilitada para pruebas.
Permite probar éxito, rechazo, fallo previo, timeout posterior y aceptación sin cambio.
Una respuesta incierta se comprueba antes de repetir; como máximo hay tres intentos
manuales por operación. Los conflictos no se fuerzan con un reintento. Una propuesta
sin intentos puede cancelarse; revertir exige preparar y confirmar una propuesta nueva.
Ninguno de estos resultados equivale a un precio publicado o verificado en Mercado Libre.

## Inventario propio y Full

Creá ubicaciones propias compartidas o ubicaciones Full asociadas a una referencia
de cuenta. Cada producto/ubicación se da de alta una sola vez. Para propio, declarás
conteo inicial y margen; para Full, la cantidad empieza desconocida y se carga como
observación manual con referencia de origen.

En propio, libre sin asignar = físico − margen − reservas − asignaciones disponibles,
con piso cero. Las asignaciones distribuyen la misma existencia entre cuentas;
no crean más stock. Un ajuste requiere motivo y no puede consumir reservas ni
asignaciones protegidas. El mínimo de alerta es opcional y explícito; se compara
con físico menos margen y reservas (las asignaciones disponibles siguen siendo stock).

Un conteo para conciliar registra base, observado y diferencia sin ajustar existencias.
Investigá la diferencia, registrá un ajuste si corresponde y repetí el conteo para
cerrar la incidencia con evidencia. No hay ajuste automático.

Full conserva cantidad, fecha y origen de la última observación manual. No admite
ajustes ni asignaciones propias; las ventas manuales Full no alteran esa observación
ni descuentan inventario propio. No es una medición en tiempo real.

## Ventas manuales

Primero confirmá la política mostrada en Ventas locales. La reserva requiere una
asignación disponible de esa cuenta. Registrar reserva reduce esa asignación y
aumenta lo reservado, sin descontar todavía el físico. Despachar descuenta una sola
vez y libera la reserva. Cancelar una reserva la libera; si la cuenta continúa habilitada,
devuelve esa cantidad a su asignación. Una cuenta deshabilitada conserva la posibilidad
de finalizar una venta existente, pero no de iniciar otra o aumentar su reserva.

Usá Preparar siguiente estado para conservar cuenta, existencia y referencia de venta.
Cada modificación aumenta la secuencia. Corregí la cantidad en un evento de reserva
separado antes de despachar/cancelar. Una devolución parcial indica el total acumulado
recibido y requiere confirmar recepción física para reponer. Una venta despachada
no se repone mediante cancelación.

Los eventos duplicados no repiten movimientos; las secuencias viejas se ignoran y
dos estados distintos con la misma secuencia generan conflicto. La identidad incluye
cuenta y referencia; no cambies la existencia de una venta para corregirla implícitamente.

## Alertas, avisos y exportaciones

Alertas y auditoría consolida pendientes de listas vigentes, mínimos, Full desconocido,
diferencias de conteo y problemas del simulador. Reconocer no resuelve; la causa debe
desaparecer de la evidencia local. Al reaparecer, abre otro ciclo conservando historia.
No se supervisa nada mientras el servidor está detenido; las alertas se revisan al consultar.

Podés preparar un aviso .eml con destinatario explícito. Se descarga para revisión;
el sistema no lo envía ni lo marca entregado. Repetir preparación para el mismo ciclo
y destinatario devuelve el mismo aviso.

La auditoría filtra por cuenta, recurso, acción, fecha y estado registrado; muestra
historia, no solo el estado actual. Los registros antiguos sin estado conservado no
aparecen al filtrar un estado. La descarga de estado local incluye inventario,
ventas, propuestas históricas, resultados simulados y alertas con sus fechas/orígenes.
Una propuesta histórica necesita revalidación antes de ejecutarse; la exportación no
vuelve a leer los Excel ni certifica datos remotos.

## Pendiente para la integración real

Aplicación y cuentas autorizadas; documentación/capacidades verificadas; OAuth y
catálogo paginado; contratos de precios/stock y verificación remota; webhooks y
conciliación programada. El correo necesita un servicio configurado y una prueba de
entrega. Alojamiento público, roles y operación multiusuario requieren otra especificación.
Las partes remotas de 004–007 permanecen pendientes; estas funciones locales no las sustituyen.
