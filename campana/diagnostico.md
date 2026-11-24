# Diagnóstico de la campaña de ayuntamientos

Revisado el 2026-11-20 con los datos de Apollo, HubSpot y el píxel propio.
Sustituye al análisis del 17/11 y al parte del 20/11 por la mañana, que tenían
cinco errores. Están listados al final para que no se repitan.

## Las cifras que valen

| | Cifra | De dónde sale |
|---|---|---|
| Contactos que han recibido al menos un correo | 93 | Apollo, mensajes entregados |
| Abrieron | **46 · 49 %** | Píxel propio (`tracking/aperturas.gs`), aperturas creíbles |
| Respondieron | **4 · 4,3 %** | Mensajes de respuesta en Apollo y HubSpot |
| Respuestas positivas | **0** | Leídas una a una |
| Rebote desde el relanzamiento del 12/10 | **4 de 202 · 2 %** | Apollo |

## Qué dijeron las cuatro respuestas

1. Un servicio de planeamiento: que miremos la sede electrónica y el perfil del
   contratante, que es donde salen las licitaciones.
2. Un jefe de sección de playas y litoral: «No tenemos presupuesto».
3. Una empresa municipal de servicios: «BAJA».
4. Un ayuntamiento pequeño, tras el cuarto correo: «BAJA».

Las dos bajas están anotadas y esos buzones no se vuelven a tocar.

## Dónde se rompe

El correo llega y se abre. Lo que falla está entre abrir y contestar.

| Tipo de buzón | Abre | Responde |
|---|---|---|
| Alcaldía | 67 % | sin dato |
| Puerta genérica (`info@`, `ajuntament@`…) | 51 % | 2 de 53 |
| Buzón temático (medio ambiente, servicios, playas) | 46 % | 2 de 13 |
| Contratación / registro | 41 % | 0 de 17 |
| Persona con nombre | sin dato | 0 de 4 |

Tres conclusiones:

- **El asunto y la entregabilidad no eran el problema.** Abre la mitad, y abre
  igual en todos los tipos de buzón.
- **Quien abre no puede comprar.** La puerta genérica y contratación suman 70 de
  los 93 contactos. Un auxiliar de registro abre el correo y no tiene a quién
  pasárselo ni motivo para contestar.
- **A las personas del perfil casi no se les ha escrito.** De los 12 contactos
  con nombre que había en la lista, 8 no han recibido nunca un correo: a 7 les
  faltaba el campo `municipio` y Apollo no envía una plantilla con una variable
  vacía; el octavo quedó bloqueado porque otra persona de su ayuntamiento ya
  había contestado. Los cuatro que sí recibieron correo son poca muestra para
  concluir nada.

Y las dos respuestas con contenido son dos objeciones concretas (procedimiento
y presupuesto) que el correo no adelantaba. La v2 ya adelanta la primera
(contrato menor). La v3 propuesta adelanta la segunda (presupuesto de 2027).

## Qué se sostiene del plan y qué cambia

Se sostiene: el recorte a tres pasos, el contrato menor en la primera frase
útil, la franja de 5.000 a 50.000 habitantes y dejar fuera contratación,
registro y las puertas genéricas.

Cambia:

- **El píxel se queda.** Mide bien.
- **El rebote ya no es una urgencia.** 11 de los 15 rebotes fueron de la tanda de
  septiembre. Desde el relanzamiento es un 2 %, por debajo del umbral de Apollo.
- **La vía de entrada.** El técnico con nombre casi nunca tiene su correo
  publicado. Lo que sí publican las webs municipales son el concejal delegado
  del área y el buzón del departamento. Ver `perfil-objetivo.md`.
- **El volumen.** Con tres pasos y 8 correos al día entran menos de 3 contactos
  nuevos diarios. La lista nueva necesita más cupo para no tardar seis meses.

## Errores de los análisis anteriores

| Lo que se dijo | Lo que es |
|---|---|
| «Las aperturas no se pueden medir: solo 6 de 260 registran el píxel» | Era el contador de Apollo, que en el plan gratuito no mide. El píxel propio da 46 de 93. |
| «6,5 % de respuesta, la mejor de vuestras campañas» | Son 4 respuestas reales (4,3 %). Dos campañas anteriores tuvieron tasas más altas. |
| «2 respuestas con interés» | «Muestra interés» es una etapa que HubSpot pone sola a cualquier respuesta. Positivas: 0. |
| «13 descartados que confirman respuestas negativas» | Eran 11 rebotes de septiembre descartados en bloque y 2 negocios de prueba. |
| «14 % de rebote, se está quemando el dominio» | 2 % desde el relanzamiento. |
