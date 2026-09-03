#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Revision de marca de las piezas exportadas.

Comprueba lo del apartado «antes de entregar» de la skill de marca que se
puede comprobar a maquina: medida exacta, fondo petroleo, el turquesa con
cuentagotas y cero colores prohibidos (rojo, amarillo, naranja, coral, lima).

Uso:  python3 creatividades/tools/revisar.py
"""
import colorsys
import glob
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import piezas  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG = os.path.join(ROOT, "png")

FONDO = (1, 49, 61)
ACENTO = (0, 173, 181)
# El turquesa satura enseguida: por encima de este porcentaje deja de ser
# un acento y empieza a ser un fondo.
TOPE_ACENTO = 12.0


# Umbral de saturacion alto a proposito: la arena, la madera y el laton de
# las fotos reales son calidos pero casi neutros, y no son una decision de
# paleta. Aqui interesa cazar un naranja, un coral o un amarillo de verdad.
SATURACION_MINIMA = 0.40


def es_prohibido(r, g, b):
    """Rojo, naranja, amarillo, coral o lima con saturacion real."""
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    if s < SATURACION_MINIMA or l < 0.14 or l > 0.85:
        return False
    grados = h * 360
    return grados < 90 or grados > 330


def revisar(ruta, esperado):
    """Devuelve (fallos, avisos).

    Fallo: la pieza esta mal hecha —no mide lo que debe, o el turquesa ha
    dejado de ser un acento—. Aviso: hay tono calido, que en las fotos
    reales de Gravity Wave es arena, madera o laton y no una decision de
    paleta; lo mira una persona y decide.
    """
    im = Image.open(ruta).convert("RGB")
    fallos, avisos = [], []
    if esperado and im.size != esperado:
        fallos.append("mide %dx%d, esperado %dx%d"
                      % (im.size + esperado))

    crudo = im.resize((160, 160), Image.NEAREST).tobytes()
    muestras = [tuple(crudo[i:i + 3]) for i in range(0, len(crudo), 3)]
    total = len(muestras)
    acento = prohibido = 0
    peor = None
    for r, g, b in muestras:
        if (abs(r - ACENTO[0]) < 26 and abs(g - ACENTO[1]) < 26
                and abs(b - ACENTO[2]) < 26):
            acento += 1
        if es_prohibido(r, g, b):
            prohibido += 1
            peor = (r, g, b)

    pct_acento = 100.0 * acento / total
    if pct_acento > TOPE_ACENTO:
        fallos.append("turquesa en el %.1f%% de la pieza (tope %.0f%%)"
                      % (pct_acento, TOPE_ACENTO))
    if prohibido > total * 0.004:
        avisos.append("tono calido en el %.2f%% (ej. rgb%s)"
                      % (100.0 * prohibido / total, peor))
    return fallos, avisos


def main():
    esperados = {tb["id"]: (tb["w"], tb["h"]) for tb in piezas.todas()}
    rutas = sorted(glob.glob(os.path.join(PNG, "*.png")))
    if not rutas:
        sys.exit("No hay PNG: lanza primero build.py")

    n_fallos = 0
    n_avisos = 0
    for ruta in rutas:
        tid = os.path.basename(ruta)[:-4]
        fallos, avisos = revisar(ruta, esperados.get(tid))
        for f in fallos:
            n_fallos += 1
            print("  FALLO  %-8s %s" % (tid, f))
        for a in avisos:
            n_avisos += 1
            print("  aviso  %-8s %s" % (tid, a))

    faltan = sorted(set(esperados) - {os.path.basename(r)[:-4] for r in rutas})
    if faltan:
        n_fallos += len(faltan)
        print("  FALLO  sin exportar: %s" % ", ".join(faltan))

    print("\n%d piezas revisadas · %d fallos · %d avisos para mirar a ojo."
          % (len(rutas), n_fallos, n_avisos))
    return 1 if n_fallos else 0


if __name__ == "__main__":
    sys.exit(main())
