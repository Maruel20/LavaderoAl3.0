from backend.database import get_db_connection
from backend.schemas import InsumoCreate, MovimientoInventario

class InventarioRepository:
    def get_all(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT i.*,
                CASE
                    WHEN i.stock > i.stock_minimo * 2 THEN 'optimo'
                    WHEN i.stock > i.stock_minimo THEN 'bajo'
                    ELSE 'critico'
                END as estado_stock
                FROM inventario i ORDER BY i.nombre
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_stock(self, id_insumo: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT stock FROM inventario WHERE id = %s", (id_insumo,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def create(self, insumo: InsumoCreate):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO inventario (nombre, categoria, stock, stock_minimo, precio_unitario, unidad)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (insumo.nombre, insumo.categoria, insumo.stock, 
                                 insumo.stock_minimo, insumo.precio_unitario, insumo.unidad))
            conn.commit()
            id_insumo = cursor.lastrowid
            
            # Movimiento inicial
            cursor.execute("""
                INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, motivo, usuario)
                VALUES (%s, 'entrada', %s, 'Stock Inicial', 'admin')
            """, (id_insumo, insumo.stock))
            conn.commit()
            return id_insumo
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def update_dynamic(self, id_insumo: int, campos: list, vals: list):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            vals.append(id_insumo)
            sql = f"UPDATE inventario SET {', '.join(campos)} WHERE id = %s"
            cursor.execute(sql, vals)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def delete(self, id_insumo: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM inventario WHERE id = %s", (id_insumo,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def registrar_movimiento(self, movimiento: MovimientoInventario, nuevo_stock: float):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE inventario SET stock = %s WHERE id = %s", (nuevo_stock, movimiento.id_insumo))
            cursor.execute("""
                INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, motivo, usuario)
                VALUES (%s, %s, %s, %s, %s)
            """, (movimiento.id_insumo, movimiento.tipo_movimiento, movimiento.cantidad, movimiento.motivo, movimiento.usuario))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
