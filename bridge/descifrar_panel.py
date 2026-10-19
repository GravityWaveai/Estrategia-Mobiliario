#!/usr/bin/env python3
"""Descifra la copia del panel que el workflow guarda como artefacto.

    HUBSPOT_TOKEN=… python3 bridge/descifrar_panel.py relanzamiento.bin > panel.html

El fichero lo deja la fase PANEL del puente (cifrar_panel) en PANEL_SALIDA y
el workflow lo sube como artefacto «panel» de cada pasada. La clave se deriva
del token de HubSpot (clave_panel), que tienen tanto el runner de GitHub como
la sesión que republica el panel; no hay que pasar ninguna otra.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apollo_hubspot_bridge import clave_panel, descifrar_panel  # noqa: E402


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if not os.environ.get("HUBSPOT_TOKEN"):
        sys.exit("Falta HUBSPOT_TOKEN en el entorno: de él se deriva la clave del panel")
    with open(sys.argv[1], "rb") as f:
        sys.stdout.write(descifrar_panel(f.read(), clave_panel()))


if __name__ == "__main__":
    main()
