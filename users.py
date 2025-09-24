import re
import random
import string

def generate_username(first_name, first_lastname):
    """Genera un nombre de usuario sencillo y fácil de recordar."""
    # Quita espacios y convierte a minúsculas
    first_name_clean = re.sub(r'\s+', '', first_name).lower()
    first_lastname_clean = re.sub(r'\s+', '', first_lastname).lower()
    
    # Crea un nombre de usuario con el formato: inicial_nombre + apellido + número aleatorio
    username = f"{first_name_clean[0]}{first_lastname_clean}"
    random_part = ''.join(random.choices(string.digits, k=3))
    return f"{username}{random_part}"

def find_user_by_email(cursor, email):
    """Busca un usuario en la base de datos por su email."""
    cursor.execute('SELECT id, username FROM users WHERE email = ?', (email,))
    return cursor.fetchone()

def create_new_user(cursor, first_name, first_lastname, second_lastname, phone, email):
    """
    Registra un nuevo usuario en la base de datos con un nombre de usuario generado.
    Retorna el ID del nuevo usuario y su nombre de usuario.
    """
    username = generate_username(first_name, first_lastname)
    cursor.execute(
        'INSERT INTO users (username, first_name, first_lastname, second_lastname, phone, email) VALUES (?, ?, ?, ?, ?, ?)',
        (username, first_name, first_lastname, second_lastname, phone, email)
    )
    user_id = cursor.lastrowid
    return user_id, username
