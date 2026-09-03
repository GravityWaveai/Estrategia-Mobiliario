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
  5. REBOTES  — lo único que sigue viniendo de Apollo, porque HubSpot no puede
                saberlo: un correo que no llegó nunca no genera actividad.

Es idempotente: `apollo_estado` en HubSpot hace de memoria, así que se puede
relanzar sin duplicar inscripciones.

Variables de entorno:
  HUBSPOT_TOKEN          token de la app privada de HubSpot   (obligatorio)
  APOLLO_API_KEY         API key de Apollo                    (obligatorio)
  BRIDGE_ENABLED         "1" para escribir de verdad; si no, simulacro
  OUTBOUND_DAILY_CAP     tope diario del OUTBOUND (por defecto 50)
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
CAP = int(os.environ.get("OUTBOUND_DAILY_CAP", "50"))

# Identificadores fijos del embudo
SEQ_INBOUND = "6a9844b94208650014fc4754"
SEQ_OUTBOUND = "6a9844f7d0bf520010f72cc1"
LIST_OUTBOUND = "6a983205f242c800107386c8"
CAMPANA = "mobiliario_urbano"
PIPELINE = "4080461018"
ETAPA_LEAD = "5948376264"   # «Lead mobiliario», la primera
VENTANA_CADENCIA = 45       # días que dura la cadencia más larga, con margen

# Estados de Apollo que HubSpot no puede deducir por su cuenta. La respuesta
# NO está aquí a propósito: la detecta HubSpot (ver sync_replies).
ESTADO_SOLO_APOLLO = {
    "bounced": "rebotado",
    "hard_bounced": "rebotado",
    "spam_blocked": "rebotado",
}

# Estados desde los que todavía se puede pasar a «respondido»
EN_CURSO = ["enviado", "abierto"]


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
    for c in res.get("contacts", []):
        if (c.get("email") or "").lower() == email.lower():
            return c
    return None


def apollo_enroll(sequence_id, contact_ids, sender_id):
    return apollo("POST", f"/emailer_campaigns/{sequence_id}/add_contact_ids", {
        "emailer_campaign_id": sequence_id,
        "contact_ids": contact_ids,
        "send_email_from_email_account_id": sender_id,
    })


def apollo_stop(sequence_id, contact_ids):
    return apollo("POST", f"/emailer_campaigns/{sequence_id}/remove_or_stop_contact_ids", {
        "emailer_campaign_id": sequence_id,
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
    res = hs("GET", f"/crm/v4/objects/contacts/{contact_id}/associations/deals")
    return [r["toObjectId"] for r in res.get("results", [])]


def hs_stamp(contact_id, props):
    """Escribe las propiedades en el contacto y en sus negocios del pipeline."""
    write(f"contacto {contact_id} <- {props}",
          lambda: hs("PATCH", f"/crm/v3/objects/contacts/{contact_id}", {"properties": props}))
    for deal_id in (hs_deal_ids(contact_id) if ENABLED else []):
        hs("PATCH", f"/crm/v3/objects/deals/{deal_id}", {"properties": props})


# --------------------------------------------------------------------------
# Tareas

def enroll_inbound(sender_id):
    """Leads del formulario web que aún no están en la secuencia."""
    desde = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    leads = hs_search_contacts(
        [{"filters": [
            {"propertyName": "productos_interes", "operator": "HAS_PROPERTY"},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
            {"propertyName": "apollo_estado", "operator": "NOT_HAS_PROPERTY"},
            {"propertyName": "createdate", "operator": "GTE", "value": desde},
        ]}],
        ["email", "firstname", "apollo_estado"],
    )
    log(f"INBOUND: {len(leads)} lead(s) pendientes de inscribir")
    for lead in leads:
        email = lead["properties"]["email"]
        contacto = apollo_find_by_email(email)
        if not contacto:
            # El pull de HubSpot->Apollo tarda hasta 15 min; se reintenta luego.
            log(f"  {email}: todavía no está en Apollo, se reintenta en la próxima pasada")
            continue
        write(f"inscribir {email} en INBOUND",
              lambda c=contacto: apollo_enroll(SEQ_INBOUND, [c["id"]], sender_id))
        hs_stamp(lead["id"], {"apollo_estado": "enviado", "campana_apollo": CAMPANA})


def enroll_outbound(sender_id):
    """Hasta CAP ayuntamientos al día, desde la lista de Apollo."""
    pendientes, page = [], 1
    while len(pendientes) < CAP:
        res = apollo_contacts(page=page, contact_label_ids=[LIST_OUTBOUND])
        lote = res.get("contacts", [])
        if not lote:
            break
        for c in lote:
            if c.get("emailer_campaign_ids"):
                continue          # ya está en alguna secuencia
            if not c.get("email"):
                continue          # sin correo no hay nada que enviar
            pendientes.append(c["id"])
            if len(pendientes) >= CAP:
                break
        if page >= res.get("pagination", {}).get("total_pages", 1):
            break
        page += 1
    log(f"OUTBOUND: {len(pendientes)} ayuntamiento(s) a inscribir hoy (tope {CAP})")
    if pendientes:
        write(f"inscribir {len(pendientes)} en OUTBOUND",
              lambda: apollo_enroll(SEQ_OUTBOUND, pendientes, sender_id))


def _apollo_sequences_of(email):
    """Secuencias en las que el contacto sigue activo, si está en Apollo."""
    c = apollo_find_by_email(email)
    return (c, c.get("emailer_campaign_ids") or []) if c else (None, [])


def sync_replies():
    """La respuesta la capta HubSpot; aquí solo se actúa sobre ella.

    `hs_sales_email_last_replied` es una propiedad nativa: HubSpot la rellena
    al registrar la respuesta a un correo de ventas, que es justo lo que Apollo
    empuja al CRM. No dependemos de ningún campo indocumentado de Apollo.
    """
    respondieron = hs_search_contacts(
        [{"filters": [
            {"propertyName": "campana_apollo", "operator": "EQ", "value": CAMPANA},
            {"propertyName": "hs_sales_email_last_replied", "operator": "HAS_PROPERTY"},
            {"propertyName": "apollo_estado", "operator": "IN", "values": EN_CURSO},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
        ]}],
        ["email", "apollo_estado", "hs_sales_email_last_replied"],
    )
    log(f"RESPUESTA: {len(respondieron)} contacto(s) han respondido")
    for h in respondieron:
        props = h["properties"]
        hs_stamp(h["id"], {
            "apollo_estado": "respondido",
            "apollo_fecha_respuesta": props["hs_sales_email_last_replied"],
        })
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
    # (a) y (c) — se leen del contacto
    por_contacto = hs_search_contacts(
        [{"filters": [
            {"propertyName": "engagements_last_meeting_booked", "operator": "HAS_PROPERTY"},
            {"propertyName": "apollo_estado", "operator": "IN", "values": EN_CURSO},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
         ]},
         {"filters": [
            {"propertyName": "apollo_estado", "operator": "IN",
             "values": ["respondido", "reunion_agendada", "baja"]},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
         ]}],
        ["email", "apollo_estado"],
    )
    for h in por_contacto:
        props = h["properties"]
        if props["apollo_estado"] in EN_CURSO:      # llegó por la reunión
            hs_stamp(h["id"], {"apollo_estado": "reunion_agendada"})
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
    """Corta si alguien del ayuntamiento ha escrito, sea quien sea.

    El caso que ni Apollo ni las propiedades nativas cubren: escribimos al
    buzón de contratación y contesta el técnico desde su dirección personal.
    Para Apollo eso no es una respuesta a su hilo, y para HubSpot es otro
    contacto, así que el ayuntamiento seguiría recibiendo seguimientos.

    Aquí se mira a nivel de empresa: si hay CUALQUIER correo entrante asociado
    al ayuntamiento después de que empezara la cadencia, se para.
    """
    activos = hs_search_contacts(
        [{"filters": [
            {"propertyName": "campana_apollo", "operator": "EQ", "value": CAMPANA},
            {"propertyName": "apollo_estado", "operator": "IN", "values": EN_CURSO},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
            {"propertyName": "associatedcompanyid", "operator": "HAS_PROPERTY"},
        ]}],
        ["email", "apollo_estado", "associatedcompanyid"],
    )
    if not activos:
        log("ENTRANTES: no hay contactos en cadencia")
        return

    # Un ayuntamiento puede tener varios contactos inscritos
    por_empresa = {}
    for h in activos:
        por_empresa.setdefault(h["properties"]["associatedcompanyid"], []).append(h)

    # Los correos asociados a cada ayuntamiento, sin traerlos enteros
    email_ids, de_quien = [], {}
    for company_id in por_empresa:
        res = hs("GET", f"/crm/v4/objects/companies/{company_id}/associations/emails?limit=100")
        for r in res.get("results", []):
            email_ids.append(r["toObjectId"])
            de_quien[r["toObjectId"]] = company_id

    limite = (datetime.now(timezone.utc) - timedelta(days=VENTANA_CADENCIA)).isoformat()
    con_respuesta = set()
    for lote in _chunks(sorted(set(email_ids))):
        res = hs("POST", "/crm/v3/objects/emails/batch/read", {
            "inputs": [{"id": i} for i in lote],
            "properties": ["hs_email_direction", "hs_timestamp"],
        })
        for e in res.get("results", []):
            p = e["properties"]
            if p.get("hs_email_direction") == "INCOMING_EMAIL" and (p.get("hs_timestamp") or "") >= limite:
                con_respuesta.add(de_quien[int(e["id"])])

    parados = 0
    for company_id in con_respuesta:
        for h in por_empresa[company_id]:
            hs_stamp(h["id"], {"apollo_estado": "respondido"})
            _sacar_de_apollo(h["properties"]["email"], "alguien del ayuntamiento ha escrito")
            parados += 1
    log(f"ENTRANTES: {len(por_empresa)} ayuntamiento(s) en cadencia, "
        f"{len(con_respuesta)} con correo entrante, {parados} contacto(s) parados")


def main():
    if not HUBSPOT_TOKEN or not APOLLO_API_KEY:
        sys.exit("Faltan HUBSPOT_TOKEN o APOLLO_API_KEY")
    if not ENABLED:
        log("=== SIMULACRO: no se escribe nada. Define BRIDGE_ENABLED=1 para activar. ===")
    sender_id = apollo_sender_account_id()
    # Primero lo que corta, luego lo que inscribe: así nunca se escribe a
    # alguien que ya ha respondido o tiene reunión.
    sync_replies()
    stop_when_engaged()
    stop_on_any_inbound()
    enroll_inbound(sender_id)
    enroll_outbound(sender_id)
    sync_bounces()
    log("Listo.")


if __name__ == "__main__":
    main()
