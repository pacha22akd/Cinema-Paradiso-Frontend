import os
import requests

from dotenv import load_dotenv
from flask import session

load_dotenv()

API_URL = os.environ["API_URL"].rstrip("/")

def encabezado_auth():
    # El backend identifica al usuario por el token que se guarda en la sesión al hacer login
    return {"Authorization": f"Bearer {session.get('token')}"}

class ErrorApi(Exception):
    """Se lanza cuando el backend contesta con un error, o cuando no logramos hablar con él"""

    def __init__(self, mensaje, status):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status = status

def sacar_mensaje(respuesta):
    """Busca el texto del error en la respuesta del backend"""
    try:
        cuerpo = respuesta.json()
    except ValueError:
        return "El servidor respondió algo inesperado."

    if isinstance(cuerpo, dict):
        if cuerpo.get("errors"):
            return cuerpo["errors"][0].get("description", "Ocurrió un error.")
        if cuerpo.get("error"):
            return cuerpo["error"]
    return "Ocurrió un error inesperado."

def llamar_api(metodo, endpoint, datos=None, parametros=None):
    respuesta = requests.request(
        method=metodo,
        url=f"{API_URL}/{endpoint.lstrip('/')}",
        headers=encabezado_auth(),
        json=datos,
        params=parametros,
        timeout=10
    )

    return respuesta

