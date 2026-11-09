import os
import requests

from dotenv import load_dotenv
from flask import session

load_dotenv()

API_URL = os.environ["API_URL"].rstrip("/")


def encabezado_auth():
    # El backend identifica al usuario por el token que se guarda en la sesión al hacer login
    token = session.get("token")

    if token:
        return {"Authorization": f"Bearer {token}"}

    return {}


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
    try:
        respuesta = requests.request(
            method=metodo,
            url=f"{API_URL}/{endpoint.lstrip('/')}",
            headers=encabezado_auth(),
            json=datos,
            params=parametros,
            timeout=10
        )

        if respuesta.status_code == 204:
            return None, 204

        if not respuesta.ok:
            mensaje = sacar_mensaje(respuesta)
            return mensaje, respuesta.status_code

        return respuesta.json(), respuesta.status_code

    except requests.RequestException:
        return "No se pudo establecer conexión con el backend.", 503

