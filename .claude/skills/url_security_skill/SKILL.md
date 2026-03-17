---
name: url_security_skill
description: Apply this skill whenever the user works with external inputs in Flask: URL parameters, form fields, file uploads, query strings, or any data entering the system from outside. The goal is to validate and sanitize before use, never after.
---


# SKILL: Input Sanitization & Validation (Flask + Python)



## CORE PRINCIPLE
**Never trust external input. Validate structure, sanitize content, reject everything else.**

External inputs include:
- `request.args`, `request.form`, `request.json`, `request.files`
- URL parameters (`?next=`, `?redirect=`, `?file=`)
- File names from uploads
- Any string that will touch the filesystem, database, or redirect logic



## 1. OPEN REDIRECT — Validating `next` URLs

### Attack vector
An attacker crafts a URL like `?next=https://evil.com` or `?next=javascript:alert(1)` to hijack post-login redirects.

### Validation rules (in order)
1. Reject `None` or empty values first
2. Reject if length > 2048 characters
3. Parse with `urlparse()` — catch `ValueError`
4. Reject if `scheme` is in a blocklist (`http`, `https`, `javascript`, etc.)
5. Reject if `netloc` is present (any external domain = dangerous)
6. Reject if `scheme` is present but `netloc` is empty (e.g. `example.com` parsed as scheme)
7. Reject if path starts with `//` (protocol-relative URL)
8. Only allow paths starting with `/` (relative, internal routes)

### Reference implementation
```python
from urllib.parse import urlparse

def validar_next(url_completa_next):
  """
        Valida que una URL `next` sea segura para redirección interna.
        Devuelve la URL limpia si es válida, False en caso contrario.
  """

    scheme_malignos = ["http", "https", "javascript", "data", "vbscript", "file"]
    extensiones_dominio_maligno = [
        "com", "es", "io", "dev", "mx", "net", "org",
        "info", "xyz", "co", "ai", "app", "tech", "dio"
    ]

    if not url_completa_next:
        return False

    if len(url_completa_next) > 2048:
        return False

    try:
        url_trozeada = urlparse(url_completa_next, allow_fragments=True)
    except ValueError:
        return False

    scheme = url_trozeada.scheme
    netloc = url_trozeada.netloc
    path   = url_trozeada.path

    if scheme in scheme_malignos:
        return False

    # scheme presente pero netloc vacío → Chrome lo interpreta como hostname
    if scheme or netloc:
        return False

    # Rutas tipo C:\... o similares no son rutas relativas web
    if url_trozeada[0] != "":
        if url_trozeada[0][0] == "C":
            return False


    # Solo permitir rutas internas absolutas: /ruta/valida
    if path.startswith("/") and not path.startswith("//"):
        return url_completa_next

    return False
```

### Flask usage pattern
```python
next_raw   = request.args.get("next") or request.form.get("next")
next_limpio = validar_next(next_raw)

if not next_limpio:
    return redirect(url_for("home.index"))

return redirect(next_limpio)
```

**Key**: pass the raw string, never trust it before validation. Use `next_limpio`, never `next_raw`.

---

## 2. FILE UPLOAD — Validating image names and extensions

### Attack vector
An attacker uploads `shell.php`, `malware.exe`, or `image.png.php` to execute code server-side or serve malicious content.

### Validation rules
1. Filename must contain at least one `.`
2. Count all dots — use the **last segment** as the real extension (prevents `image.png.php` bypass)
3. Normalize: lowercase + strip whitespace
4. Check extension against an **explicit allowlist** (not a blocklist)
5. Return a clean, normalized filename for storage

### Reference implementation
```python
import re
CHARS_PELIGROSOS = re.compile(r'[\\/<>:"|?*\x00]')

def img_normalizada(img_nombre, numero):
    formato_nombre = img_nombre.split(".")[numero].lower().strip()
    img_limpio     = img_nombre.lower().strip()
    return formato_nombre, img_limpio

def validar_imagen(img_nombre, formatos):

  if not img_nombre or not isinstance(img_nombre, str):
    return False, None, None

  if len(img_nombre) > 255:
        return False, None, None

  if "." not in img_nombre:
    return False, None, None

  if CHARS_PELIGROSOS.search(img_nombre):
        return False, None, None

  puntos = img_nombre.count(".")
  formato_imagen, img_limpio = img_normalizada(img_nombre, puntos)

  if formato_imagen in formatos:
      return True, img_limpio, formato_imagen

  return False, None, None
```

### Flask usage pattern
```python
#En la ruta o donde se vaya hacer la llamada a la función de saneamineto
FORMATOS_PERMITIDOS = {"jpg", "jpeg", "png", "webp"}
import uuid

archivo = request.files.get("imagen")
if not archivo or not archivo.filename:
    abort(400)

es_valida, nombre_limpio, extension = validar_imagen(archivo.filename, FORMATOS_PERMITIDOS)

if not es_valida:
    abort(415)  # Unsupported Media Type

# Nunca usar nombre_limpio directamente como ruta final
# Generar un nombre seguro propio:
import uuid
nombre_final = f"{uuid.uuid4().hex}.{extension}"
archivo.save(os.path.join(UPLOAD_FOLDER, nombre_final))
```

**Key**: even after validation, never use the original filename as the storage path. Generate a UUID-based name.

---

## 3. SQL INJECTION — ORM-first approach

### Attack vector
Concatenating user input into raw SQL strings: `f"SELECT * FROM users WHERE email = '{email}'"`.

### Rules
- **Always use parameterized queries or ORM methods**
- Never use f-strings or `.format()` to build SQL
- If using raw SQL with `psycopg2`, use `%s` placeholders

```python
# WRONG — SQL injection risk
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

# CORRECT — parameterized
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# CORRECT — with SQLAlchemy ORM
user = User.query.filter_by(email=email).first()
```

---

## 4. GENERAL INPUT RULES FOR FLASK

Apply these consistently across all routes:

| Input type         | Action                                              |
|--------------------|-----------------------------------------------------|
| URL `next` param   | `validar_next()` → reject if False                  |
| File name          | `validar_imagen()` → rename with UUID on save       |
| Text fields        | Strip whitespace, enforce max length, type-check    |
| Numeric fields     | Cast with `int()` / `float()` inside `try/except`   |
| Email fields       | Use `re` or a library like `email-validator`        |
| Raw SQL            | Never — use ORM or parameterized queries            |

---

## 5. WHAT CLAUDE SHOULD DO WHEN APPLYING THIS SKILL

- If a route receives `request.args` or `request.form` with a `next`, `redirect`, or URL-like parameter → apply `validar_next()` pattern
- If a route handles file uploads → apply `validar_imagen()` + UUID rename
- If raw SQL strings appear → refactor to ORM or parameterized queries
- If user text is rendered back into HTML → confirm Jinja2 autoescaping is active
- Always validate **at the entry point of the route**, before any business logic
- Return early (`abort()` or `redirect()`) on invalid input — do not attempt to "fix" malicious input

---

## NOTES
- These patterns are designed for a **Flask + Python + PostgreSQL** stack
- Prioritizes explicitness and control over magic — consistent with the project's architectural philosophy
- Allowlists > blocklists wherever possible (safer by default)
- It is very important follow the previous skills that were defined in [revise_refactor_code](../revise_refactor_code/SKILL.md) and USE ONLY the stack that I mentioned in CLAUDE.md if changes are important you should bear in mind testing changes, to prove the code works properly.
- Try always to IMPROVE the code WITHOUT LOSING LEGIBILITY in the code.