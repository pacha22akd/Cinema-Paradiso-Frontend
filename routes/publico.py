# Pantallas públicas: cartelera, detalle de película, login y perfil.
import unicodedata
import requests
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for, current_app
from services.api import API_URL, encabezado_auth
from services import mock_data
from services.auth import revisar_login
from services.api import llamar_api

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


@publico_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Usamos el wrapper de tu compañero
        respuesta = llamar_api(
            metodo="POST", 
            endpoint="/sesiones", 
            datos={"email": email, "password": password}
        )

        # Si el servidor no responde (timeout o apagado)
        if respuesta is None:
            flash("Error de conexión con el servidor", "error")
            return render_template('login.html')

        if respuesta.status_code == 200:
            datos = respuesta.json()
            
            # Guardamos en la sesión del Front
            session['token'] = datos['token']
            session['usuario_nombre'] = datos['usuario']['nombre']
            session['usuario_id'] = datos['usuario']['id']
            session['rol'] = datos['usuario']['rol'] 

            # Redirigimos según el rol
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if session['rol'] == 'administrador':
                return redirect(url_for('admin.dashboard')) 
            
            return redirect(url_for('publico.cartelera'))
            
        else:
            # Leemos el JSON de error del backend
            error_data = respuesta.json()
            mensaje = error_data.get('errors', [{}])[0].get('description', 'Credenciales inválidas')
            flash(mensaje, 'error')

    return render_template('login.html')


@publico_bp.route('/logout')
def logout():
    session.clear() # Borra el token y todos los datos
    flash("Sesión cerrada correctamente", "exito")
    return redirect(url_for('publico.cartelera'))


@publico_bp.route('/perfil')
def perfil():
    # Llamamos a tu función. Si no está logueado, devuelve una redirección.
    redireccion = revisar_login()
    if redireccion:
        return redireccion
        
    # Si pasa, significa que está logueado. Pedimos los datos al backend.
    respuesta_perfil = llamar_api("GET", "/usuarios/perfil")
    respuesta_compras = llamar_api("GET", "/compras", parametros={"per_page": 100})

    if respuesta_perfil.status_code != 200 or respuesta_compras.status_code != 200:
        flash("No se pudo cargar tu perfil. Iniciá sesión de nuevo.", "danger")
        return redirect(url_for('publico.login'))

    historial = respuesta_compras.json()["data"]

    vistas = 0
    for compra in historial:
        if compra["estado"] == "usada":
            vistas = vistas + 1

    return render_template('perfil.html', perfil=respuesta_perfil.json(), historial=historial, vistas=vistas)

@publico_bp.route("/perfil/editar", methods=["GET", "POST"])
def editar_perfil():
    respuesta = revisar_login()
    if respuesta is not None:
        return respuesta

    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", ""),
            "apellido": request.form.get("apellido", ""),
            "telefono": request.form.get("telefono", ""),
            "email": request.form.get("email", ""),
        }

        # La contraseña es opcional: si queda vacía, no se cambia
        password = request.form.get("password", "")
        if password != "":
            datos["password"] = password
            
        respuesta_api = llamar_api("PATCH", "/usuarios/perfil", datos=datos)

        if respuesta_api.status_code == 200:
            actualizado = respuesta_api.json()
            # Se actualiza la sesión para que la barra de arriba muestre el nombre nuevo
            session["usuario_nombre"] = actualizado["nombre"]
            flash("Tus datos se actualizaron correctamente.", "success")
            return redirect(url_for("publico.perfil"))

        # El backend explica el error (email repetido, formato inválido, etc.)
        error = respuesta_api.json()["errors"][0]["description"]
        flash(error, "danger")
        return render_template("editar_perfil.html", usuario=datos)

    # GET: se traen los datos actuales para completar el formulario
    respuesta_api = llamar_api("GET", "/usuarios/perfil")
    if respuesta_api.status_code != 200:
        flash("No se pudo cargar tu perfil. Iniciá sesión de nuevo.", "danger")
        return redirect(url_for("publico.login"))

    return render_template("editar_perfil.html", usuario=respuesta_api.json()["datos_personales"])

@publico_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        confirmar_password = request.form.get('confirmar_password')

        # Validación local en el front
        if password != confirmar_password:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for('publico.registro'))

        # Preparamos el JSON
        datos_registro = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "telefono": telefono,
            "password": password
        }

        # Usamos el wrapper de tu compañero
        respuesta = llamar_api(
            metodo="POST", 
            endpoint="/usuarios", 
            datos=datos_registro
        )

        if respuesta is None:
            flash("Error de conexión con el servidor.", "error")
            return render_template('registro.html')

        if respuesta.status_code == 201:
            flash("¡Registro exitoso! Ya podés iniciar sesión.", "exito")
            return redirect(url_for('publico.login'))
        else:
            error_data = respuesta.json()
            mensaje = error_data.get('errors', [{}])[0].get('description', 'Error al registrar')
            flash(mensaje, 'error')

    return render_template('registro.html')