from backend.database import get_db_connection
from backend.schemas import UsuarioCreate

class AuthRepository:
    def get_by_username(self, username: str):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def create_user(self, user: UsuarioCreate, hashed_password: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)"
            cursor.execute(query, (user.username, hashed_password, user.rol or 'usuario'))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
