import os
from flask import Flask, render_template, request, redirect, url_for, flash
import db
import users

# Inicializa la aplicación de Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clave secreta para mensajes flash

@app.route('/')
def home():
    """Ruta para la página de inicio."""
    return render_template('home.html')

@app.route('/solicitar', methods=['POST'])
def solicitar_transporte():
    """Ruta que procesa el formulario de solicitud de transporte."""
    # Obtiene los datos del formulario
    first_name = request.form['first_name']
    first_lastname = request.form['first_lastname']
    second_lastname = request.form['second_lastname']
    phone = request.form['phone']
    email = request.form['email']
    pickup_location = request.form['pickup_location']
    destination = request.form['destination']
    notes = request.form.get('notes', '')

    # Conecta a la base de datos
    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        # Busca al usuario por email
        user_data = users.find_user_by_email(cursor, email)
        
        if user_data:
            # El usuario ya existe, obtenemos su ID
            user_id = user_data[0]
            flash(f'¡Hola de nuevo, {first_name}! Tu solicitud ha sido registrada.', 'success')
        else:
            # El usuario es nuevo, lo registramos automáticamente
            new_user_id, new_username = users.create_new_user(
                cursor, first_name, first_lastname, second_lastname, phone, email
            )
            user_id = new_user_id
            flash(f'¡Bienvenido, {first_name}! Has sido registrado con el usuario: {new_username}. Tu solicitud ha sido registrada.', 'success')

        # Registra la solicitud de transporte
        cursor.execute(
            'INSERT INTO requests (user_id, pickup_location, destination, notes) VALUES (?, ?, ?, ?)',
            (user_id, pickup_location, destination, notes)
        )
        conn.commit()

    except Exception as e:
        flash(f'Ocurrió un error al procesar tu solicitud: {e}', 'error')
    finally:
        # Cierra la conexión a la base de datos
        conn.close()

    return redirect(url_for('index'))

@app.route('/formulario')
def index():
    """Ruta para la página del formulario."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3030)


# Migraciones Cmder
        # set FLASK_APP=app.py     <--Crea un directorio de migraciones
        # flask db init             <--
        # $ flask db stamp head
        # $ flask db migrate
        # $ flask db migrate -m "mensaje x"
        # $ flask db upgrade
        # ERROR [flask_migrate] Error: Target database is not up to date.
        # $ flask db stamp head
        # $ flask db migrate
        # $ flask db upgrade
        # git clone https://github.com/kerm1977/MI_APP_FLASK.git
        # mysql> DROP DATABASE kenth1977$db; PYTHONANYWHATE
# -----------------------

# del db.db
# rmdir /s /q migrations
# flask db init
# flask db migrate -m "Reinitial migration with all correct models"
# flask db upgrade


# -----------------------
# Consola de pythonanywhere ante los errores de versiones
# Error: Can't locate revision identified by '143967eb40c0'

# flask db stamp head
# flask db migrate
# flask db upgrade

# Database pythonanywhere
# kenth1977$db
# DROP TABLE alembic_version;
# rm -rf migrations
# flask db init
# flask db migrate -m "Initial migration after reset"
# flask db upgrade

# 21:56 ~/LATRIBU1 (main)$ source env/Scripts/activate
# (env) 21:57 ~/LATRIBU1 (main)$

# En caso de que no sirva el env/Scripts/activate
# remover en env
# 05:48 ~/latribuapp (main)$ rm -rf env
# Crear nuevo
# 05:49 ~/latribuapp (main)$ python -m venv env
# 05:51 ~/latribuapp (main)$ source env/bin/activate
# (env) 05:52 ~/latribuapp (main)$ 



# Cuando se cambia de repositorio
# git remote -v
# git remote add origin <URL_DEL_REPOSITORIO>
# git remote set-url origin <NUEVA_URL_DEL_REPOSITORIO>
# git branchgit remote -v
# git push -u origin flet



# borrar base de datos y reconstruirla
# pip install PyMySQL
# SHOW TABLES;
# 21:56 ~/LATRIBU1 (main)$ source env/Scripts/activate <-- Entra al entorno virtual
# (env) 21:57 ~/LATRIBU1 (main)$
# (env) 23:30 ~/LATRIBU1 (main)$ cd /home/kenth1977/LATRIBU1
# (env) 23:31 ~/LATRIBU1 (main)$ rm -f instance/db.db
# (env) 23:32 ~/LATRIBU1 (main)$ rm -rf migrations
# (env) 23:32 ~/LATRIBU1 (main)$ flask db init
# (env) 23:33 ~/LATRIBU1 (main)$ flask db migrate -m "Initial migration with all models"
# (env) 23:34 ~/LATRIBU1 (main)$ flask db upgrade
# (env) 23:34 ~/LATRIBU1 (main)$ ls -l instance/db


# GUARDA  todas las dependecias para utilizar offline luego
# pip download -r requirements.txt -d librerias_offline
# INSTALA  todas las dependecias para utilizar offline luego
# pip install --no-index --find-links=./librerias_offline -r requirements.txt
