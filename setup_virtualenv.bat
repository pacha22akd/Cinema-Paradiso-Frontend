@echo off
REM Crea el entorno virtual e instala las dependencias (Windows)
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Listo. Para correr la app:
echo   venv\Scripts\activate
echo   python app.py
echo Abrir http://localhost:5001
