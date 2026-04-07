# Tabla de compatibilidad aro/cubierta (origen SRAM), de carácter general
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
    {"rim_ref": 94, "min": 114, "max": 133}  # fat bike
]

#Tabla de compatibilidad de Vittoria Hook y Hookless (clincher)
RIM_TIRE_COMPATIBILITY_VITTORIA= [
    {"rim_ref": 17, "min":22, "max": 24},
    {"rim_ref": 19, "min":25, "max": 28},
    {"rim_ref": 21, "min":29, "max": 34},
    {"rim_ref": 23, "min":35, "max": 46},
    {"rim_ref": 25, "min":47, "max": 57},
    {"rim_ref": 30, "min":58, "max": 65},
    {"rim_ref": 35, "min":66, "max": 71},
    {"rim_ref": 45, "min":72, "max": 83}
]

RIM_TIRE_COMPATIBILITY_SCHWALBE = [
    {"rim_ref": 15, "min": 18,  "max": 25},
    {"rim_ref": 17, "min": 22,  "max": 28},
    {"rim_ref": 19, "min": 25,  "max": 32},
    {"rim_ref": 21, "min": 28,  "max": 40},
    {"rim_ref": 23, "min": 35,  "max": 50},
    {"rim_ref": 25, "min": 42,  "max": 62},
    {"rim_ref": 30, "min": 55,  "max": 70},
    {"rim_ref": 35, "min": 62,  "max": 80},
    {"rim_ref": 45, "min": 70,  "max": 90}
]

# Mapeo marca → tabla de compatibilidad aro/cubierta
TIRE_BRAND_COMPATIBILITY = {
    "TIRE_BRAND_GENERAL":  RIM_TIRE_COMPATIBILITY,
    "TIRE_BRAND_VITTORIA": RIM_TIRE_COMPATIBILITY_VITTORIA,
    "TIRE_BRAND_SCHWALBE": RIM_TIRE_COMPATIBILITY_SCHWALBE,
}

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
    "DEFAULT_MTB":      {"min": 15, "max": 100}
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

ALTITUDE_LIMITS = {"min": 0, "max": 4500}  # metros sobre el nivel del mar

REQUIRED_FIELDS = [
    "rider_weight", "bike_weight",
    "tire_width_front", "tire_width_rear",
    "inner_rim_width", "wheel_diameter",
    "tire_casing", "ride_style", "rim_type", "surface",
    "altitude"]


MAX_PRESSURE_BAR = {
    "RIM_TYPE_TUBELESS_STRAIGHT": {"WHEEL_FRONT": 4.8, "WHEEL_REAR": 5.0},
    "RIM_TYPE_TUBELESS_CROCHET":  {"WHEEL_FRONT": 6.5, "WHEEL_REAR": 6.9},
    "RIM_TYPE_TUBES":             {"WHEEL_FRONT": 7.5, "WHEEL_REAR": 8.3},
    "RIM_TYPE_TUBULAR":           {"WHEEL_FRONT": 8.0, "WHEEL_REAR": 8.5}
}


PRESSURE_MIN_BAR = {
    "RIDE_STYLE_ROAD":   3.5,   # por debajo → riesgo de pellizco
    "RIDE_STYLE_GRAVEL": 1.8,   # tubeless aguanta presiones más bajas
}