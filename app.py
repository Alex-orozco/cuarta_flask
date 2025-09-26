from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_por_defecto")

DATABASE = "basedatos.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Usuario y contraseña requeridos", "warning")
            return redirect(url_for("login"))

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["usuario"] = username
            session["carrito"] = []
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales inválidas", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/inventario", methods=["GET", "POST"])
def inventario():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    if request.method == "POST":
        producto = request.form["producto"]
        precio_venta = request.form.get("precio_venta", type=float)
        cantidad = request.form.get("cantidad", type=int)

        if not producto or precio_venta is None or cantidad is None or precio_venta < 0 or cantidad < 0:
            flash("Datos inválidos", "warning")
            return redirect(url_for("inventario"))

        try:
            conn.execute("INSERT INTO inventario (producto, precio_venta, cantidad) VALUES (?, ?, ?)",
                         (producto, precio_venta, cantidad))
            conn.commit()
            flash("Producto agregado", "success")
        except sqlite3.Error as e:
            flash(f"Error en la base de datos: {e}", "danger")
    productos = conn.execute("SELECT * FROM inventario").fetchall()
    conn.close()
    return render_template("inventario.html", productos=productos)

@app.route("/carrito/agregar/<int:id>")
def agregar_carrito(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    producto = conn.execute("SELECT * FROM inventario WHERE id = ?", (id,)).fetchone()
    conn.close()

    if producto and producto["cantidad"] > 0:
        session["carrito"].append({"id": producto["id"], "producto": producto["producto"],
                                   "precio_venta": producto["precio_venta"]})
        flash("Producto agregado al carrito", "success")
    else:
        flash("Producto sin stock", "warning")
    return redirect(url_for("dashboard"))

@app.route("/carrito")
def ver_carrito():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("carrito.html", carrito=session.get("carrito", []))

@app.route("/venta/finalizar")
def finalizar_venta():
    if "usuario" not in session:
        return redirect(url_for("login"))

    carrito = session.get("carrito", [])
    if not carrito:
        flash("Carrito vacío", "warning")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    try:
        for item in carrito:
            conn.execute("UPDATE inventario SET cantidad = cantidad - 1 WHERE id = ?", (item["id"],))
        conn.commit()
        session["carrito"] = []
        flash("Venta finalizada", "success")
    except sqlite3.Error as e:
        flash(f"Error al finalizar venta: {e}", "danger")
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Usuario y contraseña requeridos", "warning")
            return redirect(url_for("usuarios"))

        existing = conn.execute("SELECT * FROM usuarios WHERE username = ?", (username,)).fetchone()
        if existing:
            flash("El usuario ya existe", "warning")
            return redirect(url_for("usuarios"))

        hashed_password = generate_password_hash(password)
        try:
            conn.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Usuario creado", "success")
        except sqlite3.Error as e:
            flash(f"Error en la base de datos: {e}", "danger")
    usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
