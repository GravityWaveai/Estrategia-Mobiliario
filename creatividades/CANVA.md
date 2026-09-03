# Las piezas en Canva

Las diez piezas están importadas en Canva como **diseños editables**: el texto
entró como capa de texto viva, no como imagen, así que se puede cambiar un
titular, un precio o el nombre de un municipio sin tocar código.

**Carpeta:** [Gravity Wave · Mobiliario urbano 2026](https://www.canva.com/folder/FAHUKI1WIvo)

| Cód. | Pieza | Pág. | Editar |
|---|---|---|---|
| P01 | Teaser | 1 | [Abrir](https://www.canva.com/d/ksp0FKU0JIusoR2) |
| P02 | El bucle en tres pasos | 4 | [Abrir](https://www.canva.com/d/9MI2FtqgJjDZ0Hj) |
| P03 | Carrusel héroe de lanzamiento | 8 | [Abrir](https://www.canva.com/d/XfxuESBtsJlswHn) |
| P04 | Manifiesto | 1 | [Abrir](https://www.canva.com/d/iOrnX0iVtsecmsf) |
| P05 | El catálogo pieza a pieza | 7 | [Abrir](https://www.canva.com/d/pHvVAK_VU-FFE1V) |
| P06 | Los doce acabados | 1 | [Abrir](https://www.canva.com/d/EoDCcI1jk6DYS5e) |
| P07 | Cómo lo compra un ayuntamiento (LinkedIn) | 6 | [Abrir](https://www.canva.com/d/SY8eIYYMTOBWJ0y) |
| P08 | Tarjeta de cita (post de fundadora) | 1 | [Abrir](https://www.canva.com/d/FckpTQg6o3Bm8uQ) |
| P09 | Stories | 3 | [Abrir](https://www.canva.com/d/6qkmJJNQp54cYXk) |
| P10 | Plantilla por municipio | 1 | [Abrir](https://www.canva.com/d/OphKDK_75o4Mh9S) |

## Qué usar y cuándo

| Para | Usa |
|---|---|
| Publicar el calendario tal cual | Los **PNG** de `png/` y el PDF de LinkedIn: son exactos de marca |
| Cambiar un texto, un precio o adaptar por municipio | Los **diseños de Canva** de arriba |
| Cambiar la campaña de raíz (titulares, piezas nuevas) | El **generador** (`tools/piezas.py`) y reimportar |

## Dos cosas que la importación no conserva

Canva no puede ingerir una fuente incrustada ni todo el CSS, así que los
diseños importados son **editables pero no idénticos** a los PNG:

1. **La tipografía sale sustituida.** Cera Pro va incrustada en base64 en el
   HTML y Canva la cambia por una suya. Se arregla de una vez: subid Cera Pro
   a vuestro **Kit de Marca** de Canva (Marca → Fuentes) y aplicadla a los
   diseños; los archivos están en `assets/fonts/` del repo.
2. **Algunos velos y encuadres se aplanan.** Las composiciones a dos mitades
   (la foto arriba, el titular abajo) entran como foto a sangre con el texto
   encima. Se recoloca a mano en un minuto, o se usa el PNG si la pieza va a
   publicarse sin cambios.

Por eso la regla de arriba: **PNG para publicar, Canva para editar.**

## Reimportar después de un cambio

Si cambiáis la campaña en el generador, hay que rehacer el HTML anotado y
volver a importar (la importación crea diseños nuevos, no actualiza los
existentes):

```bash
python3 creatividades/tools/build.py --canva creatividades/canva
git add -A creatividades/canva && git commit -m "..." && git push
```

Y luego importar en Canva desde la URL cruda de cada archivo:

```
https://raw.githubusercontent.com/GravityWaveai/Estrategia-Mobiliario/<rama>/creatividades/canva/p03.html
```

Funciona porque cada tablero lleva `data-document-role="page"`, que es lo que
el importador de Canva convierte en página.
