from fastapi import APIRouter, HTTPException
from database import get_db_connection
from schemas import TarifaUpdate

router = APIRouter()

@router.get("/api/tarifas")
def get_tarifas():
    """Obtener todas las tarifas"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM tarifas
            WHERE activo = TRUE
            ORDER BY tipo_vehiculo, tipo_servicio
        """)

        tarifas = cursor.fetchall()
        return tarifas

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tarifas: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/tarifas/{tipo_vehiculo}/{tipo_servicio}")
def get_tarifa_especifica(tipo_vehiculo: str, tipo_servicio: str):
    """Obtener una tarifa específica por tipo de vehículo y servicio"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM tarifas
            WHERE tipo_vehiculo = %s
                AND tipo_servicio = %s
                AND activo = TRUE
        """, (tipo_vehiculo, tipo_servicio))

        tarifa = cursor.fetchone()

        if not tarifa:
            raise HTTPException(status_code=404, detail="Tarifa no encontrada")

        return tarifa

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tarifa: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/api/tarifas/{tipo_vehiculo}/{tipo_servicio}")
def update_tarifa(tipo_vehiculo: str, tipo_servicio: str, tarifa: TarifaUpdate):
    """Actualizar el precio de una tarifa"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE tarifas
            SET precio = %s
            WHERE tipo_vehiculo = %s
                AND tipo_servicio = %s
                AND activo = TRUE
        """, (tarifa.precio, tipo_vehiculo, tipo_servicio))

        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarifa no encontrada")

        return {"mensaje": "Tarifa actualizada exitosamente"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar tarifa: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/tarifas/vehiculo/{tipo_vehiculo}")
def get_tarifas_vehiculo(tipo_vehiculo: str):
    """Obtener todas las tarifas de un tipo de vehículo"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM tarifas
            WHERE tipo_vehiculo = %s
                AND activo = TRUE
            ORDER BY tipo_servicio
        """, (tipo_vehiculo,))

        tarifas = cursor.fetchall()
        return tarifas

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tarifas del vehículo: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/tarifas/tipos/vehiculos")
def get_tipos_vehiculos():
    """Obtener todos los tipos de vehículos disponibles"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT DISTINCT tipo_vehiculo
            FROM tarifas
            WHERE activo = TRUE
            ORDER BY tipo_vehiculo
        """)

        tipos = cursor.fetchall()
        return [tipo['tipo_vehiculo'] for tipo in tipos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tipos de vehículos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/tarifas/tipos/servicios")
def get_tipos_servicios():
    """Obtener todos los tipos de servicios disponibles"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT DISTINCT tipo_servicio, descripcion
            FROM tarifas
            WHERE activo = TRUE
            ORDER BY tipo_servicio
        """)

        servicios = cursor.fetchall()
        return servicios

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tipos de servicios: {str(e)}")
    finally:
        cursor.close()
        conn.close()
