# Puente Apollo ↔ HubSpot

Apollo envía los correos, HubSpot es el CRM y el pipeline. `apollo_hubspot_bridge.py`
es la única pieza que los une. Se lanza cada hora desde
`.github/workflows/apollo-bridge.yml`.

## Qué hace en cada pasada

| Paso | Qué mira | Qué hace |
|---|---|---|
| **RESPUESTA** | Contactos de HubSpot con `hs_sales_email_last_replied` relleno | Marca `apollo_estado = respondido`, copia la fecha y los saca de la secuencia |
| **PARADA** | Cuatro señales, ver abajo | Saca al contacto de la secuencia |
| **INBOUND** | Contactos con `productos_interes` relleno y `apollo_estado` vacío (últimos 30 días) | Los inscribe en la secuencia INBOUND y marca `apollo_estado = enviado` |
| **OUTBOUND** | Contactos de la lista de Apollo que no están en ninguna secuencia | Inscribe hasta 50 al día en la secuencia OUTBOUND, y marca `campana_apollo` en los que ya estén en HubSpot |
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

## Las cuatro señales de parada

La cadencia se corta en cuanto hay contacto real, venga por donde venga. Las tres
primeras son automáticas y no requieren que nadie haga nada:

| Señal | De dónde sale | Qué caso cubre |
|---|---|---|
| Respuesta al contacto | `hs_sales_email_last_replied` | Contestan al hilo, o escriben a Amaia por su cuenta. Su bandeja está conectada a HubSpot, así que lo registra igual |
| Correo entrante del mismo contacto | Objetos `email` con `hs_email_from_email` = su dirección | Escribe a Amaia **en un hilo nuevo** en vez de responder al de la secuencia. Apollo no lo reconoce como respuesta suya |
| Correo entrante del ayuntamiento | Objetos `email` asociados a la empresa | Contesta **otra persona** desde otra dirección. Requiere que el contacto tenga empresa asociada |
| Reunión agendada | `engagements_last_meeting_booked` | Reservan hueco en el calendario. Apollo no lo ve |
| Negocio fuera de «Lead mobiliario» | `dealstage` | Lo que no deja rastro de correo: una llamada, un aviso por LinkedIn |

Las dos del medio exigen el scope `sales-email-read` en el token de HubSpot, y
miran los últimos 45 días. La de dirección funciona siempre; la de empresa solo
para los contactos que tengan empresa asociada.

**Punto débil conocido**: hoy solo la mitad de los contactos del portal tienen
empresa asociada, así que en la otra mitad el caso «contesta un compañero desde
otra dirección» no se detecta. Se arregla activando en HubSpot la creación y
asociación automática de empresas por dominio de correo
(Settings → Objects → Companies), que además beneficia a todo el CRM. No se puede
hacer por API. Buscar por dominio en los correos tampoco es alternativa: la
Search API solo acepta la dirección completa, no comodines.

Además, poner `apollo_estado` a mano en HubSpot también para la cadencia. No hace
falta para nada — es una salida de emergencia, no parte del funcionamiento.

**Por qué la parada la hace el puente y no Apollo**: Apollo corta solo cuando
alguien responde o se marca como interesado, pero no ve el calendario de Amaia.
Si la reunión se agenda desde el enlace de HubSpot, Apollo seguiría escribiendo.

**Por qué el estado se escribe también en el negocio**: los cuatro workflows de
etapa son de objeto negocio y no pueden filtrar por propiedades del contacto.

## Por qué OUTBOUND también escribe en HubSpot

El workflow que crea el negocio para el OUTBOUND (`4840005827`) se dispara con
la lista **2845**, filtrada por `campana_apollo = mobiliario_urbano AND
NOT_IN_LIST 2841`. Sin que algo escriba esa propiedad, la lista nunca se
puebla y el negocio no se crea nunca — el correo sale, pero no aparece nada en
el pipeline. Por eso, tras inscribir en Apollo, el puente busca en HubSpot los
contactos ya pushed desde Apollo y les marca `campana_apollo`. Al que Apollo
aún no haya empujado a HubSpot (el pull tarda hasta 15 min) se le marca en la
siguiente pasada — igual que ya hacía `enroll_inbound` con los suyos.

La exclusión `NOT_IN_LIST 2841` es lo que impide que el negocio se cree dos
veces: en cuanto el workflow se dispara, mete al contacto en la lista 2841
(acción 4), y eso lo saca automáticamente de la 2845.

## Idempotencia

`apollo_estado` en HubSpot es la memoria del puente: si está relleno, el
contacto ya se inscribió. Relanzar el job no duplica nada.

## Configuración en GitHub

**Settings → Secrets and variables → Actions**

| | Nombre | Valor |
|---|---|---|
| Secret | `HUBSPOT_TOKEN` | token de la app privada. Necesita además `sales-email-read` |
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
