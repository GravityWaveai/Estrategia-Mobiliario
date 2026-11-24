# Secuencia OUTBOUND v2 — ayuntamientos

Propuesta de 2026-11-20, **aplicada en Apollo ese mismo día** con el visto bueno de
Amaia. La secuencia `6a9844f7d0bf520010f72cc1` tiene ya 3 pasos (días 0, 4 y 9) y el
texto de abajo. Los 60 contactos que estaban en los pasos 4 y 5 han terminado la
cadencia en vez de recibirlos.

Secuencia antes: 5 pasos · 8 correos/día. Ahora: 3 pasos · 8 correos/día.

## Qué cambia y por qué

| Cambio | Motivo |
|---|---|
| De 5 pasos a 3 | La campaña lleva 4 respuestas reales (ver `diagnostico.md`). Lo único que produjo el paso 4 fue una baja, y el 5 no ha salido nunca. Los pasos 4 y 5 se comían dos tercios del cupo diario sin devolver nada útil. |
| El correo 1 pide un área, no una reunión | Un técnico no reserva hueco en el calendario de un proveedor. Decir «Medio Ambiente» cuesta cinco segundos, y es el dato que de verdad hace falta. |
| El contrato menor, en la primera frase útil | Es lo único que desbloquea a un técnico municipal: si no hace falta licitación, la conversación es posible este año. No aparecía en ningún correo. |
| El píxel de aperturas **se queda** | Se quitó el 20/11 por un error de lectura y se repuso el mismo día. Ver la nota de abajo. |
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

## Cómo se aplicó

`apollo_sequences_update` con los 3 pasos que se quedan y sin los dos últimos. Es un
diff declarativo: **el paso que no va en la llamada se borra**, y con él su plantilla.
Por eso los textos de los pasos 4 y 5 quedan copiados abajo, para poder rehacerlos.

Efecto inmediato: los 43 contactos que estaban en el paso 4 y los 17 del paso 5 han
pasado a «terminado». Lo único que había dado el paso 4 era una baja; el 5 no llegó a salir.

### Nota sobre el píxel de aperturas (corrección del 20/11)

En la primera aplicación se quitó el píxel de `script.google.com` de las tres
plantillas con el argumento de que «solo lo registraban 6 de 260 correos». **Era
falso.** Esa cifra es el contador de aperturas propio de Apollo, que en el plan
gratuito no mide nada. El píxel del equipo (`tracking/aperturas.gs`) sí funciona:
de 93 correos entregados registra 46 aperturas creíbles, un 49 %.

El píxel se repuso el mismo día en los tres pasos (`p=1`, `p=2`, `p=3`). Entre la
retirada y la reposición pudo salir algún correo sin él; esos no se pueden medir.
Las aperturas siguen siendo una métrica válida de esta campaña y el panel las
sigue contando.

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

---

## Propuesta v3 del correo 1 — pendiente de visto bueno

No está aplicada. Cambia dos cosas respecto a la v2, y solo dos, para poder
atribuir el resultado:

1. **Saludo con nombre** cuando el contacto es una persona. La lista nueva trae
   concejales con nombre y apellidos; «Hola Carlos,» no es lo mismo que «Hola,».
2. **Se adelanta a la objeción que ya nos han dado.** La única respuesta de un
   responsable del perfil fue «No tenemos presupuesto». El correo deja de pedir
   algo para este año y se apoya en el calendario: el presupuesto de 2027.

> Hola {nombre},
>
> Soy Amaia, de Gravity Wave. Fabricamos bancos y papeleras con el plástico de las
> redes de pesca que retiramos del Mediterráneo. Están instalados en Calpe, en
> Dénia y en el paseo de Benidorm —esas letras grandes del paseo son nuestras—.
>
> Te escribo ahora por el calendario, no porque busque nada para este año. Si en
> {{municipio}} estáis preparando el presupuesto de 2027, me gustaría que quien
> lleva el mobiliario urbano tenga la ficha técnica y un precio orientativo antes
> de que se cierre. Por precio unitario entra en **contrato menor**, sin licitación.
>
> ¿Me dices qué técnico lo lleva, o a qué correo se lo mando?
>
> Un saludo,
> Amaia Rodríguez
> Gravity Wave S.L. · Calpe (Alicante) · 676 525 906

Antes de aplicarla hay que comprobar cómo resuelve Apollo el saludo cuando el
contacto es un buzón sin nombre. Apollo no envía un correo con una variable
vacía —es lo que dejó sin salir los correos de siete contactos con nombre—, así
que el saludo tiene que ir en un campo propio relleno en todos los contactos
(«Hola Carlos,» o «Buenos días,»), o con la sintaxis condicional de Apollo
probada primero en un envío a una dirección interna.

---

## v4 · con la voz de Amaia — pendiente de su visto bueno (24/11)

Sustituye a la v3. No está aplicada: la secuencia está pausada hasta que Amaia
lea estos textos. Están también, al lado de los anteriores, en el documento
«Campaña ayuntamientos · Antes y ahora».

Cómo escribe Amaia, sacado de sus correos reales: corto, directo, de tú, una
idea por línea, preguntas concretas y «¡Gracias!» para cerrar.

**Asunto:** `Bancos para {{municipio}} hechos con redes de pesca`

### Correo 1 — día 0

> Hola Carlos,  *(«Hola,» si es el buzón de un departamento)*
>
> Soy Amaia, cofundadora de Gravity Wave. Estamos en Calpe y nos dedicamos a
> sacar redes de pesca del Mediterráneo y convertirlas en bancos y papeleras.
>
> Ya están en la calle en Calpe y en Dénia, y las letras grandes del paseo de
> Benidorm también son nuestras.
>
> Te escribo porque {{municipio}} es de costa y creo que os puede encajar. Dos
> cosas que me suelen preguntar los ayuntamientos:
>
> — No hay que pintarlo ni barnizarlo. Aguanta el salitre tal cual.
> — Por precio unitario entra en contrato menor, sin licitación.
>
> ¿Me dices quién lleva el mobiliario urbano en {{municipio}}? Le mando el
> catálogo y un precio orientativo, por si os cuadra para el presupuesto de 2027.
>
> ¡Gracias!
> Amaia

### Correo 2 — día 4, mismo hilo

> Hola de nuevo,
>
> Te mando una foto, que se entiende mejor que explicándolo. Así quedaron las
> letras en el paseo de Benidorm:
>
> *[foto]*
>
> Es el mismo material que usamos en los bancos. El color es el de la propia
> red, así que no se destiñe con el sol.
>
> Si me dices a quién se lo paso, le mando el catálogo y no te molesto más.
>
> Saludos,
> Amaia

### Correo 3 — día 9, mismo hilo

> Hola,
>
> Último correo, que no quiero ser pesada.
>
> Si el mobiliario urbano no depende de ti, ¿le reenvías este correo a quien lo
> lleve? Y si ahora no toca, con un «no» me vale y lo apunto.
>
> Si más adelante os planteáis renovar bancos o papeleras en {{municipio}}, aquí
> estamos, en Calpe.
>
> ¡Gracias por leerme!
> Amaia
