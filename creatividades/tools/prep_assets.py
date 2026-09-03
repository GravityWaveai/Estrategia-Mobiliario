#!/usr/bin/env python3
"""Prepara los assets de las creatividades de RRSS.

Lee las fotos reales de producto y las 12 muestras Gravitec de la skill
`interactive-product-customizer`, las optimiza y las deja en
`creatividades/assets/`. Idempotente: se puede relanzar.

Uso:  python3 creatividades/tools/prep_assets.py [--src RUTA_ASSETS_SKILL]
"""
import argparse
import glob
import os
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FOTOS = os.path.join(ROOT, "assets", "fotos")
OUT_ACAB = os.path.join(ROOT, "assets", "acabados")

# Fotos reales de producto. (fichero origen, nombre destino, ancho máximo)
FOTOS = [
    ("banco_urbano.jpg",        "banco-urbano.jpg",   1400),
    ("banco_nero_base.jpg",     "banco-nero.jpg",     1100),
    ("mesa_palaia_base.jpg",    "mesa-palaia.jpg",    1200),
    ("papelera_sorell_base.jpg","papelera-sorell.jpg",1000),
    ("papelera_cubica.jpg",     "papelera-cubica.jpg", 900),
    ("taburete_base.jpg",       "taburete-melva.jpg",  800),
    ("posavasos.jpg",           "posavasos.jpg",       900),
    ("letras_base.jpg",         "letrero-corporeo.jpg",1200),
]

# Los 12 acabados Gravitec® 2026, en el orden del catálogo.
ACABADOS = ["Cadaques", "Vulcano", "Sicilia", "Ifach", "Palermo", "Formentera",
            "Capri", "Itaca", "Andros", "Niza", "Atenas", "Marsella"]

# Las muestras traen una franja clara de mesa en el borde inferior.
RECORTE_INFERIOR = 0.10


def encontrar_origen(ruta_cli):
    if ruta_cli:
        return ruta_cli
    patron = os.path.expanduser(
        "~/.claude/skills/synced/*/interactive-product-customizer/assets")
    for candidato in sorted(glob.glob(patron)):
        if os.path.isdir(candidato):
            return candidato
    return None


def guardar(im, destino, calidad=86):
    im.convert("RGB").save(destino, "JPEG", quality=calidad, optimize=True,
                           progressive=True)
    return os.path.getsize(destino)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", help="assets/ de la skill interactive-product-customizer")
    args = ap.parse_args()

    src = encontrar_origen(args.src)
    if not src:
        sys.exit("No encuentro los assets de la skill; pásalos con --src")

    os.makedirs(OUT_FOTOS, exist_ok=True)
    os.makedirs(OUT_ACAB, exist_ok=True)

    for origen, destino, ancho in FOTOS:
        ruta = os.path.join(src, "products", origen)
        if not os.path.exists(ruta):
            print("  falta %s" % origen)
            continue
        im = Image.open(ruta)
        if im.width > ancho:
            im = im.resize((ancho, round(im.height * ancho / im.width)),
                           Image.LANCZOS)
        kb = guardar(im, os.path.join(OUT_FOTOS, destino)) // 1024
        print("  foto     %-22s %dx%d  %d KB" % (destino, im.width, im.height, kb))

    for nombre in ACABADOS:
        ruta = os.path.join(src, "swatches", "%s.png" % nombre)
        if not os.path.exists(ruta):
            print("  falta acabado %s" % nombre)
            continue
        im = Image.open(ruta).convert("RGB")
        # Fuera la franja de mesa del borde inferior y a cuadrado.
        im = im.crop((0, 0, im.width, round(im.height * (1 - RECORTE_INFERIOR))))
        lado = min(im.width, im.height)
        izq = (im.width - lado) // 2
        arr = (im.height - lado) // 2
        im = im.crop((izq, arr, izq + lado, arr + lado)).resize((640, 640),
                                                                Image.LANCZOS)
        kb = guardar(im, os.path.join(OUT_ACAB, "%s.jpg" % nombre.lower())) // 1024
        print("  acabado  %-22s 640x640  %d KB" % (nombre, kb))

    wordmark_png()




# --------------------------------------------------------------------------
# El wordmark en PNG transparente.
#
# Por que PNG y no el SVG: al rasterizar el SVG del wordmark dentro de una
# caja posicionada con "bottom" (el pie de las piezas), Chrome headless
# pinta solo la parte de arriba del trazado y corta la palabra WAVE por la
# mitad; da igual si va como <img>, en linea o como background-image.
#
# Y por que desde el logo COMPLETO y recortando con Pillow: rasterizar el
# SVG ya recortado tambien pierde el borde inferior. Rasterizamos el logo
# oficial entero, que sale exacto, y recortamos la banda del wordmark con
# las coordenadas medidas sobre ese mismo render.
LOGO_OFICIAL = "logo-gravity-blanco.svg"
# Banda del wordmark en el sistema del logo oficial (viewBox 0 0 2000 2000):
# GRAVITY ocupa y 748..880 y WAVE y 932..1223; ambas x 450..1601.
BANDA = (450, 748, 1602, 1224)
LADO = 2000


def _svg_logo_oficial():
    """El SVG del logo oficial: en el repo, o en la skill de propuestas."""
    local = os.path.join(ROOT, "assets", LOGO_OFICIAL)
    if os.path.exists(local):
        return local
    patron = os.path.expanduser(
        "~/.claude/skills/synced/*/gravity-wave-propuestas/assets/" + LOGO_OFICIAL)
    for c in sorted(glob.glob(patron)):
        return c
    return None


def wordmark_png(escala=2):
    import base64
    import subprocess
    import tempfile

    exe = next((c for c in (
        "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
        "/usr/bin/chromium", "/usr/bin/google-chrome") if os.path.exists(c)),
        None)
    origen = _svg_logo_oficial()
    if not exe or not origen:
        print("  sin Chrome o sin logo oficial: no regenero el PNG")
        return

    bruto = open(origen).read()
    lado = LADO * escala
    izq, arr, der, aba = [v * escala for v in BANDA]

    for variante, relleno in (("blanco", "#FFFFFF"), ("negro", "#101820")):
        # En el archivo oficial .st1 es el trazo visible y .st0 el oculto.
        svg = (bruto.replace(".st1{fill:#FFFFFF;}", ".st1{fill:%s;}" % relleno)
                    .replace(".st0{fill:#222220;}", ".st0{fill:none;}"))
        uri = "data:image/svg+xml;base64," + base64.b64encode(
            svg.encode()).decode()
        tmp = tempfile.mkdtemp(prefix="gw-wm-")
        try:
            pagina = os.path.join(tmp, "wm.html")
            with open(pagina, "w") as f:
                f.write("<!doctype html><body style='margin:0'>"
                        "<img src='%s' width='%d' height='%d' "
                        "style='display:block'></body>" % (uri, lado, lado))
            crudo = os.path.join(tmp, "crudo.png")
            subprocess.run([exe, "--headless=new", "--no-sandbox",
                            "--disable-gpu", "--hide-scrollbars",
                            "--force-device-scale-factor=1",
                            "--default-background-color=00000000",
                            "--virtual-time-budget=3000",
                            "--screenshot=%s" % crudo,
                            "--window-size=%d,%d" % (lado, lado), pagina],
                           capture_output=True)
            if not os.path.exists(crudo):
                print("  no pude rasterizar el logo (%s)" % variante)
                continue
            im = Image.open(crudo).convert("RGBA").crop((izq, arr, der, aba))
            im = im.resize((1152, 476), Image.LANCZOS)
            destino = os.path.join(ROOT, "assets",
                                   "logo-gw-wordmark-%s.png" % variante)
            im.save(destino, optimize=True)
            caja = im.getbbox()
            print("  wordmark %-8s %dx%d  %d KB  ink=%s"
                  % (variante, im.width, im.height,
                     os.path.getsize(destino) // 1024, caja))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
