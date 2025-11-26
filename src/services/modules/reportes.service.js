import apiClient from '../apiClient';

export default {
    async getReporteGeneral(fechaInicio, fechaFin) {
        const params = { fecha_inicio: fechaInicio, fecha_fin: fechaFin };
        const response = await apiClient.get('/reportes/general', { params });
        return response.data;
    },
    async getReporteEmpleados(fechaInicio, fechaFin) {
        const params = { fecha_inicio: fechaInicio, fecha_fin: fechaFin };
        const response = await apiClient.get('/reportes/empleados', { params });
        return response.data;
    },
    async getReporteServiciosDiarios(dias = 30) {
        const response = await apiClient.get('/reportes/servicios-diarios', { params: { dias } });
        return response.data;
    },
    async getReporteConvenios(fechaInicio, fechaFin) {
        const params = { fecha_inicio: fechaInicio, fecha_fin: fechaFin };
        const response = await apiClient.get('/reportes/convenios', { params });
        return response.data;
    },
    async getReporteInventario() {
        const response = await apiClient.get('/reportes/inventario');
        return response.data;
    },
    async getReporteFinanciero(anio) {
        const params = anio ? { anio } : {};
        const response = await apiClient.get('/reportes/financiero', { params });
        return response.data;
    }
}