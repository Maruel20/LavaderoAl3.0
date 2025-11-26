import apiClient from '../apiClient';

export default {
    async getLiquidaciones() {
        const response = await apiClient.get('/liquidaciones');
        return response.data;
    },
    async getLiquidacionDetalle(id) {
        const response = await apiClient.get(`/liquidaciones/${id}`);
        return response.data;
    },
    async calcularLiquidacion(liquidacion) {
        const response = await apiClient.post('/liquidaciones/calcular', liquidacion);
        return response.data;
    },
    async marcarLiquidacionPagada(id) {
        const response = await apiClient.put(`/liquidaciones/${id}/pagar`);
        return response.data;
    },
    async getLiquidacionesEmpleado(idEmpleado) {
        const response = await apiClient.get(`/liquidaciones/empleado/${idEmpleado}`);
        return response.data;
    },
    async deleteLiquidacion(id) {
        const response = await apiClient.delete(`/liquidaciones/${id}`);
        return response.data;
    }
}