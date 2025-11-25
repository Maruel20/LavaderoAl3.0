<template>
  <div class="container-fluid py-4 fade-in">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-speedometer2 me-2"></i>
          Dashboard
        </h2>
        <p class="text-muted">Resumen general del lavadero</p>
      </div>
    </div>

     Métricas principales 
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="metric-card blue">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <div class="metric-label">Servicios Hoy</div>
              <div class="metric-value">{{ metrics.serviciosHoy }}</div>
            </div>
            <i class="bi bi-water" style="font-size: 3rem; opacity: 0.3;"></i>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="metric-card green">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <div class="metric-label">Ingresos Hoy</div>
              <div class="metric-value">${{ metrics.ingresosHoy.toLocaleString() }}</div>
            </div>
            <i class="bi bi-cash-stack" style="font-size: 3rem; opacity: 0.3;"></i>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="metric-card orange">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <div class="metric-label">Clientes Activos</div>
              <div class="metric-value">{{ metrics.clientesActivos }}</div>
            </div>
            <i class="bi bi-people" style="font-size: 3rem; opacity: 0.3;"></i>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="metric-card red">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <div class="metric-label">Insumos Bajos</div>
              <div class="metric-value">{{ metrics.insumosBajos }}</div>
            </div>
            <i class="bi bi-exclamation-triangle" style="font-size: 3rem; opacity: 0.3;"></i>
          </div>
        </div>
      </div>
    </div>

     Servicios recientes y alertas 
    <div class="row g-3">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-clock-history me-2"></i>
              Servicios Recientes
            </h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Cliente</th>
                    <th>Vehículo</th>
                    <th>Servicio</th>
                    <th>Empleado</th>
                    <th>Monto</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="servicio in serviciosRecientes" :key="servicio.id">
                    <td>#{{ servicio.id }}</td>
                    <td>{{ servicio.cliente }}</td>
                    <td>{{ servicio.vehiculo }}</td>
                    <td>{{ servicio.tipoServicio }}</td>
                    <td>{{ servicio.empleado }}</td>
                    <td class="fw-bold">${{ servicio.monto.toLocaleString() }}</td>
                    <td>
                      <span :class="'badge bg-' + servicio.estadoColor">
                        {{ servicio.estado }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
         Alertas de inventario 
        <div class="card mb-3">
          <div class="card-header bg-warning text-dark">
            <h5 class="mb-0">
              <i class="bi bi-exclamation-triangle me-2"></i>
              Alertas de Inventario
            </h5>
          </div>
          <div class="card-body">
            <div class="list-group list-group-flush">
              <div 
                v-for="alerta in alertasInventario" 
                :key="alerta.id"
                class="list-group-item px-0"
              >
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ alerta.nombre }}</strong>
                    <br>
                    <small class="text-muted">Stock: {{ alerta.stock }} {{ alerta.unidad }}</small>
                  </div>
                  <span class="badge bg-danger">Bajo</span>
                </div>
              </div>
            </div>
          </div>
        </div>

         Empleados activos 
        <div class="card">
          <div class="card-header bg-info text-white">
            <h5 class="mb-0">
              <i class="bi bi-person-check me-2"></i>
              Empleados Activos
            </h5>
          </div>
          <div class="card-body">
            <div class="list-group list-group-flush">
              <div 
                v-for="empleado in empleadosActivos" 
                :key="empleado.id"
                class="list-group-item px-0"
              >
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <span class="status-icon active"></span>
                    <strong>{{ empleado.nombre }}</strong>
                    <br>
                    <small class="text-muted">{{ empleado.serviciosHoy }} servicios hoy</small>
                  </div>
                  <span class="badge bg-success">${{ empleado.comisionHoy.toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'DashboardView',
  data() {
    return {
      metrics: {
        serviciosHoy: 0,
        ingresosHoy: 0,
        clientesActivos: 0,
        insumosBajos: 0
      },
      serviciosRecientes: [],
      alertasInventario: [],
      empleadosActivos: []
    }
  },
  mounted() {
    this.cargarDatos()
  },
  methods: {
    async cargarDatos() {
      try {
        await Promise.all([
          this.cargarMetricas(),
          this.cargarServiciosRecientes(),
          this.cargarAlertasInventario(),
          this.cargarEmpleadosActivos()
        ])
      } catch (error) {
        console.error('Error al cargar datos del dashboard:', error)
      }
    },
    async cargarMetricas() {
      try {
        const data = await api.getMetricasDashboard()
        this.metrics = {
          serviciosHoy: data.servicios_hoy || 0,
          ingresosHoy: data.ingresos_hoy || 0,
          clientesActivos: data.clientes_activos || 0,
          insumosBajos: data.insumos_bajos || 0
        }
      } catch (error) {
        console.error('Error al cargar métricas:', error)
      }
    },
    async cargarServiciosRecientes() {
      try {
        const data = await api.getServiciosRecientes(10)
        this.serviciosRecientes = data.map(s => ({
          id: s.id,
          cliente: s.patente,
          vehiculo: `${s.tipo_vehiculo} ${s.patente}`,
          tipoServicio: this.formatearTipoServicio(s.tipo_servicio),
          empleado: s.nombre_empleado || 'Sin asignar',
          monto: s.monto_total,
          estado: this.formatearEstado(s.estado),
          estadoColor: this.getEstadoColor(s.estado)
        }))
      } catch (error) {
        console.error('Error al cargar servicios recientes:', error)
      }
    },
    async cargarAlertasInventario() {
      try {
        const data = await api.getAlertasInventarioDashboard()
        this.alertasInventario = data.map(a => ({
          id: a.id,
          nombre: a.nombre,
          stock: a.stock,
          unidad: a.unidad
        }))
      } catch (error) {
        console.error('Error al cargar alertas de inventario:', error)
      }
    },
    async cargarEmpleadosActivos() {
      try {
        const data = await api.getEmpleadosTop(5)
        this.empleadosActivos = data.map(e => ({
          id: e.id,
          nombre: e.nombre,
          serviciosHoy: e.total_servicios || 0,
          comisionHoy: e.total_comisiones || 0
        }))
      } catch (error) {
        console.error('Error al cargar empleados activos:', error)
      }
    },
    formatearTipoServicio(tipo) {
      const tipos = {
        'lavado_simple': 'Lavado Simple',
        'lavado_completo': 'Lavado Completo',
        'encerado': 'Encerado',
        'lavado_motor': 'Lavado Motor',
        'pulido': 'Pulido',
        'descontaminacion': 'Descontaminación'
      }
      return tipos[tipo] || tipo
    },
    formatearEstado(estado) {
      const estados = {
        'completado': 'Completado',
        'pendiente': 'Pendiente',
        'cancelado': 'Cancelado'
      }
      return estados[estado] || estado
    },
    getEstadoColor(estado) {
      const colores = {
        'completado': 'success',
        'pendiente': 'warning',
        'cancelado': 'danger'
      }
      return colores[estado] || 'secondary'
    }
  }
}
</script>

