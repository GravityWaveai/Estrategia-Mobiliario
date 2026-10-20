#!/usr/bin/env bash
# Comprueba SPF, DKIM, DMARC y extras de thegravitywave.com contra el DNS
# público (dns.google, el mismo que usa el puente). Sin credenciales.
#   dns/comprobar.sh            # thegravitywave.com
#   dns/comprobar.sh otro.com   # otro dominio
set -euo pipefail
DOM="${1:-thegravitywave.com}"
exec python3 - "$DOM" <<'PY'
import json, re, sys, urllib.request, urllib.parse

dom = sys.argv[1]

def consulta(nombre, tipo):
    url = f"https://dns.google/resolve?name={urllib.parse.quote(nombre)}&type={tipo}"
    with urllib.request.urlopen(url, timeout=15) as r:
        d = json.load(r)
    out = []
    for a in d.get("Answer", []) or []:
        v = a.get("data") or ""
        if tipo == "TXT":
            v = "".join(t.strip('"') for t in v.split('" "')).strip('"')
        out.append(v)
    return out

def txt(nombre, prefijo):
    return next((x for x in consulta(nombre, "TXT") if x.lower().startswith(prefijo)), None)

OK, MEH, KO = "\033[32m✔\033[0m", "\033[33m▲\033[0m", "\033[31m✘\033[0m"
puntos = 0

# --- SPF
spf = txt(dom, "v=spf1")
def consultas_spf(reg, vistos=None, prof=0):
    """Cuenta los mecanismos que gastan consulta DNS (include, a, mx, ptr, exists, redirect)."""
    n = 0
    for tok in (reg or "").split():
        t = tok.lstrip("+-~?").lower()
        if t.startswith(("include:", "redirect=")):
            n += 1
            sub = t.split(":", 1)[1] if ":" in t else t.split("=", 1)[1]
            if prof < 10:
                try:
                    n += consultas_spf(txt(sub, "v=spf1"), prof=prof + 1)
                except Exception:
                    pass
        elif t in ("a", "mx", "ptr") or t.startswith(("a:", "mx:", "ptr:", "exists:")):
            n += 1
    return n
if spf:
    nq = consultas_spf(spf)
    google = "_spf.google.com" in spf
    estado = OK if google and nq <= 10 else MEH
    puntos += 25 if google else 0
    print(f"{estado} SPF    {spf}")
    print(f"        {nq} consultas DNS de 10{' · no incluye a Google' if not google else ''}")
    dup = [m for m in ("+a", "+mx", "ip4:213.158.86.32") if m in spf]
    if dup:
        print(f"        redundantes: {', '.join(dup)} (ya cubiertos por los include)")
else:
    print(f"{KO} SPF    no hay registro")

# --- DKIM
dkim = txt(f"google._domainkey.{dom}", "v=dkim1")
if dkim:
    bits = "2048" if len(re.sub(r".*p=", "", dkim)) > 300 else "1024"
    puntos += 25
    print(f"{OK} DKIM   google._domainkey existe (clave {bits} bits)")
else:
    puntos += 10
    print(f"{MEH} DKIM   google._domainkey no existe: Gmail firma con gappssmtp.com (10 de 25 puntos)")
for sel in ("selector1", "selector2", "k1", "mail", "default"):
    if txt(f"{sel}._domainkey.{dom}", "v=dkim1"):
        print(f"        también firma: {sel}._domainkey")
PORTAL_HUBSPOT = "26243090"
hs = [c for sel in ("hs1", "hs2") for c in consulta(f"{sel}-{PORTAL_HUBSPOT}._domainkey.{dom}", "CNAME")]
print(f"{OK if len(hs) == 2 else MEH} HubSpot {'dominio de envío conectado (hs1/hs2-' + PORTAL_HUBSPOT + ' → hubspotemail.net)' if len(hs) == 2 else 'faltan los CNAME hs1/hs2-' + PORTAL_HUBSPOT + '._domainkey: reconectar el dominio en HubSpot → Dominios'}")

# --- DMARC
dmarc = txt(f"_dmarc.{dom}", "v=dmarc1")
if dmarc:
    tags = dict(kv.strip().split("=", 1) for kv in dmarc.split(";") if "=" in kv)
    p, pct = tags.get("p", "none"), int(tags.get("pct", "100"))
    faltan = [t for t in ("rua", "ruf", "fo") if t not in tags]
    estado = OK if pct == 100 and p in ("quarantine", "reject") else MEH
    puntos += 20 if pct == 100 else 10
    print(f"{estado} DMARC  {dmarc}")
    print(f"        política {p}, aplicada al {pct}%" + (f" · sin {', '.join(faltan)}" if faltan else ""))
else:
    print(f"{KO} DMARC  no hay registro")

# --- Extras
for nombre, pref, etiqueta in ((f"_smtp._tls.{dom}", "v=tlsrptv1", "TLS-RPT"),
                               (f"_mta-sts.{dom}", "v=stsv1", "MTA-STS"),
                               (f"default._bimi.{dom}", "v=bimi1", "BIMI")):
    v = txt(nombre, pref)
    print(f"{OK if v else MEH} {etiqueta:8}{v or 'no existe (opcional)'}")

mx = consulta(dom, "MX")
print(f"{OK if any('google' in m for m in mx) else MEH} MX     {', '.join(sorted(mx)) or 'sin MX'}")
print(f"\nParte DNS de la salud del panel: {puntos} de 70 (el resto son rebotes y spam de Apollo).")
PY
