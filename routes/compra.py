# Flujo de compra: horario -> entradas -> butacas -> comida -> confirmación -> pago.
# Como todavía no hay base de datos, lo que elige el usuario viaja en la URL
# (por ejemplo ?general=2&butacas=B4) y se va pasando de un paso al siguiente.
from datetime import datetime
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from services import mock_data
from services.auth import revisar_login

compra_bp = Blueprint("compra", __name__)

@compra_bp.before_request
def proteger():
    # Se ejecuta antes de CUALQUIER ruta de compra: hay que estar logueado
    return revisar_login()


def armar_resumen(datos):
    """Con lo que eligió el usuario, calcula las entradas, los servicios y el total."""
    entradas = []
    for tipo in mock_data.get_tipos_entrada():
        cantidad = datos.get(tipo["clave"], 0, type=int)
        if cantidad > 0:
            entradas.append({"nombre": tipo["nombre"], "cantidad": cantidad,
                             "subtotal": cantidad * tipo["precio"]})

    servicios = []
    for servicio in mock_data.get_servicios():
        cantidad = datos.get("srv_" + str(servicio["id"]), 0, type=int)
        if cantidad > 0 and servicio["activo"]:
            servicios.append({"nombre": servicio["nombre"], "cantidad": cantidad,
                              "subtotal": cantidad * servicio["precio"]})

    total = 0
    cantidad_entradas = 0
    for entrada in entradas:
        total = total + entrada["subtotal"]
        cantidad_entradas = cantidad_entradas + entrada["cantidad"]
    for servicio in servicios:
        total = total + servicio["subtotal"]

    return {"entradas": entradas, "servicios": servicios, "butacas": datos.getlist("butacas"),
            "cantidad_entradas": cantidad_entradas, "total": total}


def cargar_compra(funcion_id):
    """Busca la función, su película y calcula el resumen. Lo usan todos los pasos."""
    funcion = mock_data.get_funcion(funcion_id)
    if funcion is None:
        abort(404)
    pelicula = mock_data.get_pelicula(funcion["pelicula_id"])
    resumen = armar_resumen(request.values)
    return funcion, pelicula, resumen


@compra_bp.route("/horario/<int:pelicula_id>")
def horario(pelicula_id):
    pelicula = mock_data.get_pelicula(pelicula_id)
    if pelicula is None:
        abort(404)
    return render_template("compra/horario.html", pelicula=pelicula, funcion=None, resumen=None,
                           funciones=mock_data.get_funciones(pelicula_id), cines=mock_data.get_cines())


@compra_bp.route("/<int:funcion_id>/entradas")
def entradas(funcion_id):
    funcion, pelicula, resumen = cargar_compra(funcion_id)
    return render_template("compra/entradas.html", funcion=funcion, pelicula=pelicula,
                           resumen=resumen, tipos=mock_data.get_tipos_entrada())


@compra_bp.route("/<int:funcion_id>/butacas")
def butacas(funcion_id):
    funcion, pelicula, resumen = cargar_compra(funcion_id)
    filas, columnas, ocupadas = mock_data.get_mapa_butacas()
    return render_template("compra/butacas.html", funcion=funcion, pelicula=pelicula,
                           resumen=resumen, filas=filas, columnas=columnas, ocupadas=ocupadas)


@compra_bp.route("/<int:funcion_id>/comida")
def comida(funcion_id):
    funcion, pelicula, resumen = cargar_compra(funcion_id)
    servicios = []
    for servicio in mock_data.get_servicios():
        if servicio["activo"]:
            servicios.append(servicio)
    return render_template("compra/comida.html", funcion=funcion, pelicula=pelicula,
                           resumen=resumen, servicios=servicios)


@compra_bp.route("/<int:funcion_id>/confirmacion")
def confirmacion(funcion_id):
    funcion, pelicula, resumen = cargar_compra(funcion_id)
    return render_template("compra/confirmacion.html", funcion=funcion, pelicula=pelicula, resumen=resumen)

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

@compra_bp.route("/<int:funcion_id>/pago", methods=["GET", "POST"])
def pago(funcion_id):
    funcion, pelicula, resumen = cargar_compra(funcion_id)
    datos = {"titular": "", "numero": "", "vencimiento": ""}

    if request.method == "POST":
        errores = validar_tarjeta(request.form)
        if not errores:
            return redirect(url_for("compra.exito"))
        for error in errores:
            flash(error, "danger")
        datos = {
            "titular": request.form.get("titular", ""),
            "numero": request.form.get("numero", ""),
            "vencimiento": request.form.get("vencimiento", ""),
        }

    return render_template("compra/pago.html", funcion=funcion, pelicula=pelicula,
                           resumen=resumen, datos=datos)

@compra_bp.route("/exito")
def exito():
    return render_template("compra/exito.html")
