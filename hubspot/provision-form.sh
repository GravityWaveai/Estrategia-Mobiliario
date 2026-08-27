#!/usr/bin/env bash
# Aprovisionamiento del formulario web — Estrategia Mobiliario Urbano
#
# Crea (si no existe) el formulario «Lead mobiliario urbano — web» en el
# portal 26243090 a partir de spec/form-lead-mobiliario.json, e imprime su
# GUID. Ese GUID es el que hay que pegar en web/index.html:
#
#   var HS_FORM_GUID = "<guid>";
#
# Es idempotente: si el formulario ya existe, solo informa del GUID.
#
# Uso:
#   export HUBSPOT_PRIVATE_APP_TOKEN=pat-eu1-...
#   ./provision-form.sh
#
# El token necesita, además de los scopes del provision.sh, el scope «forms».
# Los campos del formulario usan las propiedades de contacto creadas por
# provision.sh (tipo_entidad, municipio, productos_interes, plazo_proyecto,
# canal_origen): ejecuta primero provision.sh si aún no lo has hecho.

set -euo pipefail

API="https://api.hubapi.com"
SPEC="$(cd "$(dirname "$0")/spec" && pwd)/form-lead-mobiliario.json"

: "${HUBSPOT_PRIVATE_APP_TOKEN:?Define HUBSPOT_PRIVATE_APP_TOKEN antes de ejecutar}"

command -v jq >/dev/null || { echo "Necesito jq instalado"; exit 1; }

FORM_NAME=$(jq -r .name "$SPEC")

hs() { # hs METHOD PATH [JSON_BODY]
  local method="$1" path="$2" body="${3:-}"
  local args=(-sS -X "$method" "$API$path" \
    -H "Authorization: Bearer $HUBSPOT_PRIVATE_APP_TOKEN" \
    -H "Content-Type: application/json" \
    -w '\n%{http_code}')
  [[ -n "$body" ]] && args+=(-d "$body")
  curl "${args[@]}"
}

split_response() {
  RESP_CODE="${1##*$'\n'}"
  RESP_BODY="${1%$'\n'*}"
}

echo "— Buscando formulario «$FORM_NAME»…"
split_response "$(hs GET "/marketing/v3/forms/?limit=100&formTypes=hubspot")"
if [[ "$RESP_CODE" != "200" ]]; then
  echo "  ✗ No puedo listar formularios (HTTP $RESP_CODE):"
  echo "$RESP_BODY" | jq . 2>/dev/null || echo "$RESP_BODY"
  echo "  ¿Tiene el token el scope «forms»?"
  exit 1
fi

GUID=$(echo "$RESP_BODY" | jq -r --arg n "$FORM_NAME" '.results[] | select(.name == $n) | .id' | head -n1)

if [[ -n "$GUID" && "$GUID" != "null" ]]; then
  echo "  ✓ Ya existe."
else
  echo "  · No existe; creándolo…"
  split_response "$(hs POST "/marketing/v3/forms/" "$(cat "$SPEC")")"
  if [[ "$RESP_CODE" != "200" && "$RESP_CODE" != "201" ]]; then
    echo "  ✗ Error al crear el formulario (HTTP $RESP_CODE):"
    echo "$RESP_BODY" | jq . 2>/dev/null || echo "$RESP_BODY"
    exit 1
  fi
  GUID=$(echo "$RESP_BODY" | jq -r .id)
  echo "  ✓ Creado."
fi

echo
echo "GUID del formulario: $GUID"
echo
echo "Último paso — pégalo en web/index.html:"
echo "  var HS_FORM_GUID = \"$GUID\";"
echo
echo "Prueba de punta a punta: envía el formulario desde la web y comprueba"
echo "que aparece el contacto en HubSpot con sus propiedades de Mobiliario"
echo "Urbano rellenas."
