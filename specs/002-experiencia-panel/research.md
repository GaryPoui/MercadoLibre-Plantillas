# Decisiones de diseño

- Mantener JavaScript nativo evita migrar datos o introducir un build solo por presentación.
- Inicio deriva contadores de endpoints existentes; no simula ventas/cuentas conectadas.
- Tres pasos reflejan archivo → correspondencias → resultado. No bloquear navegación
  histórica ni ocultar revisiones por seguir el recorrido visual.
- Mantener controles de formulario nativos y etiquetas; no usar dependencias web externas.
- Consultas paralelas independientes; errores visibles y datos previos descartados al logout.
- Revisión de la propuesta: se descartaron tarjetas decorativas repetidas y estadísticas
  comerciales ficticias. El énfasis es la tabla de proveedores y las acciones de revisión.
