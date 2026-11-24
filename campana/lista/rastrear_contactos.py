#!/usr/bin/env python3
"""Rastrea las webs oficiales de los ayuntamientos objetivo y saca los correos
que publican, cada uno con el texto que lo rodea y la página donde aparece.

No adivina direcciones: solo recoge lo que está escrito en la web municipal.
El resultado son datos personales de terceros y se guarda en `exports/`, que
está fuera de git (ver .gitignore). Este script no contiene ningún contacto.

Uso:
    python3 campana/lista/rastrear_contactos.py rastrear [--prioridad 1,2] [--solo COD_INE,...]
    python3 campana/lista/rastrear_contactos.py candidatos

`rastrear` es reanudable: salta los municipios que ya tienen fichero en
exports/rastreo/. `candidatos` lee esos ficheros y escribe
exports/candidatos-rastreo.csv con los correos que parecen del perfil
(Medio Ambiente, Playas, Parques y Jardines, Servicios, Obras, Vía Pública).

La clasificación es una criba, no un veredicto: cada candidato hay que leerlo
antes de pasarlo a la lista de envío.

Qué páginas abre en cada web, con un cupo por tipo para no perderse en noticias:
  G  gobierno: corporación, equipo de gobierno, concejales, delegaciones, y las
     fichas personales que cuelgan de ahí cuando la lista no trae los correos
  A  áreas: Medio Ambiente, Playas, Parques y Jardines, Servicios, Obras…
  D  directorio, teléfonos, contacto
  I  índices («Áreas», «Servicios», «Ayuntamiento») que llevan a las anteriores
"""
import concurrent.futures
import csv
import html
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UNIVERSO = os.path.join(RAIZ, "campana", "lista", "universo-municipios.csv")
SALIDA = os.path.join(RAIZ, "exports", "rastreo")
CANDIDATOS = os.path.join(RAIZ, "exports", "candidatos-rastreo.csv")

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
CUPO = {"G": 20, "A": 10, "D": 3, "I": 4}   # páginas por tipo y ayuntamiento
MAX_SEGUNDOS = 300                           # por ayuntamiento
HILOS = 8                                    # ayuntamientos en paralelo; más satura el proxy

# Todo se compara sin tildes y en minúsculas.
ES_A = re.compile(
    r"medio ?ambiente|medi ?ambient|playas|platges|litoral|parques|parcs|jardin"
    r"|servicios (tecnicos|publicos|urbanos|generales|municipales)"
    r"|serveis (tecnics|publics|urbans|generals|municipals)"
    r"|via publica|mantenimiento|manteniment|obras|obres|brigada|infraestruct|sostenib")
ES_G = re.compile(
    r"corporacion|corporacio|equipo de gobierno|equip de govern|gobierno|govern\b|concejal|regidor"
    r"|delegacion|delegacio|organigrama|organizacion (municipal|politica)|organitzacio (municipal|politica)"
    r"|composicion|composicio|grupos? (politicos?|municipal)|grups? (politics?|municipals?)"
    r"|\bpleno\b|\bple\b|institucional|quien es quien|qui es qui|cargos|carrecs|consistorio|consistori")
ES_D = re.compile(r"directorio|directori|telefonos|telefons|contact")
ES_I = re.compile(r"\bareas\b|\barees\b|servicios|serveis|departament|ayuntamiento|ajuntament"
                  r"|transparencia|\bmunicipal\b|tu ayuntamiento|el teu ajuntament")
EVITAR = re.compile(
    r"noticia|noticies|news|agenda|evento|event|blog|actualidad|actualitat|bando|\bban\b|anunci"
    r"|\.(pdf|jpe?g|png|gif|zip|docx?|xlsx?|mp[34]|ics)(\?|$)|login|facebook|twitter|instagram|youtube"
    r"|whatsapp|linkedin|t\.me|/tag/|/category/|wp-content|cookies|privacidad|privacitat|aviso legal"
    r"|avis legal|accesibilidad|accessibilitat|/20\d\d/|perfil.{0,3}contrat|licitacion|empleo|ocupacio"
    r"|sedelectronica|cita ?previa|galeria|video|rss|feed|mapa web|sitemap|buscar|search|idioma"
    r"|que hacer|que fer|que ver|que veure|donde dormir|on dormir|gastronomia|alojamiento|allotjament")
NOMBRE = re.compile(r"^(?:(?:D\.|Dña\.|Sr\.|Sra\.|Don|Doña)\s+)?[A-ZÁÉÍÓÚÀÈÒÏÜÑÇ][\wàèéíòóúïüñç'’·.\-]+"
                    r"(?:\s+(?:de|del|de la|i|y|[A-ZÁÉÍÓÚÀÈÒÏÜÑÇ][\wàèéíòóúïüñç'’·.\-]+)){1,5}$")

# Lo que hace que un correo sea del perfil: aparece junto a él o en su página.
PERFIL = re.compile(
    r"medio ?ambient|medi ?ambient|playa|platg|litoral|parques|parcs|jardin"
    r"|servicios (tecnicos|publicos|urbanos|generales|municipales)"
    r"|serveis (tecnics|publics|urbans|generals|municipals)"
    r"|obras y servicios|obres i serveis|mantenimiento|manteniment|via publica|brigada"
    r"|infraestruct|sostenib|transicion ecologica|transicio ecologica|limpieza viaria|neteja viaria"
    r"|zonas verdes|zones verdes|espacios publicos|espais publics|mobiliario urbano|mobiliari urba")
BUZON_PERFIL = re.compile(
    r"medi|ambient|playa|platg|litoral|servici|serveis|obres|obras|manten|jardin|parques|parcs"
    r"|tecni|viapublica|brigada|sostenib|infraestr|ecolog")
BUZON_FUERA = re.compile(
    r"^(info|informacio|registr|contrata|contracta|alcald|batl|ayuntamiento|ajuntament|oac|sac|oficina"
    r"|atencion|atencio|policia|dpd|dpo|lopd|prensa|premsa|comunica|cultura|deport|esport|juventud"
    r"|joventut|biblioteca|turism|tourist|serviciossociales|serveissocials|ssocials|padron|padro"
    r"|tesorer|intervenc|secretar|rrhh|personal|empleo|adl|aedl|omic|consum|educac|fiestas|festes"
    r"|igual|comerc|museo|museu|archivo|arxiu|radio|webmaster|web|notific|factur|tribut|rentas"
    r"|recauda|mercad|cementeri|sanidad|sanitat|mayores|proteccion|bombers|bomberos|participa"
    r"|transparencia|urbanism|estadistica|catastro|cadastre|juzgado|jutjat|no-?reply|noreply)")
PARTICULAR = re.compile(r"@(gmail|hotmail|yahoo|outlook|live|msn|icloud|telefonica|movistar|terra|ono)\.")

RE_CORREO = re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+\-]*@[A-Za-z0-9][A-Za-z0-9.\-]*\.[A-Za-z]{2,}")
RE_ENLACE = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.S | re.I)
RE_HREF = re.compile(r"""href\s*=\s*["']([^"'>]+)["']""", re.I)


def llano(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def sin_etiquetas(s):
    s = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def bajar(url, segundos=15):
    """Devuelve (código, url final, texto). Usa curl para respetar el proxy del entorno."""
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--compressed", "-m", str(segundos), "--max-filesize", "4000000",
             "--max-redirs", "5", "-A", UA, "-H", "Accept-Language: es-ES,es;q=0.9,ca;q=0.8",
             "-w", "\n%{http_code}\t%{content_type}\t%{url_effective}", url],
            capture_output=True, timeout=segundos + 10)
    except Exception:
        return 0, url, ""
    cuerpo, _, cola = r.stdout.rpartition(b"\n")
    try:
        codigo, tipo, final = cola.decode("utf-8", "replace").split("\t")
    except ValueError:
        return 0, url, ""
    if "html" not in tipo and "text" not in tipo:
        return int(codigo or 0), final, ""
    m = re.search(rb"charset=[\"']?([\w\-]+)", cuerpo[:3000])
    cod = m.group(1).decode() if m else "utf-8"
    try:
        texto = cuerpo.decode(cod, "replace")
    except LookupError:
        texto = cuerpo.decode("utf-8", "replace")
    return int(codigo or 0), final, texto


def dominio_base(url):
    partes = (urllib.parse.urlsplit(url).hostname or "").split(".")
    return ".".join(partes[-2:])


def descifrar_cf(hexa):
    """Correos ofuscados por Cloudflare (data-cfemail)."""
    try:
        b = bytes.fromhex(hexa)
        return "".join(chr(c ^ b[0]) for c in b[1:])
    except ValueError:
        return ""


CARGO = re.compile(r"concejal|regidor|teniente de alcalde|tinent d.alcald")
G_NUCLEO = re.compile(r"corporacion|corporacio|equipo de gobierno|equip de govern|concejal|regidor"
                      r"|delegacion|delegacio|organigrama|composicion|composicio|\bpleno\b|\bple\b")


def tipo_de_enlace(url, texto):
    """(tipo, prioridad) según a qué parezca llevar el enlace; ('', 0) si no interesa.
    Manda el texto del enlace; la URL solo desempata, y solo por su último tramo.
    Los titulares de noticia (texto largo, slug largo) se descartan, salvo que sean
    la ficha de un concejal del perfil («D. Fulano, Concejal de Medio Ambiente»)."""
    ruta = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
    ultimo = ruta.rstrip("/").rsplit("/", 1)[-1]
    t = llano(texto)
    u = llano(re.sub(r"[-_.]+", " ", ultimo))
    if EVITAR.search(t) or EVITAR.search(llano(url)) or EVITAR.search(llano(re.sub(r"[-_/.]+", " ", ruta))):
        return "", 0
    if CARGO.search(t + " " + u) and PERFIL.search(t + " " + u):
        return "G", 6
    if len(texto) > 60 or ultimo.count("-") >= 6:
        return "", 0
    for donde in (t, u):
        if ES_A.search(donde):
            return "A", 4
        if G_NUCLEO.search(donde):
            return "G", 5
        if ES_G.search(donde):
            return "G", 2
        if ES_D.search(donde):
            return "D", 3
        if donde is t and ES_I.search(donde):
            return "I", 1
    return "", 0


def enlaces(pagina, url, base):
    """{destino: (tipo, prioridad, texto)} de los enlaces internos de la página."""
    salida = {}
    for atributos, interior in RE_ENLACE.findall(pagina):
        m = RE_HREF.search(atributos)
        if not m:
            continue
        href = html.unescape(m.group(1)).strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        destino = urllib.parse.urldefrag(urllib.parse.urljoin(url, href))[0]
        if not destino.startswith("http") or dominio_base(destino) != base:
            continue
        texto = sin_etiquetas(interior)[:120]
        salida.setdefault(destino, tipo_de_enlace(destino, texto) + (texto,))
    return salida


def correos(pagina, url):
    """Cada correo de la página con su contexto. Marca cuando el enlace mailto no
    coincide con la dirección que se lee, porque entonces una de las dos está mal."""
    pagina = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", pagina, flags=re.S | re.I)
    pagina = re.sub(r'<a\b[^>]*data-cfemail="([0-9a-f]+)"[^>]*>.*?</a>',
                    lambda m: " " + descifrar_cf(m.group(1)) + " ", pagina, flags=re.S | re.I)
    pagina = re.sub(r'/cdn-cgi/l/email-protection#([0-9a-f]+)',
                    lambda m: "mailto:" + descifrar_cf(m.group(1)), pagina, flags=re.I)
    distinto = {}

    def anclar(m):
        atributos, interior = m.group(1), m.group(2)
        h = re.search(r"""href\s*=\s*["']\s*mailto:([^"'?>\s]+)""", atributos, re.I)
        if not h:
            return m.group(0)
        enlace = html.unescape(urllib.parse.unquote(h.group(1))).strip()
        visible = RE_CORREO.search(sin_etiquetas(interior))
        if visible:
            if visible.group(0).lower() != enlace.lower():
                distinto[visible.group(0).lower()] = enlace.lower()
            return " " + interior + " "
        return " " + sin_etiquetas(interior) + " " + enlace + " "

    pagina = RE_ENLACE.sub(anclar, pagina)
    pagina = re.sub(r"\s*(\[at\]|\(at\)|\[arroba\]|\(arroba\))\s*", "@", pagina, flags=re.I)
    titulo = re.search(r"<title[^>]*>(.*?)</title>", pagina, re.S | re.I)
    titulo = sin_etiquetas(titulo.group(1))[:90] if titulo else ""
    plano = html.unescape(pagina)
    salida = []
    for m in RE_CORREO.finditer(plano):
        correo = m.group(0).strip(".").lower()
        if re.search(r"\.(png|jpe?g|gif|webp|svg|css|js)$", correo) or "sentry" in correo or "example" in correo:
            continue
        ini, fin = m.start(), m.end()
        abre, cierra = plano.rfind("<", 0, ini), plano.rfind(">", 0, ini)
        if abre > cierra:                             # el correo está dentro de una etiqueta
            ini = abre
            fin = max(fin, plano.find(">", fin) + 1)
        antes = sin_etiquetas(re.sub(r"^[^<]*>", " ", plano[max(0, ini - 4000):ini]))[-300:]
        despues = sin_etiquetas(re.sub(r"<[^>]*$", " ", plano[fin:fin + 1500]))[:200]
        cabeceras = re.findall(r"<h[1-4][^>]*>(.*?)</h[1-4]>", plano[:m.start()], re.S | re.I)
        salida.append({
            "email": correo, "antes": antes, "despues": despues,
            "cabecera": sin_etiquetas(cabeceras[-1])[:90] if cabeceras else "",
            "titulo": titulo, "url": url, "enlace_distinto": distinto.get(correo, ""),
        })
    return salida


def rastrear_web(candidata, resultado, inicio, reparto):
    codigo, final, portada = 0, "", ""
    for esquema in ("https://", "http://"):
        codigo, final, portada = bajar(esquema + re.sub(r"^https?://", "", candidata))
        if codigo == 200 and len(portada) > 500:
            break
    if codigo != 200 or len(portada) <= 500:
        resultado["error"] += f"{candidata}: portada no legible (HTTP {codigo}, {len(portada)} caracteres). "
        return
    base = dominio_base(final)
    antes_n = len(resultado["correos"])
    # cola: url -> (tipo, profundidad, prioridad); la portada es un índice
    cola = {final: ("I", 0, 9)}
    hechas, gastado = {}, {k: 0 for k in CUPO}
    while cola and time.time() - inicio < MAX_SEGUNDOS:
        pendientes = [u for u, (t, _, _) in cola.items() if gastado[t] < max(2, CUPO[t] // reparto) or u == final]
        if not pendientes:
            break
        url = max(pendientes, key=lambda u: (cola[u][2], -cola[u][1]))
        tipo, hondo, _ = cola.pop(url)
        if url == final:
            cod, real, pagina = codigo, final, portada
        else:
            cod, real, pagina = bajar(url)
            gastado[tipo] += 1
        hechas[url] = f"{cod} {tipo}{hondo}"
        if cod != 200 or not pagina:
            continue
        hallados = correos(pagina, real)
        resultado["correos"] += hallados
        if tipo == "D" or hondo >= 3:
            continue
        for otro, (t, prio, texto) in enlaces(pagina, real, base).items():
            if otro in hechas or otro in cola:
                continue
            if tipo == "G" and not t and not hallados and NOMBRE.match(texto.strip()):
                t, prio = "G", 3                      # ficha personal de un concejal
            if not t:
                continue
            if tipo == "I" and (hondo == 0 or t != "I"):
                cola[otro] = (t, hondo + 1, prio)
            elif tipo == "G" and t == "G":
                cola[otro] = (t, hondo + 1, prio)
            elif tipo == "A" and t in ("A", "D") and hondo < 2:
                cola[otro] = (t, hondo + 1, prio - 1)
    resultado["paginas"] += [f"{estado} {u}" for u, estado in hechas.items()]
    if len(portada) < 6000 and len(resultado["correos"]) == antes_n and len(hechas) <= 2:
        resultado["error"] += f"{candidata}: la web se pinta con JavaScript, no hay texto que leer. "


def rastrear(fila):
    destino = os.path.join(SALIDA, fila["cod_ine"] + ".json")
    if os.path.exists(destino):
        return fila["municipio"], "ya estaba"
    resultado = {"cod_ine": fila["cod_ine"], "municipio": fila["municipio"],
                 "provincia": fila["provincia"], "web": fila["web"], "paginas": [], "correos": [],
                 "error": ""}
    inicio = time.time()
    webs = fila["web"].split()
    for candidata in webs:
        try:
            rastrear_web(candidata, resultado, inicio, len(webs))
        except Exception as e:                        # una web rara no para el resto
            resultado["error"] += f"{candidata}: {type(e).__name__} {e}. "
    os.makedirs(SALIDA, exist_ok=True)
    with open(destino, "w") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=1)
    return fila["municipio"], (f"{len(resultado['paginas'])} páginas, "
                               f"{len({c['email'] for c in resultado['correos']})} correos {resultado['error']}")


def clase(correo, contexto):
    local = re.sub(r"[.\-_]", "", llano(correo.split("@")[0]))
    if BUZON_FUERA.search(local) and not re.search(r"medi|ambient|playa|platg", local):
        return "fuera"
    if BUZON_PERFIL.search(local):
        return "buzon"
    return "persona" if PERFIL.search(contexto) else "otro"


def candidatos():
    universo = {f["cod_ine"]: f for f in csv.DictReader(open(UNIVERSO))}
    filas = []
    for nombre in sorted(os.listdir(SALIDA)):
        d = json.load(open(os.path.join(SALIDA, nombre)))
        u = universo[d["cod_ine"]]
        mejor = {}
        for c in d["correos"]:
            cerca = llano(c["antes"][-200:] + " " + c["despues"][:120])
            pagina = llano(c["cabecera"] + " " + c["titulo"] + " " + urllib.parse.unquote(c["url"]))
            k = clase(c["email"], cerca)
            if k == "otro" and PERFIL.search(pagina):
                k = "persona?"      # el perfil sale en la página, no junto al correo
            puntos = {"buzon": 4, "persona": 3, "persona?": 1, "otro": 0, "fuera": 0}[k]
            puntos += 1 if PERFIL.search(pagina) else 0
            if c["email"] not in mejor or puntos > mejor[c["email"]][0]:
                mejor[c["email"]] = (puntos, k, c)
        for correo, (puntos, k, c) in mejor.items():
            if k in ("fuera", "otro") or PARTICULAR.search(correo):
                continue
            filas.append({
                "provincia": u["provincia"], "municipio": u["municipio"], "cod_ine": u["cod_ine"],
                "prioridad": u["prioridad"], "clase": k, "puntos": puntos, "email": correo,
                "contexto": (c["antes"][-200:] + " ‹" + correo + "› " + c["despues"][:120]).strip(),
                "cabecera": c["cabecera"], "enlace_distinto": c["enlace_distinto"], "fuente": c["url"],
            })
    filas.sort(key=lambda f: (f["prioridad"], f["provincia"], f["municipio"], -f["puntos"]))
    campos = ["provincia", "municipio", "cod_ine", "prioridad", "clase", "puntos", "email",
              "contexto", "cabecera", "enlace_distinto", "fuente"]
    with open(CANDIDATOS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} candidatos de {len({f['cod_ine'] for f in filas})} municipios -> {CANDIDATOS}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("rastrear", "candidatos"):
        sys.exit(__doc__)
    if sys.argv[1] == "candidatos":
        return candidatos()
    prioridades, solo = {"1", "2"}, None
    args = sys.argv[2:]
    for i, a in enumerate(args):
        if a == "--prioridad":
            prioridades = set(args[i + 1].split(","))
        if a == "--solo":
            solo = set(args[i + 1].split(","))
    filas = [f for f in csv.DictReader(open(UNIVERSO))
             if f.get("web") and (f["cod_ine"] in solo if solo else f["prioridad"] in prioridades)]
    print(f"{len(filas)} ayuntamientos", flush=True)
    with concurrent.futures.ThreadPoolExecutor(HILOS) as grupo:
        for municipio, estado in grupo.map(rastrear, filas):
            print(f"{municipio}: {estado}", flush=True)


if __name__ == "__main__":
    main()
