import mysql.connector.pooling
from config import DB_CONFIG

# Creamos el pool una sola vez (Singleton implícito)
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="lavadero_pool",
    pool_size=5,
    pool_reset_session=True,
    **DB_CONFIG
)

def get_db_connection():
    try:
        return db_pool.get_connection()
    except Exception as err:
        print(f"Error en el pool de base de datos: {err}")
        raise err