from fastapi import APIRouter, HTTPException

from backend.repositories import InventarioRepository
from backend.schemas import InsumoCreate, InsumoUpdate, MovimientoInventario

router = APIRouter()
repo = InventarioRepository()

@router.get("/api/inventario")
def get_inventario():
    try:
        return repo.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/inventario")
def create_insumo(insumo: InsumoCreate):
    try:
        new_id = repo.create(insumo)
        return {"mensaje": "Insumo creado", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/inventario/{id_insumo}")
def update_insumo(id_insumo: int, insumo: InsumoUpdate):
    try:
        campos, vals = [], []
        if insumo.nombre: campos.append("nombre=%s"); vals.append(insumo.nombre)
        if insumo.categoria: campos.append("categoria=%s"); vals.append(insumo.categoria)
        if insumo.stock_minimo is not None: campos.append("stock_minimo=%s"); vals.append(insumo.stock_minimo)
        if insumo.precio_unitario is not None: campos.append("precio_unitario=%s"); vals.append(insumo.precio_unitario)
        if insumo.unidad: campos.append("unidad=%s"); vals.append(insumo.unidad)

        if not campos: return {"mensaje": "Nada que actualizar"}
        
        rows = repo.update_dynamic(id_insumo, campos, vals)
        if rows == 0: raise HTTPException(status_code=404, detail="Insumo no encontrado")
        return {"mensaje": "Insumo actualizado"}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/inventario/{id_insumo}")
def delete_insumo(id_insumo: int):
    try:
        rows = repo.delete(id_insumo)
        if rows == 0: raise HTTPException(status_code=404, detail="Insumo no encontrado")
        return {"mensaje": "Insumo eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/inventario/movimiento")
def registrar_movimiento(movimiento: MovimientoInventario):
    try:
        res = repo.get_stock(movimiento.id_insumo)
        if not res: raise HTTPException(status_code=404, detail="Insumo no existe")
        
        stock_actual = res[0]
        nuevo_stock = stock_actual

        if movimiento.tipo_movimiento == 'entrada': nuevo_stock += movimiento.cantidad
        elif movimiento.tipo_movimiento == 'salida':
            nuevo_stock -= movimiento.cantidad
            if nuevo_stock < 0: raise HTTPException(status_code=400, detail="Stock insuficiente")
        elif movimiento.tipo_movimiento == 'ajuste': nuevo_stock = movimiento.cantidad
            
        repo.registrar_movimiento(movimiento, nuevo_stock)
        return {"mensaje": "Movimiento registrado", "nuevo_stock": nuevo_stock}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
