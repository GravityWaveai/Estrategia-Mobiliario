# Secuencia OUTBOUND v2 — ayuntamientos

Propuesta de 2026-11-20. **Todavía no aplicada en Apollo**: cambiar una secuencia
viva con contactos en cadencia necesita el visto bueno de Amaia.

Secuencia actual: `6a9844f7d0bf520010f72cc1` · 5 pasos · 8 correos/día.

## Qué cambia y por qué

| Cambio | Motivo |
|---|---|
| De 5 pasos a 3 | Las 6 respuestas salieron de los correos 1 y 2. Los pasos 3 y 4 llevan 77 entregados y **cero** respuestas; el 5 no ha salido nunca. Los pasos 4 y 5 se comen dos tercios del cupo diario sin devolver nada. |
| El correo 1 pide un área, no una reunión | Un técnico no reserva hueco en el calendario de un proveedor. Decir «Medio Ambiente» cuesta cinco segundos, y es el dato que de verdad hace falta. |
| El contrato menor, en la primera frase útil | Es lo único que desbloquea a un técnico municipal: si no hace falta licitación, la conversación es posible este año. No aparecía en ningún correo. |
| Fuera el píxel de `script.google.com` | 6 de 260 correos lo registraron. No mide nada y es señal de spam para los filtros de la administración. |
| Pie legal de seis líneas a dos | El bloque de RGPD ocupaba más que el mensaje. Sigue cumpliendo: base jurídica, identidad y baja. |
| Asuntos planos | «{{municipio}} y el Mediterráneo: ¿tenéis algo en marcha?» suena a campaña. Un asunto administrativo pasa mejor los filtros y se parece más a lo que el técnico abre. |

Lo que **no** cambia: el tono, la prueba local (Calpe, Dénia, Benidorm) y la
salida fácil. Eso ya estaba bien.

---

## Correo 1 — día 0 · hilo nuevo

**Asunto:** `Mobiliario urbano en {{municipio}} — ¿quién lo lleva?`

> Hola,
>
> En Gravity Wave fabricamos bancos y papeleras con el plástico de las redes de
> pesca que retiramos del Mediterráneo. Están instalados en Calpe, en Dénia y en
> el paseo de Benidorm —esas letras grandes del paseo son nuestras—.
>
> Te escribo por algo concreto: por precio unitario entran en **contrato menor**,
> así que no hace falta licitación ni esperar a un acuerdo marco.
>
> ¿En {{municipio}} esto lo lleva Medio Ambiente, Parques y Jardines o Servicios?
> Con que me digas el área —o el nombre de quien lo lleva— me vale: le paso la
> ficha técnica a quien corresponda y no te molesto más.
>
> Un saludo,
> Amaia Rodríguez
> Gravity Wave S.L. · Calpe (Alicante) · 676 525 906

## Correo 2 — día 4 · responde al hilo

> Hola de nuevo,
>
> Te dejo una foto por si ayuda a situarlo: así quedó el material en el paseo de
> Benidorm.
>
> *[foto letras Benidorm]*
>
> Lo que suelen preguntar los técnicos son dos cosas:
>
> — No se pinta ni se barniza. Aguanta el salitre sin tratamiento, así que no
> arrastra partida de mantenimiento cada año.
> — El color es el de la red de origen, así que no se destiñe con el sol.
>
> ¿Me dices a quién le paso la ficha técnica?

## Correo 3 — día 9 · responde al hilo

> Hola,
>
> Este es mi último correo, no quiero ser pesada.
>
> Si estáis cerrando el presupuesto de {{municipio}} para 2027, es buen momento
> para dejar prevista una partida de mobiliario urbano. Si te viene bien, te
> mando la ficha técnica y el precio para que lo tengáis a mano cuando toque.
>
> Y si no es el momento, con un «no» me vale y lo anoto.

## Pie, en los tres

> Gravity Wave S.L. · B42708982 · Calle Llevant 1, 03710 Calpe (Alicante)
> Te escribimos a una dirección profesional publicada, por interés legítimo en una
> comunicación entre empresa y administración (RGPD art. 6.1.f). Responde **BAJA**
> y no volvemos a escribirte.

---

## Cómo aplicarlo

`apollo_sequences_update` con los 3 pasos que se quedan y sin los dos últimos.
Es un diff declarativo: **el paso que no va en la llamada se borra**, y con él su
plantilla. Antes de ejecutarlo, los textos de los pasos 4 y 5 quedan copiados
abajo para poder rehacerlos.

En cadencia hay hoy 43 contactos en el paso 4 y 17 en el paso 5: al quitar esos
pasos terminan la secuencia en vez de recibirlos. Como ninguno de los dos ha
dado una sola respuesta, es lo que queremos.

### Respaldo — paso 4 (se borra)

Asunto: *(vacío, responde al hilo)*

> Hola de nuevo,
> Hay un dato que casi nunca sale en la comparativa de presupuestos y que luego
> pesa durante años: el mantenimiento.
> Nuestro material no se pinta ni se barniza, aguanta el salitre sin tratamientos
> y el color es el de la red de origen, así que no se destiñe con el sol. En la
> práctica, una partida menos en el presupuesto de mantenimiento cada año.
> Y hay un segundo dato que sí es fácil de llevar a una memoria o a un pleno:
> cada pieza lleva calculado el CO₂ que ahorra frente a fabricarla con plástico
> virgen.
> ¿Cómo vais de mantenimiento con el mobiliario actual en {{municipio}}? ¿Os está
> dando trabajo o de momento va bien?

### Respaldo — paso 5 (se borra)

Asunto: *(vacío, responde al hilo)*

> Hola,
> Este es mi último correo, no quiero ser pesada.
> Si en algún momento os planteáis renovar bancos, papeleras o alguna zona
> infantil en {{municipio}}, aquí me tenéis. Y si prefieres que no vuelva a
> escribir, con un «no, gracias» me vale y lo anoto.
> Gracias por el tiempo de todas formas.
