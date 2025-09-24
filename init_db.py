import sqlite3
from werkzeug.security import generate_password_hash

DB = "cuarta.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Usuarios
    c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    ''')

    # Inventario
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        producto TEXT NOT NULL,
        precio_compra REAL NOT NULL,
        precio_venta REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    ''')

    # Ventas
    c.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket TEXT NOT NULL,
        fechahora TEXT NOT NULL,
        producto TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        subtotal REAL NOT NULL
    )
    ''')

    # Crear admin por defecto: usuario admin / password: admin123 (cámbiala)
    admin_user = "admin"
    admin_pass = generate_password_hash("admin123")
    try:
        c.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
                  (admin_user, admin_pass, "admin"))
    except Exception:
        # ya existe
        pass

    conn.commit()
    conn.close()
    print("Base de datos inicializada en", DB)
    print("Usuario admin: admin  | contraseña: admin123  (cámbiala después)")

if __name__ == "__main__":
    init_db()
