from flask import Blueprint, redirect, render_template, request, session, url_for

from services import mock_data
from services.auth import revisar_admin
from services.api import llamar_api


admin_bp = Blueprint("admin", __name__)


@admin_bp.before_request
def proteger():
    return revisar_admin()


def consultar_api(metodo, endpoint, datos=None):
    try:
        respuesta = llamar_api(metodo, endpoint, datos)

    except Exception:
        return None, ("No se pudo conectar con el Backend", 503)

    if respuesta.status_code == 401:
        session.clear()
        return None, redirect(url_for("publico.login"))

    if respuesta.status_code == 403:
        return None, ("No tiene permisos de administrador", 403)

    return respuesta, None


def obtener_error(respuesta):
    try:
        datos = respuesta.json()
        errores = datos.get("errors", [])

        if errores:
            return errores[0].get(
                "description",
                "No se pudo completar la operación"
            )

    except Exception:
        return "No se pudo completar la operación"

    return "No se pudo completar la operación"


@admin_bp.route("/backoffice")
def dashboard():
    return render_template("admin/dashboard.html", est=mock_data.get_estadisticas())


@admin_bp.route("/peliculas", methods=["GET", "POST"])
def peliculas():
    if request.method == "POST":
        imagen = request.files.get("imagen")

        if imagen is not None and imagen.filename:
            return "El Backend recibe una URL del póster, no un archivo", 400

        datos = {
            "titulo": request.form.get("titulo", "").strip(),
            "sinopsis": request.form.get("sinopsis", "").strip()
        }

        respuesta, error = consultar_api("POST", "admin/peliculas", datos)

        if error is not None:
            return error

        if respuesta.status_code == 201:
            return redirect(url_for("admin.peliculas"))

        return obtener_error(respuesta), respuesta.status_code

    respuesta, error = consultar_api(
        "GET", "admin/peliculas"
    )

    if error is not None:
        return error

    if respuesta.status_code != 200:
        return obtener_error(respuesta), respuesta.status_code

    lista_peliculas = respuesta.json()

    for pelicula in lista_peliculas:
        pelicula["poster"] = pelicula.get("poster_url")
        pelicula["duracion"] = pelicula.get("duracion_min")

    return render_template(
        "admin/peliculas.html",
        peliculas=lista_peliculas,
        cines=mock_data.get_cines()
    )


@admin_bp.route("/servicios")
def servicios():
    respuesta, error = consultar_api("GET", "admin/servicios")

    if error is not None:
        return error

    if respuesta.status_code == 200:
        lista_servicios = respuesta.json()

    elif respuesta.status_code == 404:
        lista_servicios = []

    else:
        return obtener_error(respuesta), respuesta.status_code

    for servicio in lista_servicios:
        servicio["activo"] = True

    return render_template(
        "admin/servicios.html",
        servicios=lista_servicios
    )


@admin_bp.route("/servicios/guardar", methods=["POST"])
def guardar_servicio():
    try:
        precio = float(request.form.get("precio", ""))

    except ValueError:
        return "El precio debe ser un número válido", 400

    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "categoria": request.form.get("categoria", "").strip(),
        "precio": precio
    }

    respuesta, error = consultar_api("POST", "admin/servicios", datos)

    if error is not None:
        return error

    if respuesta.status_code == 201:
        return redirect(url_for("admin.servicios"))

    return obtener_error(respuesta), respuesta.status_code


@admin_bp.route("/servicios/<int:servicio_id>/baja", methods=["POST"])
def baja_servicio(servicio_id):

    respuesta, error = consultar_api("DELETE", f"admin/servicios/{servicio_id}")

    if error is not None:
        return error

    if respuesta.status_code == 200:
        return redirect(url_for("admin.servicios"))

    return obtener_error(respuesta), respuesta.status_code
