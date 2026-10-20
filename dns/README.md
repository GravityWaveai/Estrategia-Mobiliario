# Salud del dominio `thegravitywave.com`

Auditoría del 20/10/2026 y los cambios que faltan para que el correo de
Gravity Wave (Gmail/Apollo, HubSpot y la web) salga autenticado al 100 %.
El porcentaje de «salud del dominio» del panel suma 25 SPF + 25 DKIM propio
(10 si firma Google con su clave) + 20 DMARC (10 si `pct<100`) + 20 rebotes
+ 10 sin spam; la parte DNS vale 70 y hoy da **45**.

## Estado el 20/10/2026

| Registro | Hoy | Problema |
| --- | --- | --- |
| NS | Cloudflare (`kristina`, `plato`) | — Los cambios se hacen en el panel de Cloudflare. |
| MX | Google Workspace | — Correcto. |
| SPF | `v=spf1 ip4:213.158.86.32 ip4:51.178.3.36 include:_spf.webempresa.eu +a +mx +include:_spf.google.com ~all` | Funciona, pero lleva tres mecanismos redundantes (`ip4:213.158.86.32` y `+a` están dentro de `_spf.webempresa.eu`; `+mx` es Google, ya incluido). 7 consultas DNS de 10 posibles. |
| DKIM `google._domainkey` | **no existe** | Gmail firma con `thegravitywave-com.20251104.gappssmtp.com` (lo confirma Apollo). La firma no está alineada con el dominio: vale para pasar DMARC solo mientras SPF alinee, y se rompe en reenvíos y listas. Es lo que más resta. |
| DKIM `default._domainkey` | existe (2048 bits) | Es la clave del servidor de Webempresa (cPanel). Firma solo lo que manda la web; no la usa Gmail. Se deja. |
| DKIM HubSpot (`hs1-*`, `hs2-*`) | **no existe** | HubSpot envía miles de correos al mes desde `@thegravitywave.com` (1.516 entregados en mayo, 3.940 en julio) con el dominio **sin conectar**: firma con `hubspotemail.net` y no alinea. Si DMARC pasa a `pct=100` sin arreglar esto, ese correo va a spam. |
| DMARC | `v=DMARC1; p=quarantine; pct=5; rua=mailto:julen@thegravitywave.com` | Solo cubre el 5 % del correo. Sin `ruf`/`fo`, sin alineación explícita. |
| BIMI, MTA-STS, TLS-RPT | no existen | Opcionales; cuentan en algunos verificadores. |
| CAA | no existe | No afecta al correo. |

Quién envía con el dominio hoy:

- **Google Workspace** (todos los buzones, y Apollo a través de `amaia@`).
- **HubSpot** marketing (desde `norberto@`, `amaia@`, `info@`, `julen@`…).
- **Webempresa** (`213.158.86.32`, `ns50171.webempresa.eu`): el WordPress de
  la web, formularios.
- `51.178.3.36` (OVH, sin PTR): no sabemos qué es. Se mantiene en el SPF
  hasta identificarlo; si en un mes los informes DMARC no lo muestran
  enviando, se quita.

## Qué hay que hacer, en orden

Las fases 1 a 3 se pueden hacer el mismo día. La 4 espera a que la 1 y la 2
estén verificadas. Ningún paso corta el correo si se respeta el orden.

### 1. DKIM propio en Google Workspace (25 puntos)

1. [admin.google.com](https://admin.google.com) → Aplicaciones → Google
   Workspace → Gmail → **Autenticar correo electrónico**.
2. Dominio `thegravitywave.com` → **Generar registro nuevo**: longitud de
   clave **2048**, prefijo del selector **`google`** (el que mira el puente).
3. Copiar el valor `v=DKIM1; k=rsa; p=MIIB…` y crearlo en Cloudflare como
   TXT en `google._domainkey` (con `aplicar-cloudflare.sh dkim '<valor>'` o
   a mano; proxy desactivado, es un TXT).
4. Esperar 10–60 minutos y pulsar **Iniciar autenticación** en el mismo
   sitio del Admin. Hasta entonces Gmail sigue firmando con la clave de
   `gappssmtp.com`, así que no se pierde nada.
5. Comprobar: enviarse un correo desde `amaia@` y en Gmail «Mostrar
   original» debe decir `DKIM: 'PASS' con el dominio thegravitywave.com`.

### 2. Conectar el dominio de envío en HubSpot

1. HubSpot → Configuración → Contenido → **Dominios y URL** → Conectar un
   dominio → **Envío de correo electrónico** → `thegravitywave.com`.
2. HubSpot da tres CNAME con nombres propios del portal (del estilo
   `hs1-XXXX._domainkey`, `hs2-XXXX._domainkey` y uno para el remitente del
   sobre). Se crean en Cloudflare tal cual, **sin proxy** (nube gris); con
   `aplicar-cloudflare.sh cname <nombre> <destino>` o a mano.
3. Volver a HubSpot y pulsar **Verificar**. A partir de ahí HubSpot firma
   DKIM con `thegravitywave.com` y alinea el sobre.

Sin este paso no se puede subir DMARC al 100 % sin mandar el marketing a
spam. Es el prerrequisito de la fase 4.

### 3. Limpiar el SPF

Sustituir el TXT actual por:

```
v=spf1 include:_spf.google.com include:_spf.webempresa.eu ip4:51.178.3.36 ~all
```

Autoriza exactamente a los mismos emisores (Google, Webempresa y la IP de
OVH) con 5 consultas DNS en vez de 7 y sin mecanismos duplicados. HubSpot no
necesita `include` porque, una vez conectado, usa su propio dominio de sobre
alineado por DKIM. Se mantiene `~all` (softfail): con DMARC es lo que
recomienda Google; `-all` no suma y hace daño en reenvíos.

`aplicar-cloudflare.sh spf` lo deja así.

### 4. DMARC al 100 % (20 puntos)

Solo cuando (1) y (2) estén verificados, y como mínimo 48 h después, para
dar tiempo a que todo el correo en cola salga ya firmado:

```
v=DMARC1; p=quarantine; pct=100; rua=mailto:julen@thegravitywave.com; ruf=mailto:julen@thegravitywave.com; fo=1; adkim=r; aspf=r
```

(`aplicar-cloudflare.sh dmarc quarantine`). Lo que cambia respecto a hoy:
`pct=100` cubre todo el correo; `ruf`/`fo=1` piden informe de cada fallo,
que es lo que dirá si queda algún emisor olvidado (la IP de OVH, algún SaaS).

Tras 2–4 semanas de informes sin fallos legítimos, pasar a rechazo:

```
v=DMARC1; p=reject; pct=100; rua=mailto:julen@thegravitywave.com; ruf=mailto:julen@thegravitywave.com; fo=1; adkim=s; aspf=s
```

(`aplicar-cloudflare.sh dmarc reject`). Es el máximo que mide cualquier
verificador. Los informes `rua` llegan como XML adjunto a `julen@`; para
leerlos cómodamente vale cualquier buzón gratuito de informes DMARC
(Postmark, dmarcian, EasyDMARC…) poniendo su dirección en `rua` además de la
nuestra.

### 5. Extras (suben la nota en verificadores, no en Gmail/Outlook)

- **TLS-RPT** (`aplicar-cloudflare.sh tlsrpt`): TXT en `_smtp._tls` con
  `v=TLSRPTv1; rua=mailto:julen@thegravitywave.com`. Inofensivo, avisa si
  alguien no consigue entregarnos por TLS.
- **MTA-STS**: exige servir
  `https://mta-sts.thegravitywave.com/.well-known/mta-sts.txt` con la
  política (modo `testing` primero) y un TXT `_mta-sts` con `v=STSv1;
  id=<fecha>`. En Cloudflare se hace con un Worker o Pages; está en el
  script como `mta-sts` solo el TXT, la página hay que publicarla aparte.
- **BIMI** (`default._bimi` TXT `v=BIMI1; l=https://…/logo.svg; a=`):
  solo tiene sentido con DMARC en `p=quarantine; pct=100` o `reject`, el
  logo en SVG Tiny PS y, para que Gmail lo enseñe, un certificado VMC de
  pago. Yahoo y Fastmail lo muestran sin VMC. Se deja para después de la
  fase 4.

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

```
export CF_API_TOKEN=…        # token con permiso Zone:DNS:Edit sobre thegravitywave.com
dns/aplicar-cloudflare.sh spf
dns/aplicar-cloudflare.sh dkim 'v=DKIM1; k=rsa; p=MIIB…'
dns/aplicar-cloudflare.sh cname hs1-XXXX._domainkey hs1-XXXX._domainkey.hubspotemail.net
dns/aplicar-cloudflare.sh tlsrpt
dns/aplicar-cloudflare.sh dmarc quarantine     # cuando (1) y (2) estén verificados
dns/aplicar-cloudflare.sh dmarc reject         # 2–4 semanas después
```

Cada orden crea o actualiza un registro (nunca borra otros), enseña lo que
había y lo que deja, y con `--dry-run` delante solo lo enseña. El token se
crea en Cloudflare → Mi perfil → Tokens de API → plantilla «Editar DNS de
zona», limitado a esta zona. La sesión de Claude no tiene ese token ni
acceso al Admin de Google, por eso estos pasos los tiene que ejecutar una
persona (o pasar el token por secreto de GitHub y correr el script desde
Actions).
