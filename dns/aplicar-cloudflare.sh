#!/usr/bin/env bash
# Crea o actualiza los registros de correo de thegravitywave.com en Cloudflare.
# Nunca borra nada: si el registro existe lo sustituye, si no lo crea.
#
#   export CF_API_TOKEN=…   # Zone:DNS:Edit sobre la zona
#   dns/aplicar-cloudflare.sh [--dry-run] spf
#   dns/aplicar-cloudflare.sh [--dry-run] dkim 'v=DKIM1; k=rsa; p=MIIB…'   # selector google
#   dns/aplicar-cloudflare.sh [--dry-run] dmarc quarantine|reject
#   dns/aplicar-cloudflare.sh [--dry-run] tlsrpt
#   dns/aplicar-cloudflare.sh [--dry-run] mta-sts                          # solo el TXT
#   dns/aplicar-cloudflare.sh [--dry-run] cname <nombre> <destino>         # los CNAME de HubSpot
#   dns/aplicar-cloudflare.sh [--dry-run] txt <nombre> '<valor>'           # cualquier otro TXT
#
# DOMINIO=otro.com cambia la zona. Ver dns/README.md para el orden de los pasos.
set -euo pipefail
DOM="${DOMINIO:-thegravitywave.com}"
INFORMES="${DMARC_RUA:-julen@thegravitywave.com}"
DRY=0
if [ "${1:-}" = "--dry-run" ]; then DRY=1; shift; fi
ORDEN="${1:-}"; [ -n "$ORDEN" ] || { sed -n 2,14p "$0"; exit 1; }
shift

case "$ORDEN" in
  spf)      TIPO=TXT;   NOMBRE="$DOM";              VALOR="v=spf1 include:_spf.google.com include:_spf.webempresa.eu ip4:51.178.3.36 ~all" ;;
  dkim)     TIPO=TXT;   NOMBRE="google._domainkey.$DOM"; VALOR="${1:?falta el valor v=DKIM1… que da el Admin de Google}" ;;
  dmarc)    TIPO=TXT;   NOMBRE="_dmarc.$DOM"
            case "${1:-}" in
              quarantine) VALOR="v=DMARC1; p=quarantine; pct=100; rua=mailto:$INFORMES; ruf=mailto:$INFORMES; fo=1; adkim=r; aspf=r" ;;
              reject)     VALOR="v=DMARC1; p=reject; pct=100; rua=mailto:$INFORMES; ruf=mailto:$INFORMES; fo=1; adkim=s; aspf=s" ;;
              *) echo "dmarc quarantine | dmarc reject" >&2; exit 1 ;;
            esac ;;
  tlsrpt)   TIPO=TXT;   NOMBRE="_smtp._tls.$DOM";   VALOR="v=TLSRPTv1; rua=mailto:$INFORMES" ;;
  mta-sts)  TIPO=TXT;   NOMBRE="_mta-sts.$DOM";     VALOR="v=STSv1; id=$(date -u +%Y%m%d%H%M)" ;;
  cname)    TIPO=CNAME; NOMBRE="${1:?falta el nombre}"; VALOR="${2:?falta el destino}" ;;
  txt)      TIPO=TXT;   NOMBRE="${1:?falta el nombre}"; VALOR="${2:?falta el valor}" ;;
  *) echo "orden desconocida: $ORDEN" >&2; exit 1 ;;
esac
case "$NOMBRE" in *."$DOM"|"$DOM") ;; *) NOMBRE="$NOMBRE.$DOM" ;; esac

if [ "$DRY" = 1 ]; then
  echo "(dry-run) $TIPO $NOMBRE"; echo "          $VALOR"; exit 0
fi
: "${CF_API_TOKEN:?falta CF_API_TOKEN (Cloudflare → Mi perfil → Tokens de API → Editar DNS de zona)}"

API=https://api.cloudflare.com/client/v4
cf() { curl -sS -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" "$@"; }
json() { python3 -c "import sys,json; d=json.load(sys.stdin); $1"; }

ZONA=$(cf "$API/zones?name=$DOM&status=active" | json 'r=d.get("result") or []; print(r[0]["id"] if r else "")')
[ -n "$ZONA" ] || { echo "Cloudflare no devuelve la zona $DOM con este token" >&2; exit 1; }

# Para TXT se busca el registro del mismo tipo y nombre que empiece igual
# (v=spf1, v=DMARC1, v=DKIM1…); así no se pisa el google-site-verification
# que vive en el mismo nombre que el SPF.
PREFIJO=$(printf '%s' "$VALOR" | cut -d';' -f1 | cut -d' ' -f1)
ID=$(cf "$API/zones/$ZONA/dns_records?type=$TIPO&name=$NOMBRE&per_page=100" \
  | PREF="$PREFIJO" TIPO="$TIPO" json 'import os
pref, tipo = os.environ["PREF"].lower(), os.environ["TIPO"]
for r in d.get("result") or []:
    c = r.get("content","").strip("\"")
    if tipo != "TXT" or c.lower().startswith(pref):
        print(r["id"]); print(c); break')
ID_REG=$(printf '%s\n' "$ID" | sed -n 1p); ANTES=$(printf '%s\n' "$ID" | sed -n 2p)

CUERPO=$(NOMBRE="$NOMBRE" TIPO="$TIPO" VALOR="$VALOR" python3 -c 'import os,json
print(json.dumps({"type":os.environ["TIPO"],"name":os.environ["NOMBRE"],"content":os.environ["VALOR"],"ttl":1,"proxied":False}))')
if [ -n "$ID_REG" ]; then
  echo "había:  $ANTES"
  RES=$(cf -X PUT "$API/zones/$ZONA/dns_records/$ID_REG" --data "$CUERPO")
else
  echo "había:  (nada)"
  RES=$(cf -X POST "$API/zones/$ZONA/dns_records" --data "$CUERPO")
fi
printf '%s' "$RES" | json 'import sys
if not d.get("success"): print("ERROR:", d.get("errors")); sys.exit(1)
r=d["result"]; print("queda: ", r["type"], r["name"]); print("        ", r["content"])'
echo "Propaga en 1–5 minutos; comprueba con dns/comprobar.sh"
