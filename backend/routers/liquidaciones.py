from fastapi import APIRouter, HTTPException

from backend.repositories import EmpleadoRepository, LiquidacionRepository
from backend.schemas import LiquidacionCreate

router = APIRouter()
liq_repo = LiquidacionRepository()
emp_repo = EmpleadoRepository()

@router.get("/liquidaciones")
def get_liquidaciones():
    try:
        return liq_repo.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/liquidaciones/{id_liquidacion}")
def get_liquidacion_detalle(id_liquidacion: int):
    try:
        liquidacion = liq_repo.get_by_id(id_liquidacion)
        if not liquidacion: raise HTTPException(status_code=404, detail="Liquidación no encontrada")

        liquidacion['servicios'] = liq_repo.get_detalles(liquidacion['id_empleado'], liquidacion['periodo_inicio'], liquidacion['periodo_fin'])
        return liquidacion
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/liquidaciones/calcular")
def calcular_liquidacion(liquidacion: LiquidacionCreate):
    try:
        if not emp_repo.get_by_id(liquidacion.id_empleado):
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        if liq_repo.check_duplicates(liquidacion.id_empleado, liquidacion.periodo_inicio, liquidacion.periodo_fin):
            raise HTTPException(status_code=400, detail="Ya existe una liquidación para este período")

        totales = liq_repo.calculate_totals(liquidacion.id_empleado, liquidacion.periodo_inicio, liquidacion.periodo_fin)
        if totales['total_servicios'] == 0:
             raise HTTPException(status_code=400, detail="No hay servicios completados en este período.")

        new_id = liq_repo.create(liquidacion, totales)
        return {"mensaje": "Liquidación creada", "id": new_id}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/liquidaciones/{id_liquidacion}/pagar")
def marcar_liquidacion_pagada(id_liquidacion: int):
    try:
        rows = liq_repo.mark_paid(id_liquidacion)
        if rows == 0: raise HTTPException(status_code=404, detail="Liquidación no encontrada o ya pagada")
        return {"mensaje": "Liquidación pagada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/liquidaciones/{id_liquidacion}")
def eliminar_liquidacion(id_liquidacion: int):
    try:
        liq = liq_repo.get_by_id(id_liquidacion)
        if not liq: raise HTTPException(status_code=404, detail="Liquidación no encontrada")
        if liq['estado'] == 'pagada': raise HTTPException(status_code=400, detail="No se puede eliminar una liquidación pagada")

        liq_repo.delete(id_liquidacion)
        return {"mensaje": "Liquidación eliminada"}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
