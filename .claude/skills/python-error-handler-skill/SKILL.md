---
name: python-error-handler-skill
description: Skill creada para el manejo de errores, siempre que haya lógica backend por detrás que pueda fallar, tanto de forma transitoria (servidor, muchas peticiones de golpe en una parte de código, commits), como otro tipo de fallos (json vacío, formatos incorrectos, otro tipo de error).
---

# Cual es el objetivo de la skill
El objetivo es en todo momento controlar los errores, para no romper la aplicación y conseguir un correcto flujo de trabajo y de seguimiento, es muy importante que esta skill se apoyo en las ya creadas skills [python_retry_decorator_skill](../python-retry-decorator-skill/SKILL.md) para que sepa cuando tiene que implementar el decorador, y además de [revise_refactor_code](../revise-refactor-code/SKILL.md) para que sepa que tenemos que implementar siempre en este caso los test para saber el correcto flujo de trabajo.

## Formato de la skill
La lógica siempre tendrá que tener manejo de errores (try, except, else y finally), para poder controlar las partes con posibilidad de error en el código, su formato tendrá la siguiente forma:


```python
# routes/analysis.py
import logging
from flask import Blueprint, request
from utils.decorators import retry
from utils.responses import error_response, success_response

logger = logging.getLogger("bike_analytics")
bp = Blueprint("analysis", __name__)


@retry(max_tries=3, exceptions=(ConnectionError, TimeoutError), delay=1.0)
def _llamar_servicio_cv(angles_data: dict) -> dict:
    """Llama al servicio de análisis biomecánico. Reintenta si falla la conexión."""
    # Aquí iría la llamada real al módulo CV / MediaPipe
    ...


@bp.route("/api/analysis", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "angles" not in data:
        return error_response("Faltan datos de ángulos", 400)

    try:
        result = _llamar_servicio_cv(data["angles"])
        return (result, "Análisis completado")

    except (ConnectionError, TimeoutError) as e:
        logger.error(f"Servicio CV no disponible tras reintentos: {e}")
        return error_response("Servicio de análisis temporalmente no disponible", 503)

    except Exception as e:
        logger.exception(f"Error inesperado en análisis: {e}")
        return error_response("Error interno en el análisis", 500)
  

    from flask import jsonify
```

```python
# utils/responses.py
#En el fichero de utils correspondiente estas posibles funciones utilizadas utils/responses.py
def error_response(message: str, status_code: int, details: str = None):
    """
    Respuesta de error estandarizada para la API.

    Ejemplo de respuesta:
    {
        "error": true,
        "message": "No se pudo procesar el video",
        "details": "MediaPipe falló en el frame 42",
        "status": 500
    }
    """
    payload = {
        "error": True,
        "message": message,
        "status": status_code
    }
    if details:
        payload["details"] = details

    return jsonify(payload), status_code
```

- Ya viene dictada la estructura con las funcioness definidas arriba.

## Secuencia
1. Crear la estructura de errores controlados, para no romper la aplicación, estructura try/except y cuando haya que cerrar conexiones como en la de una base de datos, o código 100% necesario de ejecutar aunque haya error utilizar la estructura finally.

2. Si el código funciona correctamente pués solo pasará por el try, y si llega a excepciones por errores controlados se mandará un json a la función, api que esperaba una respuesta, con el error, su descripción y código. Pero si en cambio el error era para pasar a otra página como el 404, el error 500 de servidor, o el 403, se puede redireccionar o mandar un template html personalizado, capturado en el blueprint de errores donde estarán los errorhandler.

```python
# Ruta de página — el navegador la visita directamente
@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

# Endpoint de API — HTMX o fetch consumen la respuesta
@bp.route("/api/calculate", methods=["POST"])
def calculate():
    ...
    return error_response("Datos inválidos", 400)
```
- Esto es un ejemplo sencillo de la estructura básica que podría tener, pero entiende el flujo que estamos utilizando.

3. Finalmente será testear los cambios siguiendo la estructura de la skill de testing que he referenciado arriba, para verificar que los errores son controlados, que se obtienen los resultados esperados y que la aplicación es robusta tanto para casos de uso normales, como posibles errores simulados que puedan ocurrir.

## Aclaración Final
Los templates que se creen serán muy sencillos inicialmente solo para comprobar que funciona, ya más adelante en skills de frontend o yo mismo, los diseñaré y mejoraré, además para códigos de error que devuelvan html pero no sea útil crear una plantilla, simplemente podemos pensar en redireccionar a la ruta de comienzo de la página.