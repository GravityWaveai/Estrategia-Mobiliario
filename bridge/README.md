# Puente Apollo ↔ HubSpot

Apollo envía los correos, HubSpot es el CRM y el pipeline. `apollo_hubspot_bridge.py`
es la única pieza que los une. Se lanza cada hora desde
`.github/workflows/apollo-bridge.yml`.

## Qué hace en cada pasada

| Paso | Qué mira | Qué hace |
|---|---|---|
| **RESPUESTA** | Contactos de HubSpot con `hs_sales_email_last_replied` relleno | Marca `apollo_estado = respondido`, copia la fecha y los saca de la secuencia |
| **PARADA** | Tres señales: reunión agendada, negocio fuera de la primera etapa, o estado puesto a mano | Saca al contacto de la secuencia |
| **INBOUND** | Contactos con `productos_interes` relleno y `apollo_estado` vacío (últimos 30 días) | Los inscribe en la secuencia INBOUND y marca `apollo_estado = enviado` |
| **OUTBOUND** | Contactos de la lista de Apollo que no están en ninguna secuencia | Inscribe hasta 50 al día en la secuencia OUTBOUND |
| **REBOTES** | El estado de campaña en Apollo | Marca `apollo_estado = rebotado`. Es lo único que sigue viniendo de Apollo |

Lo que corta va primero a propósito: no tiene sentido inscribir a alguien que
acaba de responder o de agendar una reunión.

**Por qué la respuesta la detecta HubSpot y no Apollo**: `hs_sales_email_last_replied`
es una propiedad nativa que HubSpot rellena al registrar la respuesta a un correo
de ventas — y eso es exactamente lo que Apollo le empuja al CRM. Apollo sí sabe
que ha habido respuesta, pero no expone la fecha con un nombre estable en su API,
así que depender de él dejaba el eslabón sin garantía. El negocio, además, avanza
por su cuenta con `hs_latest_sales_email_reply_date`, sin pasar por el puente.

**Por qué los rebotes sí vienen de Apollo**: un correo que nunca llegó no genera
ninguna actividad en HubSpot, así que no hay nada nativo que mirar.

## Las tres señales de parada

La cadencia se corta en cuanto hay contacto real, venga por donde venga. Ninguna
de las tres depende de que Apollo hile bien la conversación:

| Señal | De dónde sale | Qué caso cubre |
|---|---|---|
| Respuesta | `hs_sales_email_last_replied` | Contestan al hilo, o escriben a Amaia por su cuenta. La bandeja de Amaia está conectada a HubSpot, así que lo registra igual |
| Reunión agendada | `engagements_last_meeting_booked` | Reservan hueco en el calendario. Apollo no lo ve |
| Negocio fuera de «Lead mobiliario» | `dealstage` | Cualquier otra cosa: una llamada, un correo desde otra dirección del ayuntamiento, un aviso por LinkedIn. Si Amaia movió la ficha, es que pasó algo |

La tercera es además la válvula manual: Amaia puede poner `apollo_estado` a
«Respondido» en la ficha del contacto y en la siguiente pasada deja de recibir
correos, sin tener que entrar en Apollo.

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

## Identificadores fijos

| Pieza | Id |
|---|---|
| Secuencia INBOUND (Apollo) | `6a9844b94208650014fc4754` |
| Secuencia OUTBOUND (Apollo) | `6a9844f7d0bf520010f72cc1` |
| Lista OUTBOUND (Apollo) | `6a983205f242c800107386c8` |
| Pipeline Mobiliario Urbano (HubSpot) | `4080461018` |
