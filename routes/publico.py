# Pantallas públicas: cartelera, detalle de película, login y perfil.
import unicodedata
import requests
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from services.api import API_URL, encabezado_auth
from services import mock_data
from services.auth import revisar_login

publico_bp = Blueprint("publico", __name__)

@publico_bp.route("/")
def cartelera():
    peliculas = mock_data.get_peliculas()
    return render_template("index.html", peliculas=peliculas)

def sin_acentos(texto):
    #Pasa a minúsculas y quita los acentos para que siempre coincida
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn") #saca acentos y espacios 

@publico_bp.route("/peliculas")
def peliculas():
    busqueda = request.args.get("q", "").strip()
    todas = mock_data.get_peliculas()

    if busqueda:
        buscado = sin_acentos(busqueda)
        resultado = []
        for peli in todas:
            if buscado in sin_acentos(peli["titulo"]):
                resultado.append(peli)
    else:
        resultado = todas

    return render_template("cartelera.html", peliculas=resultado, busqueda=busqueda)

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

    respuesta_perfil = requests.get(f"{API_URL}/usuarios/perfil", headers=encabezado_auth())
    respuesta_compras = requests.get(f"{API_URL}/compras?per_page=100", headers=encabezado_auth())

    if respuesta_perfil.status_code != 200 or respuesta_compras.status_code != 200:
        flash("No se pudo cargar tu perfil. Iniciá sesión de nuevo.", "danger")
        return redirect(url_for("publico.login"))

    perfil_usuario = respuesta_perfil.json()
    historial = respuesta_compras.json()["data"]

    vistas = 0 

    for compra in historial:
        if compra["estado"] == "usada":
            vistas = vistas + 1
    return render_template("perfil.html", usuario=perfil_usuario["datos_personales"], historial=historial, vistas=vistas)

@publico_bp.route("/perfil/editar", methods=["GET", "POST"])
def editar_perfil():
    respuesta = revisar_login()
    if respuesta is not None:
        return respuesta

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        contraseña = request.form.get("contraseña", "").strip()
        if not nombre or "@" not in email:
            flash("Ingresá un nombre y un correo electrónico válido.", "danger")
            return render_template("editar_perfil.html", usuario=session["usuario"])

        usuario = dict(session["usuario"])
        usuario.update({"nombre": nombre, "email": email, "contraseña": contraseña})
        session["usuario"] = usuario
        flash("Tus datos se actualizaron correctamente.", "success")
        return redirect(url_for("publico.perfil"))

    return render_template("editar_perfil.html", usuario=session["usuario"])

@publico_bp.route("/registro")
def registro():
    return render_template("registro.html")

