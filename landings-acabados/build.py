#!/usr/bin/env python3
"""Genera las 12 landings de acabados Gravitec® + índice en dist/.

Uso:  python3 build.py            -> HTML autocontenidos (fuentes, logo e imágenes en base64)
      python3 build.py --linked   -> HTML que enlazan a ../img/ y ../assets/ (más ligeros, para servir en web)

Edita datos.json (textos y datos) y template.html (maqueta). No toques dist/ a mano.
"""
import base64, json, mimetypes, sys, html
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
DIST = HERE / "dist"
LINKED = "--linked" in sys.argv

data = json.loads((HERE / "datos.json").read_text())
C, G, ACAB = data["comun"], data["grupos"], data["acabados"]
TPL = (HERE / "template.html").read_text()
LOGO = (HERE / "assets" / "logo-gw-simple.svg").read_text().strip()


def src(rel):
    """Ruta relativa dentro de landings-acabados/ -> data URI o ruta relativa desde dist/."""
    p = HERE / rel
    if LINKED:
        return "../" + rel
    mime = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def font_face(weight, style, file):
    p = ROOT / "assets" / "fonts" / file
    if not p.exists():
        return ""
    if LINKED:
        url = f"../../assets/fonts/{file}"
    else:
        url = f"data:font/woff2;base64,{base64.b64encode(p.read_bytes()).decode()}"
    return (f"@font-face{{font-family:'Cera Pro';font-weight:{weight};font-style:{style};"
            f"font-display:swap;src:url({url}) format('woff2')}}")


FONTS = "\n".join([
    font_face(400, "normal", "CeraPro-Regular-latin.woff2"),
    font_face(500, "normal", "CeraPro-Medium-latin.woff2"),
    font_face("700 900", "normal", "CeraPro-Black-latin.woff2"),
    font_face(900, "italic", "CeraPro-BlackItalic-latin.woff2"),
])
if not FONTS.strip():
    print("AVISO: no se encontraron las fuentes Cera Pro en assets/fonts; se usará Poppins/system-ui")

e = html.escape
LAZY = ' loading="lazy"' if LINKED else ""  # con base64 el lazy solo retrasa el pintado


def render(tpl, ctx):
    out = tpl
    for k, v in ctx.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def cifras_html():
    parts = []
    for c in C["cifras"]:
        pre = f'<span class="pre">{e(c["prefijo"])}</span>' if c.get("prefijo") else ""
        parts.append(f'<div><div class="num">{pre}{e(c["valor"])}<small>{e(c["unidad"])}</small></div>'
                     f'<div class="lbl">{e(c["etiqueta"])}</div></div>')
    return "".join(parts)


def formatos_html():
    return "".join(
        f'<li><span class="t">{e(f["talla"])}</span><span class="m">{e(f["medida"])}</span>'
        f'<span class="p">{e(f["plazo"])}</span><span class="d">{e(f["m2"])} · {e(f["espesores"])}</span></li>'
        for f in C["formatos"])


def props_html(grupo):
    return "".join(
        f'<div><div class="v">{e(t["valor"])}<small>{e(t["unidad"])}</small></div><div class="k">{e(t["prop"])}</div></div>'
        for t in G[grupo]["tecnica"][:6])


def chips(items):
    return "".join(f"<li>{e(i)}</li>" for i in items)


def circular_html():
    return "".join(f'<div><h3>{e(c["titulo"])}</h3><p>{e(c["texto"])}</p></div>' for c in C["circular"])


def uso_html(a):
    return "".join(
        f'<figure><img src="{src("img/uso/" + f + ".jpg")}" alt="{e(cap)}"{LAZY}><figcaption>{e(cap)}</figcaption></figure>'
        for f, cap in a["uso"])


def otros_html(actual):
    return "".join(
        f'<a href="{o["slug"]}.html"><img src="{src("img/thumb/" + o["slug"] + ".jpg")}" alt="Acabado {e(o["nombre"])}"{LAZY}><span>{e(o["nombre"])}</span></a>'
        for o in ACAB if o["slug"] != actual)


def build_landing(i, a):
    mano = f'img/mano/{a["mano"]}.jpg' if a.get("mano") else f'img/estudio/{a["estudio"]}.jpg'
    ctx = {
        "fonts_css": FONTS, "logo": LOGO,
        "nombre": e(a["nombre"]), "nombre_url": a["nombre"].replace(" ", "%20"),
        "num": f"{i:02d}", "chars": str(len(a["nombre"])), "tagline": e(a["tagline"]), "titulo": e(a["titulo"]),
        "descripcion": e(a["descripcion"]), "base": e(a["base"]), "veta": e(a["veta"]), "caracter": e(a["caracter"]),
        "img_textura": src(f'img/textura/{a["slug"]}.jpg'), "img_mano": src(mano),
        "mano_clase": "" if a.get("mano") else "retrato",
        "img_redes": src("img/comun/redes.jpg"),
        "nota_muestra": e(C["nota_muestra"]), "nota_tecnica": e(C["nota_tecnica"]),
        "cifras": cifras_html(), "uso": uso_html(a),
        "grupo_nombre": e(G[a["grupo"]]["nombre"]), "composicion": e(G[a["grupo"]]["composicion"]),
        "formatos": formatos_html(), "textura": e(C["textura"]), "props": props_html(a["grupo"]),
        "trabajo": chips(C["trabajo"]), "avisos": "".join(f"<div>{e(x)}</div>" for x in C["avisos"]),
        "aplicaciones": chips(C["aplicaciones"]), "circular": circular_html(), "otros": otros_html(a["slug"]),
        "email": C["email"], "web": C["web"], "web_url": C["web_url"],
    }
    return render(TPL, ctx)


INDEX_TPL = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Acabados Gravitec® · Gravity Wave</title><meta name="theme-color" content="#01313D">
<style>{{fonts_css}}
:root{--fondo:#01313D;--formentera:#00ADB5;--blanco:#fff}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Cera Pro',Poppins,system-ui,sans-serif;background:var(--fondo);color:var(--blanco);line-height:1.6;font-size:17px}
a{color:inherit;text-decoration:none}.wrap{width:min(1180px,100% - 2.5rem);margin-inline:auto}
.eyebrow{font-weight:500;font-size:.7rem;letter-spacing:.3em;text-transform:uppercase;color:var(--formentera)}
h1{font-weight:900;letter-spacing:-.02em;line-height:.96;text-transform:uppercase;font-size:clamp(3rem,9vw,7rem);margin:.6rem 0 1rem}
header{padding:2rem 0 1rem;display:flex;justify-content:space-between;align-items:center}.logo{width:130px;color:#fff}.logo svg{width:100%;height:auto;display:block}
.intro{padding:3rem 0 2rem}.intro p{max-width:34em}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;padding-bottom:5rem}
.grid a{position:relative;display:block;aspect-ratio:4/5;overflow:hidden;border-radius:2px;isolation:isolate}
.grid img{width:100%;height:100%;object-fit:cover;transition:transform .35s;display:block}
.grid a:hover img{transform:scale(1.05)}
.grid .lb{position:absolute;inset:auto 0 0 0;padding:1rem;background:linear-gradient(to top,rgba(1,49,61,.92),rgba(1,49,61,0));z-index:1}
.grid .n{font-weight:900;font-size:clamp(1.3rem,3vw,2rem);letter-spacing:-.02em;text-transform:uppercase;line-height:1;display:block}
.grid .s{font-size:.7rem;letter-spacing:.25em;text-transform:uppercase;font-weight:500;opacity:.8;display:block;margin-bottom:.3rem}
footer{padding:2rem 0 3rem;border-top:1px solid rgba(255,255,255,.14);font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;opacity:.75;font-weight:500}
@media(min-width:760px){.grid{grid-template-columns:repeat(4,1fr);gap:1.2rem}.logo{width:150px}}
</style></head><body>
<div class="wrap"><header><a class="logo" href="{{web_url}}" aria-label="Gravity Wave">{{logo}}</a><span class="eyebrow">Gravitec® by Gravity Wave</span></header>
<div class="intro"><p class="eyebrow">Doce acabados · un solo material</p><h1>Elige tu acabado</h1><p>Paneles fabricados con redes de pesca recicladas del Mediterráneo. Toca un acabado para ver su ficha: color, formatos, propiedades y usos.</p></div>
<div class="grid">{{cards}}</div>
<footer>Gravity Wave · Plastic Free Oceans · {{web}}</footer></div>
</body></html>"""


def build_index():
    cards = "".join(
        f'<a href="{a["slug"]}.html"><img src="{src("img/thumb/" + a["slug"] + ".jpg")}" alt="Acabado {e(a["nombre"])}"{LAZY}>'
        f'<span class="lb"><span class="s">{i:02d}</span><span class="n">{e(a["nombre"])}</span></span></a>'
        for i, a in enumerate(ACAB, 1))
    return render(INDEX_TPL, {"fonts_css": FONTS, "logo": LOGO, "cards": cards, "web": C["web"], "web_url": C["web_url"]})


if __name__ == "__main__":
    DIST.mkdir(exist_ok=True)
    for i, a in enumerate(ACAB, 1):
        out = DIST / f'{a["slug"]}.html'
        out.write_text(build_landing(i, a))
        print(f"{out.name:18s} {out.stat().st_size/1024:7.0f} KB")
    (DIST / "index.html").write_text(build_index())
    print("index.html", round((DIST / "index.html").stat().st_size / 1024), "KB")
