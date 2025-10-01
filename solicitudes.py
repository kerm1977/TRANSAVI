import sqlite3
# Importamos Blueprint en lugar de Flask para encapsular las rutas
from flask import Blueprint, render_template, g, url_for, jsonify

# Creamos el Blueprint (Plano) para todas las rutas relacionadas con solicitudes
# El nombre del blueprint es 'solicitudes_bp' y su prefijo de URL es '/solicitudes'
solicitudes_bp = Blueprint('solicitudes_bp', __name__, url_prefix='/solicitudes')

DATABASE = 'db.db'

# --- Funciones de Utilidad de Base de Datos ---

def get_db():
    """Abre una conexión a la base de datos si aún no hay una."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre
    return db

@solicitudes_bp.teardown_request
def close_connection(exception):
    """Cierra la conexión a la base de datos al finalizar la solicitud."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Endpoint principal del Panel de Solicitudes ---

# La ruta aquí es solo '/', pero la URL completa será '/solicitudes/' debido al url_prefix
@solicitudes_bp.route('/', methods=['GET'])
# Se renombra la función a 'solicitudes' para que el endpoint sea 'solicitudes_bp.solicitudes'
def solicitudes(): 
    """
    Ruta para mostrar el panel de administración con la lista de usuarios
    y el total de solicitudes.
    """
    try:
        db = get_db()
        cursor = db.cursor()

        # Consulta SQL para obtener todos los usuarios y el conteo de sus solicitudes
        query = """
        SELECT 
            u.id, 
            u.username, 
            u.first_name,
            u.first_lastname,
            u.second_lastname,
            u.email,
            u.phone,
            COUNT(r.id) AS request_count 
        FROM users u
        LEFT JOIN requests r ON u.id = r.user_id
        GROUP BY u.id
        ORDER BY u.id DESC;
        """
        
        cursor.execute(query)
        # Convertimos los Rows a diccionarios para Jinja
        users_data = [dict(row) for row in cursor.fetchall()]

        # Nota: Aquí se está pasando la lista completa, pero para una aplicación grande 
        # se debería implementar paginación.

        return render_template('solicitudes.html', users=users_data)

    except sqlite3.Error as e:
        # En caso de error de DB (ej. tabla no existe), se muestra un error amigable.
        print(f"Database error: {e}")
        return render_template('solicitudes.html', users=None, error="Error al cargar datos de la base de datos.")

# --- Endpoint API para el Detalle de Solicitud (Requiere JSON/AJAX) ---
@solicitudes_bp.route('/user_requests/<string:username>', methods=['GET'])
def api_user_requests(username):
    """
    Endpoint para obtener el detalle de todas las solicitudes de un usuario específico 
    (utilizado por la función de búsqueda en JavaScript de solicitudes.html).
    """
    try:
        db = get_db()
        cursor = db.cursor()

        # 1. Buscar el ID del usuario por su username
        cursor.execute("SELECT id, first_name, first_lastname, email, phone FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        
        if not user_row:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
            
        user_data = dict(user_row)
        user_id = user_data['id']

        # 2. Obtener todas las solicitudes (facturas) de ese usuario
        # Se asume que la tabla 'requests' tiene un campo llamado 'user_id' y otros campos relevantes como 'request_number'
        request_query = """
        SELECT 
            id, 
            request_number, 
            request_date,
            origin_province,
            destination_province,
            service_type,
            total_price
            -- Agrega todos los campos relevantes de tu tabla requests aquí
        FROM requests 
        WHERE user_id = ? 
        ORDER BY request_date DESC;
        """
        cursor.execute(request_query, (user_id,))
        requests_list = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            "success": True, 
            "user": user_data,
            "requests": requests_list
        })

    except sqlite3.Error as e:
        print(f"Database error in API: {e}")
        return jsonify({"success": False, "message": f"Error interno del servidor: {e}"}), 500
