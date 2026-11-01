# Para correrlo:  python app.py   y abrir http://localhost:5001
import os

from flask import Flask, render_template

from routes.publico import publico_bp
from routes.compra import compra_bp
from routes.admin import admin_bp

app = Flask(__name__)

# Flask necesita una clave secreta para poder guardar la sesión del usuario (el login)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo")

app.register_blueprint(publico_bp)
app.register_blueprint(compra_bp, url_prefix="/comprar")
app.register_blueprint(admin_bp, url_prefix="/admin")

@app.errorhandler(403)
def prohibido(error):
    return render_template("errors/403.html"), 403

@app.errorhandler(404)
def no_encontrado(error):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def error_servidor(error):
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
