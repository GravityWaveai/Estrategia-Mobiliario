# Web — primera parte del embudo Mobiliario Urbano

`index.html` es la landing de captación: la versión navegable del
**Catálogo Mobiliario Urbano Gravitec 2026** (Canva `DAHTUG63Aks`), con el
sistema visual aprobado (fondo `#01313D`, Cera Pro incrustada, aqua `#5FC9BD`,
degradados sobre foto real) y el formulario que alimenta el embudo de HubSpot.

Es un único archivo autocontenido (~0,9 MB, fuentes e imágenes en base64),
pensado para colgarlo bajo `www.thegravitywave.com` (p. ej.
`/mobiliario-urbano/`): al vivir en el dominio, la cookie `hubspotutk` del
tracking de HubSpot ya instalado se adjunta sola y la atribución de origen
queda completa.

## Estructura (la del catálogo)

1. **Portada** — «Mobiliario urbano» + Catálogo 2026 + Made in Spain.
2. **Del mar al público** — Mar → Puerto → Recuperación → Transformación →
   Producto, con la tira de fotos del catálogo.
3. **Tres familias con tarifa oficial** —
   01 Bancos y papeleras (banco 654 € · papelera 265 €, plazo 5–6 semanas) ·
   02 Parques infantiles Serie Mar (632 € – 21.164 €, plazo 6–8 semanas) ·
   03 Letras de exterior (1.250 €/letra, pedidos 6–10, plazo 9–11 semanas).
   Cada «Pedir precio…» preselecciona la familia en el formulario.
4. **Acabados** — Formentera (redes verdes) y Atenas (redes azules).
5. **Compra pública** — las 5 razones + las 3 vías de contratación.
6. **Formulario** (`#propuesta`) — propuesta en <24 h (etapa «Lead
   mobiliario», máx. 1 día).
7. **Cierre** — «¿Te unes a la ola?».

## Formulario → HubSpot

- Envía a `api.hsforms.com` (portal **26243090**), sin token en el navegador.
  El GUID del formulario se genera con `hubspot/provision-form.sh` y se pega
  en `var HS_FORM_GUID = "...";`.
- **Sin GUID configurado** el envío cae a un `mailto:` prellenado a
  info@thegravitywave.com — ningún lead se pierde.
- Campos → propiedades: `firstname`, `email`, `phone`, `tipo_entidad`,
  `municipio`, `productos_interes` (banco · papelera · parque_infantil ·
  letrero_corporeo · otro), `unidades_estimadas` (1–5 · 6–15 · 16–50 ·
  +50 · sin definir), `plazo_proyecto`, `message` y `canal_origen`
  (oculto, derivado de `utm_source`: instagram → `instagram`,
  linkedin → `linkedin`, email → `email_ayuntamientos`, resto →
  `web_directo`).

### Del envío al pipeline

1. El envío crea/actualiza el **contacto** con las propiedades de
   Mobiliario Urbano rellenas y la sumisión de formulario registrada.
2. El **agente procesador de leads** (paso 2 del plan, ver
   `hubspot/README.md`) detecta la sumisión, crea el **negocio** en la etapa
   «Lead mobiliario» del pipeline Mobiliario Urbano (propietaria: Amaia) y
   dispara la generación de propuesta + mockups con los datos del formulario
   (productos, unidades para el precio por volumen, municipio para los
   mockups).
3. A partir de ahí aplican las reglas del pipeline (importe obligatorio,
   seguimientos 5/12/14 días, reactivaciones).

## Cómo publicarla en thegravitywave.com (Elementor)

La web usa Elementor, y en un widget HTML **no** se puede pegar `index.html`
entero (lleva `<!doctype>`, `<head>`…): para eso existe **`elementor.html`**,
el mismo contenido como fragmento con todo el CSS acotado bajo `#gw-mob`
para que el tema no lo pise.

1. Páginas → Añadir nueva → **Editar con Elementor**.
2. Engranaje (abajo izquierda) → Configuración de página → Diseño de página →
   **Elementor Canvas** (sin cabecera ni pie del tema; la landing trae su
   propia barra superior).
3. Arrastrar un widget **HTML** y pegar dentro el contenido íntegro de
   `elementor.html`.
4. En la sección que lo contiene: ancho «Ancho completo» y padding 0
   (pestaña Avanzado).
5. Publicar (p. ej. en `/mobiliario-urbano/`).

**No hay que subir nada a Medios**: fuentes e imágenes van embebidas en
base64 dentro del propio HTML.

## Cómo regenerarla

Fuente única: `src/landing-template.html` + `src/img/*.jpg` (recortes del
catálogo de Canva re-exportado a 4K) + `assets/fonts/*-latin.woff2`.

```bash
python3 web/build.py   # regenera web/index.html y web/elementor.html
```

Para tocar textos o estilos, editar `src/landing-template.html` y regenerar
— nunca los dos HTML generados a mano.
