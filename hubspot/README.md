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
