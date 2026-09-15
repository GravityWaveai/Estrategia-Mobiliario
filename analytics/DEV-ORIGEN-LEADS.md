# Cómo hacer que se sepa de dónde viene cada lead

Guía para quien publica en redes y para quien toca la web. Nace del lead de
prueba `TestLK Test` (15/09/2026), que entró desde una publicación de LinkedIn
y el panel lo dio por «Web directo». El diagnóstico entero está en
`README.md`, sección «Por qué hay que etiquetar el enlace SIEMPRE».

En una frase: **la etiqueta viaja dentro de la dirección y siempre llega; el
referente lo borra LinkedIn por el camino.** Por eso etiquetar el enlace no es
opcional ni una mejora — es la única vía que funciona siempre.

---

## Los enlaces que hay que publicar

| Dónde se publica | Enlace exacto |
|---|---|
| LinkedIn | `https://www.thegravitywave.com/mobiliario-urbano/?utm_source=linkedin&utm_medium=social&utm_campaign=mobiliario-2026` |
| Instagram | `https://www.thegravitywave.com/mobiliario-urbano/?utm_source=instagram&utm_medium=social&utm_campaign=mobiliario-2026` |

Se enlaza **siempre a `/mobiliario-urbano/`**, la variante A, nunca a
`/mobiliario-urbano-b/`. El sorteo A/B ya reparte solo al 50 %, y conserva la
query al redirigir, así que la etiqueta sobrevive. Enlazar a la B a mano
rompería el reparto.

Las secuencias de Apollo van **sin UTM**, las dos, por decisión (11/09/2026).

---

## PARTE 1 — LinkedIn

No hace falta desarrollador. Lo hace quien publique.

1. Copia el enlace de LinkedIn de la tabla de arriba.
2. Pégalo en el cuerpo de la publicación. LinkedIn lo acortará a `lnkd.in/…`
   al mostrarlo: **es normal y no rompe nada**, la etiqueta viaja dentro del
   destino y llega igual.
3. Repasa que también lo lleven el enlace de la **página de empresa**, el del
   **botón de la página** y el de la **bio**, si apuntan a la landing.
4. Si algún día se hace **publicidad** en LinkedIn, el mismo enlace, cambiando
   `utm_medium=social` por `utm_medium=paid`.

**Cuidado con una trampa.** Cuando copias la dirección de una publicación de
LinkedIn te da algo como
`…activity-7505537474094579712-vKhF?utm_source=share&utm_medium=member_desktop`.
Esas UTM son **de LinkedIn para su propia web** y no viajan al enlace de
salida. No sirven de nada aquí y no hay que reutilizarlas.

### Lo que NO arregla esto

Ni acortadores propios, ni «Ver más», ni publicar la imagen con el enlace en
el primer comentario. Lo único que arregla el problema es que la dirección
lleve `?utm_source=linkedin`.

---

## PARTE 2 — Instagram

Tampoco hace falta desarrollador.

1. **Enlace de la bio**: usa el enlace de Instagram de la tabla. Si vais por
   Linktree o similar, la UTM tiene que ir en el enlace **de destino** dentro
   de la herramienta, no en el de la bio.
2. **Stories con sticker de enlace**: mismo enlace, pegado entero.
3. **Publicidad en Instagram**: mismo enlace con `utm_medium=paid`.

Instagram sí suele mandar referente desde el navegador de escritorio, pero
desde la aplicación no. Mismo caso que LinkedIn: la etiqueta es lo fiable.

---

## PARTE 3 — La web (esto sí es para el desarrollador)

Son **dos páginas de WordPress** con el mismo código dentro de un widget HTML
de Elementor. **Hay que hacer el mismo cambio en las dos**; comprobado el
15/09/2026 que las dos tienen la versión antigua:

- `https://www.thegravitywave.com/mobiliario-urbano/` (post_id 11817)
- `https://www.thegravitywave.com/mobiliario-urbano-b/`

Copia de referencia del código: `analytics/generate-lead.js` en este repo. Si
editas la página, edita también ese archivo.

### Paso 3.1 — Pegar el bloque de captura ARRIBA DEL TODO

Dentro del widget HTML, busca el `<script>` que empieza así:

```html
<script>
/* Prueba A/B mobiliario urbano — reparto 50/50 con cookie.
   Va primero a propósito: la redirección debe ocurrir antes de pintar nada. */
```

**Justo ANTES de ese `<script>`**, añade este otro bloque entero:

```html
<script>
var GW_UTM_SRC = "gw_utm_source",
    GW_UTM_CAMP = "gw_utm_campaign",
    GW_REF = "gw_referente";

/* Todo acceso a sessionStorage va envuelto: en modo privado, con cookies
   bloqueadas o dentro de un iframe, leer o escribir LANZA. Y esto corre en
   la ruta del formulario, así que una excepción aquí costaría un lead. */
function guardaOrigen(clave, valor) {
  if (!valor) return;
  try {
    if (!sessionStorage.getItem(clave)) sessionStorage.setItem(clave, valor);
  } catch (e) { /* sin persistencia: se sigue leyendo de la URL */ }
}
function recuperaOrigen(clave) {
  try { return sessionStorage.getItem(clave) || ""; } catch (e) { return ""; }
}

/* De qué red viene un referente. LinkedIn manda unas veces linkedin.com y
   otras lnkd.in, su acortador de enlaces salientes. */
var REDES_REFERENTE = [
  ["linkedin",  ["linkedin.com", "lnkd.in", "licdn.com"]],
  ["instagram", ["instagram.com", "ig.me"]]
];

function canalDeReferente(url) {
  if (!url) return "";
  var host;
  try { host = new URL(url).hostname.toLowerCase(); } catch (e) { return ""; }
  /* Navegación dentro de la propia web: no es una captación nueva. */
  if (host === location.hostname.toLowerCase()) return "";
  for (var i = 0; i < REDES_REFERENTE.length; i++) {
    var dominios = REDES_REFERENTE[i][1];
    for (var j = 0; j < dominios.length; j++) {
      var d = dominios[j];
      /* Sufijo exacto: vale "linkedin.com" y "www.linkedin.com", nunca
         "linkedin.com.loquesea.net". */
      if (host === d || host.slice(-(d.length + 1)) === "." + d) {
        return REDES_REFERENTE[i][0];
      }
    }
  }
  return "";
}

/* Se ejecuta en cada carga, cuanto antes. La redirección A/B conserva la
   query (`location.replace(URL_B + location.search + location.hash)`), así
   que la UTM sobrevive por sí sola; el referente no, de ahí que se guarde
   aquí antes de que el sorteo tenga ocasión de redirigir. */
(function capturaOrigen() {
  var p = new URLSearchParams(location.search);
  guardaOrigen(GW_UTM_SRC,  (p.get("utm_source")   || "").toLowerCase());
  guardaOrigen(GW_UTM_CAMP, (p.get("utm_campaign") || "").toLowerCase());
  guardaOrigen(GW_REF,      canalDeReferente(document.referrer));
})();</script>
```

**El orden importa y no es un detalle de estilo.** El sorteo A/B redirige con
`location.replace()` entre las dos landings. Después de esa redirección,
`document.referrer` ya no es LinkedIn: es la otra landing. Si el bloque se
pega después, se pierde el único rastro que quedaba.

### Paso 3.2 — Sustituir `canalOrigen()` entera

En el `<script>` grande de más abajo (el que empieza por
`var HS_PORTAL_ID = "26243090";`) hay esta función:

```js
function canalOrigen() {
  var p = new URLSearchParams(location.search);
  var src = (p.get("utm_source") || "").toLowerCase();
  if (src === "instagram") return "instagram";
  if (src === "linkedin") return "linkedin";
  if (src === "email") return "email_ayuntamientos";
  return "web_directo";
}
```

Bórrala entera y pon esta en su sitio:

```js
function canalOrigen() {
  var p = new URLSearchParams(location.search);
  var src  = recuperaOrigen(GW_UTM_SRC)  || (p.get("utm_source")   || "").toLowerCase();
  var camp = recuperaOrigen(GW_UTM_CAMP) || (p.get("utm_campaign") || "").toLowerCase();
  if (src === "instagram") return "instagram";
  if (src === "linkedin") return "linkedin";
  if (src === "email") return camp.indexOf("ayuntamientos") !== -1 ? "email_ayuntamientos" : "otro";
  var ref = recuperaOrigen(GW_REF) || canalDeReferente(document.referrer);
  if (ref) return ref;
  return "web_directo";
}
```

No hay que tocar nada más: `payload()` ya llama a `canalOrigen()` y ya manda
`canal_origen` a HubSpot.

### Paso 3.3 — Comprobar que funciona

Con la página ya publicada, en las dos landings:

1. Abre en una **ventana nueva de incógnito**
   `https://www.thegravitywave.com/mobiliario-urbano/?utm_source=linkedin&utm_medium=social&utm_campaign=mobiliario-2026`
2. Abre la consola del navegador (F12) y escribe `canalOrigen()`.
   Tiene que responder `"linkedin"`.
3. Navega a otra página de la web y vuelve al formulario **sin la UTM**.
   Vuelve a escribir `canalOrigen()`: tiene que seguir diciendo `"linkedin"`.
   Eso es la persistencia en `sessionStorage`; si dice `"web_directo"`, el
   bloque del paso 3.1 no se está ejecutando.
4. Envía un formulario de prueba y busca el contacto en HubSpot: la propiedad
   `canal_origen` tiene que decir `linkedin`.
5. En el panel, pestaña **Inbound**, tabla «Lead a lead»: ese lead tiene que
   salir como **LinkedIn**, no como «Web directo».

Repite el 1-3 con `?utm_source=instagram`.

---

## PARTE 4 — GA4 y GTM (aparte, y NO bloquea nada)

**El panel no depende de esto.** El panel lee HubSpot directamente. Lo de
abajo es solo para que la conversión aparezca también en los informes de
Google Analytics, y puede hacerse más tarde sin que nada se rompa.

Está todo detallado en `README.md`, secciones «El evento `generate_lead`»,
«Configuración en GTM» y «Configuración en GA4». Resumen:

1. En la página, dentro del `.then()` del envío, después de comprobar `r.ok`
   y antes de `showOk()`, el `dataLayer.push` del apartado 1 de
   `generate-lead.js`.
2. En GTM: tres variables de capa de datos, un activador de evento
   personalizado `generate_lead`, y una etiqueta de evento GA4 a
   `G-7LN8GNKJM8` con comprobación de consentimiento por `analytics_storage`.
3. En GA4: dar de alta las tres dimensiones personalizadas de ámbito Evento y
   marcar `generate_lead` como evento clave.

Ningún dato personal viaja en ese evento: ni nombre, ni email, ni teléfono, ni
el mensaje libre, que suele traer el municipio y a veces el nombre de una
persona.

---

## Lo que sigue sin poder arreglarse

- El lead `TestLK Test` **no se recupera hacia atrás**. Nadie guardó de dónde
  venía. O se corrige a mano en HubSpot, o se queda como está.
- Un clic desde la **aplicación móvil de LinkedIn** a un enlace **sin
  etiquetar** seguirá cayendo en «Web directo». El respaldo por referente del
  paso 3.1 recupera los de escritorio, no los de la app. Por eso el enlace
  etiquetado no es negociable.
