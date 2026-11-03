# Decisiones técnicas
Fecha2026-11-02. Investigación oficial por agente de fase0.
- UploadFile no limita cuerpo: contador ASGI12MiB antes del multipart, archivo10MiB.
  https://fastapi.tiangolo.com/tutorial/request-files/ y https://starlette.dev/requests/
- openpyxl lectura doble fórmula/caché; keep_links=False; defusedxml y ZIP acotado.
  https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html
- Evaluador restringido propio (sin eval): aritmética, comparaciones, IF/IFERROR,
  SUM/ROUND/VLOOKUP exacto, celdas locales, ciclos/límites. No ejecutar macros/URL.
  Fórmula no soportada/dependencia inválida queda pendiente aunque tenga caché.
- SQLite local fuera de OneDrive, transacciones breves BEGIN IMMEDIATE, FK on,
  CAS de revisiones evita pérdida de cambios; sin WAL inicialmente.
  https://docs.python.org/3/library/sqlite3.html y https://www.sqlite.org/lang_transaction.html
- UI nativa mismo origen; React pospuesto. No dependencia cloud/IA ni tarifas nuevas.
- Contraseña PBKDF2, sesión opaca revocable,8h, HttpOnly/SameSite strict; CSRF,
  allowlist Host/Origin y loopback. No tratar cookie legible como almacén privado.
  https://starlette.dev/middleware/#sessionmiddleware
- Tests pytest/TestClient y Playwright; sin credenciales ML.
  https://fastapi.tiangolo.com/tutorial/testing/
