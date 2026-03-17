---
name: auth_security_skill
description: El disparador será provocado por conversaciones relacionadas con el auth, rate limit en el auth, test de usuarios, mejoras en las funciones o nivel de seguridad a nivel de registro/sesión usuario, todo lo que tenga que ver con la mejora y desarrollo del auth.
---

# En cambios que pueden comprometer el funcionamiento del usuario a nivel AUTH
Skill para mantener y mejorar la seguridad del sistema de autenticación.
Proyecto de tamaño mediano/pequeño — aplicar criterio de ingeniería sin sobreingeniería.


## Principios base

- Cubrir los fallos más evidentes primero
- No añadir complejidad innecesaria
- Priorizar protección contra usuarios maliciosos sobre casos de uso extremos teóricos
- Seguir las directrices de [revise_refactor_code](../revise_refactor_code/SKILL.md)



## Cuándo activar esta skill

- Cambios en rutas `/auth/*`
- Modificaciones en modelos de usuario o sesión
- Añadir o modificar rate limiting
- Nuevas validaciones de formulario
- Cambios en mensajes de error del auth
- Petición explícita de revisión de seguridad en auth


## Cómo proceder ante un cambio

### 1. Ejecutar tests existentes primero

- Antes de crear nada nuevo, correr los tests ya existentes relacionados con el cambio.
Solo si guardan relación con lo modificado.


### 2. Evaluar si el cambio requiere tests nuevos

Un cambio requiere tests nuevos si:
- Añade una validación no cubierta
- Introduce un nuevo mensaje de error
- Cambia el comportamiento esperado de una ruta
- Añade protección que necesita verificación post-operación (ej: rate limit, funcionalidad de los usuarios frente a los nuevos cambios, casos extremos)



## Seguridad en el AUTH de la aplicación
- Se tendrán que implementar las medidas exigidas por el desarrollador (yo), o implementarse cuando se vea necesario que pueda haber una fuga de seguridad. Lo ideal será cubrir todos los edge cases pero como es una web de mediano/pequeño tamaño como digo en el objetivo del proyecto no hacer sobreingenieria y complicar todo.

- Cubrir principalmente los fallos más evidentes, tratar de crear test que cubran más casos y sobre todo posibles usuarios maliciosos que serán los que haya que controlar, para que no puedan tirar la web.


## Como funcionar y que tests ejecutar
- La manera de proceder será la siguiente cubrir inicialmente las nuevas medidas/cambios producidos con los test ya creados, en caso de que se vea incompleta la seguridad porque igual esa medida requiere una validación post operación, o validación adicional de su contenido crear los test nuevos.

- Los test nuevos siempre se crearán después de que se hayan pasado los iniciales, siempre cuando estos posibles test existentes guarden relación con los cambios, solo si no tiene relación no será necesarios ejecutarlos.

- Los test tendrán que cubrir casos en auth más radicales, revisar que los formatos se cumplen en las situaciones normales, el uso de errores funciona de manera esperada, los posibles mensajes de error creados se implmentan de manera satisfactoria...

- Cubrir para casos extremos, también hay que cubrir a ese usuario que pueda llegar a meter bots o hacer constantes peticiones malognas, por ello y junto a medidas como rate limiting, podemos implementar mensajes de error o lanzar errores con el codigo de error a los usuarios que por ejemplo hacen más peticiones o las mismas de las que se establece en el limiter de la ruta.

- Si estas medidas no se han creado deberán ser adicionadas sin duda alguna al proyecto lanzar el test que tambiñen deberá crearse para cada caso abarcado posible.

## Criterio de severidad

- Tipo | Prioridad 
- Ruta protegida accesible sin auth | Crítica — bloquear |
- Sin rate limit en login/registro | Alta |
- Mensaje de error expone info sensible | Media |
- Validación de formato incompleta | Media |
- Caso extremo teórico improbable | Baja — valorar coste/beneficio |
- Razonar otras posibles situaciones, SIEMPRE en caso de duda preguntar sobre la forma de implementación, grado de importancia.