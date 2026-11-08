import os
import requests

from dotenv import load_dotenv
from flask import session

load_dotenv()

API_URL = os.environ["API_URL"].rstrip("/")

def encabezado_auth():
    # El backend identifica al usuario por el token que se guarda en la sesión al hacer login
    return {"Authorization": f"Bearer {session.get('token')}"}

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