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
 * 2. canalOrigen() — versión corregida
 *
 * La versión anterior mandaba a `email_ayuntamientos` CUALQUIER visita con
 * utm_source=email. En cuanto la secuencia INBOUND de Apollo llevara UTM,
 * un lead que ya vino por web y vuelve desde un correo quedaría reetiquetado
 * como ayuntamiento, y la atribución del embudo diría una cosa por otra.
 *
 * Ahora el canal se decide por la campaña, no solo por la fuente. De los
 * cinco valores del enumerado `canal_origen` en HubSpot
 * (hubspot/spec/contact-properties.json) esta función produce cuatro:
 * email_ayuntamientos, instagram, linkedin, web_directo y otro.
 * ------------------------------------------------------------------ */

function canalOrigen() {
  var p = new URLSearchParams(location.search);
  var src = (p.get("utm_source") || "").toLowerCase();
  var camp = (p.get("utm_campaign") || "").toLowerCase();
  if (src === "instagram") return "instagram";
  if (src === "linkedin") return "linkedin";
  if (src === "email") return camp.indexOf("ayuntamientos") !== -1 ? "email_ayuntamientos" : "otro";
  return "web_directo";
}
