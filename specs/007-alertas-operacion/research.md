# Decisiones para modo local

Se conserva el runtime y almacenamiento existentes. No se crea un conector ficticio
que afirme autorizaciones, envíos o respuestas de Mercado Libre. El adaptador local
permite comprobar reglas y recuperación sin adquirir servicios ni introducir credenciales.
Identidad explícita por ID; ninguna unión por descripción o SKU de proveedores distintos.
BEGIN IMMEDIATE serializa revisiones y efectos; claves de idempotencia conservan fingerprint.
El correo descargable es un archivo preparado, nunca una entrega confirmada.
