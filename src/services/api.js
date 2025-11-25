import axios from 'axios';

// Configuración base de axios
const API_URL = 'http://localhost:8000/api';

// Crear instancia de axios con configuración base
const apiClient = axios.create({
    baseURL: API_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor para agregar el token JWT a todas las peticiones
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor para manejar errores globalmente
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response) {
            // Error de respuesta del servidor
            if (error.response.status === 401) {
                // Token inválido o expirado - redirigir a login
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
            }
        } else if (error.request) {
            // Error de red - sin respuesta del servidor
            console.error('Error de red: No se pudo conectar con el servidor');
        } else {
            console.error('Error:', error.message);
        }
        return Promise.reject(error);
    }
);

export default {
    // --- AUTH ---
    async login(username, password) {
        const response = await apiClient.post('/login', { username, password });
        return response.data;
    },

    
    // --- SERVICIOS ---
    async getServicios() {
        const response = await apiClient.get('/servicios');
        return response.data;
    },
    async createServicio(servicio) {
        const response = await apiClient.post('/servicios', servicio);
        return response.data;
    },
    // NUEVO: Update
    async updateServicio(id, servicio) {
        const response = await apiClient.put(`/servicios/${id}`, servicio);
        return response.data;
    },
    // NUEVO: Delete (Cancelar)
    async deleteServicio(id) {
        const response = await apiClient.delete(`/servicios/${id}`);
        return response.data;
    },
    // --- EMPLEADOS ---
    async getEmpleados() {
        const response = await apiClient.get('/empleados');
        return response.data;
    },
    async createEmpleado(empleado) {
        const response = await apiClient.post('/empleados', empleado);
        return response.data;
    },
    // AGREGAR ESTOS DOS:
    async updateEmpleado(id, empleado) {
        const response = await apiClient.put(`/empleados/${id}`, empleado);
        return response.data;
    },
    async deleteEmpleado(id) {
        const response = await apiClient.delete(`/empleados/${id}`);
        return response.data;
    },
    
    // ...
   // ... dentro de export default { ...
    
    // --- INVENTARIO ---
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
    // NUEVO: Función Eliminar
    async deleteInsumo(id) {
        const response = await apiClient.delete(`/inventario/${id}`);
        return response.data;
    },
    async registrarMovimiento(movimiento) {
        const response = await apiClient.post('/inventario/movimiento', movimiento);
        return response.data;
    },
    
    // ... resto de funciones

    // --- LIQUIDACIONES ---
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
    // ... dentro del objeto export default { ...

    // --- LIQUIDACIONES ---
    async getLiquidaciones() {
        const response = await apiClient.get('/liquidaciones');
        return response.data;
    },
    // ... (otras funciones existentes) ...
    
    // AGREGAR ESTA FUNCIÓN NUEVA:
    async deleteLiquidacion(id) {
        const response = await apiClient.delete(`/liquidaciones/${id}`);
        return response.data;
    },
    
    // ...
   // ... en export default { ...
    
    // --- CONVENIOS ---
    async getConvenios() {
        const response = await apiClient.get('/convenios');
        return response.data;
    },
    async createConvenio(data) {
        const response = await apiClient.post('/convenios', data);
        return response.data;
    },
    async updateConvenio(id, data) {
        const response = await apiClient.put(`/convenios/${id}`, data);
        return response.data;
    },
    // NUEVO: Delete
    async deleteConvenio(id) {
        const response = await apiClient.delete(`/convenios/${id}`);
        return response.data;
    },
    // NUEVOS: Vehículos
    async getVehiculosConvenio(idConvenio) {
        const response = await apiClient.get(`/convenios/${idConvenio}/vehiculos`);
        return response.data;
    },
    async addVehiculoConvenio(idConvenio, vehiculo) {
        const response = await apiClient.post(`/convenios/${idConvenio}/vehiculos`, vehiculo);
        return response.data;
    },
    async removeVehiculoConvenio(idVehiculo) {
        const response = await apiClient.delete(`/convenios/vehiculos/${idVehiculo}`);
        return response.data;
    },

    // --- TARIFAS ---
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
    },

    // --- REPORTES ---
    async getReporteGeneral(fechaInicio, fechaFin) {
        const params = {};
        if (fechaInicio) params.fecha_inicio = fechaInicio;
        if (fechaFin) params.fecha_fin = fechaFin;
        const response = await apiClient.get('/reportes/general', { params });
        return response.data;
    },
    async getReporteEmpleados(fechaInicio, fechaFin) {
        const params = {};
        if (fechaInicio) params.fecha_inicio = fechaInicio;
        if (fechaFin) params.fecha_fin = fechaFin;
        const response = await apiClient.get('/reportes/empleados', { params });
        return response.data;
    },
    async getReporteServiciosDiarios(dias = 30) {
        const response = await apiClient.get('/reportes/servicios-diarios', { params: { dias } });
        return response.data;
    },
    async getReporteConvenios(fechaInicio, fechaFin) {
        const params = {};
        if (fechaInicio) params.fecha_inicio = fechaInicio;
        if (fechaFin) params.fecha_fin = fechaFin;
        const response = await apiClient.get('/reportes/convenios', { params });
        return response.data;
    },
    async getReporteInventario() {
        const response = await apiClient.get('/reportes/inventario');
        return response.data;
    },
    async getReporteFinanciero(anio) {
        const params = {};
        if (anio) params.anio = anio;
        const response = await apiClient.get('/reportes/financiero', { params });
        return response.data;
    },

    // --- DASHBOARD ---
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
    },
    
    
};