--- 
name: revise-refactor-code
description:   Ejecutar cuando el usuario indique que ha modificado, código manualmente. Activación: usuario escribe "revisa mis cambios", "review", cambios hechos, o similar. Cambios tambien en cualquier fichero como Models, routes, utils, de lógica creada con el lenguaje Python, PostgreSQL, SQL, Flask, SQLalchemy. NO ejecutar de forma autónoma sin confirmación.
--- 

# Revisión y refactor post-modificación manual


## Filosofía de intervención
- Corriges errores, mejoras lo existente, iteras sobre lo construido.
- NO reescribes desde cero ni añades capas de abstracción no solicitadas.
- Respetas el stack (Flask, HTMX/Alpine, Tailwind, PostgreSQL) y la
  preferencia por claridad arquitectónica sobre complejidad.
- Si una mejora es opcional o de gusto, la propones — no la impones.


## Paso 1 — Diagnóstico antes de tocar nada
Antes de cualquier cambio, responde estas preguntas internamente:
- ¿Qué archivos/funciones han cambiado? (usa git diff o lectura directa)
- ¿Cuál parece ser la intención del cambio?
- ¿Hay algo que claramente rompe lógica, seguridad o consistencia?
- ¿Hay algo que preservar sin tocar aunque parezca mejorable?

Si la intención no está clara → pregunta antes de actuar.
Si el cambio afecta múltiples módulos → confirma el alcance con el usuario.


## Paso 2 — Clasificación de hallazgos (antes de modificar)
Presenta un resumen estructurado con tres categorías:

**[CRÍTICO]** — Bugs, errores lógicos, problemas de seguridad, inconsistencias
de datos. Se corrigen siempre, pero avisando qué y por qué.

**[MEJORA]** — Legibilidad, convenciones Python/Flask, pequeñas optimizaciones.
Se aplican si no alteran la intención original.

**[SUGERENCIA]** — Features útiles, patrones recomendables, refactors mayores.
Se proponen con explicación breve. El usuario decide si aplicarlos.


## Paso 3 — Ejecución por bloques
- Si hay cambios en múltiples partes del proyecto: ir módulo a módulo,
  confirmar con el usuario entre bloques si el alcance es significativo.
- Cada bloque de cambios debe ser legible, comentado brevemente si añade
  lógica no obvia, y coherente con el estilo previo del archivo.
- No añadir dependencias externas sin mencionarlo explícitamente.


## Paso 4 — Testing
Ejecutar tests en estos casos:
- Se modificó lógica de negocio, rutas Flask, o consultas a base de datos.
- Se corrigió un [CRÍTICO].
- El cambio afecta flujo de datos entre módulos.

Protocolo:
1. Ejecutar el test relevante.
2. Si falla: un ciclo de corrección + re-test.
3. Si falla de nuevo: reportar el error al usuario con diagnóstico claro
   en lugar de seguir iterando a ciegas. Máximo 4-5 intentos autónomos.

No hacer testing para: cambios puramente estéticos, renombrado de variables,
comentarios, o ajustes de formato.


## Paso 5 — Resumen final
Al terminar, entregar un resumen breve:
- Qué se corrigió y por qué era un problema.
- Qué se mejoró y qué ganamos con ello.
- Qué sugerencias quedan pendientes de decisión tuya.
- Estado de los tests ejecutados.


