#!/bin/bash
# Crea el entorno virtual e instala las dependencias (Linux / macOS)
set -e
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo ""
echo "Listo. Para correr la app:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo "Abrir http://localhost:5001"
