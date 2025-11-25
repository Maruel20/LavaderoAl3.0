<template>
  <div class="container-fluid py-4 fade-in">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-briefcase me-2"></i>
          Convenios Corporativos
        </h2>
        <p class="text-muted">Gestiona empresas, descuentos y flotas autorizadas</p>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary" @click="abrirModalCrear">
          <i class="bi bi-plus-circle me-2"></i>
          Nuevo Convenio
        </button>
      </div>
    </div>

    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
              <input type="text" class="form-control border-start-0" placeholder="Buscar por empresa o NIT..." v-model="busqueda">
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

    <div class="card shadow-sm">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-3">Empresa / Cliente</th>
                <th>Contacto</th>
                <th>Descuento</th>
                <th>Vigencia</th>
                <th class="text-center">Flota</th>
                <th>Estado</th>
                <th class="text-end pe-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in conveniosFiltrados" :key="c.id">
                <td class="ps-3">
                  <div class="fw-bold">{{ c.nombre_empresa }}</div>
                  <small class="text-muted">NIT: {{ c.rut_empresa }}</small>
                </td>
                <td>
                  <div>{{ c.contacto }}</div>
                  <small class="text-muted"><i class="bi bi-telephone me-1"></i>{{ c.telefono }}</small>
                </td>
                <td>
                  <span class="badge" :class="c.tipo_descuento === 'porcentaje' ? 'bg-primary' : 'bg-info'">
                    {{ c.tipo_descuento === 'porcentaje' ? '%' : '$' }}
                  </span>
                  <span class="fw-bold ms-1">
                     {{ c.tipo_descuento === 'porcentaje' ? c.valor_descuento + '%' : '$' + c.valor_descuento.toLocaleString() }}
                  </span>
                </td>
                <td>
                  <small>{{ formatDate(c.fecha_inicio) }}</small> <br>
                  <small class="text-muted">hasta {{ formatDate(c.fecha_termino) }}</small>
                </td>
                <td class="text-center">
                  <button class="btn btn-sm btn-outline-secondary position-relative" @click="verVehiculos(c)">
                    <i class="bi bi-car-front-fill"></i>
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" v-if="c.total_vehiculos > 0">
                      {{ c.total_vehiculos }}
                    </span>
                  </button>
                </td>
                <td>
                  <span :class="'badge rounded-pill bg-' + (c.estado === 'activo' ? 'success' : 'secondary')">
                    {{ c.estado }}
                  </span>
                </td>
                <td class="text-end pe-3">
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" title="Editar" @click="editarConvenio(c)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button v-if="c.estado === 'activo'" class="btn btn-outline-danger" title="Desactivar" @click="eliminarConvenio(c)">
                      <i class="bi bi-slash-circle"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalConvenio" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">{{ form.id ? 'Editar Convenio' : 'Nuevo Convenio Corporativo' }}</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="guardarConvenio">
              <h6 class="text-primary border-bottom pb-2 mb-3">Información de la Empresa</h6>
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label fw-bold">Razón Social *</label>
                  <input type="text" class="form-control" v-model="form.nombre_empresa" required placeholder="Ej: Transportes SAS">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">NIT / RUT *</label>
                  <input type="text" class="form-control" v-model="form.rut_empresa" required placeholder="Ej: 900.123.456-7">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Persona de Contacto</label>
                  <input type="text" class="form-control" v-model="form.contacto">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Teléfono *</label>
                  <input type="text" class="form-control" v-model="form.telefono" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Email Corporativo</label>
                  <input type="email" class="form-control" v-model="form.email">
                </div>
              </div>

              <h6 class="text-primary border-bottom pb-2 mb-3">Condiciones del Convenio</h6>
              <div class="row g-3 mb-4">
                <div class="col-md-3">
                  <label class="form-label fw-bold">Tipo Descuento</label>
                  <select class="form-select" v-model="form.tipo_descuento">
                    <option value="porcentaje">Porcentaje (%)</option>
                    <option value="monto_fijo">Monto Fijo ($)</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label fw-bold">Valor</label>
                  <input type="number" class="form-control" v-model="form.valor_descuento" required min="0">
                </div>
                <div class="col-md-3">
                  <label class="form-label">Inicio</label>
                  <input type="date" class="form-control" v-model="form.fecha_inicio" required>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Término</label>
                  <input type="date" class="form-control" v-model="form.fecha_termino">
                </div>
              </div>

              <div v-if="!form.id">
                <h6 class="text-primary border-bottom pb-2 mb-3 d-flex justify-content-between align-items-center">
                  Vehículos Iniciales (Opcional)
                  <button type="button" class="btn btn-sm btn-outline-success" @click="agregarFilaVehiculo">
                    <i class="bi bi-plus"></i> Agregar Fila
                  </button>
                </h6>
                <div class="table-responsive bg-light p-2 rounded">
                  <table class="table table-sm table-borderless mb-0">
                    <thead>
                      <tr class="text-muted small">
                        <th>Patente *</th>
                        <th>Tipo *</th>
                        <th>Modelo</th>
                        <th>Color</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(v, index) in vehiculosTemp" :key="index">
                        <td><input type="text" class="form-control form-control-sm text-uppercase" v-model="v.patente" placeholder="ABC-123"></td>
                        <td>
                          <select class="form-select form-select-sm" v-model="v.tipo_vehiculo">
                            <option value="auto">Auto</option>
                            <option value="camioneta">Camioneta</option>
                            <option value="suv">SUV</option>
                            <option value="furgon">Furgón</option>
                          </select>
                        </td>
                        <td><input type="text" class="form-control form-control-sm" v-model="v.modelo" placeholder="Ej: Hilux"></td>
                        <td><input type="text" class="form-control form-control-sm" v-model="v.color" placeholder="Blanco"></td>
                        <td><button type="button" class="btn btn-sm text-danger" @click="vehiculosTemp.splice(index, 1)"><i class="bi bi-x-lg"></i></button></td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="text-muted small mt-2" v-if="vehiculosTemp.length === 0">No se añadirán vehículos por ahora. Podrás hacerlo después.</div>
                </div>
              </div>
              
              <div class="mt-4 text-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Cancelar</button>
                <button type="submit" class="btn btn-primary">Guardar Convenio</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalVehiculos" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Flota de {{ convenioSeleccionado?.nombre_empresa }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="card bg-light border-0 mb-3" v-if="convenioSeleccionado?.estado === 'activo'">
              <div class="card-body">
                <h6 class="card-title small fw-bold text-muted mb-2">AGREGAR VEHÍCULO NUEVO</h6>
                <div class="row g-2 align-items-end">
                  <div class="col-md-3">
                    <label class="small">Patente</label>
                    <input type="text" class="form-control form-control-sm text-uppercase" v-model="nuevoVehiculo.patente" placeholder="AAA-123">
                  </div>
                  <div class="col-md-3">
                     <label class="small">Tipo</label>
                     <select class="form-select form-select-sm" v-model="nuevoVehiculo.tipo_vehiculo">
                        <option value="auto">Auto</option>
                        <option value="camioneta">Camioneta</option>
                        <option value="suv">SUV</option>
                        <option value="furgon">Furgón</option>
                     </select>
                  </div>
                  <div class="col-md-3">
                    <label class="small">Modelo</label>
                    <input type="text" class="form-control form-control-sm" v-model="nuevoVehiculo.modelo">
                  </div>
                  <div class="col-md-3">
                    <button class="btn btn-sm btn-success w-100" @click="agregarVehiculoIndividual">
                      <i class="bi bi-plus-lg"></i> Agregar
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="table-responsive">
              <table class="table table-hover table-sm">
                <thead>
                  <tr>
                    <th>Patente</th>
                    <th>Tipo</th>
                    <th>Modelo</th>
                    <th>Color</th>
                    <th class="text-end">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="v in vehiculosLista" :key="v.id">
                    <td class="fw-bold">{{ v.patente }}</td>
                    <td>{{ v.tipo_vehiculo.toUpperCase() }}</td>
                    <td>{{ v.modelo || '-' }}</td>
                    <td>{{ v.color || '-' }}</td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-danger border-0" @click="eliminarVehiculo(v.id)">
                        <i class="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="vehiculosLista.length === 0">
                    <td colspan="5" class="text-center text-muted py-3">No hay vehículos registrados en este convenio.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import * as bootstrap from 'bootstrap'
import api from '@/services/api'

export default {
  name: 'ConveniosView',
  data() {
    return {
      busqueda: '',
      filtroEstado: 'activo',
      convenios: [],
      
      // Formulario Principal
      form: {
        id: null,
        nombre_empresa: '',
        rut_empresa: '',
        contacto: '',
        telefono: '',
        email: '',
        tipo_descuento: 'porcentaje',
        valor_descuento: 0,
        fecha_inicio: '',
        fecha_termino: '',
        observaciones: ''
      },
      
      // Vehículos Temporales (Solo para creación masiva)
      vehiculosTemp: [],
      
      // Gestión Modal Vehículos
      convenioSeleccionado: null,
      vehiculosLista: [],
      nuevoVehiculo: { patente: '', tipo_vehiculo: 'auto', modelo: '', color: '' }
    }
  },
  mounted() {
    this.cargarConvenios();
  },
  computed: {
    conveniosFiltrados() {
      return this.convenios.filter(c => {
        const term = this.busqueda.toLowerCase();
        const matchText = c.nombre_empresa.toLowerCase().includes(term) || c.rut_empresa.includes(term);
        const matchEst = this.filtroEstado ? c.estado === this.filtroEstado : true;
        return matchText && matchEst;
      });
    }
  },
  methods: {
    async cargarConvenios() {
      try {
        const data = await api.getConvenios();
        // data ya es array (verificado en python)
        this.convenios = data;
      } catch (e) { console.error(e); }
    },

    // --- CRUD CONVENIO ---
    abrirModalCrear() {
      this.limpiarForm();
      this.vehiculosTemp = [];
      new bootstrap.Modal(document.getElementById('modalConvenio')).show();
    },
    
    editarConvenio(c) {
      // Clonar datos para no editar la tabla reactivamente antes de guardar
      this.form = { ...c };
      // Ajuste de fechas para input date (YYYY-MM-DD)
      if(this.form.fecha_inicio) this.form.fecha_inicio = this.form.fecha_inicio.split('T')[0];
      if(this.form.fecha_termino) this.form.fecha_termino = this.form.fecha_termino.split('T')[0];
      
      new bootstrap.Modal(document.getElementById('modalConvenio')).show();
    },

    async guardarConvenio() {
      try {
        const payload = { ...this.form };
        
        let idConvenio;
        if (payload.id) {
          await api.updateConvenio(payload.id, payload);
          idConvenio = payload.id;
          alert("Convenio actualizado");
        } else {
          const res = await api.createConvenio(payload);
          idConvenio = res.id;
          
          // Guardar vehículos iniciales si existen
          if (this.vehiculosTemp.length > 0) {
            for (const v of this.vehiculosTemp) {
              if (v.patente) await api.addVehiculoConvenio(idConvenio, v);
            }
          }
          alert("Convenio creado exitosamente");
        }

        bootstrap.Modal.getInstance(document.getElementById('modalConvenio')).hide();
        this.cargarConvenios();
        
      } catch (error) {
        alert("Error: " + (error.response?.data?.detail || error.message));
      }
    },

    async eliminarConvenio(c) {
      if(!confirm(`¿Desactivar convenio con ${c.nombre_empresa}?`)) return;
      try {
        await api.deleteConvenio(c.id);
        this.cargarConvenios();
      } catch(e) { alert("Error al eliminar"); }
    },

    // --- GESTIÓN VEHÍCULOS ---
    agregarFilaVehiculo() {
      this.vehiculosTemp.push({ patente: '', tipo_vehiculo: 'auto', modelo: '', color: '' });
    },

    async verVehiculos(c) {
      this.convenioSeleccionado = c;
      this.nuevoVehiculo = { patente: '', tipo_vehiculo: 'auto', modelo: '', color: '' };
      try {
        this.vehiculosLista = await api.getVehiculosConvenio(c.id);
        new bootstrap.Modal(document.getElementById('modalVehiculos')).show();
      } catch(e) { console.error(e); }
    },

    async agregarVehiculoIndividual() {
      if(!this.nuevoVehiculo.patente) return alert("Falta patente");
      try {
        await api.addVehiculoConvenio(this.convenioSeleccionado.id, this.nuevoVehiculo);
        this.nuevoVehiculo = { patente: '', tipo_vehiculo: 'auto', modelo: '', color: '' };
        // Recargar lista
        this.vehiculosLista = await api.getVehiculosConvenio(this.convenioSeleccionado.id);
        this.cargarConvenios(); // Para actualizar contador en tabla principal
      } catch (error) {
        alert("Error: " + (error.response?.data?.detail || "No se pudo agregar"));
      }
    },

    async eliminarVehiculo(idVehiculo) {
      if(!confirm("¿Quitar vehículo del convenio?")) return;
      try {
        await api.removeVehiculoConvenio(idVehiculo);
        this.vehiculosLista = this.vehiculosLista.filter(v => v.id !== idVehiculo);
        this.cargarConvenios();
      } catch(e) { alert("Error al quitar vehículo"); }
    },

    // --- UTILIDADES ---
    limpiarForm() {
      this.form = {
        id: null, nombre_empresa: '', rut_empresa: '', contacto: '', telefono: '', 
        email: '', tipo_descuento: 'porcentaje', valor_descuento: 0, 
        fecha_inicio: new Date().toISOString().split('T')[0], fecha_termino: '', observaciones: ''
      };
    },
    formatDate(dateStr) {
      if(!dateStr) return '-';
      return new Date(dateStr).toLocaleDateString('es-CO');
    }
  }
}
</script>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>