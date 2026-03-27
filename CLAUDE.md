# SKILL PRINCIPAL Y PERSISTENTE DEL PROYECTO

## Explicación del proyecto

- Web gratuita y profesional de ciclismo más concretamente sobre el calculo de presiones en las ruedas del ciclista, según la entrada de valores que ingresa el usuario en un formulario.

- Se considerán los siguientes aspectos, disciplina de ciclismo, peso del ciclista + peso de la bici, ancho del neumático, tipo del terreno, sistema de cubierta, y objetivos del ciclista.

- Que destaque por la simplicidad y utilidad donde el usuario puede ver el historial de analisis registrarse y hacer peticiones de cálculo con varias bicicletas.

## Stack

- Vamos a utilizar el siguiente stack tecnológico el cual no deberá cambiarse NUNCA, por ninguna razón.

- Lenguaje backend Python con el framework Flask para toda la parte del servidor.

- Frontend será empleado html, css, JavaScript con los frameworks TailwindCss y HTMX, nada más.

- Base de datos a utilizar será postgreSQL con el ORM en Flask de SQLalchemy.

- También usaremos todas las extensiones disponibles de Flask que no puedan ser necesarias pero SOLO si es necesario, sin hacer sobreingeniería, ni complicar demas el proyecto.

- Si se puede simplificar sin perder rendimiento usar las plantillas Jinja2, pués tengo experiencia solo si no se pisa con HTMX,pero es probable que se pise con fetch de JS o HTMX por ende dar prioridad a JS o HTMX.

- Las APIS a utilizar serán las Api Rest solo cuando sea necesario.

- Seguimiento de errores con Sentry que se implementa bien con Flask por lo visto y testing con pytest.

## Detalles a seguir en el proyecto MUY IMPORTANTE

- El proyecto tiene intención de ser el primero a producción por lo tanto se deberá distinguir el entorno de desarrollo con el de producción, todas las credenciales y configuraciones no deberán hardcodearse y serán protegidas mediante el uso de entornos virtuales, y emplear gitignore necesario.

- Se emplearan JWT para proteguer las Apis y y las rutas validandolo y con duración limitada para no evitar intrusos maliciosos.
Implementar Rate limit en las rutas que lo requieran vulnerables a constantes consultas o ataques diferentes.

- Utilizar CSRF en los formularios para que vayan más protegidos.

- Revisar y sanear urls de los media queries, formatos de los uploads y tamaños de archivos coherentes.

- Validación de formularios, tanto desde la parte del servidor como de la parte del cliente, no queremos usuarios que no cumplan formatos estandar.

- Tratar de implementar medidas de seguridad vitales para el MVP, pero sin complicar en exceso

## Arquitectura del MVP

- Vamos a emplear una arquitectura por capas cliente-servidor no muy compleja para el MVP y proyecto pequeño creo que resultará suficiente. Con la siguiente estructura:
flask_app/
├── src/                    ← Código fuente (Source)
│   ├── database/           ← Conexión y esquema de BD
│   ├── models/             ← Lógica del esquema (ORM)
│   ├── routes/             ← Blueprints, puntos de entrada HTTP
│   ├── services/           ← Lógica de negocio pura
│   ├── tests/              ← Pruebas unitarias
│   └── utils/              ← Funciones auxiliares reutilizables
│   └── __init__.py         ← Application Factory (crea la app Flask)
├── venv/
├── config.py               ← Configuración de la app
├── index.py                ← Entry point
├── .gitignore
├── requirements.txt
└── README.md

- Con este formato y el uso de blueprints para separar las rutas y hacer el código más legible.

- Buenas prácticas DRY, y poner la lógica en funciones y en funciones dentro de clases si es necesario porque es una lógica más grande, el objetivo es código legible y mantenible.

- En partes complicadas un mínimo de documentación

## Manejo de errores

- Respuestas de error con formato JSON consistente: {error: "", code: ""}
- Errores de validación

## Convenciones de código

- PEP8 estricto en Python
- snake_case para variables y funciones
- PascalCase para clases
- Nombres en inglés en el código, español solo en comentarios si es necesario
- ¡SUPER IMPORTANTE! no pasarse de código, ir haciendo en pequeños pasos para que no me pierda y deje de entender el proyecto 80-100 caracteres por línea

## Decisiones cerradas (no reabrir)

- Sin React, Vue ni frameworks JS pesados
- Sin FastAPI ni Django, solo Flask
- Sin Docker en MVP (añadir en fase post-lanzamiento)
- Sin Redis en MVP salvo que sea estrictamente necesario
- ORM siempre SQLAlchemy, queries crudas si es necesario para optimización justificada
- Nunca me tiene que borrar comentarios propios, como mucho corregirmelos
- Siempre antes de elaborar un plan tiene que dejarme cambiar el modelo y no ejecutar directamente
- No quitarme comentarios personales, ni añadir comas inútiles
- Finalmente no cambiarme nada del formato que modifique, si he tocado formato o ñ en cualquier palabra NO MODIFICAR
