# Aprovisionamiento de HubSpot — Estrategia Mobiliario Urbano

Especificación técnica y script de creación de la estructura del embudo
«Mobiliario Urbano» en el portal HubSpot **26243090** (Gravity Wave).

Documento operativo de referencia: artifact **«Embudo Mobiliario Urbano»**
(26/08/2026). Este directorio es la versión ejecutable de su sección
«La columna vertebral en HubSpot».

## Qué crea

| Pieza | Detalle | Spec |
|---|---|---|
| Pipeline de negocios «Mobiliario Urbano» | 7 etapas con probabilidades 10/20/35/55/75/100/0 % | `spec/pipeline-mobiliario-urbano.json` |
| 5 propiedades de contacto | `tipo_entidad`, `municipio`, `productos_interes`, `canal_origen`, `plazo_proyecto` | `spec/contact-properties.json` |
| 5 propiedades de negocio | `estado_agente`, `url_propuesta`, `url_mockup`, `motivo_perdida`, `fecha_reactivacion` | `spec/deal-properties.json` |
| Grupo de propiedades «Mobiliario Urbano» | En contactos y en negocios, para que las diez queden agrupadas | (implícito en las specs) |

## Estado de la integración (auditoría 01/09/2026)

| Comprobación | Estado |
|---|---|
| 5 propiedades de contacto | ✓ Creadas en el portal, idénticas a la spec |
| 5 propiedades de negocio | ✓ Creadas |
| Pipeline «Mobiliario Urbano» | ✓ Creado (id `4080461018`) |
| Formulario de HubSpot | ✗ **No existe**: la página tiene `HS_FORM_GUID = ""` y cae al fallback de mailto — ningún lead se sincroniza aún |
| Propiedad `unidades_estimadas` | ✗ La página la envía pero no existía en la spec ni en el portal (añadida a la spec; la crea `provision-form.sh`) |
| Opción `parque_infantil` en `productos_interes` | ✗ La página la ofrece pero el enumerado no la tenía (añadida a la spec; la añade `provision-form.sh`) |
| `municipio` | La página no la pide como campo propio (va en el mensaje libre) |

Para cerrar la integración: ejecutar `provision-form.sh` (abajo) y pegar el
GUID resultante en la página.

## Formulario de la web

La página `/mobiliario-urbano/` envía directamente a la Forms API v3
(`api.hsforms.com/submissions/v3/integration/submit/26243090/<GUID>`), con
cookie `hubspotutk` y consentimiento GDPR incluidos. El formulario se crea con:

```bash
export HUBSPOT_PRIVATE_APP_TOKEN=pat-eu1-...   # necesita además el scope `forms`
./provision-form.sh
```

El script es idempotente, imprime el GUID y la línea exacta
(`var HS_FORM_GUID = "…";`) a pegar en la página. La definición del
formulario vive en `spec/form-mobiliario-urbano.json`.

## Cómo ejecutarlo

El conector de HubSpot de Claude puede leer y crear **registros**, pero no
pipelines ni propiedades; para eso hace falta la API con un token de app
privada:

```bash
export HUBSPOT_PRIVATE_APP_TOKEN=pat-eu1-...
./provision.sh
```

El script es idempotente: se puede relanzar sin duplicar nada.

Crear la app privada (requiere superadmin, ~2 min):
**Settings → Integrations → Private Apps → Create private app**, con scopes
`crm.objects.contacts.{read,write}`, `crm.objects.deals.{read,write}`,
`crm.schemas.contacts.{read,write}`, `crm.schemas.deals.{read,write}`.

### Alternativa manual

Si se prefiere no crear token, las tres specs de `spec/` contienen los
nombres internos, etiquetas, tipos y valores exactos para crearlo a mano en
**Settings → Properties** y **Settings → Objects → Deals → Pipelines**.

## Reglas del pipeline (configuración en UI, no cubierta por API)

1. **Importe obligatorio** desde «Propuesta en preparación»
   (Conditional stage properties de la etapa). Lo rellena el agente con los
   precios por volumen del configurador — nunca queda a 0 €.
2. **`motivo_perdida` obligatorio** al mover a «Descartado»; si el motivo es
   «ahora no», rellenar también `fecha_reactivacion`.
3. **No existe etapa «Frío»**: un negocio parado se pierde con motivo y fecha
   de reactivación, y la automatización 6 lo reabre ese día.

## Etapas — criterios y caducidad

| Etapa | Prob. | Entra cuando | Sale cuando | Máx. días |
|---|---|---|---|---|
| Lead mobiliario | 10 % | El formulario crea el negocio | El agente termina propuesta + mockups | 1 |
| Propuesta en preparación | 20 % | Agente trabajando · importe puesto | Amaia aprueba el envío | 2 |
| Propuesta entregada | 35 % | Email enviado con propuesta + agenda | Reunión reservada | 14 |
| Reunión agendada | 55 % | Hueco en el calendario de Amaia | Reunión celebrada | 10 |
| Ajuste de propuesta | 75 % | Reunión hecha · en negociación | Acuerdo o descarte | 21 |
| Acuerdo firmado (ganado) | 100 % | Pedido confirmado por escrito | — | — |
| Descartado (perdido) | 0 % | No hay proyecto · exige `motivo_perdida` | «ahora no» → `fecha_reactivacion` | — |

## Datos fijos del portal

| Dato | Valor |
|---|---|
| Portal | 26243090 |
| Propietaria de los negocios del pipeline | Amaia Rodriguez — `hubspot_owner_id` **681386458** |
| Pipelines existentes (no tocar) | Pipeline de ventas nuevas (`default`) · Puertos (`78112237`) · Asuntos Públicos (`310056942`) · Sea Hub (`186523326`) · Proyectos AD HOC (`1045301446`) |

Los nombres de etapa del pipeline nuevo no se repiten en ningún otro
pipeline del portal: los informes cruzados no mezclan cosas distintas.

## Después del aprovisionamiento (Paso 2 del plan)

Con la estructura creada, Claude:

1. Verifica pipeline y propiedades contra estas specs.
2. Mete un lead de prueba de punta a punta
   (formulario → contacto + negocio en «Lead mobiliario» → propuesta → tarea).
3. Deja programados los agentes 2, 5, 6 y 7 del documento operativo
   (generación de propuestas, seguimiento 5/12/14 días, reactivaciones,
   informe semanal del lunes 8:00).

## Esquema UTM de los canales

| Canal | `utm_source` | `utm_medium` | `utm_campaign` |
|---|---|---|---|
| Campaña ayuntamientos | `email` | `email` | `mobiliario-ayuntamientos-2026` |
| Instagram | `instagram` | `social` | `mobiliario-2026` |
| LinkedIn | `linkedin` | `social` | `mobiliario-2026` |

## Restricción de suscripción: sin Marketing Hub Pro (02/09/2026)

El portal 26243090 tiene **Sales Hub Professional** (asientos `core`,
`sales-pro`, `partner`, `view-only`) pero **no Marketing Hub Pro**. Eso
invalida la acción de workflow «Enviar correo de marketing»
(`actionTypeId 0-4`): la API la acepta al crearla, pero la UI la marca como
*«Las acciones de correo necesitan una suscripción a Marketing Hub Pro o
superior para usarse en Workflows»* y el workflow no la ejecutaría.

El único workflow del portal que usa `0-4` y sigue activo (`1410639086`,
«Enviar correo luego del envío de formularios») es un seguimiento heredado
de formulario, no una vía reutilizable para una cadencia de 5 correos.

### Solución adoptada — secuencias, sin cambiar de suscripción

Las **secuencias sí entran en Sales Hub Pro**, y tres workflows activos del
portal ya inscriben en secuencia (`2242763970`, `2349356246`, `2349356262`),
así que la acción `0-46510720` está disponible y probada aquí.

Los dos workflows de cadencia se han reconstruido sustituyendo la cadena
`0-4` + `0-1` (correo + espera) por una sola inscripción en secuencia:

| Workflow | Id | Pasos |
|---|---|---|
| MU · INBOUND — Lead web (secuencia) | `4839947487` | propietario → `inbound__outbound` → `lifecyclestage` → crear negocio → inscribir en secuencia `855582936` |
| MU · OUTBOUND — Ayuntamientos (secuencia) | `4840005827` | propietario → `inbound__outbound` → `lifecyclestage` → añadir a lista 2841 → crear negocio → inscribir en secuencia `855582933` |

Remitente de ambas: Amaia (`userId` 49211842,
`amaia@thegravitywave.com`), con `shouldUseContactTimeZone`.

Las cadencias de las secuencias coinciden con las que tenían los workflows:
INBOUND 0/3/4/5/6 días · OUTBOUND 0/5/5/6/7 días.

### Efectos secundarios de volver a secuencias

- **Se elimina el paso «marcar como contacto de marketing»** (`0-31`) de
  ambos workflows: las secuencias salen de la bandeja de Amaia y no
  consumen contactos de marketing. Desaparece el conflicto con el cupo de
  4.000 y con el reseteo mensual.
- La exclusión de la lista 2923 en el workflow de reseteo `939189697` deja
  de ser necesaria (protege contactos que ya no hace falta proteger). No se
  ha retirado: hay que quitarla a mano si se quiere recuperar ese cupo.
- La detección de respuesta sigue funcionando: `4839860441`
  («MU · Respuesta o reunión → Muestra interés») ya contempla
  `hs_latest_sales_email_reply_date`, que es la propiedad que rellenan las
  secuencias, además de las de reunión.
- Los 10 correos de marketing creados quedan sin uso. El copy aprobado está
  en el artifact «Copys Mobiliario Urbano» y hay que **pegarlo a mano en los
  pasos de las dos secuencias**: la Sequences API es de solo lectura
  (`PUT`/`PATCH`/`POST` devuelven 405).

## Ejecución de correo en Apollo (02/09/2026)

Con la acción `0-46510720` («Inscribir en secuencia») también bloqueada en la UI
por suscripción, la ejecución de correo se traslada a Apollo. HubSpot se queda
como CRM y pipeline.

**Por qué Apollo y no otra vía**: HubSpot no expone escritura de secuencias
(`POST /automation/v4/sequences` → 405; `/automation/v3/sequences` → 404;
`/sequences/v2/` → 401, endpoint interno de la UI) ni de plantillas de ventas,
así que Zapier/Make tampoco pueden crearlas: son envoltorios de esa misma API.
La API de Apollo sí crea secuencias completas, con asunto y cuerpo de cada paso.

### Secuencias creadas por API

| Secuencia | Id | Cadencia (días laborables) |
|---|---|---|
| INBOUND · Mobiliario Urbano — Lead web | `6a9844b94208650014fc4754` | 0 · 3 · 4 · 5 · 6 |
| OUTBOUND · Mobiliario Urbano — Ayuntamientos | `6a9844f7d0bf520010f72cc1` | 0 · 5 · 5 · 6 · 7 |

Ambas inactivas, horario «De 10 a 13 Europa» (`6780eebd4c847a01b0f7c509`),
firma de Apollo desactivada (el cuerpo ya firma) y pie legal en los diez
correos. OUTBOUND lleva `max_emails_per_day: 50` por paso.

### Integración Apollo ↔ HubSpot

- Pull HubSpot → Apollo: automático cada 15 min, no desactivable.
- Push Apollo → HubSpot: solo `Primary email status = Verified`; sella
  `hs_sourced_contact_origin = APOLLO` (propiedad nativa de HubSpot).
- Push de correo: solo los enviados desde Apollo y sus respuestas. Deja fuera
  la bandeja personal del remitente.
- Mapeo añadido: Apollo `City` → HubSpot `municipio`, que es la propiedad que
  usa el workflow de creación de negocios para nombrarlos.

### Datos pendientes de arreglar en la lista OUTBOUND (137 contactos)

Muestreo de 10 registros: ninguno tiene nombre, `city` está vacío en la mayoría
y `organization_name` es poco fiable (aparecen «Europa», «Inst», dominios
sueltos). Por eso el copy aprobado se creó **sin el token de municipio**: con
estos datos habría enviado asuntos truncados. El campo personalizado
`Provincia` sí está relleno y es fiable.


## Estado final del embudo (02/09/2026)

### Reparto de responsabilidades

| | Apollo | HubSpot |
|---|---|---|
| Envío de los correos | ✓ | — |
| Cadencia y parada por respuesta | ✓ | — |
| Contactos, negocios, pipeline | — | ✓ |
| Etapas del negocio | — | ✓ |
| Parada por reunión agendada | — | HubSpot lo detecta, el puente lo ejecuta en Apollo |

### Propiedades de contacto añadidas

| Propiedad | Tipo | Quién la rellena |
|---|---|---|
| `provincia` | texto | La integración de Apollo, desde su campo personalizado «Provincia». Es el dato que personaliza los correos OUTBOUND |
| `apollo_estado` | lista | El puente |
| `apollo_fecha_respuesta` | fecha/hora | El puente |

`apollo_estado` y `apollo_fecha_respuesta` existen también en negocios: los
workflows de etapa son de objeto negocio y no pueden filtrar por propiedades
del contacto, así que el puente escribe en los dos.

### Workflows

| Id | Nombre | Qué hace ahora |
|---|---|---|
| `4839947487` | MU · INBOUND — Lead web (propiedades y negocio) | Propietario, `inbound__outbound`, `lifecyclestage`, crea el negocio |
| `4840005827` | MU · OUTBOUND — Ayuntamientos (propiedades y negocio) | Ídem + añade a la lista 2841 |
| `4839142587` | MU · Propuesta enviada | Sin cambios |
| `4839860441` | MU · Respuesta o reunión → Muestra interés | 5 ramales: 3 nativos (sales email, reunión reservada, actividad de reunión) + `apollo_estado = respondido` + `apollo_fecha_respuesta` relleno |
| `4839928017` | MU · Reunión agendada | 3 ramales: los 2 nativos + `apollo_estado = reunion_agendada` |
| `4839041253` | MU · Reunión realizada → Negociación | Sin cambios |

Los dos primeros perdieron el paso de inscripción en secuencia: esa acción
también está bloqueada por suscripción en la UI. La inscripción la hace el
puente (`bridge/`).

Los seis están **desactivados** a la espera de la prueba de punta a punta.

`4839860441` tenía además una sexta rama (`hs_latest_marketing_email_reply_date
IS_KNOWN`) que se ha quitado (04/09): esa propiedad no existe en el portal
— no es que esté vacía, es un nombre inválido, así que esa rama nunca pudo
dispararse. No se ha sustituido por la propiedad real
(`hs_email_last_reply_date`, "Last marketing email reply date") a propósito:
es una fecha global a cualquier correo de marketing de Gravity Wave, no solo
a los de Mobiliario Urbano, así que un ayuntamiento con negocio abierto que
respondiera a una newsletter cualquiera habría saltado de etapa por error.
La rama que sí importa (`hs_latest_sales_email_reply_date`, la que rellena
Apollo) queda intacta.

Se creó además, en un intento previo, `4846749929` («MU · Respuesta detectada
por HubSpot → apollo_estado»): marcaba `apollo_estado = respondido` en el
contacto cuando `campana_apollo = mobiliario_urbano` y
`hs_sales_email_last_replied` estaba relleno. Quedó redundante en cuanto
`sync_replies()` empezó a hacer exactamente eso desde el puente (con el
añadido de `apollo_fecha_respuesta`, que este workflow no rellenaba). Nunca
se activó y se ha borrado del portal.

### Limpieza hecha

- Retirada la exclusión de la lista 2923 del workflow de reseteo mensual
  `939189697` (sus tres ramales vuelven a 469, 1568 y 2120). Con Apollo
  enviando, los leads de mobiliario ya no consumen contactos de marketing, así
  que protegerlos del reseteo solo gastaba cupo. La reinscripción mensual queda
  intacta.
- Borrada la lista 2923, que ya no la referenciaba ningún workflow.

### Pendiente de hacer a mano

1. Conectar el buzón de Amaia en Apollo (hoy el único conectado es el de Julen).
2. En Apollo, pestaña **Fields**: mapear su campo `Provincia` → HubSpot
   `provincia`. La API de la integración no expone los mapeos.
3. Borrar los 10 correos de marketing huérfanos y «ZZ prueba viabilidad». El
   token no tiene los scopes `marketing.email.*`.
4. Confirmar en el editor de Apollo que `{{provincia}}` sale como variable
   reconocida y no como texto plano.
5. Rotar el token de la app privada de HubSpot: se expuso durante la
   configuración.
