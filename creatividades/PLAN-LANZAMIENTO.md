# Lanzamiento en redes — Mobiliario urbano

Creatividades y calendario para lanzar la línea de mobiliario urbano de
Gravity Wave en **Instagram y LinkedIn**, alineadas con la estrategia de
captación de ayuntamientos del embudo «Mobiliario Urbano».

**33 creatividades · 10 piezas · 4 semanas.**

---

## 1. El problema que resuelve este plan

La estrategia va a ayuntamientos, pero **la mayoría de los seguidores de
Gravity Wave no son ayuntamientos**: son gente a la que le importa el mar,
marcas, y equipos de ESG. Una campaña de catálogo B2G les aburre, y sin ellos
no hay alcance.

La salida es **contar una sola historia en dos capas**:

| Capa | Para quién | Dónde vive | Qué dice |
|---|---|---|---|
| **Pública** | Todo el mundo | Portada y primeras diapositivas de cada carrusel, posts sueltos, stories | El plástico que sacamos del Mediterráneo vuelve a tu ciudad convertido en un banco |
| **Decisor** | Ayuntamientos y compra pública | Últimas diapositivas del carrusel, carrusel de LinkedIn, textos de LinkedIn | Pliego, plazos, precio por volumen, trazabilidad, contacto |

El carrusel es el formato que permite las dos cosas a la vez: **gancho
compartible al principio, sustancia administrativa en la cola.** Quien no es
ayuntamiento se queda en la diapositiva 3 y le gusta; quien lo es llega a la 7
y escribe.

La idea central es la misma en todas las piezas:

> **Sacar el plástico es la mitad del trabajo. La otra es darle un sitio.**

No se vende un banco: se vende que la limpieza del Mediterráneo deje de ser un
gasto que se repite y se convierta en cadena de suministro. Ese reencuadre es
lo que hace la historia compartible y, a la vez, lo que le da al técnico
municipal un argumento que defender.

---

## 2. Calendario

| Semana | Día | Pieza | Canal | Formato |
|---|---|---|---|---|
| 1 | Martes 10:00 | **P01** Teaser | IG + LI | 1 imagen 4:5 |
| 1 | Todo el día | **P09** Stories 1 | IG | 3 stories |
| 1 | Viernes 13:00 | **P02** El bucle en tres pasos | IG | Carrusel 4 |
| 2 | Martes 10:00 | **P03** Carrusel héroe ← *la pieza principal* | IG + LI | Carrusel 8 |
| 2 | Viernes 13:00 | **P04** Manifiesto | IG + LI | 1 imagen 4:5 |
| 3 | Martes 10:00 | **P05** El catálogo pieza a pieza | IG | Carrusel 7 |
| 3 | Jueves 19:00 | **P06** Los doce acabados | IG | 1 imagen 1:1 |
| 4 | Miércoles 09:00 | **P07** Cómo lo compra un ayuntamiento | LI | Documento PDF 6 pág. |
| 4 | Viernes 09:00 | **P08** Post de fundadora | LI (perfil de Amaia) | 1 imagen 4:5 |
| — | Cuando entre un municipio | **P10** Plantilla por municipio | IG + LI | 1 imagen 4:5 |

**Reparto por canal.** Instagram lleva el peso del relato (6 piezas);
LinkedIn lleva la conversión (el documento B2G y el post de fundadora, más las
piezas compartidas). El documento de LinkedIn es el formato con más alcance
orgánico en administración pública, y es el único que va solo a ese canal.

**Cadencia.** Dos posts por semana en el feed, más stories el día de cada
post. Cuatro semanas sostenidas rinden más que diez piezas en una.

---

## 3. Las piezas

Los **textos completos de cada pieza, en las dos voces**, están en
`kit-creatividades.html` justo debajo de sus imágenes, y en
`tools/copys.py` para copiar y pegar.

| Código | Pieza | Tableros | Medida |
|---|---|---|---|
| P01 | Teaser · «Este banco estuvo en el fondo del mar» | 1 | 1080×1350 |
| P02 | El bucle: sale del mar → material → tu ciudad | 4 | 1080×1350 |
| P03 | Carrusel héroe de lanzamiento | 8 | 1080×1350 |
| P04 | Manifiesto · «La otra mitad del trabajo» | 1 | 1080×1350 |
| P05 | El catálogo pieza a pieza, con precio | 7 | 1080×1350 |
| P06 | Los doce acabados Gravitec® | 1 | 1080×1080 |
| P07 | Cómo un ayuntamiento lo compra | 6 | 1200×1200 |
| P08 | Tarjeta de cita para el post de fundadora | 1 | 1200×1500 |
| P09 | Stories: teaser, encuesta y llamada a la acción | 3 | 1080×1920 |
| P10 | Plantilla reutilizable por municipio | 1 | 1080×1350 |

**El carrusel héroe (P03) en detalle** — es donde ocurren las dos capas:

1. Portada: mobiliario urbano hecho con el plástico del Mediterráneo
2. El problema, con su fuente a la vista
3. Qué es Gravitec®
4. El catálogo de un vistazo
5. Los doce acabados
6. Trazabilidad
7. **Lo que se lleva un municipio** ← la carga útil para ayuntamientos
8. Llamada a la acción

---

## 4. Enlaces y medición

El embudo ya tiene su esquema de UTMs (`hubspot/README.md`); las piezas usan
el mismo, de modo que cada lead entra etiquetado en HubSpot y se puede leer el
canal en el informe del lunes.

```
Instagram  ?utm_source=instagram&utm_medium=social&utm_campaign=mobiliario-2026
LinkedIn   ?utm_source=linkedin&utm_medium=social&utm_campaign=mobiliario-2026
```

Ponlas en el enlace de la biografía de Instagram, en la pegatina de enlace de
las stories y en los enlaces de los textos de LinkedIn. La propiedad
`canal_origen` del contacto se rellena con ellas.

**Qué mirar, por orden de importancia:** mensajes directos y comentarios de
ayuntamientos > leads con `canal_origen` de redes en el pipeline > guardados y
compartidos de P06 y P03 > alcance. El alcance es el medio, no el objetivo:
la campaña gana si entran negocios en «Lead mobiliario».

**Respuesta a mensajes.** A todo el que pregunte, la misma frase, que es la
promesa que ya está en el embudo: *«Decidnos municipio, pieza y acabado y os
mandamos propuesta y mockup de vuestra pieza en 24 h, sin compromiso.»*
Eso crea el negocio en «Lead mobiliario» y arranca el reloj de un día.

---

## 5. Antes de publicar

Cuatro cosas que hay que cerrar. Todas están señaladas en el kit, en la nota
turquesa de su pieza.

1. **Fotos de misión.** P02 diapositiva 1 y P10 llevan hueco marcado para una
   foto real (red o cabo bajo el agua; pieza instalada en el municipio). Todo
   lo demás usa fotografía real de producto.
2. **La cifra de 229.000 t/año** (P03 diapositiva 2) es de UICN, «The
   Mediterranean: Mare Plasticum», 2020, y va con la fuente impresa en la
   propia pieza. Confirmadla contra vuestro informe de impacto antes de
   publicar; si preferís usar vuestro propio dato de kilos retirados, se
   cambia en `piezas.py`.
3. **Los precios** (P05 y P07) son los del catálogo Ocean Originals, IVA no
   incluido. Comprobad que la tarifa sigue vigente. Si preferís no publicar
   precio, se quita la pastilla y la tabla y se regenera.
4. **El texto de P08** es un borrador para que Amaia lo reescriba en su voz.
   La cita no está atribuida a nadie en la imagen, a propósito.

Y una decisión que conviene que veáis: la foto real de la **Mesa Palaia**
(P05) es de una instalación con sillas de patas doradas, y ese es el único
tono cálido de toda la campaña. La revisión automática lo marca como aviso.
Se ha dejado porque es la foto real de la pieza instalada; si preferís cero
tono cálido, sustituid `assets/fotos/mesa-palaia.jpg` y regenerad.

Y la plantilla **P10** lleva los campos entre corchetes: `[MUNICIPIO]`, `[N]`,
`[ubicación]`, `[X] kg`. Sustituidlos antes de publicar.

---

## 6. Qué hay en esta carpeta

```
kit-creatividades.html     el kit completo con las 33 piezas y sus textos
png/                       las 33 piezas en PNG, a tamaño real de píxel
carrusel-linkedin-ayuntamientos.pdf   P07 listo para subir como documento
assets/                    wordmark, fotos de producto y los 12 acabados
tools/                     el generador (ver README.md)
```

`kit-creatividades.html` es un solo archivo, sin dependencias externas: se
abre en cualquier navegador y se puede mandar por correo o proyectar en una
reunión.
