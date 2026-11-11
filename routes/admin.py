# Backoffice del administrador. Todas las rutas de acá empiezan con /admin.
import requests
from flask import Blueprint, redirect, render_template, request, session, url_for, current_app
from services.api import llamar_api 
from services import mock_data
from services.auth import revisar_admin

admin_bp = Blueprint("admin", __name__)

@admin_bp.before_request
def proteger():
    # Se ejecuta antes de CUALQUIER ruta de admin: hay que ser administrador
    return revisar_admin()

def responder_error_api(mensaje, estado):
    if estado == 401:
        session.clear()
        return redirect(url_for("publico.login"))

    return str(mensaje), estado

def leer_datos_pelicula():
    datos = {
        "titulo": request.form.get("titulo", "").strip(),
        "sinopsis": request.form.get("sinopsis", "").strip(),
        "poster_url": request.form.get("poster_url", "").strip(),
        "genero": request.form.get("genero", "").strip(),
        "clasificacion": request.form.get("clasificacion", "").strip(),
        "api_id": request.form.get("api_id", "").strip()
    }

    for campo in ("duracion_min", "anio_estreno"):
        valor = request.form.get(campo, "").strip()

        if valor == "":
            datos[campo] = None

        else:
            try:
                datos[campo] = int(valor)

            except ValueError:
                return None, f"El campo {campo} debe ser un numero entero"

    return datos, None

@admin_bp.route("/peliculas", methods=["GET", "POST"])
def peliculas():
    if request.method == "POST":
        datos, error = leer_datos_pelicula()

        if error is not None:
            return error, 400

        if request.form.get("accion") == "precargar":
            lista, estado = llamar_api("GET", "/admin/peliculas")

            if estado != 200:
                return responder_error_api(lista, estado)

            return render_template("admin/peliculas.html", peliculas=lista, pelicula_editar=None, pelicula_precarga=datos)

        resultado, estado = llamar_api("POST", "/admin/peliculas", datos=datos)

        if estado == 201:
            return redirect(url_for("admin.peliculas"))

        return responder_error_api(resultado, estado)

    lista, estado = llamar_api("GET", "/admin/peliculas")

    if estado != 200:
        return responder_error_api(lista, estado)

    pelicula_editar = None
    id_editar = request.args.get("editar", type=int)

    if id_editar is not None:
        for pelicula in lista:
            if pelicula["id"] == id_editar:
                pelicula_editar = pelicula

        if pelicula_editar is None:
            return "La pelicula solicitada no existe", 404

    return render_template("admin/peliculas.html", peliculas=lista, pelicula_editar=pelicula_editar, pelicula_precarga=None)

@admin_bp.route("/peliculas/<int:pelicula_id>/editar", methods=["POST"])
def editar_pelicula(pelicula_id):
    datos, error = leer_datos_pelicula()

    if error is not None:
        return error, 400

    resultado, estado = llamar_api("PATCH", f"/admin/peliculas/{pelicula_id}", datos=datos)

    if estado == 200:
        return redirect(url_for("admin.peliculas"))

    return responder_error_api(resultado, estado)


@admin_bp.route("/peliculas/<int:pelicula_id>/eliminar", methods=["POST"])
def eliminar_pelicula(pelicula_id):
    resultado, estado = llamar_api("DELETE", f"/admin/peliculas/{pelicula_id}")

    if estado == 200:
        return redirect(url_for("admin.peliculas"))

    return responder_error_api(resultado, estado)

@admin_bp.route("/peliculas/externas", methods=["GET"])
def buscar_pelicula_omdb():
    titulo = request.args.get("titulo")
    anio = request.args.get("anio", "").strip()
    pelicula = None
    mensaje = None

    if titulo is not None:
        titulo = titulo.strip()

        if titulo == "":
            mensaje = "El titulo es obligatorio"

        else:
            parametros = {"titulo": titulo}

            if anio != "":
                parametros["anio"] = anio

            resultado, estado = llamar_api("GET", "/admin/peliculas/externas", parametros=parametros)

            if estado == 200:
                pelicula = resultado

            elif estado == 404:
                mensaje = str(resultado)

            else:
                return responder_error_api(resultado, estado)

    return render_template("admin/peliculas_omdb.html", pelicula=pelicula, mensaje=mensaje, titulo=titulo or "", anio=anio)

def leer_datos_servicio():
    try:
        precio = float(request.form.get("precio", ""))

    except ValueError:
        return None, "El precio debe ser un numero valido"

    if precio <= 0:
        return None, "El precio debe ser mayor a cero"

    texto_stock = request.form.get("stock", "").strip()
    stock = None

    if texto_stock != "":
        try:
            stock = int(texto_stock)

        except ValueError:
            return None, "El stock debe ser un numero entero"

        if stock < 0:
            return None, "El stock no puede ser negativo"

    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "categoria": request.form.get("categoria", "").strip(),
        "precio": precio,
        "stock": stock,
        "imagen_url": request.form.get("imagen_url", "").strip()
    }

    return datos, None

@admin_bp.route("/servicios")
def servicios():
    lista, estado = llamar_api("GET", "/admin/servicios")

    if estado == 404 and lista == "No hay servicios actualmente":
        lista = []

    elif estado != 200:
        return responder_error_api(lista, estado)

    servicio_editar = None
    id_editar = request.args.get("editar", type=int)

    if id_editar is not None:
        for servicio in lista:
            if servicio["id"] == id_editar:
                servicio_editar = servicio

        if servicio_editar is None:
            return "El servicio solicitado no existe", 404

    return render_template("admin/servicios.html", servicios=lista, servicio_editar=servicio_editar)

@admin_bp.route("/servicios/guardar", methods=["POST"])
def guardar_servicio():
    datos, error = leer_datos_servicio()

    if error is not None:
        return error, 400

    resultado, estado = llamar_api("POST", "/admin/servicios", datos=datos)

    if estado == 201:
        return redirect(url_for("admin.servicios"))

    return responder_error_api(resultado, estado)


@admin_bp.route("/servicios/<int:servicio_id>/editar", methods=["POST"])
def editar_servicio(servicio_id):
    datos, error = leer_datos_servicio()

    if error is not None:
        return error, 400

    resultado, estado = llamar_api("PATCH", f"/admin/servicios/{servicio_id}", datos=datos)

    if estado == 200:
        return redirect(url_for("admin.servicios"))

    return responder_error_api(resultado, estado)


@admin_bp.route("/servicios/<int:servicio_id>/baja", methods=["POST"])
def baja_servicio(servicio_id):
    resultado, estado = llamar_api("DELETE", f"/admin/servicios/{servicio_id}")

    if estado == 200:
        return redirect(url_for("admin.servicios"))

    return responder_error_api(resultado, estado)

@admin_bp.route("/backoffice")
def dashboard():
    try:
        # 1. Llamamos a la API y DESEMPAQUETAMOS la tupla (datos, status_code)
        funciones_json, status_f = llamar_api("GET", "/admin/estadisticas/ocupacion/funciones")
        peliculas_json, status_p = llamar_api("GET", "/admin/estadisticas/ocupacion/peliculas")
        franjas_json, status_fr = llamar_api("GET", "/admin/estadisticas/franjas_horarias")
        generos_json, status_g = llamar_api("GET", "/admin/estadisticas/ventas_genero")
        cancelaciones_json, status_c = llamar_api("GET", "/admin/estadisticas/cancelaciones")
        kpis_json, status_k = llamar_api("GET", "/admin/estadisticas/kpis")

      
        if status_f != 200: funciones_json = []
        if status_p != 200: peliculas_json = []
        if status_fr != 200: franjas_json = []
        if status_g != 200: generos_json = []
        if status_c != 200: cancelaciones_json = []
        
        if status_k != 200 or not kpis_json:
            kpis_json = {"entradas_vendidas": 0, "ingresos": 0, "ocupacion_media": 0, "total_cancelaciones": 0}

        # Transformamos los datos (la variable ya es un diccionario/lista de Python, no hace falta .json())
        datos_funciones = []
        if isinstance(funciones_json, list):
            for f in funciones_json:
                hora = f.get('fecha_hora_inicio', '')[11:16] if f.get('fecha_hora_inicio') else ""
                etiqueta = f"{f.get('pelicula', 'Sin nombre')} {hora}"
                datos_funciones.append([etiqueta, float(f.get('porcentaje_ocupacion', 0))])

        datos_peliculas = []
        if isinstance(peliculas_json, list):
            datos_peliculas = [[p.get('pelicula', 'Sin nombre'), float(p.get('porcentaje_ocupacion', 0))] for p in peliculas_json]

        datos_franjas = []
        if isinstance(franjas_json, list):
            datos_franjas = [[f"{f.get('hora', 0)}:00 h", int(f.get('entradas_vendidas', 0))] for f in franjas_json]

        datos_generos = []
        if isinstance(generos_json, list):
            datos_generos = [[g.get('genero', 'Otro'), float(g.get('cantidad_entradas', 0))] for g in generos_json]

        # Cálculo de cancelaciones
        total_cancelaciones = 0
        if isinstance(cancelaciones_json, list):
            for item in cancelaciones_json:
                if isinstance(item, dict):
                    total_cancelaciones += item.get('cantidad', 0)

        
        total_entradas = kpis_json.get('entradas_vendidas', 0)
        total_cancel = kpis_json.get('total_cancelaciones', 0)

        plata = kpis_json.get('ingresos', 0) 
        ingresos_formato = f"${plata:,.0f}".replace(",", ".")

        porcentaje_cancelado = 0
        if total_entradas > 0:
            porcentaje_cancelado = round((total_cancel / total_entradas) * 100, 1)

        est = {
            "kpis": [
                {"nombre": "Entradas vendidas", "valor": str(total_entradas)},
                {"nombre": "Ingresos", "valor": ingresos_formato},
                {"nombre": "Ocupación media", "valor": f"{kpis_json.get('ocupacion_media', 0):.0f} %"},
                {"nombre": "Cancelaciones", "valor": str(total_cancel)}
            ],
            "ocupacion_funcion": datos_funciones,
            "ocupacion_pelicula": datos_peliculas,
            "franjas": datos_franjas,
            "ventas_genero": datos_generos,
            "cancelaciones": {"total": total_cancel, "porcentaje": str(porcentaje_cancelado)}
        }

    except Exception as e:
        print(f"Error general conectando con el Backend: {e}")
        est = {
            "kpis": [], "ocupacion_funcion": [], "ocupacion_pelicula": [],
            "franjas": [], "ventas_genero": [], "cancelaciones": {"total": 0, "porcentaje": 0}
        }

    return render_template("admin/dashboard.html", est=est)

@admin_bp.route("/funciones", methods=["GET"])
def funciones():
    peliculas, estado = llamar_api("GET", "/admin/peliculas")
    if estado != 200:
        return responder_error_api(peliculas, estado)

    salas, estado = llamar_api("GET", "/admin/salas")
    if estado != 200:
        return responder_error_api(salas, estado)

    lista_funciones, estado = llamar_api("GET", "/admin/funciones")
    if estado != 200:
        return responder_error_api(lista_funciones, estado)

    return render_template(
        "admin/funciones.html",
        peliculas=peliculas,
        salas=salas,
        funciones=lista_funciones
    )


@admin_bp.route("/funciones/guardar", methods=["POST"])
def guardar_funcion():
    try:
        datos = {
            "pelicula_id": int(request.form.get("pelicula_id", "")),
            "sala_id": int(request.form.get("sala_id", "")),
            "fecha_hora_inicio": request.form.get("fecha_hora_inicio", "").strip(),
            "fecha_hora_fin": request.form.get("fecha_hora_fin", "").strip(),
            "precio_base": float(request.form.get("precio_base", "")),
            "estado": "programada"
        }
    except (ValueError, TypeError):
        return "La pelicula, la sala y el precio deben ser validos", 400

    resultado, estado = llamar_api("POST", "/admin/funciones", datos=datos)

    if estado == 201:
        return redirect(url_for("admin.funciones"))

    return responder_error_api(resultado, estado)