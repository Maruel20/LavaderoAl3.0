<template>
  <div class="container-fluid py-4 fade-in">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-cash-coin me-2"></i>
          Liquidaciones de Empleados
        </h2>
        <p class="text-muted">Gestiona pagos, comisiones y nómina</p>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalLiquidacion">
          <i class="bi bi-calculator me-2"></i>
          Nueva Liquidación
        </button>
      </div>
    </div>

    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
             <label class="form-label small fw-bold">Filtrar por Empleado</label>
             <select class="form-select" v-model="filtros.empleado">
               <option value="">Todos los empleados</option>
               <option v-for="emp in empleados" :key="emp.id" :value="emp.nombre">{{ emp.nombre }}</option>
             </select>
          </div>
          <div class="col-md-3">
             <label class="form-label small fw-bold">Estado</label>
             <select class="form-select" v-model="filtros.estado">
               <option value="">Todos los estados</option>
               <option value="Pendiente">Pendiente</option>
               <option value="Pagada">Pagada</option>
             </select>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card border-start border-4 border-primary h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 text-uppercase small">Total Liquidaciones</h6>
            <h3 class="mb-0">{{ liquidaciones.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-start border-4 border-warning h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 text-uppercase small">Pendientes de Pago</h6>
            <h3 class="mb-0 text-warning">{{ pendientesCount }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-start border-4 border-success h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 text-uppercase small">Pagadas</h6>
            <h3 class="mb-0 text-success">{{ liquidaciones.length - pendientesCount }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-start border-4 border-info h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 text-uppercase small">Monto Pendiente</h6>
            <h3 class="mb-0 text-info">${{ totalPendiente.toLocaleString() }}</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body p-0">
        <div v-if="cargando" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2 text-muted">Cargando datos...</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-3">ID</th>
                <th>Empleado</th>
                <th>Período</th>
                <th class="text-center">Servicios</th>
                <th class="text-end">Total Ventas</th>
                <th class="text-center">% Com.</th>
                <th class="text-end">A Pagar</th>
                <th class="text-center">Estado</th>
                <th class="text-end pe-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="liq in liquidacionesFiltradas" :key="liq.id">
                <td class="ps-3 text-muted">#{{ liq.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ liq.empleado }}</div>
                  <small class="text-muted" style="font-size: 0.8rem;">{{ liq.rut }}</small>
                </td>
                <td>
                  <small>{{ formatDate(liq.periodoInicio) }} <br> {{ formatDate(liq.periodoFin) }}</small>
                </td>
                <td class="text-center">
                   <span class="badge bg-secondary rounded-pill">{{ liq.cantidadServicios }}</span>
                </td>
                <td class="text-end text-muted">${{ liq.totalServicios.toLocaleString() }}</td>
                <td class="text-center">{{ liq.porcentajeComision }}%</td>
                <td class="text-end fw-bold text-success fs-6">${{ liq.totalComision.toLocaleString() }}</td>
                <td class="text-center">
                  <span :class="'badge rounded-pill bg-' + (liq.estado === 'Pagada' ? 'success' : 'warning text-dark')">
                    {{ liq.estado }}
                  </span>
                </td>
                <td class="text-end pe-3">
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="verDetalle(liq)" data-bs-toggle="modal" data-bs-target="#modalDetalleLiquidacion" title="Ver Detalle">
                      <i class="bi bi-eye"></i>
                    </button>
                    
                    <button v-if="liq.estado === 'Pendiente'" class="btn btn-outline-success" @click="marcarPagada(liq)" title="Marcar como Pagada">
                      <i class="bi bi-check-lg"></i>
                    </button>

                    <button v-if="liq.estado === 'Pendiente'" class="btn btn-outline-danger" @click="eliminarLiquidacion(liq)" title="Eliminar Registro">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="liquidacionesFiltradas.length === 0">
                <td colspan="9" class="text-center py-4 text-muted">
                  No se encontraron liquidaciones con los filtros actuales.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalLiquidacion" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title"><i class="bi bi-calculator me-2"></i>Generar Liquidación</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="calcularLiquidacion">
              <div class="mb-3">
                <label class="form-label fw-bold">Empleado</label>
                <select class="form-select" v-model="nuevaLiquidacion.id_empleado" required>
                  <option value="">Seleccione un empleado...</option>
                  <option v-for="emp in empleados" :key="emp.id" :value="emp.id">{{ emp.nombre }}</option>
                </select>
              </div>
              <div class="row">
                <div class="col-6 mb-3">
                  <label class="form-label fw-bold">Fecha Inicio</label>
                  <input type="date" class="form-control" v-model="nuevaLiquidacion.periodo_inicio" required>
                </div>
                <div class="col-6 mb-3">
                  <label class="form-label fw-bold">Fecha Fin</label>
                  <input type="date" class="form-control" v-model="nuevaLiquidacion.periodo_fin" required>
                </div>
              </div>
              <div class="alert alert-info d-flex align-items-center small">
                <i class="bi bi-info-circle fs-4 me-2"></i>
                <div>
                  El sistema calculará automáticamente las comisiones sumando los servicios "completados" en este rango de fechas.
                </div>
              </div>
              <div class="modal-footer px-0 pb-0 border-top-0">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="submit" class="btn btn-primary" :disabled="procesando">
                  <span v-if="procesando" class="spinner-border spinner-border-sm me-1"></span>
                  Generar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalDetalleLiquidacion" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Detalle Liquidación #{{ liquidacionSeleccionada.id }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body bg-light" v-if="liquidacionSeleccionada.id">
            <div class="card mb-3 border-0 shadow-sm">
              <div class="card-body">
                <div class="row align-items-center">
                  <div class="col-md-6">
                    <h5 class="fw-bold mb-1">{{ liquidacionSeleccionada.empleado }}</h5>
                    <p class="text-muted mb-0">{{ liquidacionSeleccionada.rut }}</p>
                    <small class="text-primary">{{ liquidacionSeleccionada.email }}</small>
                  </div>
                  <div class="col-md-6 text-md-end mt-3 mt-md-0">
                    <div class="text-muted small">Total a Pagar</div>
                    <h2 class="text-success fw-bold mb-0">${{ liquidacionSeleccionada.totalComision?.toLocaleString() }}</h2>
                    <span :class="'badge mt-2 bg-' + (liquidacionSeleccionada.estado === 'Pagada' ? 'success' : 'warning text-dark')">
                      {{ liquidacionSeleccionada.estado }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white fw-bold">Desglose de Servicios</div>
              <div class="card-body p-0">
                <div class="table-responsive" style="max-height: 350px;">
                  <table class="table table-striped mb-0 small">
                    <thead class="sticky-top bg-white">
                      <tr>
                        <th>Fecha</th>
                        <th>Vehículo</th>
                        <th>Servicio</th>
                        <th class="text-end">Monto Total</th>
                        <th class="text-end">Comisión Ganada</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="serv in detalleServicios" :key="serv.id">
                        <td>{{ formatDate(serv.fecha) }}</td>
                        <td>{{ serv.tipo_vehiculo }} <span class="text-muted">({{ serv.patente }})</span></td>
                        <td>{{ formatearServicio(serv.tipo_servicio) }}</td>
                        <td class="text-end text-muted">${{ serv.monto_total?.toLocaleString() }}</td>
                        <td class="text-end fw-bold text-success">${{ serv.monto_comision?.toLocaleString() }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            <button class="btn btn-outline-dark"><i class="bi bi-printer me-1"></i> Imprimir</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import * as bootstrap from 'bootstrap'
import api from '@/services/api' // Asegúrate de que la ruta sea correcta

export default {
  name: 'LiquidacionesView',
  data() {
    return {
      cargando: false,
      procesando: false,
      empleados: [],
      liquidaciones: [],
      detalleServicios: [],
      filtros: { empleado: '', estado: '' },
      nuevaLiquidacion: {
        id_empleado: '',
        periodo_inicio: '',
        periodo_fin: ''
      },
      liquidacionSeleccionada: {}
    }
  },
  computed: {
    liquidacionesFiltradas() {
      return this.liquidaciones.filter(l => {
        const matchEmp = this.filtros.empleado ? l.empleado === this.filtros.empleado : true;
        const matchEst = this.filtros.estado ? l.estado === this.filtros.estado : true;
        return matchEmp && matchEst;
      });
    },
    pendientesCount() {
      return this.liquidaciones.filter(l => l.estado === 'Pendiente').length;
    },
    totalPendiente() {
      return this.liquidaciones
        .filter(l => l.estado === 'Pendiente')
        .reduce((sum, l) => sum + l.totalComision, 0);
    }
  },
  async mounted() {
    await this.cargarEmpleados();
    await this.cargarLiquidaciones();
  },
  methods: {
    async cargarEmpleados() {
      try {
        const data = await api.getEmpleados();
        this.empleados = data;
      } catch (e) { console.error("Error empleados", e); }
    },
    async cargarLiquidaciones() {
      this.cargando = true;
      try {
        const data = await api.getLiquidaciones();
        // Mapeo EXACTO con los nombres que vienen de Python (snake_case a camelCase si quieres, o directo)
        this.liquidaciones = data.map(l => ({
          id: l.id,
          empleado: l.nombre_empleado,
          rut: l.rut,
          email: l.email, // Si viene en el get all (a veces no, check query)
          periodoInicio: l.periodo_inicio,
          periodoFin: l.periodo_fin,
          cantidadServicios: l.total_servicios,
          totalServicios: l.monto_total_servicios,
          porcentajeComision: l.porcentaje_comision, // Ahora sí existe
          totalComision: l.total_comisiones,
          estado: l.estado === 'pendiente' ? 'Pendiente' : 'Pagada',
          fechaPago: l.fecha_pago
        }));
      } catch (error) {
        console.error("Error cargando liquidaciones", error);
        alert("Error de conexión al cargar datos.");
      } finally {
        this.cargando = false;
      }
    },
    async calcularLiquidacion() {
      this.procesando = true;
      try {
        await api.calcularLiquidacion(this.nuevaLiquidacion);
        alert("Liquidación generada con éxito");
        
        // Cerrar modal manualmente
        const modalEl = document.getElementById('modalLiquidacion');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        
        // Limpiar form
        this.nuevaLiquidacion = { id_empleado: '', periodo_inicio: '', periodo_fin: '' };
        await this.cargarLiquidaciones();
        
      } catch (error) {
        const msg = error.response?.data?.detail || "Error desconocido";
        alert("No se pudo generar: " + msg);
      } finally {
        this.procesando = false;
      }
    },
    async verDetalle(liq) {
      this.liquidacionSeleccionada = liq;
      this.detalleServicios = []; 
      try {
        const data = await api.getLiquidacionDetalle(liq.id);
        // Completamos datos que faltaban en la vista de lista (ej: email)
        this.liquidacionSeleccionada = { ...this.liquidacionSeleccionada, ...data, estado: data.estado === 'pendiente' ? 'Pendiente' : 'Pagada' };
        this.detalleServicios = data.servicios || [];
      } catch (error) {
        console.error("Error detalle", error);
        alert("No se pudo cargar el detalle.");
      }
    },
    async marcarPagada(liq) {
      if(!confirm(`¿Confirmas el pago a ${liq.empleado}?`)) return;
      try {
        await api.marcarLiquidacionPagada(liq.id);
        // Actualizamos localmente para no recargar todo si no quieres
        liq.estado = 'Pagada'; 
        await this.cargarLiquidaciones(); // Recarga completa para asegurar
      } catch (error) {
        alert("Error al procesar el pago.");
      }
    },
    // NUEVO MÉTODO DE ELIMINAR
    async eliminarLiquidacion(liq) {
      if (!confirm(`⚠️ ¿Estás seguro de ELIMINAR la liquidación de ${liq.empleado}?\n\nEsta acción borrará el registro y permitirá volver a calcular el período.`)) {
        return;
      }
      try {
        await api.deleteLiquidacion(liq.id);
        alert("Liquidación eliminada correctamente.");
        await this.cargarLiquidaciones();
      } catch (error) {
        const msg = error.response?.data?.detail || "Error al eliminar";
        alert(msg);
      }
    },
    formatDate(dateStr) {
      if(!dateStr) return '-';
      // Ajuste para zona horaria si es necesario, o simple string
      return new Date(dateStr).toLocaleDateString('es-CL'); 
    },
    formatearServicio(texto) {
      if(!texto) return '';
      return texto.replace(/_/g, ' ').toUpperCase();
    }
  }
}
</script>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.card { border-radius: 0.5rem; }
</style>