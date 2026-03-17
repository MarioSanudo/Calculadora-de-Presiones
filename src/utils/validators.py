from urllib.parse import urlparse


# Schemes que no deben aparecer en URLs internas de redirección
_SCHEMES_BLOQUEADOS = {
    "http", "https", "javascript", "data", "vbscript", "file"
}


def validar_next(url_next):
    """
    Valida que una URL `next` sea segura para redirección interna.
    Solo permite rutas relativas internas tipo /ruta/valida.
    Devuelve la URL si es válida, False en caso contrario.
    """
    if not url_next or not isinstance(url_next, str):
        return False

    if len(url_next) > 2048:
        return False

    try:
        parsed = urlparse(url_next)
    except ValueError:
        return False

    # Rechazar si tiene scheme (http/https/javascript...) o dominio externo
    if parsed.scheme in _SCHEMES_BLOQUEADOS:
        return False

    if parsed.scheme or parsed.netloc:
        return False

    # Solo rutas internas absolutas: /ruta — no protocol-relative //ruta
    if parsed.path.startswith("/") and not parsed.path.startswith("//"):
        return url_next

    return False
