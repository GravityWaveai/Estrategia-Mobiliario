# -*- coding: utf-8 -*-
"""Las 10 piezas del lanzamiento de mobiliario urbano en RRSS.

Cada pieza son uno o varios "tableros" (artboards) a tamaño real de píxel.
Nada de datos inventados: precios del catálogo Ocean Originals, los 12
acabados Gravitec® reales, y las cifras externas siempre con su fuente
a la vista.
"""
from estilo import FLECHA, PFO, acabado, foto, wordmark

IG45 = (1080, 1350)     # feed de Instagram, 4:5
IG11 = (1080, 1080)     # feed de Instagram, 1:1
IGST = (1080, 1920)     # stories
LI11 = (1200, 1200)     # documento / carrusel de LinkedIn
LI45 = (1200, 1500)     # post de imagen de LinkedIn, 4:5

# Frases y datos reales reutilizados en varias piezas.
FRASE_ACABADOS = ("Todos nuestros acabados lucen literalmente el color exacto "
                  "de las redes que sacamos del mar.")
ACABADOS = ["Cadaques", "Vulcano", "Sicilia", "Ifach", "Palermo", "Formentera",
            "Capri", "Itaca", "Andros", "Niza", "Atenas", "Marsella"]
ACABADOS_TXT = ["Cadaqués", "Vulcano", "Sicilia", "Ifach", "Palermo",
                "Formentera", "Capri", "Ítaca", "Andros", "Niza", "Atenas",
                "Marsella"]

# Catálogo Ocean Originals (€/ud, +IVA): precio de unidad suelta y precio
# por volumen. Se publica la horquilla real, sin inventar los tramos de
# cantidad, que se fijan con el pedido.
CATALOGO = [
    ("Banco Urbano",    "banco-urbano.jpg",     644, 466,
     "Listones de Gravitec® sobre estructura metálica. Con respaldo. "
     "La pieza de calle, ya instalada en vía pública."),
    ("Banco Nero",      "banco-nero.jpg",       519, 490,
     "Banco macizo de Gravitec®, sin metal a la vista. Interior, "
     "vestíbulos y espacios cubiertos."),
    ("Mesa Palaia",     "mesa-palaia.jpg",      469, 395,
     "Tablero de Gravitec® de gran formato. Salas, comedores, "
     "centros cívicos y bibliotecas."),
    ("Papelera Sorell", "papelera-sorell.jpg",  307, 179,
     "Papelera de exterior en Gravitec®. El acabado se elige entre "
     "los doce del catálogo."),
    ("Taburete Melva",  "taburete-melva.jpg",    88,  80,
     "Taburete de Gravitec®. La pieza de entrada para un primer "
     "pedido de prueba."),
    ("Letrero corpóreo", None,  0,   0,
     "El nombre del municipio, un mirador o un parque, cortado en "
     "Gravitec®. Presupuesto a medida según medidas."),
]


# --------------------------------------------------------------- utilidades
def marca(clase=""):
    return ('<div class="marca %s" role="img" aria-label="Gravity Wave" '
            'style="background-image:url(%s)"></div>' % (clase, wordmark()))


def pie(izq="", der=""):
    return ('<div class="scrim"></div><div class="pie">%s%s</div>'
            % (izq or "<div></div>", der or "<div></div>"))


def contador(i, total):
    return '<div class="contador">%02d / %02d</div>' % (i, total)


def desliza(texto="Desliza"):
    return '<div class="desliza">%s %s</div>' % (texto, FLECHA)


def bg_foto(nombre, clase=""):
    return '<div class="bg %s %s"></div>' % (foto(nombre), clase)


def bg_acabado(nombre, clase=""):
    return '<div class="bg %s %s"></div>' % (acabado(nombre), clase)


# Donde cae el motivo en cada foto, para que el encuadre no lo corte.
ENCUADRE = {"banco-urbano.jpg": "center 58%"}


def mitad_foto(nombre):
    """Foto a sangre en la mitad de arriba; el texto va sobre petroleo."""
    pos = ENCUADRE.get(nombre)
    estilo_pos = ' style="background-position:%s"' % pos if pos else ""
    return '<div class="mitad %s"%s></div>' % (foto(nombre), estilo_pos)


def hueco(aviso):
    return ('<div class="hueco"><div class="marco"></div>'
            '<div class="av">%s</div></div>' % aviso)


def tablero(tid, nombre, canal, tam, cuerpo, nota=""):
    return {"id": tid, "nombre": nombre, "canal": canal,
            "w": tam[0], "h": tam[1], "html": cuerpo, "nota": nota}


def mosaico_acabados(cols, filas, nombres=None, con_nombres=True, clase=""):
    nombres = nombres or ACABADOS
    celdas = []
    for i, n in enumerate(nombres[:cols * filas]):
        etq = ('<span>%s</span>' % ACABADOS_TXT[ACABADOS.index(n)]
               if con_nombres else "")
        celdas.append('<div class="t %s">%s</div>' % (acabado(n), etq))
    return ('<div class="mosaico %s" style="grid-template-columns:repeat(%d,1fr);'
            'grid-template-rows:repeat(%d,1fr)">%s</div>'
            % (clase, cols, filas, "".join(celdas)))


# =========================================================== P01 · teaser
def p01():
    cuerpo = (
        bg_acabado("Cadaques")
        + '<div class="velo abajo"></div>'
        + '<div class="lienzo abajo">'
        '<div class="ante">Mobiliario urbano · Gravity Wave</div>'
        '<h1 class="tit mt-s">Este banco<br>estuvo en el<br>'
        '<em>fondo del mar</em></h1>'
        '<hr class="filete mt-l">'
        '</div>'
        + pie(marca(), '<div class="etq">thegravitywave.com</div>')
    )
    return [tablero("p01", "Teaser · Este banco estuvo en el fondo del mar",
                    "IG + LinkedIn", IG45, cuerpo)]


# ============================================================= P02 · bucle
def p02():
    t = []
    pasos = [
        ("01", "Sale del mar", "Red de pesca y cabo, retirados del "
         "Mediterráneo y de sus puertos.", "hueco",
         "Foto de misión:<br>red o cabo bajo el agua"),
        ("02", "Se convierte en material", "Se limpia, se tritura y se "
         "prensa en Gravitec®, nuestro propio material.", "acabado",
         "Sicilia"),
        ("03", "Vuelve a tu ciudad", "Bancos, mesas y papeleras en la "
         "plaza, en el paseo, en el colegio.", "foto", "banco-urbano.jpg"),
    ]
    for i, (num, tit, txt, tipo, dato) in enumerate(pasos, start=1):
        if tipo == "hueco":
            fondo = hueco(dato)
            velo = '<div class="velo abajo"></div>'
        elif tipo == "acabado":
            fondo = bg_acabado(dato)
            velo = '<div class="velo abajo"></div>'
        else:
            fondo = bg_foto(dato, "banco")
            velo = '<div class="velo abajo"></div>'
        cuerpo = (fondo + velo + '<div class="lienzo abajo">'
                  '<div class="ante">%s</div>'
                  '<h1 class="tit l mt-s">%s</h1>'
                  '<p class="txt mt">%s</p></div>'
                  % (num, tit, txt)
                  + pie(marca(), contador(i, 4)))
        t.append(tablero("p02-%d" % i, "El bucle · %s" % tit,
                         "IG carrusel", IG45, cuerpo))

    cierre = ('<div class="lienzo centro">'
              '<div class="ante">El círculo se cierra</div>'
              '<h1 class="tit xl mt-s">En la<br>calle</h1>'
              '<hr class="filete mt-l">'
              '<p class="txt mt">Sacar el plástico del mar es la mitad del '
              'trabajo. La otra mitad es <b>darle un sitio donde quedarse</b>.'
              '</p></div>'
              + pie(marca(), PFO))
    t.append(tablero("p02-4", "El bucle · Cierre", "IG carrusel", IG45, cierre))
    return t


# ======================================================= P03 · carrusel héroe
def p03():
    T = 8
    t = []

    # 1 · portada
    t.append(tablero("p03-1", "Héroe · Portada", "IG carrusel", IG45,
        bg_foto("banco-urbano.jpg", "top")
        + '<div class="velo abajo"></div>'
        + '<div class="lienzo abajo">'
        '<div class="ante">Lanzamiento · Mobiliario urbano</div>'
        '<h1 class="tit mt-s">Mobiliario<br>urbano hecho<br>con el plástico<br>'
        'del <em>Mediterráneo</em></h1>'
        '<hr class="filete mt-l"></div>'
        + pie(marca(), desliza())))

    # 2 · el problema, con fuente a la vista
    t.append(tablero("p03-2", "Héroe · El problema", "IG carrusel", IG45,
        '<div class="lienzo">'
        '<div class="ante">El problema</div>'
        '<h1 class="tit m mt-s">Al Mediterráneo<br>le entran cada año</h1>'
        '<div class="empuja"><div class="cifra">229.000<span class="un">'
        ' toneladas</span></div>'
        '<p class="txt mt">de plástico. Una parte enorme es <b>aparejo de '
        'pesca</b>: redes y cabos que nadie recoge porque no tenían salida.</p>'
        '<p class="fuente mt-s">Fuente: UICN, «The Mediterranean: Mare '
        'Plasticum», 2020.</p></div></div>'
        + pie(marca(), contador(2, T))))

    # 3 · qué es Gravitec
    t.append(tablero("p03-3", "Héroe · Gravitec®", "IG carrusel", IG45,
        bg_foto("papelera-sorell.jpg")
        + '<div class="velo abajo"></div>'
        + '<div class="lienzo abajo">'
        '<div class="ante">La solución</div>'
        '<h1 class="tit l mt-s">Las redes no se<br>reciclan solas</h1>'
        '<p class="txt mt">Las sacamos, las limpiamos y las prensamos en '
        '<b>Gravitec®</b>: nuestro propio material, en panel y en granza, '
        'listo para fabricar.</p></div>'
        + pie(marca(), contador(3, T))))

    # 4 · el catálogo
    rejilla = [("Banco", "banco-urbano.jpg"), ("Banco Nero", "banco-nero.jpg"),
               ("Mesa", "mesa-palaia.jpg"), ("Papelera", "papelera-sorell.jpg"),
               ("Papelera", "papelera-cubica.jpg"),
               ("Taburete", "taburete-melva.jpg")]
    fichas = "".join('<div class="c %s"><b>%s</b></div>' % (foto(f), n)
                     for n, f in rejilla)
    t.append(tablero("p03-4", "Héroe · El catálogo", "IG carrusel", IG45,
        '<div class="lienzo">'
        '<div class="ante">Qué se puede pedir</div>'
        '<h1 class="tit m mt-s">Bancos, mesas,<br>papeleras,<br>taburetes '
        'y letreros</h1>'
        '<div class="rejilla" style="grid-template-columns:repeat(3,1fr)">%s'
        '</div></div>' % fichas
        + pie(marca(), contador(4, T))))

    # 5 · los 12 acabados
    t.append(tablero("p03-5", "Héroe · 12 acabados", "IG carrusel", IG45,
        mosaico_acabados(3, 4, con_nombres=False)
        + '<div class="velo abajo"></div>'
        + '<div class="lienzo abajo">'
        '<div class="ante">Doce acabados</div>'
        '<h1 class="tit l mt-s">Ningún color<br>está inventado</h1>'
        '<p class="txt mt">%s</p></div>' % FRASE_ACABADOS
        + pie(marca(), contador(5, T))))

    # 6 · trazabilidad
    t.append(tablero("p03-6", "Héroe · Trazabilidad", "IG carrusel", IG45,
        '<div class="lienzo">'
        '<div class="ante">Trazabilidad</div>'
        '<h1 class="tit m mt-s">Cada pieza sabe<br>de qué mar viene</h1>'
        '<div class="lista empuja">'
        '<div class="item"><div class="n">01</div><div class="c">'
        '<strong>Puerto de origen</strong>Se registra de dónde salió el '
        'aparejo que lleva dentro.</div></div>'
        '<div class="item"><div class="n">02</div><div class="c">'
        '<strong>Kilos retirados</strong>Los kilos del pedido se anotan a '
        'nombre de quien lo compra.</div></div>'
        '<div class="item"><div class="n">03</div><div class="c">'
        '<strong>Informe de impacto</strong>Un documento que se puede '
        'publicar y auditar.</div></div>'
        '</div></div>'
        + pie(marca(), contador(6, T))))

    # 7 · lo que se lleva un municipio  ← la carga útil para ayuntamientos
    t.append(tablero("p03-7", "Héroe · Lo que se lleva un municipio",
                     "IG carrusel", IG45,
        '<div class="lienzo">'
        '<div class="ante">Si sois ayuntamiento</div>'
        '<h1 class="tit m mt-s">Lo que se lleva<br>un municipio</h1>'
        '<div class="lista">'
        '<div class="item"><div class="n">—</div><div class="c">'
        'Mobiliario de calle <strong style="display:inline;font-size:inherit">'
        '</strong>con la misma vida útil que el de siempre.</div></div>'
        '<div class="item"><div class="n">—</div><div class="c">'
        'Kilos de plástico retirados del Mediterráneo <b>a nombre del '
        'municipio</b>.</div></div>'
        '<div class="item"><div class="n">—</div><div class="c">'
        'Criterio ambiental que encaja en pliego y en los ODS 12 y 14.'
        '</div></div>'
        '<div class="item"><div class="n">—</div><div class="c">'
        'Fotos, textos y datos para contárselo a los vecinos.</div></div>'
        '</div></div>'
        + pie(marca(), contador(7, T))))

    # 8 · CTA
    t.append(tablero("p03-8", "Héroe · Llamada a la acción", "IG carrusel",
                     IG45,
        bg_acabado("Niza")
        + '<div class="velo plano"></div>'
        + '<div class="lienzo centro">'
        '<div class="ante blanca">Hablemos</div>'
        '<h1 class="tit l mt-s">¿Ponemos un<br>banco del<br>Mediterráneo<br>'
        'en <em>vuestra ciudad</em>?</h1>'
        '<p class="txt mt">Escríbenos por mensaje directo o entra en '
        '<b>thegravitywave.com</b>. Te mandamos propuesta y mockup de vuestra '
        'pieza en 24 h.</p></div>'
        + pie(marca(), PFO)))
    return t


# ========================================================= P04 · manifiesto
def p04():
    cuerpo = ('<div class="lienzo centro">'
              '<div class="ante">Manifiesto</div>'
              '<h1 class="tit mt-s">Sacar el<br>plástico es<br>la mitad<br>'
              'del trabajo.<br><em>La otra es<br>darle un sitio.</em></h1>'
              '<hr class="filete mt-l"></div>'
              + pie(marca(), PFO))
    return [tablero("p04", "Manifiesto · La otra mitad del trabajo",
                    "IG + LinkedIn", IG45, cuerpo)]


# =========================================================== P05 · catálogo
def p05():
    t = []
    T = len(CATALOGO) + 1
    t.append(tablero("p05-1", "Catálogo · Portada", "IG carrusel", IG45,
        bg_acabado("Cadaques")
        + '<div class="velo abajo"></div>'
        + '<div class="lienzo abajo">'
        '<div class="ante">Ocean Originals</div>'
        '<h1 class="tit xl mt-s">El<br>catálogo</h1>'
        '<p class="txt mt">Seis piezas de Gravitec®, doce acabados y precio '
        'que baja por volumen.</p></div>'
        + pie(marca(), desliza())))

    for i, (nombre, fichero, suelta, volumen, txt) in enumerate(CATALOGO,
                                                                start=2):
        if suelta:
            precio = ('<div class="precio"><span class="v">%d – %d €</span>'
                      '<span class="u">/ud según volumen</span></div>'
                      % (volumen, suelta))
        else:
            precio = ('<div class="precio"><span class="v">A medida</span>'
                      '<span class="u">según medidas y acabado</span></div>')
        if fichero:
            panel = ('<div class="tarjeta"><div class="foto %s"></div></div>'
                     % foto(fichero))
        else:
            panel = ('<div class="tarjeta">%s</div>'
                     % hueco("Foto pendiente:<br>letrero con el nombre "
                             "del municipio"))
        cuerpo = (panel
                  + '<div class="lienzo bajo-tarjeta">'
                  '<div class="ante">Pieza %02d de 06</div>'
                  '<h1 class="tit s mt-s">%s</h1>'
                  '<p class="txt sm mt-s">%s</p>%s</div>'
                  % (i - 1, nombre, txt, precio)
                  + pie(marca(), contador(i, T)))
        t.append(tablero("p05-%d" % i, "Catálogo · %s" % nombre,
                         "IG carrusel", IG45, cuerpo,
                         nota="Precio del catálogo Ocean Originals, +IVA."))
    return t


# ========================================================== P06 · 12 acabados
def p06():
    cuerpo = (mosaico_acabados(4, 3, clase="dentro")
              + '<div class="banda">'
              '<div class="ante">Acabados Gravitec® 2026</div>'
              '<h1 class="tit m mt-s">Doce acabados</h1>'
              '<p class="txt sm mt-s" style="max-width:calc(var(--u)*700)">%s'
              '</p></div>' % FRASE_ACABADOS
              + pie(marca(), ""))
    return [tablero("p06", "Los doce acabados", "IG feed 1:1", IG11, cuerpo)]


# ================================================ P07 · carrusel B2G LinkedIn
def p07():
    T = 6
    t = []
    t.append(tablero("p07-1", "LinkedIn B2G · Portada", "LinkedIn documento",
                     LI11,
        bg_foto("banco-urbano.jpg", "top")
        + '<div class="velo abajo"></div>'
        + '<div class="lienzo abajo">'
        '<div class="ante">Compra pública · Mobiliario urbano</div>'
        '<h1 class="tit m mt-s">Cómo un ayuntamiento<br>compra mobiliario '
        'hecho<br>con el plástico<br>del <em>Mediterráneo</em></h1>'
        '<hr class="filete mt-l"></div>'
        + pie(marca(), desliza("Pasa página"))))

    t.append(tablero("p07-2", "LinkedIn B2G · El encaje", "LinkedIn documento",
                     LI11,
        '<div class="lienzo">'
        '<div class="ante">01 · El encaje administrativo</div>'
        '<h1 class="tit m mt-s">No hace falta<br>inventar un<br>procedimiento'
        '</h1>'
        '<div class="lista">'
        '<div class="item"><div class="n">—</div><div class="c">'
        '<strong>Contrato menor</strong>Un primer pedido de prueba —unos '
        'taburetes, una papelera— entra por contrato menor.</div></div>'
        '<div class="item"><div class="n">—</div><div class="c">'
        '<strong>Lote de mobiliario</strong>En una licitación de mobiliario '
        'urbano somos un lote más, con ficha técnica y garantía.</div></div>'
        '<div class="item"><div class="n">—</div><div class="c">'
        '<strong>Criterio ambiental</strong>El material reciclado de origen '
        'marino puntúa como criterio de compra pública verde, y suma en '
        'los ODS 12 y 14.</div></div>'
        '</div></div>'
        + pie(marca(), contador(2, T))))

    filas = "".join(
        '<tr><td>%s</td><td>%s</td><td>%s</td></tr>'
        % (n, ("%d €" % a) if a else "a medida",
           ("%d €" % b) if b else "a medida")
        for n, _, a, b, _ in CATALOGO)
    t.append(tablero("p07-3", "LinkedIn B2G · Precios", "LinkedIn documento",
                     LI11,
        '<div class="lienzo">'
        '<div class="ante">02 · Precio</div>'
        '<h1 class="tit m mt-s">El precio baja<br>por volumen</h1>'
        '<table class="tabla"><thead><tr><th>Pieza</th>'
        '<th>Unidad suelta</th><th>Por volumen</th></tr></thead>'
        '<tbody>%s</tbody></table>'
        '<p class="fuente mt">Catálogo Ocean Originals, €/ud, IVA no '
        'incluido. El tramo exacto se fija con el pedido.</p></div>' % filas
        + pie(marca(), contador(3, T)),
        nota="Comprobar la tarifa vigente antes de publicar."))

    t.append(tablero("p07-4", "LinkedIn B2G · Plazos", "LinkedIn documento",
                     LI11,
        '<div class="lienzo">'
        '<div class="ante">03 · Plazos</div>'
        '<h1 class="tit m mt-s">Propuesta y mockup<br>de vuestra pieza</h1>'
        '<div class="empuja"><div class="cifra">24<span class="un"> h</span></div>'
        '<p class="txt mt">Nos decís municipio, pieza y acabado, y os '
        'mandamos <b>la propuesta y el mockup de vuestra pieza</b> al día '
        'siguiente. El plazo de fabricación se confirma con el pedido.</p>'
        '</div></div>'
        + pie(marca(), contador(4, T))))

    t.append(tablero("p07-5", "LinkedIn B2G · Lo que comunica el municipio",
                     "LinkedIn documento", LI11,
        bg_acabado("Capri")
        + '<div class="velo plano"></div>'
        + '<div class="lienzo">'
        '<div class="ante blanca">04 · Lo que se puede contar</div>'
        '<h1 class="tit m mt-s">Un banco que<br>explica solo<br>de qué va</h1>'
        '<div class="lista">'
        '<div class="item"><div class="n">—</div><div class="c">'
        'Los kilos retirados del Mediterráneo, a nombre del municipio.'
        '</div></div>'
        '<div class="item"><div class="n">—</div><div class="c">'
        'Informe de impacto publicable, con puerto de origen.</div></div>'
        '<div class="item"><div class="n">—</div><div class="c">'
        'Fotos, textos y placa para el mobiliario instalado.</div></div>'
        '</div></div>'
        + pie(marca(), contador(5, T))))

    t.append(tablero("p07-6", "LinkedIn B2G · Contacto", "LinkedIn documento",
                     LI11,
        '<div class="lienzo centro">'
        '<div class="ante">05 · Siguiente paso</div>'
        '<h1 class="tit l mt-s">Decidnos vuestro<br>municipio y qué<br>'
        'pieza os <em>encaja</em></h1>'
        '<p class="txt mt">Os mandamos propuesta y mockup en 24 h. Sin '
        'compromiso y sin coste.</p>'
        '<hr class="filete mt-l">'
        '<p class="txt mt">thegravitywave.com &nbsp;·&nbsp; Calpe, Alicante'
        '</p></div>'
        + pie(marca(), PFO)))
    return t


# ==================================================== P08 · tarjeta de cita
def p08():
    cuerpo = (bg_acabado("Vulcano")
              + '<div class="velo plano"></div>'
              + '<div class="lienzo centro">'
              '<div class="ante">Gravity Wave</div>'
              '<h1 class="tit m mt-s">«No hemos hecho<br>un banco bonito.<br>'
              'Hemos hecho un<br><em>sitio donde poner</em><br>lo que sacamos'
              '<br>del mar.»</h1>'
              '<hr class="filete mt-l"></div>'
              + pie(marca(), PFO))
    return [tablero("p08", "Tarjeta de cita para post de fundadora",
                    "LinkedIn", LI45, cuerpo,
                    nota="La cita es una propuesta de redacción: que la "
                         "valide Amaia antes de publicar.")]


# ============================================================ P09 · stories
def p09():
    t = []
    t.append(tablero("p09-1", "Stories · Teaser", "IG stories", IGST,
        bg_acabado("Cadaques")
        + '<div class="velo plano"></div>'
        + '<div class="lienzo centro">'
        '<div class="ante">Mañana</div>'
        '<h1 class="tit l mt-s">Algo del<br>fondo del<br>mar vuelve<br>'
        'a la <em>calle</em></h1>'
        '<hr class="filete mt-l"></div>'
        + pie(marca(), '<div class="etq">10:00</div>')))

    t.append(tablero("p09-2", "Stories · Encuesta", "IG stories", IGST,
        '<div class="lienzo" style="justify-content:flex-start">'
        '<div class="ante">Pregunta rápida</div>'
        '<h1 class="tit m mt-s">¿Sabes de qué<br>está hecho el<br>banco de '
        'tu<br>plaza?</h1>'
        '<p class="txt mt">Deja libre la mitad de abajo para la pegatina de '
        'encuesta.</p></div>'
        + pie(marca(), "")))

    t.append(tablero("p09-3", "Stories · Llamada a la acción", "IG stories",
                     IGST,
        bg_foto("banco-urbano.jpg", "top")
        + '<div class="velo arriba"></div>'
        + '<div class="lienzo" style="justify-content:flex-start">'
        '<div class="ante">Mobiliario urbano</div>'
        '<h1 class="tit m mt-s">Propuesta y<br>mockup de<br>vuestra pieza<br>'
        'en <em>24 h</em></h1>'
        '<p class="txt mt">Pega aquí el enlace a thegravitywave.com</p>'
        '</div>'
        + pie(marca(), "")))
    return t


# ================================================= P10 · plantilla municipio
def p10():
    cuerpo = (hueco("Foto de la pieza instalada<br>en el municipio")
              + '<div class="velo abajo"></div>'
              + '<div class="lienzo abajo">'
              '<div class="ante">Nuevo municipio</div>'
              '<h1 class="tit l mt-s">[MUNICIPIO]<br>ya se sienta<br>en el '
              '<em>Mediterráneo</em></h1>'
              '<p class="txt mt">[N] piezas de Gravitec® en [ubicación]. '
              '<b>[X] kg</b> de red y cabo fuera del mar.</p></div>'
              + pie(marca(), PFO))
    return [tablero("p10", "Plantilla reutilizable por municipio",
                    "IG + LinkedIn", IG45, cuerpo,
                    nota="Plantilla: sustituir [MUNICIPIO], [N], [ubicación] "
                         "y [X] kg por los datos reales de cada entrega.")]


# ------------------------------------------------------------------- índice
PIEZAS = [
    ("P01", "Teaser", "Semana 1", p01),
    ("P02", "El bucle en tres pasos", "Semana 1", p02),
    ("P03", "Carrusel héroe de lanzamiento", "Semana 2", p03),
    ("P04", "Manifiesto", "Semana 2", p04),
    ("P05", "El catálogo pieza a pieza", "Semana 3", p05),
    ("P06", "Los doce acabados", "Semana 3", p06),
    ("P07", "Carrusel B2G de LinkedIn", "Semana 4", p07),
    ("P08", "Tarjeta de cita para post de fundadora", "Semana 4", p08),
    ("P09", "Stories", "Todas las semanas", p09),
    ("P10", "Plantilla por municipio", "Cuando entre un municipio", p10),
]


def todas():
    salida = []
    for codigo, nombre, fase, fn in PIEZAS:
        for tb in fn():
            tb["pieza"] = codigo
            tb["pieza_nombre"] = nombre
            tb["fase"] = fase
            salida.append(tb)
    return salida
