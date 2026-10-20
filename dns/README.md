# Salud del dominio `thegravitywave.com`

Auditoría del 20/10/2026 y los cambios que faltan para que el correo de
Gravity Wave (Gmail/Apollo, HubSpot y la web) salga autenticado al 100 %.
El porcentaje de «salud del dominio» del panel suma 25 SPF + 25 DKIM propio
(10 si firma Google con su clave) + 20 DMARC (10 si `pct<100`) + 20 rebotes
+ 10 sin spam; la parte DNS vale 70 y hoy da **45**.

## Quién tiene las llaves

| Qué | Dónde | Quién |
| --- | --- | --- |
| Registro del dominio (.com y .es) | GoDaddy | Titular Abora World S.L.L. / Julen Rodríguez. **El .com caduca el 21/10/2026** (RDAP del 20/10: sin renovar todavía). |
| DNS (zona) | Cloudflare, nameservers `kristina` y `plato` | Cuenta de **Appgile** (Tomix, `tcorralb@appgile.com`). Migrado desde el cPanel de Webempresa el 7/10/2026. Gravity Wave no tiene usuario ni token. |
| Hosting web y buzones del .es | Webempresa (cPanel, `213.158.86.32`) | `norberto@` |
| Google Workspace (DKIM de Gmail) | admin.google.com | Un administrador del Workspace (Norberto o Julen). |
| HubSpot (portal 26243090) | HubSpot → Dominios | Equipo. Ya conectado. |

Los cambios de DNS los pide Gravity Wave a Appgile (requisito en Appgile o
correo a Tomix). El DKIM de Google solo lo puede generar un administrador
del Workspace.

## Estado el 20/10/2026

| Registro | Hoy | Problema |
| --- | --- | --- |
| MX | Google Workspace | — Correcto. |
| SPF | `v=spf1 ip4:213.158.86.32 ip4:51.178.3.36 include:_spf.webempresa.eu +a +mx +include:_spf.google.com ~all` | Funciona, pero lleva tres mecanismos redundantes (`ip4:213.158.86.32` y `+a` están dentro de `_spf.webempresa.eu`; `+mx` es Google, ya incluido). 7 consultas DNS de 10 posibles. |
| DKIM `google._domainkey` | **no existe** | Gmail firma con `thegravitywave-com.20251104.gappssmtp.com` (lo confirma Apollo). La firma no está alineada con el dominio: pasa DMARC solo porque SPF alinea, y se rompe en reenvíos y listas. Es lo que más resta. |
| DKIM `default._domainkey` | existe (2048 bits) | Clave del servidor de Webempresa (cPanel). Firma lo que manda la web. Se deja. |
| DKIM HubSpot | `hs1-26243090._domainkey` y `hs2-26243090._domainkey` → `hubspotemail.net` | Correcto: HubSpot firma con el dominio y alinea. (El puente no lo mira porque no puntúa.) |
| DMARC | `v=DMARC1; p=quarantine; pct=5; rua=mailto:julen@thegravitywave.com` | Solo cubre el 5 % del correo. Sin `ruf`/`fo`, sin alineación explícita. |
| TLS-RPT, MTA-STS, BIMI | no existen | Opcionales; cuentan en algunos verificadores. |
| `thegravitywave.es` | SPF Webempresa, DKIM cPanel, DMARC `p=none` | Los buzones del .es viven en Webempresa (`mail.thegravitywave.es`). DMARC sin política. |
| `store.thegravitywave.com` | SPF y DKIM propios de cPanel, sin DMARC | Tienda de los QR. Hereda la DMARC del dominio raíz, bien. |

Quién envía con el dominio hoy:

- **Google Workspace** (todos los buzones, y Apollo a través de `amaia@`).
- **HubSpot** marketing (desde `norberto@`, `amaia@`, `info@`, `julen@`…):
  1.516 entregados en mayo, 3.940 en julio. DKIM alineado.
- **Webempresa** (`213.158.86.32`): el WordPress de la web y la tienda.
- `51.178.3.36` (OVH, sin PTR): no sabemos qué es. Se mantiene en el SPF
  hasta identificarlo; si en un mes los informes DMARC no lo muestran
  enviando, se quita.

## Qué hay que hacer, en orden

### 0. Renovar el dominio (hoy)

`thegravitywave.com` caduca el **21/10/2026 a las 17:55** (hora
peninsular). Si GoDaddy no lo renueva, cae la web y todo el correo del
dominio. Comprobar en GoDaddy (cuenta de Abora World / Julen) que la
renovación automática está activa o renovarlo a mano.

### 1. DKIM propio en Google Workspace (25 puntos)

1. [admin.google.com](https://admin.google.com) → Aplicaciones → Google
   Workspace → Gmail → **Autenticar correo electrónico**.
2. Dominio `thegravitywave.com` → **Generar registro nuevo**: longitud de
   clave **2048**, prefijo del selector **`google`** (el que mira el puente).
3. Copiar el valor `v=DKIM1; k=rsa; p=MIIB…` y pasárselo a Appgile para que
   lo cree en Cloudflare como TXT en `google._domainkey` (o
   `aplicar-cloudflare.sh dkim '<valor>'` si alguien tiene token).
4. Cuando el TXT resuelva (10–60 min), pulsar **Iniciar autenticación** en
   el mismo sitio del Admin. Hasta entonces Gmail sigue firmando con la
   clave de `gappssmtp.com`, así que no se pierde nada.
5. Comprobar: enviarse un correo desde `amaia@` y en Gmail «Mostrar
   original» debe decir `DKIM: 'PASS' con el dominio thegravitywave.com`.

### 2. HubSpot

Ya conectado (verificado el 20/10). Nada que hacer.

### 3. Limpiar el SPF

Sustituir el TXT actual por:

```
v=spf1 include:_spf.google.com include:_spf.webempresa.eu ip4:51.178.3.36 ~all
```

Autoriza exactamente a los mismos emisores (Google, Webempresa y la IP de
OVH) con 5 consultas DNS en vez de 7 y sin mecanismos duplicados. HubSpot no
necesita `include` porque usa su propio dominio de sobre alineado por DKIM.
Se mantiene `~all` (softfail): con DMARC es lo que recomienda Google; `-all`
no suma y hace daño en reenvíos.

### 4. DMARC al 100 % (20 puntos)

Hoy todo el correo legítimo ya pasa DMARC (Gmail por SPF, HubSpot por
DKIM, la web por ambos), así que subir a `pct=100` es seguro. Lo ideal es
hacerlo con el DKIM de Google ya activo (paso 1), para que los reenvíos
también pasen:

```
v=DMARC1; p=quarantine; pct=100; rua=mailto:julen@thegravitywave.com; ruf=mailto:julen@thegravitywave.com; fo=1; adkim=r; aspf=r
```

Lo que cambia respecto a hoy: `pct=100` cubre todo el correo; `ruf`/`fo=1`
piden informe de cada fallo, que es lo que dirá si queda algún emisor
olvidado (la IP de OVH, algún SaaS).

Tras 2–4 semanas de informes sin fallos legítimos, pasar a rechazo:

```
v=DMARC1; p=reject; pct=100; rua=mailto:julen@thegravitywave.com; ruf=mailto:julen@thegravitywave.com; fo=1; adkim=s; aspf=s
```

Es el máximo que mide cualquier verificador. Los informes `rua` llegan como
XML adjunto a `julen@`; para leerlos cómodamente vale cualquier buzón
gratuito de informes DMARC (Postmark, dmarcian, EasyDMARC…) poniendo su
dirección en `rua` además de la nuestra.

Para el `.es`, lo mismo pero empezando por `p=quarantine; pct=100`: sus
buzones de Webempresa ya firman y alinean.

### 5. Extras (suben la nota en verificadores, no en Gmail/Outlook)

- **TLS-RPT**: TXT en `_smtp._tls` con `v=TLSRPTv1;
  rua=mailto:julen@thegravitywave.com`. Inofensivo, avisa si alguien no
  consigue entregarnos por TLS.
- **MTA-STS**: exige servir
  `https://mta-sts.thegravitywave.com/.well-known/mta-sts.txt` con la
  política (modo `testing` primero) y un TXT `_mta-sts` con `v=STSv1;
  id=<fecha>`. En Cloudflare se hace con un Worker o Pages; Appgile puede.
- **BIMI** (`default._bimi` TXT `v=BIMI1; l=https://…/logo.svg; a=`):
  solo con DMARC en `p=quarantine; pct=100` o `reject`, logo en SVG Tiny PS
  y, para que Gmail lo enseñe, un certificado VMC de pago. Yahoo y Fastmail
  lo muestran sin VMC. Se deja para después de la fase 4.

### 6. Apollo

Apollo avisa además de que el único buzón enlazado (`amaia@`) está al
límite de capacidad y pide enlazar un segundo buzón del dominio (Apollo →
Settings → Mailboxes). No afecta a la autenticación, pero sí a los retrasos
de envío de la secuencia.

## Comprobar

```
dns/comprobar.sh
```

Consulta el DNS público (dns.google, el mismo que usa el puente) y enseña
cada registro con su estado, las consultas que gasta el SPF y los puntos de
la parte DNS de la salud del panel (sobre 70). No necesita credenciales.

## Aplicar en Cloudflare

Para quien tenga la zona (Appgile) o un token con `Zone:DNS:Edit`:

```
export CF_API_TOKEN=…
dns/aplicar-cloudflare.sh spf
dns/aplicar-cloudflare.sh dkim 'v=DKIM1; k=rsa; p=MIIB…'
dns/aplicar-cloudflare.sh tlsrpt
dns/aplicar-cloudflare.sh dmarc quarantine
dns/aplicar-cloudflare.sh dmarc reject         # 2–4 semanas después
```

Cada orden crea o actualiza un registro (nunca borra otros), enseña lo que
había y lo que deja, y con `--dry-run` delante solo lo enseña. Si Appgile
crea un token limitado a la zona y lo guarda como secreto de GitHub, el
puente podría aplicar estos cambios desde Actions.
