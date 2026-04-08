---
name: verneris-design
description: Diseño frontend específico para Verneris. Usar siempre que se modifique, cree o refactorice cualquier template HTML, componente visual, layout o estilo CSS de la aplicación.
---
 
# Verneris — Frontend Design Skill
 
## Contexto del producto
 
**Verneris** es una calculadora de presión de neumáticos para ciclistas. El usuario introduce parámetros de su bici (tipo de cubierta, peso, terreno, sistema tubeless/tubed) y recibe una presión recomendada, con correcciones físicas propias.
 
- **Usuario objetivo**: ciclista amateur-serio o enthusiast. Técnico, exigente, orientado a datos y rendimiento.
- **Flujo principal**: landing → registro/login → calculadora (formulario con inputs → resultado inmediato vía HTMX) → historial de cálculos guardados.
- **Producto hermano futuro**: SaaS de ingeniería eléctrica. El diseño de Verneris sienta las bases de la identidad visual de la marca.
 
---
 
## Stack técnico — restricciones de implementación
 
- **Templates**: Jinja2 (Flask). Cada página es un template HTML con herencia (`base.html`).
- **CSS**: TailwindCSS vía CDN. Clases utilitarias. Sin ficheros `.css` separados salvo para variables globales o animaciones que Tailwind no cubra.
- **JavaScript**: mínimo y vanilla. Sin React, Vue ni frameworks pesados.
- **Interactividad**: HTMX para swaps parciales de DOM. Los formularios principales usan `hx-post`, `hx-target`, `hx-swap`. Los partials devuelven fragmentos HTML, no páginas completas.
- **Iconos**: usar Heroicons SVG inline o Lucide via CDN si hace falta. No FontAwesome.
- **Fuentes**: Google Fonts via `<link>` en `base.html`.
- **Animaciones**: CSS puro preferido. JS solo si es imprescindible.
 
**Reglas de oro para HTMX**:
- Los errores de validación devuelven status 200 con el partial de error renderizado (no 4xx).
- El resultado de la calculadora se inyecta en un `div` con id específico (`#result-container` o similar).
- No romper el flujo HTMX añadiendo redirecciones o recargas de página completa donde antes había swaps.
 
---
 
## Identidad visual — Verneris Design System
 
### Dirección estética
 
**Referencia principal**: MyVeloFit — limpio, deportivo, jerarquía visual fuerte, uso del naranja como acento dominante sobre fondo blanco/gris muy claro.  
**Referencia secundaria**: Strava — datos como protagonistas, tipografía bold y confiada, sensación de rendimiento y comunidad.  
**Resultado**: interfaz deportiva de datos. No una app genérica. Cada página debe sentirse como una herramienta profesional para ciclistas serios.
 
### Paleta de colores
 
```css
:root {
  /* Primarios */
  --color-accent:        #F25C05;  /* naranja Verneris — CTA, highlights, activos */
  --color-accent-hover:  #D94F04;  /* naranja oscuro — hover states */
  --color-accent-light:  #FFF0E8;  /* naranja muy claro — fondos de badge, chips */
 
  /* Neutros base (fondo claro, modo light) */
  --color-bg:            #F8F8F7;  /* fondo general — blanco cálido, no puro */
  --color-surface:       #FFFFFF;  /* tarjetas, modales, formularios */
  --color-border:        #E5E3DF;  /* bordes sutiles */
  --color-border-strong: #C9C6C0;  /* bordes de inputs activos */
 
  /* Texto */
  --color-text-primary:  #1A1A18;  /* títulos y texto principal */
  --color-text-secondary:#6B6860;  /* labels, descripciones, meta */
  --color-text-muted:    #A8A5A0;  /* placeholders, disabled */
 
  /* Feedback */
  --color-success:       #16A34A;
  --color-error:         #DC2626;
  --color-warning:       #D97706;
}
```
 
### Tipografía
 
```
Display / Headings:  "Barlow Condensed" — bold, deportivo, compacto. Ideal para títulos de sección y hero.
Body / UI:           "DM Sans" — legible, moderno, no genérico. Para labels, párrafos, inputs.
Datos / Resultados:  "DM Mono" — para mostrar valores numéricos de presión (ej: "4.2 BAR"). Hace que los números tengan peso visual.
```
 
Google Fonts import (pegar en `<head>` de `base.html`):
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
```
 
### Espaciado y forma
 
- **Border-radius**: inputs y cards `rounded-xl` (12px). Botones primarios `rounded-full`. Badges `rounded-full`.
- **Sombras**: `shadow-sm` por defecto en cards. `shadow-md` en hover. Nunca `shadow-xl` en elementos de UI normales — reservado para modales.
- **Densidad**: media-alta. No dejar demasiado aire vacío pero tampoco saturar. Cada sección tiene un propósito claro.
 
---
 
## Componentes clave — patrones a respetar
 
### Botón primario (CTA)
```html
<button class="bg-[#F25C05] hover:bg-[#D94F04] text-white font-semibold px-6 py-3 rounded-full transition-all duration-200 text-sm tracking-wide">
  Calcular presión
</button>
```
 
### Botón secundario
```html
<button class="border border-[#E5E3DF] hover:border-[#F25C05] hover:text-[#F25C05] text-[#6B6860] font-medium px-6 py-3 rounded-full transition-all duration-200 text-sm">
  Ver historial
</button>
```
 
### Input de formulario
```html
<div class="flex flex-col gap-1.5">
  <label class="text-sm font-medium text-[#1A1A18]" for="weight">Peso del ciclista</label>
  <input 
    type="number" 
    id="weight" 
    name="weight"
    class="border border-[#E5E3DF] focus:border-[#F25C05] focus:ring-2 focus:ring-[#F25C05]/20 rounded-xl px-4 py-3 text-[#1A1A18] bg-white outline-none transition-all text-sm"
    placeholder="75"
  >
  <span class="text-xs text-[#A8A5A0]">kg</span>
</div>
```
 
### Resultado de presión (el momento más importante de la app)
```html
<div class="bg-[#1A1A18] rounded-2xl p-8 text-center">
  <p class="text-[#A8A5A0] text-sm font-medium uppercase tracking-widest mb-2">Presión recomendada</p>
  <p class="font-['DM_Mono'] text-6xl font-medium text-white">4.2</p>
  <p class="text-[#F25C05] text-xl font-semibold mt-1">BAR</p>
  <p class="text-[#6B6860] text-sm mt-4">Basado en tu configuración actual</p>
</div>
```
 
### Card de sección / módulo
```html
<div class="bg-white border border-[#E5E3DF] rounded-2xl p-6 hover:shadow-md transition-shadow duration-200">
  <!-- contenido -->
</div>
```
 
### Navbar
- Fondo blanco con `border-b border-[#E5E3DF]`.
- Logo en negro + acento naranja en el símbolo.
- Links en `text-[#6B6860]` → hover `text-[#1A1A18]`.
- CTA "Calcular" en botón naranja `rounded-full` a la derecha.
- Sticky en scroll.
 
### Flash messages / alertas
```html
<!-- Error -->
<div class="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
  <!-- icono heroicon -->
  Mensaje de error
</div>
 
<!-- Éxito -->
<div class="bg-[#F0FDF4] border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
  Guardado correctamente
</div>
```
 
---
 
## Páginas — estructura y notas específicas
 
### Landing (`/`)
- Hero con fondo `#1A1A18` (oscuro) o imagen ciclismo con overlay oscuro. Título grande en Barlow Condensed bold. CTA naranja prominente.
- Sección de features en 3 columnas sobre fondo `#F8F8F7`.
- Sin exceso de marketing — el ciclista serio valora la concisión.
 
### Calculadora (`/calculator`)
- Layout de dos columnas en desktop: formulario izquierda, resultado derecha (sticky).
- En mobile: formulario arriba, resultado abajo (HTMX swap in-place).
- El resultado debe ser el elemento más visualmente prominente de la página.
- Agrupar inputs por categoría (rueda delantera / trasera, condiciones) con separadores visuales claros.
 
### Auth (`/login`, `/register`)
- Centrado, fondo `#F8F8F7`, card blanca con `shadow-sm`.
- Formulario limpio y estrecho (max-w-md).
- OAuth buttons (Google) con iconos propios, borde gris, hover naranja.
 
### Historial (`/history`)
- Tabla o lista de cards. Cada entrada muestra: fecha, configuración resumida, presión resultado.
- Ordenado por fecha descendente.
- Acción "Cargar esta configuración" que rellena el formulario vía HTMX.

### Botón secundario — forma consistente con primario
- Los botones secundarios mantienen la misma forma que el primario (rounded-full,
mismo padding) pero en tono gris neutro. Nunca borde simple sobre fondo blanco.

- Regla: en Verneris solo existen dos tipos de botón — naranja (acción principal)
y gris (#E5E3DF, acción secundaria). Ningún botón con solo borde y fondo blanco.
 
---
 
## Lo que NO hacer
 
- ❌ No usar `Inter`, `Roboto`, `Arial` ni fuentes del sistema como tipografía principal.
- ❌ No gradientes morados, azules genéricos ni paletas "startup tech".
- ❌ No `shadow-xl` en cards normales — satura visualmente.
- ❌ No añadir JS donde HTMX ya cubre la interacción.
- ❌ No romper el flujo parcial de HTMX con `window.location.href` o recargas innecesarias.
- ❌ No usar clases Tailwind arbitrarias para colores que ya están en el design system — mantener consistencia.
- ❌ No centrar todo — la composición asimétrica es más deportiva y dinámica.
 
---
 
## Instrucciones de uso para Claude Code
 
Cuando modifiques o crees templates:
 
1. **Hereda siempre de `base.html`** — no crear páginas standalone.
2. **Usa las variables de color del design system** — si Tailwind no tiene la clase exacta, usa `text-[#F25C05]` con el valor del design system.
3. **El resultado de presión es el hero de la calculadora** — nunca lo hagas pequeño o secundario.
4. **Respeta los patrones de HTMX existentes** — no cambiar `hx-target`, `hx-swap` o IDs de contenedores sin revisar la ruta Flask correspondiente.
5. **Mobile-first** — el ciclista usa el móvil en el taller o antes de salir a rodar.
6. **Consistencia tipográfica**:
   - Títulos de página: Barlow Condensed 700, `text-3xl` mínimo.
   - Labels de formulario: DM Sans 500, `text-sm`.
   - Valores numéricos clave: DM Mono.
   - Body text: DM Sans 400.

- Es vital que no se rompa la sincronía que ya existe con el backend desde el frontend respetar esa parte.