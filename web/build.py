#!/usr/bin/env python3
"""Genera el fragmento HTML para el widget de Elementor de la landing de
Mobiliario Urbano. Incrusta las fuentes Cera Pro (subsets latinos de
assets/fonts) y el logo del menú, y escribe el resultado en
web/dist/mobiliario-fragmento-elementor.html.

Uso:  python3 web/build.py
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web" / "src"
DIST = ROOT / "web" / "dist"
FONTS = ROOT / "assets" / "fonts"


def b64(name: str) -> str:
    return base64.b64encode((FONTS / name).read_bytes()).decode("ascii")


def main() -> None:
    html = (SRC / "fragmento.html").read_text(encoding="utf-8")

    path_d = (SRC / "logo-path.txt").read_text(encoding="utf-8").strip()
    logo_menu = (
        '<svg class="menu-logo-svg" aria-hidden="true" focusable="false" '
        'xmlns="http://www.w3.org/2000/svg" width="53" height="24" '
        'viewBox="0 27 53 24" fill="none">'
        f'<path fill-rule="evenodd" clip-rule="evenodd" d="{path_d}" fill="white"></path>'
        "</svg>"
    )

    html = (
        html.replace("__FONT_REGULAR__", b64("CeraPro-Regular-latin.woff2"))
        .replace("__FONT_MEDIUM__", b64("CeraPro-Medium-latin.woff2"))
        .replace("__FONT_BLACK__", b64("CeraPro-Black-latin.woff2"))
        .replace("__LOGO_SVG_MENU__", logo_menu)
    )

    assert "__FONT" not in html and "__LOGO" not in html, "quedan tokens sin sustituir"

    DIST.mkdir(parents=True, exist_ok=True)
    out = DIST / "mobiliario-fragmento-elementor.html"
    out.write_text(html, encoding="utf-8")
    print(f"OK → {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
