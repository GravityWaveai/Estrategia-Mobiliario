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
 *   3. Configuración del proyecto (rueda) → Propiedades del script →
 *      «Añadir propiedad»: CLAVE = la misma clave que el secreto
 *      APERTURAS_KEY de GitHub. La clave NO va en este archivo.
 *   4. Arriba a la derecha: «Implementar» → «Nueva implementación».
 *      Tipo: «Aplicación web». Ejecutar como: «Yo». Quién tiene acceso:
 *      «Cualquier usuario». → «Implementar». Autoriza cuando lo pida.
 *   5. Copia la «URL de la aplicación web» (termina en /exec) y pégala en el
 *      chat. Con eso se termina de conectar todo.
 *
 * Cada vez que se cambia este archivo hay que publicar una versión nueva:
 * Implementar → Gestionar implementaciones → lápiz → Versión: «Nueva
 * versión» → Implementar. La URL no cambia.
 *
 * La hoja de cálculo se crea sola en tu Drive la primera vez que llega una
 * apertura; se llama «Aperturas · Mobiliario Urbano».
 *
 * Comprobaciones desde fuera (URL = la de la aplicación web):
 *   URL?c=PRUEBA&p=0            → debe responder «ok» y añadir una fila
 *   URL?list=1&key=CLAVE        → la lista en JSON
 *   URL?diag=1&key=CLAVE        → prueba cada paso y dice cuál falla
 */

var NOMBRE_HOJA = "Aperturas · Mobiliario Urbano";

function clave_() {
  return PropertiesService.getScriptProperties().getProperty("CLAVE") || "";
}

function texto_(s) {
  return ContentService.createTextOutput(String(s)).setMimeType(ContentService.MimeType.TEXT);
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

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

// Apunta una apertura. Devuelve "" si fue bien o el texto del error.
function apuntar_(c, paso) {
  try {
    var h = hoja_();
    // Fecha en texto ISO (UTC) para que no dependa de la zona horaria de la
    // hoja. Google no expone ni la IP ni el User-Agent del lector; las
    // columnas quedan por si algún día cambia. Nunca se guarda la IP.
    h.appendRow([new Date().toISOString(), c, paso, "", ""]);
    SpreadsheetApp.flush();
    return "";
  } catch (err) {
    return String(err && err.message ? err.message : err);
  }
}

function doGet(e) {
  try {
    var p = (e && e.parameter) || {};
    var clave = clave_();

    // Diagnóstico: ?diag=1&key=...  Prueba cada paso y dice cuál falla.
    if (p.diag === "1") {
      if (!clave) return json_({error: "falta la propiedad CLAVE del script"});
      if (p.key !== clave) return json_({error: "clave incorrecta"});
      var d = {clave: "ok"};
      try { d.sheet_id = PropertiesService.getScriptProperties().getProperty("SHEET_ID") || "(sin crear)"; } catch (e1) { d.sheet_id = "error: " + e1; }
      try { var h0 = hoja_(); d.hoja = h0.getParent().getUrl(); d.filas = h0.getLastRow(); } catch (e2) { d.hoja = "error: " + e2; }
      var errA = apuntar_("DIAG", "0");
      d.apuntar = errA ? "error: " + errA : "ok";
      return json_(d);
    }

    // Lectura para el puente: ?list=1&key=...&since=YYYY-MM-DD
    if (p.list === "1") {
      if (!clave) return json_({error: "falta la propiedad CLAVE del script"});
      if (p.key !== clave) return json_({error: "clave incorrecta"});
      var h = hoja_();
      var filas = h.getDataRange().getValues().slice(1);
      var desde = p.since ? new Date(p.since) : null;
      var out = [];
      for (var i = 0; i < filas.length; i++) {
        var f = filas[i];
        var fecha = f[0] instanceof Date ? f[0] : new Date(f[0]);
        if (isNaN(fecha.getTime())) continue;
        if (desde && fecha < desde) continue;
        out.push({fecha: fecha.toISOString(), contacto: String(f[1]), paso: String(f[2]), agente: String(f[3])});
      }
      return json_({hoja: h.getParent().getUrl(), total: out.length, aperturas: out});
    }

    // Píxel: ?c=<id de contacto en Apollo>&p=<número de correo 1..5>
    var c = String(p.c || "").trim();
    var paso = String(p.p || "").trim();
    if (!c || c === "{{tracking_id}}") return texto_("ignorado");
    var err = apuntar_(c, paso);
    // Apps Script no puede devolver una imagen; el programa de correo pide la
    // dirección igualmente y eso es lo que cuenta. Lo que reciba lo descarta.
    // (Una respuesta vacía la rechaza Google con un 400: siempre va texto.)
    return texto_(err ? "error: " + err : "ok");
  } catch (fatal) {
    return texto_("error: " + fatal);
  }
}
