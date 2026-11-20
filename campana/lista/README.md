# La lista de contactos

Cómo se construye la lista de ayuntamientos de la campaña y qué hay en cada
fichero. **Los contactos no están en este repositorio**: son datos personales de
terceros y el repositorio es público. Viven en `exports/`, que git ignora.

## Ficheros

| Fichero | Qué es | ¿En git? |
|---|---|---|
| `universo-municipios.csv` | Los 510 municipios costeros evaluados, con población, Bandera Azul 2026, prioridad y web oficial. Datos públicos. | Sí |
| `rastrear_contactos.py` | Lee las webs oficiales y saca los correos publicados con su contexto. No contiene contactos. | Sí |
| `exports/rastreo/` | Lo que devolvió cada web, un JSON por municipio. | No |
| `exports/candidatos-rastreo.csv` | La criba automática: correos que parecen del perfil. | No |
| `exports/contactos-ayuntamientos.csv` | **La lista.** Solo lo que se ha leído y dado por bueno. | No |

## Estado a 2026-11-20

- 177 municipios objetivo (111 de prioridad 1, 66 de prioridad 2).
- 119 webs leídas. De 41 no hay respuesta desde este entorno, 11 se pintan con
  JavaScript y no dejan texto que leer, y 6 no publican ningún correo.
- **176 filas en la lista, de 78 municipios.**
  - 115 en la primera ola: listas para enviar, como mucho dos por municipio.
  - 37 en reserva: buenas, para la segunda vuelta.
  - 6 que ya estaban en la lista antigua de Apollo.
  - 11 personas identificadas sin correo publicado: son para llamar.
  - 7 por confirmar: la web da dos direcciones distintas o la página es vieja.

Faltan por cubrir 99 municipios, 55 de ellos de prioridad 1. Casi todos son los
de las webs que no se dejaron leer: se hacen entrando a mano o con un navegador.

## Columnas de la lista

`tipo` es `buzon`, `concejal` o `tecnico`. Cuando un buzón tiene al lado el
nombre de quien lo lleva, va en `nombre` entre paréntesis con su cargo.

`estado`: `listo` (dirección leída en la web oficial), `revisar` (el motivo está
en `nota`) o `sin_email`.

`ola`: `1` (enviar primero), `reserva`, `llamada` o `ya en Apollo`.

`fuente` es la página exacta donde está publicado el correo. Si alguien
pregunta de dónde hemos sacado su dirección, la respuesta está ahí.

## Reglas con las que se ha hecho

1. Solo direcciones publicadas en la web del propio ayuntamiento. Ninguna se ha
   deducido de un patrón ni se ha sacado de una base de datos.
2. Cuando el texto visible y el enlace de la web dan dos direcciones distintas,
   no se elige: va a `revisar`.
3. Fuera contratación, registro, alcaldía y las puertas genéricas.
4. Fuera los dos buzones que pidieron la baja y los tres clientes de referencia.

## Cómo repetirlo

```
python3 campana/lista/rastrear_contactos.py rastrear     # reanudable
python3 campana/lista/rastrear_contactos.py candidatos
```

El rastreador tarda unos 25 minutos para los 177 y no hay que subirle los
hilos: con más de ocho en paralelo el proxy empieza a cortar conexiones y los
ayuntamientos salen como «portada no legible» sin serlo.

La criba que hace `candidatos` no es un veredicto. Asocia cada correo al texto
que tiene alrededor, y en las páginas donde el nombre va después del correo se
equivoca de persona. Cada fila de la lista se ha leído antes de entrar.
