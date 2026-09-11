# Medición — landing de mobiliario urbano

Cómo se mide `https://www.thegravitywave.com/mobiliario-urbano/` y cómo se
piden informes de GA4 para este embudo.

El puente con HubSpot y el pipeline están en `../hubspot/README.md` y
`../bridge/README.md`. Aquí solo está la parte de analítica.

## Identificadores

| Pieza | Valor |
|---|---|
| Cuenta GA4 | The gravity wave |
| Propiedad | The gravity wave - GA4 · `374842401` |
| Flujo de datos | `https://www.thegravitywave.com` |
| ID de medición | `G-7LN8GNKJM8` |
| Contenedor de GTM | `GTM-M6FNQ79` |
| Proyecto de Google Cloud (MCP) | `thegravitywave-ga4-mcp` |
| Retención de datos | 14 meses (eventos y usuarios) — verificado 10/09/2026 |
| Consentimiento | Consent Mode v2, plugin GDPR de Moove |

Verificado el 10/09/2026: la etiqueta `G-7LN8GNKJM8` pertenece a la propiedad
`374842401`. Era el primer punto a descartar — si fueran propiedades distintas,
todos los informes saldrían a cero sin que nada estuviera roto.

## El evento `generate_lead`

Es la única conversión que mide esta landing.

**Cuándo dispara**: solo cuando la Forms API de HubSpot ha respondido 2xx al
envío del formulario. Ni antes, ni en la rama de `mailtoFallback()`, ni en los
errores. El código exacto y el porqué de esa colocación están en
`generate-lead.js`.

**Qué lleva**:

| Parámetro | Origen | Valores |
|---|---|---|
| `canal_origen` | `canalOrigen()` de la página, a partir de las UTM | `email_ayuntamientos` · `instagram` · `linkedin` · `web_directo` · `otro` |
| `landing_variant` | Cookie `gw_landing_variant` | La variante A/B servida, o `sin_variante` |
| `tipo_entidad` | Campo `f-entidad` del formulario | `ayuntamiento` · el resto del enumerado de la spec |

**Qué no lleva, y no debe llevar nunca**: nombre, apellidos, email, teléfono
ni el campo de mensaje libre. Ese mensaje suele traer el municipio y a veces
el nombre de una persona; mandarlo a GA4 sería meter datos personales en una
herramienta que no es el CRM.

## Configuración en GTM

1. Tres **variables de capa de datos**: `canal_origen`, `landing_variant`,
   `tipo_entidad`.
2. Un **activador** de tipo evento personalizado, nombre `generate_lead`.
3. Una **etiqueta de evento de GA4**: ID de medición `G-7LN8GNKJM8`, nombre de
   evento `generate_lead`, y los tres parámetros mapeados a sus variables.
4. En esa etiqueta, **comprobación adicional de consentimiento por
   `analytics_storage`**, para que respete el plugin de Moove.
5. Modo Vista previa → un envío de prueba → comprobar que la etiqueta dispara
   y que el evento aparece en Tiempo real de GA4 → publicar el contenedor.

## Configuración en GA4

- **Definiciones personalizadas**: dar de alta `canal_origen`,
  `landing_variant` y `tipo_entidad` como dimensiones personalizadas de
  **ámbito Evento**. Sin esto los parámetros se recogen pero no aparecen en
  ningún informe, que es la forma más habitual de creer que la medición falla
  cuando funciona.
- **Eventos** → marcar `generate_lead` como **evento clave**. No es
  retroactivo: cuenta desde el día que se marca.
- **Filtros de datos** → filtro de **tráfico interno** por IP de oficina. Con
  el volumen actual, cada visita del equipo mueve los porcentajes varios
  puntos.

## De dónde viene cada lead: la campaña se guarda al entrar

`canal_origen` leía `location.search` **en el momento de enviar**. Quien
llegaba desde Instagram, miraba el catálogo, volvía al formulario y enviaba
ya no tenía la UTM en la URL: contaba como `web_directo`. Lo mismo si el
enlace de la publicación no la llevaba.

Ahora la campaña se captura **en cuanto se ve** y se lee de ahí al enviar.
Dos claves de `sessionStorage`, `gw_utm_source` y `gw_utm_campaign`, escritas
una sola vez por sesión. Código en `generate-lead.js`.

**Manda la primera campaña de la sesión.** Si alguien llega por Instagram y
más tarde vuelve desde LinkedIn, cuenta como Instagram: fue lo que lo trajo.
Para que mande la última, se quita la condición `if (!sessionStorage.getItem(...))`
de `guardaCampana()`.

**`sessionStorage` y no `localStorage`**: una visita de mañana desde otro
sitio es otra captación y debe contar como tal.

**No añade ninguna categoría de dato nueva**: es la misma UTM que el
formulario ya manda a HubSpot en `canal_origen`, guardada unos minutos en el
navegador de quien navega. Nada que no estuviera viajando ya.

**Degrada sin romper.** Todo acceso a `sessionStorage` va en `try/catch`: en
modo privado, con cookies bloqueadas o dentro de un iframe, leer o escribir
lanza excepción, y esto corre en la ruta del formulario — una excepción ahí
costaría un lead. Si no hay persistencia, se lee la URL y se comporta como
antes: ni mejor ni peor.

Comprobado en navegador, los ocho casos:

| Recorrido | `canal_origen` |
|---|---|
| Instagram → vuelve sin UTM | `instagram` |
| LinkedIn → dos páginas sin UTM | `linkedin` |
| Entra directo, sin UTM nunca | `web_directo` |
| `utm_source=email` + campaña `…ayuntamientos…` | `email_ayuntamientos` |
| `utm_source=email` + campaña `…inbound…` | `otro` |
| Instagram y **después** LinkedIn | `instagram` (primera) |
| `sessionStorage` bloqueado, UTM en la URL | `instagram` |
| `sessionStorage` bloqueado, sin UTM | `web_directo` |

## Esquema UTM

| Canal | `utm_source` | `utm_medium` | `utm_campaign` |
|---|---|---|---|
| Campaña ayuntamientos (OUTBOUND) | `email` | `email` | `mobiliario-ayuntamientos-2026` |
| Instagram | `instagram` | `social` | `mobiliario-2026` |
| LinkedIn | `linkedin` | `social` | `mobiliario-2026` |

Los enlaces a la landing de los 5 pasos de la secuencia OUTBOUND de Apollo
(`6a9844f7d0bf520010f72cc1`) tienen que llevar esas tres UTM **antes** de que
la secuencia se encienda. Si se enciende sin ellas, el tráfico entra como
directo y no hay forma de recuperar la atribución después.

La secuencia INBOUND (`6a9844b94208650014fc4754`) va **sin UTM** a propósito:
se envía a gente que ya convirtió, no aporta atribución de captación y sí
podría ensuciar `canal_origen`. Si algún día se quiere medir, con la
`canalOrigen()` corregida ya es seguro usar
`utm_source=email&utm_campaign=mobiliario-inbound-2026`.

## Cómo pedir un informe de GA4

El MCP oficial de Google Analytics (`analytics-mcp` 0.7.0, permiso
`analytics.readonly`) corre **en el entorno local de Codex**, no en Claude Code
web. Las credenciales no salen de esa máquina y no se piden ni se guardan aquí.

Para pedir un informe hay que dar los cuatro datos, o la consulta no es
ejecutable: **periodo · dimensiones · métricas · filtro**. Ejemplo:

> Periodo: últimos 30 días · Dimensiones: `sessionSourceMedium`,
> `sessionCampaignName` · Métricas: `sessions`, `engagedSessions`,
> `engagementRate` · Filtro: `landingPagePlusQueryString` contiene
> `mobiliario-urbano`

El resultado vuelve en Markdown o CSV y se incorpora aquí.

## Línea base — 10/09/2026

Primera medición completa, con la landing ya publicada y el evento de
conversión **todavía sin instrumentar**.

| Dato | Valor |
|---|---|
| Sesiones (30 días) | 15 |
| Usuarios | 7 |
| `page_view` · `session_start` · `first_visit` | 30 · 15 · 5 |
| `generate_lead` | 0 — el evento no existía en la página |
| Sesiones los 30 días anteriores | 0 |
| Primera actividad registrada | 28/08/2026 |
| Fuentes | `google / organic` 10 (40 % engagement) · directo 5 (80 %) |
| Dispositivo | Escritorio 11 · Móvil 4 |
| País | España 14 · Argentina 1 |
| Sesiones con `utm_source=email` | 0 |

**Leads reales en esa ventana: ninguno.** Contrastado contra HubSpot el
11/09/2026: los únicos contactos del formulario son de prueba («Prueba AB»,
«Luis Hurtado», «Test Mobiliario»). Los cuatro contactos con
`canal_origen = email_ayuntamientos` no pasaron por la landing: se importaron
con el canal puesto a mano y no tienen `apollo_estado`.

Las cero sesiones de email **no son un fallo de las UTM**: las dos secuencias
de Apollo están inactivas y no se ha enviado ningún correo todavía.

Con 15 sesiones, buena parte del propio equipo, **ninguna comparación de
fuentes, variantes o engagement de esta tabla es concluyente**. Sirve como
punto de partida, no como diagnóstico.

## Limitaciones conocidas

- **`canal_origen` no es un campo de atribución web.** Lo rellena la landing
  desde las UTM, pero también se pone a mano en las importaciones del
  outbound. Para cruzar GA4 con el pipeline hay que filtrar por contactos
  creados por el formulario, no por `canal_origen` a secas. Verificado el
  11/09/2026: los 4 contactos con `canal_origen = email_ayuntamientos` tienen
  `hs_analytics_source = OFFLINE`, o sea que nunca pasaron por la landing.
- **`canal_origen` solo ve enlaces etiquetados; el panel no depende de él.**
  Aun con la captura persistente, si el enlace no lleva UTM no hay campaña que
  guardar. El reparto por canal del panel sale de `hs_analytics_source` +
  `hs_analytics_source_data_1`, que lee el referente del navegador y funciona
  sin UTM: ahí es donde se ve Instagram frente a LinkedIn. `canal_origen`
  responde a otra pregunta — desde qué enlace etiquetado se envió.
- **El fuente de la landing está desincronizado.** La página dice «Generado
  por web/build.py: no editar el dist a mano», pero ninguna rama con `web/src`
  contiene `gwLandingVariant`: el script de la prueba A/B se pegó directo en
  WordPress. Si alguien regenera desde `web/src` y republica, la prueba A/B
  desaparece — y con ella lo de este directorio. Hay que decidir cuál de los
  dos es el fuente antes de seguir tocando la página.
- **El Consent Mode descarta lo que no se acepta.** Es correcto legalmente,
  pero GA4 medirá menos sesiones de las que hay y no cuadrará con HubSpot. A
  este volumen no se alcanzan los umbrales de modelado de Google, así que esas
  visitas se pierden sin estimación.
- **La prueba A/B de `landing_variant` no va a concluir.** Distinguir dos
  variantes exige cientos de conversiones. Con 15 sesiones al mes no hay
  horizonte razonable.
- **No hay circuito cerrado hasta el negocio.** GA4 sabe de qué fuente viene
  la sesión; HubSpot sabe si el negocio se gana. Nada une las dos cosas por
  contacto. Se resolvería mandando el `client_id` de GA4 a un campo oculto del
  formulario, pero exige propiedad nueva en HubSpot y tocar la spec: no
  compensa hasta que haya volumen.
