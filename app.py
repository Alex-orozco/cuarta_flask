from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import os
import uuid

DB = "cuarta.db"
app = Flask(__name__)
app.secret_key = os.urandom(24)  # para sesiones; en producción usar una variable fija

# -------------------------
# Utilidades de BD
# -------------------------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
# Rutas de autenticación
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.execute("SELECT * FROM usuarios WHERE username = ?", (usuario,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            session["rol"] = user["rol"]
            session["cart"] = {}  # carrito: {codigo: {producto, cantidad, precio}}
            return redirect(url_for("inventario"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------------------------
# Inventario
# -------------------------
@app.route("/inventario", methods=["GET", "POST"])
def inventario():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    # agregar producto (solo admin)
    if request.method == "POST" and session.get("rol") == "admin":
        codigo = request.form.get("codigo") or str(uuid.uuid4())[:8]
        producto = request.form.get("producto")
        precio_compra = float(request.form.get("precio_compra") or 0)
        precio_venta = float(request.form.get("precio_venta") or 0)
        stock = int(request.form.get("stock") or 0)
        conn.execute("INSERT INTO inventario (codigo, producto, precio_compra, precio_venta, stock) VALUES (?, ?, ?, ?, ?)",
                     (codigo, producto, precio_compra, precio_venta, stock))
        conn.commit()
        flash("Producto agregado", "success")

    cur = conn.execute("SELECT * FROM inventario ORDER BY id DESC")
    productos = cur.fetchall()
    conn.close()
    return render_template("inventory.html", productos=productos, rol=session.get("rol"))

# -------------------------
# Agregar al carrito
# -------------------------
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user" not in session:
        return redirect(url_for("login"))
    codigo = request.form.get("codigo")
    cantidad = int(request.form.get("cantidad") or 0)
    if cantidad <= 0:
        flash("Cantidad inválida", "warning")
        return redirect(url_for("inventario"))

    conn = get_db()
    cur = conn.execute("SELECT * FROM inventario WHERE codigo = ?", (codigo,))
    p = cur.fetchone()
    if not p:
        flash("Producto no encontrado", "danger")
        conn.close()
        return redirect(url_for("inventario"))

    if cantidad > p["stock"]:
        flash("Stock insuficiente", "warning")
        conn.close()
        return redirect(url_for("inventario"))

    cart = session.get("cart", {})

    if codigo in cart:
        cart[codigo]["cantidad"] += cantidad
    else:
        cart[codigo] = {"producto": p["producto"], "cantidad": cantidad, "precio": p["precio_venta"]}

    session["cart"] = cart
    flash("Agregado al carrito", "success")
    conn.close()
    return redirect(url_for("inventario"))

# -------------------------
# Ver carrito
# -------------------------
@app.route("/carrito")
def carrito():
    if "user" not in session:
        return redirect(url_for("login"))
    cart = session.get("cart", {})
    total = sum(item["cantidad"] * item["precio"] for item in cart.values())
    return render_template("cart.html", cart=cart, total=total)

# -------------------------
# Finalizar venta
# -------------------------
@app.route("/finalizar", methods=["POST"])
def finalizar():
    if "user" not in session:
        return redirect(url_for("login"))
    cart = session.get("cart", {})
    if not cart:
        flash("El carrito está vacío", "warning")
        return redirect(url_for("inventario"))

    ticket = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    for codigo, item in cart.items():
        producto = item["producto"]
        cantidad = item["cantidad"]
        subtotal = cantidad * float(item["precio"])

        conn.execute("INSERT INTO ventas (ticket, fechahora, producto, cantidad, subtotal) VALUES (?, ?, ?, ?, ?)",
                     (ticket, fecha, producto, cantidad, subtotal))

        # actualizar stock
        conn.execute("UPDATE inventario SET stock = stock - ? WHERE codigo = ?", (cantidad, codigo))

    conn.commit()
    conn.close()
    session["cart"] = {}
    flash("Venta registrada", "success")
    return redirect(url_for("ver_ticket", ticket=ticket))

# -------------------------
# Ver ticket
# -------------------------
@app.route("/ticket/<ticket>")
def ver_ticket(ticket):
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.execute("SELECT * FROM ventas WHERE ticket = ?", (ticket,))
    filas = cur.fetchall()
    conn.close()
    total = sum(f["subtotal"] for f in filas)
    return render_template("ticket.html", filas=filas, ticket=ticket, total=total)

# -------------------------
# Rutas extra: crear usuario (solo admin)
# -------------------------
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if "user" not in session or session.get("rol") != "admin":
        flash("Acceso denegado", "danger")
        return redirect(url_for("login"))
    conn = get_db()
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        rol = request.form["rol"]
        try:
            conn.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
                         (username, password, rol))
            conn.commit()
            flash("Usuario creado", "success")
        except Exception as e:
            flash("No se pudo crear el usuario: " + str(e), "danger")
    cur = conn.execute("SELECT id, username, rol FROM usuarios ORDER BY id DESC")
    users = cur.fetchall()
    conn.close()
    return render_template("users.html", users=users)

if __name__ == "__main__":
    app.run(debug=True)
