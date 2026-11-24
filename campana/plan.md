# El plan de la campaña de ayuntamientos

Planteado el 2026-11-24. Qué se quiere conseguir, cómo funciona la máquina,
quién hace qué cada día y con qué números se decide si va bien.

## El objetivo

Que un técnico o un concejal de un municipio costero conteste con un nombre:
«eso lo lleva Fulano». De ahí salen la ficha, el precio y el contrato menor.
La campaña no vende por correo: consigue la conversación.

Hasta ahora, 93 ayuntamientos contactados y ninguna conversación. La causa está
en `diagnostico.md`: se escribía a quien no puede comprar.

## Cómo funciona

```
 webs municipales
        │  el agente lee 5 ayuntamientos al día
        ▼
 V2 · EN ESPERA  ──────────►  lista de envío  ──────►  secuencia de 2 correos
 (leídos y dados              el agente pasa           el puente inscribe
  por buenos)                 cada mañana los          y Apollo envía
        │                     que tocan                      │
        ▼                                                    ▼
 V2 · RESERVA                                          respuestas
 (segunda vuelta)                                            │
                                                             ▼
                                              Amaia contesta el mismo día
```

Cuatro piezas, cada una con un solo trabajo:

| Pieza | Qué hace | Quién |
|---|---|---|
| **Agente de prospección** | Lee webs, elige contactos del perfil, los carga en espera, cada mañana pasa a envío los 7 que tocan y elige los 3 seguimientos del día. Avisa de respuestas y de problemas. | Claude, cada día laborable a las 7:17 |
| **Puente** | Inscribe en la secuencia lo que haya en la lista de envío, hasta el tope diario. Mide aperturas. | GitHub, cada hora |
| **Secuencia** | Dos correos: el primero y, a la semana, un seguimiento con la foto de Benidorm para 3 de cada 7. | Apollo, de 10 a 19 h |
| **La conversación** | Contestar a quien responde, llamar a quien no tiene correo, mandar ficha y precio. | Amaia |

La rutina del agente está escrita paso a paso en `agente-prospeccion.md`.

## El ritmo

| | Hasta el 24/11 | Desde el visto bueno de Amaia |
|---|---|---|
| Ayuntamientos nuevos al día | 2 | **7** |
| Seguimientos al día | los que cupieran | **3** |
| Correos al día, en total | 8 | **10** como máximo |
| Contactos nuevos por semana | 10 | 35 |

Lo fijó Amaia el 24/11: empezar de cero con la lista nueva y no pasar de 10
correos al día contando los seguimientos, con prioridad a los nuevos. La primera
ola (113 contactos) sale en poco más de tres semanas.

El reparto tiene un coste que conviene tener presente: con 3 seguimientos al
día, 4 de cada 7 contactos reciben un solo correo. Por eso los 3 no se reparten
al azar: van primero a quien abrió el correo 1 y no contestó. Los otros 4 quedan
apartados para una segunda vuelta.

Amaia dio el visto bueno el 24/11: ese día se aplicaron los textos, se paró a
los contactos de la lista antigua que seguían dentro de la secuencia, se fusionó
el tope nuevo y se reactivó la secuencia.

## Las dos semanas que importan

El presupuesto municipal de 2027 se cierra entre diciembre y febrero. El
seguimiento se apoya en eso. Lo que entre en secuencia antes de Navidad llega a tiempo;
lo que entre en febrero, no. Por eso el orden de salida es: primero prioridad 1
(con Bandera Azul), empezando por Alicante, Valencia, Castellón y Murcia, que
son los que conocen Calpe, Dénia y Benidorm.

## Qué se mide y cuándo se actúa

| Indicador | Bien | Se actúa si… | Qué se hace |
|---|---|---|---|
| Rebote de la lista nueva | menos del 3 % | llega al 5 % con 20 enviados | El agente deja de alimentar y se limpia la lista |
| Apertura | 45 % o más | baja del 30 % | Problema de entrega o de asunto: se revisa antes de seguir |
| **Respuesta** | 8 % o más | menos del 4 % con 60 enviados | El perfil o el correo 1 no funcionan: se cambia uno de los dos, no los dos |
| Respuestas que dan un nombre | una de cada tres | ninguna en 15 respuestas | La pregunta del correo 1 no se entiende |
| Tiempo en contestar a una respuesta | el mismo día | más de dos días | Es el único indicador que depende de Amaia |

El 8 % es un objetivo de trabajo, no una previsión: sale de que los buzones del
área contestaron 2 de 13 en la lista antigua, que es una muestra muy pequeña.
Las primeras tres semanas dirán el número real.

Cada lunes el agente deja la tabla de la semana por vía de entrada (buzón,
concejal, técnico) y por prioridad. Es lo que dirá por dónde seguir.

Con unos 100 correos enviados, a las tres semanas, hay dato para decidir. Si la
respuesta está por debajo del 4 % o no hay ninguna respuesta útil, se cambia una
sola cosa, el texto o el perfil, y se vuelve a medir.

## Lo que hace Amaia

1. **Contestar el mismo día** a cualquier respuesta. El agente avisa y deja la
   respuesta propuesta.
2. **Dos correos a mano**, ya escritos: al jefe de playas que dijo que no había
   presupuesto y al técnico de Medio Ambiente al que Apollo nunca escribió.
3. **Llamar** a las 11 personas identificadas que no publican correo. Son
   concejales con nombre y delegación; la centralita los pasa.
4. **Decidir** si se mantiene el reparto de 7 y 3 cuando haya tres semanas de
   datos.

## Lo que queda fuera, a propósito

- Contratación, registro, alcaldía y las puertas genéricas. 23 contactos de la
  lista antigua que aún no habían recibido nada se han apartado de la cola.
- Municipios de más de 100.000 habitantes.
- Comprar bases de datos o gastar créditos de Apollo en enriquecer.
- Validar las direcciones una a una: el rebote se vigila en vez de pagarlo por
  adelantado.

## Riesgos

| Riesgo | Cómo se ve | Qué lo frena |
|---|---|---|
| La plantilla nueva sale con el saludo en crudo | El agente lee cada mañana el último correo 1 enviado | Se para la alimentación ese mismo día |
| Un contacto sin `municipio` deja de recibir | Estado `failed` en la secuencia | El agente lo comprueba antes de alimentar |
| Direcciones caducadas | Rebote | Umbral del 5 % |
| El agente no corre un día | No entra nadie nuevo y Apollo elige los 3 seguimientos por su cuenta | El tope por paso en Apollo (7 y 3) impide pasar de 10; el agente lo ordena al día siguiente |
| HubSpot se apaga | El panel deja de actualizarse | Los envíos no dependen de él desde el 20/11 (pendiente de fusionar) |
| Demasiados correos al mismo ayuntamiento | Dos personas del mismo sitio comentan que les ha llegado lo mismo | Dos por municipio y de áreas distintas; el resto, a reserva. Un solo seguimiento por municipio |
| El asunto nuevo se abre menos de lo esperado | El correo 1 lo abre menos del 30 % la primera semana | Se vuelve al asunto original |
| La foto del correo 1 perjudica la entrega | Suben el rebote o los no enviados | Se quita del correo 1 y se deja solo en el seguimiento |

## Después de los 177

Cuando se acabe la cola el agente lo dice y propone el siguiente universo:
la segunda vuelta a la reserva en los municipios que no contestaron, los
costeros de menos de 5.000 habitantes, o los puertos pesqueros con el gancho
de «las redes de vuestra propia flota», que es el mejor argumento que hay y
todavía no se ha usado en ningún correo.
