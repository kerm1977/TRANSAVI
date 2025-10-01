import sqlite3
import os

# Definir la ruta de la base de datos dentro de un directorio 'instance'
# Esto es una buena práctica en Flask
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'db.db')
# Asegurarse de que el directorio 'instance' exista
os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)


def get_db_connection():
    """Establece y retorna una conexión a la base de datos SQLite."""
    # Usamos la ruta completa para asegurar la conexión
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a los datos por nombre de columna
    return conn

def get_last_request_number(cursor, user_id):
    """Obtiene el último número de solicitud para un user_id dado."""
    cursor.execute(
        'SELECT request_number FROM requests WHERE user_id = ? ORDER BY id DESC LIMIT 1',
        (user_id,)
    )
    result = cursor.fetchone()
    if result:
        # Devuelve el número de solicitud como entero
        return int(result['request_number'])
    return 0 # Si no hay solicitudes, devuelve 0


def create_tables():
    """Crea las tablas 'users', 'requests' y la nueva tabla 'admins' si no existen."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de Usuarios (Cuentas de Solicitud/Clientes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            first_lastname TEXT NOT NULL,
            second_lastname TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')

    # NUEVA TABLA: Administradores (Cuentas de Superusuario)
    # Nota: En una aplicación real, la contraseña debe estar hasheada.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL, 
            role TEXT DEFAULT 'admin' -- Rol simple para diferenciar
        )
    ''')

    # Tabla de Solicitudes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            
            -- Nuevo campo consecutivo por usuario
            request_number TEXT NOT NULL,
            
            -- Información de la Entidad/Solicitud
            request_type TEXT NOT NULL, -- SI / NO
            entity_name TEXT,
            entity_phone TEXT,
            entity_notes TEXT,
            
            -- Información del Recorrido
            activity_type TEXT NOT NULL,
            
            -- Lugar de Recogida
            pickup_province TEXT NOT NULL,
            pickup_canton TEXT NOT NULL,
            pickup_señas TEXT NOT NULL,
            pickup_map_link TEXT,
            
            -- Destino
            destination_province TEXT NOT NULL,
            destination_canton TEXT NOT NULL,
            destination_señas TEXT NOT NULL,
            destination_map_link TEXT,
            
            -- Notas generales del recorrido
            notes TEXT,
            
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # OPCIONAL: Insertar un administrador inicial si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        # Administrador por defecto: admin / 12345
        # NOTA: En producción, usar una contraseña hasheada como hash(12345)
        cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ('admin', '12345'))
        print("Administrador inicial creado: Usuario='admin', Contraseña='12345'")
    
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    create_tables()
    print("Tablas de la base de datos creadas exitosamente.")
