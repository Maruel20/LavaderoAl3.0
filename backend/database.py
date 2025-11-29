import mysql.connector.pooling
from typing import Optional

from backend.config import DB_CONFIG

# Pool lazy initialization to avoid failing at import time when DB is down
_db_pool: Optional[mysql.connector.pooling.MySQLConnectionPool] = None

def _get_db_pool() -> mysql.connector.pooling.MySQLConnectionPool:
    global _db_pool
    if _db_pool is None:
        _db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="lavadero_pool",
            pool_size=20,
            pool_reset_session=True,
            **DB_CONFIG,
        )
    return _db_pool

def get_db_connection():
    try:
        pool = _get_db_pool()
        return pool.get_connection()
    except Exception as err:
        print(f"Error en el pool de base de datos: {err}")
        raise err
