# El perfil objetivo de la campaña de ayuntamientos

Definido el 2026-11-20 y revisado ese mismo día con dos cosas que no se tenían
por la mañana: las aperturas reales de la campaña (`diagnostico.md`) y lo que de
verdad publican las webs municipales (`lista/README.md`).

## La regla en una línea

> **El área que compra y mantiene el mobiliario urbano —Servicios, Vía Pública,
> Parques y Jardines, Medio Ambiente o Playas— de un municipio costero
> mediterráneo o insular de 5.000 a 50.000 habitantes.**

## A quién se le escribe dentro del área

La versión anterior decía «al técnico, no al concejal». Leídas 119 webs
municipales, eso no se puede sostener tal cual: el correo personal de un técnico
casi nunca está publicado. De 158 direcciones del perfil encontradas, solo 2 son
el correo personal de un técnico.

Lo que sí se publica, por orden de valor:

| Vía de entrada | Qué es | Cuántas hay en la lista |
|---|---|---|
| **Buzón del departamento con el técnico nombrado** | `mediambient@…` y, al lado, «Tècnica: Fulana». Llega a su mesa y se le puede escribir por su nombre. | 11 |
| **Buzón del departamento** | El correo del área de Servicios, Medio Ambiente, Playas o la Brigada. Lo lee quien gestiona el día a día. | 82 |
| **Concejal delegado del área, con nombre** | En un municipio de este tamaño firma el contrato menor y conoce al técnico. No se le pide que compre: se le pide el nombre del técnico. | 63 |
| Técnico con correo personal | El ideal. Cuando aparece, va el primero. | 2 |

Los datos de la campaña apuntan en la misma dirección: los buzones temáticos
son el único grupo con una tasa de respuesta distinta (2 de 13, frente a 2 de 53
en las puertas genéricas y 0 de 17 en contratación).

El correo 1 ya está escrito para esto: no pide una reunión, pide «¿quién lo
lleva?». A un concejal o a un buzón de departamento esa pregunta se contesta
reenviando el correo.

## Dos contactos por municipio, no más

En cada ayuntamiento entran primero dos direcciones de áreas distintas —una del
lado de Servicios o Vía Pública y otra del lado de Medio Ambiente o Playas—. El
resto queda en reserva para una segunda vuelta. Tres correos iguales en la misma
semana al mismo ayuntamiento se leen como envío masivo.

## Por qué ese tamaño de municipio

| Habitantes | Qué pasa | Veredicto |
|---|---|---|
| < 5.000 | No hay técnico de medio ambiente; decide el alcalde. Pedido pequeño pero decisión en una semana. | Segunda ola |
| **5.000 – 50.000** | Hay técnico, hay partida y el contrato menor es la vía normal para mobiliario. Decisión en semanas. | **Objetivo** |
| 50.000 – 100.000 | Empieza a pesar la licitación y los acuerdos marco. | Solo con contacto nominal |
| > 100.000 | Todo va a licitación, ciclos de 12–18 meses, y ya tienen proveedor homologado. | **Fuera** |

## El universo, con datos oficiales

Ya no es una estimación. Sale de cruzar el fichero de unidades locales de
Eurostat (qué municipios son costeros y su población del INE a 1 de enero de
2024) con la relación de playas con Bandera Azul 2026 de ADEAC.

| Prioridad | Criterio | Municipios |
|---|---|---|
| **1** | 5.000 – 50.000 habitantes, con mar y con Bandera Azul 2026 | 111 |
| **2** | 5.000 – 50.000 habitantes, con mar, sin Bandera Azul | 66 |
| | **Objetivo de la campaña** | **177** |

Están en `lista/universo-municipios.csv`, cada uno con su web oficial. Fuera
quedan los clientes de referencia (Calp, Dénia, Benidorm), los dos buzones que
pidieron la baja y los municipios de más de 100.000 habitantes.

## Señales que multiplican la probabilidad

1. **Ha publicado un contrato menor de mobiliario urbano, bancos o papeleras en
   los últimos 18 meses.** Dice tres cosas a la vez: compran esto, tienen partida
   y sabes por cuánto. Sigue sin explotar: es el siguiente filtro que añadir.
2. **Presupuesto 2027 en tramitación.** Es la ventana abierta ahora.
3. **Bandera Azul.** Ya está en la lista: es lo que separa la prioridad 1 de la 2.
4. **Puerto pesquero en el municipio.** El banco se puede hacer con las redes de
   su propia flota. Es el mejor gancho que tenemos y no se usa en ningún correo.

## Criterio de exclusión, explícito

- Buzones de `contratacion@`, `contractacio@`, `registro@`, `registre@`
- Puertas genéricas: `info@`, `general@`, `ajuntament@`, `ayuntamiento@`, `oac@`,
  `sac@`, `alcaldia@`, `atencionciudadano@`, `web@`, `webmaster@`
- Buzones de incidencias, de salvamento o de reservas, aunque lleven «playas» o
  «medio ambiente» en el nombre
- Municipios de más de 100.000 habitantes
- Cualquier contacto sin municipio relleno en Apollo: la plantilla usa
  `{{municipio}}` y Apollo no envía un correo con una variable vacía

## Qué medir para saber si el perfil funciona

- **Respuestas que dan un nombre o un área.** Es lo que pide el correo 1.
- **Tasa de respuesta por vía de entrada**: buzón con técnico, buzón, concejal.
  Con 115 contactos en la primera ola hay muestra para ver diferencias.
- **Aperturas**, como hasta ahora: el píxel propio funciona (49 %).
- **Rebote de la ola nueva.** Las direcciones salen de webs oficiales pero no
  están validadas una a una; si pasa del 4 % se para y se limpia.
