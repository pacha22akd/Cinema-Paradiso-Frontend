# Backoffice del administrador. Todas las rutas de acá empiezan con /admin.
from flask import Blueprint, redirect, render_template, request, session, url_for

from services import mock_data
from services.auth import revisar_admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.before_request
def proteger():
    # Se ejecuta antes de CUALQUIER ruta de admin: hay que ser administrador
    return revisar_admin()


@admin_bp.route("/")
def perfil():
    return render_template("admin/perfil.html", admin=session["usuario"])


@admin_bp.route("/dashboard")
def dashboard():
    return render_template("admin/dashboard.html", est=mock_data.get_estadisticas())


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
