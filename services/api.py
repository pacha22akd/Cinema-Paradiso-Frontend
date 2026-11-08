import os
from flask import session

# Dirección del backend. Se puede cambiar desde el .env si corre en otro lado
API_URL = os.getenv("API_URL", "http://localhost:5000")


def encabezado_auth():
    # El backend identifica al usuario por el token que se guarda en la sesión al hacer login
    return {"Authorization": f"Bearer {session.get('token')}"}