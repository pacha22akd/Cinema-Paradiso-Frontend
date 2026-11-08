from flask import session, redirect, url_for, flash, abort

def revisar_login():
    if "token" not in session:
        flash("Iniciá sesión para continuar.", "warning")
        return redirect(url_for("publico.login", next=url_for('publico.cartelera'))) 
    return None

def revisar_admin():
    respuesta = revisar_login()
    if respuesta is not None:
        return respuesta
    
    if session.get("rol") != "administrador":
        abort(403)  
    return None
