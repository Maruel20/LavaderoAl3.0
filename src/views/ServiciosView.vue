<template>
  <div class="container-fluid py-4 fade-in">
    <div class="row mb-4 align-items-center">
      <div class="col">
        <h2 class="fw-bold text-primary"><i class="bi bi-droplet-half me-2"></i>Gestión de Servicios</h2>
        <p class="text-muted mb-0">Administración de lavados, convenios y asignación de personal</p>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary shadow-sm" @click="abrirModalCrear">
          <i class="bi bi-plus-lg me-2"></i>Nuevo Servicio
        </button>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light text-secondary">
              <tr>
                <th class="ps-4">Fecha / Hora</th>
                <th>Vehículo</th>
                <th>Tipo Cliente</th>
                <th>Servicio</th>
                <th>Empleado</th>
                <th class="text-end">Monto</th>
                <th class="text-center">Estado</th>
                <th class="text-end pe-4">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in servicios" :key="s.id" :class="{'table-active text-muted opacity-75': s.estado === 'cancelado'}">
                <td class="ps-4">
                  <div class="fw-bold text-dark">{{ s.fecha_fmt }}</div>
                  <small class="text-muted">{{ s.hora_fmt }}</small>
                </td>
                <td>
                  <div class="fw-bold font-monospace">{{ s.patente }}</div>
                  <small class="text-muted text-capitalize">{{ s.tipo_vehiculo }}</small>
                </td>
                <td>
                  <div v-if="s.es_convenio" class="d-flex align-items-center">
                    <span class="badge bg-indigo text-white me-2">Convenio</span>
                    <small class="text-truncate" style="max-width: 150px;" :title="s.nombre_empresa">
                      {{ s.nombre_empresa }}
                    </small>
                  </div>
                  <span v-else class="badge bg-light text-dark border">Particular</span>
                </td>
                <td>{{ formatearServicio(s.tipo_servicio) }}</td>
                <td>
                  <i class="bi bi-person-circle text-muted me-1"></i>
                  {{ s.nombre_empleado || 'Sin asignar' }}
                </td>
                <td class="text-end fw-bold">
                  <span :class="s.estado === 'cancelado' ? 'text-decoration-line-through' : 'text-success'">
                    ${{ s.monto_total?.toLocaleString() }}
                  </span>
                </td>
                <td class="text-center">
                  <span :class="`badge rounded-pill bg-${getColorEstado(s.estado)}`">
                    {{ s.estado }}
                  </span>
                </td>
                <td class="text-end pe-4">
                  <div class="btn-group" v-if="s.estado !== 'cancelado'">
                    <button class="btn btn-sm btn-outline-secondary" @click="abrirModalEditar(s)" title="Editar">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="cancelarServicio(s)" title="Cancelar / Eliminar">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="servicios.length === 0">
                <td colspan="8" class="text-center py-5 text-muted">
                  <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                  No hay servicios registrados recientemente.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalServicio" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header text-white" :class="modoEdicion ? 'bg-warning' : 'bg-primary'">
            <h5 class="modal-title fw-bold">
              <i :class="modoEdicion ? 'bi bi-pencil-square' : 'bi bi-magic'"></i>
              {{ modoEdicion ? 'Editar Servicio' : 'Nuevo Servicio' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          
          <div class="modal-body p-4">
            
            <div v-if="!modoEdicion" class="d-flex justify-content-center mb-4">
              <div class="btn-group shadow-sm" role="group">
                <input type="radio" class="btn-check" name="tipoReg" id="regNormal" value="normal" v-model="tipoRegistro" @change="limpiarFormulario">
                <label class="btn btn-outline-primary px-4" for="regNormal">Particular</label>
                
                <input type="radio" class="btn-check" name="tipoReg" id="regConvenio" value="convenio" v-model="tipoRegistro" @change="limpiarFormulario">
                <label class="btn btn-outline-primary px-4" for="regConvenio">Empresa / Convenio</label>
              </div>
            </div>

            <form @submit.prevent="guardarServicio">
              
              <div v-if="tipoRegistro === 'convenio'" class="card bg-light border-primary mb-4">
                <div class="card-body">
                  <label class="form-label fw-bold text-primary">Paso 1: Validar Patente</label>
                  <div class="input-group mb-2">
                    <input 
                      type="text" 
                      class="form-control text-uppercase fw-bold" 
                      v-model="form.patente" 
                      placeholder="Ej: AB1234" 
                      :disabled="modoEdicion"
                      @keyup.enter="!modoEdicion && validarConvenio()"
                    >
                    <button class="btn btn-primary" type="button" @click="validarConvenio" :disabled="validando || modoEdicion">
                      <span v-if="validando" class="spinner-border spinner-border-sm me-1"></span>
                      Validar
                    </button>
                  </div>
                  
                  <div v-if="convenioDetectado" class="alert alert-success d-flex align-items-center py-2 mb-0">
                    <i class="bi bi-check-circle-fill me-2 fs-5"></i>
                    <div>
                      <strong>{{ convenioDetectado.nombre_empresa }}</strong>
                      <div class="small">
                        Descuento: {{ convenioDetectado.tipo_descuento === 'porcentaje' ? convenioDetectado.valor_descuento + '%' : '$' + convenioDetectado.valor_descuento }}
                        | Vehículo registrado: <span class="text-uppercase">{{ convenioDetectado.tipo_vehiculo || 'N/A' }}</span>
                      </div>
                    </div>
                  </div>
                  <div v-if="errorConvenio" class="text-danger small mt-1">
                    <i class="bi bi-exclamation-circle-fill me-1"></i> {{ errorConvenio }}
                  </div>
                </div>
              </div>

              <div class="row g-3">
                <div class="col-md-4" v-if="tipoRegistro === 'normal'">
                  <label class="form-label fw-bold">Patente</label>
                  <input type="text" class="form-control text-uppercase" v-model="form.patente" required maxlength="8">
                </div>

                <div class="col-md-4">
                  <label class="form-label fw-bold">Tipo Vehículo</label>
                  <select class="form-select" v-model="form.tipo_vehiculo" required @change="calcularPrecio">
                    <option value="auto">Auto</option>
                    <option value="camioneta">Camioneta</option>
                    <option value="suv">SUV</option>
                    <option value="furgon">Furgón</option>
                  </select>
                </div>

                <div class="col-md-4">
                  <label class="form-label fw-bold">Servicio</label>
                  <select class="form-select" v-model="form.tipo_servicio" required @change="calcularPrecio">
                    <option value="">Seleccione...</option>
                    <option v-for="(precio, key) in tarifas[form.tipo_vehiculo]" :key="key" :value="key">
                       {{ formatearServicio(key) }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-bold">Asignar a Empleado</label>
                  <select class="form-select" v-model="form.id_empleado" required>
                    <option value="">Seleccione...</option>
                    <option v-for="emp in empleados" :key="emp.id" :value="emp.id">
                      {{ emp.nombre }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-bold text-success">Total a Cobrar</label>
                  <div class="input-group">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control fw-bold fs-5 text-end text-success" v-model="form.monto_total" required>
                  </div>
                  <div v-if="montoDescuento > 0" class="form-text text-end text-muted small">
                    <span class="text-decoration-line-through">Lista: ${{ precioLista }}</span> 
                    <span class="text-success ms-1">(-${{ montoDescuento }})</span>
                  </div>
                </div>

                <div class="col-12">
                  <label class="form-label">Observaciones (Opcional)</label>
                  <textarea class="form-control" v-model="form.observaciones" rows="2" placeholder="Detalles extra..."></textarea>
                </div>
              </div>
            </form>

          </div>
          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="button" class="btn" :class="modoEdicion ? 'btn-warning' : 'btn-primary'" @click="guardarServicio">
              <i class="bi" :class="modoEdicion ? 'bi-pencil-square' : 'bi-save'"></i>
              {{ modoEdicion ? 'Actualizar Cambios' : 'Registrar Servicio' }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import * as bootstrap from 'bootstrap'
import api from '@/services/api' // Asumo que tienes configurado Axios aquí

export default {
  name: 'ServiciosView',
  data() {
    return {
      servicios: [],
      empleados: [],
      tarifas: {},
      
      // Control UI
      modoEdicion: false,
      tipoRegistro: 'normal',
      validando: false,
      convenioDetectado: null,
      errorConvenio: null,
      modalInstance: null,
      
      // Variables de Cálculo
      precioLista: 0,
      montoDescuento: 0,

      // Formulario
      form: {
        id: null,
        patente: '',
        tipo_vehiculo: 'auto',
        tipo_servicio: '',
        monto_total: 0,
        id_empleado: '',
        id_convenio: null,
        descuento: 0,
        observaciones: ''
      }
    }
  },
  mounted() {
    this.modalInstance = new bootstrap.Modal(document.getElementById('modalServicio'));
    this.cargarDatosIniciales();
  },
  methods: {
    // --- 1. CARGA DE DATOS ---
    async cargarDatosIniciales() {
      try {
        const [resServ, resEmp, resTarif] = await Promise.all([
          api.getServicios(), // Debe llamar a GET /api/servicios
          api.getEmpleados(), // GET /api/empleados
          api.getTarifas()    // GET /api/tarifas
        ]);

        // Procesar Servicios
        this.servicios = (resServ.data || resServ).map(s => ({
          ...s,
          fecha_fmt: new Date(s.fecha).toLocaleDateString(),
          hora_fmt: new Date(s.fecha).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        }));

        this.empleados = resEmp.data || resEmp;

        // Procesar Tarifas para acceso rápido: tarifas[tipo_vehiculo][servicio] = precio
        const listaTarifas = resTarif.data || resTarif;
        this.tarifas = {};
        listaTarifas.forEach(t => {
          if (!this.tarifas[t.tipo_vehiculo]) this.tarifas[t.tipo_vehiculo] = {};
          this.tarifas[t.tipo_vehiculo][t.tipo_servicio] = t.precio;
        });

      } catch (error) {
        console.error("Error cargando datos:", error);
        alert("Error de conexión al cargar datos.");
      }
    },

    // --- 2. LÓGICA CONVENIOS ---
    async validarConvenio() {
      if (!this.form.patente) return;
      
      this.validando = true;
      this.errorConvenio = null;
      this.convenioDetectado = null;
      this.form.id_convenio = null;

      try {
        const res = await api.verificarConvenioPatente(this.form.patente);
        // Espera { tiene_convenio: bool, convenio: object }
        
        if (res.data.tiene_convenio || res.tiene_convenio) {
          const datos = res.data.convenio || res.convenio;
          this.convenioDetectado = datos;
          
          this.form.id_convenio = datos.id_convenio;
          // Si el convenio especifica tipo de vehículo, lo seteamos
          if (datos.tipo_vehiculo) {
            this.form.tipo_vehiculo = datos.tipo_vehiculo;
          }
          this.calcularPrecio();
        } else {
          this.errorConvenio = "Patente no asociada a convenio vigente.";
        }
      } catch (e) {
        this.errorConvenio = "Error al validar la patente.";
      } finally {
        this.validando = false;
      }
    },

    // --- 3. CÁLCULO DE PRECIOS ---
    calcularPrecio() {
      const v = this.form.tipo_vehiculo;
      const s = this.form.tipo_servicio;

      // Obtener precio base
      if (v && s && this.tarifas[v] && this.tarifas[v][s]) {
        this.precioLista = parseFloat(this.tarifas[v][s]);
      } else {
        this.precioLista = 0;
      }

      this.montoDescuento = 0;

      // Aplicar descuento si hay convenio activo
      if (this.tipoRegistro === 'convenio' && this.convenioDetectado && this.precioLista > 0) {
        const c = this.convenioDetectado;
        if (c.tipo_descuento === 'porcentaje') {
          this.montoDescuento = Math.round(this.precioLista * (c.valor_descuento / 100));
        } else {
          this.montoDescuento = parseFloat(c.valor_descuento);
        }
      }

      // Total final
      this.form.monto_total = Math.max(0, this.precioLista - this.montoDescuento);
      this.form.descuento = this.montoDescuento;
    },

    // --- 4. GESTIÓN DEL FORMULARIO ---
    abrirModalCrear() {
      this.modoEdicion = false;
      this.limpiarFormulario();
      this.modalInstance.show();
    },

    abrirModalEditar(servicio) {
      this.modoEdicion = true;
      
      // Determinar si es convenio o particular basado en datos existentes
      this.tipoRegistro = servicio.es_convenio ? 'convenio' : 'normal';
      
      // Copiar datos al formulario
      this.form = {
        id: servicio.id,
        patente: servicio.patente,
        tipo_vehiculo: servicio.tipo_vehiculo,
        tipo_servicio: servicio.tipo_servicio,
        monto_total: servicio.monto_total,
        id_empleado: servicio.id_empleado,
        id_convenio: servicio.id_convenio,
        descuento: servicio.descuento,
        observaciones: servicio.observaciones || ''
      };

      // Si es convenio, simulamos la detección para mostrar el banner visual
      if (servicio.es_convenio) {
        this.convenioDetectado = {
          nombre_empresa: servicio.nombre_empresa || 'Convenio Registrado',
          tipo_descuento: 'histórico', // No importa para visualización
          valor_descuento: 0 // Solo visual
        };
      } else {
        this.convenioDetectado = null;
      }

      this.modalInstance.show();
    },

    limpiarFormulario() {
      this.form = {
        id: null, patente: '', tipo_vehiculo: 'auto', tipo_servicio: '',
        monto_total: 0, id_empleado: '', id_convenio: null, descuento: 0, observaciones: ''
      };
      this.convenioDetectado = null;
      this.errorConvenio = null;
      this.precioLista = 0;
      this.montoDescuento = 0;
    },

    // --- 5. GUARDAR (CREATE / UPDATE) ---
    async guardarServicio() {
      // Validaciones básicas
      if (!this.form.patente || !this.form.tipo_servicio || !this.form.id_empleado) {
        alert("Por favor complete los campos obligatorios.");
        return;
      }
      
      if (this.tipoRegistro === 'convenio' && !this.form.id_convenio && !this.modoEdicion) {
         alert("Debe validar la patente del convenio primero.");
         return;
      }

      const payload = {
        ...this.form,
        patente: this.form.patente.toUpperCase()
      };

      try {
        if (this.modoEdicion) {
          // UPDATE
          await api.updateServicio(this.form.id, payload);
          alert("Servicio actualizado correctamente");
        } else {
          // CREATE
          await api.createServicio(payload);
          alert("Servicio registrado exitosamente");
        }
        
        this.modalInstance.hide();
        this.cargarDatosIniciales(); // Recargar tabla
      } catch (error) {
        console.error(error);
        const msg = error.response?.data?.detail || "Error al guardar";
        alert("Error: " + msg);
      }
    },

    // --- 6. ELIMINAR / CANCELAR ---
    async cancelarServicio(item) {
      if (!confirm(`¿Está seguro de cancelar el servicio de la patente ${item.patente}?`)) return;
      
      try {
        await api.deleteServicio(item.id);
        this.cargarDatosIniciales();
      } catch (error) {
        alert("No se pudo cancelar el servicio.");
      }
    },

    // --- UTILIDADES ---
    formatearServicio(slug) {
      if (!slug) return '';
      return slug.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    getColorEstado(estado) {
      const map = {
        'completado': 'success',
        'pendiente': 'warning',
        'cancelado': 'secondary'
      };
      return map[estado] || 'primary';
    }
  }
}
</script>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.bg-indigo { background-color: #6610f2; }
.opacity-75 { opacity: 0.75; }
</style>