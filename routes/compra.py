# Flujo de compra: horario -> entradas -> butacas -> comida -> confirmación -> pago.
# Como todavía no hay base de datos, lo que elige el usuario viaja en la URL
# (por ejemplo ?general=2&butacas=B4) y se va pasando de un paso al siguiente.
from flask import Blueprint, abort, redirect, render_template, request, url_for

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


@compra_bp.route("/<int:funcion_id>/pago", methods=["GET", "POST"])
def pago(funcion_id):
    # POST = el usuario apretó "Confirmar compra"
    if request.method == "POST":
        return redirect(url_for("compra.exito"))  # Hito 3: acá se guarda la compra en el backend
    funcion, pelicula, resumen = cargar_compra(funcion_id)
    return render_template("compra/pago.html", funcion=funcion, pelicula=pelicula, resumen=resumen)


@compra_bp.route("/exito")
def exito():
    return render_template("compra/exito.html")
