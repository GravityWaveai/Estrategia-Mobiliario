# Registros DNS del correo

Lo que hay que publicar, tal cual, y en qué orden. Contexto y por qué en
[`../ENTREGABILIDAD.md`](../ENTREGABILIDAD.md). Los DNS de
`thegravitywave.com` están en Webempresa (el SPF los nombra).

Comprobar cualquier registro sin instalar nada:

```bash
curl -s -H 'accept: application/dns-json' \
  'https://dns.google/resolve?name=google._domainkey.thegravitywave.com&type=TXT'
```

---

## 1. `thegravitywave.com` — el dominio de la empresa

Hoy (21/09/2026):

| Registro | Valor actual |
|---|---|
| SPF | `v=spf1 ip4:213.158.86.32 ip4:51.178.3.36 include:_spf.webempresa.eu +a +mx +include:_spf.google.com ~all` |
| DKIM | `google._domainkey` **no existe**. Solo `default._domainkey` (clave del hosting, 2048 bits) |
| DMARC | `v=DMARC1; p=quarantine; pct=5; rua=mailto:julen@thegravitywave.com` |

### Paso 1 — DKIM de Google Workspace (hoy, 10 minutos)

En la consola de administración: **Apps › Google Workspace › Gmail ›
Autenticar correo**. Elegir `thegravitywave.com`, **Generar registro nuevo**,
longitud de clave **2048**, selector `google`. Google muestra un TXT como:

```
Nombre:  google._domainkey
Tipo:    TXT
Valor:   v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA…
```

Publicarlo en Webempresa. Ojo: una clave de 2048 bits supera los 255
caracteres de una cadena TXT; el panel de Webempresa la parte solo o hay que
pegarla como dos cadenas entre comillas seguidas. Esperar a que resuelva (de
minutos a 48 h) y volver a la consola: **Iniciar autenticación**.

Comprobación: mandar un correo desde cualquier buzón de Workspace a un Gmail
de prueba, «Mostrar original», y en `Authentication-Results` tiene que poner
`dkim=pass header.d=thegravitywave.com`. Si pone `header.d=…gappssmtp.com`,
todavía no está.

> Antes de generar nada, mirar en esa misma pantalla si el DKIM ya figura
> como activado con selector `default`. Es poco probable (ese selector es el
> que crea el hosting), pero es un vistazo.

### Paso 2 — SPF limpio (el mismo día)

Sustituir el TXT actual por:

```
v=spf1 ip4:213.158.86.32 ip4:51.178.3.36 include:_spf.webempresa.eu include:_spf.google.com ~all
```

Qué cambia y por qué:

- Fuera `+a`: autoriza a la IP de la web, que ya está como `ip4:`.
- Fuera `+mx`: autoriza a enviar a los servidores de **entrada** de Google, que
  no envían nada nuestro. Superficie regalada.
- Fuera el `+` delante de `include:`: es el valor por defecto, sobra.
- Se mantiene `~all`. No pasar a `-all` hasta que DMARC lleve un mes limpio.

Consultas DNS: pasa de 7 a 5 (de las 10 permitidas). Con margen para la
herramienta que haga falta mañana.

### Paso 3 — DMARC, por etapas (empezar una semana después del paso 1)

**Crear primero un alias `dmarc@thegravitywave.com`** que reciban Julen y
quien administre Workspace: los informes llegan como XML adjuntos, ilegibles a
mano. Darlos de alta en un lector gratuito (Postmark DMARC Digests, dmarcian
free o similar) que los convierte en un resumen semanal.

| Cuándo | Registro `_dmarc.thegravitywave.com` |
|---|---|
| Hoy | dejar el actual hasta que DKIM esté activo y verificado |
| DKIM activo + 1 semana de informes sin sorpresas | `v=DMARC1; p=quarantine; pct=25; sp=quarantine; adkim=r; aspf=r; rua=mailto:dmarc@thegravitywave.com; fo=1` |
| + 2 semanas limpias | `…; pct=100; …` |
| + 1 mes limpio, y nada legítimo cayendo | `v=DMARC1; p=reject; sp=reject; adkim=r; aspf=r; rua=mailto:dmarc@thegravitywave.com; fo=1` |

`sp=quarantine` cubre los subdominios: hoy nadie envía desde
`*.thegravitywave.com`, así que cualquier cosa que lo intente es suplantación.

> **Regla:** no subir `pct` sin haber leído los informes del tramo anterior.
> Si al subir cae correo legítimo (un formulario de la web, una herramienta
> que envíe «como» nosotros), bajar y añadir esa fuente al SPF/DKIM antes.

### Paso 4 — Google Postmaster Tools (hoy, 5 minutos)

[postmaster.google.com](https://postmaster.google.com): añadir
`thegravitywave.com` y verificarlo con un TXT. Es la **única** forma de ver la
reputación real del dominio ante Gmail y la tasa de denuncias de spam. Los
datos tardan unos días en aparecer y solo salen con volumen; aun así, es lo
que hay que mirar antes de decidir nada sobre volumen.

---

## 2. El dominio de outbound — plantilla

Sustituir `DOMINIO-OUTBOUND` por el que se compre. Candidatos, por comprobar
disponibilidad: `gravitywave.es`, `thegravitywave.es`, `gravity-wave.es`,
`gravitywave.eco`. Que parezca la marca, que no parezca desechable, y **que
redirija a la web** (301) para que quien lo teclee llegue a algún sitio.

### Buzones

La opción más barata y controlada: añadirlo como **dominio secundario** en el
Workspace actual (sin coste por dominio) y crear un **usuario** en él
(`amaia@DOMINIO-OUTBOUND`, ~7 €/mes). Un alias no vale: Apollo conecta el
buzón por OAuth de Gmail y el remitente tiene que ser una cuenta real.

Apollo también vende dominios y buzones ya configurados y con calentamiento
(`Mailboxes`, en Ajustes). Es más caro por buzón pero quita el trabajo de DNS
y de calentamiento; si nadie va a poder hacer el calentamiento a mano de la
tabla de `ENTREGABILIDAD.md`, es la opción realista.

### Registros

| Registro | Nombre | Valor |
|---|---|---|
| MX | `@` | los cinco de Google (`aspmx.l.google.com` 1, `alt1`/`alt2` 5, `alt3`/`alt4` 10) |
| TXT (SPF) | `@` | `v=spf1 include:_spf.google.com ~all` |
| TXT (DKIM) | `google._domainkey` | el que genere la consola, 2048 bits |
| TXT (DMARC) | `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@thegravitywave.com; fo=1` |
| A / redirección | `@`, `www` | 301 a `https://www.thegravitywave.com/` |

El SPF de este dominio lleva **solo Google**. Nada de hosting, nada de `a`,
nada de `mx`: cuanto más corto, mejor.

DMARC arranca en `p=none` a propósito: un dominio nuevo se observa dos
semanas antes de aplicar nada. Luego, `p=quarantine` y al mes `p=reject`,
igual que arriba.

### Antes de enviar el primer correo desde él

1. Los cuatro registros resueltos y DKIM en estado «autenticando» en la consola.
2. Un correo a un Gmail de prueba con `spf=pass`, `dkim=pass`
   `header.d=DOMINIO-OUTBOUND`, `dmarc=pass`.
3. Un correo a [mail-tester.com](https://www.mail-tester.com) con nota ≥ 9/10.
4. El buzón conectado en Apollo y `OUTBOUND_SENDER_EMAIL` apuntando a él (ver
   `bridge/README.md`). El puente se niega a arrancar si no coincide.
5. Foto en Gmail, firma **de texto plano**, y un par de semanas de correos
   normales a gente que conteste. Solo entonces, la secuencia.
