#!/usr/bin/env bash
# Aprovisionamiento de HubSpot — Estrategia Mobiliario Urbano
#
# Crea (si no existen) en el portal 26243090:
#   1. Grupo de propiedades «Mobiliario Urbano» en contactos y negocios
#   2. 5 propiedades de contacto  (spec/contact-properties.json)
#   3. 5 propiedades de negocio   (spec/deal-properties.json)
#   4. Pipeline de negocios «Mobiliario Urbano» con 7 etapas (spec/pipeline-mobiliario-urbano.json)
#
# Es idempotente: lo que ya existe se deja tal cual y se informa.
#
# Uso:
#   export HUBSPOT_PRIVATE_APP_TOKEN=pat-eu1-...   # token de app privada
#   ./provision.sh
#
# El token necesita los scopes:
#   crm.objects.deals.read/write, crm.objects.contacts.read/write,
#   crm.schemas.deals.read/write, crm.schemas.contacts.read/write
#
# Cómo crear la app privada (2 min, requiere superadmin):
#   HubSpot → Settings → Integrations → Private Apps → Create private app
#   → pestaña Scopes → marcar los seis de arriba → Create → copiar token.

set -euo pipefail

API="https://api.hubapi.com"
SPEC_DIR="$(cd "$(dirname "$0")/spec" && pwd)"

: "${HUBSPOT_PRIVATE_APP_TOKEN:?Define HUBSPOT_PRIVATE_APP_TOKEN antes de ejecutar}"

command -v jq >/dev/null || { echo "Necesito jq instalado"; exit 1; }

hs() { # hs METHOD PATH [JSON_BODY]
  local method="$1" path="$2" body="${3:-}"
  local args=(-sS -X "$method" "$API$path" \
    -H "Authorization: Bearer $HUBSPOT_PRIVATE_APP_TOKEN" \
    -H "Content-Type: application/json" \
    -w '\n%{http_code}')
  [[ -n "$body" ]] && args+=(-d "$body")
  curl "${args[@]}"
}

# Separa cuerpo y código HTTP de la respuesta de hs()
split_response() { # respuesta → variables globales RESP_BODY, RESP_CODE
  RESP_CODE="${1##*$'\n'}"
  RESP_BODY="${1%$'\n'*}"
}

ensure_group() { # objectType
  local obj="$1"
  local spec="$SPEC_DIR/contact-properties.json"
  [[ "$obj" == "deals" ]] && spec="$SPEC_DIR/deal-properties.json"
  local name label
  name=$(jq -r .groupName "$spec")
  label=$(jq -r .groupLabel "$spec")

  split_response "$(hs GET "/crm/v3/properties/$obj/groups/$name")"
  if [[ "$RESP_CODE" == "200" ]]; then
    echo "  ✓ Grupo «$label» ya existe en $obj"
    return
  fi
  split_response "$(hs POST "/crm/v3/properties/$obj/groups" \
    "$(jq -n --arg n "$name" --arg l "$label" '{name:$n,label:$l}')")"
  if [[ "$RESP_CODE" == "201" ]]; then
    echo "  + Grupo «$label» creado en $obj"
  else
    echo "  ✗ Error creando grupo en $obj ($RESP_CODE): $RESP_BODY" >&2
    exit 1
  fi
}

ensure_properties() { # objectType specFile
  local obj="$1" spec="$2"
  local count
  count=$(jq '.inputs | length' "$spec")
  for i in $(seq 0 $((count - 1))); do
    local prop name
    prop=$(jq -c ".inputs[$i]" "$spec")
    name=$(jq -r .name <<<"$prop")

    split_response "$(hs GET "/crm/v3/properties/$obj/$name")"
    if [[ "$RESP_CODE" == "200" ]]; then
      # Existe: si es enumeración, sincroniza las opciones con la spec
      # (añade las nuevas, p. ej. parque_infantil; PATCH es idempotente).
      if [[ "$(jq -r .type <<<"$prop")" == "enumeration" ]]; then
        local spec_opts live_opts
        spec_opts=$(jq -c '[.options[].value] | sort' <<<"$prop")
        live_opts=$(jq -c '[.options[].value] | sort' <<<"$RESP_BODY")
        if [[ "$spec_opts" != "$live_opts" ]]; then
          split_response "$(hs PATCH "/crm/v3/properties/$obj/$name" \
            "$(jq -c '{options: .options}' <<<"$prop")")"
          if [[ "$RESP_CODE" == "200" ]]; then
            echo "  ~ $obj.$name ya existía; opciones sincronizadas con la spec"
          else
            echo "  ✗ Error sincronizando opciones de $obj.$name ($RESP_CODE): $RESP_BODY" >&2
            exit 1
          fi
        else
          echo "  ✓ $obj.$name ya existe"
        fi
      else
        echo "  ✓ $obj.$name ya existe"
      fi
      continue
    fi
    split_response "$(hs POST "/crm/v3/properties/$obj" "$prop")"
    if [[ "$RESP_CODE" == "201" ]]; then
      echo "  + $obj.$name creada"
    else
      echo "  ✗ Error creando $obj.$name ($RESP_CODE): $RESP_BODY" >&2
      exit 1
    fi
  done
}

ensure_pipeline() {
  local spec="$SPEC_DIR/pipeline-mobiliario-urbano.json"
  local label
  label=$(jq -r .label "$spec")

  split_response "$(hs GET "/crm/v3/pipelines/deals")"
  if [[ "$RESP_CODE" != "200" ]]; then
    echo "  ✗ No puedo listar pipelines ($RESP_CODE): $RESP_BODY" >&2
    exit 1
  fi
  local existing
  existing=$(jq -r --arg l "$label" '.results[] | select(.label == $l) | .id' <<<"$RESP_BODY")
  if [[ -n "$existing" ]]; then
    echo "  ✓ Pipeline «$label» ya existe (id $existing)"
    return
  fi
  split_response "$(hs POST "/crm/v3/pipelines/deals" \
    "$(jq -c 'del(.objectType)' "$spec")")"
  if [[ "$RESP_CODE" == "201" ]]; then
    echo "  + Pipeline «$label» creado (id $(jq -r .id <<<"$RESP_BODY"))"
    echo
    echo "  Etapas creadas:"
    jq -r '.stages[] | "    \(.displayOrder). \(.label)  →  \(.id)"' <<<"$RESP_BODY"
  else
    echo "  ✗ Error creando pipeline ($RESP_CODE): $RESP_BODY" >&2
    exit 1
  fi
}

echo "== Grupos de propiedades =="
ensure_group contacts
ensure_group deals

echo
echo "== Propiedades de contacto =="
ensure_properties contacts "$SPEC_DIR/contact-properties.json"

echo
echo "== Propiedades de negocio =="
ensure_properties deals "$SPEC_DIR/deal-properties.json"

echo
echo "== Pipeline =="
ensure_pipeline

echo
echo "Aprovisionamiento completado."
echo "Pendiente solo de UI (no expuesto por API pública):"
echo "  · Importe obligatorio al entrar en «Propuesta en preparación»"
echo "    (Settings → Objects → Deals → Pipelines → Mobiliario Urbano →"
echo "     Conditional stage properties)"
echo "  · motivo_perdida obligatorio al entrar en «Descartado» (mismo sitio)"
