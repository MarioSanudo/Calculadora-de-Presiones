---
name: verneris-layout
description: Usar cuando se modifique estructura, layout o maquetación de templates en Verneris. NO usar para cambios de color, tipografía o estilos — para eso está verneris-design.
---

## Estructura y Layout — Directrices globales

### Filosofía de maquetación
Las páginas de Verneris no son formularios flotantes en el vacío. Cada página tiene
profundidad: secciones con propósito, imágenes reales, contexto. El usuario debe
sentir que está en un producto serio, no en un prototipo.

### Imágenes
- Usar siempre URLs reales de Unsplash de ciclismo: ruedas, carretera, cubiertas,
  válvulas, ciclistas en acción.
- Formato: `https://images.unsplash.com/photo-ID?w=1200&q=80`
- Nunca placeholders grises ni divs vacíos como sustituto de imagen.
- Las imágenes de fondo llevan siempre overlay oscuro (`bg-black/50` mínimo)
  para garantizar legibilidad del texto encima.

### Layouts por página

**Landing (`/`)**
Estructura de secciones en orden obligatorio:
1. Hero — fondo oscuro, texto izquierda, imagen derecha, CTA naranja
2. Cómo funciona — 3 pasos, fondo #F8F8F7
3. Imagen inmersiva — ancho completo, overlay + frase
4. Sobre el proyecto — 2 columnas: texto + imagen detalle cubierta
5. CTA final — franja naranja ancho completo

**Login / Register (`/login`, `/register`)**
- Desktop: 2 columnas. Izquierda 40% formulario, derecha 60% imagen ciclista
  con overlay y frase motivacional.
- Mobile: solo el formulario. La imagen desaparece (`hidden md:block`).
- El formulario interior (campos, ids, names, hx-*, action, method) es intocable.

**Calculadora (`/calculator`)**
- Formulario ancho: `max-w-2xl` mínimo, centrado.
- Inputs agrupados en grid de 2 columnas donde aplique.
- Resultado SIEMPRE debajo del formulario, nunca al lado, y que no haya que desplazarse para abajo para poder ver el resultado pierde sencillez.
- Bloque resultado: fondo `#1A1A18`, número DM Mono grande, acento naranja.

### Regla absoluta de HTMX
Antes de modificar cualquier template, listar explícitamente todos los atributos
`hx-post`, `hx-get`, `hx-target`, `hx-swap`, `hx-trigger`, IDs de contenedores
target y `name` de inputs del formulario. Ninguno de estos puede cambiar.
El layout que los rodea sí puede cambiar. Ellos, no.


## Sección "Sobre el proyecto" — Contenido y footer

### Sobre mí — texto a generar
Generar texto conciso y elegante (máximo 4 párrafos cortos) con este contenido:

- **Quién es Mario**: estudiante de ingeniería eléctrica ciclista amateur serio, actualmente hace running. Construye Verneris en solitario compaginándolo
  con la carrera.
- **El proyecto**: Verneris nació de una frustración real — la presión correcta
  de los neumáticos es uno de los factores más ignorados y más influyentes en
  rendimiento y confort, las herramientas actuales están incompletas en inglés. Verneris es gratuita, para cualquier ciclista.
- **El modelo técnico**: no es una tabla estática. Está basado en la fórmulaciones
  físicas con correcciones propias de temperatura, altitud...
  Ingeniería aplicada al ciclismo.
- **Lo que viene**: la ingeniería eléctrica abre otra dimensión. Hay intención
  de desarrollar herramientas en ese ámbito — Verneris es el primero de una
  familia de productos técnicos accesibles. Sin más detalle por ahora.

Tono: directo, técnico pero humano. Sin marketing vacío. Nada de "apasionado
por la tecnología" ni frases genéricas de startup.

### Imagen personal
Usar `url_for('static', filename='img/NOMBRE_ARCHIVO')`.
Preguntar el nombre exacto del archivo si no está especificado.
Aplicar `rounded-2xl object-cover`. Nunca inventar el path.

### Footer
Layout: logo Verneris a la izquierda, enlaces centrales (Calculadora, Historial,
Privacidad), iconos de redes sociales a la derecha.

Redes sociales — usar SVG inline con los logos oficiales, no FontAwesome:
- Twitter/X → https://x.com/SanudoMario
- Strava → https://www.strava.com/athletes/64718951

Color iconos: `text-[#6B6860]` por defecto, hover `text-[#F25C05]`.
Fondo footer: `#1A1A18`. Texto: `#6B6860`. 
Línea superior: `border-t border-white/10`.
Copyright: "© 2025 Verneris. Hecho con criterio."

### Imágenes externas
Para hero, sección inmersiva, login y register usar URLs Unsplash directas:
`https://images.unsplash.com/photo-ID?w=1200&q=80`
Ciclismo de carretera o gravel: ruedas, cubiertas, válvulas, asfalto mojado,
detalles mecánicos. Sin MTB ni ciclismo de montaña genérico.

### Imágenes propias
Siempre con `url_for('static', filename='img/archivo')`.
Nunca hardcodear paths relativos.