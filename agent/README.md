# Agente Apollo semanal — ampliación de la BBDD de ayuntamientos

Agente que cada lunes busca en Apollo.io contactos nominales de decisión en
los ayuntamientos costeros de la base de datos, los añade a la BBDD del repo
y los da de alta en HubSpot para que continúen el workflow del embudo
«Mobiliario Urbano» (portal 26243090).

## La base de datos

| Archivo | Papel |
|---|---|
| `data/contactos.csv` | **Fuente canónica.** Una fila por contacto/email. El agente añade filas aquí. |
| `data/ayuntamientos-costeros.xlsx` | Vista Excel para trabajar a mano. El agente la **regenera** desde el CSV en cada ejecución — no editarla directamente; editar el CSV. |
| `agent/state.json` | Rotación: qué municipios se han procesado ya en la vuelta actual. |

Columnas del CSV: `municipio, provincia, comunidad_autonoma, nombre,
apellidos, cargo, email, tipo_email, fuente, origen (manual|apollo),
fecha_alta, hubspot_sync`.

Punto de partida (01/09/2026): 223 municipios de Cataluña, C. Valenciana,
Baleares y Canarias; 156 con email institucional, 67 sin email localizado.

## Qué hace cada semana

1. Elige un lote de municipios (25 por defecto, `agent/config.json`),
   priorizando los que aún no tienen ningún contacto nominal — los 67 sin
   email entran los primeros.
2. Por cada municipio busca en Apollo la organización («Ayuntamiento de X» /
   «Ajuntament de X») y personas con los cargos de `cargos_objetivo`
   (alcaldía, medio ambiente, urbanismo, contratación…).
3. Enriquece cada persona (1 crédito Apollo por email revelado, máx. 3 por
   municipio) y descarta emails ya presentes en la BBDD.
4. Añade los nuevos al CSV con `origen=apollo`, regenera el Excel y hace
   commit al repo.
5. Da de alta cada contacto en HubSpot (upsert por email) con
   `tipo_entidad=ayuntamiento`, `municipio` y
   `canal_origen=email_ayuntamientos` — las propiedades que ya usa el
   embudo, de modo que los workflows de HubSpot siguen desde ahí.
   El resultado queda en la columna `hubspot_sync`
   (`creado` / `actualizado` / `error_*` / `sin_token`).

Cuando todos los municipios han tenido su turno, la rotación se reinicia y
vuelve a repasarlos (cargos cambian tras elecciones, altas nuevas en Apollo).

## Modo principal: Rutina de Claude (sin API keys)

Con Apollo y HubSpot conectados a Claude (cuenta julen@thegravitywave.com),
existe la Rutina **«Agente Apollo semanal — Ayuntamientos costeros»**
(`trig_01CBmh4A2VpDTAdauzLx7oHf`): cada lunes a las 06:00 UTC despierta la
sesión de Claude que tiene los conectores y ejecuta el ciclo completo con
los conectores de Apollo y HubSpot — sin necesidad de API key de Apollo ni
token de HubSpot.

Estado: **pausada** hasta el arranque de la campaña. Para activarla:
decirle a Claude «activa el agente Apollo» o activarla en claude.ai →
Routines. Para pararla, lo mismo a la inversa.

Primera verificación real (02/09/2026): Santa Susanna (municipio sin email)
→ Joan Campolier, Alcalde, ajuntament@stasusanna.org (verificado), añadido
a la BBDD.

## Alternativa: GitHub Actions con API key (una sola vez)

1. **Apollo**: en apollo.io → Settings → Integrations → API → crear API key.
   Requiere un plan con acceso a API (los planes gratuitos no lo incluyen).
2. **HubSpot**: reutiliza el token de app privada de `hubspot/README.md`
   (scopes de contactos read/write). Ejecutar antes `hubspot/provision.sh`
   si aún no se ha hecho.
3. **GitHub** → Settings → Secrets and variables → Actions:
   - `APOLLO_API_KEY`
   - `HUBSPOT_PRIVATE_APP_TOKEN`

Con eso, el workflow `.github/workflows/agente-apollo-semanal.yml` corre
solo cada lunes a las 06:00 UTC. También se puede lanzar a mano desde la
pestaña **Actions** (botón *Run workflow*), con opción de `dry_run`.

## Ejecución local

```bash
export APOLLO_API_KEY=...
export HUBSPOT_PRIVATE_APP_TOKEN=pat-eu1-...   # opcional
python3 agent/apollo_agent.py --dry-run        # ver qué haría
python3 agent/apollo_agent.py --lote 5         # lote pequeño de prueba
python3 agent/apollo_agent.py --solo-export-xlsx  # regenerar el Excel del CSV
```

Dependencia local: `pip install openpyxl` (solo para el Excel).

## Coste en créditos Apollo

Por ejecución, como máximo `25 municipios × 3 enriquecimientos = 75
créditos/semana` (~300/mes). Las búsquedas de organización y de personas no
consumen créditos de email; solo `people/match`. Ajustable en
`agent/config.json` (`municipios_por_ejecucion`, `max_contactos_por_municipio`).

## Ampliar el alcance

- **Más territorio** (Andalucía, Murcia, Galicia…): añadir los municipios al
  CSV (basta `municipio, provincia, comunidad_autonoma`, resto vacío y
  `origen=manual`) y el agente los irá completando en su rotación.
- **Más cargos**: `cargos_objetivo` en `agent/config.json`.
