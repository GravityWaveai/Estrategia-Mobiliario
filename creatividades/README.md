# Creatividades de RRSS — Mobiliario urbano

Generador de las creatividades del lanzamiento en Instagram y LinkedIn.
El plan de campaña, el calendario y los textos están en
[`PLAN-LANZAMIENTO.md`](PLAN-LANZAMIENTO.md).

## Regenerar todo

```bash
pip install Pillow
python3 creatividades/tools/prep_assets.py   # solo si cambian fotos o acabados
python3 creatividades/tools/build.py
```

Sale:

| Salida | Qué es |
|---|---|
| `kit-creatividades.html` | Las 33 piezas con sus textos, en un único archivo autocontenido |
| `png/<id>.png` | Cada pieza a tamaño real de píxel, lista para subir |
| `carrusel-linkedin-ayuntamientos.pdf` | La pieza P07 paginada, para el post de documento de LinkedIn |

`build.py --solo-kit` genera solo el HTML (no necesita Chrome).

Y para revisar lo entregado:

```bash
python3 creatividades/tools/revisar.py
```

Comprueba pieza a pieza la medida exacta, el fondo petróleo, que el turquesa
siga siendo un acento (tope del 12 % de la superficie) y que no haya rojo,
naranja, amarillo, coral ni lima. Distingue **fallos** (la pieza está mal
hecha) de **avisos** (hay tono cálido, que en las fotos reales de Gravity Wave
es arena, madera o latón; lo mira una persona y decide). Sale con código 1
solo si hay fallos, así que sirve tal cual en un hook o en CI.

## Los cuatro módulos

| Archivo | Responsabilidad |
|---|---|
| `tools/estilo.py` | Paleta, Cera Pro incrustada y el CSS del sistema visual |
| `tools/piezas.py` | Las 10 piezas: maquetación y contenido de cada tablero |
| `tools/copys.py` | Los textos de cada pieza, en voz de Instagram y de LinkedIn |
| `tools/build.py` | Monta el kit, exporta los PNG y el PDF |
| `tools/prep_assets.py` | Optimiza fotos y acabados y hornea el wordmark |

Para cambiar un titular o un precio, `piezas.py`. Para cambiar un texto de
publicación, `copys.py`. Para tocar la tipografía o el color, `estilo.py`.

## Sistema visual

Sale de la skill `gravity-wave-marca`, no de una interpretación:

- Fondo `#01313D`, texto blanco, acento `#00ADB5` **con cuentagotas**.
- **Cera Pro real** incrustada en base64 desde `assets/fonts/` (Black para
  titulares, Medium para antetítulos, Regular para párrafos).
- La regla de oro: **antetítulo diminuto y espaciado encima de un titular
  enorme y macizo**, alineado a la izquierda.
- Logo: el **wordmark simple** (`GRAVITY` espaciado sobre `WAVE` en Black),
  sin olas, solo en blanco o negro. Recortado del logo oficial, no redibujado.
- Fotografía a sangre con velo `#01313D` encima, para que el texto respire.

Todas las medidas van en la unidad `--u` (= ancho ÷ 1080), así las mismas
reglas sirven para las piezas de 1080 y las de 1200 de ancho.

## Dos cosas que conviene saber si toca tocar el generador

Ambas costaron una tarde y están comentadas en el código, para no repetirlas:

1. **El viewport de Chrome headless es unos 87 px más bajo que
   `--window-size`.** La franja de abajo de la pieza no se renderizaba y se
   rellenaba con el color de fondo, así que el pie salía cortado sin que se
   notara. `build.py` pide ventana de sobra y recorta la pieza a su tamaño
   exacto (`MARGEN_VENTANA`).
2. **El wordmark va en PNG, no en SVG.** Al rasterizar el SVG dentro del pie
   (una caja posicionada con `bottom`), Chrome pinta solo la parte de arriba
   del trazado y corta la palabra WAVE por la mitad, tanto como `<img>` como
   en línea o como `background-image`. `prep_assets.py` hornea el PNG
   recortando el logo oficial con Pillow.

## De dónde salen los datos

Nada inventado:

- **Fotos de producto y los 12 acabados Gravitec®**: de la skill
  `interactive-product-customizer`.
- **Precios**: catálogo Ocean Originals, €/ud, IVA no incluido.
- **Propuesta y mockup en 24 h**: es el compromiso de la etapa «Lead
  mobiliario» del pipeline (`hubspot/README.md`).
- **229.000 t/año al Mediterráneo**: UICN, «The Mediterranean: Mare
  Plasticum», 2020 — con la fuente impresa en la propia pieza.
- **UTMs**: el mismo esquema del embudo, en `hubspot/README.md`.

Donde falta una foto real, la pieza lleva un **hueco marcado on-brand** en vez
de una imagen que no toca. Ver el apartado «Antes de publicar» del plan.
