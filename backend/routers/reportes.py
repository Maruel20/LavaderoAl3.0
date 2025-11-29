from fastapi import APIRouter, HTTPException
from typing import Optional

from backend.repositories import ReporteRepository

router = APIRouter()
repo = ReporteRepository()

@router.get("/api/reportes/general")
def get_reporte_general(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    try:
        where = "WHERE s.fecha BETWEEN %s AND %s AND s.estado = 'completado'" if fecha_inicio else "WHERE MONTH(s.fecha) = MONTH(CURDATE()) AND YEAR(s.fecha) = YEAR(CURDATE()) AND s.estado = 'completado'"
        params = [fecha_inicio, fecha_fin] if fecha_inicio else []
        return repo.get_general(where, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reportes/empleados")
def get_reporte_empleados(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    try:
        where = "AND s.fecha BETWEEN %s AND %s" if fecha_inicio else "AND MONTH(s.fecha) = MONTH(CURDATE()) AND YEAR(s.fecha) = YEAR(CURDATE())"
        params = [fecha_inicio, fecha_fin] if fecha_inicio else []
        return repo.get_empleados(where, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reportes/servicios-diarios")
def get_reporte_servicios_diarios(dias: int = 30):
    try:
        return repo.get_servicios_diarios(dias)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reportes/convenios")
def get_reporte_convenios(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    try:
        where = "AND s.fecha BETWEEN %s AND %s" if fecha_inicio else "AND MONTH(s.fecha) = MONTH(CURDATE()) AND YEAR(s.fecha) = YEAR(CURDATE())"
        params = [fecha_inicio, fecha_fin] if fecha_inicio else []
        return repo.get_convenios(where, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reportes/inventario")
def get_reporte_inventario():
    try:
        return repo.get_inventario()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reportes/financiero")
def get_reporte_financiero(anio: Optional[int] = None):
    try:
        from datetime import datetime
        year = anio if anio else datetime.now().year
        return repo.get_financiero(year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
