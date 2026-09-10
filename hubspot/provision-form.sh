#!/usr/bin/env bash
# Aprovisionamiento del FORMULARIO de mobiliario urbano — portal 26243090
#
# La página https://www.thegravitywave.com/mobiliario-urbano/ envía a la
# Forms API v3 con HS_PORTAL_ID + HS_FORM_GUID. Este script deja HubSpot
# listo para recibir esos envíos:
#
#   1. Asegura las propiedades de contacto `unidades_estimadas` y
#      `landing_variant` (la página las envía y no estaban en el
#      aprovisionamiento inicial)
#   2. Asegura la opción `parque_infantil` en `productos_interes`
#      (la página la ofrece como checkbox; sin la opción, el envío se rechaza)
#   3. Crea (si no existe, por nombre) el formulario
#      spec/form-mobiliario-urbano.json y muestra su GUID
#   4. Asegura el campo oculto `landing_variant` en el formulario
#      (prueba A/B: sin él, la Forms API rechaza el envío que lo incluye)
#
# Al terminar imprime la línea exacta a pegar en la página:
#   var HS_FORM_GUID = "xxxxxxxx-....";
#
# Es idempotente: se puede relanzar sin duplicar nada.
#
# Uso:
#   export HUBSPOT_PRIVATE_APP_TOKEN=pat-eu1-...
#   ./provision-form.sh
#
# El token necesita, además de los scopes de provision.sh:
#   forms  (Marketing → Forms)

set -euo pipefail

API="https://api.hubapi.com"
SPEC_DIR="$(cd "$(dirname "$0")/spec" && pwd)"
FORM_SPEC="$SPEC_DIR/form-mobiliario-urbano.json"
CONTACT_SPEC="$SPEC_DIR/contact-properties.json"

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

split_response() { # respuesta → RESP_BODY, RESP_CODE
  RESP_CODE="${1##*$'\n'}"
  RESP_BODY="${1%$'\n'*}"
}

echo "== 1. Propiedades de contacto que envía la página =="
ensure_prop() { # ensure_prop NOMBRE
  local nombre="$1" prop
  prop=$(jq -c --arg n "$nombre" '.inputs[] | select(.name == $n)' "$CONTACT_SPEC")
  [[ -n "$prop" ]] || { echo "  ✗ $nombre no está en $CONTACT_SPEC" >&2; exit 1; }
  split_response "$(hs GET "/crm/v3/properties/contacts/$nombre")"
  if [[ "$RESP_CODE" == "200" ]]; then
    echo "  ✓ $nombre ya existe"
    return
  fi
  split_response "$(hs POST "/crm/v3/properties/contacts" "$prop")"
  if [[ "$RESP_CODE" == "201" ]]; then
    echo "  + $nombre creada"
  else
    echo "  ✗ Error creando $nombre ($RESP_CODE): $RESP_BODY" >&2
    exit 1
  fi
}
ensure_prop unidades_estimadas
ensure_prop landing_variant

echo
echo "== 2. Opciones de contacts.productos_interes =="
# La spec es la lista definitiva (Parque infantil · Banco · Papelera · Otro ·
# Letras de exterior). El valor interno de «Letras de exterior» sigue siendo
# letrero_corporeo porque es el que envía la página web. Las opciones que no
# están en la spec (mesa, taburete) se retiran: solo las usaban contactos de
# prueba.
SPEC_OPTS=$(jq -c '.inputs[] | select(.name == "productos_interes") | .options' "$CONTACT_SPEC")
split_response "$(hs GET "/crm/v3/properties/contacts/productos_interes")"
[[ "$RESP_CODE" == "200" ]] || { echo "  ✗ No puedo leer la propiedad ($RESP_CODE): $RESP_BODY" >&2; exit 1; }
CURRENT_OPTS=$(jq -c '[.options[] | {label, value, displayOrder}] | sort_by(.displayOrder)' <<<"$RESP_BODY")
if [[ "$(jq -c 'map({label, value})' <<<"$CURRENT_OPTS")" == "$(jq -c 'map({label, value})' <<<"$SPEC_OPTS")" ]]; then
  echo "  ✓ Las opciones ya coinciden con la spec"
else
  split_response "$(hs PATCH "/crm/v3/properties/contacts/productos_interes" \
    "$(jq -n --argjson o "$SPEC_OPTS" '{options: $o}')")"
  if [[ "$RESP_CODE" == "200" ]]; then
    echo "  + Opciones sincronizadas: $(jq -r 'map(.label) | join(" · ")' <<<"$SPEC_OPTS")"
  else
    echo "  ✗ Error actualizando opciones ($RESP_CODE): $RESP_BODY" >&2
    exit 1
  fi
fi

echo
echo "== 3. Formulario =="
FORM_NAME=$(jq -r .name "$FORM_SPEC")
# Busca por nombre entre los formularios existentes (paginado simple)
GUID=""
AFTER=""
while :; do
  split_response "$(hs GET "/marketing/v3/forms/?limit=100${AFTER:+&after=$AFTER}")"
  [[ "$RESP_CODE" == "200" ]] || { echo "  ✗ No puedo listar formularios ($RESP_CODE): $RESP_BODY" >&2; exit 1; }
  GUID=$(jq -r --arg n "$FORM_NAME" '.results[] | select(.name == $n) | .id' <<<"$RESP_BODY" | head -1)
  [[ -n "$GUID" ]] && break
  AFTER=$(jq -r '.paging.next.after // empty' <<<"$RESP_BODY")
  [[ -n "$AFTER" ]] || break
done

if [[ -n "$GUID" ]]; then
  echo "  ✓ El formulario «$FORM_NAME» ya existe"
else
  # La API exige createdAt/updatedAt en el POST aunque luego los sobrescribe
  NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  split_response "$(hs POST "/marketing/v3/forms/" \
    "$(jq -c --arg t "$NOW" '. + {createdAt: $t, updatedAt: $t}' "$FORM_SPEC")")"
  if [[ "$RESP_CODE" == "201" || "$RESP_CODE" == "200" ]]; then
    GUID=$(jq -r .id <<<"$RESP_BODY")
    echo "  + Formulario creado"
  else
    echo "  ✗ Error creando el formulario ($RESP_CODE): $RESP_BODY" >&2
    echo "    (Alternativa: crearlo a mano en Marketing → Forms con los campos" >&2
    echo "     de $FORM_SPEC y copiar el GUID de la URL del editor.)" >&2
    exit 1
  fi
fi

echo
echo "== 4. Campo oculto landing_variant en el formulario =="
# La Forms API rechaza con 400 cualquier campo que no esté en la definición del
# formulario, así que sin este campo los envíos de la prueba A/B fallarían.
# Se parchea la definición VIVA en lugar de reenviar la spec completa: el
# formulario puede tener campos añadidos a mano desde HubSpot (p. ej. company)
# que la spec no conoce, y reenviar la spec los borraría.
split_response "$(hs GET "/marketing/v3/forms/$GUID")"
[[ "$RESP_CODE" == "200" ]] || { echo "  ✗ No puedo leer el formulario ($RESP_CODE): $RESP_BODY" >&2; exit 1; }
if jq -e '[.fieldGroups[].fields[].name] | index("landing_variant")' <<<"$RESP_BODY" >/dev/null; then
  echo "  ✓ Ya presente"
else
  GROUP=$(jq -c '.fieldGroups[] | select(any(.fields[]; .name == "landing_variant"))' "$FORM_SPEC")
  [[ -n "$GROUP" ]] || { echo "  ✗ landing_variant no está en $FORM_SPEC" >&2; exit 1; }
  # Se inserta detrás de canal_origen (el otro campo oculto) para agrupar los
  # campos que no ve el visitante; si no estuviera, va al final.
  BODY=$(jq -c --argjson g "$GROUP" '
    ((([.fieldGroups | to_entries[]
        | select(any(.value.fields[]; .name == "canal_origen")) | .key] | first)
      // ((.fieldGroups | length) - 1)) + 1) as $i
    | {fieldGroups: (.fieldGroups[0:$i] + [$g] + .fieldGroups[$i:])}' <<<"$RESP_BODY")
  split_response "$(hs PATCH "/marketing/v3/forms/$GUID" "$BODY")"
  if [[ "$RESP_CODE" == "200" ]]; then
    echo "  + Campo añadido (oculto)"
  else
    echo "  ✗ Error añadiendo el campo ($RESP_CODE): $RESP_BODY" >&2
    exit 1
  fi
fi

echo
echo "GUID del formulario: $GUID"
echo
echo "Último paso — pegar en la página /mobiliario-urbano/ (Elementor):"
echo "  var HS_FORM_GUID = \"$GUID\";"
echo
echo "Y verificar con un envío de prueba que el contacto llega a HubSpot"
echo "con hs_analytics_source = FORMS (no OFFLINE)."
