from fastapi import APIRouter, HTTPException
from database import get_db_connection
from typing import Optional

router = APIRouter()

@router.get("/api/reportes/general")
def get_reporte_general(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    """Obtener reporte general de ingresos y servicios"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Si no se proporcionan fechas, usar el mes actual
        where_clause = ""
        params = []

        if fecha_inicio and fecha_fin:
            where_clause = "WHERE s.fecha BETWEEN %s AND %s AND s.estado = 'completado'"
            params = [fecha_inicio, fecha_fin]
        else:
            where_clause = "WHERE MONTH(s.fecha) = MONTH(CURDATE()) AND YEAR(s.fecha) = YEAR(CURDATE()) AND s.estado = 'completado'"

        # Ingresos totales
        cursor.execute(f"""
            SELECT
                COUNT(*) as total_servicios,
                COALESCE(SUM(monto_total), 0) as ingresos_totales,
                COALESCE(SUM(monto_comision), 0) as total_comisiones,
                COALESCE(AVG(monto_total), 0) as ticket_promedio
            FROM servicios s
            {where_clause}
        """, params)

        totales = cursor.fetchone()

        # Servicios por tipo
        cursor.execute(f"""
            SELECT
                tipo_servicio,
                COUNT(*) as cantidad,
                SUM(monto_total) as ingresos
            FROM servicios s
            {where_clause}
            GROUP BY tipo_servicio
            ORDER BY ingresos DESC
        """, params)

        por_tipo = cursor.fetchall()

        # Servicios por vehículo
        cursor.execute(f"""
            SELECT
                tipo_vehiculo,
                COUNT(*) as cantidad,
                SUM(monto_total) as ingresos
            FROM servicios s
            {where_clause}
            GROUP BY tipo_vehiculo
            ORDER BY ingresos DESC
        """, params)

        por_vehiculo = cursor.fetchall()

        return {
            "totales": totales,
            "por_tipo_servicio": por_tipo,
            "por_tipo_vehiculo": por_vehiculo
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte general: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/reportes/empleados")
def get_reporte_empleados(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    """Obtener reporte de rendimiento por empleado"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        where_clause = ""
        params = []

        if fecha_inicio and fecha_fin:
            where_clause = "AND s.fecha BETWEEN %s AND %s"
            params = [fecha_inicio, fecha_fin]
        else:
            where_clause = "AND MONTH(s.fecha) = MONTH(CURDATE()) AND YEAR(s.fecha) = YEAR(CURDATE())"

        cursor.execute(f"""
            SELECT
                e.id,
                e.nombre,
                e.rut,
                e.porcentaje_comision,
                COUNT(s.id) as total_servicios,
                COALESCE(SUM(s.monto_total), 0) as total_vendido,
                COALESCE(SUM(s.monto_comision), 0) as total_comisiones,
                COALESCE(AVG(s.monto_total), 0) as ticket_promedio
            FROM empleados e
            LEFT JOIN servicios s ON e.id = s.id_empleado AND s.estado = 'completado' {where_clause}
            WHERE e.estado = 'activo'
            GROUP BY e.id, e.nombre, e.rut, e.porcentaje_comision
            ORDER BY total_vendido DESC
        """, params)

        empleados = cursor.fetchall()
        return empleados

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte de empleados: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/reportes/servicios-diarios")
def get_reporte_servicios_diarios(dias: int = 30):
    """Obtener servicios e ingresos diarios de los últimos N días"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                DATE(fecha) as fecha,
                COUNT(*) as total_servicios,
                SUM(monto_total) as ingresos,
                SUM(monto_comision) as comisiones
            FROM servicios
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                AND estado = 'completado'
            GROUP BY DATE(fecha)
            ORDER BY fecha DESC
        """, (dias,))

        servicios_diarios = cursor.fetchall()
        return servicios_diarios

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte de servicios diarios: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/reportes/convenios")
def get_reporte_convenios(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    """Obtener reporte de servicios por convenio"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        where_clause = ""
        params = []

        if fecha_inicio and fecha_fin:
            where_clause = "AND s.fecha BETWEEN %s AND %s"
            params = [fecha_inicio, fecha_fin]
        else:
            where_clause = "AND MONTH(s.fecha) = MONTH(CURDATE()) AND YEAR(s.fecha) = YEAR(CURDATE())"

        cursor.execute(f"""
            SELECT
                c.id,
                c.nombre_empresa,
                c.rut_empresa,
                COUNT(s.id) as total_servicios,
                COALESCE(SUM(s.monto_total), 0) as total_facturado,
                COALESCE(SUM(s.descuento), 0) as total_descuentos
            FROM convenios c
            LEFT JOIN servicios s ON c.id = s.id_convenio
                AND s.es_convenio = TRUE
                AND s.estado = 'completado'
                {where_clause}
            WHERE c.estado = 'activo'
            GROUP BY c.id, c.nombre_empresa, c.rut_empresa
            ORDER BY total_facturado DESC
        """, params)

        convenios = cursor.fetchall()
        return convenios

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte de convenios: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/reportes/inventario")
def get_reporte_inventario():
    """Obtener reporte de estado del inventario"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Resumen general
        cursor.execute("""
            SELECT
                COUNT(*) as total_insumos,
                SUM(stock * precio_unitario) as valor_total_inventario,
                SUM(CASE WHEN stock <= stock_minimo THEN 1 ELSE 0 END) as insumos_stock_critico,
                SUM(CASE WHEN stock <= stock_minimo * 1.5 THEN 1 ELSE 0 END) as insumos_stock_bajo
            FROM inventario
        """)

        resumen = cursor.fetchone()

        # Insumos por categoría
        cursor.execute("""
            SELECT
                categoria,
                COUNT(*) as cantidad_insumos,
                SUM(stock) as stock_total,
                SUM(stock * precio_unitario) as valor_categoria
            FROM inventario
            GROUP BY categoria
            ORDER BY valor_categoria DESC
        """)

        por_categoria = cursor.fetchall()

        # Insumos con stock bajo
        cursor.execute("""
            SELECT
                nombre,
                categoria,
                stock,
                stock_minimo,
                precio_unitario,
                CASE
                    WHEN stock <= stock_minimo THEN 'CRITICO'
                    WHEN stock <= stock_minimo * 1.5 THEN 'BAJO'
                    ELSE 'NORMAL'
                END as nivel_alerta
            FROM inventario
            WHERE stock <= stock_minimo * 1.5
            ORDER BY stock ASC
        """)

        stock_bajo = cursor.fetchall()

        return {
            "resumen": resumen,
            "por_categoria": por_categoria,
            "stock_bajo": stock_bajo
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte de inventario: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/api/reportes/financiero")
def get_reporte_financiero(anio: Optional[int] = None):
    """Obtener reporte financiero mensual del año"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not anio:
            cursor.execute("SELECT YEAR(CURDATE()) as anio")
            anio = cursor.fetchone()['anio']

        cursor.execute("""
            SELECT
                MONTH(fecha) as mes,
                MONTHNAME(fecha) as nombre_mes,
                COUNT(*) as total_servicios,
                SUM(monto_total) as ingresos_brutos,
                SUM(monto_comision) as total_comisiones,
                SUM(monto_total - monto_comision) as ingresos_netos
            FROM servicios
            WHERE YEAR(fecha) = %s
                AND estado = 'completado'
            GROUP BY MONTH(fecha), MONTHNAME(fecha)
            ORDER BY mes
        """, (anio,))

        mensual = cursor.fetchall()

        # Calcular totales del año
        cursor.execute("""
            SELECT
                COUNT(*) as total_servicios_anio,
                COALESCE(SUM(monto_total), 0) as ingresos_brutos_anio,
                COALESCE(SUM(monto_comision), 0) as comisiones_anio,
                COALESCE(SUM(monto_total - monto_comision), 0) as ingresos_netos_anio
            FROM servicios
            WHERE YEAR(fecha) = %s
                AND estado = 'completado'
        """, (anio,))

        totales_anio = cursor.fetchone()

        return {
            "anio": anio,
            "mensual": mensual,
            "totales": totales_anio
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte financiero: {str(e)}")
    finally:
        cursor.close()
        conn.close()
