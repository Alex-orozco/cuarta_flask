INSTRUCCIONES SIMPLES (para usuarios sin experiencia)

1) Descargar y descomprimir el archivo ZIP en una carpeta (por ejemplo: C:\proyectos\cuarta_flask o ~/cuarta_flask)

2) Abrir la terminal:
   - Windows: abrir "PowerShell" o "Símbolo del sistema"
   - Mac / Linux: abrir "Terminal"

3) Ir a la carpeta del proyecto:
   - Windows ejemplo: cd C:\proyectos\cuarta_flask
   - Mac/Linux ejemplo: cd ~/cuarta_flask

4) Crear y activar un entorno virtual (recomendado):
   - Windows (PowerShell):
     python -m venv venv
     .\venv\Scripts\Activate.ps1
   - Windows (cmd):
     python -m venv venv
     venv\Scripts\activate
   - Mac / Linux:
     python3 -m venv venv
     source venv/bin/activate

5) Instalar dependencias:
   pip install -r requirements.txt

6) Inicializar la base de datos (esto crea el archivo cuarta.db y el usuario admin):
   python init_db.py
   (en Mac/Linux usar python3 si es necesario)

7) Ejecutar la app:
   python app.py
   (la app abrirá en http://127.0.0.1:5000 en tu navegador)

8) Login inicial:
   Usuario: admin
   Contraseña: admin123
   (cámbiala en Usuarios -> Crear usuario y borra el admin si quieres)

Para detener la app: presiona Ctrl+C en la terminal.

Si no entiendes algún paso dime en qué sistema (Windows o Mac) estás y te doy pasos exactos.
