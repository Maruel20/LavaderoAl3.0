from fastapi import APIRouter, HTTPException
from database import get_db_connection
from schemas import ServicioCreate, ServicioUpdate

router = APIRouter()

# --- READ (LEER) ---
@router.get("/api/servicios")
def get_servicios():
    """Obtener todos los servicios con datos de empleado"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT s.*, e.nombre as nombre_empleado, c.nombre_empresa
            FROM servicios s
            LEFT JOIN empleados e ON s.id_empleado = e.id
            LEFT JOIN convenios c ON s.id_convenio = c.id
            ORDER BY s.fecha DESC
            LIMIT 100
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- CREATE (CREAR) ---
@router.post("/api/servicios")
def create_servicio(data: ServicioCreate):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Obtener datos del empleado para la comisión
        cursor.execute("SELECT porcentaje_comision FROM empleados WHERE id = %s", (data.id_empleado,))
        empleado = cursor.fetchone()
        if not empleado: 
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        # 2. Calcular Comisión
        porcentaje_emp = empleado['porcentaje_comision']
        monto_comision = int(data.monto_total * (porcentaje_emp / 100))

        # 3. Preparar variables Convenio
        es_convenio = 1 if data.id_convenio else 0
        id_convenio = data.id_convenio
        descuento = data.descuento if data.descuento else 0

        # 4. Insertar (Incluyendo observaciones)
        query = """
            INSERT INTO servicios 
            (patente, tipo_vehiculo, tipo_servicio, monto_total, monto_comision, 
             id_empleado, id_convenio, es_convenio, descuento, observaciones, fecha, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'completado')
        """
        values = (
            data.patente.upper(), 
            data.tipo_vehiculo, 
            data.tipo_servicio, 
            data.monto_total, 
            monto_comision, 
            data.id_empleado,
            id_convenio,
            es_convenio,
            descuento,
            data.observaciones  # Agregado
        )

        cursor.execute(query, values)
        conn.commit()
        return {"mensaje": "Servicio registrado", "id": cursor.lastrowid}

    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- UPDATE (ACTUALIZAR) ---
@router.put("/api/servicios/{id_servicio}")
def update_servicio(id_servicio: int, data: ServicioUpdate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Verificar existencia y obtener datos actuales para recálculo
        cursor.execute("SELECT * FROM servicios WHERE id = %s", (id_servicio,))
        actual = cursor.fetchone()
        if not actual:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        # 2. Recalcular comisión si cambia monto o empleado
        monto_comision_nuevo = None
        
        nuevo_monto = data.monto_total if data.monto_total is not None else actual['monto_total']
        nuevo_empleado_id = data.id_empleado if data.id_empleado is not None else actual['id_empleado']
        
        # Si cambiaron datos críticos, recalculamos comisión
        if data.monto_total is not None or data.id_empleado is not None:
            cursor.execute("SELECT porcentaje_comision FROM empleados WHERE id = %s", (nuevo_empleado_id,))
            emp = cursor.fetchone()
            if emp:
                monto_comision_nuevo = int(float(nuevo_monto) * (emp['porcentaje_comision'] / 100))

        # 3. Construir Query Dinámica
        campos = []
        vals = []
        
        if data.patente: campos.append("patente=%s"); vals.append(data.patente.upper())
        if data.tipo_vehiculo: campos.append("tipo_vehiculo=%s"); vals.append(data.tipo_vehiculo)
        if data.tipo_servicio: campos.append("tipo_servicio=%s"); vals.append(data.tipo_servicio)
        if data.monto_total is not None: campos.append("monto_total=%s"); vals.append(data.monto_total)
        if data.id_empleado is not None: campos.append("id_empleado=%s"); vals.append(data.id_empleado)
        if data.observaciones is not None: campos.append("observaciones=%s"); vals.append(data.observaciones)
        
        if monto_comision_nuevo is not None:
            campos.append("monto_comision=%s")
            vals.append(monto_comision_nuevo)

        if not campos:
            return {"mensaje": "No hubo cambios"}
        
        vals.append(id_servicio)
        sql = f"UPDATE servicios SET {', '.join(campos)} WHERE id = %s"
        
        cursor.execute(sql, vals)
        conn.commit()
        
        return {"mensaje": "Servicio actualizado correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- DELETE (SOFT DELETE) ---
@router.delete("/api/servicios/{id_servicio}")
def cancelar_servicio(id_servicio: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE servicios 
            SET estado = 'cancelado', monto_comision = 0 
            WHERE id = %s
        """, (id_servicio,))
        conn.commit()
        return {"mensaje": "Servicio cancelado"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()