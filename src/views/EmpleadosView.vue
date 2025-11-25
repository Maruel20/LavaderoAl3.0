<template>
  <div class="container-fluid py-4 fade-in">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-person-badge me-2"></i>
          Gestión de Empleados
        </h2>
        <p class="text-muted">Administra el personal del lavadero</p>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary" @click="abrirModalCrear">
          <i class="bi bi-plus-circle me-2"></i>
          Nuevo Empleado
        </button>
      </div>
    </div>

    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-search"></i></span>
              <input 
                type="text" 
                class="form-control" 
                placeholder="Buscar por nombre o Cédula..."
                v-model="busqueda"
              >
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filtroEstado">
              <option value="">Todos los estados</option>
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card border-start border-4 border-primary h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 text-uppercase small">Total Personal</h6>
            <h3 class="mb-0">{{ empleados.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-start border-4 border-success h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 text-uppercase small">Activos</h6>
            <h3 class="mb-0 text-success">{{ empleadosActivos }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-start border-4 border-warning h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 text-uppercase small">Comisión Promedio</h6>
            <h3 class="mb-0 text-warning">40% - 50%</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-3">Nombre</th>
                <th>Cédula (C.C.)</th>
                <th>Contacto</th>
                <th>% Comisión</th>
                <th>Estado</th>
                <th class="text-end pe-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="empleados.length === 0">
                <td colspan="6" class="text-center py-5 text-muted">
                  <i class="bi bi-people fs-1 d-block mb-2"></i>
                  No hay empleados registrados.
                </td>
              </tr>
              <tr v-for="empleado in empleadosFiltrados" :key="empleado.id">
                <td class="ps-3">
                  <div class="fw-bold">{{ empleado.nombre }}</div>
                  <small class="text-muted" style="font-size: 0.75rem;">ID Interno: {{ empleado.id }}</small>
                </td>
                <td>{{ empleado.rut }}</td> <td>
                  <div v-if="empleado.telefono"><i class="bi bi-whatsapp text-success me-1"></i> {{ empleado.telefono }}</div>
                  <div v-if="empleado.email" class="small text-muted">{{ empleado.email }}</div>
                </td>
                <td>
                  <span :class="'badge bg-' + (empleado.porcentajeComision >= 50 ? 'success' : 'primary')">
                    {{ empleado.porcentajeComision }}%
                  </span>
                </td>
                <td>
                  <span :class="'badge rounded-pill bg-' + (empleado.estado === 'activo' ? 'success' : 'secondary')">
                    {{ empleado.estado === 'activo' ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td class="text-end pe-3">
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" title="Editar" @click="editarEmpleado(empleado)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button 
                      v-if="empleado.estado === 'activo'"
                      class="btn btn-outline-danger" 
                      title="Desactivar" 
                      @click="eliminarEmpleado(empleado)"
                    >
                      <i class="bi bi-person-x"></i>
                    </button>
                    <button 
                      v-else
                      class="btn btn-outline-success" 
                      title="Reactivar" 
                      @click="reactivarEmpleado(empleado)" >
                      <i class="bi bi-person-check"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalEmpleado" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">
              <i class="bi" :class="form.id ? 'bi-pencil-square' : 'bi-person-plus'"></i>
              {{ form.id ? 'Editar Empleado' : 'Nuevo Empleado' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" id="btnCerrarModalEmp"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="guardarEmpleado">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold">Nombre Completo *</label>
                  <input type="text" class="form-control" v-model="form.nombre" required placeholder="Ej: Juan Pérez">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Cédula (C.C.) *</label>
                  <input type="number" class="form-control" v-model="form.rut" placeholder="Ej: 1045678900" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Celular / WhatsApp *</label>
                  <input type="tel" class="form-control" v-model="form.telefono" placeholder="Ej: 300 123 4567" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Correo Electrónico</label>
                  <input type="email" class="form-control" v-model="form.email" placeholder="juan@ejemplo.com">
                </div>
                <div class="col-md-12">
                  <label class="form-label fw-bold">Porcentaje de Comisión *</label>
                  <div class="row g-2">
                    <div class="col-md-6">
                       <select class="form-select" v-model="form.porcentaje_comision" required>
                        <option value="40">40% (Estándar)</option>
                        <option value="50">50% (Convenios / Senior)</option>
                        <option value="0">Sin comisión (Sueldo fijo)</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div class="col-12 mt-4">
                   <div class="alert alert-light border d-flex align-items-center mb-0">
                    <i class="bi bi-info-circle fs-4 text-primary me-3"></i>
                    <div>
                      <strong>Nota sobre pagos:</strong> Las comisiones se calcularán automáticamente al cerrar el servicio basado en este porcentaje.
                    </div>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="button" class="btn btn-primary" @click="guardarEmpleado">
              <i class="bi bi-save me-2"></i>
              {{ form.id ? 'Actualizar Datos' : 'Guardar Empleado' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as bootstrap from 'bootstrap'
import api from '@/services/api';

export default {
  name: 'EmpleadosView',
  data() {
    return {
      busqueda: '',
      filtroEstado: 'activo', // Por defecto ver solo activos
      empleados: [],
      form: {
        id: null,
        nombre: '',
        rut: '', // En backend es rut, visualmente es Cédula
        telefono: '',
        email: '',
        porcentaje_comision: 40
      }
    }
  },
  mounted() {
    this.cargarEmpleados();
  },
  computed: {
    empleadosFiltrados() {
      return this.empleados.filter(emp => {
        const term = this.busqueda.toLowerCase();
        const coincideBusqueda = emp.nombre.toLowerCase().includes(term) || 
                                 emp.rut.toString().includes(term); // rut es string o number
        
        const coincideEstado = this.filtroEstado ? emp.estado === this.filtroEstado : true;
        
        return coincideBusqueda && coincideEstado;
      });
    },
    empleadosActivos() {
      return this.empleados.filter(e => e.estado === 'activo').length;
    }
  },
  methods: {
    async cargarEmpleados() {
      try {
        const response = await api.getEmpleados();
        // Normalizar respuesta
        const data = Array.isArray(response) ? response : (response.data || []);
        
        this.empleados = data.map(e => ({
          ...e,
          // Mapeo seguro de nombres de columna
          porcentajeComision: e.porcentaje_comision,
          rut: e.rut // La base de datos guarda la cédula aquí
        }));
      } catch (error) {
        console.error("Error:", error);
      }
    },

    abrirModalCrear() {
      this.limpiarFormulario();
      const modal = new bootstrap.Modal(document.getElementById('modalEmpleado'));
      modal.show();
    },

    editarEmpleado(emp) {
      // Clonamos el objeto para no modificar la tabla en tiempo real
      this.form = {
        id: emp.id,
        nombre: emp.nombre,
        rut: emp.rut,
        telefono: emp.telefono,
        email: emp.email || '',
        porcentaje_comision: emp.porcentajeComision
      };
      const modal = new bootstrap.Modal(document.getElementById('modalEmpleado'));
      modal.show();
    },

    async guardarEmpleado() {
      if (!this.form.nombre || !this.form.rut || !this.form.telefono) {
        alert("Completa los campos obligatorios (*)");
        return;
      }

      try {
        const payload = {
          nombre: this.form.nombre,
          rut: this.form.rut.toString(), // Aseguramos string para BD
          telefono: this.form.telefono,
          email: this.form.email,
          porcentaje_comision: parseInt(this.form.porcentaje_comision)
        };

        if (this.form.id) {
            // EDITAR (PUT)
             // Necesitas agregar updateEmpleado en api.js
             // await api.updateEmpleado(this.form.id, payload);
             
             // Si no tienes updateEmpleado en api.js, usa axios directo temporalmente o agrégalo:
             await api.updateEmpleado(this.form.id, payload); // Asumiendo que ya lo agregaste
             alert("Empleado actualizado correctamente");
        } else {
            // CREAR (POST)
            await api.createEmpleado(payload);
            alert("Empleado registrado correctamente");
        }
        
        // Cerrar modal
        const modalEl = document.getElementById('modalEmpleado');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        this.cargarEmpleados();
        this.limpiarFormulario();
        
      } catch (error) {
        console.error("Error guardar:", error);
        alert("Error: " + (error.response?.data?.detail || "Verifica la Cédula o conexión"));
      }
    },

    async eliminarEmpleado(emp) {
      if (!confirm(`¿Estás seguro de desactivar a ${emp.nombre}?\nYa no aparecerá en nuevos servicios.`)) {
        return;
      }
      try {
        // Asumiendo que agregaste deleteEmpleado en api.js
        await api.deleteEmpleado(emp.id); 
        alert("Empleado desactivado.");
        this.cargarEmpleados();
      } catch (error) {
        alert("Error al desactivar empleado");
      }
    },

    async reactivarEmpleado(emp) {
       // Opcional: Reutiliza el endpoint de update para cambiar estado o crea uno específico
       alert("Funcionalidad de reactivación pendiente de backend");
    },

    limpiarFormulario() {
      this.form = {
        id: null,
        nombre: '',
        rut: '',
        telefono: '',
        email: '',
        porcentaje_comision: 40
      };
    }
  }
}
</script>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>