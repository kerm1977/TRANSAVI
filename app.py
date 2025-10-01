import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session # Agregamos 'session'
import db
import users
# IMPORTACIÓN CRUCIAL: Importamos los Blueprints
from solicitudes import solicitudes_bp 
from admin import admin_bp # <--- NUEVA IMPORTACIÓN

# Inicializa la aplicación de Flask
app = Flask(__name__)
# Clave secreta para mensajes flash (¡IMPORTANTE!)
app.secret_key = os.urandom(24)

# REGISTRO CRUCIAL: Registramos los Blueprints
app.register_blueprint(solicitudes_bp)
app.register_blueprint(admin_bp) # <--- NUEVO REGISTRO

# LLAMADA CRUCIAL: Asegura que la base de datos y las tablas se creen al iniciar la aplicación.
db.create_tables()

@app.route('/')
def home():
    """
    Ruta para la página de inicio. Ahora redirige directamente al formulario,
    ya que la solicitud de servicio ya no requiere login.
    """
    # Redirigimos directamente a la ruta del formulario.
    return redirect(url_for('index'))


# Endpoint para verificación de existencia de usuario (AJAX)
@app.route('/check_username', methods=['GET'])
def check_username():
    """Verifica si un nombre de usuario existe en la base de datos."""
    username = request.args.get('username')
    
    if not username:
        return jsonify({'exists': False, 'message': 'Falta el nombre de usuario'}), 400

    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_data = users.find_user_by_username(cursor, username)
        
        if user_data:
            # Devuelve 'True' y el nombre de usuario encontrado
            return jsonify({'exists': True, 'username': user_data['username']})
        else:
            return jsonify({'exists': False})
    except Exception as e:
        print(f"Error al verificar usuario: {e}")
        return jsonify({'exists': False, 'message': 'Error interno del servidor'}), 500
    finally:
        conn.close()

# Endpoint para cargar datos del usuario existente (AJAX)
@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    """Obtiene y devuelve los datos de un usuario por su nombre de usuario."""
    username = request.args.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': 'Falta el nombre de usuario'}), 400

    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscamos todos los campos del usuario por el username
        user_data = users.find_user_by_username(cursor, username)

        if user_data:
            # Convertimos la fila de SQLite (diccionario/Row) a un diccionario estándar
            # Excluimos 'id' y 'username' ya que ya se conocen
            data = {k: user_data[k] for k in user_data.keys() if k not in ['id', 'username']}
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': False, 'message': 'Usuario no encontrado.'})
    
    except Exception as e:
        print(f"Error al obtener datos del usuario: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500
    finally:
        conn.close()

# Endpoint para buscar los detalles completos de una solicitud (AJAX)
@app.route('/find_request_details', methods=['GET'])
def find_request_details():
    """Busca una solicitud específica por nombre de usuario y número consecutivo."""
    username = request.args.get('username')
    request_num_raw = request.args.get('request_number') # Input crudo del usuario
    
    if not username or not request_num_raw:
        return jsonify({'success': False, 'message': 'Faltan Usuario o Consecutivo.'}), 400

    # --- FIX CRÍTICO: Relleno de ceros (padding) ---
    try:
        # 1. Intentar convertir a entero el input del usuario.
        # 2. Convertir de nuevo a string y aplicar zfill(4) para asegurar 4 dígitos.
        request_num_padded = str(int(request_num_raw)).zfill(4)
    except ValueError:
        # Si el usuario ingresa letras u otro valor no numérico, devolver error.
        return jsonify({'success': False, 'message': 'El Consecutivo debe ser un número válido de 1 a 4 dígitos.'}), 400
    # -----------------------------------------------

    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscamos el ID del usuario primero
        user_data = users.find_user_by_username(cursor, username)
        if not user_data:
            return jsonify({'success': False, 'message': 'Usuario no encontrado.'})

        user_id = user_data['id']
        
        # --- FIX PARA DATOS CORRUPTOS EN DB: Usar LIKE para coincidir 0001 y 0001N ---
        # Buscamos solicitudes cuyo request_number EMPIECE con el número rellenado.
        
        # Primero probamos la coincidencia exacta con el número de 4 dígitos
        data = users.get_full_request_details_by_user_id_and_number(cursor, user_id, request_num_padded)
        
        if not data:
            # Si no hay coincidencia exacta (ej: 0001), intentamos buscar usando LIKE.
            # Esta es la parte que corrige el error si el dato es '0001N' o similar.
            data = users.get_full_request_details_by_user_id_and_number_like(cursor, user_id, request_num_padded)


        if data:
            # Retornamos todos los datos como un diccionario estándar
            return jsonify({'success': True, 'data': dict(data)})
        else:
            return jsonify({'success': False, 'message': 'Solicitud no encontrada para ese Usuario y Consecutivo.'})

    except Exception as e:
        print(f"Error al buscar solicitud completa: {e}")
        # Retornamos un mensaje de error interno más detallado
        return jsonify({'success': False, 'message': f'Error interno del servidor al buscar: {e}'}), 500
    finally:
        conn.close()


@app.route('/solicitar', methods=['POST'])
def solicitar_transporte():
    """
    Ruta que procesa el formulario de solicitud de transporte y guarda los datos.
    Se ejecuta con la lógica de autenticación/registro que estaba en el app.py original,
    permitiendo a usuarios nuevos o existentes enviar solicitudes sin necesidad de login.
    """
    
    # --- 1. Obtiene datos del Flujo de Usuario ---
    # Ya no chequeamos la sesión, sino que usamos la lógica de index.html
    has_user = request.form['has_user']
    user_id = None
    username = None
    
    # Variables de usuario
    first_name = request.form.get('first_name', '')
    first_lastname = request.form.get('first_lastname', '')
    second_lastname = request.form.get('second_lastname', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    
    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        if has_user == 'SI':
            # Flujo 1: Usuario Existente (Requiere username)
            username_input = request.form['username']
            user_data = users.find_user_by_username(cursor, username_input)
            
            if user_data:
                user_id = user_data['id']
                username = user_data['username']
                # Nota: Si el usuario existe y completó los datos, podrías actualizar sus campos aquí
                # Pero por simplicidad, solo confirmamos la identidad.
                flash(f'¡Usuario {username} autenticado! Tu solicitud ha sido registrada.', 'success')
            else:
                flash('El usuario no existe. Por favor, verifica el nombre de usuario o selecciona "No".', 'error')
                return redirect(url_for('index'))

        else:
            # Flujo 2: Nuevo Usuario
            if not all([first_name, first_lastname, second_lastname, phone, email]):
                flash('Faltan campos obligatorios para el registro de nuevo usuario.', 'error')
                return redirect(url_for('index'))
                
            new_username = users.generate_custom_username(first_name, first_lastname, second_lastname, phone)
            
            # Buscamos si el email o el username generado ya existen
            existing_user_by_email = users.find_user_by_email(cursor, email)
            existing_user_by_username = users.find_user_by_username(cursor, new_username)
            
            if existing_user_by_email:
                flash(f'El email {email} ya está registrado. Por favor, selecciona "Sí" en "¿Ya tienes un usuario?"', 'error')
                return redirect(url_for('index'))
            
            if existing_user_by_username:
                 # Si el username generado ya existe, se podría añadir un sufijo
                 flash('Error: El nombre de usuario generado ya existe. Intenta con otro teléfono o nombre.', 'error')
                 return redirect(url_for('index'))
            
            # Crea el nuevo usuario
            user_id, _ = users.create_new_user(
                cursor, first_name, first_lastname, second_lastname, phone, email
            )
            username = new_username
            
            # Muestra el nombre de usuario autogenerado
            flash(f'¡Tu Nuevo usuario Transavi es: {username}! Tu solicitud ha sido registrada.', 'success')

        # Si no se pudo autenticar o crear el usuario, abortar el registro de solicitud.
        if user_id is None:
            flash('Error de autenticación o registro. Inténtalo de nuevo.', 'error')
            return redirect(url_for('index'))


        # --- 3. Generación del Consecutivo y Guardado de la Solicitud ---
        
        # 3.1 Generar el número de solicitud consecutivo (0001, 0002, etc.)
        last_request_num = db.get_last_request_number(cursor, user_id)
        new_request_num = str(last_request_num + 1).zfill(4) # Formato 0001, 0002...

        # 3.2 Obtiene datos del Recorrido y Entidad
        request_type = request.form['es_entidad'] # 'SI' o 'NO'
        entity_name = request.form.get('nombre_entidad', '')
        entity_phone = request.form.get('telefono_empresa', '')
        entity_notes = request.form.get('notes_entidad', '')
        activity_type = request.form['tipo_actividad']
        
        # Lugar de Recogida
        pickup_province = request.form['pickup_province']
        pickup_canton = request.form['pickup_canton']
        pickup_señas = request.form['pickup_señas']
        pickup_map_link = request.form.get('pickup_map_link', '')
        
        # Destino
        destination_province = request.form['destination_province']
        destination_canton = request.form['destination_canton']
        destination_señas = request.form['destination_señas']
        destination_map_link = request.form.get('destination_map_link', '')
        notes = request.form.get('notes', '') # Notas generales del recorrido

        # 3.3 Registra la solicitud de transporte
        cursor.execute(
            """
            INSERT INTO requests (
                user_id, request_number,
                request_type, entity_name, entity_phone, entity_notes, 
                activity_type, 
                pickup_province, pickup_canton, pickup_señas, pickup_map_link, 
                destination_province, destination_canton, destination_señas, destination_map_link, 
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, new_request_num,
                request_type, entity_name, entity_phone, entity_notes, 
                activity_type, 
                pickup_province, pickup_canton, pickup_señas, pickup_map_link, 
                destination_province, destination_canton, destination_señas, destination_map_link, 
                notes
            )
        )
        conn.commit()
        
        # Muestra el número de solicitud en el mensaje flash
        flash(f'Número de Solicitud generado: {username}-{new_request_num}', 'info')


    except Exception as e:
        conn.rollback()
        print(f"Error al procesar la solicitud: {e}") 
        flash(f'Ocurrió un error al procesar tu solicitud. Error interno: {e}', 'error')
    finally:
        conn.close()

    # Redirigir al formulario, mostrando el mensaje flash.
    return redirect(url_for('index'))

@app.route('/formulario')
def index():
    """Ruta para la página del formulario. Abierta a todo público."""
    # Eliminamos el chequeo de sesión para permitir el acceso directo al formulario.
    return render_template('index.html')

if __name__ == '__main__':
    # Usar un puerto diferente ya que el 5000 puede estar en uso en algunos entornos.
    # Si estás ejecutando localmente, puedes cambiar el puerto.
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
