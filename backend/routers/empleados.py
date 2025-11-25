from fastapi import APIRouter, HTTPException
from database import get_db_connection
from schemas import EmpleadoCreate
import mysql.connector

router = APIRouter()

# --- READ (LEER) ---
@router.get("/api/empleados")
def get_empleados():
    """Obtener todos los empleados (activos e inactivos para gestión)"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Traemos todos para que el admin pueda ver/reactivar si es necesario
        cursor.execute("SELECT * FROM empleados ORDER BY estado, nombre")
        empleados = cursor.fetchall()
        return empleados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener empleados: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- CREATE (CREAR) ---
@router.post("/api/empleados")
def create_empleado(empleado: EmpleadoCreate):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Validación de Cédula (usamos campo 'rut' de la BD por compatibilidad)
        cursor.execute("SELECT id FROM empleados WHERE rut = %s", (empleado.rut,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un empleado con esta Cédula")

        query = """
            INSERT INTO empleados (nombre, rut, telefono, email, porcentaje_comision, estado)
            VALUES (%s, %s, %s, %s, %s, 'activo')
        """
        values = (empleado.nombre, empleado.rut, empleado.telefono, empleado.email, empleado.porcentaje_comision)
        cursor.execute(query, values)
        conn.commit()

        return {"message": "Empleado creado correctamente", "id": cursor.lastrowid}
    except HTTPException:
        raise
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- UPDATE (ACTUALIZAR) ---
@router.put("/api/empleados/{id_empleado}")
def update_empleado(id_empleado: int, empleado: EmpleadoCreate):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si la cédula ya existe en OTRO empleado
        cursor.execute("SELECT id FROM empleados WHERE rut = %s AND id != %s", (empleado.rut, id_empleado))
        if cursor.fetchone():
             raise HTTPException(status_code=400, detail="Esa cédula ya pertenece a otro empleado")

        query = """
            UPDATE empleados 
            SET nombre = %s, rut = %s, telefono = %s, email = %s, porcentaje_comision = %s
            WHERE id = %s
        """
        values = (empleado.nombre, empleado.rut, empleado.telefono, empleado.email, empleado.porcentaje_comision, id_empleado)
        
        cursor.execute(query, values)
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        return {"mensaje": "Empleado actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- DELETE (BORRADO LÓGICO) ---
@router.delete("/api/empleados/{id_empleado}")
def delete_empleado(id_empleado: int):
    """Desactivar un empleado (Soft Delete)"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Cambiamos estado a 'inactivo' en lugar de DELETE FROM
        cursor.execute("UPDATE empleados SET estado = 'inactivo' WHERE id = %s", (id_empleado,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        return {"mensaje": "Empleado desactivado correctamente"}
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()