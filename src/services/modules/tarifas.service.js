import apiClient from '../apiClient';

export default {
    async getTarifas() {
        const response = await apiClient.get('/tarifas');
        return response.data;
    },
    async getTarifaEspecifica(tipoVehiculo, tipoServicio) {
        const response = await apiClient.get(`/tarifas/${tipoVehiculo}/${tipoServicio}`);
        return response.data;
    },
    async updateTarifa(tipoVehiculo, tipoServicio, precio) {
        const response = await apiClient.put(`/tarifas/${tipoVehiculo}/${tipoServicio}`, { precio });
        return response.data;
    },
    async getTarifasVehiculo(tipoVehiculo) {
        const response = await apiClient.get(`/tarifas/vehiculo/${tipoVehiculo}`);
        return response.data;
    },
    async getTiposVehiculos() {
        const response = await apiClient.get('/tarifas/tipos/vehiculos');
        return response.data;
    },
    async getTiposServicios() {
        const response = await apiClient.get('/tarifas/tipos/servicios');
        return response.data;
    }
}