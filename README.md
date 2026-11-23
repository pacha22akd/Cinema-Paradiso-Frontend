# Cine Paradiso - Frontend

Este repositorio contiene el Frontend de la aplicación web **Cine Paradiso**, desarrollado en Python con el framework Flask y utilizando el motor de plantillas Jinja2. Su función principal es renderizar las vistas (HTML/CSS) para los clientes y administradores, y actuar como un cliente HTTP intermediario que consume la API del Backend para obtener y enviar los datos.

### Integrantes
* **María Eugenia Vallejo**
* **Maximo Febles**
* **Sebastián Romero**
* **Brunella Mía Valdata**
* **Sofia Levin**
* **Joaquín Ventura**
* **Córdoba Milagros Belén**

## Tecnologías Utilizadas

El proyecto fue desarrollado utilizando las siguientes librerías y herramientas:

*   **Flask (3.1.3):** Framework principal para el enrutamiento y renderizado de vistas.
*   **Jinja2:** Motor de plantillas para inyectar datos dinámicos en el HTML.
*   **requests (2.34.2):** Librería utilizada en el servidor para consumir los endpoints del Backend.
*   **python-dotenv (1.2.3):** Gestión de variables de entorno (URL del Backend, Secret Key).
*   **HTML & CSS:** Maquetado y diseño responsive (adaptable a celulares).
*   **JavaScript:** Interactividad en el navegador (carruseles, cálculos de totales en vivo, mostrar/ocultar contraseña).

## Funcionalidades Principales

* Renderizado Dinámico: Las vistas se arman en el servidor inyectando los datos del Backend con Jinja2.

* Autenticación Híbrida (JWT): El frontend guarda el Token JWT en una sesión de Flask segura. El archivo auth.py protege las rutas para que solo usuarios logueados o administradores puedan acceder a ciertas vistas.

* Experiencia de Compra Fluida: Interfaz interactiva para seleccionar butacas, agregar servicios (comida/bebida) con cálculo del total en tiempo real, y visualización del ticket/QR final.

* Diseño Responsive: Todas las vistas (incluyendo tablas y mapas de butacas) están adaptadas para dispositivos móviles, facilitando la compra desde el celular.

* Panel de Administración: Interfaz para que los administradores gestionen películas, funciones y validen los códigos QR escaneados en la puerta.

## Instalación y Ejecución Local

Seguí estos pasos para correr el frontend en tu máquina:

### Requisitos Previos
*   Python 3.10 o superior.
*   MySQL Server.
*   Git.
*   El Backend de Cine Paradiso debe estar corriendo (por defecto en http://127.0.0.1:5000).

### 1. Clonar el repositorio y crear el entorno virtual
Abrí una terminal y ejecutá:
```bash
git clone https://github.com/pacha22akd/Cinema-Paradiso-Frontend.git
cd cine-paradiso-frontend
python -m venv venv

# Activar el entorno virtual:
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```
### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```
### 3. Configurar variables de entorno
```
API_URL=http://127.0.0.1:5000
SECRET_KEY=TU_KEY
```
Para la secret key, debes abrir una terminal de python y ejecutar este comando
```
python -c “import secrets; print(secrets.token_urlsafe(48))”
```
Lo que te devuelve, lo tenes que pegar en SECRET_KEY.(Aclaracion: la secret key del back no es la misma en el front, deben ser 2 distintas para que pueda funcionar bien.)
### 5. Levantar el servidor
Para levantar el front tenes que estar en la carpeta raiz del proyecto y abrir una terminal para luego ejecutar el siguiente comando.
```bash
# Linux / macOS 
python app.py

# WSL
python3 app.py
```
Una vez ejecutado, el servidor comenzara a correrse en http://127.0.0.1:5001.