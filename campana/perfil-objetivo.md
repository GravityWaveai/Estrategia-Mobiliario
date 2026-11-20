# El perfil objetivo de la campaña de ayuntamientos

Definido el 2026-11-20 a partir de lo que ha pasado con los primeros 118
contactos. Sustituye al criterio anterior, que era «ayuntamiento costero» a
secas y producía un 75 % de direcciones a las que no se les puede vender.

## La regla en una línea

> **Técnico de Medio Ambiente, Parques y Jardines o Servicios de un municipio
> costero mediterráneo o insular de 5.000 a 50.000 habitantes.**

Todo lo demás es secundario.

## Por qué ese cargo

En un ayuntamiento la compra de mobiliario urbano tiene tres papeles y solo uno
sirve para un correo frío:

| Papel | Quién | ¿Sirve escribirle? |
|---|---|---|
| **Lo quiere** | Técnico de Medio Ambiente · Parques y Jardines · Playas y Litoral · ingeniero de Servicios Urbanos | **Sí.** Es quien redacta la memoria y quien pide presupuesto. Sin él no hay expediente. |
| Lo dota | Concejal del área | A veces. Vale para el relato político y para desatascar, no para empezar. |
| Lo tramita | Contratación · Secretaría · Intervención | **No.** Tramita lo que ya está decidido. Un correo comercial ahí no se contesta, y responderlo sería impropio. |

De las 6 respuestas que lleva la campaña, ninguna vino de contratación.

## Por qué ese tamaño de municipio

Es la variable que no se estaba usando y la que más decide.

| Habitantes | Qué pasa | Veredicto |
|---|---|---|
| < 5.000 | No hay técnico de medio ambiente; decide el alcalde. Pedido pequeño pero decisión en una semana. | Segunda ola |
| **5.000 – 50.000** | Hay técnico, hay partida y el contrato menor es la vía normal para mobiliario. Decisión en semanas. | **Objetivo** |
| 50.000 – 100.000 | Empieza a pesar la licitación y los acuerdos marco. | Solo con contacto nominal |
| > 100.000 | Todo va a licitación, ciclos de 12–18 meses, y ya tienen proveedor homologado. | **Fuera** |

En la lista actual están Barcelona, Valencia, Palma, Elche, Alicante, Orihuela y
Torrevieja. Son justo los que menos pueden responder a un correo frío.

## Señales que multiplican la probabilidad

Por orden de valor. Las dos primeras son las que de verdad separan una lista
buena de una excelente.

1. **Ha publicado un contrato menor de mobiliario urbano, bancos o papeleras en
   los últimos 18 meses.** Los contratos menores adjudicados se publican por
   obligación legal. Dice tres cosas a la vez: compran esto, tienen partida y
   sabes por cuánto.
2. **Presupuesto 2027 en tramitación con inversión en espacios públicos.** De
   octubre a diciembre se decide qué entra. Es la ventana que está abierta ahora.
3. **Bandera Azul** en alguna playa. Hay partida de litoral y un relato de
   sostenibilidad que alimentar.
4. **Puerto pesquero en el municipio.** El argumento deja de ser abstracto: el
   banco se puede hacer con las redes de su propia flota. Es el mejor gancho que
   tenemos y no se está usando.
5. **Adhesión a la Agenda Urbana o plan de economía circular.** Compromiso
   político ya escrito, fácil de citar en la memoria.

## Dónde se sacan los nombres

No de una base de datos comprada: de ahí salieron los `info@` y los
`contratacion@`.

- **Portal de transparencia** de cada ayuntamiento. La Ley 19/2013 obliga a
  publicar el organigrama y los responsables de cada área.
- **Sede electrónica → perfil del contratante**, para los contratos menores
  publicados y quién los firmó.
- **Plataforma de Contratación del Sector Público**, para cruzar quién ha
  comprado mobiliario urbano.
- La web del propio ayuntamiento, sección Medio Ambiente o Servicios.

## Tamaño del universo

Municipios costeros del Mediterráneo peninsular, Baleares y Canarias: del orden
de 280. En la banda de 5.000 a 50.000 habitantes quedan unos 170. A dos contactos
por municipio —el técnico y el concejal del área— salen **unos 340 contactos**.

Es suficiente para la campaña entera y es un trabajo acotado: se hace una vez.

## Criterio de exclusión, explícito

Fuera de la lista, sin excepción:

- Buzones de `contratacion@`, `contractacio@`, `registro@`, `registre@`
- Puertas genéricas: `info@`, `general@`, `ajuntament@`, `ayuntamiento@`, `oac@`,
  `sac@`, `alcaldia@`, `atencionciudadano@`, `web@`, `webmaster@`
- Municipios de más de 100.000 habitantes
- Cualquier contacto sin municipio relleno en Apollo: la plantilla usa
  `{{municipio}}` y Apollo no envía un correo con una variable vacía. Hoy hay 14
  correos sin enviar exactamente por esto.

## Qué medir para saber si el perfil funciona

El primer mes con la lista nueva valida o corrige la hipótesis. Lo que hay que
mirar:

- **Respuestas que dan un nombre o un área.** Es lo que pide el correo 1 y el
  verdadero indicador de que el perfil es bueno.
- **Personas con nombre añadidas por semana.** Es el cuello de botella real.
- Tasa de respuesta por banda de población, para confirmar que 5.000–50.000 es
  de verdad la franja buena.

La tasa de apertura no: con 6 de 260 correos registrados, en administración
pública no se puede medir.
