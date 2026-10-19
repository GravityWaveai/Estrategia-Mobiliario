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
 *   3. El panel. El puente genera cada media hora la página del panel con
 *      todos los datos ya dentro (panel/plantilla.html) y la manda aquí por
 *      POST. Se guarda en la hoja «panel» y se sirve con ?ver=1&key=CLAVE,
 *      así se puede ver desde cualquier navegador sin depender de nada más.
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
 * Mobiliario Urbano» y tiene tres pestañas: «aperturas», «visitas» y «panel».
 *
 * Comprobaciones desde fuera (URL = la de la aplicación web). OJO: Google
 * reserva el parámetro «c» en las aplicaciones web y corta la petición, por
 * eso el contacto va en «t» y la campaña en «cmp».
 *   URL?t=PRUEBA&p=0                        → «ok» y añade una fila en aperturas
 *   URL?v=1&p=/mobiliario-urbano/&s=prueba  → «ok» y añade una fila en visitas
 *   URL?list=1&key=CLAVE[&since=AAAA-MM-DD] → aperturas en JSON
 *   URL?visits=1&key=CLAVE[&since=…]        → visitas en JSON
 *   URL?ver=1&key=CLAVE                     → el panel, como página
 *   URL?panel=1&key=CLAVE                   → el panel en JSON ({generado, html, datos})
 *   POST URL?panel=1&key=CLAVE  {html, datos} → guarda el panel (lo hace el puente)
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

// Pestaña «panel»: la última copia del panel que genera el puente (la página
// entera y sus datos). Una celda no admite más de 50.000 caracteres, así que
// va partido en trozos: columna A dice qué es (generado, html, datos) y la B
// lleva el trozo. Cada trozo empieza por «~» para que la hoja no lo tome por
// una fórmula, un número o una fecha.
var TROZO = 45000;

function hojaPanel_() {
  var ss = libro_();
  var h = ss.getSheetByName("panel");
  if (!h) {
    h = ss.insertSheet("panel");
    h.appendRow(["clave", "valor"]);
    h.setFrozenRows(1);
  }
  return h;
}

function trozos_(s) {
  var out = [], i = 0;
  s = String(s || "");
  while (i < s.length) {
    var fin = Math.min(i + TROZO, s.length);
    // No partir un carácter de dos unidades (emoji) por la mitad.
    var cu = s.charCodeAt(fin - 1);
    if (fin < s.length && cu >= 0xD800 && cu <= 0xDBFF) fin++;
    out.push("~" + s.slice(i, fin));
    i = fin;
  }
  return out;
}

// Guarda la página y los datos (texto JSON). Devuelve "" o el error.
function guardarPanel_(html, datosTexto) {
  try {
    var h = hojaPanel_();
    var filas = [["clave", "valor"], ["generado", new Date().toISOString()]];
    var th = trozos_(html);
    for (var i = 0; i < th.length; i++) filas.push(["html", th[i]]);
    var td = trozos_(datosTexto);
    for (var j = 0; j < td.length; j++) filas.push(["datos", td[j]]);
    h.clearContents();
    h.getRange(1, 1, filas.length, 2).setValues(filas);
    SpreadsheetApp.flush();
    return "";
  } catch (err) {
    return String(err && err.message ? err.message : err);
  }
}

// Lee el panel guardado: {generado, html, datos} (datos como texto) o null.
function leerPanel_() {
  var h = libro_().getSheetByName("panel");
  if (!h || h.getLastRow() < 2) return null;
  var filas = h.getDataRange().getValues().slice(1);
  var out = {generado: "", html: "", datos: ""};
  for (var i = 0; i < filas.length; i++) {
    var k = String(filas[i][0]);
    var v = filas[i][1] == null ? "" : String(filas[i][1]);
    if (k === "generado") out.generado = v;
    else if (k === "html") out.html += v.replace(/^~/, "");
    else if (k === "datos") out.datos += v.replace(/^~/, "");
  }
  return out.html ? out : null;
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
      try { var pn = leerPanel_(); d.panel = pn ? "generado " + pn.generado + ", " + Math.round(pn.html.length / 1024) + " KB" : "(sin panel todavía)"; } catch (e5) { d.panel = "error: " + e5; }
      return json_(d);
    }

    // El panel que genera el puente. ?ver=1&key=... lo enseña como página;
    // ?panel=1&key=... lo da en JSON ({generado, html, datos}).
    if (p.ver === "1" || p.panel === "1") {
      var esPagina = p.ver === "1";
      if (!clave) return esPagina ? texto_("falta la propiedad CLAVE del script") : json_({error: "falta la propiedad CLAVE del script"});
      if (p.key !== clave) return esPagina ? texto_("clave incorrecta") : json_({error: "clave incorrecta"});
      var panel = leerPanel_();
      if (!esPagina) {
        if (!panel) return json_({error: "todavía no hay panel guardado"});
        var datos = null;
        try { datos = JSON.parse(panel.datos); } catch (e6) { datos = null; }
        return json_({generado: panel.generado, html: panel.html, datos: datos});
      }
      if (!panel) return texto_("Todavía no hay panel: el puente lo genera en su próxima pasada (cada media hora).");
      return HtmlService.createHtmlOutput(panel.html).setTitle("Panel · Mobiliario Urbano");
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

// El puente manda el panel generado: POST URL?panel=1&key=CLAVE con el cuerpo
// {"html": "<!doctype html>…", "datos": {…}} en JSON. Se guarda entero en la
// pestaña «panel» y a partir de ahí lo sirve ?ver=1 y ?panel=1.
function doPost(e) {
  try {
    var p = (e && e.parameter) || {};
    var clave = clave_();
    if (p.panel !== "1") return json_({error: "petición desconocida"});
    if (!clave) return json_({error: "falta la propiedad CLAVE del script"});
    if (p.key !== clave) return json_({error: "clave incorrecta"});
    var cuerpo;
    try {
      cuerpo = JSON.parse((e.postData && e.postData.contents) || "");
    } catch (e1) {
      return json_({error: "el cuerpo no es JSON"});
    }
    if (!cuerpo || typeof cuerpo.html !== "string" || cuerpo.html.length < 1000) {
      return json_({error: "falta el html del panel"});
    }
    var err = guardarPanel_(cuerpo.html, JSON.stringify(cuerpo.datos || {}));
    if (err) return json_({error: err});
    return json_({ok: true, generado: new Date().toISOString(), html_kb: Math.round(cuerpo.html.length / 1024)});
  } catch (fatal) {
    return json_({error: String(fatal)});
  }
}
