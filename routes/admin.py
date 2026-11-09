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


@admin_bp.route("/peliculas", methods=["GET", "POST"])
def peliculas():
    if request.method == "POST":
        return redirect(url_for("admin.peliculas"))  # Hito 3: acá se envía la película al backend
    peliculas = mock_data.get_peliculas()
    return render_template("admin/peliculas.html", peliculas=peliculas, cines=mock_data.get_cines())

@admin_bp.route("/servicios")
def servicios():
    return render_template("admin/servicios.html", servicios=mock_data.get_servicios())

@admin_bp.route("/servicios/guardar", methods=["POST"])
def guardar_servicio():
    return redirect(url_for("admin.servicios"))  # Hito 3: guardar en el backend

@admin_bp.route("/servicios/<int:servicio_id>/baja", methods=["POST"])
def baja_servicio(servicio_id):
    return redirect(url_for("admin.servicios"))  # Hito 3: dar de baja en el backend

@admin_bp.route("/backoffice")
def dashboard():
    try:
        # 1. Llamamos a la API y DESEMPAQUETAMOS la tupla (datos, status_code)
        funciones_json, status_f = llamar_api("GET", "/admin/estadisticas/ocupacion/funciones")
        peliculas_json, status_p = llamar_api("GET", "/admin/estadisticas/ocupacion/peliculas")
        franjas_json, status_fr = llamar_api("GET", "/admin/estadisticas/franjas_horarias")
        generos_json, status_g = llamar_api("GET", "/admin/estadisticas/ventas_genero")
        cancelaciones_json, status_c = llamar_api("GET", "/admin/estadisticas/cancelaciones")

        # 2. Si la API devolvió error (status != 200), forzamos lista vacía
        if status_f != 200: funciones_json = []
        if status_p != 200: peliculas_json = []
        if status_fr != 200: franjas_json = []
        if status_g != 200: generos_json = []
        if status_c != 200: cancelaciones_json = []

        # 3. Transformamos los datos (la variable ya es un diccionario/lista de Python, no hace falta .json())
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

        # 4. Cálculo de cancelaciones
        total_cancelaciones = 0
        if isinstance(cancelaciones_json, list):
            for item in cancelaciones_json:
                if isinstance(item, dict):
                    total_cancelaciones += item.get('cantidad', 0)

        # 5. Armamos el diccionario "est" final
        est = {
            "kpis": [
                {"nombre": "Entradas vendidas", "valor": "1.284"},
                {"nombre": "Ingresos", "valor": "$8,4 M"},
                {"nombre": "Ocupación media", "valor": "74 %"},
                {"nombre": "Cancelaciones", "valor": str(total_cancelaciones)}
            ],
            "ocupacion_funcion": datos_funciones,
            "ocupacion_pelicula": datos_peliculas,
            "franjas": datos_franjas,
            "ventas_genero": datos_generos,
            "cancelaciones": {"total": total_cancelaciones, "porcentaje": "4.2"}
        }

    except Exception as e:
        print(f"Error general conectando con el Backend: {e}")
        est = {
            "kpis": [], "ocupacion_funcion": [], "ocupacion_pelicula": [],
            "franjas": [], "ventas_genero": [], "cancelaciones": {"total": 0, "porcentaje": 0}
        }

    return render_template("admin/dashboard.html", est=est)