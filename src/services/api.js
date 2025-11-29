import authService from './modules/auth.service';
import empleadosService from './modules/empleados.service';
import serviciosService from './modules/servicios.service';
import inventarioService from './modules/inventario.service';
import liquidacionesService from './modules/liquidaciones.service';
import conveniosService from './modules/convenios.service';
import tarifasService from './modules/tarifas.service';
import reportesService from './modules/reportes.service';
import dashboardService from './modules/dashboard.service';

const api = {
    ...authService,
    ...empleadosService,
    ...serviciosService,
    ...inventarioService,
    ...liquidacionesService,
    ...conveniosService,
    ...tarifasService,
    ...reportesService,
    ...dashboardService
};

export default api;
