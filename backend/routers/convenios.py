from fastapi import APIRouter, HTTPException
from database import get_db_connection
from schemas import ConvenioCreate, ConvenioUpdate, VehiculoConvenioCreate

router = APIRouter()

# --- READ (LEER) ---
@router.get("/api/convenios")
def get_convenios():
    """Obtener convenios con conteo de vehículos activos"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Query optimizada para contar vehículos activos
        cursor.execute("""
            SELECT 
                c.*,
                (SELECT COUNT(*) FROM vehiculos_convenio v 
                 WHERE v.id_convenio = c.id AND v.estado = 'activo') as total_vehiculos
            FROM convenios c
            ORDER BY c.estado, c.nombre_empresa
        """)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- CREATE (CREAR) ---
@router.post("/api/convenios")
def create_convenio(convenio: ConvenioCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO convenios
            (nombre_empresa, rut_empresa, contacto, telefono, email, direccion,
             tipo_descuento, valor_descuento, fecha_inicio, fecha_termino, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            convenio.nombre_empresa, convenio.rut_empresa, convenio.contacto,
            convenio.telefono, convenio.email, convenio.direccion,
            convenio.tipo_descuento, convenio.valor_descuento,
            convenio.fecha_inicio, convenio.fecha_termino, convenio.observaciones
        ))
        conn.commit()
        return {"mensaje": "Convenio creado", "id": cursor.lastrowid}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- UPDATE (ACTUALIZAR) ---
@router.put("/api/convenios/{id_convenio}")
def update_convenio(id_convenio: int, convenio: ConvenioUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        campos = []
        valores = []
        # Mapeo dinámico simple
        if convenio.nombre_empresa: campos.append("nombre_empresa=%s"); valores.append(convenio.nombre_empresa)
        if convenio.rut_empresa: campos.append("rut_empresa=%s"); valores.append(convenio.rut_empresa)
        if convenio.contacto: campos.append("contacto=%s"); valores.append(convenio.contacto)
        if convenio.telefono: campos.append("telefono=%s"); valores.append(convenio.telefono)
        if convenio.email: campos.append("email=%s"); valores.append(convenio.email)
        if convenio.tipo_descuento: campos.append("tipo_descuento=%s"); valores.append(convenio.tipo_descuento)
        if convenio.valor_descuento is not None: campos.append("valor_descuento=%s"); valores.append(convenio.valor_descuento)
        if convenio.fecha_inicio: campos.append("fecha_inicio=%s"); valores.append(convenio.fecha_inicio)
        if convenio.fecha_termino: campos.append("fecha_termino=%s"); valores.append(convenio.fecha_termino)
        if convenio.estado: campos.append("estado=%s"); valores.append(convenio.estado)
        
        if not campos: return {"mensaje": "Sin cambios"}
        
        valores.append(id_convenio)
        cursor.execute(f"UPDATE convenios SET {', '.join(campos)} WHERE id = %s", valores)
        conn.commit()
        return {"mensaje": "Convenio actualizado"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- DELETE (SOFT DELETE) ---
@router.delete("/api/convenios/{id_convenio}")
def delete_convenio(id_convenio: int):
    """Desactivar convenio"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE convenios SET estado = 'inactivo' WHERE id = %s", (id_convenio,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Convenio no encontrado")
        return {"mensaje": "Convenio desactivado"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- VEHÍCULOS ---
@router.post("/api/convenios/{id_convenio}/vehiculos")
def add_vehiculo_convenio(id_convenio: int, vehiculo: VehiculoConvenioCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Validar duplicados activos
        cursor.execute("SELECT id FROM vehiculos_convenio WHERE patente = %s AND estado = 'activo'", (vehiculo.patente,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Esta patente ya tiene un convenio activo")

        cursor.execute("""
            INSERT INTO vehiculos_convenio (id_convenio, patente, tipo_vehiculo, modelo, color)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_convenio, vehiculo.patente, vehiculo.tipo_vehiculo, vehiculo.modelo, vehiculo.color))
        
        conn.commit()
        return {"mensaje": "Vehículo agregado", "id": cursor.lastrowid}
    except HTTPException: raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/api/convenios/{id_convenio}/vehiculos")
def get_vehiculos_convenio(id_convenio: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM vehiculos_convenio WHERE id_convenio = %s AND estado='activo'", (id_convenio,))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.delete("/api/convenios/vehiculos/{id_vehiculo}")
def remove_vehiculo_convenio(id_vehiculo: int):
    """Desactivar vehículo del convenio"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE vehiculos_convenio SET estado = 'inactivo' WHERE id = %s", (id_vehiculo,))
        conn.commit()
        return {"mensaje": "Vehículo eliminado del convenio"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
# Asegúrate de que esto esté en convenios.py
@router.get("/api/convenios/validar/{patente}")
def validar_convenio_patente(patente: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Busca convenio activo para esa patente
        cursor.execute("""
            SELECT c.id as id_convenio, c.nombre_empresa, c.tipo_descuento, c.valor_descuento, v.tipo_vehiculo
            FROM vehiculos_convenio v
            JOIN convenios c ON v.id_convenio = c.id
            WHERE v.patente = %s AND v.estado = 'activo' AND c.estado = 'activo'
        """, (patente,))
        
        convenio = cursor.fetchone()
        if convenio:
            return {"tiene_convenio": True, "convenio": convenio}
        return {"tiene_convenio": False}
    finally:
        cursor.close()
        conn.close()