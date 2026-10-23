# Seguimiento de aperturas propio

Apollo solo ofrece seguimiento de aperturas en los planes Professional y
Organization; la cuenta de Gravity Wave está en Free. Así que se mide igual
que lo haría Apollo, pero con piezas propias:

| Pieza | Dónde | Qué hace |
|---|---|---|
| Píxel | Al final de los cinco correos de la secuencia OUTBOUND | `<img src="<URL>?t={{tracking_id}}&p=N" width="1" height="1">`. `{{tracking_id}}` es un campo personalizado de Apollo que el puente rellena con el id del contacto; `N` es el número de correo (1-5). Va en `t` y no en `c` porque Google reserva `c` en las aplicaciones web y corta la petición |
| Receptor | `aperturas.gs`, publicado como aplicación web de Google Apps Script en la cuenta de Google de Gravity Wave | Apunta fecha, contacto y paso en la hoja «Aperturas · Mobiliario Urbano» (se crea sola en Drive) |
| Lector | Fase **APERTURAS** de `bridge/apollo_hubspot_bridge.py` | Cada hora pide al receptor las aperturas nuevas y pasa `apollo_estado` de `enviado` a `abierto` en HubSpot |
| Relleno | Fase **TRACKING** del puente | Da `tracking_id` a todo contacto de la lista OUTBOUND que no lo tenga, y crea el campo en Apollo si no existe |
| Panel | Fase **PANEL** del puente + pestaña «panel» del receptor | El puente genera la página del panel con los datos dentro y el receptor la guarda y la sirve (`?ver=1&key=…`) |

## Visitas a la landing y clics del banner (16/10)

El mismo receptor tiene una segunda pestaña, «visitas». La alimenta
`visitas-gtm.html`, un fragmento que se pega en Google Tag Manager
(contenedor `GTM-M6FNQ79`) con el activador «vista de página · Page Path
contiene /mobiliario-urbano». Guarda fecha, ruta, `utm_source`,
`utm_medium`, `utm_campaign` y el dominio que enlazó; nada de la persona.

Los **clics del banner de la home** son las visitas que llegan con
`utm_source=home&utm_medium=banner`. El botón «Descubre más» de la home
enlaza desde el 16/10 a
`https://www.thegravitywave.com/mobiliario-urbano/?utm_source=home&utm_medium=banner&utm_campaign=mobiliario-2026`
(comprobado en la home publicada). El panel lee `?visits=1&key=…` y muestra
visitas, clics del banner, origen y visitas por día.

La landing tiene dos versiones, **A con precios** (`/mobiliario-urbano/`) y
**B sin precios** (`/mobiliario-urbano-b/`): un script en la propia página
sortea la versión la primera vez, la guarda en una cookie 90 días y redirige
a la otra URL si hace falta. Como la etiqueta llega a dispararse en las dos
páginas durante esa redirección, el puente cuenta una sola visita por origen
en 90 segundos y se queda con la versión donde se queda el visitante
(`pagina` = A o B en los datos del panel). Los formularios se atribuyen a
una versión por las URL que HubSpot guarda del visitante
(`hs_analytics_last_url` y `hs_analytics_first_url`).

En marcha desde el 16/10: receptor en su versión 5, etiqueta publicada en la
versión 64 del contenedor. La vista previa de Tag Manager dispara la
etiqueta en su propia página (`/render`, referente `gtm-msr.appspot.com`);
el receptor y el panel ignoran esas filas, y también las pruebas
(`utm_source` que empieza por `prueba` o `DIAG`).

## El panel, servido desde el receptor (19/10)

El receptor tiene desde el 19/10 una tercera pestaña, «panel». Cada media
hora el puente genera la página del panel con todos los datos ya dentro
(fase PANEL, ver `bridge/README.md`) y la manda con
`POST URL?panel=1&key=CLAVE` y el cuerpo `{"html": …, "datos": …}`. El
receptor la guarda troceada (una celda no admite más de 50.000 caracteres;
cada trozo empieza por `~` para que la hoja no lo tome por una fórmula) y
la sirve:

- `URL?ver=1&key=CLAVE` — la página, para abrirla en el navegador. La clave
  va en el enlace, así que ese enlace es tan privado como la clave.
- `URL?panel=1&key=CLAVE` — JSON `{generado, html, datos}`, para quien quiera
  los datos sin la página.
- `URL?diag=1&key=CLAVE` dice ahora también cuándo se generó el panel guardado.

Hasta que se publique la versión del script con `doPost` (Implementar →
Gestionar implementaciones → lápiz → Nueva versión), el puente avisa en el
log «el receptor no acepta todavía el panel» y sigue; la página se genera
igual y se sube como artefacto cifrado de la pasada.

Por qué así y no con Google Analytics: la web lleva GA4 (`G-7LN8GNKJM8`),
pero no hay forma de leerlo desde el panel ni desde el puente (la prueba de
Supermetrics caducó el 30/09 y HubSpot no tiene su código en la web). Con
el receptor propio el dato es nuestro y gratis.

## Publicar el receptor (una vez)

Está explicado en la cabecera de `aperturas.gs`. En corto: script.google.com →
nuevo proyecto → pegar el archivo → Implementar → Aplicación web, ejecutar
como «Yo», acceso «Cualquier usuario» → copiar la URL `/exec`.

Esa URL va en `APERTURAS_URL` del workflow. La clave vive en dos sitios y
tiene que ser la misma en ambos, y **en ninguno de los dos es el código**:

- GitHub: secreto `APERTURAS_KEY` del repositorio (Settings → Secrets and
  variables → Actions → New repository secret).
- Apps Script: propiedad `CLAVE` del script (Configuración del proyecto →
  Propiedades del script).

La primera clave estuvo escrita en este repositorio público (en el
workflow y en `aperturas.gs`) hasta el 16/10; sigue en el historial de git,
por eso se cambió por otra y se sacó del código. Hasta que la URL esté
puesta, la fase APERTURAS no hace nada y lo dice en el log. Si falta el
secreto, el receptor contesta «clave incorrecta» y la fase lo dice.

`URL?diag=1&key=CLAVE` prueba cada paso del receptor (propiedad, hoja,
escritura) y dice cuál falla; añade una fila `DIAG` que el puente y el panel
ignoran.

## Qué cuenta como apertura (20/10)

Un píxel solo dice que *algo* cargó la imagen del correo; no dice quién.
Los registros del 16 al 20/10 enseñaron tres patrones, y el puente los
separa en `clasificar_aperturas()` (`bridge/apollo_hubspot_bridge.py`):

| Patrón | Qué es | Qué hace el puente |
|---|---|---|
| Carga en los 3 minutos siguientes al envío | El servidor de correo del ayuntamiento, o Gmail/Outlook, descarga las imágenes al recibir. Nadie ha leído nada | Se descarta («automática»). La hora de envío la da HubSpot, donde Apollo registra cada correo al enviarlo |
| Dos o más ayuntamientos cargan con menos de 90 s entre carga y carga | Alguien de Gravity Wave mirando los correos enviados. El domingo 18/10 a las 11:07 cargaron cuatro ayuntamientos y el correo de prueba interno en el mismo minuto; el lunes, dos con 0,4 s de diferencia | Se descarta («ráfaga»). Cualquier carga junto a una fila que no es de la lista (PRUEBA, DIAG, el correo interno) es ráfaga también |
| Carga aislada, minutos u horas después del envío | Lo más parecido a una lectura que puede medir un píxel | Cuenta como apertura creíble |

Además, un contacto cuyo correo **rebotó** no tiene ninguna carga creíble:
nadie lo ha leído. Si su píxel se carga es desde nuestro buzón, porque el
aviso de rebote que recibe Amaia lleva dentro el correo original con el
píxel (Sant Lluís, 22/10: rebote a las 12:54, carga a las 13:14).

Solo las creíbles ponen `apollo_estado = abierto` en HubSpot; si un
contacto estaba en «abierto» sin ninguna carga creíble, vuelve a «enviado».
El panel enseña las creíbles y, aparte, cuántos ayuntamientos tienen solo
cargas automáticas o internas. Ni así es una certeza: es una estimación
conservadora, y quien lee con las imágenes bloqueadas no aparece nunca.

## Qué mide y qué no

- Mide **menos de lo real, nunca más**: un correo leído con las imágenes
  bloqueadas (Outlook en muchos ayuntamientos) no se registra. Es la misma
  limitación que tiene el tracking de Apollo o de cualquier herramienta.
- Gmail y Apple Mail a veces descargan las imágenes antes de que nadie abra
  el correo. El puente ignora las cargas de los **3 minutos** siguientes al
  envío (y las de los 90 segundos siguientes a la inscripción).
- El píxel pasa por `script.google.com`, no por el dominio de Gravity Wave,
  así que no toca la reputación de `thegravitywave.com`.
- No se guarda la IP del lector: Google no la expone y tampoco hace falta.

## Orden para encender

1. ~~El puente crea el campo `tracking_id` en Apollo y lo rellena en los
   contactos de la lista (fase TRACKING)~~ — hecho el 16/10: 135 de 135,
   los 71 en cadencia incluidos. El campo es `6ad207bd5a7c2e0014573df8`.
2. ~~Alguien publica `aperturas.gs` y pega la URL~~ — publicado el 16/10;
   la URL está en el workflow. El 400 que daba el píxel no era la escritura
   sino el nombre del parámetro: Google reserva `c` en las aplicaciones web
   y la petición no llegaba al script; con `t` funciona. Versión con la
   clave en propiedades y `?diag=1` publicada el 16/10. Comprobación:
   `curl "<URL>?t=PRUEBA&p=0"` devuelve `ok` y la fila aparece en
   `?list=1&key=…`.
3. ~~Se añade el píxel a las cinco plantillas~~ — hecho el 16/10 por API,
   con el texto de los cinco correos sin cambios (comprobado byte a byte
   en `body_text`). El píxel va justo antes de `</body>`, con `p=1…5`.
4. ~~Se despausa la secuencia~~ — hecha a mano el 16/10. La pasada del
   puente de las 13:12 UTC leyó 3 aperturas reales (Badalona, Creixell y
   Elche, correo 2 del relanzamiento) y marcó los 3 contactos «abierto» en
   HubSpot. Todo encendido.
