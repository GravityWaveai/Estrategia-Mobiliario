# Agente de prospección: rutina diaria

Lo ejecuta Claude cada día laborable a las 7:17 (hora de Madrid), antes de que
el puente inscriba a las 9:00 y de que Apollo empiece a enviar a las 10:00. Hace
cinco cosas, siempre en este orden: **comprobar, alimentar, elegir los
seguimientos, buscar y contar**.

Este fichero es la única fuente de instrucciones. Si algo de aquí choca con lo
que recuerdes de otro día, manda lo que pone aquí.

No contiene ni debe contener datos personales: el repositorio es público. Los
contactos viven en Apollo. En el repositorio solo entra qué municipios están
cubiertos (`campana/lista/cola-prospeccion.csv`).

## Las piezas

| Qué | Dónde | Identificador |
|---|---|---|
| Secuencia | Apollo | `6a9844f7d0bf520010f72cc1` |
| Lista de envío (el puente inscribe desde aquí) | Apollo · `OUTBOUND - MOBILIARIO URBANO` | `6a983205f242c800107386c8` |
| Lista de espera (leídos y dados por buenos) | Apollo · `V2 · EN ESPERA` | `6b05ad7fe36010001090c27a` |
| Reserva (tercer contacto y siguientes de un municipio) | Apollo · `V2 · RESERVA` | `6b05afe23f10330014ba9177` |
| Ya pasados a envío | Apollo · `V2 · EN COLA` | `6b05af812376ca0010c7052a` |
| Vía de entrada | Apollo · `V2 · BUZON`, `V2 · CONCEJAL`, `V2 · TECNICO` | `6b05afecb69ae10014e36577`, `6b05ad7fe36010001090c27b`, `6b05b0451815c30018c5ece2` |
| Prioridad | Apollo · `V2 · P1`, `V2 · P2` | `6b05ad7fe36010001090c27c`, `6b05affd7a0aab001837b151` |
| Referidos por una respuesta | Apollo · `V2 · REFERIDO` | por nombre |
| Recibieron el correo 1 y no el seguimiento | Apollo · `V2 · SIN SEGUIMIENTO` | por nombre |
| Bajas | Apollo · `V2 · BAJA (no contactar)` | por nombre |
| Campo `municipio` | Apollo, campo propio | `6a999f44b6a7d5001357d023` |
| Cola de municipios | repositorio | `campana/lista/cola-prospeccion.csv` |
| Perfil y exclusiones | repositorio | `campana/perfil-objetivo.md` |

El **tope diario** es el `OUTBOUND_DAILY_CAP` del flujo de GitHub en la rama por
defecto. Se lee así, cada día, porque puede cambiar:

```
git fetch -q origin && git show "origin/$(git remote show origin | sed -n 's/.*HEAD branch: //p')":.github/workflows/apollo-bridge.yml | grep -E "OUTBOUND_(DAILY_CAP|MAX_EMAILS_PER_DAY):"
```

Dos cosas de método que ya han costado tiempo:

- **Las llamadas a Apollo se hacen desde la conversación principal.** Un
  subagente que intenta usar Apollo se queda esperando un permiso que nadie ve
  a las siete de la mañana. Los subagentes solo leen webs.
- **Nombres de organización cortos.** Apollo rechazó dos tandas enteras por
  un contacto con «Ayuntamiento de Vandellòs i l'Hospitalet de l'Infant». Con
  «Ajuntament de Vandellòs» entró. Si una tanda falla con «Failed to create
  contacts», el culpable suele ser un solo contacto: se parte la tanda.
- **Las respuestas de Apollo al crear o editar contactos son enormes**, unas
  700 palabras por contacto. Por eso los lotes son pequeños y las búsquedas
  piden solo los campos que hacen falta (`fields`).

## Estado: en marcha desde el 24/11

Amaia dio el visto bueno el 24/11. Ese día se aplicó la v5 (`secuencia-v2.md`):
dos correos, 7 nuevos y 3 seguimientos al día, 10 en total, seguimiento a los
7 días. Se paró a los 22 contactos de la lista antigua
que seguían dentro y se fusionó el tope nuevo en la rama por defecto.

**Lo que enseñó el arranque (24 a 26/11).** El tope del paso 1 se bajó a 1
para probar con un solo correo y Apollo dejó toda la cola aplazada día y medio:
cuando un paso llega a su tope, los correos que sobran quedan aplazados y Apollo
no los vuelve a mirar hasta que cambia el tope o se reactiva la secuencia. Dos
reglas desde entonces:

- **El tope del paso 1 es 10 y no se baja.** Los 7 nuevos al día los limita el
  puente al inscribir, no Apollo. El tope del seguimiento sigue en 3 y el de la
  secuencia en 10.
- **En la cola del paso 1 no debe haber más correos que hueco para hoy.** Por
  eso se alimenta contando lo que ya hay programado (apartado 2).

Las llamadas que escriben en Apollo (crear contactos, listas, parar a alguien,
tocar la secuencia) pueden quedarse esperando una aprobación si Amaia no está
delante, y entonces la rutina se para ahí. Por eso van **al final**, después de
guardar la cola y de dejar escrito el parte.

Cuatro cosas que vigilar los primeros días, además de la rutina:

1. **El saludo.** Los dos primeros correos (25/11, a dos buzones) salieron
   bien: asunto con el municipio, «Hola,» y ninguna variable en crudo. Falta
   leer el primero enviado a una persona («Hola Nombre,»). Si sale en crudo, se
   avisa y se pide pausar la secuencia.
2. **La espera de 7 días**: naturales o laborables (ver el apartado 3).
3. **La apertura del correo 1.** El asunto es nuevo:
   «¿Mobiliario urbano en {{municipio}}?». Si el primer lunes ha abierto menos
   del 30 % de quienes lo recibieron, se avisa y se propone volver al original,
   «{{municipio}} y el Mediterráneo: ¿tenéis algo en marcha?».
4. **La foto.** El correo 1 lleva la foto de Benidorm. Si el rebote o los
   correos no enviados suben respecto a la lista antigua, se dice en el parte.

Reglas de texto que puso Amaia el 24/11 y valen para todo lo que escriba el
agente, partes incluidos: **ningún guion largo** y correos naturales, como
escribe ella.

## 1 · Comprobar (antes de tocar nada)

1. **La secuencia está activa.** `apollo_emailer_messages_search` con la
   secuencia y `display_mode: metadata_mode` da el recuento por estado.
2. **Nadie se ha quedado sin enviar por la plantilla.** Busca los contactos de
   la lista `V2 · EN COLA` con sus `contact_campaign_statuses`. Si alguno está
   en `failed` con un motivo que hable de variables («dynamic variables»,
   «snippets») **no se alimenta hoy** y se avisa: es un fallo de plantilla o un
   contacto sin `municipio`, y afecta a todos los que vengan detrás.
3. **El saludo se pinta bien.** Lee el contenido del último correo 1 enviado
   (`apollo_emailer_messages_search` con estado `delivered`, luego
   `apollo_emailer_messages_get_content`). Si en el texto aparece `{{`, `#if` o
   `#endif`, **se para todo** y se avisa: la plantilla está saliendo en crudo.
4. **Rebote de la lista nueva.** De los contactos de `V2 · EN COLA` que ya han
   recibido el correo 1, cuántos han rebotado. Con 20 o más enviados y un 5 % o
   más de rebote, **no se alimenta** y se avisa.
5. **Respuestas nuevas.** `apollo_emailer_messages_search` con la secuencia y
   el estado `replied` dice quién ha contestado. El texto de la respuesta no
   está en Apollo: llega al buzón de envío de Amaia, que no es el que Claude
   tiene conectado. Mientras HubSpot siga vivo se puede leer allí
   (`search_communications`); si no, se avisa a Amaia de quién ha contestado
   para que lo abra ella. Lo que hay que hacer con cada una está en el
   apartado «Respuestas».

Si una de las comprobaciones 2, 3 o 4 falla, se salta el paso 2 (alimentar) y
se sigue con los demás: elegir seguimientos y buscar contactos no añaden envíos.

## 2 · Alimentar la lista de envío

El puente inscribe cada día laborable a los contactos más recientes de la lista
de envío, hasta el tope. Por eso los contactos nuevos no se cargan todos de
golpe: esperan en `V2 · EN ESPERA` y cada mañana pasan a envío **tantos como el
tope diario**. Así se decide aquí quién sale y en qué orden.

1. Lee los contactos de `V2 · EN ESPERA` (id, municipio, listas).
2. Ordénalos por el `orden` que tiene su municipio en la cola (se cruza por
   `municipio_apollo`). Los dos contactos de un mismo municipio van juntos.
3. Quita de la selección los de un municipio que haya contestado en los
   últimos 30 días o que esté en bajas.
4. Si alguno de `V2 · EN ESPERA` ya está en la lista de envío o en una
   secuencia, no cuenta: se le quita `V2 · EN ESPERA` y se pasa al siguiente.
5. A los primeros, tantos como el tope: añádelos a la lista de envío y a
   `V2 · EN COLA`, y quítalos de `V2 · EN ESPERA`.

En la lista de envío no debe esperar nadie de un día para otro: lo que se pasa
por la mañana lo inscribe el puente ese mismo día. Antes de pasar a nadie se
cuenta lo que ya está pendiente de salir: los correos del paso 1 que Apollo
tiene programados (`scheduled` menos los seguimientos) más los contactos de la
lista de envío que el puente aún no ha inscrito. Se pasa solo lo que falte
hasta 7; si ya hay 7 o más, ese día no se pasa a nadie. Si el agente no corre un día, ese día no entra nadie
nuevo y no pasa nada.

**Sin pedir permiso.** Amaia lo dejó dicho el 24/11: los contactos del perfil
entran en la lista de envío sin preguntarle. El agente alimenta cada mañana y lo
cuenta en el parte; no espera un sí. La inscripción en la secuencia la sigue
haciendo el puente, que es quien respeta el tope diario.

## 3 · Elegir los seguimientos del día

El tope son **10 correos al día: 7 primeros correos y 3 seguimientos**. Lo fijó
Amaia el 24/11, con prioridad a los nuevos. Como entran 7 contactos al día y
solo hay sitio para 3 seguimientos, cada mañana se decide quién recibe el suyo.
El seguimiento sale 7 días después del correo 1, el mismo día de la semana, así
que cada día toca un solo grupo de siete.

1. Saca el grupo de hoy: los contactos que recibieron el correo 1 hace 7 días
   (`apollo_emailer_messages_search` con la secuencia y el paso 1, por fecha de
   envío) y siguen activos en la secuencia. Quien contestó, rebotó o pidió la
   baja ya está fuera.
2. Ordénalos así:
   1. Abrió el correo 1. Mientras HubSpot siga vivo es `apollo_estado =
      abierto`, que escribe el puente con el píxel propio.
   2. Persona con nombre antes que buzón.
   3. Prioridad 1 antes que prioridad 2.

   No más de uno por municipio, salvo que sobren huecos.
3. Los tres primeros se quedan como están: Apollo les envía el seguimiento hoy.
4. A los demás se les para en la secuencia
   (`apollo_emailer_campaigns_remove_or_stop_contact_ids` con `mode: stop` y el
   motivo «Sin seguimiento: tope de 10 correos al día»). **Nunca `remove`**, que
   es irreversible. Se les añade a `V2 · SIN SEGUIMIENTO`: son la segunda vuelta
   de más adelante.
5. Si se juntan dos grupos (un festivo, un día sin agente), tres por grupo.
6. Si no se sabe quién abrió (HubSpot apagado, píxel caído), se elige por los
   criterios 2 y 3 y se dice en el parte.

El tope de cada paso en Apollo (7 y 3) es el cinturón de seguridad: aunque el
agente falle un día, no salen más de 10 correos. Ese día Apollo elige por su
cuenta y deja cola; al día siguiente se para a quien lleve más de un día
esperando el seguimiento y no esté entre los elegidos.

La primera semana hay que comprobar en Apollo que la espera de 7 días cuenta
días naturales. Si cuenta laborables, el grupo de hoy es el de hace 9 días y se
corrige este apartado.

## 4 · Buscar contactos nuevos

Cinco municipios al día, mientras queden pendientes en la cola. A 7 contactos
nuevos diarios la lista de espera se gasta deprisa: con menos de cinco no
se repone.

1. De `cola-prospeccion.csv`, los cinco primeros con `estado = pendiente`,
   ordenados por `intentos` y después por `orden`. Así los que fallan pasan al
   final en vez de bloquear la cola. Con tres intentos fallidos se dejan.
2. Para cada uno, lee la web oficial. Dos herramientas, y se usan las dos. El
   rastreador entra en webs que al lector le devuelven un error 503, así que va
   primero; el lector, para las que el rastreador no entiende:
   - El rastreador, que es rápido y no gasta:
     `python3 campana/lista/rastrear_contactos.py rastrear --solo COD_INE` y
     luego `candidatos`. Borra antes `exports/rastreo/COD_INE.json` si existe.
   - Un agente de lectura (`web-fetch`) con el encargo de abajo, para lo que el
     rastreador no ve: fichas de concejales, webs con JavaScript, delegaciones.
3. Elige con las reglas del perfil. En resumen:
   - Solo direcciones publicadas en la web del propio ayuntamiento. Nunca una
     deducida de un patrón.
   - Dentro: buzón del área (Servicios, Vía Pública, Obras y Servicios, Parques
     y Jardines, Medio Ambiente, Playas, Brigada), concejal delegado de esas
     áreas con su correo, técnico con su correo.
   - Fuera: contratación, registro, alcaldía, `info@` y demás puertas
     genéricas; buzones de incidencias, salvamento o reservas; correos de
     Gmail y similares.
   - Si el texto visible y el enlace `mailto` no coinciden, no se elige: se
     anota en la cola y se deja.
   - Si la página lleva años sin actualizar, el buzón del área vale; el nombre
     de la persona, no.
4. Como mucho **dos** para envío por municipio, de áreas distintas: una del
   lado de Servicios o Vía Pública y otra del lado de Medio Ambiente o Playas.
   El resto, a reserva.
5. Créalos en Apollo con `apollo_contacts_bulk_create` (12 por llamada como
   mucho; la respuesta es muy larga): `email`, `title` con el cargo o el
   departamento, `organization_name`, `first_name` y `last_name` **solo si es
   una persona con nombre**, y el campo `municipio` con el nombre tal como se
   escribe en una frase («la Vila Joiosa», no «Vila Joiosa, la»). En un buzón
   sin persona `first_name` se deja vacío: la plantilla saluda con «Hola,».
6. Apollo no aplica las listas al crear. Con los ids que devuelve, añade cada
   contacto a sus listas con `apollo_labels_add_entity_ids_to_label_names`:
   `V2 · EN ESPERA` o `V2 · RESERVA`, la de su vía y la de su prioridad.
7. Si Apollo lo devuelve en `existing_contacts` es que el correo ya estaba. No
   le aplica los campos nuevos: hay que ponerle el `municipio` con
   `apollo_contacts_update`. Y si ya está en alguna secuencia, no se toca.
8. Actualiza la fila del municipio en la cola: `estado` (`cubierto` si hay al
   menos uno para envío), `contactos`, `intentos`, `ultimo_intento` y una
   `nota` corta si no salió nada («web en JavaScript», «solo publica el
   registro», «concejal sin correo: llamar»). Sin nombres ni direcciones.

### Encargo para el agente de lectura

```
Start at {WEB}, the official website of the town council (Ayuntamiento / Ajuntament) of {MUNICIPIO} ({PROVINCIA}, Spain). If it redirects to a site that is not the council's, stop and say so. Using ONLY official council pages (its own domain, its sede electrónica, its transparency portal), read at most 9 pages and find:
C = CURRENT councillors (concejal/a, regidor/a) whose delegation includes Medio Ambiente / Medi Ambient, Playas / Platges / Litoral, Parques y Jardines, Servicios (urbanos, técnicos, generales, públicos), Obras y Servicios, Mantenimiento or Vía Pública.
T = named municipal staff of those areas (técnico/a, jefe/a de servicio or sección, ingeniero/a).
B = the own mailbox and phone of those departments (not the general info@ / registro mailbox).
Look under: Corporación, Equipo de gobierno, Concejalías, Regidories, Áreas, Medio Ambiente, Playas, Servicios, Directorio, Contacto, Transparencia (organigrama).
Reply ONLY in this format, one line per item, "-" where not published:
MUNICIPIO: {MUNICIPIO}
VIGENCIA: <legislature or date shown on the pages>
C | full name | delegated areas as written | email | phone | source URL
T | full name | job title | email | phone | source URL
B | department | email | phone | source URL
NOTAS: <max 2 lines: conflicts between pages, pages that would not load>
Rules: copy emails exactly as published; never construct or guess an email address; do not use non-official websites.
```

## Respuestas

La velocidad importa más que el texto: una respuesta contestada el mismo día
vale el doble. El agente no contesta a nadie. Avisa el mismo día y deja escrita
en el parte la respuesta que propone, para copiar y enviar.

| Qué dice | Qué se hace |
|---|---|
| Da un nombre o un área («eso lo lleva Fulano», «escribid a tal correo») | Es lo que pide el correo 1 y lo mejor que puede pasar. Se crea el contacto en `V2 · REFERIDO`, **fuera de la secuencia**, y se propone el correo de Amaia para esa persona, citando a quien la remitió. |
| Pide la ficha, el precio o una llamada | Respuesta propuesta para el mismo hilo. Sin precios: los pone Amaia. |
| Objeción («no hay presupuesto», «va por licitación») | Respuesta propuesta que contesta a esa objeción y pide solo quién lo lleva. |
| «Baja» o cualquier negativa clara | El contacto a `V2 · BAJA (no contactar)`. No se vuelve a escribir a ese buzón, y a nadie más de ese ayuntamiento en 90 días. |
| Respuesta automática o acuse | Nada. |

**Nunca se envía un correo.**

## 5 · Contar

Guarda la cola (`git add campana/lista/cola-prospeccion.csv`, commit y push a
la rama de trabajo) y deja un parte de diez líneas como mucho:

- Pasados a envío hoy: cuántos y de qué municipios.
- Seguimientos de hoy: a qué municipios, con qué criterio, y a cuántos se ha
  parado.
- Encontrados hoy: cuántos, de qué municipios y por qué vía.
- Respuestas nuevas, cada una con lo que se ha preparado.
- Salud: rebote de la lista nueva y cualquier correo no enviado.
- Recorrido: cuántos quedan en espera y cuántos días son al tope actual;
  cuántos municipios quedan pendientes.
- Lo que necesite una decisión de Amaia, si hay algo.

Los lunes, además, la tabla de la semana por vía de entrada: enviados,
abiertos, respondidos y qué dijeron. Con ella se rellena la columna «Campaña
nueva» de las siete tasas (apertura; respuesta por contactado y por apertura;
respuesta útil por respuesta; cliente por respuesta, por apertura y por
contactado). Es el dato que dirá si el perfil funciona.

## Lo que el agente no hace nunca

- Deducir, completar o adivinar una dirección.
- Cambiar las plantillas de la secuencia.
- Inscribir a mano en la secuencia saltándose el tope del puente.
- Enviar un correo.
- Escribir a un municipio de la lista de exclusión: los tres clientes de
  referencia (Calp, Dénia, Benidorm) y los dos ayuntamientos que pidieron la
  baja (Alcúdia y Creixell).
- Gastar créditos de Apollo: nada de enriquecer, validar ni buscar personas.
- Subir un contacto al repositorio.

## Cuando se acabe la cola

Con los 177 municipios recorridos, el agente lo dice y propone el siguiente
universo en vez de seguir dando vueltas: municipios costeros de menos de 5.000
habitantes (decide el alcalde), los de 50.000 a 100.000 solo con contacto
nominal, o la segunda vuelta a la reserva en los municipios que no contestaron.

## Cómo pararlo

Decírselo a Claude en esta conversación («para el agente»), o desactivar la
tarea programada «Prospección diaria · ayuntamientos» en claude.ai. Parar el
agente no para los envíos: lo que ya esté en la lista de envío sigue su curso.
Para parar los envíos, se pausa la secuencia en Apollo.
