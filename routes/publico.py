# Pantallas públicas: cartelera, detalle de película, login y perfil.
import unicodedata
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from services import mock_data
from services.auth import revisar_login
from services.api import llamar_api

publico_bp = Blueprint("publico", __name__)

@publico_bp.route("/")
def cartelera():
    peliculas = mock_data.get_peliculas()
    return render_template("index.html", peliculas=peliculas)

def sin_acentos(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn")

@publico_bp.route("/peliculas")
def peliculas():
    busqueda = request.args.get("q", "").strip()
    todas = mock_data.get_peliculas()

    if busqueda:
        buscado = sin_acentos(busqueda)
        resultado = [peli for peli in todas if buscado in sin_acentos(peli["titulo"])]
    else:
        resultado = todas

    return render_template("cartelera.html", peliculas=resultado, busqueda=busqueda)

@publico_bp.route("/pelicula/<int:pelicula_id>")
def pelicula(pelicula_id):
    peli = mock_data.get_pelicula(pelicula_id)
    if peli is None:
        abort(404)
    cines = mock_data.get_cines()
    funciones = mock_data.get_funciones(pelicula_id)
    return render_template("pelicula.html", pelicula=peli, cines=cines, funciones=funciones)


@publico_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # La nueva función devuelve (datos, status_code)
        respuesta, status_code = llamar_api(
            metodo="POST", 
            endpoint="/sesiones", 
            datos={"email": email, "password": password}
        )

        if status_code == 200:
            # 'respuesta' ahora ya es el diccionario con los datos, no hace falta .json()
            session['token'] = respuesta['token']
            session['usuario_nombre'] = respuesta['usuario']['nombre']
            session['usuario_id'] = respuesta['usuario']['id']
            session['rol'] = respuesta['usuario']['rol']
            session['usuario_email'] = respuesta['usuario']['email']

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if session['rol'] == 'administrador':
                return redirect(url_for('admin.dashboard')) 
            
            return redirect(url_for('publico.cartelera'))
            
        else:
            # Si falla, 'respuesta' ya es el string con el mensaje de error
            flash(respuesta, 'error')

    return render_template('login.html')


@publico_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "exito")
    return redirect(url_for('publico.cartelera'))


@publico_bp.route('/perfil')
def perfil():
    redireccion = revisar_login()
    if redireccion:
        return redireccion
        
    respuesta_perfil, status_perfil = llamar_api("GET", "/usuarios/perfil")
    respuesta_compras, status_compras = llamar_api("GET", "/compras", parametros={"per_page": 100})

    if status_perfil != 200 or status_compras != 200:
        flash("No se pudo cargar tu perfil. Iniciá sesión de nuevo.", "danger")
        return redirect(url_for('publico.login'))

    # 'respuesta_compras' ya es un dict, accedemos directo a 'data'
    historial = respuesta_compras["data"]

    vistas = sum(1 for compra in historial if compra["estado"] == "usada")

    # 'respuesta_perfil' ya es un dict
    return render_template('perfil.html', perfil=respuesta_perfil, historial=historial, vistas=vistas)

@publico_bp.route("/perfil/compras/<int:compra_id>/reenviar_mail", methods=["POST"])
def reenviar_mail(compra_id):
    redireccion = revisar_login()
    if redireccion:
        return redireccion

    respuesta, status = llamar_api("POST", f"/compras/{compra_id}/reenviar_mail")

    if status == 200:
        flash("Te reenviamos el mail con tus entradas.", "success")
    else:
        flash(respuesta, "danger") # 'respuesta' ya es el mensaje de error

    return redirect(url_for("publico.perfil"))

@publico_bp.route("/perfil/editar", methods=["GET", "POST"])
def editar_perfil():
    respuesta_auth = revisar_login()
    if respuesta_auth is not None:
        return respuesta_auth

    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", ""),
            "apellido": request.form.get("apellido", ""),
            "telefono": request.form.get("telefono", ""),
            "email": request.form.get("email", ""),
        }

        password = request.form.get("password", "")
        if password != "":
            datos["password"] = password
            
        respuesta_api, status = llamar_api("PATCH", "/usuarios/perfil", datos=datos)

        if status == 200:
            session["usuario_nombre"] = respuesta_api["nombre"]
            flash("Tus datos se actualizaron correctamente.", "success")
            return redirect(url_for("publico.perfil"))

        flash(respuesta_api, "danger") # 'respuesta_api' es el mensaje de error
        return render_template("editar_perfil.html", usuario=datos)

    # GET
    respuesta_api, status = llamar_api("GET", "/usuarios/perfil")
    if status != 200:
        flash("No se pudo cargar tu perfil. Iniciá sesión de nuevo.", "danger")
        return redirect(url_for("publico.login"))

    return render_template("editar_perfil.html", usuario=respuesta_api["datos_personales"])

@publico_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        confirmar_password = request.form.get('confirmar_password')

        if password != confirmar_password:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for('publico.registro'))

        datos_registro = {
            "nombre": nombre, "apellido": apellido, "email": email,
            "telefono": telefono, "password": password
        }

        respuesta, status = llamar_api(metodo="POST", endpoint="/usuarios", datos=datos_registro)

        if status == 201:
            flash("¡Registro exitoso! Ya podés iniciar sesión.", "exito")
            return redirect(url_for('publico.login'))
        else:
            flash(respuesta, 'error')

    return render_template('registro.html')