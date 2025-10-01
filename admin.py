import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
import db
import users
import re
from functools import wraps

# Creamos el Blueprint (Plano) para las rutas de autenticación
# El nombre del blueprint es 'admin_bp' y su prefijo de URL es '/'
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/')

DATABASE = 'db.db'

# --- Funciones de Utilidad de Base de Datos para el Blueprint ---

def get_db():
    """Abre una conexión a la base de datos si aún no hay una."""
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        # Usamos la ruta completa para asegurar la conexión, como en db.py
        db_conn = db.get_db_connection()
    return db_conn

@admin_bp.teardown_request
def close_connection(exception):
    """Cierra la conexión a la base de datos al finalizar la solicitud."""
    db_conn = getattr(g, '_database', None)
    if db_conn is not None:
        db_conn.close()

# --- Decorador para requerir autenticación (opcional, pero útil) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Asumiendo que guardas el ID del usuario en la sesión al hacer login
        if session.get('user_id') is None:
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('admin_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas de Autenticación ---

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión del usuario existente."""
    if request.method == 'POST':
        # Se requiere al menos uno de los dos campos
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()

        conn = get_db()
        cursor = conn.cursor()
        
        user_data = None
        
        # 1. Buscar el usuario por username o email
        if username:
            user_data = users.find_user_by_username(cursor, username)
        
        if not user_data and email:
            user_data = users.find_user_by_email(cursor, email)
        
        
        if user_data:
            # Iniciar Sesión (Simulación de autenticación exitosa)
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            flash(f'¡Bienvenido de nuevo, {user_data["username"]}!', 'success')
            return redirect(url_for('index')) 
        else:
            flash('Usuario o Email no encontrado. Intenta de nuevo o regístrate.', 'error')
            
    return render_template('login.html')


@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja el registro de nuevos usuarios."""
    if request.method == 'POST':
        first_name = request.form['first_name'].strip()
        first_lastname = request.form['first_lastname'].strip()
        second_lastname = request.form['second_lastname'].strip()
        phone = request.form['phone'].strip()
        email = request.form['email'].strip()

        conn = get_db()
        cursor = conn.cursor()

        # Validaciones de existencia
        if users.find_user_by_email(cursor, email):
            flash(f'El email {email} ya está registrado. Por favor, inicia sesión.', 'error')
            return redirect(url_for('admin_bp.register'))

        # Generar nombre de usuario y verificar si ya existe
        new_username = users.generate_custom_username(first_name, first_lastname, second_lastname, phone)
        if users.find_user_by_username(cursor, new_username):
            # Si el nombre de usuario generado ya existe (muy improbable, pero posible), se avisa.
            flash('Error: El nombre de usuario generado ya existe. Contacta a soporte.', 'error')
            return redirect(url_for('admin_bp.register'))
        
        # Crear el nuevo usuario
        try:
            user_id, final_username = users.create_new_user(
                cursor, first_name, first_lastname, second_lastname, phone, email
            )
            conn.commit()
            
            # Iniciar Sesión automáticamente
            session['user_id'] = user_id
            session['username'] = final_username
            flash(f'¡Registro exitoso! Tu nuevo usuario es: {final_username}', 'success')
            return redirect(url_for('index'))
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Error de base de datos durante el registro: {e}")
            flash('Ocurrió un error en la base de datos al registrar el usuario.', 'error')
        
    return render_template('register.html')


@admin_bp.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('admin_bp.login'))
