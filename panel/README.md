# Panel de conversión — Mobiliario Urbano

`panel-mobiliario-urbano.html` es un panel que lee HubSpot **en directo** y
separa los resultados en cuatro vistas: INBOUND, OUTBOUND, las dos juntas y
**vs semana pasada**.

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

### Reuniones — el objetivo de la campaña

Es lo primero de cada pestaña, con la conversión a reunión como cifra
protagonista, y en el embudo la etapa «Reunión Agendada» va marcada
«objetivo».

| Métrica | Definición exacta |
|---|---|
| Negocios con reunión | Negocios del segmento con al menos una reunión de Amaia asociada. **Sale del calendario, no de la etapa**: un negocio que se sentó y acabó descartado sigue contando, que es lo que mide el esfuerzo comercial |
| Conversión a reunión | Negocios con reunión ÷ negocios creados |

### Embudo

| Métrica | Definición exacta |
|---|---|
| Canal de entrada (solo inbound) | Por dónde llegó cada lead, de `hs_analytics_source` + `hs_analytics_source_data_1`. **No se usa `canal_origen`** — ver abajo |
| Lead a lead (solo inbound) | La misma fuente, pero sin agregar: una fila por persona que envió el formulario, con su origen, qué pidió y la primera página que vio. El nombre enlaza a su ficha de HubSpot. Va encima de los resultados económicos. Quien rechaza las cookies de seguimiento entra sin fuente y sale como «Sin fuente», contado aparte en la nota en vez de repartido a ojo |
| Productos de interés (solo inbound) | Leads que marcaron cada opción de `productos_interes`. Es una casilla múltiple, así que un lead cuenta en todos los que pidió y la suma pasa del total de leads a propósito: lo que compara la barra es producto contra producto. El más pedido va en Formentera para que la respuesta se lea sin contar cifras. Una opción nueva del formulario aparece con su valor interno en vez de desaparecer del recuento |
| Negocios por etapa | `dealstage` de los negocios del pipeline `4080461018`, en columnas tipo kanban: una por etapa, en el orden del pipeline, con el porcentaje sobre el total del segmento |
| Motivos de pérdida | `motivo_perdida` de los negocios en «Descartado» |

El total de formularios completados y de ayuntamientos contactados ya no tiene
tarjeta propia: sale en la nota del gráfico de productos, en la fila «Entradas
al embudo» de la comparativa y en las dos primeras filas de la tabla semanal.

### vs semana pasada

**Cinco cifras y nada más** (simplificada el 11/09/2026): la conversión a
reunión de protagonista, y al lado se sentaron, negocios nuevos, ganados e
ingresos. Cada una con su cambio contra la semana anterior.

Cuatro son **hechos con fecha dentro de la ventana**, exactos. La quinta, la
**conversión a reunión**, se mide **acumulada a la fecha de corte** de cada
ventana —igual que en las demás pestañas—, y lo que se compara son dos fotos.
Medirla dentro de la ventana (lo conseguido esta semana ÷ lo creado esta
semana) mezclaría cohortes y llegaba a dar **150 %**: las reuniones de esta
semana son de negocios entrados hace meses. Lo dice la nota de la pestaña.

Se retiraron el embudo semanal por etapa, la tabla de diez métricas y el
bloque económico. Están en el historial de git si vuelven a hacer falta.

### Resultados económicos

Van **al final de cada pestaña**, a propósito: la campaña se mide por
reuniones cerradas, y el dinero es la consecuencia.

| Métrica | Definición exacta |
|---|---|
| Conversión a ganado | «Información enviada» → «Ganado», sobre todos los negocios del segmento |
| Pipeline abierto | Suma de `amount_in_home_currency` de los negocios que no están en «Ganado» ni «Descartado» |
| Ingresos ganados | Suma de importes de los negocios en «Ganado» con `closedate` dentro del periodo |

## Instagram, LinkedIn o web: de dónde sale ese dato

Hay **dos vías** en el portal que dicen por dónde entró un lead, y no dicen lo
mismo. El panel usa la primera:

**1. `hs_analytics_source` + `hs_analytics_source_data_1` — la que se usa.**
Es el seguimiento propio de HubSpot, que lee el referente del navegador. La
fuente sola no distingue redes —Instagram y LinkedIn caen las dos en
«Organic Social»—; el nombre está en el detalle. Verificado contra el portal
el 11/09/2026: `instagram` 144 contactos, `linkedin` 56, `facebook` 10, más
`PAID_SOCIAL` con su propio reparto. Funciona **aunque el enlace no lleve
UTM**, porque no depende de la URL.

**2. `canal_origen` — la que NO se usa.** Es el campo oculto del formulario,
y su función en la página hace bien su trabajo:

```js
var src = (p.get("utm_source") || "").toLowerCase();
if (src === "instagram") return "instagram";
if (src === "linkedin")  return "linkedin";
if (src === "email")     return "email_ayuntamientos";
return "web_directo";
```

El problema es *cuándo* lo lee: en el momento de enviar, de la URL que haya
entonces. Si el visitante llega con la UTM, navega a otra página y vuelve, o
si el enlace de la publicación no lleva UTM, cae en `web_directo`. Por eso los
tres leads que hay hoy dicen `web_directo` aunque dos vinieran de sitios
distintos.

Sigue siendo útil como **intención declarada de campaña** —dice desde qué
enlace etiquetado se envió—, pero no como reparto de canales. Si se quisiera
fiable, habría que guardar el `utm_source` en `sessionStorage` la primera vez
que se ve y leerlo de ahí al enviar; es un cambio en la página web, no en el
panel.

## Las tres decisiones que había que tomar

**1. Un contacto que está en Apollo y además rellena el formulario cuenta como
INBOUND** (último toque). El negocio es inbound si alguno de sus contactos
asociados tiene `productos_interes` relleno o su `inbound__outbound` empieza
por `INBOUND`; si no, es outbound si tiene `campana_apollo` o su
`inbound__outbound` empieza por `OUTBOUND`.

**2. De reuniones solo se cuentan las agendadas, y solo en la pestaña
semanal.** «Realizadas», «propuestas
enviadas» y «negocios con reunión» se retiraron del panel el 04/09/2026: las
tres eran deducidas, no leídas. «Realizadas» tenía que inferirse de la hora de
fin porque `hs_meeting_outcome` está vacío en las 176 reuniones de Amaia
—incluidas las de 2023: no lo rellena la sincronización de calendario, es un
campo manual—, y las otras dos dependían de unas fechas de entrada por etapa
que HubSpot aún no ha creado. Lo que queda es lo que se lee directamente.
El recuento de negocios en las etapas «Propuesta enviada» y «Reunión
Agendada» sigue en el embudo, que ese sí es exacto.

**3. El periodo por defecto es «desde el inicio»**, con selector de 90 / 30 /
7 días. Filtra por `createdate` del negocio, salvo los ingresos ganados, que
filtran por `closedate` porque es cuando entra el dinero.

## Las etapas no están clavadas en el código

El panel expone **las etapas del pipeline, no una copia suya**. La pertenencia
y el orden salen de `hubspot/spec/pipeline-mobiliario-urbano.json`, porque el
conector no expone a qué pipeline pertenece cada etapa; todo lo demás lo manda
HubSpot:

- **La etiqueta** se lee en vivo de `get_properties` sobre `dealstage`. Si
  alguien renombra una etapa en el portal, el panel cambia solo.
- **La probabilidad** se toma del primer negocio que haya en esa etapa
  (`hs_deal_stage_probability`, que la calcula HubSpot). Las de la spec son
  solo el valor de partida mientras no haya negocios.
- **Una etapa que desaparezca** del portal se marca «ya no está en el
  pipeline» en vez de seguir mostrándose como si nada.
- **Una etapa que se añada** se descubre en cuanto un negocio la usa, y sale
  marcada «etapa nueva». No se le atribuyen etapas alcanzadas ni tiempos de
  tránsito, porque su posición en el embudo no se puede deducir: para eso hay
  que añadirla a la spec.

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

> Verificado contra el portal el 04/09/2026. `hubspot/spec/pipeline-mobiliario-urbano.json`
> ya refleja estos nombres e ids; antes describía siete etapas que nunca se
> crearon con esos nombres. Las **probabilidades no se han podido verificar**:
> el conector no expone la metadata del pipeline. El valor ponderado no
> depende de ellas —usa `hs_projected_amount_in_home_currency`, que lo calcula
> HubSpot—, pero conviene confirmarlas en Settings → Objects → Deals →
> Pipelines.

## Qué se quitó y por qué (11/09/2026)

Sobraba información y costaba encontrar lo que importa.

| Quitado | Motivo |
|---|---|
| «Reuniones agendadas» | Contaba citas, no negocios; la conversión usa negocios, así que invitaba a comparar dos cosas distintas |
| «Aún sin reunión» | Es el total menos los que se sentaron, y el faro ya dice «5 de 10» en su pie |
| Tiempo medio en cada etapa | Pedido |
| Ponderado por probabilidad | Pedido |
| Probabilidad de etapa en el kanban | No se pidió, pero se quedaba sin sentido: solo alimentaba el ponderado. Sin él eran dos porcentajes juntos y sin etiqueta |
| Embudo semanal, tabla de diez métricas y bloque económico semanal | La pestaña baja a cinco cifras |

No es solo ocultar: se borró el cálculo que ya no pinta nadie. Y con
«Reuniones agendadas» se cae **una consulta entera a HubSpot** por refresco,
porque el recuento del calendario solo alimentaba esa tarjeta. Quedan **7
consultas donde había 10**.

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
- **Etapas añadidas después.** Una etapa nueva se detecta y se muestra, pero
  no entra en el cálculo de etapas alcanzadas ni de tiempos: su sitio en el
  embudo hay que declararlo en la spec.
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

Sigue la skill `gravity-wave-marca` al pie:

- **Un solo mundo visual, el de la marca.** El fondo es `#01313D` siempre, no
  el tema del sistema: la guía lo fija como fondo de las piezas digitales. El
  panel declara `color-scheme: dark` para que el desplegable, el foco y las
  barras nativas se pinten en oscuro en vez de tomarlos prestados del
  anfitrión. Si alguien lo prefiere claro, se recupera el tema doble.
- **Regla de oro**: antetítulo diminuto y espaciado (Medium, `.3em`) sobre
  titular macizo en caja alta (Black, `-.02em`). Vale para la cabecera y para
  cada sección.
- **Cifras**: número enorme en Black arriba, etiqueta debajo en blanco a
  cuerpo pequeño, nota al pie en gris. La cifra en Formentera es **solo la
  principal de cada fila**; el resto en blanco, porque el turquesa satura.
- **Sin rojo, ámbar ni verde.** La rampa del embudo va de Deep Blue
  `#1E6778` a Formentera `#00ADB5`, y lo perdido se apaga a gris azulado en
  vez de encenderse. En la pestaña semanal el signo también: mejora en
  Formentera, empeora en gris.
- **Cera Pro real** (Black 900 / Medium 500 / Regular 400), incrustada en
  base64 desde `assets/fonts/`. Poppins como red de seguridad.
- **Firma** `PLASTIC FREE OCEANS` apilada en tres líneas, Black, en la
  esquina inferior izquierda. Radios de 0–2 px.

**No lleva el logotipo**: este repositorio no trae `assets/logos/`, y el
wordmark no se redibuja nunca. Sigue en su lugar la regla de composición de la
marca —antetítulo diminuto y espaciado sobre titular macizo—, que según la
propia guía basta para que la pieza sea Gravity Wave. Si se añaden los SVG al
repo, se puede incrustar el logo simple en blanco.
