# Decisiones

Usar IDs y alias explícitos evita confundir nombre de archivo con identidad.
Asociar import_id al activar bloquea reutilización posterior en otro proveedor/alcance;
varias hojas revisadas del mismo libro pueden contribuir al mismo snapshot. No se
elige entre revisiones del mismo import/hoja silenciosamente.
Snapshot revisado y guardado en preview no se reconstruye al activar/exportar.
Concurrencia: validar current_version_id, revision de alcance/proveedor y bindings
bajo BEGIN IMMEDIATE. Dos activaciones de la misma base no pueden ganar juntas.
Ausentes se conservan pendientes; precio inválido único conserva valor previo certificado
con referencia al intento. Duplicados conservan alternativas y quedan bloqueados.
Historial de snapshots preserva nombres/semántica originales aunque cambie nombre visible.
