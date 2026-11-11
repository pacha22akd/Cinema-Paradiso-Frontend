# Flujo de compra: horario -> entradas -> butacas -> comida -> confirmación -> pago -> éxito.
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.api import llamar_api
from services.auth import revisar_login

compra_bp = Blueprint("compra", __name__)

def get_pelicula(pelicula_id):

    peliculas, estado = llamar_api("GET", "/peliculas")

    pelicula_buscada = None

    if estado == 200:
        for pelicula in peliculas:
            if pelicula["id"] == pelicula_id:
                pelicula_buscada = pelicula

    return pelicula_buscada, estado


def get_funciones(pelicula_id):

    funciones, estado = llamar_api("GET", "/peliculas/" + str(pelicula_id) + "/funciones")

    if estado == 200:
        for funcion in funciones:
            funcion["inicio"] = datetime.fromisoformat(funcion["fecha_hora_inicio"])

    return funciones, estado


def get_funcion(pelicula_id, funcion_id):

    funciones, estado = get_funciones(pelicula_id)

    funcion_buscada = None

    if estado == 200:
        for funcion in funciones:
            if funcion["funcion_id"] == funcion_id:
                funcion_buscada = funcion

    return funcion_buscada, estado


def get_butacas(funcion_id):

    return llamar_api("GET", "/funciones/" + str(funcion_id) + "/butacas")


def get_servicios():

    return llamar_api("GET", "/servicios")


def crear_compra(funcion_id, butaca_ids):

    return llamar_api("POST", "/compras", datos={"funcion_id": funcion_id, "butaca_ids": butaca_ids})


def agregar_servicio(compra_id, servicio_id, cantidad):

    return llamar_api("POST", "/compras/" + str(compra_id) + "/servicios", datos={"servicio_id": servicio_id, "cantidad": cantidad})


def pagar_compra(compra_id):

    return llamar_api("POST", "/compras/" + str(compra_id) + "/pagar")


def cancelar_compra(compra_id, motivo):

    return llamar_api("PATCH", "/compras/" + str(compra_id) + "/cancelar", datos={"motivo": motivo})


def get_compra(compra_id):

    compra, estado = llamar_api("GET", "/compras/" + str(compra_id))

    if estado == 200:
        compra["inicio"] = datetime.fromisoformat(compra["fecha_hora_inicio"])

    return compra, estado


# RUTAS DEL FLUJO DE COMPRA

@compra_bp.before_request
def proteger():
    # Se ejecuta antes de CUALQUIER ruta de compra: hay que estar logueado
    return revisar_login()


def manejar_error(mensaje, estado):
    """Devuelve la respuesta que corresponde cuando el backend contestó con un error"""
    if estado == 401:
        # el token venció o no existe: hay que volver a loguearse
        session.clear()
        flash("Tu sesión expiró. Iniciá sesión nuevamente.", "warning")
        return redirect(url_for("publico.login"))
    if estado == 404:
        return render_template("errors/404.html"), 404
    flash(mensaje, "danger")
    return redirect(url_for("publico.cartelera"))


@compra_bp.app_template_filter("precio")
def formato_precio(valor):
    texto = "{:,.2f}".format(valor)                                       
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")   
    if texto.endswith(",00"):
        texto = texto[:-3]
    return "$" + texto


def agrupar_por_local(funciones):
    locales = []
    for funcion in funciones:
        grupo = None
        for local in locales:
            if local["id"] == funcion["local_id"]:
                grupo = local
        if grupo is None:
            grupo = {"id": funcion["local_id"], "nombre": funcion["local_nombre"],
                     "direccion": funcion["local_direccion"], "funciones": []}
            locales.append(grupo)
        grupo["funciones"].append(funcion)
    return locales


def armar_resumen(funcion, butacas_sala, servicios, datos):
    maximo_entradas = 8

    cantidad = datos.get("cantidad", 0, type=int)
    if cantidad < 1 or cantidad > maximo_entradas:
        cantidad = 0

    elegidas = datos.getlist("butacas")
    butacas = []
    for butaca in butacas_sala:
        if str(butaca["butaca_id"]) in elegidas and butaca["estado_disponibilidad"] == "disponible":
            butacas.append({"id": butaca["butaca_id"], "codigo": butaca["fila"] + str(butaca["numero"])})

    pedidos = []
    cantidades = {}
    for servicio in servicios:
        cant_servicio = datos.get("srv_" + str(servicio["id"]), 0, type=int)
        if cant_servicio > 0:
            pedidos.append({"id": servicio["id"], "nombre": servicio["nombre"], "cantidad": cant_servicio,
                            "subtotal": cant_servicio * servicio["precio"]})
            cantidades[servicio["id"]] = cant_servicio

    subtotal_entradas = cantidad * funcion["precio_base"]
    total = subtotal_entradas
    for pedido in pedidos:
        total = total + pedido["subtotal"]

    parametros = {}
    if cantidad:
        parametros["cantidad"] = [cantidad]
    if butacas:
        parametros["butacas"] = []
        for butaca in butacas:
            parametros["butacas"].append(butaca["id"])
    for servicio_id, cant_servicio in cantidades.items():
        parametros["srv_" + str(servicio_id)] = [cant_servicio]

    return {"cantidad_entradas": cantidad, "subtotal_entradas": subtotal_entradas,
            "butacas": butacas, "servicios": pedidos, "cantidades": cantidades, "total": total,
            "parametros": parametros, "maximo_entradas": maximo_entradas}


def cargar_compra(pelicula_id, funcion_id):
    pelicula, estado = get_pelicula(pelicula_id)
    if estado != 200:
        return None, manejar_error(pelicula, estado)

    funcion, estado = get_funcion(pelicula_id, funcion_id)
    if estado != 200:
        return None, manejar_error(funcion, estado)

    butacas_sala, estado = get_butacas(funcion_id)
    if estado != 200:
        return None, manejar_error(butacas_sala, estado)

    servicios, estado = get_servicios()
    if estado != 200:
        return None, manejar_error(servicios, estado)

    resumen = armar_resumen(funcion, butacas_sala, servicios, request.values)
    contexto = {"pelicula": pelicula, "funcion": funcion, "butacas_sala": butacas_sala,
                "servicios": servicios, "resumen": resumen}
    return contexto, None


def revisar_cantidad(contexto):
    if contexto["resumen"]["cantidad_entradas"] >= 1:
        return None
    flash("Elegí cuántas entradas querés para continuar.", "warning")
    return redirect(url_for("compra.entradas", pelicula_id=contexto["pelicula"]["id"],
                            funcion_id=contexto["funcion"]["funcion_id"]))


def revisar_butacas(contexto):
    """Devuelve None si hay elegida exactamente una butaca disponible por entrada;
    si no, manda al usuario de vuelta al mapa de butacas. Si alguna butaca elegida se ocupó
    mientras tanto, armar_resumen ya la descartó y cae por acá."""
    respuesta = revisar_cantidad(contexto)
    if respuesta is not None:
        return respuesta
    resumen = contexto["resumen"]
    if len(resumen["butacas"]) == resumen["cantidad_entradas"]:
        return None
    flash("Elegí " + str(resumen["cantidad_entradas"]) + " butacas disponibles para continuar.", "warning")
    return redirect(url_for("compra.butacas", pelicula_id=contexto["pelicula"]["id"],
                            funcion_id=contexto["funcion"]["funcion_id"], **resumen["parametros"]))


@compra_bp.route("/horario/<int:pelicula_id>")
def horario(pelicula_id):
    pelicula, estado = get_pelicula(pelicula_id)
    if estado != 200:
        return manejar_error(pelicula, estado)

    funciones, estado = get_funciones(pelicula_id)
    if estado != 200:
        return manejar_error(funciones, estado)

    return render_template("compra/horario.html", pelicula=pelicula, funcion=None, resumen=None,
                           locales=agrupar_por_local(funciones))


@compra_bp.route("/<int:pelicula_id>/<int:funcion_id>/entradas")
def entradas(pelicula_id, funcion_id):
    contexto, error = cargar_compra(pelicula_id, funcion_id)
    if error is not None:
        return error
    return render_template("compra/entradas.html", **contexto)


@compra_bp.route("/<int:pelicula_id>/<int:funcion_id>/butacas")
def butacas(pelicula_id, funcion_id):
    contexto, error = cargar_compra(pelicula_id, funcion_id)
    if error is not None:
        return error
    respuesta = revisar_cantidad(contexto)
    if respuesta is not None:
        return respuesta
    return render_template("compra/butacas.html", **contexto)


@compra_bp.route("/<int:pelicula_id>/<int:funcion_id>/comida")
def comida(pelicula_id, funcion_id):
    contexto, error = cargar_compra(pelicula_id, funcion_id)
    if error is not None:
        return error
    respuesta = revisar_butacas(contexto)
    if respuesta is not None:
        return respuesta
    return render_template("compra/comida.html", **contexto)


@compra_bp.route("/<int:pelicula_id>/<int:funcion_id>/confirmacion")
def confirmacion(pelicula_id, funcion_id):
    contexto, error = cargar_compra(pelicula_id, funcion_id)
    if error is not None:
        return error
    respuesta = revisar_butacas(contexto)
    if respuesta is not None:
        return respuesta
    return render_template("compra/confirmacion.html", **contexto)


def validar_tarjeta(form):
    errores = []

    titular = form.get("titular", "").strip()
    numero = form.get("numero", "").replace(" ", "")
    vencimiento = form.get("vencimiento", "").strip()
    cvv = form.get("cvv", "").strip()

    if not titular or not all(c.isalpha() or c in " '-" for c in titular):
        errores.append("Ingresá el nombre del titular (solo letras).")

    if not (13 <= len(numero) <= 19 and numero.isascii() and numero.isdigit()):
        errores.append("El número de tarjeta debe tener solo números (entre 13 y 19 dígitos).")

    partes = vencimiento.split("/")
    formato_valido = (
        len(vencimiento) == 5
        and len(partes) == 2
        and len(partes[0]) == 2
        and len(partes[1]) == 2
        and all(parte.isascii() and parte.isdigit() for parte in partes)
    )

    if not formato_valido or not (1 <= int(partes[0]) <= 12):
        errores.append("El vencimiento debe tener el formato MM/AA.")
    else:
        mes = int(partes[0])
        anio = 2000 + int(partes[1])
        hoy = datetime.now()
        if (anio, mes) < (hoy.year, hoy.month):
            errores.append("La tarjeta está vencida.")

    if not (len(cvv) in (3, 4) and cvv.isascii() and cvv.isdigit()):
        errores.append("El CVV debe tener solo números (3 o 4 dígitos).")

    return errores


def fallar_compra(compra_id, mensaje, estado):
    """Algo falló después de crear la compra. Devuelve lo mismo que registrar_compra:
    (None, False, (mensaje, estado))."""
    if estado == 503:
        mensaje = ("No pudimos confirmar si tu pago se completó. Revisá tus entradas en tu "
                   "perfil antes de volver a intentar.")
    else:
        cancelar_compra(compra_id, "No se pudo completar el pago")
    return None, False, (mensaje, estado)


def registrar_compra(funcion, resumen):
    butaca_ids = []
    for butaca in resumen["butacas"]:
        butaca_ids.append(butaca["id"])

    compra, estado = crear_compra(funcion["funcion_id"], butaca_ids)
    if estado >= 400:
        return None, False, (compra, estado)
    compra_id = compra["compra_id"]

    for servicio in resumen["servicios"]:
        respuesta, estado = agregar_servicio(compra_id, servicio["id"], servicio["cantidad"])
        if estado >= 400:
            return fallar_compra(compra_id, respuesta, estado)

    pago, estado = pagar_compra(compra_id)
    if estado >= 400:
        return fallar_compra(compra_id, pago, estado)

    if pago is None:  # el backend pudo contestar 204 sin cuerpo
        pago = {}
    return compra_id, pago.get("email_enviado", False), None


@compra_bp.route("/<int:pelicula_id>/<int:funcion_id>/pago", methods=["GET", "POST"])
def pago(pelicula_id, funcion_id):
    contexto, error = cargar_compra(pelicula_id, funcion_id)
    if error is not None:
        return error
    respuesta = revisar_butacas(contexto)
    if respuesta is not None:
        return respuesta

    datos = {"titular": "", "numero": "", "vencimiento": ""}

    if request.method == "POST":
        errores = validar_tarjeta(request.form)
        if not errores:
            compra_id, email_enviado, error = registrar_compra(contexto["funcion"], contexto["resumen"])
            if error is not None:
                mensaje, estado = error
                if estado != 409:
                    return manejar_error(mensaje, estado)
                # 409 = conflicto: alguien se quedó con una butaca, la función ya empezó, etc.
                flash(mensaje, "danger")
                return redirect(url_for("compra.butacas", pelicula_id=pelicula_id, funcion_id=funcion_id,
                                        cantidad=contexto["resumen"]["cantidad_entradas"]))
            # mail=0 solo se agrega si el mail con el QR no se pudo enviar
            if email_enviado:
                return redirect(url_for("compra.exito", compra_id=compra_id))
            return redirect(url_for("compra.exito", compra_id=compra_id, mail=0))

        for mensaje in errores:
            flash(mensaje, "danger")
        datos = {
            "titular": request.form.get("titular", ""),
            "numero": request.form.get("numero", ""),
            "vencimiento": request.form.get("vencimiento", ""),
        }

    return render_template("compra/pago.html", datos=datos, **contexto)


@compra_bp.route("/exito/<int:compra_id>")
def exito(compra_id):
    compra, estado = get_compra(compra_id)
    if estado != 200:
        return manejar_error(compra, estado)
    mail_enviado = request.args.get("mail") != "0"
    return render_template("compra/exito.html", compra=compra, mail_enviado=mail_enviado)
