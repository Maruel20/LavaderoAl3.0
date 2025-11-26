from database import get_db_connection

class TarifaRepository:
    def get_all(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM tarifas WHERE activo = TRUE ORDER BY tipo_vehiculo, tipo_servicio")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_specific(self, vehiculo: str, servicio: str):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM tarifas WHERE tipo_vehiculo=%s AND tipo_servicio=%s AND activo=TRUE", (vehiculo, servicio))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def update(self, vehiculo: str, servicio: str, precio: float):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE tarifas SET precio=%s WHERE tipo_vehiculo=%s AND tipo_servicio=%s AND activo=TRUE", (precio, vehiculo, servicio))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def get_by_vehiculo(self, vehiculo: str):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM tarifas WHERE tipo_vehiculo=%s AND activo=TRUE ORDER BY tipo_servicio", (vehiculo,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_types_vehiculos(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT DISTINCT tipo_vehiculo FROM tarifas WHERE activo = TRUE ORDER BY tipo_vehiculo")
            return [t['tipo_vehiculo'] for t in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def get_types_servicios(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT DISTINCT tipo_servicio, descripcion FROM tarifas WHERE activo = TRUE ORDER BY tipo_servicio")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()