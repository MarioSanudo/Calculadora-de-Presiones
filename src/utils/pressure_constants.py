# Tabla de compatibilidad aro/cubierta (origen SRAM), añadir de más fabricantes
RIM_TIRE_COMPATIBILITY = [
    {"rim_ref": 15, "min": 18,  "max": 22},
    {"rim_ref": 17, "min": 22,  "max": 25},
    {"rim_ref": 19, "min": 25,  "max": 29},   # 28mm carretera cae aquí
    {"rim_ref": 21, "min": 29,  "max": 35},
    {"rim_ref": 23, "min": 35,  "max": 47},   # gravel 40mm cae aquí
    {"rim_ref": 25, "min": 47,  "max": 58},
    {"rim_ref": 30, "min": 58,  "max": 66},
    {"rim_ref": 35, "min": 66,  "max": 72},
    {"rim_ref": 45, "min": 72,  "max": 84},
    {"rim_ref": 55, "min": 84,  "max": 96},
    {"rim_ref": 76, "min": 96,  "max": 113},
    {"rim_ref": 94, "min": 114, "max": 133},  # fat bike
]

WHEEL_POSITION_FACTORS = {
    "WHEEL_FRONT": 0.94,
    "WHEEL_REAR":  1.00,
}

CASING_FACTORS = {
    "TIRE_CASING_DOUBLE":     0.90,   # Doble ply / DH — muy resistente
    "TIRE_CASING_REINFORCED": 0.95,   # Reforzada
    "TIRE_CASING_STANDARD":   1.00,   # Estándar — referencia
    "TIRE_CASING_THIN":       1.025,  # Ligera — más presión para compensar
}

RIDE_STYLE_FACTORS = {
    "RIDE_STYLE_ROAD":   1.00,   # Carretera — referencia
    "RIDE_STYLE_GRAVEL": 0.90,   # Gravel — menos presión para tracción
}

RIM_TYPE_FACTORS_ROAD = {
    "RIM_TYPE_TUBULAR":           1.10,    # Pegado — históricamente más presión
    "RIM_TYPE_TUBES":             1.05,    # Con cámara
    "RIM_TYPE_TUBELESS_CROCHET":  1.03,    # Tubeless gancho
    "RIM_TYPE_TUBELESS_STRAIGHT": 0.955,   # Tubeless straight side (hookless)
}

SURFACE_FACTORS = {
    "SURFACE_DRY":  1.00,
    "SURFACE_WET":  0.90,   # Mojado — menos presión para más área de contacto
    "SURFACE_SNOW": 0.50,   # Nieve — presión muy baja para flotación
}

# Rangos de ancho de cubierta válidos por modalidad.
# La clave tupla (modalidad, tipo_aro) tiene prioridad sobre la clave string.
TIRE_WIDTH_LIMITS = {
    # Caso especial: carretera + tubeless gancho → rango más restrictivo
    ("RIDE_STYLE_ROAD", "RIM_TYPE_TUBELESS_CROCHET"): {
        "min": 28, "max": 50
    },
    "RIDE_STYLE_ROAD":   {"min": 18, "max": 65},
    "RIDE_STYLE_GRAVEL": {"min": 28, "max": 65}
}

INNER_RIM_LIMITS = {
    "RIM_TYPE_TUBULAR": {"min": 32, "max": 32},  # fijo — tubulares siempre 32mm
    "DEFAULT_ROAD":     {"min": 15, "max": 50},
    "DEFAULT_MTB":      {"min": 15, "max": 100},
}

# Valores pre-rellenados al seleccionar una modalidad en el formulario
RIDE_STYLE_DEFAULTS = {
    "RIDE_STYLE_ROAD": {
        "inner_rim_width": 23,
        "rim_type":        "RIM_TYPE_TUBELESS_CROCHET",
        "wheel_diameter":  622,
        "tire_width":      28,
        "tire_casing":     "TIRE_CASING_STANDARD",
        "bike_weight":     8,
    },
    "RIDE_STYLE_GRAVEL": {
        "inner_rim_width": 25,
        "rim_type":        "RIM_TYPE_TUBELESS_CROCHET",
        "wheel_diameter":  622,
        "tire_width":      40,
        "tire_casing":     "TIRE_CASING_STANDARD",
        "bike_weight":     11,
    }
}

# Diámetros permitidos: 622=700c, 584=650b, 559=26", 571=27.5"
ALLOWED_DIAMETERS = {559, 571, 584, 622}

REQUIRED_FIELDS = [
    "rider_weight", "bike_weight", "tire_width",
    "inner_rim_width", "wheel_diameter",
    "tire_casing", "ride_style", "rim_type", "surface"]
