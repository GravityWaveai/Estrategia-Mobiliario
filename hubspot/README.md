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

## Estado: aprovisionado y verificado (31/08/2026)

Conexión comprobada contra el portal 26243090 (EU1, Europe/Madrid, EUR).
El pipeline y las diez propiedades existen y coinciden con las specs de
`spec/` — nombres internos, etiquetas, tipos y opciones, valor a valor.

IDs reales en el portal (los necesitan los agentes y automatizaciones):

| Pieza | ID |
|---|---|
| Pipeline «Mobiliario Urbano» | `4080461018` |
| Etapa «Lead mobiliario» | `5948376264` |
| Etapa «Propuesta en preparación» | `5948376265` |
| Etapa «Propuesta entregada» | `5948376266` |
| Etapa «Reunión agendada» | `5948376267` |
| Etapa «Ajuste de propuesta» | `5948376268` |
| Etapa «Acuerdo firmado» (ganado) | `5948376269` |
| Etapa «Descartado» (perdido) | `5948376270` |

Pendiente de configurar en UI (no cubierto por API): las tres reglas del
apartado siguiente (importe obligatorio, `motivo_perdida` obligatorio) y
los pasos 2–3 del plan post-aprovisionamiento.

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
