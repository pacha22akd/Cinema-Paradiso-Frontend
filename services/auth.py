from flask import abort, flash, redirect, session, url_for


def revisar_login():
    """Si el usuario NO inició sesión, lo manda al login.
    Si está todo bien devuelve None (y la ruta sigue normalmente)."""
    if "usuario" not in session:
        flash("Iniciá sesión para continuar.", "warning")
        return redirect(url_for("publico.login"))
    return None


def revisar_admin():
    """Igual que revisar_login, pero además exige que el usuario sea administrador."""
    respuesta = revisar_login()
    if respuesta is not None:
        return respuesta
    if session["usuario"]["rol"] != "admin":
        abort(403)  # prohibido: está logueado pero no es admin
    return None
