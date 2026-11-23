import os

from dotenv import load_dotenv
from flask import Flask, render_template

from routes.publico import publico_bp
from routes.compra import compra_bp
from routes.admin import admin_bp

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["API_URL"] = os.environ.get("API_URL")

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
