# Memoria del proyecto

Leer solo este índice al retomar; abrir una nota si su tema es relevante.
Estado: MVP Excel local terminado y verificado; ver README para iniciar.
Revalidado en este equipo: 66tests y Chrome aprobados; referencias privadas ausentes.
Rama: `codex/mvp-excel`. Activa: `specs/001-importacion-excel`.
Siguiente: nuevas listas/perfiles; integración real ML requiere otra especificación.
Datos reales: `data/private/`, jamás commitear. Sin escrituras Mercado Libre.

| Hito | Nota | Resultado |
| --- | --- | --- |
| 000 | [Base](000-base.md) | Preparación, delegación y persistencia compacta |
| 001 | [Diseño](001-design.md) | Contratos y18 tareas; sin bloqueos críticos |
| 002 | [Motor](002-engine.md) | 52tests y9casos privados; exportación determinista |
| 003 | [Aplicación](003-app.md) | API/panel;66tests y recorrido navegador completo |
| 004 | [Entrega](004-delivery.md) | Guía,18tareas terminadas y verificación final |
| 005 | [Arranque local](005-local-run.md) | Entorno instalado, revalidación y sistema iniciado |

Formato: una nota de hasta 120 palabras por hito, decisión/validación/siguiente.
El commit que contiene cada nota es su referencia: `git log -- docs/memory/000-base.md`.
No copiar logs, planillas, tokens ni contexto completo a memorias.
