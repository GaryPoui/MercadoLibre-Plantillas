# Casos de referencia iniciales, sin datos comerciales

Fecha: 2026-11-02. Base: capturas reales de las planillas ya entregadas.
Los nombres, códigos, importes, coordenadas y fórmulas exactos están en la carpeta
privada. Este índice anonimiza la información comercial; no inventa un proveedor
de entrada ni asegura resultados de un conversor inexistente.

| Caso | Situación tomada de la referencia | Resultado esperado inicial |
| --- | --- | --- |
| CAS-01 | Dos filas con código textual de cero inicial y cálculos de estructura simple | Conservar identidad y base; costo, promoción, neto y margen coinciden con la aritmética observada; cifras y parámetros en el expediente privado |
| CAS-02 | Falta el valor base, pero hay costo y fórmulas dependientes que muestran cero | Preservar ausencia; derivados dependientes pendientes; no publicar ni completar con cero |
| CAS-03 | Valor base cero explícito y división por cero | Distinguir cero introducido de ausencia; conservar evidencia y marcar cálculo inválido |
| CAS-04 | Varios identificadores en una celda | Mantener valor original y candidatos separados; no elegir destino ni duplicar stock |
| CAS-05 | Referencia rota cuya función de error devuelve cero | Señalar referencia y derivados afectados; cero histórico visible en revisión, sin certificar envío o margen |
| CAS-06 | Cabeceras distribuidas, familia y presentaciones antes de los productos | Preservar contexto y posiciones de perfil; no contar cabeceras como productos ni asumir una sola presentación |
| CAS-07 | Ventas y cantidad vendida; importes de distinto tipo/escala visible | Clasificar como métrica de ventas, no stock; mantener texto, número y presentación sin alterar escala a ciegas |
| CAS-08 | Mismo código con destinos diferentes | Conservar filas y marcar candidatos de vínculo; no fusionar automáticamente |
| CAS-09 | Hoja de tareas junto al catálogo | Clasificar y contabilizar como hoja operativa excluida del catálogo |

CAS-01 contiene una pareja de entrada/salida documental de dos filas tomada de la
misma referencia, con aritmética comprobada por separado. No es una pareja original
de proveedor y plantilla final corregida; el usuario autorizó avanzar con esta base.

Los casos derivados siguientes se especifican para las pruebas futuras, sin afirmar
que hayan sucedido en los archivos reales: modificar un factor crea una versión nueva;
retirar una regla no reescribe historial; una corrección local no cambia otra lista;
dos archivos en una revisión generan una salida con los mismos orígenes y resultados.

La futura verificación del conversor deberá reabrir los archivos generados y contrastar
estos resultados, las fórmulas permitidas, sus dependencias y los totales. La preparación
documental no reemplaza esas pruebas.
