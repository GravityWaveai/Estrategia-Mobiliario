/**
 * Receptor de aperturas y visitas — Gravity Wave · Mobiliario Urbano.
 *
 * Qué hace:
 *   1. Aperturas de correo. Cada correo de la secuencia de Apollo lleva al
 *      final una imagen invisible cuya dirección es la de este script, con el
 *      id del contacto y el número de correo. Cuando el ayuntamiento abre el
 *      correo, su programa pide la imagen y este script apunta la apertura en
 *      la hoja «aperturas». El puente Apollo ↔ HubSpot la lee cada hora y
 *      marca «abierto» en HubSpot.
 *   2. Visitas a la landing. Un fragmento en la web (tracking/visitas-gtm.html,
 *      cargado por Google Tag Manager en /mobiliario-urbano/) pide esta misma
 *      dirección con el origen de la visita (utm_source, utm_medium,
 *      utm_campaign y referente). Se apunta en la hoja «visitas». El panel la
 *      lee para saber cuánta gente llega a la landing y cuántos vienen del
 *      banner de la home.
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
 * La hoja de cálculo se crea sola en tu Drive; se llama «Aperturas ·
 * Mobiliario Urbano» y tiene dos pestañas: «aperturas» y «visitas».
 *
 * Comprobaciones desde fuera (URL = la de la aplicación web). OJO: Google
 * reserva el parámetro «c» en las aplicaciones web y corta la petición, por
 * eso el contacto va en «t» y la campaña en «cmp».
 *   URL?t=PRUEBA&p=0                        → «ok» y añade una fila en aperturas
 *   URL?v=1&p=/mobiliario-urbano/&s=prueba  → «ok» y añade una fila en visitas
 *   URL?list=1&key=CLAVE[&since=AAAA-MM-DD] → aperturas en JSON
 *   URL?visits=1&key=CLAVE[&since=…]        → visitas en JSON
 *   URL?diag=1&key=CLAVE                    → prueba cada paso y dice cuál falla
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

function libro_() {
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
  return ss;
}

// Pestaña «aperturas» (la primera del libro, como siempre).
function hoja_() {
  return libro_().getSheets()[0];
}

// Pestaña «visitas»; se crea la primera vez que hace falta.
function hojaVisitas_() {
  var ss = libro_();
  var h = ss.getSheetByName("visitas");
  if (!h) {
    h = ss.insertSheet("visitas");
    h.appendRow(["fecha_utc", "pagina", "utm_source", "utm_medium", "utm_campaign", "referente"]);
    h.setFrozenRows(1);
  }
  return h;
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

// Apunta una visita a la landing. Devuelve "" si fue bien o el error.
function apuntarVisita_(p) {
  try {
    var corta = function (s, n) { return String(s || "").trim().slice(0, n); };
    hojaVisitas_().appendRow([
      new Date().toISOString(),
      corta(p.p, 200),      // página (ruta)
      corta(p.s, 100),      // utm_source
      corta(p.m, 100),      // utm_medium
      corta(p.cmp, 100),    // utm_campaign
      corta(p.r, 300)       // referente (dominio que enlazó)
    ]);
    SpreadsheetApp.flush();
    return "";
  } catch (err) {
    return String(err && err.message ? err.message : err);
  }
}

// Devuelve las filas de una pestaña desde una fecha, como objetos.
function filas_(h, campos, since) {
  var filas = h.getDataRange().getValues().slice(1);
  var desde = since ? new Date(since) : null;
  var out = [];
  for (var i = 0; i < filas.length; i++) {
    var f = filas[i];
    var fecha = f[0] instanceof Date ? f[0] : new Date(f[0]);
    if (isNaN(fecha.getTime())) continue;
    if (desde && fecha < desde) continue;
    var o = {fecha: fecha.toISOString()};
    for (var j = 0; j < campos.length; j++) o[campos[j]] = String(f[j + 1] == null ? "" : f[j + 1]);
    out.push(o);
  }
  return out;
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
      try { var h0 = hoja_(); d.hoja = h0.getParent().getUrl(); d.filas_aperturas = h0.getLastRow() - 1; } catch (e2) { d.hoja = "error: " + e2; }
      try { d.filas_visitas = hojaVisitas_().getLastRow() - 1; } catch (e3) { d.filas_visitas = "error: " + e3; }
      var errA = apuntar_("DIAG", "0");
      d.apuntar = errA ? "error: " + errA : "ok";
      var errV = apuntarVisita_({p: "/diag", s: "DIAG"});
      d.apuntar_visita = errV ? "error: " + errV : "ok";
      return json_(d);
    }

    // Lectura para el puente y el panel: ?list=1&key=...&since=YYYY-MM-DD
    if (p.list === "1") {
      if (!clave) return json_({error: "falta la propiedad CLAVE del script"});
      if (p.key !== clave) return json_({error: "clave incorrecta"});
      var h = hoja_();
      var out = filas_(h, ["contacto", "paso", "agente"], p.since);
      return json_({hoja: h.getParent().getUrl(), total: out.length, aperturas: out});
    }

    // Lectura de visitas para el panel: ?visits=1&key=...&since=YYYY-MM-DD
    if (p.visits === "1") {
      if (!clave) return json_({error: "falta la propiedad CLAVE del script"});
      if (p.key !== clave) return json_({error: "clave incorrecta"});
      var hv = hojaVisitas_();
      var vis = filas_(hv, ["pagina", "utm_source", "utm_medium", "utm_campaign", "referente"], p.since);
      return json_({hoja: hv.getParent().getUrl(), total: vis.length, visitas: vis});
    }

    // Visita a la landing: ?v=1&p=<ruta>&s=<utm_source>&m=<utm_medium>&cmp=<utm_campaign>&r=<referente>
    if (p.v === "1") {
      // Solo la landing. La vista previa de Tag Manager dispara la etiqueta en
      // su propia página (/render, referente gtm-msr.appspot.com) y no es una
      // visita; tampoco lo es nada que no sea /mobiliario-urbano.
      if (!/mobiliario-urbano/.test(String(p.p || "")) || /gtm-msr|tagassistant/.test(String(p.r || ""))) return texto_("ignorado");
      var errVis = apuntarVisita_(p);
      return texto_(errVis ? "error: " + errVis : "ok");
    }

    // Píxel: ?t=<id de contacto en Apollo>&p=<número de correo 1..5>
    // OJO: Google reserva el parámetro «c» (la petición no llega al script).
    // El píxel usa «t»; «c» se deja solo por compatibilidad.
    var c = String(p.t || p.c || "").trim();
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
