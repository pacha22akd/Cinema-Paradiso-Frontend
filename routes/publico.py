# Pantallas públicas: cartelera, detalle de película, login y perfil.
import unicodedata
import requests
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for, current_app
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


@publico_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # 1. Petición al Backend (JWT)
            respuesta = requests.post(
                f"{current_app.config['API_URL']}/sesiones", 
                json={"email": email, "password": password}
            )

            if respuesta.status_code == 200:
                datos = respuesta.json()
                
                # 2. Guardamos los datos en la sesión del Frontend
                session['token'] = datos['token']
                session['usuario_nombre'] = datos['usuario']['nombre']
                session['usuario_id'] = datos['usuario']['id']
                session['rol'] = datos['usuario']['rol'] # Guarda 'administrador' o 'cliente'

                # 3. Redirigimos según el rol
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)

                if session['rol'] == 'administrador':
                    return redirect(url_for('admin.dashboard')) 
                
                return redirect(url_for('publico.cartelera'))
                
            else:
                # Si el back devolvió error (400, 401, 403)
                error_data = respuesta.json()
                mensaje = error_data.get('errors', [{}])[0].get('description', 'Credenciales inválidas')
                flash(mensaje, 'error')

        except requests.exceptions.RequestException:
            flash("Error de conexión con el servidor", "error")

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
    headers = {"Authorization": f"Bearer {session['token']}"}
    respuesta = requests.get(f"{current_app.config['API_URL']}/usuarios/perfil", headers=headers)
    
    if respuesta.status_code == 200:
        return render_template('perfil.html', perfil=respuesta.json())
    
    return redirect(url_for('publico.login'))

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
            
        respuesta_api = requests.patch(f"{API_URL}/usuarios/perfil", json=datos, headers=encabezado_auth())

        if respuesta_api.status_code == 200:
            actualizado = respuesta_api.json()
            # Se actualiza la sesión para que la barra de arriba muestre el nombre nuevo
            usuario = dict(session["usuario"])
            usuario["nombre"] = actualizado["nombre"]
            usuario["email"] = actualizado["email"]
            session["usuario"] = usuario
            flash("Tus datos se actualizaron correctamente.", "success")
            return redirect(url_for("publico.perfil"))

        # El backend explica el error (email repetido, formato inválido, etc.)
        error = respuesta_api.json()["errors"][0]["description"]
        flash(error, "danger")
        return render_template("editar_perfil.html", usuario=datos)

    # GET: se traen los datos actuales para completar el formulario
    respuesta_api = requests.get(f"{API_URL}/usuarios/perfil", headers=encabezado_auth())
    if respuesta_api.status_code != 200:
        flash("No se pudo cargar tu perfil. Iniciá sesión de nuevo.", "danger")
        return redirect(url_for("publico.login"))

    return render_template("editar_perfil.html", usuario=respuesta_api.json()["datos_personales"])

@publico_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # 1. Capturamos los datos del formulario HTML
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        confirmar_password = request.form.get('confirmar_password')

        # 2. Validación rápida en el frontend: ¿Las contraseñas coinciden?
        if password != confirmar_password:
            flash("Las contraseñas no coinciden. Intentalo de nuevo.", "error")
            return redirect(url_for('publico.registro'))

        # 3. Preparamos el JSON para el backend
        datos = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "telefono": telefono,
            "password": password
        }

        try:
            # 4. Hacemos la petición POST al endpoint de usuarios del backend
            respuesta = requests.post(
                f"{current_app.config['API_URL']}/usuarios", 
                json=datos
            )

            if respuesta.status_code == 201:
                # Si el backend responde 201 Created, fue un éxito
                flash("¡Registro exitoso! Ya podés iniciar sesión.", "exito")
                return redirect(url_for('publico.login'))
            else:
                # Si hubo un error (400 por validación, 409 por duplicado)
                error_data = respuesta.json()
                mensaje = error_data.get('errors', [{}])[0].get('description', 'Error al registrar el usuario')
                flash(mensaje, 'error')

        except requests.exceptions.RequestException:
            flash("Error de conexión con el servidor. Intentá más tarde.", "error")

    # Si es GET, muestra el template de registro
    return render_template('registro.html')