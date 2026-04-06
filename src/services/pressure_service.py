import math

from flask import render_template, flash
from src.utils.pressure_constants import (
    RIM_TIRE_COMPATIBILITY, WHEEL_POSITION_FACTORS,
    CASING_FACTORS, RIDE_STYLE_FACTORS,
    RIM_TYPE_FACTORS_ROAD, SURFACE_FACTORS,
    TIRE_WIDTH_LIMITS, INNER_RIM_LIMITS,
    ALLOWED_DIAMETERS, REQUIRED_FIELDS,
    RIDE_STYLE_DEFAULTS,
    MAX_PRESSURE_BAR, PRESSURE_MIN_BAR
)



def to_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
    

def to_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def calcular_get():
    defaults = RIDE_STYLE_DEFAULTS.get("RIDE_STYLE_ROAD", {})
    return render_template("calculator/index.html", defaults=defaults)



def get_rim_ref(tire_width: float) -> float:   #Devuelve el aro de referencia para un ancho de cubierta dado
    for row in RIM_TIRE_COMPATIBILITY:
        if row["min"] <= tire_width < row["max"]:
            return row["rim_ref"]
    return 0.0  # fuera de rango — validate_inputs lo bloquea antes de llegar aquí, de todas formas hay que añadir capa



def get_rim_factor(rim_type: str) -> float:
    return RIM_TYPE_FACTORS_ROAD.get(rim_type, 1.0)




def validate_inputs(data: dict) -> list:
    errors = []

    # 1. Campos requeridos
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"El campo '{field}' es obligatorio.")

    if errors:
        return errors  # sin datos base no tiene sentido continuar
    

    # 2. Rangos numéricos
    rider_weight = data["rider_weight"]
    if not (20 <= rider_weight <= 200):
        errors.append(
            "El peso del ciclista no cumple el rango.")

    bike_weight = data["bike_weight"]
    if not (1 <= bike_weight <= 25):
        errors.append(
            "El peso de la bici no cumple el rango." )

    # 3. Enums válidos
    ride_style = data["ride_style"]
    if ride_style not in RIDE_STYLE_FACTORS:
        errors.append(f"Modalidad '{ride_style}' no válida.")   #Igual mejor mensajes flash

    tire_casing = data["tire_casing"]
    if tire_casing not in CASING_FACTORS:
        errors.append(f"Tipo de carcasa '{tire_casing}' no válido.")

    surface = data["surface"]
    if surface not in SURFACE_FACTORS:
        errors.append(f"Superficie '{surface}' no válida.")

    rim_type = data["rim_type"]
    if rim_type not in RIM_TYPE_FACTORS_ROAD:   #Mirar también para gravel
        errors.append(f"Tipo de aro '{rim_type}' no válido.")

    # 4. Ancho de cubierta — clave tupla primero, luego clave string
    tire_width = data["tire_width"]
    limit_key = (ride_style, rim_type)

    if limit_key in TIRE_WIDTH_LIMITS:
        limits = TIRE_WIDTH_LIMITS[limit_key]

    elif ride_style in TIRE_WIDTH_LIMITS:
        limits = TIRE_WIDTH_LIMITS[ride_style]

    else:
        limits = None

    if limits and not (limits["min"] <= tire_width <= limits["max"]):
        errors.append(
            f"Ancho de cubierta debe estar entre "
            f"{limits['min']} y {limits['max']} mm "
            f"para esta configuración.")


    # 5. Anchura interior del aro y creo que puede estar mal llega limit con None
    inner_rim_width = data["inner_rim_width"]
    if rim_type == "RIM_TYPE_TUBULAR":          #Revisar que no solo acepte 32mm de ancho
        rim_limits = INNER_RIM_LIMITS["RIM_TYPE_TUBULAR"]
        if inner_rim_width != rim_limits["min"]:
            errors.append(
                "Los aros tubulares tienen anchura interior fija de 32 mm.")
            
    else:
        rim_limits = INNER_RIM_LIMITS["DEFAULT_ROAD"]
        if not (rim_limits["min"] <= inner_rim_width <= rim_limits["max"]):
            errors.append(
                f"Anchura interior del aro debe estar entre "
                f"{rim_limits['min']} y {rim_limits['max']} mm.")

    # 6. Diámetro de rueda
    wheel_diameter = data["wheel_diameter"]
    if wheel_diameter not in ALLOWED_DIAMETERS:
        errors.append(
            f"Diámetro de rueda '{wheel_diameter}' no válido. "
            f"Valores permitidos: {sorted(ALLOWED_DIAMETERS)}.")

    return errors



def calculate_pressure(data: dict) -> dict:

    #Ya están validados los datos
    rider_weight = data["rider_weight"]
    bike_weight = data["bike_weight"]
    tire_width = data["tire_width"]
    inner_rim_width = data["inner_rim_width"]
    wheel_diameter = data["wheel_diameter"]
    tire_casing = data["tire_casing"]
    ride_style = data["ride_style"]
    rim_type = data["rim_type"]
    surface = data["surface"]

    # Paso 1: anchura efectiva según aro real vs aro de referencia
    ref_rim = get_rim_ref(tire_width)
    effective_width = tire_width + 0.4 * (inner_rim_width - ref_rim)

    # Se modela la cubierta como sección circular → toro perfecto   R = radio mayor (centro rueda → centro sección), r = radio menor
    R = wheel_diameter / 2 + effective_width / 2
    r = effective_width / 2
    torus_area = 4 * math.pi ** 2 * R * r  # en mm²

    # Paso 3: factor de peso normalizado respecto al valor de referencia 180
    total = 2.2 * (bike_weight + rider_weight)
    weight_factor = 1 + (total - 180) * 0.0025

    # Paso 4: factores correctores comunes a ambas ruedas
    rim_factor = get_rim_factor(rim_type)
    style_factor = RIDE_STYLE_FACTORS[ride_style]
    surf_factor = SURFACE_FACTORS[surface]
    cas_factor = CASING_FACTORS[tire_casing]

    results = {}
    for position, key in [("WHEEL_FRONT", "front"), ("WHEEL_REAR", "rear")]:
        wheel_factor = WHEEL_POSITION_FACTORS[position]

        # Paso 5: presión base (modelo empírico SRAM/Zipp)
        # Coeficientes 8.684670773 y -1.304556655 NO modificar — calibrados
        pressure_psi = (
            10 ** 8.684670773
            * torus_area ** -1.304556655
            * weight_factor
            * wheel_factor
            * rim_factor
            * style_factor
            * surf_factor
            * cas_factor
        )
        bar = pressure_psi / 14.5038
        results[key] = {
            "bar": round(bar, 2),
            "psi": round(pressure_psi, 2),
        }

    return results



def check_pressure_warnings(
    result: dict,
    rim_type: str,
    ride_style: str
) -> None:
    """Lanza flash warnings si alguna rueda cae fuera del rango seguro.
    - Por debajo del mínimo → riesgo de pellizco
    - Por encima del máximo del aro → riesgo de reventón
    """
    min_bar = PRESSURE_MIN_BAR.get(ride_style)
    rim_max = MAX_PRESSURE_BAR.get(rim_type, {})

    posiciones = [
        ("front", "WHEEL_FRONT", "delantera"),
        ("rear",  "WHEEL_REAR",  "trasera"),
    ]

    for key, pos_key, label in posiciones:
        bar = result[key]["bar"]

        if min_bar is not None and bar < min_bar:
            flash(
                f"Presión {label} ({bar} bar) muy baja para esta "
                f"configuración. Mínimo recomendado: {min_bar} bar.",
                "warning"
            )

        max_bar = rim_max.get(pos_key)
        if max_bar is not None and bar > max_bar:
            flash(
                f"Presión {label} ({bar} bar) supera el límite del "
                f"aro ({max_bar} bar). Considera una cubierta más ancha.",
                "warning"
            )
