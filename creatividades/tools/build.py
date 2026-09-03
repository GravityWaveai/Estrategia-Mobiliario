#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las creatividades de RRSS del lanzamiento de mobiliario urbano.

Salidas (en `creatividades/`):
  kit-creatividades.html   el kit completo, autocontenido, para revisar
  png/<id>.png             cada pieza a tamaño real de píxel
  carrusel-linkedin-ayuntamientos.pdf  el carrusel B2G listo para subir

Uso:
  python3 creatividades/tools/build.py            # todo
  python3 creatividades/tools/build.py --solo-kit # solo el HTML
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import copys
import estilo
import piezas

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG = os.path.join(ROOT, "png")

CHROME_CANDIDATOS = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
]


def chrome():
    for c in CHROME_CANDIDATOS:
        if os.path.exists(c):
            return c
    for nombre in ("chromium", "google-chrome", "chrome"):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta
    return None


def cabecera_css():
    """Fuentes + sistema visual + las imagenes, cada cosa una sola vez."""
    return "<style>%s\n%s\n%s</style>" % (estilo.tipografia(), estilo.CSS,
                                           estilo.css_imagenes())


def tablero_html(tb):
    """Un tablero suelto, a tamano exacto, listo para capturar."""
    return ('<div class="board" id="%s" style="width:%dpx;height:%dpx;'
            '--u:%.6fpx">%s</div>' % (tb["id"], tb["w"], tb["h"],
                                      tb["w"] / 1080.0, tb["html"]))


def pagina_suelta(tb):
    return ("<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
            "%s<style>html,body{margin:0;padding:0;background:%s;"
            "width:%dpx;height:%dpx;overflow:hidden}</style></head><body>%s"
            "</body></html>"
            % (cabecera_css(), estilo.FONDO, tb["w"], tb["h"],
               tablero_html(tb)))


KIT_CSS = """
html{background:#001a21}
body{margin:0;font-family:'Cera Pro',Poppins,system-ui,sans-serif;
  color:#fff;background:#001a21}
.wrap{max-width:1500px;margin:0 auto;padding:76px 44px 120px}
.cab{border-bottom:1px solid rgba(255,255,255,.14);padding-bottom:44px;
  margin-bottom:64px}
.cab .m{width:230px;height:95.07px;margin-bottom:36px;background-repeat:no-repeat;background-size:100% 100%}
.cab h1{font-weight:900;text-transform:uppercase;letter-spacing:-.02em;
  line-height:.96;font-size:62px;margin:0 0 20px}
.cab .a{font-weight:500;text-transform:uppercase;letter-spacing:.3em;
  font-size:14px;color:#00ADB5;margin-bottom:18px}
.cab p{font-weight:400;font-size:18px;line-height:1.6;
  color:rgba(255,255,255,.72);max-width:820px;margin:0}
.pieza{margin:0 0 84px}
.pieza .h{display:flex;align-items:baseline;gap:18px;flex-wrap:wrap;
  border-bottom:1px solid rgba(255,255,255,.1);padding-bottom:16px;
  margin-bottom:30px}
.pieza .cod{font-weight:900;font-size:30px;color:#00ADB5;
  letter-spacing:-.01em}
.pieza .nom{font-weight:900;text-transform:uppercase;font-size:26px;
  letter-spacing:-.01em}
.pieza .met{font-weight:500;text-transform:uppercase;letter-spacing:.22em;
  font-size:12px;color:rgba(255,255,255,.5);margin-left:auto}
.tiras{display:flex;gap:22px;overflow-x:auto;padding-bottom:22px;
  align-items:flex-start}
.tira{flex:0 0 auto}
.tira .marco{background:#01313D;box-shadow:0 18px 44px rgba(0,0,0,.42)}
.tira .pieinfo{font-weight:500;font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:rgba(255,255,255,.45);margin-top:11px;
  max-width:280px;line-height:1.6}
.tira .nota{font-weight:400;font-size:11px;color:#00ADB5;margin-top:5px;
  letter-spacing:0;text-transform:none;line-height:1.5;max-width:280px}
.board{transform-origin:top left}
.holder{overflow:hidden}
.copys{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));
  gap:26px;margin-top:30px;padding-top:26px;
  border-top:1px solid rgba(255,255,255,.1)}
.copy h4{font-weight:500;text-transform:uppercase;letter-spacing:.24em;
  font-size:11px;color:#00ADB5;margin:0 0 12px}
.copy pre{font-family:'Cera Pro',Poppins,system-ui,sans-serif;font-weight:400;
  font-size:13.5px;line-height:1.62;color:rgba(255,255,255,.82);margin:0;
  white-space:pre-wrap;word-break:break-word}
.copy .etq{display:block;margin-top:12px;font-size:12px;line-height:1.6;
  color:#5f9aa4}
.aviso{margin-top:20px;padding:14px 18px;border-left:2px solid #00ADB5;
  background:rgba(0,173,181,.07);font-size:13px;line-height:1.6;
  color:rgba(255,255,255,.8)}
.aviso b{font-weight:900;color:#00ADB5}

/* --- intro y calendario, solo en la version publicada --- */
.idea{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
  gap:34px;margin:0 0 58px}
.capa{padding:26px 28px;background:#01313D}
.capa h3{font-weight:900;text-transform:uppercase;letter-spacing:.01em;
  font-size:19px;margin:0 0 10px}
.capa .quien{font-weight:500;text-transform:uppercase;letter-spacing:.24em;
  font-size:11px;color:#00ADB5;margin-bottom:16px}
.capa p{font-size:14.5px;line-height:1.65;color:rgba(255,255,255,.78);
  margin:0}
.tesis{font-weight:900;text-transform:uppercase;letter-spacing:-.02em;
  line-height:1.05;font-size:34px;margin:0 0 58px;padding-left:22px;
  border-left:3px solid #00ADB5;max-width:900px;text-wrap:balance}
.cal{width:100%;border-collapse:collapse;margin:0 0 72px;
  font-size:14px;font-variant-numeric:tabular-nums}
.cal caption{text-align:left;font-weight:500;text-transform:uppercase;
  letter-spacing:.24em;font-size:11px;color:#00ADB5;padding-bottom:16px}
.cal th{text-align:left;font-weight:500;text-transform:uppercase;
  letter-spacing:.18em;font-size:10.5px;color:rgba(255,255,255,.5);
  padding:0 16px 12px 0;border-bottom:1px solid rgba(255,255,255,.16)}
.cal td{padding:13px 16px 13px 0;color:rgba(255,255,255,.82);
  border-bottom:1px solid rgba(255,255,255,.07);vertical-align:top}
.cal td.cod{font-weight:900;color:#00ADB5;white-space:nowrap}
.cal td.pza{font-weight:900;color:#fff}
.cal tr.hero td{background:rgba(0,173,181,.07)}
.envoltorio{overflow-x:auto}
"""


def kit(tableros, escala=0.26, artefacto=False):
    """El kit completo. En modo artefacto, sin envoltorio de documento."""
    if artefacto:
        partes = ["<title>El plástico vuelve a la calle</title>",
                  cabecera_css(), "<style>%s</style>" % KIT_CSS,
                  '<div class="wrap">']
    else:
        partes = ["<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">",
                  "<title>Creatividades RRSS - Mobiliario urbano</title>",
                  cabecera_css(), "<style>%s</style></head><body>" % KIT_CSS,
                  '<div class="wrap">']
    partes += [
              '<div class="cab"><div class="m" role="img" aria-label="Gravity Wave"'
              ' style="background-image:url(%s)"></div>' % estilo.wordmark(),
              '<div class="a">Lanzamiento en redes &middot; Mobiliario urbano</div>',
              '<h1>El pl&aacute;stico<br>vuelve a la calle</h1>',
              '<p>Treinta y tres creatividades para Instagram y LinkedIn. '
              'La historia es p&uacute;blica &mdash;el pl&aacute;stico del Mediterr&aacute;neo vuelve '
              'convertido en un banco&mdash; y la conversi&oacute;n a ayuntamiento vive '
              'en la cola de cada carrusel y en LinkedIn. Fondo #01313D, '
              'Cera Pro real, #00ADB5 con cuentagotas.</p></div>']
    if artefacto:
        partes.append(intro())

    por_pieza = {}
    for tb in tableros:
        por_pieza.setdefault(tb["pieza"], []).append(tb)

    for codigo, nombre, fase, _ in piezas.PIEZAS:
        grupo = por_pieza.get(codigo, [])
        if not grupo:
            continue
        c = copys.COPYS.get(codigo, {})
        canal = c.get("canales") or grupo[0]["canal"]
        fase = c.get("cuando") or fase
        partes.append('<div class="pieza"><div class="h">'
                      '<span class="cod">%s</span>'
                      '<span class="nom">%s</span>'
                      '<span class="met">%s &middot; %s &middot; %d %s</span></div>'
                      '<div class="tiras">'
                      % (codigo, nombre, fase, canal, len(grupo),
                         "pieza" if len(grupo) == 1 else "piezas"))
        for tb in grupo:
            w = round(tb["w"] * escala)
            h = round(tb["h"] * escala)
            partes.append(
                '<div class="tira"><div class="marco holder" '
                'style="width:%dpx;height:%dpx">'
                '<div style="transform:scale(%.5f);transform-origin:top left">'
                '%s</div></div>'
                '<div class="pieinfo">%s &middot; %d&times;%d</div>%s</div>'
                % (w, h, escala, tablero_html(tb), tb["nombre"],
                   tb["w"], tb["h"],
                   ('<div class="nota">%s</div>' % tb["nota"])
                   if tb.get("nota") else ""))
        partes.append('</div>')
        partes.append(bloque_copy(codigo))
        partes.append('</div>')

    partes.append("</div>" if artefacto else "</div></body></html>")
    return "".join(partes)


CALENDARIO = [
    ("Semana 1", "Martes 10:00", "P01", "Teaser", "IG + LinkedIn", "1 imagen"),
    ("Semana 1", "Viernes 13:00", "P02", "El bucle en tres pasos",
     "Instagram", "Carrusel 4"),
    ("Semana 2", "Martes 10:00", "P03", "Carrusel héroe",
     "IG + LinkedIn", "Carrusel 8"),
    ("Semana 2", "Viernes 13:00", "P04", "Manifiesto", "IG + LinkedIn",
     "1 imagen"),
    ("Semana 3", "Martes 10:00", "P05", "El catálogo pieza a pieza",
     "Instagram", "Carrusel 7"),
    ("Semana 3", "Jueves 19:00", "P06", "Los doce acabados", "Instagram",
     "1 imagen"),
    ("Semana 4", "Miércoles 09:00", "P07", "Cómo lo compra un ayuntamiento",
     "LinkedIn", "Documento 6 pág."),
    ("Semana 4", "Viernes 09:00", "P08", "Post de fundadora",
     "LinkedIn (Amaia)", "1 imagen"),
    ("Cada semana", "Con cada post", "P09", "Stories", "Instagram",
     "3 stories"),
    ("Al cerrar", "Cada municipio", "P10", "Plantilla por municipio",
     "IG + LinkedIn", "1 imagen"),
]


def intro():
    """La idea y el calendario, para que el kit publicado se explique solo."""
    filas = "".join(
        '<tr%s><td>%s</td><td>%s</td><td class="cod">%s</td>'
        '<td class="pza">%s</td><td>%s</td><td>%s</td></tr>'
        % (' class="hero"' if cod == "P03" else "", sem, dia, cod, pza, can, fmt)
        for sem, dia, cod, pza, can, fmt in CALENDARIO)
    return (
        '<p class="tesis">Sacar el plástico es la mitad del trabajo.<br>'
        'La otra es darle un sitio.</p>'
        '<div class="idea">'
        '<div class="capa"><div class="quien">Capa pública</div>'
        '<h3>Todo el mundo</h3><p>Portada y primeras diapositivas de cada '
        'carrusel, posts sueltos y stories. El plástico que sacamos del '
        'Mediterráneo vuelve a tu ciudad convertido en un banco. Es lo que '
        'se comparte y lo que da alcance.</p></div>'
        '<div class="capa"><div class="quien">Capa del decisor</div>'
        '<h3>Ayuntamientos</h3><p>Las últimas diapositivas de cada carrusel '
        'y todo LinkedIn. Encaje en pliego, plazos, precio por volumen y '
        'trazabilidad. Quien no es ayuntamiento se queda antes; quien lo es '
        'llega y escribe.</p></div>'
        '</div>'
        '<div class="envoltorio"><table class="cal">'
        '<caption>Cuatro semanas</caption><thead><tr>'
        '<th>Semana</th><th>Cuándo</th><th>Cód.</th><th>Pieza</th>'
        '<th>Canal</th><th>Formato</th></tr></thead>'
        '<tbody>%s</tbody></table></div>' % filas)


def bloque_copy(codigo):
    """El texto de la pieza, debajo de sus imagenes."""
    c = copys.COPYS.get(codigo)
    if not c:
        return ""
    cols = []
    if c.get("ig"):
        cols.append('<div class="copy"><h4>Texto para Instagram</h4>'
                    '<pre>%s</pre><span class="etq">%s</span></div>'
                    % (escapar(c["ig"]), copys.ETIQUETAS_IG))
    if c.get("li"):
        cols.append('<div class="copy"><h4>Texto para LinkedIn</h4>'
                    '<pre>%s</pre><span class="etq">%s</span></div>'
                    % (escapar(c["li"]), copys.ETIQUETAS_LI))
    aviso = ('<div class="aviso"><b>Antes de publicar &middot;</b> %s</div>'
             % escapar(c["nota"])) if c.get("nota") else ""
    return '<div class="copys">%s</div>%s' % ("".join(cols), aviso)


def escapar(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;"))


# En headless el viewport sale mas bajo que --window-size (unos 87 px), asi
# que la franja de abajo de la pieza no se renderiza y se rellena con el color
# de fondo: el pie salia cortado sin que se notase. Se pide ventana de sobra y
# se recorta la pieza a su tamano exacto.
MARGEN_VENTANA = 240


def capturar(tableros, bin_chrome):
    """Exporta cada tablero a PNG a su tamano exacto de pixel."""
    from PIL import Image

    os.makedirs(PNG, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="gw-boards-")
    hechos, fallos = [], []
    try:
        for tb in tableros:
            html = os.path.join(tmp, "%s.html" % tb["id"])
            with open(html, "w") as f:
                f.write(pagina_suelta(tb))
            crudo = os.path.join(tmp, "%s.png" % tb["id"])
            cmd = [bin_chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                   "--hide-scrollbars", "--force-device-scale-factor=1",
                   "--virtual-time-budget=2500",
                   "--screenshot=%s" % crudo,
                   "--window-size=%d,%d" % (tb["w"], tb["h"] + MARGEN_VENTANA),
                   html]
            r = subprocess.run(cmd, capture_output=True)
            if not os.path.exists(crudo):
                fallos.append((tb["id"], r.stderr.decode()[-200:]))
                continue
            im = Image.open(crudo)
            if im.height < tb["h"] or im.width < tb["w"]:
                fallos.append((tb["id"], "render %dx%d menor que la pieza %dx%d"
                               % (im.width, im.height, tb["w"], tb["h"])))
                continue
            destino = os.path.join(PNG, "%s.png" % tb["id"])
            im.convert("RGB").crop((0, 0, tb["w"], tb["h"])).save(
                destino, optimize=True)
            hechos.append(tb["id"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return hechos, fallos


def pdf_linkedin(tableros):
    """El carrusel B2G como PDF, que es el formato de documento de LinkedIn.

    Se arma con los PNG ya exportados, no con --print-to-pdf: la ruta de
    impresion de Chrome se deja fuera los fondos (el petroleo y las fotos van
    como background-image) y el PDF salia sin ellos. Asi el documento es
    identico pixel a pixel a las piezas.
    """
    from PIL import Image

    hojas = [tb for tb in tableros if tb["pieza"] == "P07"]
    imagenes = []
    for tb in hojas:
        ruta = os.path.join(PNG, "%s.png" % tb["id"])
        if not os.path.exists(ruta):
            return None
        imagenes.append(Image.open(ruta).convert("RGB"))
    if not imagenes:
        return None

    destino = os.path.join(ROOT, "carrusel-linkedin-ayuntamientos.pdf")
    imagenes[0].save(destino, "PDF", save_all=True,
                     append_images=imagenes[1:], resolution=96.0)
    return destino


# --------------------------------------------------- exportacion a Canva
# El importador de Canva convierte en pagina cada elemento marcado con
# data-document-role="page", y el texto entra como capa de texto viva, no
# como imagen. Se emite un archivo por pieza para que cada carrusel sea un
# diseno de Canva, y solo con las imagenes que esa pieza usa.
def export_canva(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    escritos = []
    for codigo, nombre, _fase, fn in piezas.PIEZAS:
        estilo.reset_imagenes()
        tableros = fn()
        paginas = []
        for tb in tableros:
            paginas.append(
                '<div class="board" data-document-role="page" '
                'data-label="%s" style="width:%dpx;height:%dpx;--u:%.6fpx">'
                '%s</div>'
                % (tb["nombre"].replace('"', "'"), tb["w"], tb["h"],
                   tb["w"] / 1080.0, tb["html"]))
        html = ("<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
                "<title>%s %s</title>%s"
                "<style>html,body{margin:0;padding:0;background:%s}%s</style>"
                "</head><body>%s</body></html>"
                % (codigo, nombre, cabecera_css(), estilo.FONDO,
                   estilo.CSS_CANVA, "".join(paginas)))
        ruta = os.path.join(carpeta, "%s.html" % codigo.lower())
        with open(ruta, "w") as f:
            f.write(html)
        escritos.append((codigo, nombre, ruta, len(tableros),
                         tableros[0]["w"], tableros[0]["h"]))
    return escritos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-kit", action="store_true")
    ap.add_argument("--artefacto", metavar="RUTA",
                    help="escribe el kit sin envoltorio, para publicar")
    ap.add_argument("--canva", metavar="CARPETA",
                    help="un HTML por pieza, anotado para importar en Canva")
    args = ap.parse_args()

    if args.canva:
        for cod, nom, ruta, n, w, h in export_canva(args.canva):
            print("canva %-4s %-34s %d pag. %dx%d  %d KB"
                  % (cod, nom[:34], n, w, h, os.path.getsize(ruta) // 1024))
        return

    tableros = piezas.todas()
    if args.artefacto:
        with open(args.artefacto, "w") as f:
            f.write(kit(tableros, artefacto=True))
        print("arte  %s (%d KB)"
              % (args.artefacto, os.path.getsize(args.artefacto) // 1024))
        return

    destino_kit = os.path.join(ROOT, "kit-creatividades.html")
    with open(destino_kit, "w") as f:
        f.write(kit(tableros))
    print("kit   %s  (%d KB, %d tableros)"
          % (os.path.relpath(destino_kit), os.path.getsize(destino_kit) // 1024,
             len(tableros)))
    if args.solo_kit:
        return

    bin_chrome = chrome()
    if not bin_chrome:
        sys.exit("No encuentro Chrome/Chromium; usa --solo-kit")

    hechos, fallos = capturar(tableros, bin_chrome)
    print("png   %d exportados en %s" % (len(hechos), os.path.relpath(PNG)))
    for i, err in fallos:
        print("      FALLO %s: %s" % (i, err))

    doc = pdf_linkedin(tableros)
    if doc:
        print("pdf   %s (%d KB, %d paginas)"
              % (os.path.relpath(doc), os.path.getsize(doc) // 1024,
                 sum(1 for t in tableros if t["pieza"] == "P07")))


if __name__ == "__main__":
    main()
