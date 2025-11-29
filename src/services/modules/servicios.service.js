import apiClient from '../apiClient';

export default {
    async getServicios() {
        const response = await apiClient.get('/servicios');
        return response.data;
    },
    async createServicio(servicio) {
        const response = await apiClient.post('/servicios', servicio);
        return response.data;
    },
    async updateServicio(id, servicio) {
        const response = await apiClient.put(`/servicios/${id}`, servicio);
        return response.data;
    },
    async deleteServicio(id) {
        const response = await apiClient.delete(`/servicios/${id}`);
        return response.data;
    }
}
