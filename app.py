from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/inventario')
def inventario():
    productos = [
        {'id': 1, 'nombre': 'Producto A', 'precio': 10.0, 'stock': 5},
        {'id': 2, 'nombre': 'Producto B', 'precio': 15.0, 'stock': 3}
    ]
    return render_template('inventario.html', productos=productos)

@app.route('/carrito')
def carrito():
    carrito = [
        {'nombre': 'Producto A', 'cantidad': 2, 'precio': 10.0},
        {'nombre': 'Producto B', 'cantidad': 1, 'precio': 15.0}
    ]
    total = sum(item['cantidad'] * item['precio'] for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/usuarios')
def usuarios():
    usuarios = [
        {'id': 1, 'username': 'admin'},
        {'id': 2, 'username': 'usuario1'}
    ]
    return render_template('usuarios.html', usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True)
