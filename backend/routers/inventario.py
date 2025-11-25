from fastapi import APIRouter, HTTPException
from database import get_db_connection
from schemas import InsumoCreate, InsumoUpdate, MovimientoInventario

router = APIRouter()

# --- READ (LEER) ---
@router.get("/api/inventario")
def get_inventario():
    """Obtener inventario con estado calculado"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                i.*,
                CASE
                    WHEN i.stock > i.stock_minimo * 2 THEN 'optimo'
                    WHEN i.stock > i.stock_minimo THEN 'bajo'
                    ELSE 'critico'
                END as estado_stock
            FROM inventario i
            ORDER BY i.nombre
        """)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- CREATE (CREAR) ---
@router.post("/api/inventario")
def create_insumo(insumo: InsumoCreate):
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
        
        # Registrar movimiento inicial automático
        id_insumo = cursor.lastrowid
        cursor.execute("""
            INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, motivo, usuario)
            VALUES (%s, 'entrada', %s, 'Stock Inicial', 'admin')
        """, (id_insumo, insumo.stock))
        conn.commit()

        return {"mensaje": "Insumo creado", "id": id_insumo}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- UPDATE (ACTUALIZAR) ---
@router.put("/api/inventario/{id_insumo}")
def update_insumo(id_insumo: int, insumo: InsumoUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Construcción dinámica de la query
        campos = []
        valores = []

        if insumo.nombre: campos.append("nombre = %s"); valores.append(insumo.nombre)
        if insumo.categoria: campos.append("categoria = %s"); valores.append(insumo.categoria)
        if insumo.stock_minimo is not None: campos.append("stock_minimo = %s"); valores.append(insumo.stock_minimo)
        if insumo.precio_unitario is not None: campos.append("precio_unitario = %s"); valores.append(insumo.precio_unitario)
        if insumo.unidad: campos.append("unidad = %s"); valores.append(insumo.unidad)
        # Nota: El stock real no se edita aquí, se modifica vía Movimientos

        if not campos:
            return {"mensaje": "Nada que actualizar"}

        valores.append(id_insumo)
        query = f"UPDATE inventario SET {', '.join(campos)} WHERE id = %s"
        
        cursor.execute(query, valores)
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Insumo no encontrado")

        return {"mensaje": "Insumo actualizado"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- DELETE (ELIMINAR) ---
@router.delete("/api/inventario/{id_insumo}")
def delete_insumo(id_insumo: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # La tabla movimientos_inventario debe tener ON DELETE CASCADE en la BD
        cursor.execute("DELETE FROM inventario WHERE id = %s", (id_insumo,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Insumo no encontrado")

        return {"mensaje": "Insumo eliminado correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# --- MOVIMIENTOS ---
@router.post("/api/inventario/movimiento")
def registrar_movimiento(movimiento: MovimientoInventario):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT stock FROM inventario WHERE id = %s", (movimiento.id_insumo,))
        res = cursor.fetchone()
        if not res: raise HTTPException(status_code=404, detail="Insumo no existe")
        
        stock_actual = res[0]
        nuevo_stock = stock_actual

        if movimiento.tipo_movimiento == 'entrada':
            nuevo_stock += movimiento.cantidad
        elif movimiento.tipo_movimiento == 'salida':
            nuevo_stock -= movimiento.cantidad
            if nuevo_stock < 0: raise HTTPException(status_code=400, detail="Stock insuficiente")
        elif movimiento.tipo_movimiento == 'ajuste':
            nuevo_stock = movimiento.cantidad # Ajuste manual directo
            
        # Actualizar stock maestro
        cursor.execute("UPDATE inventario SET stock = %s WHERE id = %s", (nuevo_stock, movimiento.id_insumo))
        
        # Registrar historial
        cursor.execute("""
            INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, motivo, usuario)
            VALUES (%s, %s, %s, %s, %s)
        """, (movimiento.id_insumo, movimiento.tipo_movimiento, movimiento.cantidad, movimiento.motivo, movimiento.usuario))
        
        conn.commit()
        return {"mensaje": "Movimiento registrado", "nuevo_stock": nuevo_stock}
    except HTTPException: raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Se mantiene get_movimientos_insumo y get_alertas igual que antes...