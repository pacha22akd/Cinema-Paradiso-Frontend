import os
from dotenv import load_dotenv
from flask import session

load_dotenv()

API_URL = os.environ["API_URL"].rstrip("/")

def encabezado_auth():
    # El backend identifica al usuario por el token que se guarda en la sesión al hacer login
    return {"Authorization": f"Bearer {session.get('token')}"}