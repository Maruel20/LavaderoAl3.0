from fastapi import APIRouter, Depends, HTTPException

from backend.repositories import DashboardRepository
from backend.routers.auth import verify_token

router = APIRouter(dependencies=[Depends(verify_token)])
repo = DashboardRepository()

@router.get("/dashboard/metricas")
def get_metricas_dashboard():
    try:
        return repo.get_metricas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/servicios-recientes")
def get_servicios_recientes(limit: int = 10):
    try:
        return repo.get_servicios_recientes(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/alertas-inventario")
def get_alertas_inventario():
    try:
        return repo.get_alertas_inventario()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/empleados-top")
def get_empleados_top(limit: int = 5):
    try:
        return repo.get_empleados_top(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/grafico-servicios")
def get_grafico_servicios(dias: int = 7):
    try:
        return repo.get_grafico_servicios(dias)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/servicios-por-tipo")
def get_servicios_por_tipo():
    try:
        return repo.get_servicios_por_tipo()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/liquidaciones-pendientes")
def get_liquidaciones_pendientes():
    try:
        return repo.get_liquidaciones_pendientes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
