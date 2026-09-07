# Landings de acabados Gravitec®

Doce fichas web, una por acabado, pensadas para el QR del folleto de la caja de
muestras: el cliente escanea y ve en el móvil el color, las cifras clave, formatos,
propiedades y usos de ese acabado. Más un índice con los doce.

```
landings-acabados/
├── datos.json      textos, cifras y datos técnicos de los 12 acabados (edita aquí)
├── template.html   maqueta de la landing (Cera Pro, #01313D, acento #00ADB5)
├── build.py        genera dist/ a partir de datos.json + template.html
├── assets/         logo simple Gravity Wave (SVG, trazados reales de GRAVITY / WAVE)
├── img/            imágenes ya optimizadas (textura, mano, estudio, uso, thumb, comun)
└── dist/           salida: 12 landings + index.html, autocontenidas (base64)
```

## Generar

```bash
python3 build.py            # HTML autocontenidos, listos para enviar o subir tal cual
python3 build.py --linked   # HTML ligeros que enlazan a ../img y ../../assets/fonts
```

Requiere Python 3 (sin dependencias). Las fuentes se leen de `../assets/fonts/`.

## Orden y slugs (para los QR)

| # | Acabado | Archivo | Familia técnica |
|---|---|---|---|
| 01 | Cadaqués | `cadaques.html` | B · base clara (ficha pág. 9) |
| 02 | Vulcano | `vulcano.html` | A · HDPE redes (ficha pág. 4-5) |
| 03 | Sicilia | `sicilia.html` | B |
| 04 | Ifach | `ifach.html` | B |
| 05 | Palermo | `palermo.html` | B |
| 06 | Formentera | `formentera.html` | A |
| 07 | Capri | `capri.html` | B |
| 08 | Ítaca | `itaca.html` | A (pendiente confirmar) |
| 09 | Andros | `andros.html` | A |
| 10 | Niza | `niza.html` | B |
| 11 | Atenas | `atenas.html` | A |
| 12 | Marsella | `marsella.html` | B |

El orden es el del catálogo 2026. Sugerencia de URL para los QR:
`thegravitywave.com/gravitec/<slug>`.

## Estructura de cada landing

1. Hero con la textura real del acabado y el nombre.
2. La muestra en la mano + descripción (base, veta, carácter).
3. Cuatro cifras: 100 % redes · hasta 77 % menos CO₂ · 5–30 mm · ISO 14001.
4. Tres fotos de producto en ese acabado (o de la familia si no hay fotos propias).
5. Formatos S/M/L, textura y seis propiedades técnicas de su familia.
6. Cómo se trabaja y aplicaciones.
7. Economía circular: origen, blockchain, retorno circular.
8. Los otros once acabados (enlazados).
9. Contacto.

## Fuentes de la información

- Ficha técnica Gravitec® (propiedades, grupos de acabados, aplicaciones).
- Catálogo 2026 (formatos, plazos, textura, guía de uso, retorno, 77 % CO₂).
- Tarjeta de la caja de muestras (fotos de las muestras, 100 % redes, ISO 14001).
- Portfolio (fotos de producto).

## Pendientes / a validar

- Confirmar la familia técnica de Ítaca (la ficha no lo asigna de forma explícita).
- Sustituir las texturas por fotos en alta resolución cuando existan: las actuales
  salen de los PDF y se han ampliado para el hero.
- Confirmar el acabado de las fotos de producto asignadas por identificación visual.
- Palermo, Niza y Andros no tienen foto "en mano"; usan la foto de estudio.
