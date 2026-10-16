# Seguimiento de aperturas propio

Apollo solo ofrece seguimiento de aperturas en los planes Professional y
Organization; la cuenta de Gravity Wave está en Free. Así que se mide igual
que lo haría Apollo, pero con piezas propias:

| Pieza | Dónde | Qué hace |
|---|---|---|
| Píxel | Al final de los cinco correos de la secuencia OUTBOUND | `<img src="<URL>?c={{tracking_id}}&p=N" width="1" height="1">`. `{{tracking_id}}` es un campo personalizado de Apollo que el puente rellena con el id del contacto; `N` es el número de correo (1-5) |
| Receptor | `aperturas.gs`, publicado como aplicación web de Google Apps Script en la cuenta de Google de Gravity Wave | Apunta fecha, contacto y paso en la hoja «Aperturas · Mobiliario Urbano» (se crea sola en Drive) |
| Lector | Fase **APERTURAS** de `bridge/apollo_hubspot_bridge.py` | Cada hora pide al receptor las aperturas nuevas y pasa `apollo_estado` de `enviado` a `abierto` en HubSpot |
| Relleno | Fase **TRACKING** del puente | Da `tracking_id` a todo contacto de la lista OUTBOUND que no lo tenga, y crea el campo en Apollo si no existe |

## Publicar el receptor (una vez)

Está explicado en la cabecera de `aperturas.gs`. En corto: script.google.com →
nuevo proyecto → pegar el archivo → Implementar → Aplicación web, ejecutar
como «Yo», acceso «Cualquier usuario» → copiar la URL `/exec`.

Esa URL va en `APERTURAS_URL` del workflow, y la clave `CLAVE` del script tiene
que coincidir con `APERTURAS_KEY`. Hasta que la URL esté puesta, la fase
APERTURAS no hace nada y lo dice en el log.

## Qué mide y qué no

- Mide **menos de lo real, nunca más**: un correo leído con las imágenes
  bloqueadas (Outlook en muchos ayuntamientos) no se registra. Es la misma
  limitación que tiene el tracking de Apollo o de cualquier herramienta.
- Gmail y Apple Mail a veces descargan las imágenes antes de que nadie abra
  el correo. El puente ignora las aperturas registradas en los **90 segundos**
  siguientes al envío cuando conoce la hora de envío.
- El píxel pasa por `script.google.com`, no por el dominio de Gravity Wave,
  así que no toca la reputación de `thegravitywave.com`.
- No se guarda la IP del lector: Google no la expone y tampoco hace falta.

## Orden para encender

1. El puente, en su primera pasada tras fusionar esto, crea el campo
   `tracking_id` en Apollo y lo rellena en los ~135 contactos de la lista
   (fase TRACKING). Se comprueba en el log: `TRACKING: N contacto(s) con
   tracking_id nuevo`.
2. Alguien publica `aperturas.gs` y pega la URL.
3. Se añade el píxel a las cinco plantillas **solo cuando todos los
   contactos en cadencia tienen `tracking_id`**: si a alguno le faltara,
   Apollo no le enviaría el correo (variable vacía).
4. Se despausa la secuencia.
