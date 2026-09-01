# Web — Landing Mobiliario Urbano (widget HTML de Elementor)

Fragmento HTML autocontenido que se pega en el **widget HTML de Elementor**
de la página `/mobiliario-urbano/` (post 11817). El resto de la página
(cabecera Astra, footer, CSS adicional de WordPress) no se toca.

## Cómo se genera y se publica

```bash
python3 web/build.py
```

Escribe `web/dist/mobiliario-fragmento-elementor.html` (~134 KB: incrusta
las fuentes Cera Pro de `assets/fonts/` y el logo). **Copiar el contenido
completo de ese archivo** y pegarlo en el widget HTML de Elementor,
sustituyendo el fragmento anterior. No editar el dist a mano: editar
`web/src/fragmento.html` y regenerar.

El efecto del botón «Pedir propuesta» de la barra superior (gradiente
animado `gw-proposal-flow`) va ahora **dentro del fragmento**, así que se
conserva aunque se pierda el CSS adicional de WordPress.

## Cambios de la revisión 31/08/2026

- **CO₂ en las fichas** (datos del catálogo Canva 2026): banco 12,13 kg ·
  papelera 5,99 kg · parques 6,55–218,4 kg según modelo · letras según nº.
- **Sin precio por escalado**: mismo precio por unidad pidas 1 o 20 piezas
  (enlaces, bullets del formulario y nota de tarifa reescritos).
- **Parques**: carrusel de 6 imágenes + botón «Ver el catálogo completo»
  → `/wp-content/uploads/2026/09/catalogomobiliariourbano2026.pdf`
  (PDF exportado del Canva «GRAVITEC · Catálogo Mobiliario Urbano 2026»,
  alojado en Medios — los enlaces de Canva salen como privados para el
  público; WordPress renombró el archivo al subirlo, sin guiones). Si una
  imagen del carrusel no está en Medios, se retira sola del carrusel.
- **Letras**: pedido mínimo **6 letras** (fuera el «6–10»).
- **Parques**: eliminado el KPI «Hasta 21.164 €».
- **Acabados**: tarjetas grandes con etiqueta, degradado y hover.
- **Formulario**: nombre y apellidos separados (`firstname`/`lastname`),
  teléfono obligatorio, campo municipio eliminado (se puede indicar en
  «¿Algo más?»), botón «Recibir propuesta».
- **Imágenes de estudio** (banco/papelera): ahora `object-fit:contain`
  sobre fondo blanco con margen, para que el fondo blanco quede enmarcado
  y no recortado/pixelado.

## Archivos a subir a Medios (carpeta 2026/08)

Nuevos (recortados del catálogo Canva 2026, ya listos en `web/src/img/`):

- `parque_carrusel_01.jpg` — modelo Barco frente al mar (portada del catálogo)
- `parque_carrusel_02.jpg` — parque con tobogán entre árboles
- `parque_carrusel_03.jpg` — tobogán y balancín al atardecer
- `parque_carrusel_04.jpg` — Crucero pirata en plaza urbana
- `parque_carrusel_05.jpg` — parque en paseo marítimo con palmeras
- `catalogo-mobiliario-urbano-2026.pdf` — catálogo completo (16 páginas),
  destino del botón «Ver el catálogo completo» (no está en el repo por
  tamaño; se exporta del Canva)

Ya existentes (se reutilizan): `hero_parque_hd-scaled.jpg`, `paso_*.jpg`,
`banco_studio.jpg`, `papelera_studio.jpg`, `parque_plaza.jpg`,
`letras_benidorm.jpg`, `acabado_*.jpg`, `cierre_puerto.jpg`.

**Pendiente de reemplazo por calidad** (se ven pixeladas o con fondo
blanco sin tratar): `banco_studio.jpg` y `papelera_studio.jpg` — exportar
a ≥1200 px de ancho; con el nuevo CSS el fondo blanco queda como marco,
pero la resolución hay que subirla en el archivo.

Las imágenes de agosto viven en `2026/08` y las del carrusel en `2026/09`
(WordPress guarda por mes de subida). El fragmento prueba ambas carpetas
por imagen; si se sube una tanda nueva en otro mes, añadir esa carpeta a
la lista `GW_IMG_BASES` del primer `<script>` del fragmento.

## HubSpot

Sin cambios de esquema: `firstname`, `lastname` y `phone` son propiedades
estándar de HubSpot. La propiedad `municipio` sigue existiendo en el
portal pero el formulario ya no la envía. `HS_FORM_GUID` sigue vacío
(fallback a mailto) hasta ejecutar el aprovisionamiento del formulario.
