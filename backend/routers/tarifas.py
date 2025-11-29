from fastapi import APIRouter, HTTPException

from backend.repositories import TarifaRepository
from backend.schemas import TarifaUpdate

router = APIRouter()
repo = TarifaRepository()

@router.get("/api/tarifas")
def get_tarifas():
    try:
        return repo.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tarifas/{tipo_vehiculo}/{tipo_servicio}")
def get_tarifa_especifica(tipo_vehiculo: str, tipo_servicio: str):
    try:
        tarifa = repo.get_specific(tipo_vehiculo, tipo_servicio)
        if not tarifa: raise HTTPException(status_code=404, detail="Tarifa no encontrada")
        return tarifa
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/tarifas/{tipo_vehiculo}/{tipo_servicio}")
def update_tarifa(tipo_vehiculo: str, tipo_servicio: str, tarifa: TarifaUpdate):
    try:
        rows = repo.update(tipo_vehiculo, tipo_servicio, tarifa.precio)
        if rows == 0: raise HTTPException(status_code=404, detail="Tarifa no encontrada")
        return {"mensaje": "Tarifa actualizada"}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tarifas/vehiculo/{tipo_vehiculo}")
def get_tarifas_vehiculo(tipo_vehiculo: str):
    try:
        return repo.get_by_vehiculo(tipo_vehiculo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tarifas/tipos/vehiculos")
def get_tipos_vehiculos():
    try:
        return repo.get_types_vehiculos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tarifas/tipos/servicios")
def get_tipos_servicios():
    try:
        return repo.get_types_servicios()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
