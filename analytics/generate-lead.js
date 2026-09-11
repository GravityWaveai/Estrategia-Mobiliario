/* Medición de la conversión en la landing /mobiliario-urbano/
 *
 * Este archivo NO se carga en ningún sitio: es la copia versionada del
 * código que vive dentro de la página de WordPress (post_id 11817,
 * https://www.thegravitywave.com/mobiliario-urbano/). El repositorio no
 * tiene la landing, así que sin esto no quedaría rastro de qué se tocó ni
 * por qué. Si alguien edita la página, edita también este archivo.
 *
 * Contexto y configuración de GTM/GA4: ../analytics/README.md
 */

/* ------------------------------------------------------------------ *
 * 1. Evento de lead
 *
 * Va DENTRO del .then() del envío del formulario, después de comprobar
 * r.ok y ANTES de llamar a showOk().
 *
 * No vale meterlo dentro de showOk(): esa función se llama también desde
 * la rama de mailtoFallback() (cuando HS_FORM_GUID está vacío), donde
 * HubSpot no ha confirmado nada y contar una conversión sería mentir.
 *
 * No lleva guardia de duplicados a propósito: al enviar, el botón queda
 * deshabilitado y el formulario se oculta, así que no hay segundo disparo.
 *
 * No viaja ningún dato personal — ni nombre, ni email, ni teléfono, ni el
 * campo de mensaje libre, que suele traer el municipio y a veces el nombre
 * de una persona. Solo las tres dimensiones que sirven para decidir.
 * ------------------------------------------------------------------ */

window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "generate_lead",
  canal_origen: canalOrigen(),
  landing_variant: window.gwLandingVariant || "sin_variante",
  tipo_entidad: document.getElementById("f-entidad").value
});

/* Queda así en la página:
 *
 *   }).then(function (r) {
 *     if (!r.ok) throw new Error("HTTP " + r.status);
 *     window.dataLayer = window.dataLayer || [];
 *     window.dataLayer.push({ ... });
 *     showOk();
 *   }).catch(function () {
 */


/* ------------------------------------------------------------------ *
 * 2. Captura de campaña — va ARRIBA, junto a las demás funciones
 *
 * El problema que resuelve: `canalOrigen()` leía `location.search` en el
 * momento de enviar. Quien llega desde Instagram, mira el catálogo, vuelve
 * al formulario y envía, ya no tiene la UTM en la URL y contaba como
 * `web_directo`. Lo mismo si el enlace de la publicación no la lleva.
 *
 * Ahora la campaña se guarda en cuanto se ve y se lee de ahí al enviar.
 *
 * `sessionStorage` y no `localStorage` a propósito: una visita de mañana
 * desde otro sitio es otra captación y debe contar como tal. Y no añade
 * ninguna categoría de dato nueva — es la misma UTM que el formulario ya
 * manda a HubSpot en `canal_origen`, guardada unos minutos en el propio
 * navegador de quien navega.
 *
 * Manda SIEMPRE la primera campaña de la sesión. Si se prefiere que una
 * visita posterior desde otra campaña reescriba la atribución, hay que
 * quitar la condición `if (!sessionStorage.getItem(clave))` de guarda().
 * ------------------------------------------------------------------ */

var GW_UTM_SRC = "gw_utm_source", GW_UTM_CAMP = "gw_utm_campaign";

/* Todo acceso a sessionStorage va envuelto: en modo privado, con cookies
   bloqueadas o dentro de un iframe, leer o escribir LANZA. Y esto corre en
   la ruta del formulario, así que una excepción aquí costaría un lead. */
function guardaCampana(clave, valor) {
  if (!valor) return;
  try {
    if (!sessionStorage.getItem(clave)) sessionStorage.setItem(clave, valor);
  } catch (e) { /* sin persistencia: se sigue leyendo de la URL */ }
}
function recuperaCampana(clave) {
  try { return sessionStorage.getItem(clave) || ""; } catch (e) { return ""; }
}

/* Se ejecuta en cada carga, cuanto antes. La redirección A/B conserva la
   query (`location.replace(URL_B + location.search + location.hash)`), así
   que da igual por cuál de las dos landings entre. */
(function capturaCampana() {
  var p = new URLSearchParams(location.search);
  guardaCampana(GW_UTM_SRC,  (p.get("utm_source")   || "").toLowerCase());
  guardaCampana(GW_UTM_CAMP, (p.get("utm_campaign") || "").toLowerCase());
})();


/* ------------------------------------------------------------------ *
 * 3. canalOrigen() — sustituye entera a la que hay en la página
 *
 * Dos arreglos sobre la versión desplegada:
 *
 *  a) Lee la campaña guardada, no la URL del momento (ver arriba). La URL
 *     queda de red de seguridad para cuando sessionStorage no esté
 *     disponible: entonces se comporta como hasta ahora, ni mejor ni peor.
 *
 *  b) `utm_source=email` ya no manda a `email_ayuntamientos` sin mirar la
 *     campaña. En cuanto la secuencia INBOUND de Apollo llevara UTM, un lead
 *     que vino por web y vuelve desde un correo quedaría reetiquetado como
 *     ayuntamiento y la atribución diría una cosa por otra.
 *
 * De los cinco valores del enumerado `canal_origen` en HubSpot
 * (hubspot/spec/contact-properties.json) produce cuatro:
 * email_ayuntamientos, instagram, linkedin, web_directo y otro.
 * ------------------------------------------------------------------ */

function canalOrigen() {
  var p = new URLSearchParams(location.search);
  var src  = recuperaCampana(GW_UTM_SRC)  || (p.get("utm_source")   || "").toLowerCase();
  var camp = recuperaCampana(GW_UTM_CAMP) || (p.get("utm_campaign") || "").toLowerCase();
  if (src === "instagram") return "instagram";
  if (src === "linkedin") return "linkedin";
  if (src === "email") return camp.indexOf("ayuntamientos") !== -1 ? "email_ayuntamientos" : "otro";
  return "web_directo";
}
