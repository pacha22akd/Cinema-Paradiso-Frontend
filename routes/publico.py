# Pantallas públicas: cartelera, detalle de película, login y perfil.
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from services import mock_data
from services.auth import revisar_login

publico_bp = Blueprint("publico", __name__)


@publico_bp.route("/")
def cartelera():
    peliculas = mock_data.get_peliculas()
    return render_template("index.html", peliculas=peliculas)


@publico_bp.route("/pelicula/<int:pelicula_id>")
def pelicula(pelicula_id):
    peli = mock_data.get_pelicula(pelicula_id)
    if peli is None:
        abort(404)  # la película no existe
    cines = mock_data.get_cines()
    funciones = mock_data.get_funciones(pelicula_id)
    return render_template("pelicula.html", pelicula=peli, cines=cines, funciones=funciones)


@publico_bp.route("/login", methods=["GET", "POST"])
def login():
    # POST = el usuario apretó el botón "Iniciar sesión"
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        usuario = mock_data.autenticar(email, password)

        if usuario is None:
            flash("Correo o contraseña incorrectos.", "danger")
            return redirect(url_for("publico.login"))

        session.clear()
        session["usuario"] = usuario  # guardamos el usuario en la sesión

        if usuario["rol"] == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("publico.cartelera"))

    # GET = el usuario recién entró a la página, mostramos el formulario
    return render_template("login.html")


@publico_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()  # borramos la sesión
    return redirect(url_for("publico.cartelera"))


@publico_bp.route("/perfil")
def perfil():
    respuesta = revisar_login()
    if respuesta is not None:
        return respuesta

    historial = mock_data.get_historial()
    vistas = 0
    for compra in historial:
        if compra["estado"] == "Utilizada":
            vistas = vistas + 1
    return render_template("perfil.html", usuario=session["usuario"], historial=historial, vistas=vistas)

