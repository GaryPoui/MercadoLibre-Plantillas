# 006 · Listas unificadas

Usuario prioriza estandarizar todas las listas relacionando SKU y precio.
Antes existía mapeo individual; faltaba consolidado. FR025/027 y T019/022 documentados.
Nueva lista unificada toma última revisión por carga, conserva proveedor/origen,
marca duplicados y precios inválidos pendientes; cero y ceros iniciales preservados.
Descarga común con informe, autenticada y determinista. Sin fusionar proveedores
ni elegir precios ganadores. Sugerencias exactas de encabezados requieren confirmación;
no asumen costo como precio. Persistencia sin migración.
73tests y recorrido Chrome ampliado aprobados; privados ausentes.
Servidor reiniciado en8765 conservando datos. README explica uso y una hoja por carga.
Siguiente: probar listas reales y resolver equivalencias explícitas cuando se necesiten.
