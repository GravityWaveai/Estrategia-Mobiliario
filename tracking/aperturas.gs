/**
 * Receptor de aperturas de correo — Gravity Wave · Mobiliario Urbano.
 *
 * Qué hace: cada correo de la secuencia de Apollo lleva al final una imagen
 * invisible cuya dirección es la de este script, con el id del contacto y el
 * número de correo. Cuando el ayuntamiento abre el correo, su programa de
 * correo pide la imagen, y este script apunta la apertura en una hoja de
 * cálculo. El puente Apollo ↔ HubSpot lee esa hoja cada hora y marca
 * «abierto» en HubSpot.
 *
 * Cómo se publica (una sola vez, 2 minutos, con la cuenta de Google de
 * Gravity Wave):
 *   1. https://script.google.com → «Nuevo proyecto».
 *   2. Borra lo que haya y pega este archivo entero. Ctrl+S. Nómbralo
 *      «Aperturas Mobiliario Urbano».
 *   3. Arriba a la derecha: «Implementar» → «Nueva implementación».
 *      Tipo: «Aplicación web». Ejecutar como: «Yo». Quién tiene acceso:
 *      «Cualquier usuario». → «Implementar». Autoriza cuando lo pida.
 *   4. Copia la «URL de la aplicación web» (termina en /exec) y pégala en el
 *      chat. Con eso se termina de conectar todo.
 *
 * La hoja de cálculo se crea sola en tu Drive la primera vez que llega una
 * apertura; se llama «Aperturas · Mobiliario Urbano».
 */

// Misma clave que en .github/workflows/apollo-bridge.yml (APERTURAS_KEY).
// Protege la lectura de la hoja; el píxel no la necesita.
var CLAVE = "la0AAolKM5Xogs4dmh4ZSZpRcNV87aNt";
var NOMBRE_HOJA = "Aperturas · Mobiliario Urbano";

function hoja_() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty("SHEET_ID");
  var ss = null;
  if (id) {
    try { ss = SpreadsheetApp.openById(id); } catch (e) { ss = null; }
  }
  if (!ss) {
    ss = SpreadsheetApp.create(NOMBRE_HOJA);
    props.setProperty("SHEET_ID", ss.getId());
    var h = ss.getSheets()[0];
    h.setName("aperturas");
    h.appendRow(["fecha_utc", "contacto", "paso", "agente", "ip_hash"]);
    h.setFrozenRows(1);
  }
  return ss.getSheets()[0];
}

function doGet(e) {
  var p = (e && e.parameter) || {};

  // Lectura para el puente: ?list=1&key=...&since=YYYY-MM-DD
  if (p.list === "1") {
    if (p.key !== CLAVE) {
      return ContentService.createTextOutput(JSON.stringify({error: "clave incorrecta"}))
        .setMimeType(ContentService.MimeType.JSON);
    }
    var h = hoja_();
    var filas = h.getDataRange().getValues().slice(1);
    var desde = p.since ? new Date(p.since) : null;
    var out = [];
    for (var i = 0; i < filas.length; i++) {
      var f = filas[i];
      var fecha = f[0] instanceof Date ? f[0] : new Date(f[0]);
      if (desde && fecha < desde) continue;
      out.push({fecha: fecha.toISOString(), contacto: String(f[1]), paso: String(f[2]), agente: String(f[3])});
    }
    return ContentService.createTextOutput(JSON.stringify({
      hoja: h.getParent().getUrl(), total: out.length, aperturas: out
    })).setMimeType(ContentService.MimeType.JSON);
  }

  // Píxel: ?c=<id de contacto en Apollo>&p=<número de correo 1..5>
  var c = String(p.c || "").trim();
  var paso = String(p.p || "").trim();
  if (c && c !== "{{tracking_id}}") {
    try {
      var ua = "";
      var ip = "";
      try { ua = (e.headers && (e.headers["User-Agent"] || e.headers["user-agent"])) || ""; } catch (x) {}
      // Google no expone la IP del lector; se deja la columna por si algún
      // día cambia. Nunca se guarda la IP en claro.
      hoja_().appendRow([new Date(), c, paso, ua.substring(0, 120), ip]);
    } catch (err) {
      // Si la hoja falla no se pierde nada más: el correo ya se abrió.
    }
  }
  // Apps Script no puede devolver una imagen; el programa de correo pide la
  // dirección igualmente y eso es lo que cuenta. Lo que reciba lo descarta.
  return ContentService.createTextOutput("").setMimeType(ContentService.MimeType.TEXT);
}
