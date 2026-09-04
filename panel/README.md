# Panel de conversión — Mobiliario Urbano

`panel-mobiliario-urbano.html` es un panel que lee HubSpot **en directo** y
separa los resultados en tres vistas: INBOUND, OUTBOUND y las dos juntas.

Publicado como artefacto privado:
<https://claude.ai/code/artifact/df4aa04d-90b5-4b4a-9340-9ac488a1b5d0>

## Cómo se actualiza

No hay exportaciones, ni fichero intermedio, ni token guardado en ninguna
parte. La página consulta HubSpot con **las credenciales del conector de quien
la abre**, mediante `claude.use("mcp")`. Cada persona del equipo entra con la
misma URL desde su ordenador y ve el CRM con sus propios permisos.

Cada consulta es un `watchTool`: se refresca sola cada 60 s (150 s las
reuniones), se pausa cuando la pestaña deja de estar visible y vuelve a
consultar al recuperarla. El sello de «Actualizado a las …» sale de
`result.cache.storedAt`, no del reloj del navegador.

Requisito por persona: tener HubSpot conectado en claude.ai → Ajustes →
Conectores. Si falta, el panel lo dice y explica cómo arreglarlo; cada código
de error tiene su propio mensaje, porque la solución es distinta en cada caso.

## De dónde sale cada métrica

Solo se usan dos herramientas del conector, y cada una para lo que sabe hacer:

| Herramienta | Para qué | Por qué esa |
|---|---|---|
| `search_crm_objects` | Negocios del pipeline, contactos de formulario, contactos de Apollo | Devuelve JSON limpio, `total` para paginar, y **omite sin fallar las propiedades que no existen** |
| `query_crm_data` | Origen de cada negocio y reuniones del pipeline | Es la única que cruza objetos (`CONTACT.…` desde `DEAL`, `DEAL.pipeline` desde `MEETING`) |

### Captación

| Métrica | Definición exacta |
|---|---|
| Formularios completados | Contactos con `productos_interes` relleno. Esa propiedad solo la escribe el formulario de `/mobiliario-urbano/`, así que equivale a una conversión. Un contacto cuenta una vez aunque lo rellene dos veces |
| Ayuntamientos contactados | Contactos con `campana_apollo = mobiliario_urbano`, que es lo que estampa el puente al inscribir en la secuencia de Apollo |
| Han respondido (outbound) | De los anteriores, `apollo_estado` en `respondido` o `reunion_agendada` |
| Negocios por etapa | `dealstage` de los negocios del pipeline `4080461018` |
| Conversión a ganado | Negocios en «Ganado» ÷ negocios del segmento |
| Propuestas enviadas | Negocios que **llegaron alguna vez** a «Propuesta enviada», no los que están ahí ahora |
| Reuniones agendadas / realizadas | Reuniones cuyo propietario es Amaia (`681386458`) **y** que están atadas a un negocio de este pipeline. Realizada = su hora de fin ya pasó y no está cancelada |
| Negocios con reunión | Negocios que llegaron a la etapa «Reunión agendada» |
| Tiempo medio por etapa | De entrar en una etapa a entrar en la siguiente por la que pasó el negocio |
| Motivos de pérdida | `motivo_perdida` de los negocios en «Descartado» |

### Resultados

| Métrica | Definición exacta |
|---|---|
| Conversión global | «Información enviada» → «Ganado», sobre todos los negocios del segmento |
| Pipeline abierto | Suma de `amount_in_home_currency` de los negocios que no están en «Ganado» ni «Descartado» |
| Ponderado | Suma de `hs_projected_amount_in_home_currency`, que HubSpot calcula como importe × probabilidad de la etapa. Si falta, se calcula con la probabilidad de la tabla de etapas |
| Ingresos ganados | Suma de importes de los negocios en «Ganado» con `closedate` dentro del periodo |

## Las tres decisiones que había que tomar

**1. Un contacto que está en Apollo y además rellena el formulario cuenta como
INBOUND** (último toque). El negocio es inbound si alguno de sus contactos
asociados tiene `productos_interes` relleno o su `inbound__outbound` empieza
por `INBOUND`; si no, es outbound si tiene `campana_apollo` o su
`inbound__outbound` empieza por `OUTBOUND`.

**2. «Reunión realizada» se cuenta por fecha pasada**, no por el campo de
resultado. `hs_meeting_outcome` está vacío en las 176 reuniones de Amaia,
incluidas las de 2023: no lo rellena la sincronización de calendario, es un
campo manual. Contar por fecha funciona desde el primer día; el precio es que
un *no-show* cuenta como celebrada. Si algún día se marcan los resultados, se
añade la cifra exacta al lado sin tocar nada más.

**3. El periodo por defecto es «desde el inicio»**, con selector de 90 / 30 /
7 días. Filtra por `createdate` del negocio, salvo los ingresos ganados, que
filtran por `closedate` porque es cuando entra el dinero.

## Etapas del pipeline `4080461018`

| # | Etapa | Id | Prob. |
|---|---|---|---|
| 1 | Información enviada | `5948376264` | 10 % |
| 2 | Muestra interés / Intención de compra | `5948376265` | 20 % |
| 3 | Propuesta enviada | `5948376266` | 35 % |
| 4 | Reunión Agendada | `5948376267` | 55 % |
| 5 | Negociación | `5948376268` | 75 % |
| 6 | Ganado | `5948376269` | 100 % |
| 7 | Descartado | `5948376270` | 0 % |

> Estos son los nombres **reales** del portal. La tabla de etapas de
> `hubspot/README.md` («Lead mobiliario», «Ajuste de propuesta», «Acuerdo
> firmado»…) es de una versión anterior de la spec y no coincide con lo que
> hay montado. El puente sí usa los ids correctos.

## Limitaciones conocidas

- **Las reuniones no se reparten por origen.** El cruce `DEAL.pipeline` desde
  `MEETING` acota al pipeline correcto, pero al pedir además el id del negocio
  vuelven dos columnas llamadas `hs_object_id` que solo se distinguen por su
  etiqueta en español. En vez de depender de eso, las reuniones se dan como
  cifra de campaña y el reparto por origen se ve en «Negocios con reunión»,
  que sale de las etapas y es exacto.
- **Tiempo por etapa, al principio.** Las propiedades
  `hs_v2_date_entered_<etapa>` de este pipeline **todavía no existen**: HubSpot
  las crea cuando el primer negocio pasa por cada etapa. `search_crm_objects`
  las ignora sin dar error, así que el panel se repara solo. Mientras tanto
  muestra lo que llevan parados los negocios abiertos en cada etapa, y lo dice.
- **Etapas alcanzadas, al principio.** Sin esas fechas, «llegó a la etapa X» se
  deduce de la posición actual. Es exacto salvo para los negocios en
  «Descartado», de los que no se sabe hasta dónde llegaron; por eso no se les
  atribuye ninguna etapa intermedia hasta que existan las fechas.
- **Tope de carga:** 600 negocios y 400 contactos por lista. Si se superan, el
  pie del panel lo avisa; se sube cambiando `PAGINAS_DEAL` y `PAGINAS_CONTACTO`.
- **El parser del TSV** de `query_crm_data` interpreta `Etiqueta (valor)`
  tomando el último paréntesis. Solo se aplica a columnas de enumeración e id,
  nunca a texto libre, donde un topónimo como «Sant Joan (Alacant)» lo rompería.

## Estado del embudo (04/09/2026)

El pipeline tiene **0 negocios** y no hay ningún contacto con `campana_apollo`.
El panel funciona y sale a cero porque el circuito aún no está encendido:

1. La página `/mobiliario-urbano/` sigue con `HS_FORM_GUID = ""`.
2. Los seis workflows del embudo están desactivados.
3. El puente solo escribe con `BRIDGE_ENABLED = 1`.

## Marca

Paleta y tipografía de la skill `gravity-wave-marca`: fondo `#01313D` en tema
oscuro, blanco dominante en claro, Formentera `#00ADB5` como acento medido, y
Cera Pro real (Black / Medium / Regular) incrustada en base64 desde
`assets/fonts/`. Sin rojos ni ámbares: un negocio perdido se apaga a gris
azulado en vez de encenderse en rojo.

**No lleva el logotipo**: este repositorio no trae `assets/logos/`, y el
wordmark no se redibuja nunca. Sigue en su lugar la regla de composición de la
marca —antetítulo diminuto y espaciado sobre titular macizo—, que según la
propia guía basta para que la pieza sea Gravity Wave. Si se añaden los SVG al
repo, se puede incrustar el logo simple en blanco.
