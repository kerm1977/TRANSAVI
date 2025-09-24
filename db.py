import sqlite3

DATABASE_NAME = 'db.db'

def get_db_connection():
    """Establece y retorna una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Permite acceder a los datos por nombre de columna
    return conn

def create_tables():
    """Crea las tablas 'users' y 'requests' si no existen."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de Usuarios
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
    
    # Tabla de Solicitudes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pickup_location TEXT NOT NULL,
            destination TEXT NOT NULL,
            notes TEXT,
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    create_tables()
    print("Tablas de la base de datos creadas exitosamente.")
