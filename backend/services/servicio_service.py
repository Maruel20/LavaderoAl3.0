from fastapi import HTTPException
from repositories import ServicioRepository, EmpleadoRepository
from services.calculo_service import CalculoService
from schemas import ServicioCreate, ServicioUpdate

class ServicioService:
    def __init__(self):
        # Inyección de dependencias manual
        self.servicio_repo = ServicioRepository()
        self.empleado_repo = EmpleadoRepository()
        self.calculo_service = CalculoService()

    def listar_servicios(self):
        return self.servicio_repo.get_all()

    def registrar_servicio(self, data: ServicioCreate):
        # 1. Validar que el empleado existe y obtener su % de comisión
        empleado = self.empleado_repo.get_by_id(data.id_empleado)
        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        # 2. Calcular Comisión (Lógica de Negocio)
        monto_comision = self.calculo_service.calcular_comision(
            data.monto_total, 
            empleado['porcentaje_comision']
        )
        
        # 3. Preparar datos de convenio (maneja nulos automáticamente)
        es_convenio, descuento = self.calculo_service.preparar_datos_convenio(
            data.id_convenio, 
            data.descuento
        )

        # 4. Persistencia
        try:
            new_id = self.servicio_repo.create(data, monto_comision, es_convenio, descuento)
            return new_id
        except Exception as e:
            # Loguear el error real en consola para debug
            print(f"Error DB: {e}")
            raise HTTPException(status_code=500, detail="Error interno al registrar el servicio")

    def actualizar_servicio(self, id_servicio: int, data: ServicioUpdate):
        # 1. Verificar que el servicio exista
        actual = self.servicio_repo.get_by_id(id_servicio)
        if not actual:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        # 2. Construir query dinámica solo con los campos que cambiaron
        campos = []
        vals = []

        if data.patente: 
            campos.append("patente=%s")
            vals.append(data.patente.upper())
        if data.tipo_vehiculo: 
            campos.append("tipo_vehiculo=%s")
            vals.append(data.tipo_vehiculo)
        if data.tipo_servicio: 
            campos.append("tipo_servicio=%s")
            vals.append(data.tipo_servicio)
        if data.monto_total is not None: 
            campos.append("monto_total=%s")
            vals.append(data.monto_total)
        if data.id_empleado is not None: 
            campos.append("id_empleado=%s")
            vals.append(data.id_empleado)
        if data.observaciones is not None: 
            campos.append("observaciones=%s")
            vals.append(data.observaciones)

        # 3. Lógica especial: Recalcular comisión si cambia el monto o el empleado
        if data.monto_total is not None or data.id_empleado is not None:
            # Usamos el nuevo valor si existe, si no, el que ya tenía en BD
            nuevo_monto = data.monto_total if data.monto_total is not None else actual['monto_total']
            nuevo_emp_id = data.id_empleado if data.id_empleado is not None else actual['id_empleado']
            
            empleado = self.empleado_repo.get_by_id(nuevo_emp_id)
            if empleado:
                nueva_comision = self.calculo_service.calcular_comision(
                    float(nuevo_monto), 
                    empleado['porcentaje_comision']
                )
                campos.append("monto_comision=%s")
                vals.append(nueva_comision)

        # Si no hay nada que actualizar, retornamos False
        if not campos:
            return False 

        # 4. Persistencia
        try:
            self.servicio_repo.update_dynamic(id_servicio, campos, vals)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def cancelar_servicio(self, id_servicio: int):
        try:
            rows = self.servicio_repo.cancel(id_servicio)
            if rows == 0:
                raise HTTPException(status_code=404, detail="Servicio no encontrado")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))