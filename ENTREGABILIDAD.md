# Entregabilidad: por qué no llegan los correos y cómo se arregla

Escrito el 21/09/2026, a partir de los datos de Apollo, el buzón de Google
Workspace y los DNS de `thegravitywave.com`. Todo lo que hay aquí está
comprobado; lo que es suposición va marcado como tal.

---

## Resumen en diez líneas

1. **La alerta de Google no va de nuestra campaña.** Es una alerta de correo
   *entrante*: Irene marcó como spam 6 correos que **recibió**. No dice nada
   de lo que enviamos. Ver [§1](#1-la-alerta-de-google-no-dice-lo-que-parece).
2. **El problema real está en los números de Apollo**, y son dos: **13,5 % de
   rebotes duros** y **1 apertura de 64 entregados**.
3. **No hay DKIM.** El dominio no tiene publicada la clave de Google
   Workspace. Esto es gratis de arreglar y es la mayor palanca que tenemos.
4. **Nada más de correo en frío desde `thegravitywave.com`.** Cualquier
   otro envío comercial que salga del dominio corporativo (de `info@` o de
   quien sea) comparte reputación con los correos de Amaia. Queda fuera de
   este documento, pero no del problema.
5. **Crear un subdominio de envío es la decisión correcta**, pero un
   subdominio no aísla tanto como creemos: para correo en frío conviene un
   **dominio aparte**. Ver [§4](#4-la-arquitectura-de-dominios).
6. **Reenviar toda la lista desde cero, tal cual, sería el peor movimiento
   posible.** Ver [§5](#5-lo-que-no-hay-que-hacer).
7. **Actualización de la tarde:** la secuencia está en pausa manual desde
   las 06:09, el puente tenía dos bugs que afectaban al reinicio (ya
   arreglados) y las tres decisiones pendientes están tomadas. Ver
   [§8](#8-actualización-2109-tarde-lo-que-se-ha-hecho-y-lo-que-se-ha-decidido).

---

## 1. La alerta de Google no dice lo que parece

La alerta del 15/09 dice, literalmente:

> 6 message(s) were reported as spam **by users in your domain**. There was 1
> recipient(s). Reported by: irene@thegravitywave.com (×6)

Es la alerta de **«un remitente externo nos ha escrito y nuestros usuarios lo
han marcado como spam»**. No es «Google ha detectado que tu dominio envía
spam» —esa es otra alerta distinta, y no la hemos recibido.

Lo confirma la alerta hermana del 16/09, del mismo tipo, que **sí nombra al
remitente**:

> Actor: celia.rodriguez@itc.uji.es · Reported by: alvaro@thegravitywave.com

Las seis denuncias de Irene tienen todas la **misma marca de tiempo**
(10:56:17), o sea que seleccionó seis correos del mismo remitente y pulsó
«Marcar como spam» una vez. Es limpieza de bandeja de entrada normal. El
«Severity: HIGH» es la etiqueta estándar de Google para este tipo de aviso,
no un juicio sobre nosotros.

**Qué hacer con esto:** nada urgente. Si se quiere cerrar del todo, en
*Alert Center* de la consola de administración se ve el remitente concreto
que Irene reportó. Merece la pena mirarlo **solo** para descartar que fuese
`amaia@` o `info@` (sería rarísimo, porque ninguna de las dos campañas
escribe a `irene@thegravitywave.com`, pero es un minuto).

> **Conclusión:** la alerta no es el motivo para rehacer la campaña. Los
> motivos son los del §2.

---

## 2. Los números reales

### Campaña A — `OUTBOUND · Mobiliario Urbano — Ayuntamientos` (Apollo)

Recuento por estado de la propia Apollo, a 21/09:

| Estado | Nº | Sobre |
|---|---|---|
| Total en la secuencia | 76 | |
| Enviados | 74 | |
| **Rebotados** | **10** | **13,5 % de los enviados** |
| No enviados (otros fallos) | 2 | |
| Entregados | 64 | |
| **Abiertos** | **1** | **1,6 % de los entregados** |
| Respondidos | 1 | 1,6 % |
| Clics | 0 | |
| Bajas | 0 | |

La ficha de la secuencia muestra 3 aperturas y 3 respuestas sobre 68
entregados; el recuento por mensaje de arriba es el que desglosa Apollo
mensaje a mensaje y es el que se ha usado aquí. En cualquiera de las dos
lecturas las conclusiones no cambian.

**Los 10 rebotes son todos del paso 1, variante A**, y 8 de ellos son
`hard_bounce`. Se concentran entre el 15 y el 18/09 — exactamente los días en
que el tope diario subió de 6 a 30. Los `contact_id` son casi todos
correlativos (`6a9832a301a939...`), es decir: **vienen del mismo CSV**.

> El README del puente ya avisaba de esto el 16/09 con 2 rebotes de 54
> (3,7 %). Tres días después van 10 de 74 (13,5 %). La proyección era
> correcta y se quedó corta.

### Qué significan estos números (y qué no)

**El 13,5 % de rebotes es el dato grave y no admite interpretación.** Apollo
avisa a partir del 3 % y **pausa la secuencia sola al 4 %** pasados 200
envíos. Google lee «este remitente escribe a buzones que no existen» como una
de las señales más fuertes de lista comprada o raspada. Es, con diferencia,
lo que más nos está costando.

**El 1,6 % de aperturas es peor de lo que es.** Hay que decirlo con
honestidad: el seguimiento de aperturas es un píxel de imagen, y **los
sistemas de correo de los ayuntamientos bloquean imágenes remotas casi
siempre** (Microsoft 365 con directivas estrictas, correo de diputación,
etc.). Una tasa de apertura del 1,6 % contra sector público **no demuestra**
que todo esté en spam.

**El dato que sí informa es la respuesta: 1,6 %–4,4 %.** Para correo en frío
a administración pública, eso está dentro de lo normal (la horquilla
habitual es 1–5 %). Si absolutamente todo estuviera en la carpeta de spam,
la tasa de respuesta sería 0.

> **Lectura honesta:** la colocación en bandeja está degradada, seguro. Pero
> la campaña **no** es el fracaso total que sugiere el 1,6 % de aperturas.
> Algo está llegando. Esto importa, porque cambia el plan: no hace falta
> quemarlo todo, hace falta arreglar la lista y la autenticación.

---

## 3. El estado técnico del dominio

Comprobado por DNS el 21/09.

| Registro | Estado | Veredicto |
|---|---|---|
| **MX** | Google Workspace | Correcto |
| **SPF** | `v=spf1 ip4:213.158.86.32 ip4:51.178.3.36 include:_spf.webempresa.eu +a +mx +include:_spf.google.com ~all` | Pasa, pero sucio |
| **DKIM** | **No existe `google._domainkey`** | **Roto** |
| **DMARC** | `v=DMARC1; p=quarantine; pct=5; rua=mailto:julen@` | A medio hacer |

### DKIM — esto es lo primero que hay que arreglar

**`google._domainkey.thegravitywave.com` no existe.** El único selector
publicado es `default._domainkey` (clave RSA de 2048 bits), que es el
selector que genera automáticamente el hosting tipo cPanel/Webempresa, **no**
el de Google Workspace (cuyo selector por defecto en la consola es `google`).

Consecuencia: cuando Gmail envía nuestro correo, al no haber clave propia
publicada lo firma con su clave genérica de respaldo, cuyo dominio es
`...gappssmtp.com`. Esa firma **es válida pero no alinea** con
`thegravitywave.com`, así que **DMARC solo nos pasa por SPF**. Para un
dominio que además está mandando correo en frío, eso es justo lo que hace que
los receptores desconfíen.

Es gratis, se tarda diez minutos y es **la mayor palanca individual** que
tenemos.

> ⚠️ **Antes de tocar nada, confirmar en la consola** (Apps › Google Workspace
> › Gmail › *Autenticar correo*) si el DKIM está activado y con qué selector.
> Es remotamente posible que alguien lo configurara con el selector `default`
> y esté funcionando. Un minuto de comprobación.

### SPF — funciona, pero hay que limpiarlo

- **`+a` y `+mx` sobran.** `+mx` autoriza a enviar en nuestro nombre a los
  servidores de *entrada* de Google, que no envían nada nuestro. Es superficie
  regalada sin ninguna ganancia.
- **Consumo de consultas DNS: ~7 de las 10 permitidas** (`a`=1, `mx`=1,
  `_spf.webempresa.eu`=1+3 anidados, `_spf.google.com`=1). No estamos rotos,
  pero no queda margen: **si añadimos una herramienta de envío más, lo
  reventamos** y el SPF empieza a fallar entero (`permerror`).
- El `~all` final (softfail) es correcto. No tocarlo todavía.

Propuesta: `v=spf1 ip4:213.158.86.32 ip4:51.178.3.36 include:_spf.webempresa.eu include:_spf.google.com ~all`

### DMARC — a medio desplegar

`p=quarantine` con **`pct=5`** significa que solo se aplica al 5 % del correo
que falla. Es un despliegue que alguien empezó y no terminó. Además los
informes (`rua`) van a `julen@` y —hay que preguntarle— probablemente nadie
los está leyendo, que es donde estaría escrito todo esto desde hace semanas.

Orden correcto: **primero DKIM**, dejar reposar una semana mirando los
informes, y **luego** subir `pct` a 25 → 50 → 100. Subir la aplicación antes
de tener DKIM alineado es pegarse un tiro en el pie.

---

## 4. La arquitectura de dominios

La intuición es correcta: **el correo en frío no debe salir del dominio que
usan los empleados**. Pero conviene afinar el cómo.

### Subdominio vs. dominio aparte

Un subdominio (`send.thegravitywave.com`) **no aísla tanto como parece**.
Google y Microsoft propagan parte de la señal de reputación a nivel de
*dominio organizativo*, así que un subdominio quemado sí puede arrastrar al
dominio padre. Ayuda, pero no es un cortafuegos.

**Un dominio aparte sí lo es**, y es lo estándar para outbound en frío:

| Opción | Aísla | Coste | Cuándo |
|---|---|---|---|
| Enviar desde `thegravitywave.com` | Nada | 0 € | Nunca para correo en frío |
| Subdominio `send.thegravitywave.com` | Parcial | 0 € | Boletines, transaccional |
| **Dominio aparte** (`gravitywave.es`, `hablemos-gravitywave.com`…) | **Total** | ~10 €/año | **Correo en frío** ✅ |

**Recomendación:** un dominio aparte, con redirección 301 a la web
principal, con su propio Workspace/buzón, su SPF, su DKIM y su DMARC. Que se
parezca a la marca y no parezca un desechable.

### Reparto propuesto

| Dominio | Para qué |
|---|---|
| `thegravitywave.com` | Correo de empleados, respuestas, INBOUND de la web, transaccional, clientes. **Nunca** correo en frío |
| Dominio aparte | Campaña de ayuntamientos (Amaia) |

Si algún día hay otra campaña en frío, va en **otro** dominio aparte: que
una no pueda quemar a la otra es exactamente el objetivo.

### Nada de esto funciona sin calentamiento

Un dominio nuevo tiene **reputación cero**, que no es lo mismo que buena
reputación. Si se le enchufan 30 correos diarios el primer día, se quema en
una semana. El calentamiento no es opcional:

| Semana | Correos/día | Qué se hace |
|---|---|---|
| 0 | 0 | DNS publicados (SPF, DKIM, DMARC), buzón creado, firma puesta |
| 1 | 5–10 | Correos reales a gente conocida que **responda** |
| 2 | 10–20 | Se mezclan los primeros contactos en frío |
| 3 | 20–30 | Campaña a ritmo bajo |
| 4+ | 30–50 | Ritmo de crucero, vigilando rebotes |

Son **3–4 semanas antes de estar a pleno rendimiento**. Conviene asumirlo en
la planificación desde hoy en lugar de descubrirlo a mitad.

---

## 5. Lo que NO hay que hacer

### No reenviar la lista entera desde cero tal cual

Es el plan que teníamos y es el que más daño haría. Tres motivos:

1. **La lista sigue sucia.** De los 137 contactos, 10 ya han rebotado y la
   proyección dice que quedan más sin descubrir. Mandar eso desde un dominio
   nuevo y sin reputación **lo quema en días** — un dominio nuevo con 13 % de
   rebotes es un dominio muerto.
2. **A los ayuntamientos ya contactados les llegarían los mismos correos otra
   vez**, ahora desde una dirección distinta. Para quien sí recibió el primero
   (y algo llegó: hubo respuestas) eso es exactamente lo que parece spam, y
   sube el riesgo de denuncia justo cuando menos nos lo podemos permitir.
3. **Perderíamos las 1–3 conversaciones abiertas**, que es lo único que ha
   funcionado.

### Tratamiento correcto de la lista

| Segmento | Qué hacer |
|---|---|
| Rebotados (10) | **Fuera, y no volver.** Marcar en HubSpot para que no reentren |
| Respondieron (1–3) | Fuera de la secuencia, seguimiento **a mano** desde el dominio principal |
| Ya contactados sin respuesta | Marcar como «tocados». Esperar **4–6 semanas** y reabordar con copy distinto que reconozca el contacto previo |
| Sin contactar | Verificar → calentar → enviar desde el dominio nuevo |

### No verificar la lista es innegociable

Con un verificador (NeverBounce, ZeroBounce, Bouncer; ~10 € por 1.000
direcciones) se pasan los 137 antes de enviar nada. **Objetivo: bajar del
2 % de rebotes.** Es el paso más barato de toda esta lista y el que más
rebote evita.

---

## 6. El correo en sí

### La campaña de ayuntamientos: el texto está bien, el HTML no

El cuerpo es bueno y conviene no tocarlo: corto, personalizado con
`{{municipio}}`, prueba social local y concreta (Calpe, Dénia, Benidorm),
salida fácil («con un "ahora no" me vale»), petición de reenvío interno, y un
pie legal RGPD/LSSI correcto con baja por respuesta. Eso está bien hecho.

El problema es **la firma de Apollo**, que mete una tabla HTML con **cuatro
imágenes remotas** alojadas en `googleusercontent.com` (un logo de 131×129,
otro de 71×71 y tres iconos sociales de 20 px). Dos consecuencias:

- **La firma pesa unas diez veces más que el mensaje.** La proporción
  texto/HTML queda fatal, que es una señal clásica de filtrado.
- Contra buzones que bloquean imágenes remotas —o sea, casi todos los
  ayuntamientos— **se ve rota**, con cuatro recuadros vacíos.

**Propuesta:** en el paso 1, firma de texto plano (nombre, cargo, teléfono,
web como enlace de texto). La firma con imágenes se deja para cuando ya hay
conversación. En una primera toma de contacto en frío, cuanto más se parezca
a un correo escrito a mano, mejor llega.

Dos detalles menores más:

- **`Hola,` a secas**, sin nombre, porque las direcciones son de cargo
  (`ajuntament@`, `alcalde@`). Es coherente, pero conviene buscar nombre y
  dirección nominal donde se pueda: llega mejor y responde más.
- **El enlace a `meetings-eu1.hubspot.com`** es un dominio compartido de
  ventas muy reconocible. En el paso 1 se puede quitar (el «responde y te
  cuento» ya es CTA suficiente) y dejarlo para el paso 2 o 3.

### Cabecera de baja en un clic

La secuencia no lleva `List-Unsubscribe`. Con nuestro volumen
(muy por debajo de 5.000/día) Google **no** lo exige, así que no es urgente
—pero ayuda, y es lo que separa a un remitente que parece profesional de uno
que no. Apollo lo puede añadir solo.

---

## 7. El plan, en orden

### Ahora (esta semana, coste ~0 €)

| # | Qué | Quién | Por qué |
|---|---|---|---|
| 1 | **Que no salga ningún otro correo en frío desde `thegravitywave.com`** | Todos | Comparte reputación con los de Amaia |
| 2 | **Activar DKIM** en Workspace y publicar `google._domainkey` | Admin | La mayor palanca, gratis, 10 min |
| 3 | **Limpiar el SPF** (quitar `+a` y `+mx`) | Admin | Deja margen de consultas DNS |
| 4 | **Sacar los 10 rebotados** de la lista y marcarlos en HubSpot | Puente | Que no vuelvan a entrar |
| 5 | **Leer los informes DMARC** que le llegan a Julen | Julen | Llevan semanas contando esto |
| 6 | **Dar de alta en Google Postmaster Tools** | Admin | Es la única forma de ver de verdad nuestra reputación |
| 7 | Confirmar en *Alert Center* quién es el remitente que reportó Irene | Admin | Cerrar la duda del §1 |

> La secuencia de ayuntamientos ya está en pausa (`active: false`). Que siga
> así hasta tener el 2 y el 4 hechos.

### A continuación (semanas 1–2, ~50 €)

8. **Comprar el dominio de outbound** y configurarlo entero: SPF, DKIM,
   DMARC (`p=none` al principio, para observar), redirección 301 a la web.
9. **Verificar los 137 contactos** con un verificador de correo.
10. **Empezar el calentamiento** del buzón nuevo según la tabla del §4.
11. **Rehacer el paso 1** con firma de texto plano y sin el enlace de HubSpot.

### Después (semanas 3–4)

12. Reconectar el puente Apollo↔HubSpot al buzón nuevo.
13. Reanudar con **6/día** —el tope que ya estaba— y **no subirlo** hasta
    tener dos semanas seguidas por debajo del 2 % de rebotes.
14. Reabordar a los «tocados» con copy nuevo, pasadas 4–6 semanas.

### Los números que hay que vigilar

| Métrica | Objetivo | Alarma |
|---|---|---|
| Rebotes | < 2 % | > 3 % → parar y verificar |
| Denuncias de spam (Postmaster) | < 0,1 % | > 0,3 % → parar del todo |
| Respuestas | > 3 % | < 1 % sostenido → el copy o la lista |
| Aperturas | *no fiarse* | — (el sector público bloquea el píxel) |

---

## 8. Actualización 21/09 (tarde): lo que se ha hecho y lo que se ha decidido

### Lo que ha aparecido al bajar al detalle

**La secuencia está en pausa manual desde hoy a las 06:09 UTC**
(`status_reason: manual_pause`). Bien: es lo que había que hacer. Pero el
puente inscribió 6 ayuntamientos más a las 09:33 (Calonge, Calvià,
Castelló, Nules, Altea, Xilxes): están en HubSpot como «enviado» y con
negocio en «Información enviada» sin que les haya salido un correo. Cuando
se reanude la secuencia sí les llegará —Apollo los tiene en `paused`—, pero
si se decide **no** reanudar esta secuencia (que es lo recomendado, ver
abajo), esos 6 hay que reasignarlos a mano.

**HubSpot tiene 0 contactos «rebotado» y Apollo tiene 10.** El paso
REBOTES del puente nunca ha funcionado: Apollo no escribe el rebote en el
contacto y además saca de la lista al que rebota, así que el puente,
recorriendo la lista, no los veía. Está arreglado (se leen de los mensajes
de la secuencia, que es donde Apollo los guarda). En la próxima pasada real
esos 10 quedarán marcados y sus negocios saldrán del pipeline con el motivo
correcto en vez de acabar como «Sin respuesta».

**Los 128 contactos de la lista con estado figuran como `verified` en
Apollo.** Incluidos, presumiblemente, los 10 que rebotaron. Es decir: la
«verificación» de Apollo no sirve para direcciones municipales raspadas de
webs. Hay que pasar un verificador de verdad antes de inscribir a nadie.

**Los pasos 2 y 3 de la secuencia tienen dos cosas más que quitar:**

- Paso 2 lleva una **imagen de 560 px** (las letras de Benidorm) incrustada.
  En un seguimiento en frío sigue siendo una señal de filtrado y contra
  buzones que bloquean imágenes se ve un hueco. Mejor un enlace de texto a
  la foto.
- Paso 3 enlaza el catálogo con un **acortador** (`canva.link/…`). Los
  acortadores son de las señales de spam más fuertes que hay, porque es lo
  que usa el phishing. Sustituir por la URL completa del PDF en la web.

### Las decisiones, tomadas

**1. Dominio aparte, no subdominio.** Por lo del §4: un subdominio arrastra
al padre. Diez euros al año no son un motivo para no hacerlo bien.

**2. Un dominio solo para esta campaña.** Nada más sale de él, y ningún
otro correo en frío sale de `thegravitywave.com`.

**3. La secuencia actual no se reanuda.** Se crea una nueva en el dominio nuevo, con los pasos
corregidos (firma de texto, sin acortador, sin imagen en el paso 2, sin el
enlace de HubSpot en el paso 1) y con la lista verificada. La actual se
deja pausada como archivo. Motivo práctico: su 13 % de rebotes acumulado es
lo que el cortacircuito nuevo mira, y arrastrarlo obligaría a desactivar el
freno justo cuando más falta hace.

### Lo que queda en vuestra mano (por orden)

| # | Qué | Dónde | Tiempo |
|---|---|---|---|
| 1 | Activar DKIM y limpiar el SPF | `dns/README.md` §1, pasos 1 y 2 | 15 min |
| 2 | Alta en Postmaster Tools | `dns/README.md` §1, paso 4 | 5 min |
| 3 | Comprar el dominio y crear el buzón | `dns/README.md` §2 | 30 min + espera DNS |
| 4 | Verificar los 137 con un verificador (NeverBounce, ZeroBounce, Bouncer) | CSV | 10 € |
| 5 | Poner `OUTBOUND_SENDER_EMAIL` en las variables del repo cuando el buzón nuevo esté en Apollo | GitHub › Settings › Variables | 1 min |
| 6 | Crear la secuencia nueva con los pasos corregidos | Apollo | 30 min |
| 7 | Calentar el buzón 3 semanas | tabla del §4 | — |
| 8 | Cambiar `SEQ_OUTBOUND` y `LIST_OUTBOUND` en el puente a la secuencia y lista nuevas | `bridge/apollo_hubspot_bridge.py` | 1 min |

El 1 y el 2, hoy. Del 3 al 5, esta semana. El 6 y el 7 corren en paralelo. El
8, el día que se reanude.

---

## Apéndice: comprobaciones

```bash
# DKIM (hoy: vacío — este es el problema)
dig +short TXT google._domainkey.thegravitywave.com

# SPF
dig +short TXT thegravitywave.com | grep spf1

# DMARC
dig +short TXT _dmarc.thegravitywave.com
```

Para probar un correo antes de una campaña: enviarlo a
[mail-tester.com](https://www.mail-tester.com) (puntúa sobre 10 y desglosa
autenticación, contenido y listas negras) y comprobar la cabecera
`Authentication-Results` en un Gmail de prueba — debe decir `dkim=pass` con
`header.d=` **de nuestro dominio**, no de `gappssmtp.com`.
