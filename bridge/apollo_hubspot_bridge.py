#!/usr/bin/env python3
"""
Puente Apollo <-> HubSpot del embudo de Mobiliario Urbano.

Apollo envía los correos; HubSpot es el CRM y el pipeline. Este script es la
única pieza que los une, y hace cuatro cosas en cada pasada:

  1. INBOUND  — inscribe en la secuencia de Apollo los leads que han entrado
                por el formulario de la web y aún no están inscritos.
  2. OUTBOUND — inscribe hasta 50 ayuntamientos al día desde la lista de Apollo.
  3. RESPUESTA— la detecta HubSpot, no Apollo: cuando la propiedad nativa
                `hs_sales_email_last_replied` se rellena, el puente marca
                `apollo_estado = respondido` y saca al contacto de la secuencia.
  4. PARADA   — si en HubSpot consta una reunión agendada (calendario de Amaia),
                saca al contacto de la secuencia de Apollo. Apollo no ve ese
                calendario, así que la parada tiene que venir de aquí.
  5. DESCARTE — si la secuencia de Apollo termina sin respuesta, el negocio
                pasa solo a «Descartado». Nadie tiene que cerrarlo a mano.
  6. REBOTES  — lo único que sigue viniendo de Apollo, porque HubSpot no puede
                saberlo: un correo que no llegó nunca no genera actividad.

Es idempotente: `apollo_estado` en HubSpot hace de memoria, así que se puede
relanzar sin duplicar inscripciones. Al inscribir (INBOUND y OUTBOUND) se
guarda también `apollo_fecha_inscripcion`: las señales de parada solo cuentan
si son posteriores, para que el historial previo de un contacto que ya estaba
en el CRM no se confunda con una reacción a esta campaña.

Variables de entorno:
  HUBSPOT_TOKEN          token de la app privada de HubSpot   (obligatorio)
  APOLLO_API_KEY         API key de Apollo                    (obligatorio)
  BRIDGE_ENABLED         "1" para escribir de verdad; si no, simulacro
  OUTBOUND_ENABLED       "0" para desactivar solo OUTBOUND sin tocar INBOUND
                         (por defecto "1" — sigue el valor de BRIDGE_ENABLED)
  OUTBOUND_DAILY_CAP     tope diario del OUTBOUND (por defecto 50)
  OUTBOUND_ENROLL_HOUR   hora UTC en la que se inscribe OUTBOUND cada día
                         (por defecto 8; el resto de pasadas de esa hora
                         no hacen nada nuevo en OUTBOUND)
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

HUBSPOT_TOKEN = os.environ.get("HUBSPOT_TOKEN", "")
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")
ENABLED = os.environ.get("BRIDGE_ENABLED") == "1"
OUTBOUND_ENABLED = os.environ.get("OUTBOUND_ENABLED", "1") == "1"
CAP = int(os.environ.get("OUTBOUND_DAILY_CAP", "50"))
HORA_ENVIO_OUTBOUND = int(os.environ.get("OUTBOUND_ENROLL_HOUR", "8"))  # UTC

# Identificadores fijos del embudo
SEQ_INBOUND = "6a9844b94208650014fc4754"
SEQ_OUTBOUND = "6a9844f7d0bf520010f72cc1"
LIST_OUTBOUND = "6a983205f242c800107386c8"
CAMPANA = "mobiliario_urbano"
PIPELINE = "4080461018"
ETAPA_LEAD = "5948376264"   # «Información enviada», la primera
ETAPA_MUESTRA_INTERES = "5948376265"
ETAPA_DESCARTADO = "5948376270"
# Opción de `motivo_perdida` (negocio). HubSpot lo exige al mover a
# «Descartado», así que el descarte automático tiene que ponerlo él mismo.
MOTIVO_SIN_RESPUESTA = "sin_respuesta"
VENTANA_CADENCIA = 45       # días que dura la cadencia más larga, con margen

# Campos personalizados de Apollo (contacto) donde se vuelca lo que el lead
# contó en el formulario web, para que los correos de INBOUND lo citen de
# verdad en vez de hablar en genérico. HubSpot guarda el valor interno
# ("banco", "6_15"...); estos diccionarios lo traducen a la etiqueta legible
# antes de escribirlo en Apollo.
# Topes de lo que se escribe en Apollo. La lista de productos se cita en el
# correo, así que se recorta a una frase si no cabe; el mensaje solo es
# contexto para Amaia y se trunca. Ojo: si el campo de Apollo es de tipo
# "texto corto" su tope real es 30 y lo impone Apollo — el puente lo detecta
# por el 422 y reintenta con la frase corta (ver enroll_inbound).
LIMITE_PRODUCTOS = 60
LIMITE_MENSAJE = 100   # tope real del campo de texto largo de Apollo (comprobado 07/09)
PRODUCTOS_RESUMIDOS = "una selección del catálogo"

# Minutos que se le dan al pull nativo HubSpot->Apollo para traer un lead del
# formulario antes de que el puente cree el contacto en Apollo por su cuenta.
ESPERA_PULL_MIN = 15

CAMPOS_APOLLO_INBOUND = {
    "productos_interes": "6a9993622c2d76000c949670",
    "unidades_estimadas": "6a9993775f82df000c6e1af6",
    "plazo_proyecto": "6a9993d8743850001cfa814f",
    "tipo_entidad": "6a9993caa7323a001c0c786c",
    "message": "6a9993bcc96c2d001cdc2d5b",
}

# Etiqueta con la que Apollo nombra cada campo en sus errores («Value for
# Mensaje formulario is over length limit 100») -> id del campo.
ETIQUETAS_CAMPOS_APOLLO = {
    "Productos interés": CAMPOS_APOLLO_INBOUND["productos_interes"],
    "Unidades estimadas": CAMPOS_APOLLO_INBOUND["unidades_estimadas"],
    "Plazo del proyecto": CAMPOS_APOLLO_INBOUND["plazo_proyecto"],
    "Tipo de entidad": CAMPOS_APOLLO_INBOUND["tipo_entidad"],
    "Mensaje formulario": CAMPOS_APOLLO_INBOUND["message"],
}

# Campo personalizado de Apollo con el municipio, verificado a mano contra el
# dominio de cada ayuntamiento (el "city" que calcula Apollo solo no es fiable
# para pueblos pequeños). El workflow OUTBOUND de HubSpot usa el "municipio"
# del contacto para el nombre del negocio, así que el puente lo copia también
# a HubSpot en vez de fiarse de que la integración nativa lo traiga bien.
CAMPO_APOLLO_MUNICIPIO = "6a999f44b6a7d5001357d023"

ETIQUETAS_PRODUCTOS_INTERES = {
    "banco": "Banco", "mesa": "Mesa", "papelera": "Papelera",
    "taburete": "Taburete", "letrero_corporeo": "Letrero corpóreo",
    "parque_infantil": "Parque infantil", "otro": "Otro",
}
ETIQUETAS_UNIDADES_ESTIMADAS = {
    "1_5": "1–5", "6_15": "6–15", "16_50": "16–50",
    "mas_50": "Más de 50", "sin_definir": "sin definir",
}
ETIQUETAS_PLAZO_PROYECTO = {
    "menos_3_meses": "menos de 3 meses", "3_6_meses": "3–6 meses",
    "6_12_meses": "6–12 meses", "sin_definir": "sin definir",
}
ETIQUETAS_TIPO_ENTIDAD = {
    "ayuntamiento": "Ayuntamiento", "empresa": "Empresa", "puerto": "Puerto",
    "hotel_resort": "Hotel / Resort", "otro": "Otro",
}

# Estados de Apollo que HubSpot no puede deducir por su cuenta. La respuesta
# NO está aquí a propósito: la detecta HubSpot (ver sync_replies).
ESTADO_SOLO_APOLLO = {
    "bounced": "rebotado",
    "hard_bounced": "rebotado",
    "spam_blocked": "rebotado",
}

# Estados desde los que todavía se puede pasar a «respondido»
EN_CURSO = ["enviado", "abierto"]

# Cuándo se inscribió el contacto en Apollo. Las señales de parada (respuesta,
# reunión, correo entrante) solo cuentan si son posteriores: un contacto que
# ya estaba en el CRM puede traer respuestas o reuniones de hace años que no
# tienen nada que ver con esta campaña.
FECHA_INSCRIPCION = "apollo_fecha_inscripcion"

# Propiedades del puente que existen también en el objeto negocio. Las demás
# (campana_apollo, municipio, apollo_fecha_inscripcion) solo están en el
# contacto: mandarlas al negocio hace que HubSpot rechace el PATCH entero.
PROPS_NEGOCIO = {"apollo_estado", "apollo_fecha_respuesta"}


def _req(url, method, headers, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:400]
        raise RuntimeError(f"{method} {url} -> {e.code}: {detail}") from None


def hs(method, path, body=None):
    return _req(
        "https://api.hubapi.com" + path, method,
        {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
        body,
    )


def apollo(method, path, body=None):
    return _req(
        "https://api.apollo.io/api/v1" + path, method,
        {"x-api-key": APOLLO_API_KEY, "Content-Type": "application/json",
         "Cache-Control": "no-cache", "accept": "application/json"},
        body,
    )


def log(*a):
    print(*a, flush=True)


def write(label, fn):
    """Ejecuta fn solo si el puente está habilitado; si no, lo anuncia."""
    if not ENABLED:
        log(f"    [simulacro] {label}")
        return None
    return fn()


def _ahora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts(valor):
    """Fecha tal y como la devuelve HubSpot (ISO 8601 o epoch en ms) -> datetime."""
    if not valor:
        return None
    if str(valor).isdigit():
        return datetime.fromtimestamp(int(valor) / 1000, tz=timezone.utc)
    dt = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _tras_inscripcion(fecha, props):
    """True si `fecha` es posterior a la inscripción del contacto en Apollo.
    Si no consta la inscripción no se descarta nada, para no perder señales
    por falta de dato."""
    inscrito = _ts(props.get(FECHA_INSCRIPCION))
    f = _ts(fecha)
    return not inscrito or not f or f >= inscrito


# --------------------------------------------------------------------------
# Apollo

def apollo_sender_account_id():
    """Buzón por defecto del equipo, que es desde donde sale la secuencia."""
    accounts = apollo("GET", "/email_accounts").get("email_accounts", [])
    if not accounts:
        raise RuntimeError("Apollo no tiene ningún buzón conectado")
    default = next((a for a in accounts if a.get("default")), accounts[0])
    log(f"  buzón remitente: {default.get('email')}")
    return default["id"]


def apollo_contacts(page=1, **filters):
    return apollo("POST", "/contacts/search", {"page": page, "per_page": 100, **filters})


def apollo_find_by_email(email):
    res = apollo_contacts(q_keywords=email)
    iguales = [c for c in res.get("contacts", [])
               if (c.get("email") or "").lower() == email.lower()]
    if len(iguales) > 1:
        # Apollo permite duplicar un contacto (uno creado a mano o por el
        # puente y otro traído después por el pull de HubSpot). Se prefiere
        # el que ya está en una de nuestras secuencias: es del que hay que
        # leer el estado y al que hay que parar. Si ninguno lo está, el
        # primero. Que quede en el log, en cualquier caso.
        nuestras = {SEQ_INBOUND, SEQ_OUTBOUND}
        en_secuencia = [c for c in iguales
                        if nuestras & set(c.get("emailer_campaign_ids") or [])]
        elegido = (en_secuencia or iguales)[0]
        log(f"  aviso: {email} tiene {len(iguales)} contactos en Apollo; se usa {elegido['id']}")
        return elegido
    return iguales[0] if iguales else None


def apollo_create_contact(props):
    """Crea en Apollo el contacto de un lead del formulario con sus datos de
    identidad. Los campos del formulario van después, por `_volcar_en_apollo`,
    que es quien sabe recortarlos a los topes de Apollo. Si Apollo ya tuviera
    ese email, devuelve el existente en vez de duplicarlo."""
    body = {"email": props["email"]}
    for prop_hs, prop_apollo in (("firstname", "first_name"), ("lastname", "last_name"),
                                 ("company", "organization_name"), ("jobtitle", "title"),
                                 ("phone", "direct_phone")):
        if props.get(prop_hs):
            body[prop_apollo] = props[prop_hs]
    contacto = apollo("POST", "/contacts", body).get("contact")
    if not contacto or not contacto.get("id"):
        raise RuntimeError(f"Apollo no devolvió el contacto creado para {props['email']}")
    return contacto


def apollo_enroll(sequence_id, contact_ids, sender_id):
    return apollo("POST", f"/emailer_campaigns/{sequence_id}/add_contact_ids", {
        "emailer_campaign_id": sequence_id,
        "contact_ids": contact_ids,
        "send_email_from_email_account_id": sender_id,
    })


def apollo_stop(sequence_id, contact_ids):
    # A diferencia de add_contact_ids, esta ruta NO lleva el id de la secuencia
    # y espera las secuencias en plural. Con el id en la ruta Apollo devolvía
    # 404 y el puente no podía cortar ninguna secuencia.
    return apollo("POST", "/emailer_campaigns/remove_or_stop_contact_ids", {
        "emailer_campaign_ids": [sequence_id],
        "contact_ids": contact_ids,
        "mode": "mark_as_finished",
    })


# --------------------------------------------------------------------------
# HubSpot

def hs_search_contacts(filter_groups, properties):
    out, after = [], None
    while True:
        body = {"filterGroups": filter_groups, "properties": properties, "limit": 100}
        if after:
            body["after"] = after
        res = hs("POST", "/crm/v3/objects/contacts/search", body)
        out += res.get("results", [])
        after = res.get("paging", {}).get("next", {}).get("after")
        if not after:
            return out


def hs_deal_ids(contact_id):
    """Negocios del contacto en el pipeline de Mobiliario Urbano — solo esos.
    Un contacto puede tener negocios de otros pipelines (cliente de otra línea,
    pruebas antiguas) y el puente no debe tocarlos."""
    res = hs("GET", f"/crm/v4/objects/contacts/{contact_id}/associations/deals")
    ids = [str(r["toObjectId"]) for r in res.get("results", [])]
    if not ids:
        return []
    lote = hs("POST", "/crm/v3/objects/deals/batch/read",
              {"inputs": [{"id": i} for i in ids], "properties": ["pipeline"]})
    return [d["id"] for d in lote.get("results", [])
            if d["properties"].get("pipeline") == PIPELINE]


# Contactos sellados en esta pasada. El índice de búsqueda de HubSpot tarda
# unos segundos en reflejar un PATCH, así que una fase posterior que busque
# «contactos en curso» todavía ve el estado viejo: el 07/09 RESPUESTA marcó a
# un contacto como respondido y, 3 s después, SIN RESPUESTA lo encontró aún
# «enviado», vio su secuencia terminada (la acabábamos de parar nosotros) y lo
# pasó a finalizado y su negocio a Descartado. Lo que ya se selló en la pasada
# no se vuelve a evaluar hasta la siguiente.
SELLADOS = set()


def hs_stamp(contact_id, props):
    """Escribe las propiedades en el contacto y, las que existen allí, en sus
    negocios del pipeline."""
    SELLADOS.add(contact_id)
    write(f"contacto {contact_id} <- {props}",
          lambda: hs("PATCH", f"/crm/v3/objects/contacts/{contact_id}", {"properties": props}))
    en_negocio = {k: v for k, v in props.items() if k in PROPS_NEGOCIO}
    if not en_negocio or not ENABLED:
        return
    for deal_id in hs_deal_ids(contact_id):
        hs("PATCH", f"/crm/v3/objects/deals/{deal_id}", {"properties": en_negocio})


# --------------------------------------------------------------------------
# Tareas

def _productos_legibles(valor_hubspot):
    """Lo que marcó en «productos de interés», dicho como lo diría una persona.

    «Otro» es una casilla del formulario, no un producto: en el correo, «tu
    solicitud de Otro» delata la plantilla. Si es lo único que marcó, se
    habla de «mobiliario urbano»; si va con otras cosas, se quita y se cierra
    con «y otras piezas». El resto de etiquetas salen como siempre."""
    valores = [v for v in (valor_hubspot or "").split(";") if v]
    otros = [ETIQUETAS_PRODUCTOS_INTERES.get(v, v) for v in valores if v != "otro"]
    if not otros:
        return "mobiliario urbano"
    texto = ", ".join(otros)
    return f"{texto} y otras piezas" if len(otros) < len(valores) else texto


def _etiquetas(valor_hubspot, mapa):
    """Traduce uno o varios valores internos de HubSpot (separados por ';')
    a sus etiquetas legibles, para que el correo cite algo con sentido."""
    if not valor_hubspot:
        return ""
    return ", ".join(mapa.get(v, v) for v in valor_hubspot.split(";") if v)


def _volcar_en_apollo(email, contact_id, campos):
    """Escribe los campos del formulario en el contacto de Apollo.

    Apollo impone topes por tipo de campo (texto corto 30, texto largo 100)
    que no se pueden configurar. Si rechaza un valor por longitud, responde
    «Value for <campo> is over length limit <N>»: se recorta ese campo a N y
    se reintenta, en vez de dejar al lead sin inscribir. Como mucho una
    vuelta por campo."""
    marca = "is over length limit "
    for _ in range(len(campos) + 1):
        try:
            return write(f"volcar datos del formulario de {email} en Apollo",
                         lambda: apollo("PATCH", f"/contacts/{contact_id}",
                                        {"typed_custom_fields": campos}))
        except RuntimeError as e:
            msg = str(e)
            if "Value for " not in msg or marca not in msg:
                raise
            etiqueta = msg.split("Value for ", 1)[1].split(marca, 1)[0].strip()
            digitos = ""
            for ch in msg.split(marca, 1)[1]:
                if not ch.isdigit():
                    break
                digitos += ch
            tope = int(digitos or 0)
            campo = ETIQUETAS_CAMPOS_APOLLO.get(etiqueta)
            if not campo or not tope or campo not in campos:
                raise
            if campo == CAMPOS_APOLLO_INBOUND["productos_interes"] and len(PRODUCTOS_RESUMIDOS) <= tope:
                campos[campo] = PRODUCTOS_RESUMIDOS
            else:
                campos[campo] = campos[campo][:tope - 1] + "…"
            log(f"  {email}: «{etiqueta}» recortado a {tope} caracteres (tope de Apollo)")
    raise RuntimeError("no se pudieron encajar los campos en los topes de Apollo")


def enroll_inbound(sender_id):
    """Leads del formulario web que aún no están en la secuencia."""
    # lastmodifieddate, no createdate: si el email ya existía en el CRM,
    # HubSpot actualiza ese contacto en vez de crear uno nuevo, así que su
    # fecha de creación puede ser de años atrás aunque el formulario se
    # acabe de rellenar. createdate dejaba fuera a cualquier lead que ya
    # estuviera en el CRM por otro motivo.
    desde = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    leads = hs_search_contacts(
        [{"filters": [
            {"propertyName": "productos_interes", "operator": "HAS_PROPERTY"},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
            {"propertyName": "apollo_estado", "operator": "NOT_HAS_PROPERTY"},
            {"propertyName": "lastmodifieddate", "operator": "GTE", "value": desde},
        ]}],
        ["email", "firstname", "lastname", "company", "jobtitle", "phone",
         "recent_conversion_date", "apollo_estado", "productos_interes",
         "unidades_estimadas", "plazo_proyecto", "tipo_entidad", "message"],
    )
    log(f"INBOUND: {len(leads)} lead(s) pendientes de inscribir")
    errores = 0
    for lead in leads:
        props = lead["properties"]
        email = props["email"]
        try:
            contacto = apollo_find_by_email(email)
            if not contacto:
                # Lo normal es que el pull nativo HubSpot->Apollo traiga al lead
                # en ~10 min, y se le da esa oportunidad (así el contacto queda
                # enlazado al CRM y no hay duplicados). Si no llega, el puente
                # lo crea él mismo: INBOUND no debe depender de la integración
                # nativa ni el lead quedarse horas —o para siempre— esperando.
                formulario = _ts(props.get("recent_conversion_date"))
                espera = datetime.now(timezone.utc) - formulario if formulario else None
                if espera is not None and espera < timedelta(minutes=ESPERA_PULL_MIN):
                    log(f"  {email}: todavía no está en Apollo; se espera al pull nativo "
                        f"hasta la próxima pasada ({ESPERA_PULL_MIN} min desde el formulario)")
                    continue
                log(f"  {email}: no está en Apollo pasados {ESPERA_PULL_MIN} min; lo crea el puente")
                contacto = write(f"crear {email} en Apollo", lambda: apollo_create_contact(props))
                if not contacto:
                    continue   # simulacro: sin id no hay nada más que anunciar

            # Vuelca lo que contó en el formulario a los campos personalizados de
            # Apollo, para que la secuencia INBOUND lo cite de verdad y no hable
            # en genérico. Tiene que ir antes de inscribirlo: el primer correo
            # sale nada más entrar.
            productos = _productos_legibles(props.get("productos_interes"))
            if len(productos) > LIMITE_PRODUCTOS:
                productos = PRODUCTOS_RESUMIDOS
            mensaje = props.get("message") or ""
            if len(mensaje) > LIMITE_MENSAJE:
                mensaje = mensaje[:LIMITE_MENSAJE - 1] + "…"
            campos = {
                CAMPOS_APOLLO_INBOUND["productos_interes"]: productos,
                CAMPOS_APOLLO_INBOUND["unidades_estimadas"]:
                    _etiquetas(props.get("unidades_estimadas"), ETIQUETAS_UNIDADES_ESTIMADAS),
                CAMPOS_APOLLO_INBOUND["plazo_proyecto"]:
                    _etiquetas(props.get("plazo_proyecto"), ETIQUETAS_PLAZO_PROYECTO),
                CAMPOS_APOLLO_INBOUND["tipo_entidad"]:
                    _etiquetas(props.get("tipo_entidad"), ETIQUETAS_TIPO_ENTIDAD),
                CAMPOS_APOLLO_INBOUND["message"]: mensaje,
            }
            _volcar_en_apollo(email, contacto["id"], campos)
            write(f"inscribir {email} en INBOUND",
                  lambda c=contacto: apollo_enroll(SEQ_INBOUND, [c["id"]], sender_id))
            hs_stamp(lead["id"], {"apollo_estado": "enviado", "campana_apollo": CAMPANA,
                                  FECHA_INSCRIPCION: _ahora()})
        except Exception as e:
            # Un lead roto (p. ej. la API key de Apollo sin permiso de
            # escritura) no debe tumbar el resto de la pasada: sin este
            # try/except, una sola excepción aquí mataba también OUTBOUND
            # y REBOTES en cada pasada, aunque no tuvieran nada que ver.
            log(f"  {email}: ERROR al inscribir en INBOUND — {e}")
            errores += 1
    if errores:
        # Que la pasada salga en rojo en Actions: si no, dos leads fallando
        # cada hora pasan por una ejecución "correcta".
        raise RuntimeError(f"{errores} lead(s) no se pudieron inscribir (ver arriba)")


def enroll_outbound(sender_id):
    """Hasta CAP ayuntamientos al día, desde la lista de Apollo."""
    candidatos, page = {}, 1
    while len(candidatos) < CAP:
        res = apollo_contacts(page=page, contact_label_ids=[LIST_OUTBOUND])
        lote = res.get("contacts", [])
        if not lote:
            break
        for c in lote:
            if c.get("emailer_campaign_ids"):
                continue          # ya está en alguna secuencia
            if not c.get("email"):
                continue          # sin correo no hay nada que enviar
            candidatos[c["email"]] = c
            if len(candidatos) >= CAP:
                break
        if page >= res.get("pagination", {}).get("total_pages", 1):
            break
        page += 1

    # No basta con que Apollo diga "sin secuencia activa": si ya se procesó
    # antes (respondió, se descartó, rebotó...) HubSpot lo sabe aunque Apollo
    # haya limpiado el campo al terminar. Sin este filtro, un ayuntamiento ya
    # cerrado podría reinscribirse solo y volver a recibir los 5 correos.
    ya_procesados = {
        h["properties"]["email"].lower()
        for h in hs_search_contacts(
            [{"filters": [
                {"propertyName": "email", "operator": "IN", "values": list(candidatos)},
                {"propertyName": "apollo_estado", "operator": "HAS_PROPERTY"},
            ]}],
            ["email"],
        )
    }
    pendientes = [c["id"] for email, c in candidatos.items() if email.lower() not in ya_procesados]
    municipio_de = {email.lower(): (c.get("typed_custom_fields") or {}).get(CAMPO_APOLLO_MUNICIPIO)
                    for email, c in candidatos.items() if email.lower() not in ya_procesados}
    saltados = len(candidatos) - len(pendientes)

    log(f"OUTBOUND: {len(pendientes)} ayuntamiento(s) a inscribir hoy (tope {CAP})"
        + (f", {saltados} descartado(s) por tener ya apollo_estado en HubSpot" if saltados else ""))
    if not pendientes:
        return

    write(f"inscribir {len(pendientes)} en OUTBOUND",
          lambda: apollo_enroll(SEQ_OUTBOUND, pendientes, sender_id))

    # Marcar campana_apollo en HubSpot: es lo que activa el workflow que crea
    # el negocio (dispara con la lista 2845, filtrada por esta propiedad). Sin
    # este paso el correo sale pero nunca aparece un negocio en el pipeline.
    # Solo se puede marcar a quien Apollo ya haya empujado a HubSpot; el resto
    # queda para la siguiente pasada, cuando el pull automático (cada 15 min)
    # los haya traído.
    #
    # También se copia "municipio": el nombre del negocio lo genera el
    # workflow con {{ enrolled_object.municipio }}, y la integración nativa
    # Apollo-HubSpot solo trae el "city" que calcula Apollo automáticamente
    # -no fiable para pueblos pequeños-, no el campo "Municipio" verificado
    # a mano. Sin este paso, varios negocios saldrían con el nombre del
    # pueblo mal o en blanco aunque el correo esté perfecto.
    en_hubspot = hs_search_contacts(
        [{"filters": [{"propertyName": "email", "operator": "IN", "values": list(municipio_de)}]}],
        ["email", "campana_apollo", "municipio", "apollo_estado"],
    )
    marcados = 0
    for h in en_hubspot:
        props = {}
        if h["properties"].get("campana_apollo") != CAMPANA:
            props["campana_apollo"] = CAMPANA
        municipio = municipio_de.get((h["properties"].get("email") or "").lower())
        if municipio and h["properties"].get("municipio") != municipio:
            props["municipio"] = municipio
        # Sin apollo_estado el contacto es invisible para el resto del puente:
        # ni respuesta, ni reunión, ni descarte lo tocarían nunca.
        if not h["properties"].get("apollo_estado"):
            props["apollo_estado"] = "enviado"
            props[FECHA_INSCRIPCION] = _ahora()
        if props:
            hs_stamp(h["id"], props)
            marcados += 1
    log(f"OUTBOUND: {marcados}/{len(pendientes)} ya estaban en HubSpot y quedan "
        f"marcados; el resto se marca en cuanto Apollo los empuje")


def _apollo_sequences_of(email):
    """Secuencias en las que el contacto sigue activo, si está en Apollo."""
    c = apollo_find_by_email(email)
    return (c, c.get("emailer_campaign_ids") or []) if c else (None, [])


def sync_replies():
    """La respuesta la capta HubSpot; aquí solo se actúa sobre ella.

    `hs_sales_email_last_replied` es una propiedad nativa: HubSpot la rellena
    al registrar la respuesta a un correo de ventas, que es justo lo que Apollo
    empuja al CRM. No dependemos de ningún campo indocumentado de Apollo.

    También mira a los ya «finalizado» (descartados por `mark_sin_respuesta`):
    una respuesta puede llegar tarde, después de que la secuencia terminara y
    el negocio se descartara solo. El workflow de HubSpot que mueve a «Muestra
    interés» solo dispara desde «Información enviada», así que si el negocio
    ya está en «Descartado» no lo reabriría por su cuenta — por eso aquí se
    reabre a mano en ese caso.
    """
    respondieron = hs_search_contacts(
        [{"filters": [
            {"propertyName": "campana_apollo", "operator": "EQ", "value": CAMPANA},
            {"propertyName": "hs_sales_email_last_replied", "operator": "HAS_PROPERTY"},
            {"propertyName": "apollo_estado", "operator": "IN", "values": EN_CURSO + ["finalizado"]},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
        ]}],
        ["email", "apollo_estado", "hs_sales_email_last_replied", FECHA_INSCRIPCION],
    )
    # Solo cuenta la respuesta posterior a la inscripción: un contacto que ya
    # estaba en el CRM puede traer una respuesta de hace meses a otro correo.
    respondieron = [h for h in respondieron
                    if _tras_inscripcion(h["properties"]["hs_sales_email_last_replied"],
                                         h["properties"])]
    log(f"RESPUESTA: {len(respondieron)} contacto(s) han respondido")
    for h in respondieron:
        props = h["properties"]
        era_finalizado = props["apollo_estado"] == "finalizado"
        hs_stamp(h["id"], {
            "apollo_estado": "respondido",
            "apollo_fecha_respuesta": props["hs_sales_email_last_replied"],
        })
        if era_finalizado:
            for deal_id in hs_deal_ids(h["id"]):
                deal = hs("GET", f"/crm/v3/objects/deals/{deal_id}?properties=dealstage")
                if deal["properties"].get("dealstage") == ETAPA_DESCARTADO:
                    write(f"reabrir el negocio {deal_id} — respuesta tardía tras el descarte",
                          lambda d=deal_id: hs("PATCH", f"/crm/v3/objects/deals/{d}",
                                                {"properties": {"dealstage": ETAPA_MUESTRA_INTERES,
                                                                "motivo_perdida": ""}}))
        # Apollo suele parar solo al detectar la respuesta, pero si el correo
        # entró por otra vía (respondieron a Amaia directamente) no se entera.
        contacto, activas = _apollo_sequences_of(props["email"])
        for seq in (SEQ_INBOUND, SEQ_OUTBOUND):
            if seq in activas:
                write(f"sacar {props['email']} de {seq}",
                      lambda s=seq, c=contacto: apollo_stop(s, [c["id"]]))


def sync_bounces():
    """Lo único que HubSpot no puede saber: el correo que nunca llegó."""
    marcados, page = 0, 1
    while True:
        res = apollo_contacts(page=page, contact_label_ids=[LIST_OUTBOUND])
        lote = res.get("contacts", [])
        if not lote:
            break
        for c in lote:
            estado = next(
                (ESTADO_SOLO_APOLLO[s["status"]]
                 for s in (c.get("contact_campaign_statuses") or [])
                 if s.get("emailer_campaign_id") in (SEQ_INBOUND, SEQ_OUTBOUND)
                 and s.get("status") in ESTADO_SOLO_APOLLO),
                None)
            if not estado or not c.get("email"):
                continue
            for h in hs_search_contacts(
                    [{"filters": [
                        {"propertyName": "email", "operator": "EQ", "value": c["email"]},
                        {"propertyName": "apollo_estado", "operator": "IN", "values": EN_CURSO},
                    ]}],
                    ["email", "apollo_estado"]):
                hs_stamp(h["id"], {"apollo_estado": estado})
                marcados += 1
        if page >= res.get("pagination", {}).get("total_pages", 1):
            break
        page += 1
    log(f"REBOTES: {marcados} contacto(s) marcados como rebotados")


def hs_search_deals(filter_groups, properties):
    out, after = [], None
    while True:
        body = {"filterGroups": filter_groups, "properties": properties, "limit": 100}
        if after:
            body["after"] = after
        res = hs("POST", "/crm/v3/objects/deals/search", body)
        out += res.get("results", [])
        after = res.get("paging", {}).get("next", {}).get("after")
        if not after:
            return out


def hs_contact_ids_of_deal(deal_id):
    res = hs("GET", f"/crm/v4/objects/deals/{deal_id}/associations/contacts")
    return [r["toObjectId"] for r in res.get("results", [])]


def _sacar_de_apollo(email, motivo):
    contacto = apollo_find_by_email(email)
    if not contacto:
        return
    for seq in (SEQ_INBOUND, SEQ_OUTBOUND):
        if seq in (contacto.get("emailer_campaign_ids") or []):
            write(f"sacar {email} de la secuencia — {motivo}",
                  lambda s=seq, c=contacto: apollo_stop(s, [c["id"]]))


def stop_when_engaged():
    """Corta la cadencia en cuanto hay contacto real, venga por donde venga.

    Tres señales, y ninguna depende de que Apollo hile bien la conversación:

      a) Reunión agendada en el calendario de Amaia. Apollo no lo ve.
      b) El negocio ha salido de la primera etapa. Da igual el motivo: si
         Amaia movió la ficha es que ha pasado algo, aunque fuera una llamada.
      c) Alguien marcó el estado a mano en HubSpot. No hace falta para nada,
         pero deja a Amaia una salida de emergencia si la necesita.
    """
    # (a) y (c) — se leen del contacto. Incluye "finalizado" porque una
    # reunión puede agendarse tarde, tras el descarte automático — el
    # negocio se reabre a mano si hace falta, igual que con una respuesta.
    por_contacto = hs_search_contacts(
        [{"filters": [
            {"propertyName": "engagements_last_meeting_booked", "operator": "HAS_PROPERTY"},
            {"propertyName": "apollo_estado", "operator": "IN", "values": EN_CURSO + ["finalizado"]},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
         ]},
         {"filters": [
            {"propertyName": "apollo_estado", "operator": "IN",
             "values": ["respondido", "reunion_agendada", "baja"]},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
         ]}],
        ["email", "apollo_estado", "engagements_last_meeting_booked", FECHA_INSCRIPCION],
    )
    for h in por_contacto:
        if h["id"] in SELLADOS:
            continue
        props = h["properties"]
        if props["apollo_estado"] in EN_CURSO + ["finalizado"]:  # llegó por la reunión
            # Una reunión de antes de la campaña no es una señal de esta.
            if not _tras_inscripcion(props.get("engagements_last_meeting_booked"), props):
                continue
            era_finalizado = props["apollo_estado"] == "finalizado"
            hs_stamp(h["id"], {"apollo_estado": "reunion_agendada"})
            if era_finalizado:
                for deal_id in hs_deal_ids(h["id"]):
                    deal = hs("GET", f"/crm/v3/objects/deals/{deal_id}?properties=dealstage")
                    if deal["properties"].get("dealstage") == ETAPA_DESCARTADO:
                        write(f"reabrir el negocio {deal_id} — reunión agendada tras el descarte",
                              lambda d=deal_id: hs("PATCH", f"/crm/v3/objects/deals/{d}",
                                                    {"properties": {"dealstage": ETAPA_MUESTRA_INTERES,
                                                                    "motivo_perdida": ""}}))
            _sacar_de_apollo(props["email"], "reunión agendada")
        else:                                       # ya estaba marcado
            _sacar_de_apollo(props["email"], f"estado {props['apollo_estado']}")
    log(f"PARADA · contacto: {len(por_contacto)} revisado(s)")

    # (b) — se lee del negocio: cualquier etapa que no sea la primera
    avanzados = hs_search_deals(
        [{"filters": [
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE},
            {"propertyName": "dealstage", "operator": "NEQ", "value": ETAPA_LEAD},
        ]}],
        ["dealname", "dealstage"],
    )
    tocados = 0
    for deal in avanzados:
        for contact_id in hs_contact_ids_of_deal(deal["id"]):
            c = hs("GET", f"/crm/v3/objects/contacts/{contact_id}"
                          "?properties=email,apollo_estado")["properties"]
            if c.get("apollo_estado") in EN_CURSO and c.get("email"):
                hs_stamp(contact_id, {"apollo_estado": "respondido"})
                _sacar_de_apollo(c["email"], "su negocio ya avanzó de etapa")
                tocados += 1
    log(f"PARADA · negocio: {tocados} contacto(s) con el negocio ya avanzado")


def _chunks(xs, n=100):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def stop_on_any_inbound():
    """Corta si el propio contacto escribe por su cuenta, en un hilo nuevo en
    vez de responder al de la secuencia — Apollo no lo reconoce como
    respuesta suya y seguiría enviando.

    A propósito solo cuenta la dirección exacta del contacto inscrito: si
    contesta un compañero suyo desde otra dirección del mismo ayuntamiento,
    no se considera respuesta.
    """
    activos = hs_search_contacts(
        [{"filters": [
            {"propertyName": "campana_apollo", "operator": "EQ", "value": CAMPANA},
            {"propertyName": "apollo_estado", "operator": "IN", "values": EN_CURSO},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
        ]}],
        ["email", "apollo_estado", FECHA_INSCRIPCION],
    )
    activos = [h for h in activos if h["id"] not in SELLADOS]
    if not activos:
        log("ENTRANTES: no hay contactos en cadencia")
        return

    limite = (datetime.now(timezone.utc) - timedelta(days=VENTANA_CADENCIA)).isoformat()
    por_email = {h["properties"]["email"].lower(): h for h in activos}
    parar = set()

    for lote in _chunks(list(por_email), 50):
        res = hs("POST", "/crm/v3/objects/emails/search", {
            "filterGroups": [{"filters": [
                {"propertyName": "hs_email_direction", "operator": "EQ", "value": "INCOMING_EMAIL"},
                {"propertyName": "hs_email_from_email", "operator": "IN", "values": lote},
                {"propertyName": "hs_timestamp", "operator": "GTE", "value": limite},
            ]}],
            "properties": ["hs_email_from_email", "hs_timestamp"],
            "limit": 100,
        })
        for e in res.get("results", []):
            remitente = (e["properties"].get("hs_email_from_email") or "").lower()
            h = por_email.get(remitente)
            # Un correo suyo anterior a la inscripción no es respuesta a esta campaña.
            if h and _tras_inscripcion(e["properties"].get("hs_timestamp"), h["properties"]):
                parar.add(h["id"])

    for h in activos:
        if h["id"] in parar:
            hs_stamp(h["id"], {"apollo_estado": "respondido"})
            _sacar_de_apollo(h["properties"]["email"], "ha entrado correo del propio contacto")

    log(f"ENTRANTES: {len(activos)} en cadencia, {len(parar)} parado(s)")


def mark_sin_respuesta():
    """Si la secuencia de Apollo termina sin que haya habido respuesta, el
    negocio se descarta solo: nadie tiene que ir a cerrarlo a mano.

    Cubre INBOUND y OUTBOUND por igual, buscando en HubSpot (no en la lista
    de Apollo, que solo tiene los de OUTBOUND) a cualquier contacto de la
    campaña que siga «en curso» y comprobando en Apollo si su secuencia ya
    terminó (status "finished") sin que hubiera respuesta.
    """
    activos = hs_search_contacts(
        [{"filters": [
            {"propertyName": "campana_apollo", "operator": "EQ", "value": CAMPANA},
            {"propertyName": "apollo_estado", "operator": "IN", "values": EN_CURSO},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
        ]}],
        ["email", "apollo_estado"],
    )
    activos = [h for h in activos if h["id"] not in SELLADOS]
    descartados = 0
    for h in activos:
        contacto = apollo_find_by_email(h["properties"]["email"])
        if not contacto:
            continue
        estados = {s.get("emailer_campaign_id"): s.get("status")
                   for s in (contacto.get("contact_campaign_statuses") or [])}
        if not any(estados.get(seq) == "finished" for seq in (SEQ_INBOUND, SEQ_OUTBOUND)):
            continue
        write(f"marcar {h['properties']['email']} como finalizado sin respuesta",
              lambda hid=h["id"]: hs_stamp(hid, {"apollo_estado": "finalizado"}))
        for deal_id in hs_deal_ids(h["id"]):
            deal = hs("GET", f"/crm/v3/objects/deals/{deal_id}?properties=dealstage")
            if deal["properties"].get("dealstage") == ETAPA_LEAD:
                write(f"descartar el negocio {deal_id} — sin respuesta tras la secuencia",
                      lambda d=deal_id: hs("PATCH", f"/crm/v3/objects/deals/{d}",
                                            {"properties": {"dealstage": ETAPA_DESCARTADO,
                                                            "motivo_perdida": MOTIVO_SIN_RESPUESTA}}))
        descartados += 1
    log(f"SIN RESPUESTA: {descartados}/{len(activos)} negocio(s) pasan a Descartado")


def _fase(nombre, fn):
    """Corre una fase de la pasada de forma aislada: si una revienta (una API
    key mal configurada, un timeout...) no debe impedir que las demás corran
    — sin esto, un solo fallo en INBOUND se llevaba por delante OUTBOUND y
    REBOTES en cada pasada, aunque no tuvieran nada que ver."""
    try:
        fn()
        return True
    except Exception as e:
        log(f"### {nombre} FALLÓ: {e}")
        return False


def main():
    if not HUBSPOT_TOKEN or not APOLLO_API_KEY:
        sys.exit("Faltan HUBSPOT_TOKEN o APOLLO_API_KEY")
    if not ENABLED:
        log("=== SIMULACRO: no se escribe nada. Define BRIDGE_ENABLED=1 para activar. ===")
    sender_id = apollo_sender_account_id()
    # Primero lo que corta, luego lo que inscribe: así nunca se escribe a
    # alguien que ya ha respondido o tiene reunión.
    ok = True
    ok &= _fase("RESPUESTA", sync_replies)
    ok &= _fase("PARADA", stop_when_engaged)
    ok &= _fase("ENTRANTES", stop_on_any_inbound)
    ok &= _fase("SIN RESPUESTA", mark_sin_respuesta)
    ok &= _fase("INBOUND", lambda: enroll_inbound(sender_id))
    # OUTBOUND solo inscribe una vez al día, a esta hora — si no, el tope de
    # 50 se salta: el cron corre cada hora, así que sin este freno un lunes
    # con mucho pendiente (importación semanal) metería 50 en la primera
    # pasada y otros 50 en la siguiente, la misma mañana.
    if not OUTBOUND_ENABLED:
        log("OUTBOUND: desactivado explícitamente (OUTBOUND_ENABLED=0)")
    elif datetime.now(timezone.utc).hour == HORA_ENVIO_OUTBOUND:
        ok &= _fase("OUTBOUND", lambda: enroll_outbound(sender_id))
    else:
        log(f"OUTBOUND: no toca todavía hoy (se inscribe a las {HORA_ENVIO_OUTBOUND}:20 UTC)")
    ok &= _fase("REBOTES", sync_bounces)
    log("Listo." if ok else "Listo, con fallos — revisa los ### de arriba.")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
