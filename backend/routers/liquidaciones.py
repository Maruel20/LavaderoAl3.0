from fastapi import APIRouter, HTTPException
from database import get_db_connection
from schemas import LiquidacionCreate
from datetime import datetime

router = APIRouter()

# --- READ (LEER TODOS) ---
@router.get("/api/liquidaciones")
def get_liquidaciones():
    """Obtener todas las liquidaciones con datos del empleado"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Se incluye e.porcentaje_comision para que se vea en la tabla
        cursor.execute("""
            SELECT
                l.*,
                e.nombre as nombre_empleado,
                e.rut,
                e.porcentaje_comision
            FROM liquidaciones l
            JOIN empleados e ON l.id_empleado = e.id
            ORDER BY l.fecha_creacion DESC
        """)

        liquidaciones = cursor.fetchall()
        return liquidaciones

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener liquidaciones: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# --- READ (LEER DETALLE) ---
@router.get("/api/liquidaciones/{id_liquidacion}")
def get_liquidacion_detalle(id_liquidacion: int):
    """Obtener detalle de una liquidación específica"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Obtener cabecera
        cursor.execute("""
            SELECT
                l.*,
                e.nombre as nombre_empleado,
                e.rut,
                e.email,
                e.telefono,
                e.porcentaje_comision
            FROM liquidaciones l
            JOIN empleados e ON l.id_empleado = e.id
            WHERE l.id = %s
        """, (id_liquidacion,))

        liquidacion = cursor.fetchone()

        if not liquidacion:
            raise HTTPException(status_code=404, detail="Liquidación no encontrada")

        # 2. Obtener servicios asociados (Detalle)
        cursor.execute("""
            SELECT
                s.id,
                s.patente,
                s.tipo_vehiculo,
                s.tipo_servicio,
                s.fecha,
                s.monto_total,
                s.monto_comision
            FROM servicios s
            WHERE s.id_empleado = %s
                AND s.fecha BETWEEN %s AND %s
                AND s.estado = 'completado'
            ORDER BY s.fecha DESC
        """, (liquidacion['id_empleado'], liquidacion['periodo_inicio'], liquidacion['periodo_fin']))

        servicios = cursor.fetchall()
        liquidacion['servicios'] = servicios

        return liquidacion

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalle: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# --- CREATE (CREAR/CALCULAR) ---
@router.post("/api/liquidaciones/calcular")
def calcular_liquidacion(liquidacion: LiquidacionCreate):
    """Calcular y crear una nueva liquidación"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Validar empleado
        cursor.execute("SELECT id, nombre FROM empleados WHERE id = %s", (liquidacion.id_empleado,))
        empleado = cursor.fetchone()
        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        # 2. Validar duplicados en fecha
        cursor.execute("""
            SELECT id FROM liquidaciones
            WHERE id_empleado = %s
                AND (
                    (periodo_inicio <= %s AND periodo_fin >= %s)
                    OR (periodo_inicio <= %s AND periodo_fin >= %s)
                )
        """, (
            liquidacion.id_empleado,
            liquidacion.periodo_inicio, liquidacion.periodo_inicio,
            liquidacion.periodo_fin, liquidacion.periodo_fin
        ))

        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe una liquidación para este período")

        # 3. Calcular totales
        cursor.execute("""
            SELECT
                COUNT(*) as total_servicios,
                COALESCE(SUM(monto_total), 0) as monto_total_servicios,
                COALESCE(SUM(monto_comision), 0) as total_comisiones
            FROM servicios
            WHERE id_empleado = %s
                AND fecha BETWEEN %s AND %s
                AND estado = 'completado'
        """, (liquidacion.id_empleado, liquidacion.periodo_inicio, liquidacion.periodo_fin))

        totales = cursor.fetchone()

        if totals['total_servicios'] == 0:
             raise HTTPException(status_code=400, detail="No hay servicios completados en este período.")

        # 4. Insertar Liquidación
        cursor.execute("""
            INSERT INTO liquidaciones
            (id_empleado, periodo_inicio, periodo_fin, total_servicios,
             monto_total_servicios, total_comisiones, estado, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, 'pendiente', NOW())
        """, (
            liquidacion.id_empleado,
            liquidacion.periodo_inicio,
            liquidacion.periodo_fin,
            totales['total_servicios'],
            totales['monto_total_servicios'],
            totales['total_comisiones']
        ))

        id_liquidacion = cursor.lastrowid

        # 5. Insertar Detalle (Snapshot)
        cursor.execute("""
            INSERT INTO detalle_liquidaciones
            (id_liquidacion, id_servicio, monto_servicio, monto_comision)
            SELECT %s, id, monto_total, monto_comision
            FROM servicios
            WHERE id_empleado = %s
                AND fecha BETWEEN %s AND %s
                AND estado = 'completado'
        """, (id_liquidacion, liquidacion.id_empleado, liquidacion.periodo_inicio, liquidacion.periodo_fin))

        conn.commit()

        return {"mensaje": "Liquidación creada exitosamente", "id": id_liquidacion}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# --- UPDATE (PAGAR) ---
@router.put("/api/liquidaciones/{id_liquidacion}/pagar")
def marcar_liquidacion_pagada(id_liquidacion: int):
    """Marcar liquidación como pagada"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE liquidaciones
            SET estado = 'pagada', fecha_pago = CURDATE()
            WHERE id = %s AND estado = 'pendiente'
        """, (id_liquidacion,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Liquidación no encontrada o ya pagada")
            
        return {"mensaje": "Liquidación pagada"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- DELETE (ELIMINAR) ---
@router.delete("/api/liquidaciones/{id_liquidacion}")
def eliminar_liquidacion(id_liquidacion: int):
    """Eliminar una liquidación (Solo si está pendiente)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar estado antes de borrar
        cursor.execute("SELECT estado FROM liquidaciones WHERE id = %s", (id_liquidacion,))
        resultado = cursor.fetchone() # Devuelve tupla (estado,)

        if not resultado:
            raise HTTPException(status_code=404, detail="Liquidación no encontrada")
        
        # Bloquear borrado si ya está pagada
        if resultado[0] == 'pagada':
             raise HTTPException(status_code=400, detail="No se puede eliminar una liquidación ya pagada.")

        # Eliminar (Cascade borrará los detalles)
        cursor.execute("DELETE FROM liquidaciones WHERE id = %s", (id_liquidacion,))
        conn.commit()

        return {"mensaje": "Liquidación eliminada exitosamente"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
    finally:
        cursor.close()
        conn.close()