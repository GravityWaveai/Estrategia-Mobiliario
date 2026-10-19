# Panel de la campaña

`plantilla.html` es el panel de seguimiento de la campaña de Mobiliario
Urbano: secuencia de Apollo, aperturas, respuestas, rebotes, salud del
dominio, inbound de la web (visitas a la landing, clics del banner de la
home, leads del formulario), negocios en HubSpot y la lista completa de
ayuntamientos con su estado.

No pide datos a nadie. La fase **PANEL** del puente
(`bridge/apollo_hubspot_bridge.py`, cada media hora) los junta con sus
llaves, los mete en el hueco

```js
const D = /*DATOS*/null;
```

y publica la página resultante (ver `bridge/README.md`, «PANEL»). Una copia
de la plantilla sin rellenar lo dice arriba en un aviso y no pinta nada.

Por qué así: la versión anterior pedía los datos desde el navegador, con los
conectores del visor de claude.ai y peticiones directas al receptor. En el
visor del equipo salía vacía (`not_granted`, peticiones bloqueadas). Con el
dato dentro, la página se ve igual en claude.ai, en el receptor
(`…/exec?ver=1&key=…`) o guardada en el escritorio.

## Dónde se ve

- **claude.ai**: la página se republica varias veces al día en el mismo
  enlace a partir del artefacto cifrado de la pasada o del receptor. Lleva la
  tipografía Cera Pro como archivos `fonts/` junto a la página.
- **Receptor**: `…/exec?ver=1&key=CLAVE`, siempre la última pasada. Sin la
  tipografía (usa la del sistema), todo lo demás igual.

## Qué lleva `D`

| Clave | Qué es |
|---|---|
| `generado` | Fecha UTC de la pasada que generó la página |
| `relanzamiento` | `2026-10-14`, la fecha desde la que se cuenta la cadencia actual |
| `visitas_desde` | Desde cuándo mide visitas el receptor (16/10) o `null` si no respondió |
| `apollo` | `active`, `status_reason`, `max_emails_per_day`, `contact_statuses` (active, paused, finished, bounced, not_sent), `unique_replied`, `unique_bounced`, `unique_spam_blocked`, `steps[]` (position, wait_time, delivered, bounced, replied), `pixel_ok` (las cinco plantillas llevan el píxel), `no_enviados[]` (municipio, quien, motivo) |
| `lista.total` | Ayuntamientos en la lista OUTBOUND de Apollo |
| `aperturas[]` | `fecha`, `contacto` (id Apollo), `email`, `municipio`, `paso`; solo contactos de la lista, últimos 45 días |
| `visitas[]` | `fecha`, `utm_source`, `utm_medium`, `utm_campaign`, `referente`; solo la landing, sin pruebas, sin la vista previa de Tag Manager, un origen cada 90 s |
| `hubspot.contactos[]` | `id`, `mun`, `who`, `email`, `estado` (apollo_estado), `insc`, `resp` |
| `hubspot.negocios[]` | `id`, `nombre`, `etapa` (id de etapa del pipeline), `creado` |
| `hubspot.leads[]` | Leads del formulario web desde el 15/09: `id`, `email`, `nombre`, `productos`, `fecha` |
| `inbound` | Secuencia INBOUND: `en_cadencia`, `terminados`, `respondieron`, `entregados`, `spam` |
| `dns` | `consultado`, y los TXT `spf`, `dmarc`, `dkim` (`null` si no existen) |

Lo que calcula la página a partir de eso: enviados = entregados + rebotados
de cada paso; abiertos = contactos distintos con alguna apertura;
pendientes = lista menos los que ya están en la secuencia; clics del banner =
visitas con `utm_source=home&utm_medium=banner`; salud del dominio = 25 SPF
+ 25 DKIM propio (10 si firma Google) + 20 DMARC (10 si `pct<100`) + 20
rebotes <2 % (10 si <4 %) + 10 sin spam. Los rebotes de la salud son los
**posteriores al relanzamiento** (seguimientos del correo 2 en adelante más
los inscritos desde el 14/10): los de septiembre venían de la lista sin
verificar y se enseñan aparte, como acumulado.

## Cambiar la plantilla

Es un solo archivo, sin dependencias. Se edita, se comprueba la sintaxis del
script (`node --check` sobre el bloque `<script>` o abriéndola en el
navegador: sin datos enseña el aviso y nada más) y en la siguiente pasada
del puente sale ya rellena. El hueco `/*DATOS*/null` tiene que seguir ahí
tal cual; si no, la fase PANEL se para y lo dice.
