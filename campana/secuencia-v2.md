# Secuencia OUTBOUND: ayuntamientos

> **En vigor: la v5, al final de este fichero** (dos correos, 10 al día),
> aplicada el 24/11 con el visto bueno de Amaia. Lo de arriba es el historial. Los textos
> que se enviaron hasta el 24/11 se conservan tal cual, con sus guiones largos;
> desde el 24/11 no se usa ninguno.

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

## Correo 1 · día 0 · hilo nuevo

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

## Correo 2 · día 4 · responde al hilo

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

## Correo 3 · día 9 · responde al hilo

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

### Respaldo · paso 4 (se borra)

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

### Respaldo · paso 5 (se borra)

Asunto: *(vacío, responde al hilo)*

> Hola,
> Este es mi último correo, no quiero ser pesada.
> Si en algún momento os planteáis renovar bancos, papeleras o alguna zona
> infantil en {{municipio}}, aquí me tenéis. Y si prefieres que no vuelva a
> escribir, con un «no, gracias» me vale y lo anoto.
> Gracias por el tiempo de todas formas.

---

## Propuestas v3 y v4 (20 y 24/11): descartadas

Ninguna llegó a enviarse. La v3 quedó cargada en el paso 1 de Apollo con la
secuencia pausada; la v4 solo existió en este fichero. Las sustituye la v5. De
ellas se conserva el saludo con nombre cuando el contacto es una persona, el
contrato menor y el presupuesto de 2027.

Sobre el saludo: Apollo no envía un correo con una variable vacía (es lo que
dejó sin salir los correos de siete contactos con nombre). La plantilla usa la
sintaxis condicional de Apollo,
`{{#if first_name}}Hola {{first_name}},{{#else}}Hola,{{#endif}}`, que todavía no
se ha visto en un envío real: el agente lee el primer correo 1 que salga.

---

## v5 · dos correos, 10 al día: aplicada el 24/11

Aplicada en Apollo el 24/11. Amaia dio el visto bueno ese día con dos cambios:
la foto de Benidorm también en el correo 1 y un asunto elegido por los datos de
apertura. Los textos están también, al lado de los anteriores, en el documento
«Campaña ayuntamientos · Antes y ahora».

Las tres reglas que puso Amaia el 24/11:

1. Como mucho **10 correos al día** contando los seguimientos, con prioridad a
   los nuevos: 7 nuevos y 3 seguimientos.
2. **Ningún guion largo** en ningún texto.
3. Naturales, como escribe ella: corto, directo, de tú, una idea por línea y
   «¡Gracias!» para cerrar.

| Paso | Cuándo | Tope al día | A quién |
|---|---|---|---|
| Correo 1 | día 0, hilo nuevo | 7 | A todos |
| Seguimiento | día 7, mismo hilo | 3 | A 3 de cada 7: primero a quien abrió el correo 1 y no contestó |

El tercer correo desaparece: con 10 al día, un segundo seguimiento le quitaría
el sitio a un ayuntamiento nuevo. Lo que pedía (el presupuesto de 2027 y que lo
reenvíen a quien lo lleve) pasa al seguimiento único.

**Asunto:** `¿Mobiliario urbano en {{municipio}}?`

Por qué este: el estudio más grande que hay sobre asuntos en frío (Belkins, 5,5
millones de correos de 2024) da la apertura más alta a tres rasgos, y este los
reúne: personalizado con algo del destinatario (46 % frente a 35 %), en forma
de pregunta (46 %, el tipo que más abre) y de 2 a 4 palabras (46 %; a partir de
7 baja al 39 % y con 9 al 35 %). El asunto original, «{{municipio}} y el
Mediterráneo: ¿tenéis algo en marcha?», tenía los dos primeros pero entre 8 y 11
palabras. Su 49 % no sirve para comparar: es por contacto y sumando hasta cinco
correos, no por correo.

### Correo 1

> Hola Carlos,  *(«Hola,» si es el buzón de un departamento)*
>
> ¿Lleváis vosotros el mobiliario urbano de {{municipio}}, los bancos y las
> papeleras?
>
> Soy Amaia, de Gravity Wave. Los hacemos con redes de pesca que sacamos del
> Mediterráneo. Ya están puestos en Calpe y en Dénia, y las letras grandes del
> paseo de Benidorm también son nuestras:
>
> *[foto: `https://www.thegravitywave.com/wp-content/uploads/2026/08/letras_benidorm.jpg`]*
>
> No hay que pintarlos ni barnizarlos, y se pueden comprar por contrato menor.
>
> Si lo lleváis vosotros, os mando el catálogo. Si lo lleva otra persona, dime
> quién y le escribo.
>
> ¡Gracias!
> Amaia

80 palabras. Se contesta con un sí o con un nombre. Lleva la foto de Benidorm
dentro del correo (la pidió Amaia el 24/11), sin enlaces y sin adjuntos, y el
píxel propio de aperturas (`p=1`).

### Seguimiento

> Hola de nuevo,
>
> Te vuelvo a mandar la foto, por si no la viste. Así quedó nuestro material en
> el paseo de Benidorm:
>
> *[la misma foto]*
>
> Si os encaja para el presupuesto de 2027, te paso el catálogo y un precio
> orientativo.
>
> Y si no depende de ti, ¿se lo reenvías a quien lo lleve?
>
> ¡Gracias!
> Amaia

La foto va dentro del correo, alojada en la web de Gravity Wave, sin enlace. No
es un adjunto. Píxel `p=2`.

El pie es el de dos líneas de arriba, en los dos correos.

### Qué se comparte y cuándo

| Cuándo | Qué |
|---|---|
| Correo 1 | Texto y la foto de las letras de Benidorm, dentro del correo |
| Seguimiento | La misma foto, otra vez |
| Cuando contestan | El catálogo «GRAVITEC · Catálogo Mobiliario Urbano 2026» en PDF y un precio orientativo, que pone Amaia |
| Nunca en frío | Adjuntos, tarifa ni precios unitarios |

### En qué se apoya

Datos publicados por empresas de correo en frío. Sirven para la dirección, no
para la cifra: son casi todos de ventas entre empresas y en inglés.

| Qué dicen | Fuente | Qué se ha hecho |
|---|---|---|
| Los correos de 100 palabras o menos, de tres o cuatro frases, son los que más respuestas reciben; los mejores bajan de 80 | [Gong](https://www.gong.io/resources/labs/does-cold-email-even-work-any-more-heres-what-the-data-says/), [Instantly](https://instantly.ai/cold-email-benchmark-report-2026), [Snov](https://snov.io/blog/cold-email-statistics/) | De 150 palabras a 80 |
| En frío funciona mejor pedir interés que pedir una reunión | [Gong, 304.174 correos](https://www.gong.io/resources/labs/this-surprising-cold-email-cta-will-help-you-book-a-lot-more-meetings/) | Se quita el enlace a la agenda; se pregunta si lo llevan ellos |
| Los seguimientos dan más de la mitad de las respuestas, pero cada uno rinde menos que el anterior y a partir del tercero la tasa baja | [Belkins](https://belkins.io/blog/sales-follow-up-statistics), [Hunter 2025, 31 millones de correos](https://hunter.io/the-state-of-cold-email-2025), [Woodpecker](https://woodpecker.co/cold-email-benchmark/) | De cuatro seguimientos a uno, primero a quien abrió |
| El primer correo, sin enlaces ni adjuntos | [Mailshake](https://mailshake.com/blog/module-1-cold-email-landscape/), [Woodpecker](https://woodpecker.co/blog/boost-cold-email-deliverability/), [Hunter](https://hunter.io/blog/is-html-harming-your-cold-email-deliverability/) | Ni enlaces ni adjuntos en ninguno de los dos |
| Una o dos imágenes no perjudican la entrega si el correo tiene texto suficiente | [lemlist](https://www.lemlist.com/blog/images-cold-email-deliverability) | Una sola foto por correo, con 80 palabras de texto |
| Abren más los asuntos personalizados (46 % frente a 35 %), en forma de pregunta (46 %) y de 2 a 4 palabras (46 %) | [Belkins, 5,5 millones de correos](https://belkins.io/blog/b2b-cold-email-subject-line-statistics), [Yesware](https://www.yesware.com/blog/cold-email-subject-lines/) | Asunto de 4 palabras, con el municipio y en pregunta |

### Lo que no se sabe todavía

- **Si convertirá mejor.** Nadie puede asegurarlo. La mejora de verdad está en la
  lista, más que en el texto: la campaña anterior tuvo un 4,3 % de respuesta, que
  es lo normal, y ninguna sirvió porque contestaba quien no podía comprar.
- **El asunto.** Sigue el patrón que más abre en los estudios, pero no está
  medido con ayuntamientos. Si en la primera semana abre el correo 1 menos del
  30 % de quienes lo reciben, se vuelve al original.
- **La foto en el correo 1.** Muchos ayuntamientos usan programas de correo que
  no cargan las imágenes hasta que el usuario lo pide: verán el texto y un
  hueco con la descripción de la foto. Tampoco cargará el píxel, así que la
  apertura medida se queda corta, como hasta ahora.
- **El píxel.** Algunas de estas fuentes aconsejan quitar el seguimiento de
  aperturas del primer correo. Se mantiene porque sin él no hay tasa de apertura
  ni forma de elegir a quién hacer seguimiento.
- **El contrato menor.** Amaia tiene que confirmar que un pedido normal queda
  por debajo de 15.000 € sin IVA. Si no, se quita la frase.
- **El teléfono.** El pie llevaba un número y la firma automática otro. Decide
  Amaia cuál se queda.
- **El saludo condicional**, hasta verlo en el primer envío real.
