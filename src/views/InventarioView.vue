<template>
  <div class="container-fluid py-4 fade-in">
    <div class="row mb-4">
      <div class="col">
        <h2 class="fw-bold">
          <i class="bi bi-box-seam me-2"></i>
          Gestión de Inventario
        </h2>
        <p class="text-muted">Control de insumos, entradas y salidas</p>
      </div>
      <div class="col-auto">
        <button class="btn btn-success me-2" @click="abrirModalMovimiento('entrada')">
          <i class="bi bi-box-arrow-in-down me-2"></i>
          Registrar Entrada
        </button>
        <button class="btn btn-warning me-2" @click="abrirModalMovimiento('salida')">
          <i class="bi bi-box-arrow-up me-2"></i>
          Registrar Salida
        </button>
        <button class="btn btn-primary" @click="abrirModalCrear">
          <i class="bi bi-plus-circle me-2"></i>
          Nuevo Insumo
        </button>
      </div>
    </div>

    <div v-if="insumosStockBajo.length > 0" class="alert alert-danger d-flex align-items-center mb-4">
      <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
      <div>
        <strong>¡Atención!</strong> Hay {{ insumosStockBajo.length }} insumo(s) con stock bajo o crítico. Revisa la lista para reponer.
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card border-start border-4 border-primary h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 small text-uppercase">Total Items</h6>
            <h3 class="mb-0">{{ insumos.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-start border-4 border-info h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 small text-uppercase">Valor Inventario</h6>
            <h3 class="mb-0 text-info">${{ valorTotalInventario.toLocaleString() }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-start border-4 border-warning h-100">
          <div class="card-body">
            <h6 class="text-muted mb-1 small text-uppercase">Stock Bajo</h6>
            <h3 class="mb-0 text-warning">{{ insumosStockBajo.length }}</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
              <input type="text" class="form-control border-start-0" placeholder="Buscar insumo..." v-model="busqueda">
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filtroCategoria">
              <option value="">Todas las categorías</option>
              <option value="quimicos">Químicos</option>
              <option value="ceras">Ceras</option>
              <option value="herramientas">Herramientas</option>
              <option value="accesorios">Accesorios</option>
              <option value="otros">Otros</option>
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
                <th class="ps-3">Insumo</th>
                <th>Categoría</th>
                <th>Stock</th>
                <th>Unidad</th>
                <th>Precio Unit.</th>
                <th>Total</th>
                <th>Estado</th>
                <th class="text-end pe-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="insumo in insumosFiltrados" :key="insumo.id">
                <td class="ps-3">
                  <div class="fw-bold">{{ insumo.nombre }}</div>
                  <small class="text-muted">Min: {{ insumo.stockMinimo }}</small>
                </td>
                <td><span class="badge bg-light text-dark border">{{ insumo.categoria }}</span></td>
                <td>
                  <h5 class="mb-0">
                    <span :class="'badge ' + (insumo.stock <= insumo.stockMinimo ? 'bg-danger' : 'bg-success')">
                      {{ insumo.stock }}
                    </span>
                  </h5>
                </td>
                <td>{{ insumo.unidad }}</td>
                <td>${{ insumo.precioUnitario.toLocaleString() }}</td>
                <td class="fw-bold text-muted">${{ (insumo.stock * insumo.precioUnitario).toLocaleString() }}</td>
                <td>
                  <i v-if="insumo.stock <= insumo.stockMinimo" class="bi bi-circle-fill text-danger small me-1"></i>
                  <i v-else class="bi bi-circle-fill text-success small me-1"></i>
                  {{ insumo.estadoTexto }}
                </td>
                <td class="text-end pe-3">
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" title="Editar" @click="editarInsumo(insumo)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger" title="Eliminar" @click="eliminarInsumo(insumo)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalInsumo" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">{{ modoEdicion ? 'Editar Insumo' : 'Nuevo Insumo' }}</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="guardarInsumo">
              <div class="mb-3">
                <label class="form-label fw-bold">Nombre del Insumo</label>
                <input type="text" class="form-control" v-model="insumoForm.nombre" required>
              </div>
              <div class="row g-2">
                <div class="col-6 mb-3">
                  <label class="form-label">Categoría</label>
                  <select class="form-select" v-model="insumoForm.categoria" required>
                    <option value="quimicos">Químicos</option>
                    <option value="ceras">Ceras</option>
                    <option value="herramientas">Herramientas</option>
                    <option value="accesorios">Accesorios</option>
                    <option value="otros">Otros</option>
                  </select>
                </div>
                <div class="col-6 mb-3">
                  <label class="form-label">Unidad</label>
                  <select class="form-select" v-model="insumoForm.unidad" required>
                    <option value="unidad">Unidad</option>
                    <option value="litro">Litro</option>
                    <option value="galon">Galón</option>
                    <option value="kilo">Kilo</option>
                    <option value="caja">Caja</option>
                  </select>
                </div>
              </div>
              
              <div class="row g-2">
                <div class="col-6 mb-3" v-if="!modoEdicion">
                  <label class="form-label fw-bold text-success">Stock Inicial</label>
                  <input type="number" class="form-control" v-model="insumoForm.stock" min="0" required>
                </div>
                <div class="col-6 mb-3" v-if="modoEdicion">
                  <label class="form-label text-muted">Stock (Solo lectura)</label>
                  <input type="text" class="form-control bg-light" :value="insumoForm.stock" disabled>
                  <small class="text-muted" style="font-size: 0.7rem">Usa "Movimientos" para cambiar stock</small>
                </div>

                <div class="col-6 mb-3">
                  <label class="form-label fw-bold text-danger">Stock Mínimo</label>
                  <input type="number" class="form-control" v-model="insumoForm.stockMinimo" min="1" required>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Precio Unitario ($)</label>
                <input type="number" class="form-control" v-model="insumoForm.precioUnitario" required>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="button" class="btn btn-primary" @click="guardarInsumo">
              <i class="bi bi-save me-2"></i> Guardar
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalMovimiento" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header text-white" :class="movimientoForm.tipo_movimiento === 'entrada' ? 'bg-success' : 'bg-warning text-dark'">
            <h5 class="modal-title">
              <i class="bi" :class="movimientoForm.tipo_movimiento === 'entrada' ? 'bi-arrow-down-circle' : 'bi-arrow-up-circle'"></i>
              Registrar {{ movimientoForm.tipo_movimiento === 'entrada' ? 'ENTRADA' : 'SALIDA' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
             <form @submit.prevent="registrarMovimiento">
                <div class="mb-3">
                  <label class="form-label">Insumo</label>
                  <select class="form-select" v-model="movimientoForm.insumoId" required>
                    <option v-for="i in insumos" :key="i.id" :value="i.id">{{ i.nombre }} (Stock: {{ i.stock }})</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label class="form-label">Cantidad</label>
                  <input type="number" class="form-control form-control-lg" v-model="movimientoForm.cantidad" min="1" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Motivo</label>
                  <select class="form-select" v-model="movimientoForm.motivo" required>
                    <option value="compra" v-if="movimientoForm.tipo_movimiento === 'entrada'">Compra / Reposición</option>
                    <option value="devolucion" v-if="movimientoForm.tipo_movimiento === 'entrada'">Devolución Cliente</option>
                    <option value="uso_interno" v-if="movimientoForm.tipo_movimiento === 'salida'">Uso en Lavado</option>
                    <option value="daño" v-if="movimientoForm.tipo_movimiento === 'salida'">Daño / Vencimiento</option>
                    <option value="ajuste">Ajuste de Inventario</option>
                  </select>
                </div>
             </form>
          </div>
          <div class="modal-footer">
             <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
             <button type="button" class="btn" :class="movimientoForm.tipo_movimiento === 'entrada' ? 'btn-success' : 'btn-warning'" @click="registrarMovimiento">
               Confirmar Movimiento
             </button>
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
  name: 'InventarioView',
  data() {
    return {
      busqueda: '',
      filtroCategoria: '',
      modoEdicion: false,
      insumos: [],
      insumoForm: {
        id: null,
        nombre: '',
        categoria: '',
        stock: 0,
        stockMinimo: 0,
        unidad: '',
        precioUnitario: 0
      },
      movimientoForm: {
        tipo_movimiento: 'entrada',
        insumoId: '',
        cantidad: 1,
        motivo: 'compra',
        usuario: 'admin'
      }
    }
  },
  mounted() {
    this.cargarInventario()
  },
  computed: {
    insumosFiltrados() {
      return this.insumos.filter(i => {
        const matchText = i.nombre.toLowerCase().includes(this.busqueda.toLowerCase());
        const matchCat = this.filtroCategoria ? i.categoria === this.filtroCategoria : true;
        return matchText && matchCat;
      });
    },
    insumosStockBajo() {
      return this.insumos.filter(i => i.stock <= i.stockMinimo)
    },
    valorTotalInventario() {
      return this.insumos.reduce((total, i) => total + (i.stock * i.precioUnitario), 0)
    }
  },
  methods: {
    async cargarInventario() {
      try {
        const data = await api.getInventario();
        const lista = Array.isArray(data) ? data : (data.data || []);
        
        this.insumos = lista.map(i => ({
          id: i.id,
          nombre: i.nombre,
          categoria: i.categoria,
          stock: i.stock,
          stockMinimo: i.stock_minimo,
          unidad: i.unidad,
          precioUnitario: i.precio_unitario,
          estadoTexto: i.stock <= i.stock_minimo ? 'Bajo' : 'Óptimo'
        }));
      } catch (e) { console.error(e); }
    },
    
    // --- CRUD INSUMOS ---
    abrirModalCrear() {
      this.modoEdicion = false;
      this.insumoForm = { nombre:'', categoria:'quimicos', stock:0, stockMinimo:5, unidad:'unidad', precioUnitario:0 };
      new bootstrap.Modal(document.getElementById('modalInsumo')).show();
    },
    editarInsumo(insumo) {
      this.modoEdicion = true;
      this.insumoForm = { ...insumo }; // Copia simple
      new bootstrap.Modal(document.getElementById('modalInsumo')).show();
    },
    async guardarInsumo() {
      if(!this.insumoForm.nombre) return alert("Nombre requerido");
      
      const payload = {
        nombre: this.insumoForm.nombre,
        categoria: this.insumoForm.categoria,
        stock: parseFloat(this.insumoForm.stock), // Solo se usa en crear
        stock_minimo: parseFloat(this.insumoForm.stockMinimo),
        unidad: this.insumoForm.unidad,
        precio_unitario: parseFloat(this.insumoForm.precioUnitario)
      };

      try {
        if(this.modoEdicion) {
          // UPDATE
          await api.updateInsumo(this.insumoForm.id, payload);
          alert("Insumo actualizado");
        } else {
          // CREATE
          await api.createInsumo(payload);
          alert("Insumo creado");
        }
        
        // Cerrar modal
        bootstrap.Modal.getInstance(document.getElementById('modalInsumo')).hide();
        this.cargarInventario();
        
      } catch (error) {
        alert("Error al guardar: " + error.message);
      }
    },
    async eliminarInsumo(insumo) {
      if(!confirm(`¿Eliminar ${insumo.nombre} del inventario?`)) return;
      try {
        await api.deleteInsumo(insumo.id);
        alert("Insumo eliminado");
        this.cargarInventario();
      } catch(e) {
        alert("Error al eliminar");
      }
    },

    // --- MOVIMIENTOS ---
    abrirModalMovimiento(tipo) {
      this.movimientoForm = {
        tipo_movimiento: tipo,
        insumoId: this.insumos.length > 0 ? this.insumos[0].id : '',
        cantidad: 1,
        motivo: tipo === 'entrada' ? 'compra' : 'uso_interno',
        usuario: 'admin'
      };
      new bootstrap.Modal(document.getElementById('modalMovimiento')).show();
    },
    async registrarMovimiento() {
      try {
        const payload = {
          id_insumo: this.movimientoForm.insumoId,
          tipo_movimiento: this.movimientoForm.tipo_movimiento,
          cantidad: parseFloat(this.movimientoForm.cantidad),
          motivo: this.movimientoForm.motivo,
          usuario: 'admin'
        };
        
        await api.registrarMovimiento(payload);
        alert("Movimiento registrado");
        
        bootstrap.Modal.getInstance(document.getElementById('modalMovimiento')).hide();
        this.cargarInventario();
        
      } catch (error) {
        alert("Error: " + (error.response?.data?.detail || error.message));
      }
    }
  }
}
</script>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>