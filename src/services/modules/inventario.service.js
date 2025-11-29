import apiClient from '../apiClient';

export default {
    async getInventario() {
        const response = await apiClient.get('/inventario');
        return response.data;
    },
    async createInsumo(insumo) {
        const response = await apiClient.post('/inventario', insumo);
        return response.data;
    },
    async updateInsumo(id, insumo) {
        const response = await apiClient.put(`/inventario/${id}`, insumo);
        return response.data;
    },
    async deleteInsumo(id) {
        const response = await apiClient.delete(`/inventario/${id}`);
        return response.data;
    },
    async registrarMovimiento(movimiento) {
        const response = await apiClient.post('/inventario/movimiento', movimiento);
        return response.data;
    }
}
