import re
import db 

def generate_custom_username(first_name, first_lastname, second_lastname, phone):
    """
    Genera un nombre de usuario con el formato: 
    Inicial_Nombre + Inicial_Apellido1 + Inicial_Apellido2 + '-' + Teléfono.
    Ejemplo: jpr-88227500
    """
    # Limpiar y obtener las iniciales
    initial_name = first_name.strip()[0].lower() if first_name else ''
    initial_lastname1 = first_lastname.strip()[0].lower() if first_lastname else ''
    initial_lastname2 = second_lastname.strip()[0].lower() if second_lastname else ''
    
    # Limpiar el teléfono (quitar espacios o guiones)
    phone_clean = re.sub(r'[\s-]', '', phone)

    # El formato del ejemplo era P1A1A2-88227500. Se usa la iniciales + teléfono limpio
    return f"{initial_name}{initial_lastname1}{initial_lastname2}-{phone_clean}"


def find_user_by_email(cursor, email):
    """Busca un usuario en la base de datos por su email."""
    cursor.execute('SELECT id, username FROM users WHERE email = ?', (email,))
    return cursor.fetchone()

def find_user_by_username(cursor, username):
    """Busca un usuario en la base de datos por su nombre de usuario."""
    # Seleccionamos todos los campos necesarios para cargar el formulario
    cursor.execute(
        'SELECT id, username, first_name, first_lastname, second_lastname, phone, email FROM users WHERE username = ?', 
        (username,)
    )
    return cursor.fetchone()

def create_new_user(cursor, first_name, first_lastname, second_lastname, phone, email):
    """
    Registra un nuevo usuario en la base de datos con el nombre de usuario generado.
    Retorna el ID del nuevo usuario y su nombre de usuario.
    """
    username = generate_custom_username(first_name, first_lastname, second_lastname, phone)
    cursor.execute(
        'INSERT INTO users (username, first_name, first_lastname, second_lastname, phone, email) VALUES (?, ?, ?, ?, ?, ?)',
        (username, first_name, first_lastname, second_lastname, phone, email)
    )
    user_id = cursor.lastrowid
    return user_id, username

# FUNCIÓN 1: Búsqueda exacta (la ideal, usada primero en app.py)
def get_full_request_details_by_user_id_and_number(cursor, user_id, request_number):
    """
    Obtiene los detalles de una solicitud específica por user_id y número de solicitud (coincidencia EXACTA).
    """
    cursor.execute(
        """
        SELECT 
            r.*, 
            u.username, u.first_name, u.first_lastname, u.second_lastname, u.phone, u.email
        FROM requests r
        JOIN users u ON r.user_id = u.id
        WHERE r.user_id = ? AND r.request_number = ?
        """,
        (user_id, request_number)
    )
    return cursor.fetchone()

# FUNCIÓN 2: Búsqueda tolerante (usada si la búsqueda exacta falla)
def get_full_request_details_by_user_id_and_number_like(cursor, user_id, request_number):
    """
    Obtiene los detalles de una solicitud por user_id y número de solicitud (coincidencia LIKE),
    útil para datos con caracteres inesperados (ej: '0001N').
    """
    # Buscamos solicitudes cuyo request_number EMPIECE con el número rellenado (ej: '0001%').
    cursor.execute(
        """
        SELECT 
            r.*, 
            u.username, u.first_name, u.first_lastname, u.second_lastname, u.phone, u.email
        FROM requests r
        JOIN users u ON r.user_id = u.id
        WHERE r.user_id = ? AND r.request_number LIKE ?
        LIMIT 1
        """,
        (user_id, f'{request_number}%')
    )
    return cursor.fetchone()

# NUEVA FUNCIÓN: Obtiene la lista de todos los usuarios y su conteo de solicitudes
def get_all_users_with_request_count(cursor):
    """
    Retorna una lista de todos los usuarios con el conteo de solicitudes asociadas.
    """
    cursor.execute(
        """
        SELECT 
            u.id, 
            u.username, 
            COUNT(r.id) as request_count 
        FROM users u
        LEFT JOIN requests r ON u.id = r.user_id
        GROUP BY u.id, u.username
        ORDER BY u.username
        """
    )
    return cursor.fetchall()
# Nota: Se eliminó la función original 'get_full_request_details' para usar las dos nuevas funciones.
