# Web — primera parte del embudo Mobiliario Urbano

`index.html` es la página de captación: la versión navegable y persuasiva del
**Catálogo Mobiliario Urbano Gravitec** (mismo sistema visual: fondo `#01313D`,
Cera Pro incrustada, aqua `#5FC9BD`, degradados sobre foto real), rematada con
el formulario que alimenta el embudo de HubSpot.

Es un único archivo autocontenido (~1 MB, fuentes e imágenes en base64):
se puede publicar tal cual en cualquier hosting, en HubSpot CMS o detrás de
`landing.thegravitywave.com`.

## Estructura persuasiva

1. **Héroe** — «Cada banco es un océano más limpio» + fila de confianza
   (ISO, normativa EN, Made in Spain, Benidorm entregado).
2. **Del mar a tu plaza** — el origen en 3 pasos.
3. **Producto real, no promesas** — banco, papelera, letras corpóreas y
   Serie Mar, con specs de las fichas técnicas. Cada «Pedir precio…»
   preselecciona el producto en el formulario.
4. **Acabados** — Formentera y Atenas reales, los 12 nombres.
5. **Trazabilidad** — doble marca y QR.
6. **Cómo se compra** — contrato menor · licitación · acuerdo marco.
7. **Formulario** (`#propuesta`) — promesa: propuesta con precios, mockups
   del municipio y fichas técnicas en <24 h (etapa «Lead mobiliario», máx. 1 día).
8. **Cierre** — «¿Te unes a la ola?».

## Formulario → HubSpot

- Envía a `api.hsforms.com` (portal **26243090**). El GUID se genera con
  `hubspot/provision-form.sh` y se pega en `var HS_FORM_GUID = "...";`.
- **Sin GUID configurado** el envío cae a un `mailto:` prellenado a
  info@thegravitywave.com — ningún lead se pierde.
- Campos → propiedades: `firstname`, `email`, `phone`, `tipo_entidad`,
  `municipio`, `productos_interes`, `plazo_proyecto`, `message` y
  `canal_origen` (oculto, derivado de `utm_source`:
  instagram → `instagram`, linkedin → `linkedin`, email →
  `email_ayuntamientos`, resto → `web_directo`).

## Cómo regenerarla

Las imágenes provienen del artifact «Catálogo Mobiliario Urbano Gravitec»
(recortadas para quitar rótulos incrustados y comprimidas) y las fuentes de
`assets/fonts/*-latin.woff2`. Si hay que tocar textos o estilos, editar
`index.html` directamente: los bloques base64 están al principio (fuentes)
y en los `src` de cada `<img>`.
