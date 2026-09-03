# Las piezas en Canva

Las diez piezas están importadas en Canva como **diseños editables**: el texto
entró como capa de texto viva, no como imagen, así que se puede cambiar un
titular, un precio o el nombre de un municipio sin tocar código.

**Carpeta:** [Gravity Wave · Mobiliario urbano 2026](https://www.canva.com/folder/FAHUKI1WIvo)

| Cód. | Pieza | Pág. | ID del diseño | Editar |
|---|---|---|---|---|
| P01 | Teaser | 1 | `DAHUKjMLH-w` | [Abrir](https://www.canva.com/design/DAHUKjMLH-w/edit) |
| P02 | El bucle en tres pasos | 4 | `DAHUKn7uoHY` | [Abrir](https://www.canva.com/design/DAHUKn7uoHY/edit) |
| P03 | Carrusel héroe de lanzamiento | 8 | `DAHUKkCDxqc` | [Abrir](https://www.canva.com/design/DAHUKkCDxqc/edit) |
| P04 | Manifiesto | 1 | `DAHUKnUSLrI` | [Abrir](https://www.canva.com/design/DAHUKnUSLrI/edit) |
| P05 | El catálogo pieza a pieza | 7 | `DAHUKhdXBdg` | [Abrir](https://www.canva.com/design/DAHUKhdXBdg/edit) |
| P06 | Los doce acabados | 1 | `DAHUKg1sDjk` | [Abrir](https://www.canva.com/design/DAHUKg1sDjk/edit) |
| P07 | Cómo lo compra un ayuntamiento (LinkedIn) | 6 | `DAHUKoozDHg` | [Abrir](https://www.canva.com/design/DAHUKoozDHg/edit) |
| P08 | Tarjeta de cita (post de fundadora) | 1 | `DAHUKhvhLUM` | [Abrir](https://www.canva.com/design/DAHUKhvhLUM/edit) |
| P09 | Stories | 3 | `DAHUKkXTIgg` | [Abrir](https://www.canva.com/design/DAHUKkXTIgg/edit) |
| P10 | Plantilla por municipio | 1 | `DAHUKkpEeRM` | [Abrir](https://www.canva.com/design/DAHUKkpEeRM/edit) |

> **Ojo con los enlaces.** La API de Canva devuelve URLs cortas del tipo
> `canva.com/d/XXXX`, pero son **tokens de un solo uso**: cambian en cada
> llamada y a otra persona le salen como documento privado. La dirección
> estable de un diseño es siempre `canva.com/design/<ID>/edit`, la de la tabla.

Si sale «privado», el navegador está en una cuenta de Canva distinta de la que
tiene conectada Claude. Entra con esa, o busca las piezas en **Proyectos**.

La carpeta [versiones descartadas](https://www.canva.com/folder/FAHUKjqkf_k)
guarda la primera tanda de importaciones, que salió con la fuente equivocada y
la firma en negro. No las uséis; se pueden borrar.

## Qué usar y cuándo

| Para | Usa |
|---|---|
| Publicar el calendario tal cual | Los **PNG** de `png/` y el PDF de LinkedIn: son exactos de marca |
| Cambiar un texto, un precio o adaptar por municipio | Los **diseños de Canva** de arriba |
| Cambiar la campaña de raíz (titulares, piezas nuevas) | El **generador** (`tools/piezas.py`) y reimportar |

## La tipografía: hasta dónde se puede llegar

Canva **no puede ingerir una fuente incrustada** en el HTML, y su API no tiene
forma de subir fuentes ni de asignar una familia tipográfica a un texto. O sea:
desde aquí no se puede meter la Cera Pro en Canva. Es una limitación de Canva,
no del generador.

Lo que sí se ha hecho: el export declara **Poppins**, que está en la biblioteca
de Canva y es la caída documentada de la Cera —geométrica, del mismo aire—. Es
lo más cerca que se llega sin tocar la cuenta. Antes Canva elegía por su cuenta
una redondeada que no se parecía en nada.

**Para tener la Cera Pro de verdad** (dos minutos, una sola vez):

1. En Canva, **Marca → Kit de marca → Fuentes → Subir una fuente**.
2. Subid los archivos de `assets/fonts/` del repo (Regular, Medium, Black,
   Black Italic). Requiere Canva Pro.
3. En cada diseño: `Ctrl/Cmd + A` para seleccionar todo y aplicar Cera Pro.

Hecho eso, decídmelo y cambio el export para que declare la Cera por delante
de Poppins; a partir de ahí las importaciones nuevas ya entrarán con la Cera
enganchada sola.

## Lo que la importación tampoco conserva

**Algunos encuadres se aplanan.** Las composiciones a dos mitades —la foto
arriba, el titular abajo— entran como foto a sangre con el texto encima. Se
recoloca a mano en un minuto, o se usa el PNG si la pieza va sin cambios.

Por eso la regla: **PNG para publicar, Canva para editar.**

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
