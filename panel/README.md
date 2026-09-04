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

### Embudo

| Métrica | Definición exacta |
|---|---|
| Productos de interés (solo inbound) | Leads que marcaron cada opción de `productos_interes`. Es una casilla múltiple, así que un lead cuenta en todos los que pidió y la suma pasa del total de leads a propósito: lo que compara la barra es producto contra producto. El más pedido va en Formentera para que la respuesta se lea sin contar cifras. Una opción nueva del formulario aparece con su valor interno en vez de desaparecer del recuento |
| Negocios por etapa | `dealstage` de los negocios del pipeline `4080461018` |
| Tiempo medio por etapa | De entrar en una etapa a entrar en la siguiente por la que pasó el negocio |
| Motivos de pérdida | `motivo_perdida` de los negocios en «Descartado» |

El total de formularios completados y de ayuntamientos contactados ya no tiene
tarjeta propia: sale en la nota del gráfico de productos, en la fila «Entradas
al embudo» de la comparativa y en las dos primeras filas de la tabla semanal.

### vs semana pasada

Compara los últimos 7 días con los 7 anteriores. Solo cuenta **hechos con
fecha dentro de la ventana** —negocios creados, etapas alcanzadas, cierres,
reuniones—, nunca fotos del embudo: HubSpot no guarda cómo estaba el pipeline
el lunes pasado, así que un «pipeline abierto la semana pasada» sería
inventado. Por eso esa pestaña no repite el valor del pipeline ni la conversión
acumulada.

| Fila | Qué cuenta |
|---|---|
| Formularios completados · Ayuntamientos contactados | Contactos creados dentro de la ventana |
| Respuestas al outbound | `apollo_fecha_respuesta` dentro de la ventana |
| Negocios creados | `createdate` dentro de la ventana |
| Negocios que cambiaron de etapa | `hs_v2_date_entered_current_stage` dentro de la ventana |
| Reuniones agendadas | Reuniones de Amaia (`681386458`) atadas a un negocio de este pipeline, con inicio dentro de la ventana. Sin repartir por origen. Es el único sitio del panel donde salen |
| Ganados · Descartados · Ingresos | `closedate` dentro de la ventana; si falta, la fecha de entrada en la etapa |

El signo se colorea por si **mejora o empeora**, no por si sube o baja: más
descartados sale en gris, no en verde. Sin rojos ni ámbares, que la marca no
admite.

Mientras HubSpot no cree las fechas de entrada por etapa, la tabla «Entradas en
cada etapa» solo puede fechar la etapa **actual** de cada negocio: uno que pasó
por dos etapas en la misma semana cuenta solo en la última. El panel lo dice en
la propia tabla y deja de decirlo en cuanto las fechas existen.

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
