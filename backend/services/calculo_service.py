class CalculoService:
    """
    Servicio encargado exclusivamente de la lógica matemática y reglas de negocio.
    No interactúa con la base de datos.
    """

    @staticmethod
    def calcular_comision(monto_total: float, porcentaje_comision: int) -> int:
        """Calcula la comisión basada en el monto y el porcentaje del empleado."""
        if monto_total < 0 or porcentaje_comision < 0:
            return 0
        return int(monto_total * (porcentaje_comision / 100))

    @staticmethod
    def preparar_datos_convenio(id_convenio: int | None, descuento: float | None):
        """
        Determina las banderas y valores para un servicio de convenio.
        Acepta None para evitar errores de validación de tipos.
        """
        es_convenio = 1 if id_convenio else 0
        monto_descuento = descuento if descuento else 0.0
        return es_convenio, monto_descuento