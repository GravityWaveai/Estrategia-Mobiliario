# Puente Apollo ↔ HubSpot

Apollo envía los correos, HubSpot es el CRM y el pipeline. `apollo_hubspot_bridge.py`
es la única pieza que los une. Se lanza cada hora desde
`.github/workflows/apollo-bridge.yml`.

## Qué hace en cada pasada

| Paso | Qué mira | Qué hace |
|---|---|---|
| **PARADA** | Contactos de HubSpot con `engagements_last_meeting_booked` relleno y aún activos en Apollo | Los saca de la secuencia y marca `apollo_estado = reunion_agendada` |
| **INBOUND** | Contactos con `productos_interes` relleno y `apollo_estado` vacío (últimos 30 días) | Los inscribe en la secuencia INBOUND y marca `apollo_estado = enviado` |
| **OUTBOUND** | Contactos de la lista de Apollo que no están en ninguna secuencia | Inscribe hasta 50 al día en la secuencia OUTBOUND |
| **ESTADO** | El estado de campaña de cada contacto en Apollo | Escribe `apollo_estado` y `apollo_fecha_respuesta` en el contacto **y en su negocio** |

La parada va primero a propósito: no tiene sentido inscribir a alguien que
acaba de agendar una reunión.

**Por qué la parada la hace el puente y no Apollo**: Apollo corta solo cuando
alguien responde o se marca como interesado, pero no ve el calendario de Amaia.
Si la reunión se agenda desde el enlace de HubSpot, Apollo seguiría escribiendo.

**Por qué el estado se escribe también en el negocio**: los cuatro workflows de
etapa son de objeto negocio y no pueden filtrar por propiedades del contacto.

## Idempotencia

`apollo_estado` en HubSpot es la memoria del puente: si está relleno, el
contacto ya se inscribió. Relanzar el job no duplica nada.

## Configuración en GitHub

**Settings → Secrets and variables → Actions**

| | Nombre | Valor |
|---|---|---|
| Secret | `HUBSPOT_TOKEN` | token de la app privada de HubSpot |
| Secret | `APOLLO_API_KEY` | Settings → Integrations → API en Apollo |
| Variable | `BRIDGE_ENABLED` | `1` para escribir de verdad. Sin ella, simulacro |
| Variable | `OUTBOUND_DAILY_CAP` | opcional, por defecto `50` |

## Primera ejecución

Lanzar a mano desde la pestaña Actions con `enabled = 0` y leer el log: dice
exactamente qué habría escrito, sin tocar nada. Solo después crear la variable
`BRIDGE_ENABLED = 1`.

## Pendiente de confirmar en la primera pasada real

Apollo no documenta con un nombre estable el momento de la respuesta dentro de
`contact_campaign_statuses`. El script prueba `replied_at` y `last_replied_at`;
si ninguno aparece, el contacto se queda en `finalizado` en vez de `respondido`
y hay que ajustar el nombre del campo mirando el log.

## Identificadores fijos

| Pieza | Id |
|---|---|
| Secuencia INBOUND (Apollo) | `6a9844b94208650014fc4754` |
| Secuencia OUTBOUND (Apollo) | `6a9844f7d0bf520010f72cc1` |
| Lista OUTBOUND (Apollo) | `6a983205f242c800107386c8` |
| Pipeline Mobiliario Urbano (HubSpot) | `4080461018` |
