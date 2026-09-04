# Puente Apollo ↔ HubSpot

Apollo envía los correos, HubSpot es el CRM y el pipeline. `apollo_hubspot_bridge.py`
es la única pieza que los une. Se lanza cada hora desde
`.github/workflows/apollo-bridge.yml`.

## Qué hace en cada pasada

| Paso | Qué mira | Qué hace |
|---|---|---|
| **RESPUESTA** | Contactos de HubSpot con `hs_sales_email_last_replied` relleno | Marca `apollo_estado = respondido`, copia la fecha y los saca de la secuencia |
| **PARADA** | Tres señales, ver abajo | Saca al contacto de la secuencia |
| **DESCARTE** | Contactos «en curso» cuya secuencia de Apollo ya terminó (`status = finished`) sin respuesta | Marca `apollo_estado = finalizado` y mueve el negocio de «Información enviada» a «Descartado» |
| **INBOUND** | Contactos con `productos_interes` relleno y `apollo_estado` vacío (últimos 30 días) | Vuelca en Apollo lo que contó el lead en el formulario (productos, unidades, plazo, tipo de entidad, mensaje), los inscribe en la secuencia INBOUND y marca `apollo_estado = enviado` |
| **OUTBOUND** | Contactos de la lista de Apollo que no están en ninguna secuencia | Inscribe hasta 50 al día en la secuencia OUTBOUND, y marca `campana_apollo` y `municipio` en los que ya estén en HubSpot |
| **REBOTES** | El estado de campaña en Apollo | Marca `apollo_estado = rebotado`. Es lo único que sigue viniendo de Apollo |

Lo que corta va primero a propósito: no tiene sentido inscribir a alguien que
acaba de responder o de agendar una reunión.

**`BRIDGE_ENABLED` activa las dos vías a la vez** — no hay un interruptor
separado por defecto: si se pone a `1` para probar INBOUND, OUTBOUND también
queda activo, sujeto solo a `OUTBOUND_ENROLL_HOUR`. Para probar solo INBOUND
sin arriesgar los 139 ayuntamientos reales de la lista de Apollo, hay que
poner además `OUTBOUND_ENABLED = 0` — con eso el paso OUTBOUND se salta
entero en cada pasada, pase la hora que pase, y no se toca ni Apollo ni
HubSpot para esa parte.

**OUTBOUND solo inscribe una vez al día**, a las `OUTBOUND_ENROLL_HOUR` UTC
(8 por defecto — 10h en España en verano, 9h en invierno), aunque el cron
corra cada hora. Sin este freno, el tope de 50 no era un tope diario de
verdad: si había más de 50 candidatos pendientes en un momento dado —por
ejemplo, tras una importación semanal grande— se inscribían 50 en una pasada
y otros 50 en la siguiente, la misma mañana. El resto de pasos (RESPUESTA,
PARADA, DESCARTE, INBOUND, REBOTES) sí corren en todas las pasadas horarias;
solo la inscripción nueva de OUTBOUND espera a su hora.

Los correos, una vez inscrito el contacto, los manda Apollo según el
calendario propio de esa secuencia (día 0, +5, +10, +16, +23 desde su
inscripción) — no hay ningún "envío diario a todos"; cada ayuntamiento
lleva su propio reloj desde el día en que entra.

**Por qué la respuesta la detecta HubSpot y no Apollo**: `hs_sales_email_last_replied`
es una propiedad nativa que HubSpot rellena al registrar la respuesta a un correo
de ventas — y eso es exactamente lo que Apollo le empuja al CRM. Apollo sí sabe
que ha habido respuesta, pero no expone la fecha con un nombre estable en su API,
así que depender de él dejaba el eslabón sin garantía. El negocio, además, avanza
por su cuenta con `hs_latest_sales_email_reply_date`, sin pasar por el puente.

**Por qué los rebotes sí vienen de Apollo**: un correo que nunca llegó no genera
ninguna actividad en HubSpot, así que no hay nada nativo que mirar.

## Las tres señales de parada

La cadencia se corta en cuanto hay contacto real, venga por donde venga. Las
tres son automáticas y no requieren que nadie haga nada:

| Señal | De dónde sale | Qué caso cubre |
|---|---|---|
| Respuesta al contacto | `hs_sales_email_last_replied` | Contestan al hilo, o escriben a Amaia por su cuenta. Su bandeja está conectada a HubSpot, así que lo registra igual |
| Correo entrante del mismo contacto | Objetos `email` con `hs_email_from_email` = su dirección | Escribe a Amaia **en un hilo nuevo** en vez de responder al de la secuencia. Apollo no lo reconoce como respuesta suya |
| Negocio fuera de «Información enviada» | `dealstage` | Lo que no deja rastro de correo: una llamada, un aviso por LinkedIn |

**A propósito NO cuenta** que conteste otra persona del ayuntamiento desde otra
dirección: solo la del propio contacto inscrito para el email; solo `hs_sales_email_last_replied`
para todo lo demás. Es una decisión explícita, no una limitación técnica.

La primera y la segunda exigen el scope `sales-email-read` en el token de
HubSpot, y miran los últimos 45 días.

Además, poner `apollo_estado` a mano en HubSpot también corta la cadencia. No hace
falta para nada — es una salida de emergencia, no parte del funcionamiento.

## Descarte automático sin respuesta

Si un contacto agota los 5 correos de su secuencia sin que haya habido
respuesta, `mark_sin_respuesta()` lo marca `apollo_estado = finalizado` y
mueve su negocio de «Información enviada» a «Descartado» — sin que Amaia
tenga que revisarlo ni cerrarlo a mano. Se detecta mirando el `status` que
Apollo da a cada contacto dentro de una secuencia (`contact_campaign_statuses`):
cuando pasa a `"finished"` sin que el contacto haya llegado antes a
`respondido`/`reunion_agendada`/etc., se considera que no hubo respuesta.
Solo mueve el negocio si sigue en la primera etapa — si ya avanzó por otro
motivo, no lo toca.

**Respuesta o reunión tardía, después del descarte**: puede pasar — el
ayuntamiento contesta semanas después, cuando el negocio ya está en
«Descartado». El workflow de HubSpot que mueve a «Muestra interés» solo
dispara desde «Información enviada», así que no lo reabriría por su cuenta.
Por eso `sync_replies()` y la parte de reunión de `stop_when_engaged()`
también miran a los contactos en estado `finalizado`, y si su negocio sigue
en «Descartado», lo reabren a mano a «Muestra interés» antes de que el
workflow siga desde ahí con el resto de etapas.

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

**Por qué `enroll_outbound()` también comprueba `apollo_estado` en HubSpot**:
no basta con que Apollo diga que el contacto no está en ninguna secuencia —
si ya se procesó antes (respondió, se descartó, rebotó...) y Apollo limpió
esa referencia al terminar, parecería "libre" otra vez. Sin esta comprobación,
un ayuntamiento ya cerrado podría reinscribirse solo y volver a recibir los
5 correos, sin fin.

Por el mismo motivo se copia también `municipio`: el nombre del negocio lo
genera el workflow con `{{ enrolled_object.municipio }}`, y la integración
nativa Apollo-HubSpot solo trae el `city` que calcula Apollo automáticamente
-nada fiable para pueblos pequeños-, no el campo personalizado "Municipio"
que se rellenó a mano y verificado contra el dominio de cada ayuntamiento.
Sin este paso, varios negocios saldrían con el nombre del pueblo mal o en
blanco aunque el correo llegue perfecto.

## Personalización de los correos

Los correos de OUTBOUND citan el municipio y la provincia (`{{municipio}}`,
`{{provincia}}`), no la empresa: el Account de Apollo no es fiable para todos
los contactos (varios comparten cuenta con otros municipios), así que se dejó
de usar `{{company_name}}`. `{{municipio}}` es el campo personalizado
"Municipio", verificado a mano contra el dominio de cada ayuntamiento —
también depende de él la copia a HubSpot descrita más abajo (para el nombre
del negocio). `{{provincia}}` es otro campo personalizado, cargado igual.
Ninguno de los dos depende del puente para el envío del correo en sí — solo
`{{productos_interes}}` etc. de INBOUND lo necesitan, porque esos datos no
existen en Apollo hasta que el puente los escribe.

Los 10 correos (5 de INBOUND + 5 de OUTBOUND) incluyen el enlace de reservas de
Amaia (`https://meetings-eu1.hubspot.com/amaia-rodriguez`, su página de
Meetings en HubSpot) como llamada a la acción, para que el ayuntamiento pueda
agendar directamente mirando su disponibilidad real, sin esperar a que
alguien conteste el correo. Es un enlace fijo en el HTML de cada plantilla,
no depende del puente — si Amaia cambia de página de reservas hay que
actualizar las 10 plantillas a mano en Apollo (o pedir que se haga vía MCP).

Los correos de INBOUND citan lo que el lead contó en el formulario web
(`{{productos_interes}}`, `{{unidades_estimadas}}`, `{{plazo_proyecto}}`).
Esto sí depende del puente: la integración nativa HubSpot↔Apollo no
sincroniza propiedades personalizadas, así que `enroll_inbound()` traduce
los valores internos de HubSpot (p. ej. `6_15`) a su etiqueta legible
(`6–15`) y los escribe en los campos personalizados de Apollo justo antes
de inscribir al contacto — de ahí que el paso de escritura vaya siempre
antes que `apollo_enroll` en esa función. Los IDs de esos campos están en
`CAMPOS_APOLLO_INBOUND`; si se borran o se renombran en Apollo (Settings →
Custom Fields → Contacts) hay que actualizar esa constante.

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
| Variable | `OUTBOUND_ENABLED` | `0` para desactivar solo OUTBOUND sin tocar INBOUND. Por defecto `1` |
| Variable | `OUTBOUND_DAILY_CAP` | opcional, por defecto `50` |
| Variable | `OUTBOUND_ENROLL_HOUR` | opcional, hora UTC de la inscripción diaria, por defecto `8` |

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
