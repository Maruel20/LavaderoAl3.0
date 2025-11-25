<template>
  <div class="container-fluid py-4 fade-in">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-graph-up me-2"></i> Reportes y Estadísticas
        </h2>
        <p class="text-muted">Analiza el rendimiento del lavadero en tiempo real</p>
      </div>
      <div class="col-auto">
        <button class="btn btn-success" @click="exportarExcel" :disabled="cargando">
          <i class="bi bi-file-earmark-excel me-2"></i>
          Exportar Reporte
        </button>
      </div>
    </div>
 
    <div class="card mb-4">
      <div class="card-body">
        <form @submit.prevent="cargarDatos" class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label">Tipo de Reporte</label>
            <select class="form-select" v-model="filtros.tipoReporte" @change="cargarDatos">
              <option value="general">General</option>
              <option value="empleados">Rendimiento Empleados</option>
              <option value="convenios">Convenios</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Fecha Inicio</label>
            <input type="date" class="form-control" v-model="filtros.fechaInicio">
          </div>
          <div class="col-md-3">
            <label class="form-label">Fecha Fin</label>
            <input type="date" class="form-control" v-model="filtros.fechaFin">
          </div>
          <div class="col-md-3">
            <button type="submit" class="btn btn-primary w-100" :disabled="cargando">
              <span v-if="cargando" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-search me-2"></i>
              {{ cargando ? 'Cargando...' : 'Generar Reporte' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-if="filtros.tipoReporte === 'general' && !cargando">
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <div class="card border-primary h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="text-muted mb-1">Ingresos Totales</h6>
                  <h3 class="mb-0 text-primary">${{ formatearDinero(metricas.ingresosTotales) }}</h3>
                </div>
                <i class="bi bi-cash-stack text-primary" style="font-size: 2.5rem; opacity: 0.3;"></i>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-success h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="text-muted mb-1">Total Servicios</h6>
                  <h3 class="mb-0 text-success">{{ metricas.totalServicios }}</h3>
                </div>
                <i class="bi bi-water text-success" style="font-size: 2.5rem; opacity: 0.3;"></i>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-warning h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="text-muted mb-1">Ticket Promedio</h6>
                  <h3 class="mb-0 text-warning">${{ formatearDinero(metricas.ticketPromedio) }}</h3>
                </div>
                <i class="bi bi-receipt text-warning" style="font-size: 2.5rem; opacity: 0.3;"></i>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-info h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="text-muted mb-1">Comisiones Pagadas</h6>
                  <h3 class="mb-0 text-info">${{ formatearDinero(metricas.totalComisiones) }}</h3>
                </div>
                <i class="bi bi-people text-info" style="font-size: 2.5rem; opacity: 0.3;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-pie-chart me-2"></i>Servicios por Tipo</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table align-middle">
                  <thead>
                    <tr>
                      <th>Tipo de Servicio</th>
                      <th>Cantidad</th>
                      <th>Ingresos</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="servicio in serviciosPorTipo" :key="servicio.tipo_servicio">
                      <td class="text-capitalize">{{ servicio.tipo_servicio.replace('_', ' ') }}</td>
                      <td><span class="badge bg-primary rounded-pill">{{ servicio.cantidad }}</span></td>
                      <td class="fw-bold">${{ formatearDinero(servicio.ingresos) }}</td>
                    </tr>
                    <tr v-if="serviciosPorTipo.length === 0">
                      <td colspan="3" class="text-center text-muted py-3">No hay datos en este periodo</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-car-front me-2"></i>Ingresos por Vehículo</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table align-middle">
                  <thead>
                    <tr>
                      <th>Vehículo</th>
                      <th>Cantidad</th>
                      <th>Ingresos</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="vehiculo in serviciosPorVehiculo" :key="vehiculo.tipo_vehiculo">
                      <td class="text-capitalize">{{ vehiculo.tipo_vehiculo }}</td>
                      <td><span class="badge bg-info rounded-pill">{{ vehiculo.cantidad }}</span></td>
                      <td class="fw-bold">${{ formatearDinero(vehiculo.ingresos) }}</td>
                    </tr>
                     <tr v-if="serviciosPorVehiculo.length === 0">
                      <td colspan="3" class="text-center text-muted py-3">No hay datos en este periodo</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row mt-4">
        <div class="col-12">
           <div class="card">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-calendar-date me-2"></i>Evolución Diaria (Últimos 30 días)</h5>
            </div>
            <div class="card-body">
               <div class="table-responsive">
                <table class="table table-hover table-sm">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Servicios</th>
                      <th>Ingresos</th>
                      <th>Comisiones</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="dia in ingresosDiarios" :key="dia.fecha">
                      <td>{{ new Date(dia.fecha).toLocaleDateString() }}</td>
                      <td>{{ dia.total_servicios }}</td>
                      <td class="text-success">${{ formatearDinero(dia.ingresos) }}</td>
                      <td class="text-danger">${{ formatearDinero(dia.comisiones) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
           </div>
        </div>
      </div>
    </div>

    <div v-if="filtros.tipoReporte === 'empleados' && !cargando">
      <div class="card">
        <div class="card-header">
           <h5 class="mb-0"><i class="bi bi-person-badge me-2"></i>Rendimiento por Empleado</h5>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>RUT</th>
                  <th>% Comisión</th>
                  <th>Servicios Realizados</th>
                  <th>Total Vendido</th>
                  <th>Comisiones Ganadas</th>
                  <th>Ticket Promedio</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="emp in reporteEmpleados" :key="emp.id">
                  <td>{{ emp.nombre }}</td>
                  <td>{{ emp.rut }}</td>
                  <td>{{ emp.porcentaje_comision }}%</td>
                  <td><span class="badge bg-secondary">{{ emp.total_servicios }}</span></td>
                  <td class="fw-bold text-success">${{ formatearDinero(emp.total_vendido) }}</td>
                  <td class="fw-bold text-primary">${{ formatearDinero(emp.total_comisiones) }}</td>
                  <td>${{ formatearDinero(emp.ticket_promedio) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="filtros.tipoReporte === 'convenios' && !cargando">
      <div class="card">
        <div class="card-header">
           <h5 class="mb-0"><i class="bi bi-briefcase me-2"></i>Reporte de Convenios</h5>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Empresa</th>
                  <th>RUT</th>
                  <th>Total Servicios</th>
                  <th>Total Facturado</th>
                  <th>Descuentos Aplicados</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="conv in reporteConvenios" :key="conv.id">
                  <td>{{ conv.nombre_empresa }}</td>
                  <td>{{ conv.rut_empresa }}</td>
                  <td><span class="badge bg-secondary">{{ conv.total_servicios }}</span></td>
                  <td class="fw-bold text-success">${{ formatearDinero(conv.total_facturado) }}</td>
                  <td class="fw-bold text-danger">${{ formatearDinero(conv.total_descuentos) }}</td>
                </tr>
                 <tr v-if="reporteConvenios.length === 0">
                    <td colspan="5" class="text-center text-muted">No se encontraron movimientos de convenios.</td>
                 </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import api from '../services/api';
import * as XLSX from 'xlsx'; 

export default {
  name: 'ReportesView',
  data() {
    return {
      cargando: false,
      error: null,
      filtros: {
        tipoReporte: 'general',
        fechaInicio: '',
        fechaFin: ''
      },
      metricas: {
        ingresosTotales: 0,
        totalServicios: 0,
        ticketPromedio: 0,
        totalComisiones: 0
      },
      serviciosPorTipo: [],
      serviciosPorVehiculo: [],
      ingresosDiarios: [],
      reporteEmpleados: [],
      reporteConvenios: []
    }
  },
  mounted() {
    this.establecerFechasPorDefecto();
    this.cargarDatos();
  },
  methods: {
    establecerFechasPorDefecto() {
      const now = new Date();
      const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
      const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
      this.filtros.fechaInicio = firstDay.toISOString().split('T')[0];
      this.filtros.fechaFin = lastDay.toISOString().split('T')[0];
    },

    async cargarDatos() {
      this.cargando = true;
      this.error = null;
      try {
        const { fechaInicio, fechaFin } = this.filtros;

        if (this.filtros.tipoReporte === 'general') {
          const generalData = await api.getReporteGeneral(fechaInicio, fechaFin);
          if (generalData.totales) {
              this.metricas.ingresosTotales = generalData.totales.ingresos_totales || 0;
              this.metricas.totalServicios = generalData.totales.total_servicios || 0;
              this.metricas.ticketPromedio = generalData.totales.ticket_promedio || 0;
              this.metricas.totalComisiones = generalData.totales.total_comisiones || 0;
          }
          this.serviciosPorTipo = generalData.por_tipo_servicio || [];
          this.serviciosPorVehiculo = generalData.por_tipo_vehiculo || [];
          
          const diariosData = await api.getReporteServiciosDiarios(30); 
          this.ingresosDiarios = diariosData || [];

        } else if (this.filtros.tipoReporte === 'empleados') {
          const empleadosData = await api.getReporteEmpleados(fechaInicio, fechaFin);
          this.reporteEmpleados = empleadosData || [];

        } else if (this.filtros.tipoReporte === 'convenios') {
          const conveniosData = await api.getReporteConvenios(fechaInicio, fechaFin);
          this.reporteConvenios = conveniosData || [];
        }

      } catch (err) {
        console.error("Error cargando reportes:", err);
        this.error = "Hubo un error al cargar los datos.";
      } finally {
        this.cargando = false;
      }
    },

    formatearDinero(valor) {
      if (!valor) return '0';
      return Number(valor).toLocaleString('es-CL');
    },

    exportarExcel() {
      if (this.cargando) return;

      const workbook = XLSX.utils.book_new();
      let nombreArchivo = `Reporte_${this.filtros.tipoReporte}_${this.filtros.fechaInicio}.xlsx`;

      if (this.filtros.tipoReporte === 'general') {
        // Hoja 1: Resumen
        const resumenData = [
          ["Métrica", "Valor"],
          ["Fecha Inicio", this.filtros.fechaInicio],
          ["Fecha Fin", this.filtros.fechaFin],
          ["Ingresos Totales", this.metricas.ingresosTotales],
          ["Total Servicios", this.metricas.totalServicios],
          ["Ticket Promedio", this.metricas.ticketPromedio],
          ["Total Comisiones", this.metricas.totalComisiones]
        ];
        const wsResumen = XLSX.utils.aoa_to_sheet(resumenData);
        XLSX.utils.book_append_sheet(workbook, wsResumen, "Resumen General");

        // Hoja 2: Por Servicio
        if (this.serviciosPorTipo.length > 0) {
          const wsTipo = XLSX.utils.json_to_sheet(this.serviciosPorTipo.map(item => ({
             "Servicio": item.tipo_servicio,
             "Cantidad": item.cantidad,
             "Ingresos": item.ingresos
          })));
          XLSX.utils.book_append_sheet(workbook, wsTipo, "Por Servicio");
        }

        // Hoja 3: Diario
        if (this.ingresosDiarios.length > 0) {
          const wsDiario = XLSX.utils.json_to_sheet(this.ingresosDiarios.map(item => ({
            "Fecha": item.fecha,
            "Servicios": item.total_servicios,
            "Ingresos": item.ingresos,
            "Comisiones": item.comisiones
          })));
          XLSX.utils.book_append_sheet(workbook, wsDiario, "Diario");
        }

      } else if (this.filtros.tipoReporte === 'empleados') {
        const wsEmpleados = XLSX.utils.json_to_sheet(this.reporteEmpleados.map(emp => ({
            "Nombre": emp.nombre,
            "RUT": emp.rut,
            "Comisión %": emp.porcentaje_comision,
            "Servicios Realizados": emp.total_servicios,
            "Ventas Totales": emp.total_vendido,
            "Comisiones Ganadas": emp.total_comisiones,
            "Promedio por Auto": emp.ticket_promedio
        })));
        XLSX.utils.book_append_sheet(workbook, wsEmpleados, "Rendimiento Empleados");

      } else if (this.filtros.tipoReporte === 'convenios') {
        const wsConvenios = XLSX.utils.json_to_sheet(this.reporteConvenios.map(conv => ({
            "Empresa": conv.nombre_empresa,
            "RUT": conv.rut_empresa,
            "Servicios": conv.total_servicios,
            "Facturado": conv.total_facturado,
            "Descuentos Otorgados": conv.total_descuentos
        })));
        XLSX.utils.book_append_sheet(workbook, wsConvenios, "Convenios");
      }

      XLSX.writeFile(workbook, nombreArchivo);
    }
  }
}
</script>

<style scoped>
.fade-in {
  animation: fadeIn 0.5s;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: none;
  margin-bottom: 1rem;
}
</style>