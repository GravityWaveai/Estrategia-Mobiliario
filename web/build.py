#!/usr/bin/env python3
"""Genera las salidas de la landing a partir de web/src/:

  web/index.html            página completa autocontenida (hosting estático, artifact)
  web/elementor.html        fragmento autocontenido con CSS acotado bajo #gw-mob
  web/elementor-light.html  el mismo fragmento pero con las imágenes en Medios de
                            WordPress (~65 KB): es el que se pega en Elementor,
                            porque 1,5 MB dentro del JSON de Elementor suele
                            colgar el guardado (límites de POST / firewall).
                            Las imágenes de web/src/img/ se suben a Medios y la
                            constante GW_IMG_BASE del fragmento apunta a su ruta.

Uso:  python3 web/build.py

Fuentes: assets/fonts/*-latin.woff2 · Imágenes: web/src/img/*.jpg
Los placeholders {{FONT:x}} / {{IMG:x}} del template se sustituyen por base64.
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web" / "src"
TEMPLATE = SRC / "landing-template.html"
WRAP_ID = "gw-mob"


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def inline_assets(html: str) -> str:
    def sub(m):
        kind, name = m.groups()
        if kind == "FONT":
            return b64(ROOT / "assets" / "fonts" / f"{name}.woff2")
        return b64(SRC / "img" / f"{name}.jpg")

    out = re.sub(r"\{\{(FONT|IMG):([A-Za-z0-9_-]+)\}\}", sub, html)
    missing = re.findall(r"\{\{[^}]+\}\}", out)
    assert not missing, f"Placeholders sin resolver: {missing}"
    return out


def prefix_selector(sel: str) -> str | None:
    """Acota un selector bajo #gw-mob. Devuelve None si hay que descartarlo."""
    sel = sel.strip()
    if not sel:
        return None
    if sel == "html":
        return None  # el fragmento no controla <html>
    if sel in (":root", "body"):
        return f"#{WRAP_ID}"
    if sel.startswith("html"):
        return None
    if sel.startswith("body"):
        return f"#{WRAP_ID}" + sel[len("body"):]
    return f"#{WRAP_ID} {sel}"


def scope_css(css: str) -> str:
    """Prefija cada regla con #gw-mob. Soporta un nivel de @media; los
    @font-face se dejan tal cual (son globales). Los comentarios se eliminan
    antes: pegados a un selector lo invalidarían."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        brace = css.find("{", i)
        if brace == -1:
            out.append(css[i:])
            break
        header = css[i:brace].strip()
        if header.startswith("@font-face"):
            end = css.find("}", brace)
            out.append(css[i:end + 1] + "\n")
            i = end + 1
        elif header.startswith("@media"):
            depth, j = 1, brace + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            inner = css[brace + 1:j - 1]
            out.append(f"{header}{{{scope_css(inner)}}}\n")
            i = j
        else:
            end = css.find("}", brace)
            decls = css[brace + 1:end]
            sels = [prefix_selector(s) for s in header.split(",")]
            sels = [s for s in sels if s]
            if sels:
                out.append(f"{','.join(sels)}{{{decls}}}\n")
            i = end + 1
    return "".join(out)


def build_elementor(html: str) -> str:
    style = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    body = re.search(r"<body>(.*)</body>", html, re.S).group(1)
    scoped = scope_css(style)
    # Blindaje extra frente al CSS del tema / Elementor
    scoped += (
        f"\n#{WRAP_ID} img{{border:none;box-shadow:none;height:auto}}"
        f"\n#{WRAP_ID} .fam .media img,#{WRAP_ID} .hero .bleed,"
        f"#{WRAP_ID} .close .bleed,#{WRAP_ID} .pasos img,"
        f"#{WRAP_ID} .swatches img{{height:100%}}"
        f"\n#{WRAP_ID} .pasos img{{height:auto;aspect-ratio:9/8}}"
        f"\n#{WRAP_ID} .swatches img{{height:auto;aspect-ratio:3/2}}"
        f"\n#{WRAP_ID} a{{text-decoration:none}}"
        # Los temas estilan h1-h3/p/label directamente; eso gana a la herencia
        # del wrapper, así que se fuerza la herencia elemento a elemento.
        f"\n#{WRAP_ID} h1,#{WRAP_ID} h2,#{WRAP_ID} h3{{margin:0;padding:0;"
        f"font-family:inherit;color:inherit;border:none;text-shadow:none}}"
        f"\n#{WRAP_ID} p,#{WRAP_ID} ul,#{WRAP_ID} figure,#{WRAP_ID} dl{{margin:0;padding:0}}"
        f"\n#{WRAP_ID} label{{color:inherit;font-family:inherit}}"
        f"\n#{WRAP_ID} input,#{WRAP_ID} select,#{WRAP_ID} textarea,#{WRAP_ID} button{{"
        f"font-family:var(--f);box-shadow:none}}"
    )
    return (
        "<!-- Landing Mobiliario Urbano Gravitec — fragmento para widget HTML de Elementor.\n"
        "     Generado por web/build.py: no editar a mano, editar web/src/ y regenerar. -->\n"
        f'<div id="{WRAP_ID}">\n<style>{scoped}</style>\n{body}\n</div>\n'
    )


IMG_BASE_DEFAULT = "/wp-content/uploads/2026/08/"


def externalize_images(html: str) -> str:
    """Sustituye cada imagen embebida por data-gw="nombre.jpg"; un pequeño
    loader las resuelve contra GW_IMG_BASE (la carpeta de Medios de WP)."""
    out = re.sub(
        r'src="data:image/jpeg;base64,\{\{IMG:([A-Za-z0-9_-]+)\}\}"',
        r'data-gw="\1.jpg"',
        html,
    )
    loader = (
        "<script>\n"
        "// Ruta de las imágenes en Medios de WordPress. Si al subirlas la URL\n"
        "// resultante es otra (año/mes distinto), cambiar SOLO esta línea.\n"
        f'var GW_IMG_BASE = "{IMG_BASE_DEFAULT}";\n'
        "document.querySelectorAll('#" + WRAP_ID + " [data-gw]').forEach(function (im) {\n"
        "  im.src = GW_IMG_BASE + im.getAttribute('data-gw');\n"
        "});\n"
        "</script>"
    )
    # el loader va justo tras el contenido, antes del script principal
    return out.replace("<script>\n// ——— Configuración HubSpot",
                       loader + "\n<script>\n// ——— Configuración HubSpot")


def main() -> None:
    template = TEMPLATE.read_text()
    full = inline_assets(template)
    (ROOT / "web" / "index.html").write_text(full)
    print(f"web/index.html            {len(full) // 1024} KB")
    embed = build_elementor(full)
    (ROOT / "web" / "elementor.html").write_text(embed)
    print(f"web/elementor.html        {len(embed) // 1024} KB")
    light = build_elementor(inline_assets(externalize_images(template)))
    (ROOT / "web" / "elementor-light.html").write_text(light)
    print(f"web/elementor-light.html  {len(light) // 1024} KB")


if __name__ == "__main__":
    main()
