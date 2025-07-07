#!/usr/bin/env python3
# usuarios.py

from flask import Flask, request, redirect, url_for, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

DB_FILE = "usuarios.db"
app = Flask(__name__)

# Plantillas HTML mínimas embebidas
TEMPLATE_INIT = """
<!doctype html>
<title>Init DB</title>
<h2>Base de datos reiniciada</h2>
<p><a href="{{ url_for('register') }}">Registrar usuarios</a></p>
"""

TEMPLATE_REGISTER = """
<!doctype html>
<title>Registrar Usuario</title>
<h2>Registrar Usuario</h2>
<form method="post">
  Usuario: <input name="username" required><br>
  Contraseña: <input name="password" type="password" required><br>
  <button type="submit">Registrar</button>
</form>
{% if msg %}<p style="color:red;">{{ msg }}</p>{% endif %}
<p><a href="{{ url_for('login') }}">Ir a Login</a></p>
"""

TEMPLATE_LOGIN = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post">
  Usuario: <input name="username" required><br>
  Contraseña: <input name="password" type="password" required><br>
  <button type="submit">Entrar</button>
</form>
{% if msg %}<p style="color:red;">{{ msg }}</p>{% endif %}
<p><a href="{{ url_for('register') }}">Ir a Registro</a></p>
"""

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/init")
def init():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users;")
    cur.execute("""
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()
    return render_template_string(TEMPLATE_INIT)

@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        user = request.form["username"].strip()
        pwd = request.form["password"]
        if not user or not pwd:
            msg = "Debe completar ambos campos."
        else:
            pwd_hash = generate_password_hash(pwd)
            try:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (user, pwd_hash)
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                msg = f"El usuario '{user}' ya existe."
    return render_template_string(TEMPLATE_REGISTER, msg=msg)

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        user = request.form["username"].strip()
        pwd = request.form["password"]
        conn = get_db_connection()
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (user,)
        ).fetchone()
        conn.close()
        if row and check_password_hash(row["password_hash"], pwd):
            return f"<h2>¡Bienvenido, {user}!</h2>"
        else:
            msg = "Usuario o contraseña incorrectos."
    return render_template_string(TEMPLATE_LOGIN, msg=msg)

if __name__ == "__main__":
    # Ejecuta en el puerto 5800
    app.run(host="0.0.0.0", port=5800, debug=True)
