---
name: python-retry-decorator-skill
description: Manejo de errores Flask y Python, usar siempre que se implementen llamadas a APIs externas, operaciones de base de datos,
  procesamiento de lógica interna de la app o cualquier operación que pueda fallar por CAUSAS TRANSITORIAS (red, servidor sobrecargado, timeout, commit ...). Incluye el decorador @retry, logging estructurado y respuestas de error consistentes. Activar ante cualquier mención de
  "manejo de errores", "retry", "reintentos", "error handling", "excepción", o cuando se implementen servicios externos (Auth con google, apis de IA, apis, o modulos externos).
---


# Error Handling — Bike Analytics
Guía de implementación del manejo de errores para el backend Flask.
La filosofía es: **fallar de forma controlada, reintentar cuando tiene sentido, loggear siempre.**



## 1. Decorador `@retry` — patrón base
Usar para operaciones que pueden fallar transitoriamente: llamadas a APIs, queries a Supabase, lectura/escritura de archivos de video, imagenes u otros archivos de upload, unicamente para causas transitorias, no errores en los tipos de datos, o en el procesamiento de datos de un usuario que llegan vacios, pues eso no va a cambiar.

```python
# utils/decorators.py
import functools
import logging
import time

logger = logging.getLogger(__name__)


def retry(max_tries=3, exceptions=(Exception,), delay=0.5, backoff=2):
    """
    Decorador para reintentar funciones que fallan por causas transitorias.

    Args:
        max_tries: Número máximo de intentos (default: 3)
        exceptions: Tupla de excepciones a capturar (default: todas)
        delay: Espera inicial entre intentos en segundos (default: 0.5), útil en caso de sobrecarga puntual
        backoff: Multiplicador de espera entre intentos (default: 2 → 0.5s, 1s, 2s)

    Uso:
        @retry(max_tries=3, exceptions=(ConnectionError, TimeoutError))
        def llamar_api_externa():
            ...
    """
    def decorador(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            espera = delay
            ultimo_error = None

            for intento in range(1, max_tries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    ultimo_error = e
                    logger.warning(
                        f"[retry] {func.__name__} — intento {intento}/{max_tries} fallido: {e}"
                    )

                    if intento < max_tries:
                        time.sleep(espera)
                        espera *= backoff

            logger.error(
                f"[retry] {func.__name__} — agotados {max_tries} intentos. "
                f"Último error: {ultimo_error}"
            )
            raise ultimo_error

        return wrapper
    return decorador
```

- Añade `delay` con `backoff` exponencial (evita saturar el servidor)
- Usa `functools.wraps` para preservar el nombre y docstring de la función original
- Logging estructurado en lugar de `print()`
- Parámetro `exceptions` tipado como tupla (más explícito)

---

## 2. Posibles casos de uso del decorador `@retry` y con qué parámetros

| Contexto                                                                          | `max_tries` |
|-----------------------------------------------------------------------------------|-------------|
| Llamada a API externa                                                             | 3           |
| Query a Supabase/PostgreSQL o db utilizada                                        | 3           |
| Procesamiento MediaPipe(ejemplo cualquiera) o cualquier Api                       | 2           |
| Lectura de archivo de video                                                       | 2           |



**No usar `@retry` en:**
- Errores de validación de datos del usuario (400 Bad Request) → no son transitorios
- Errores de autenticación (401/403) → no son transitorios, reintentar no cambia nada
- Lógica de negocio interna @retry → solo para operaciones con fallos transitorios (red, servidor)..., hay que evitar repetir una función que simplemente falle por que los datos de entrada sean malos.
- Lógica de negocio interna → usar `try/except` con `raise` para que el error llegue limpio al error handler global

---

-- Recordar utilizar de complemento las skill de manejo de errores.

## Consideración final
- Se esta utilizando la extensión de sentry, por ende los errores se mostrarán con el formato que pauta la extensión.