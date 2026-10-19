#!/usr/bin/env python3
"""Descifra la copia del panel que el workflow guarda como artefacto.

    APERTURAS_KEY=… python3 bridge/descifrar_panel.py relanzamiento.bin > panel.html

El fichero lo deja la fase PANEL del puente (cifrar_panel) en PANEL_SALIDA y
el workflow lo sube como artefacto «panel» de cada pasada. La clave es la
misma que la del receptor: el secreto APERTURAS_KEY de GitHub, que es la
propiedad CLAVE del script de Apps Script.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apollo_hubspot_bridge import descifrar_panel  # noqa: E402


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    clave = os.environ.get("APERTURAS_KEY", "")
    if not clave:
        sys.exit("Falta APERTURAS_KEY en el entorno")
    with open(sys.argv[1], "rb") as f:
        sys.stdout.write(descifrar_panel(f.read(), clave))


if __name__ == "__main__":
    main()
