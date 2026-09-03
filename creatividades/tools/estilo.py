"""Sistema visual de las creatividades de RRSS de Gravity Wave.

Un único sitio donde viven la paleta, la tipografía y los recursos de
composición, para que las 33 piezas salgan del mismo molde.

Regla de oro de la marca: antetítulo diminuto y espaciado encima de un
titular enorme y macizo. Fondo #01313D, Cera Pro, #00ADB5 con cuentagotas.
"""
import base64
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)

# ---------------------------------------------------------------- paleta
FONDO = "#01313D"
FORMENTERA = "#00ADB5"
DEEP = "#1E6778"
BLANCO = "#FFFFFF"
DARK = "#101820"


def _b64(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode()


def cera(peso, fichero, italica=False):
    ruta = os.path.join(REPO, "assets", "fonts", fichero)
    if not os.path.exists(ruta):
        return ""
    return ("@font-face{font-family:'Cera Pro';font-weight:%d;font-style:%s;"
            "font-display:block;src:url(data:font/woff2;base64,%s) format('woff2')}"
            % (peso, "italic" if italica else "normal", _b64(ruta)))


def tipografia():
    return "".join([
        cera(400, "CeraPro-Regular-latin.woff2"),
        cera(500, "CeraPro-Medium-latin.woff2"),
        cera(900, "CeraPro-Black-latin.woff2"),
        cera(900, "CeraPro-BlackItalic-latin.woff2", italica=True),
    ])


# Proporcion del wordmark: 1152 x 476.
WORDMARK_RATIO = 476 / 1152.0


def wordmark(color="blanco"):
    """El wordmark simple del logo oficial, como data URI.

    Se usa el PNG, no el SVG: al rasterizar el SVG dentro del pie de las
    piezas (una caja posicionada con "bottom") Chrome headless corta la
    palabra WAVE por la mitad. Lo genera `prep_assets.py` recortando el
    logo oficial. Solo blanco o negro, como manda la marca.
    """
    ruta = os.path.join(ROOT, "assets", "logo-gw-wordmark-%s.png" % color)
    return "data:image/png;base64," + _b64(ruta)


# Las imagenes se emiten UNA vez como clase CSS y se referencian por
# nombre de clase, para que el kit no repita el mismo base64 en cada pieza.
_IMAGENES = {}


def _registrar(clase, ruta):
    if clase not in _IMAGENES:
        _IMAGENES[clase] = "data:image/jpeg;base64," + _b64(ruta)
    return clase


def foto(nombre):
    """Devuelve la clase CSS de una foto de producto."""
    clase = "f-" + os.path.splitext(nombre)[0]
    return _registrar(clase, os.path.join(ROOT, "assets", "fotos", nombre))


def acabado(nombre):
    """Devuelve la clase CSS de una muestra Gravitec."""
    clase = "a-" + nombre.lower()
    return _registrar(clase, os.path.join(ROOT, "assets", "acabados",
                                          "%s.jpg" % nombre.lower()))


def css_imagenes():
    """El bloque CSS con todas las imagenes usadas, una sola vez."""
    return "".join(".%s{background-image:url(%s)}" % (c, d)
                   for c, d in sorted(_IMAGENES.items()))


# ------------------------------------------------------------------- CSS
# Todo se mide en la unidad --u (= ancho/1080), así las mismas reglas
# sirven para 1080 y para 1200 de ancho.
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
.board{
  position:relative;overflow:hidden;background:%(fondo)s;color:%(blanco)s;
  font-family:'Cera Pro',Poppins,system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;isolation:isolate;
}

/* ---------- capas de fondo ---------- */
.bg{position:absolute;inset:0;z-index:0;background-size:cover;background-position:center}
.bg.top{background-position:center 22%%}
.velo{position:absolute;inset:0;z-index:1}
.velo.abajo{background:linear-gradient(to top,
  rgba(1,49,61,.97) 0%%,rgba(1,49,61,.94) 32%%,rgba(1,49,61,.66) 66%%,
  rgba(1,49,61,.28) 100%%)}
.velo.plano{background:rgba(1,49,61,.80)}
.velo.suave{background:linear-gradient(to top,
  rgba(1,49,61,.95) 0%%,rgba(1,49,61,.72) 42%%,rgba(1,49,61,.22) 78%%,
  rgba(1,49,61,.10) 100%%)}
.velo.arriba{background:linear-gradient(to bottom,
  rgba(1,49,61,.96) 0%%,rgba(1,49,61,.80) 30%%,rgba(1,49,61,.20) 72%%,
  rgba(1,49,61,.06) 100%%)}

/* ---------- rejilla de la pieza ---------- */
.lienzo{position:absolute;inset:0;z-index:2;display:flex;flex-direction:column;
  padding:calc(var(--u)*68);padding-bottom:calc(var(--u)*196)}
.lienzo.sin-pie{padding-bottom:calc(var(--u)*68)}
.lienzo.abajo{justify-content:flex-end}
.lienzo.centro{justify-content:center}
.lienzo.entre{justify-content:space-between}
.pila{display:flex;flex-direction:column;gap:calc(var(--u)*44)}
.empuja{margin-top:auto}

/* ---------- tipografía ---------- */
.ante{font-weight:500;text-transform:uppercase;letter-spacing:.3em;
  font-size:calc(var(--u)*20);line-height:1.3;color:%(formentera)s}
.ante.blanca{color:rgba(255,255,255,.72)}
.tit{font-weight:900;text-transform:uppercase;letter-spacing:-.02em;
  line-height:.94;font-size:calc(var(--u)*104)}
.tit.xl{font-size:calc(var(--u)*132)}
.tit.l{font-size:calc(var(--u)*88)}
.tit.m{font-size:calc(var(--u)*66)}
.tit.s{font-size:calc(var(--u)*50);line-height:1.0}
.tit em{font-style:normal;color:%(formentera)s}
.txt{font-weight:400;font-size:calc(var(--u)*27);line-height:1.55;
  color:rgba(255,255,255,.86);max-width:calc(var(--u)*760)}
.txt b{font-weight:400;color:%(formentera)s}
.txt.sm{font-size:calc(var(--u)*23)}
.etq{font-weight:500;text-transform:uppercase;letter-spacing:.22em;
  font-size:calc(var(--u)*17);color:rgba(255,255,255,.55)}
.mt-s{margin-top:calc(var(--u)*18)}
.mt{margin-top:calc(var(--u)*30)}
.mt-l{margin-top:calc(var(--u)*48)}

/* ---------- filete y detalles ---------- */
.filete{width:calc(var(--u)*86);height:calc(var(--u)*4);background:%(formentera)s;
  border:0}
.filete.ancho{width:100%%;height:1px;background:rgba(255,255,255,.16)}
.banda{position:absolute;z-index:2;left:0;right:0;top:0;
  padding:calc(var(--u)*62) calc(var(--u)*68) calc(var(--u)*54);
  background:linear-gradient(to bottom,%(fondo)s 0%%,%(fondo)s 72%%,
    rgba(1,49,61,0) 100%%)}

/* ---------- firma de pieza ---------- */
.pfo{font-weight:900;text-transform:uppercase;line-height:.92;
  font-size:calc(var(--u)*22);letter-spacing:.01em;color:rgba(255,255,255,.5)}
.scrim{position:absolute;z-index:3;left:0;right:0;bottom:0;
  height:calc(var(--u)*230);pointer-events:none;
  background:linear-gradient(to top,rgba(1,49,61,.92),rgba(1,49,61,0))}
/* El wordmark va como imagen de fondo en una caja de tamano fijo.
   Como <img> se recorta en headless cuando cuelga de una caja
   posicionada con 'bottom'. 172 x 476/1152 = 71,0625. */
.marca{width:calc(var(--u)*172);height:calc(var(--u)*71.0625);
  flex:0 0 auto;background-repeat:no-repeat;background-position:center;
  background-size:100%% 100%%}
.pie{position:absolute;z-index:4;left:calc(var(--u)*68);right:calc(var(--u)*68);
  bottom:calc(var(--u)*62);display:flex;align-items:flex-end;
  justify-content:space-between;gap:calc(var(--u)*24)}
.contador{font-weight:500;font-size:calc(var(--u)*20);letter-spacing:.16em;
  color:rgba(255,255,255,.6)}
.desliza{display:flex;align-items:center;gap:calc(var(--u)*12);
  font-weight:500;text-transform:uppercase;letter-spacing:.22em;
  font-size:calc(var(--u)*17);color:%(formentera)s}
.desliza svg{width:calc(var(--u)*30);height:calc(var(--u)*14)}

/* ---------- cifras ---------- */
.cifra{font-weight:900;line-height:.88;letter-spacing:-.03em;
  font-size:calc(var(--u)*190);color:%(formentera)s}
.cifra .un{font-size:calc(var(--u)*54);letter-spacing:0}
.fuente{font-weight:400;font-size:calc(var(--u)*18);color:rgba(255,255,255,.45);
  letter-spacing:.02em}

/* ---------- listas ---------- */
.lista{display:flex;flex-direction:column;gap:calc(var(--u)*26);
  margin-top:calc(var(--u)*40)}
.item{display:flex;gap:calc(var(--u)*22);align-items:flex-start}
.item .n{font-weight:900;font-size:calc(var(--u)*24);color:%(formentera)s;
  min-width:calc(var(--u)*44);padding-top:calc(var(--u)*3)}
.item .c{font-weight:400;font-size:calc(var(--u)*28);line-height:1.4;
  color:rgba(255,255,255,.92)}
.item .c strong{font-weight:900;display:block;text-transform:uppercase;
  letter-spacing:.01em;font-size:calc(var(--u)*30);color:%(blanco)s;
  margin-bottom:calc(var(--u)*6)}

/* ---------- mosaico de acabados ---------- */
.mosaico{position:absolute;inset:0;z-index:0;display:grid}
.mosaico.dentro{top:calc(var(--u)*330);bottom:calc(var(--u)*152)}
.mosaico .t{position:relative;background-size:cover;background-position:center}
.mosaico .t span{position:absolute;left:calc(var(--u)*10);
  bottom:calc(var(--u)*10);font-weight:900;text-transform:uppercase;
  font-size:calc(var(--u)*18);letter-spacing:.04em;color:#fff;
  padding:calc(var(--u)*5) calc(var(--u)*10);background:rgba(1,25,32,.62)}

/* ---------- fichas de producto ---------- */
.mitad{position:absolute;z-index:0;left:0;right:0;top:0;height:52%%;
  background-size:cover;background-position:center}
.mitad::after{content:"";position:absolute;left:0;right:0;bottom:0;
  height:calc(var(--u)*90);
  background:linear-gradient(to top,%(fondo)s 6%%,rgba(1,49,61,0))}
.lienzo.bajo-mitad{justify-content:flex-end}
.tarjeta{position:absolute;z-index:0;left:0;right:0;top:0;height:60%%;
  background:linear-gradient(155deg,#0a4a59,#01313D 70%%)}
.tarjeta .foto{position:absolute;inset:calc(var(--u)*54) calc(var(--u)*62);
  background-repeat:no-repeat;background-position:center;
  background-size:contain}
.tarjeta::after{content:"";position:absolute;left:0;right:0;bottom:0;
  height:calc(var(--u)*130);
  background:linear-gradient(to top,%(fondo)s,rgba(1,49,61,0))}
.lienzo.bajo-tarjeta{justify-content:flex-end}
.precio{display:inline-flex;align-items:baseline;gap:calc(var(--u)*10);
  margin-top:calc(var(--u)*26);padding:calc(var(--u)*14) calc(var(--u)*24);
  border:1px solid rgba(0,173,181,.55);background:rgba(0,173,181,.10)}
.precio .d{font-weight:500;text-transform:uppercase;letter-spacing:.2em;
  font-size:calc(var(--u)*15);color:rgba(255,255,255,.7)}
.precio .v{font-weight:900;font-size:calc(var(--u)*40);color:%(formentera)s;
  letter-spacing:-.02em}
.precio .u{font-weight:400;font-size:calc(var(--u)*20);
  color:rgba(255,255,255,.7)}

/* ---------- rejilla de catálogo ---------- */
.rejilla{display:grid;gap:calc(var(--u)*12);margin-top:calc(var(--u)*40)}
.rejilla .c{position:relative;background-size:cover;background-position:center;
  aspect-ratio:1/1}
.rejilla .c b{position:absolute;left:calc(var(--u)*14);
  bottom:calc(var(--u)*12);font-weight:900;text-transform:uppercase;
  font-size:calc(var(--u)*18);letter-spacing:.02em;
  text-shadow:0 calc(var(--u)*2) calc(var(--u)*8) rgba(1,25,32,.8)}

/* ---------- hueco de foto pendiente ---------- */
.hueco{position:absolute;inset:0;z-index:0;
  background:linear-gradient(150deg,#04404e,#01313D 55%%,#052f3a);
  display:flex;align-items:center;justify-content:center}
.hueco .marco{position:absolute;inset:calc(var(--u)*40);
  border:calc(var(--u)*3) dashed rgba(0,173,181,.55)}
.hueco .av{position:relative;text-align:center;max-width:74%%;font-weight:900;
  text-transform:uppercase;letter-spacing:.16em;font-size:calc(var(--u)*26);
  line-height:1.8;color:%(formentera)s;margin-bottom:calc(var(--u)*120)}

/* ---------- tabla de precios ---------- */
.tabla{width:100%%;margin-top:calc(var(--u)*36);border-collapse:collapse;
  font-size:calc(var(--u)*23)}
.tabla th{font-weight:500;text-transform:uppercase;letter-spacing:.18em;
  font-size:calc(var(--u)*15);color:rgba(255,255,255,.55);text-align:right;
  padding:0 0 calc(var(--u)*14) 0;border-bottom:1px solid rgba(255,255,255,.16)}
.tabla th:first-child{text-align:left}
.tabla td{padding:calc(var(--u)*17) 0;text-align:right;font-weight:900;
  color:%(formentera)s;border-bottom:1px solid rgba(255,255,255,.08)}
.tabla td:first-child{text-align:left;font-weight:400;color:#fff}
""" % {"fondo": FONDO, "formentera": FORMENTERA, "blanco": BLANCO,
       "deep": DEEP}

FLECHA = ('<svg viewBox="0 0 30 14" fill="none" stroke="currentColor" '
          'stroke-width="2"><path d="M0 7h27M21 1l6 6-6 6"/></svg>')

PFO = '<div class="pfo">PLASTIC<br>FREE<br>OCEANS</div>'
