# Datos de prueba
from datetime import datetime, timedelta


def get_cines():
    return [
        {"id": 1, "nombre": "Cine Paradiso 1"},
        {"id": 2, "nombre": "Cine Paradiso 2"},
        {"id": 3, "nombre": "Cine Paradiso 3"},
    ]


def get_peliculas():
    peliculas = [
        {"id": 1, "titulo": "The Salt Tide", "etiqueta": "Competition", "clase_etiqueta": "", "genero": "Drama", "pais": "Croacia", "duracion": 103},
        {"id": 2, "titulo": "Nightbus to Nowhere", "etiqueta": "Competition", "clase_etiqueta": "", "genero": "Thriller", "pais": "Argentina", "duracion": 124},
        {"id": 3, "titulo": "Paper Lanterns", "etiqueta": "Documentary", "clase_etiqueta": "doc", "genero": "Documental", "pais": "Japón", "duracion": 88},
        {"id": 4, "titulo": "Concrete Sky", "etiqueta": "Competition", "clase_etiqueta": "", "genero": "Drama", "pais": "Nigeria", "duracion": 117},
        {"id": 5, "titulo": "The Longest Winter", "etiqueta": "Documentary", "clase_etiqueta": "doc", "genero": "Documental", "pais": "Noruega", "duracion": 95},
        {"id": 6, "titulo": "Wildflower Radio", "etiqueta": "Debut", "clase_etiqueta": "debut", "genero": "Comedia", "pais": "Kenia", "duracion": 96},
        {"id": 7, "titulo": "Static", "etiqueta": "Competition", "clase_etiqueta": "", "genero": "Terror", "pais": "Alemania", "duracion": 101},
        {"id": 8, "titulo": "The Diving Hour", "etiqueta": "Documentary", "clase_etiqueta": "doc", "genero": "Documental", "pais": "Portugal", "duracion": 85},
        {"id": 9, "titulo": "The Hourglass", "etiqueta": "Retrospective", "clase_etiqueta": "retro", "genero": "Fantasía", "pais": "Reino Unido", "duracion": 110},
        {"id": 10, "titulo": "Dust & Ember", "etiqueta": "Retrospective", "clase_etiqueta": "retro", "genero": "Western", "pais": "EE.UU.", "duracion": 140},
    ]
    for pelicula in peliculas:
        completar_pelicula(pelicula)
    return peliculas


def completar_pelicula(pelicula):
    """Agrega a una película los datos que son iguales para todas."""
    pelicula["clasificacion"] = "+13"
    pelicula["sinopsis"] = ("Una historia que sigue a un grupo de personas enfrentadas a un invierno "
                            "que parece no terminar nunca. Entre paisajes imponentes y silencios "
                            "largos, descubren qué los une y qué los separa.")
    pelicula["poster"] = "https://picsum.photos/seed/cp" + str(pelicula["id"]) + "/300/450"
    return pelicula


def get_pelicula(pelicula_id):
    """Busca una película por su id. Devuelve None si no existe."""
    for pelicula in get_peliculas():
        if pelicula["id"] == pelicula_id:
            return pelicula
    return None


def get_funciones(pelicula_id):
    """Devuelve las funciones de una película (3 horarios en cada cine).
    La fecha y la hora van juntas en un solo campo datetime llamado `inicio`."""
    manana = datetime.now() + timedelta(days=1)
    horas = [16, 19, 22]
    funciones = []
    for cine in get_cines():
        numero = 0
        for hora in horas:
            if numero == 1:
                formato = "3D Doblada"
            else:
                formato = "2D Subtitulada"
            funcion = {
                "id": pelicula_id * 100 + cine["id"] * 10 + numero,
                "pelicula_id": pelicula_id,
                "cine": cine,
                "sala": "Sala " + str(cine["id"] + numero),
                "formato": formato,
                "inicio": manana.replace(hour=hora, minute=0, second=0, microsecond=0),
            }
            funciones.append(funcion)
            numero = numero + 1
    return funciones


def get_funcion(funcion_id):
    """Busca una función por su id. Devuelve None si no existe."""
    pelicula_id = funcion_id // 100  # el id de la función empieza con el id de la película
    for funcion in get_funciones(pelicula_id):
        if funcion["id"] == funcion_id:
            return funcion
    return None


def get_tipos_entrada():
    return [
        {"clave": "general", "nombre": "General", "precio": 6500},
        {"clave": "VIP", "nombre": "VIP", "precio": 10000}
    ]


def get_mapa_butacas():
    """Devuelve las filas, las columnas y las butacas que ya están ocupadas."""
    filas = ["A", "B", "C", "D", "E", "F", "G", "H"]
    columnas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ocupadas = ["A3", "A4", "C5", "C6", "D7", "F2", "F3", "H9"]
    return filas, columnas, ocupadas


def get_servicios():
    return [
        {"id": 1, "nombre": "Pochoclo grande", "categoria": "Comida", "precio": 4200, "activo": True},
        {"id": 2, "nombre": "Nachos con cheddar", "categoria": "Comida", "precio": 3800, "activo": True},
        {"id": 3, "nombre": "Gaseosa 500 ml", "categoria": "Bebida", "precio": 2500, "activo": True},
        {"id": 4, "nombre": "Estacionamiento", "categoria": "Estacionamiento", "precio": 3000, "activo": True},
        {"id": 5, "nombre": "Acceso VIP", "categoria": "VIP", "precio": 9000, "activo": False},
    ]


def get_historial():
    ahora = datetime.now()
    return [
        {"pelicula": "The Longest Winter", "cine": "Cine Paradiso 1", "fecha": ahora - timedelta(days=12),
         "total": 13000, "estado": "Utilizada"},
        {"pelicula": "Static", "cine": "Cine Paradiso 2", "fecha": ahora - timedelta(days=30),
         "total": 15200, "estado": "Utilizada"},
        {"pelicula": "Dust & Ember", "cine": "Cine Paradiso 3", "fecha": ahora + timedelta(days=3),
         "total": 11000, "estado": "Activa"},
    ]


def get_estadisticas():
    """Números para el dashboard. Cada lista tiene pares (nombre, valor)."""
    return {
        "ocupacion_funcion": [("The Salt Tide 19:00", 86), ("Static 22:00", 72),
                              ("Paper Lanterns 16:00", 41), ("Dust & Ember 19:00", 93)],
        "ocupacion_pelicula": [("Dust & Ember", 91), ("The Salt Tide", 78), ("Static", 69),
                               ("Paper Lanterns", 38)],
        "ventas_genero": [("Drama", 38), ("Terror", 22), ("Documental", 15), ("Comedia", 14),
                          ("Western", 11)],
        "franjas": [("14-16 h", 12), ("16-18 h", 28), ("18-20 h", 64), ("20-22 h", 88), ("22-24 h", 47)],
        "cancelaciones": {"total": 37, "porcentaje": 4.2},
        "kpis": [("Entradas vendidas", "1.284"), ("Ingresos", "$8,4 M"),
                 ("Ocupación media", "74 %"), ("Cancelaciones", "4,2 %")],
    }


def autenticar(email, password):
    """Login de prueba. Devuelve el usuario si los datos son correctos, o None si no."""
    usuarios = [
        {"nombre": "Lucía", "email": "lucia@ejemplo.com", "password": "cliente123", "rol": "cliente"},
        {"nombre": "Admin Paradiso", "email": "admin@cineparadiso.com", "password": "admin123", "rol": "admin"},
    ]
    for usuario in usuarios:
        if usuario["email"] == email and usuario["password"] == password:
            # No devolvemos la contraseña, solo los datos que se guardan en la sesión
            return {"nombre": usuario["nombre"], "email": usuario["email"], "rol": usuario["rol"]}
    return None
