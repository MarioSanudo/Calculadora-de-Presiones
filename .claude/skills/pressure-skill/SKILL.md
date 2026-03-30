---
name: pressure-skill
description:
  Usar siempre que se trabaje en el módulo de cálculo de presión,
  se añadan nuevas modalidades, se modifiquen factores.
---

# Cálculo de Presión de Neumáticos — Verneris

## Objetivo
Crear el script de código de la calculadora de presiones, y los posibles cambios que este módulo vaya sufriendo, irá ligado con cambios en el esquema de la base de dayos para así poder guardar un historial de calculos con diferentes bicicletas o con el mismo modelo pero diferentes configuraciones.


## La fórmula core

```python
import math

def calcular_presion(
    rider_weight: float,     # kg — peso del ciclista
    bike_weight: float,      # kg — peso de la bici
    tire_width: float,       # mm — ancho nominal de la cubierta
    inner_rim_width: float,  # mm — anchura interior del aro
    wheel_diameter: float,   # mm — diámetro (622=700c, 584=650b, 559=29", 571=27.5")
    wheel_position: str,     # "WHEEL_FRONT" | "WHEEL_REAR"
    tire_casing: str,        # ver tabla CASING_FACTORS
    ride_style: str,         # ver tabla RIDE_STYLE_FACTORS
    rim_type: str,           # ver tabla RIM_TYPE_FACTORS
    surface: str,            # "SURFACE_DRY" | "SURFACE_WET" | "SURFACE_SNOW"
) -> dict:                   # {"bar": float, "psi": float}
    
    # PASO 1: Anchura efectiva
    # El mismo neumático se abre más o menos según el aro.
    # El aro de referencia para cada ancho viene de la tabla CF5.
    default_rim = _compatible_rim_width(tire_width)
    effective_width = tire_width + 0.4 * (inner_rim_width - default_rim)
    

    # PASO 2: Área del toro (proxy del volumen de aire)
    # Se modela la cubierta como sección circular → toro perfecto.
    # Fórmula: A = 4π² × R × r
    # R = radio mayor (centro rueda → centro sección cubierta)
    # r = radio menor (radio de la sección = effective_width / 2)
    R = wheel_diameter / 2 + effective_width / 2
    r = effective_width / 2
    torus_area = 4 * math.pi**2 * R * r  # en mm²

    # PASO 3: Factor de peso
    # Normaliza el peso total del sistema respecto a un valor de referencia (180).
    # El 2.2 convierte kg → unidad interna de la fórmula (no es lb, es escala propia).
    # Peso < referencia → factor < 1 → menos presión necesaria.
    total = 2.2 * (bike_weight + rider_weight)
    weight_factor = 1 + (total - 180) * 0.0025

    # PASO 4: Factor por posición de rueda
    # Delantera lleva ~40-45% del peso total → necesita menos presión.
    wheel_factor = WHEEL_POSITION_FACTORS[wheel_position]

    # PASO 5: Presión base (modelo empírico SRAM/Zipp)
    # Forma: P = 10^k × A^n × factores
    # Los coeficientes 8.684670773 y -1.304556655 son resultado de regresión
    # sobre mediciones reales. NO modificar — están calibrados para mm².

    pressure_psi = (
        10 ** 8.684670773
        * torus_area ** -1.304556655
        * weight_factor
        * wheel_factor
    )

    # PASO 6: Multiplicadores correctores
    # Se aplican en orden — todos son factores ×, no sumandos.
    rim_factor     = _get_rim_factor(ride_style, rim_type)
    pressure_psi  *= rim_factor
    pressure_psi  *= RIDE_STYLE_FACTORS[ride_style]
    pressure_psi  *= SURFACE_FACTORS[surface]
    pressure_psi  *= CASING_FACTORS[tire_casing]

    bar = pressure_psi / 14.5038
    return {
        "bar": round(bar, 2),          # unidad principal en Verneris
        "psi": round(pressure_psi, 2), # unidad secundaria
    }


def _get_rim_factor(ride_style: str, rim_type: str) -> float:
    """MVP: solo road/gravel → siempre RIM_TYPE_FACTORS_ROAD.
    La rama CROSS existe para cuando se añada ciclocross (tubular baja presión)."""
    if ride_style == "RIDE_STYLE_CROSS":
        return RIM_TYPE_FACTORS_CROSS.get(rim_type, 1.0)
    return RIM_TYPE_FACTORS_ROAD.get(rim_type, 1.0)
```

---

## Tablas de factores

### Posición de rueda
```python
WHEEL_POSITION_FACTORS = {
    "WHEEL_FRONT": 0.94,
    "WHEEL_REAR":  1.00,
}
```

### Tipo de carcasa (tireCasing)
```python
CASING_FACTORS = {
    "TIRE_CASING_DOUBLE":      0.90,   # Doble ply / DH — muy resistente, baja presión
    "TIRE_CASING_REINFORCED":  0.95,   # Reforzada
    "TIRE_CASING_STANDARD":    1.00,   # Estándar — referencia
    "TIRE_CASING_THIN":        1.025,  # Ligera — más presión para compensar rigidez menor

    # Cubiertas Goodyear específicas (incluir si se añaden al catálogo):
    # "TIRE_CASING_GY_INTER":    1.00,
    # "TIRE_CASING_GY_NSW":      1.025,
    # "TIRE_CASING_XPLR_SLICKS": 1.00,
}
```

### Modalidad (rideStyle)
```python
RIDE_STYLE_FACTORS = {
    "RIDE_STYLE_ROAD":         1.00,   # Carretera — referencia
    "RIDE_STYLE_GRAVEL":       0.90,   # Gravel — menos presión para confort/tracción

# FUERA MVP —     "RIDE_STYLE_CROSS":        0.60,   # Ciclocross — presiones muy bajas (barro)
# FUERA MVP —     "RIDE_STYLE_XCOUNTRY_MTB": 0.90,
# FUERA MVP —     "RIDE_STYLE_TRAIL_MTB":    1.05,
# FUERA MVP —     "RIDE_STYLE_ENDURO_MTB":   1.05,
# FUERA MVP —     "RIDE_STYLE_DOWNHILL_MTB": 1.10,
# FUERA MVP —     "RIDE_STYLE_FAT":          1.00,
}
```

### Tipo de llanta — Carretera/Gravel/MTB
```python
RIM_TYPE_FACTORS_ROAD = {
    "RIM_TYPE_TUBULAR":             1.10,   # Pegado — históricamente más presión
    "RIM_TYPE_TUBES":               1.05,   # Con cámara
    "RIM_TYPE_TUBELESS_CROCHET":    1.03,   # Tubeless gancho
    "RIM_TYPE_303_XPLR":            0.9675, # Llanta Zipp 303 XPLR específica
    "RIM_TYPE_TUBELESS_STRAIGHT":   0.955,  # Tubeless straight side (hookless)
}
```

### Superficie
```python
SURFACE_FACTORS = {
    "SURFACE_DRY":  1.00,
    "SURFACE_WET":  0.90,   # Mojado — menos presión para más área de contacto
    "SURFACE_SNOW": 0.50,   # Nieve — presión muy baja para flotación
}
```

---

## Tabla de compatibilidad aro/cubierta (CF5)

Determina el **aro de referencia** para un ancho de cubierta dado.
Origen: SRAM. Reemplazar progresivamente por tabla ETRTO oficial.

```python
CF5 = [
    {"compatible_rim": 15,  "min": 18,   "max": 22},
    {"compatible_rim": 17,  "min": 22,   "max": 25},
    {"compatible_rim": 19,  "min": 25,   "max": 29},   # ← 28mm road cae aquí
    {"compatible_rim": 21,  "min": 29,   "max": 35},
    {"compatible_rim": 23,  "min": 35,   "max": 47},   # ← gravel 40mm cae aquí
    {"compatible_rim": 25,  "min": 47,   "max": 58},
    {"compatible_rim": 30,  "min": 58,   "max": 66},
    {"compatible_rim": 35,  "min": 66,   "max": 72},
    {"compatible_rim": 45,  "min": 72,   "max": 84},
    {"compatible_rim": 55,  "min": 84,   "max": 96},
    {"compatible_rim": 76,  "min": 96,   "max": 113},
    {"compatible_rim": 94,  "min": 114,  "max": 133},  # ← fat bike
]

def _compatible_rim_width(tire_width: float) -> float:
    for row in CF5:
        if row["min"] <= tire_width < row["max"]:
            return row["compatible_rim"]
    return 0  # fuera de rango → edge case, tratar antes de llegar aquí
```

---

## Límites de validación por modalidad (jT)

Rango de ancho de cubierta que acepta la UI por modalidad.
Si el usuario introduce un valor fuera de rango → error de validación,
no calcular.

```python
TIRE_WIDTH_LIMITS = {
    # Caso especial: road + tubeless crochet → rango más restrictivo
    ("RIDE_STYLE_ROAD", "RIM_TYPE_TUBELESS_CROCHET"): {"min": 28, "max": 50},

    # Por modalidad (resto de combinaciones):
    "RIDE_STYLE_ROAD":         {"min": 18,  "max": 65},
    # FUERA MVP —     "RIDE_STYLE_CROSS":        {"min": 28,  "max": 40},
    "RIDE_STYLE_GRAVEL":       {"min": 28,  "max": 65},
    # FUERA MVP —     "RIDE_STYLE_XCOUNTRY_MTB": {"min": 2.0, "max": 3.8},  # pulgadas
    # FUERA MVP —     "RIDE_STYLE_TRAIL_MTB":    {"min": 2.0, "max": 3.8},
    # FUERA MVP —     "RIDE_STYLE_ENDURO_MTB":   {"min": 2.0, "max": 3.8},
    # FUERA MVP —     "RIDE_STYLE_DOWNHILL_MTB": {"min": 2.0, "max": 3.8},
    # FUERA MVP —     "RIDE_STYLE_FAT":          {"min": 3.8, "max": 5.0},
}
```

# Nota MTB (fuera MVP): cubiertas MTB van en pulgadas — convertir con 1" = 25.4mm al añadir esas modalidades.
en mm (28mm). Verneris debe detectar la unidad por modalidad y convertir
internamente a mm antes de calcular (1" = 25.4mm).

---

## Límites de anchura interior del aro (bf5)

```python
INNER_RIM_LIMITS = {
    "RIM_TYPE_TUBULAR":  {"min": 32, "max": 32},  # fijo — los tubulares son 32mm
    "DEFAULT_ROAD":      {"min": 15, "max": 50},
    "DEFAULT_MTB":       {"min": 15, "max": 100},
}
```

---

## Warnings y edge cases

### Incompatibilidad aro/cubierta
```
Condición: tire_width fuera del rango min/max de CF5 para ese inner_rim_width
Mensaje:   "Ancho de cubierta incompatible con el aro seleccionado"
Acción:    Bloquear cálculo, sugerir cubierta más ancha o aro más estrecho
```

### Presión excesiva para el aro
```
Condición: presión calculada supera el rating máximo del aro
Mensaje:   "Presión sugerida supera el límite del aro. Selecciona una cubierta más ancha"
Acción:    Mostrar resultado con warning visible, no bloquear
Pendiente: Definir tabla de ratings por tipo de llanta
```

### Incompatibilidad tipo llanta / tipo cubierta
```
Condición: combinaciones inválidas (ej: cubierta tubeless en aro de tubular)
Acción:    Mostrar warning, no bloquear
```

### Validación global antes de calcular
Todos estos campos deben estar presentes y válidos:
- `rider_weight` > 0 en rangos realistas (el peso permite valores bajos porque tambiñen puede ser usadas por padres para sus hijos)
- `bike_weight` > 0 en rango realistas (a partir de 5kg mas o menos hasta 20kg que pese como mucho yo creo)
- `tire_width` dentro de TIRE_WIDTH_LIMITS para la modalidad
- `inner_rim_width` dentro de INNER_RIM_LIMITS para el rim_type
- `wheel_diameter` en lista permitida para la modalidad
- `rim_type`, `tire_casing`, `ride_style`, `surface` en sus respectivas listas

---

## Defaults por modalidad

Valores pre-rellenados cuando el usuario selecciona una modalidad.

```python
RIDE_STYLE_DEFAULTS = {
    "RIDE_STYLE_ROAD": {
        "inner_rim_width": 23,
        "rim_type":        "RIM_TYPE_TUBELESS_CROCHET",
        "wheel_diameter":  622,
        "tire_width":      28,
        "tire_casing":     "TIRE_CASING_STANDARD",
        "bike_weight":     6.5,
    },
    "RIDE_STYLE_GRAVEL": {
        "inner_rim_width": 25,
        "rim_type":        "RIM_TYPE_TUBELESS_CROCHET",
        "wheel_diameter":  622,
        "tire_width":      40,
        "tire_casing":     "TIRE_CASING_STANDARD",
        "bike_weight":     9.0,
    },
    # FUERA MVP —     "RIDE_STYLE_TRAIL_MTB": {
    # FUERA MVP —         "inner_rim_width": 30,
    # FUERA MVP —         "rim_type":        "RIM_TYPE_TUBELESS_CROCHET",
    # FUERA MVP —         "wheel_diameter":  622,
    # FUERA MVP —         "tire_width":      2.4,  # pulgadas → convertir a mm al calcular
    # FUERA MVP —         "tire_casing":     "TIRE_CASING_STANDARD",
    # FUERA MVP —         "bike_weight":     11.8,
    # FUERA MVP —     },
}
```

---

## Verificación rápida (caso base)

```
Inputs:  60kg ciclista, 8kg bici, 28mm, aro 23mm interno, 700c (622mm),
         carretera, seco, cámara (tubes), carcasa standard

Resultado esperado:
  Delantera: ~57.2 PSI / 3.94 bar
  Trasera:   ~60.8 PSI / 4.19 bar

Pasos intermedios:
  effective_width = 28 + 0.4 × (23 - 19) = 29.60 mm
  torus_area      = 4π² × 325.80 × 14.80 = 190.358 mm²
  weight_factor   = 1 + (149.6 - 180) × 0.0025 = 0.924
  presión base    = 10^8.6847 × 190358^-1.3046 × 0.924 × [0.94|1.0]
  × 1.05 (tubes) × 1.0 (road) × 1.0 (dry) × 1.0 (standard)
```

---

## ACLARACIONES MUY IMPORTANTES!!
- Las variables que se van a mostrar en el frontend mejor que sean en español, a parte hay nombres como c5 poco legibles, cambiarlo como siempre siguiendo el formato de CLAUDE.md pero con nombres intuitivos.