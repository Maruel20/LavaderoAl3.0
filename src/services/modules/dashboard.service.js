import apiClient from '../apiClient';

export default {
    async getMetricasDashboard() {
        const response = await apiClient.get('/dashboard/metricas');
        return response.data;
    },
    async getServiciosRecientes(limit = 10) {
        const response = await apiClient.get('/dashboard/servicios-recientes', { params: { limit } });
        return response.data;
    },
    async getAlertasInventarioDashboard() {
        const response = await apiClient.get('/dashboard/alertas-inventario');
        return response.data;
    },
    async getEmpleadosTop(limit = 5) {
        const response = await apiClient.get('/dashboard/empleados-top', { params: { limit } });
        return response.data;
    },
    async getGraficoServicios(dias = 7) {
        const response = await apiClient.get('/dashboard/grafico-servicios', { params: { dias } });
        return response.data;
    },
    async getServiciosPorTipo() {
        const response = await apiClient.get('/dashboard/servicios-por-tipo');
        return response.data;
    },
    async getLiquidacionesPendientes() {
        const response = await apiClient.get('/dashboard/liquidaciones-pendientes');
        return response.data;
    }
}