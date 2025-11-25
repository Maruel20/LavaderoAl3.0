<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1">Configuración de Tarifas</h2>
        <p class="text-muted">Gestiona los precios por vehículo y servicio (Sincronizado con BD)</p>
      </div>
      <button class="btn btn-outline-primary btn-sm" @click="cargarTarifas" :disabled="cargando">
        <i class="bi bi-arrow-clockwise" :class="{ 'spin': cargando }"></i> Refrescar
      </button>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <div v-if="cargando" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th style="min-width: 150px;">Tipo de Vehículo</th>
                <th>Lavado Simple</th>
                <th>Lavado Completo</th>
                <th>Encerado</th>
                <th>Lavado Motor</th>
                <th>Pulido</th>
                <th>Descontam.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tarifa in tarifasProcesadas" :key="tarifa.tipoVehiculo">
                <td class="fw-bold">{{ tarifa.tipoVehiculo }}</td>
                
                <td>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control text-end" 
                      v-model.number="tarifa.lavado_simple"
                      @change="actualizarPrecio(tarifa.tipoVehiculo, 'lavado_simple', tarifa.lavado_simple)">
                  </div>
                </td>

                <td>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control text-end" 
                      v-model.number="tarifa.lavado_completo"
                      @change="actualizarPrecio(tarifa.tipoVehiculo, 'lavado_completo', tarifa.lavado_completo)">
                  </div>
                </td>

                <td>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control text-end" 
                      v-model.number="tarifa.encerado"
                      @change="actualizarPrecio(tarifa.tipoVehiculo, 'encerado', tarifa.encerado)">
                  </div>
                </td>

                <td>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control text-end" 
                      v-model.number="tarifa.lavado_motor"
                      @change="actualizarPrecio(tarifa.tipoVehiculo, 'lavado_motor', tarifa.lavado_motor)">
                  </div>
                </td>

                <td>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control text-end" 
                      v-model.number="tarifa.pulido"
                      @change="actualizarPrecio(tarifa.tipoVehiculo, 'pulido', tarifa.pulido)">
                  </div>
                </td>

                 <td>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control text-end" 
                      v-model.number="tarifa.descontaminacion"
                      @change="actualizarPrecio(tarifa.tipoVehiculo, 'descontaminacion', tarifa.descontaminacion)">
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="!cargando && tarifasProcesadas.length === 0" class="alert alert-warning mt-3">
          <i class="bi bi-exclamation-triangle"></i> No se encontraron tarifas. Revisa la base de datos.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Importamos el objeto 'api' que contiene tus funciones (getTarifas, updateTarifa, etc.)
import api from '@/services/api' 

export default {
  name: 'TarifasView',
  data() {
    return {
      tarifasProcesadas: [],
      cargando: false
    }
  },
  async mounted() {
    await this.cargarTarifas();
  },
  methods: {
    async cargarTarifas() {
      this.cargando = true;
      try {
        // CORRECCIÓN: Usamos la función definida en tu api.js
        const datos = await api.getTarifas(); 
        
        // En api.js ya retornas 'response.data', así que 'datos' es el array directo
        this.transformarDatos(datos);
        
      } catch (error) {
        console.error('Error cargando tarifas:', error);
      } finally {
        this.cargando = false;
      }
    },

    transformarDatos(listaPlana) {
      if (!Array.isArray(listaPlana)) {
        console.error("Formato de datos incorrecto recibido del servidor");
        return;
      }

      const agrupado = {};

      listaPlana.forEach(item => {
        const vehiculo = item.tipo_vehiculo;
        
        if (!agrupado[vehiculo]) {
          agrupado[vehiculo] = {
            tipoVehiculo: vehiculo,
            // Valores iniciales alineados con BD
            lavado_simple: 0,
            lavado_completo: 0,
            encerado: 0,
            lavado_motor: 0,
            pulido: 0,
            descontaminacion: 0
          };
        }

        if (item.tipo_servicio) {
            agrupado[vehiculo][item.tipo_servicio] = item.precio;
        }
      });

      this.tarifasProcesadas = Object.values(agrupado);
    },

    async actualizarPrecio(tipoVehiculo, tipoServicio, nuevoPrecio) {
      if (nuevoPrecio < 0) return;

      try {
        // CORRECCIÓN: Usamos la función definida en tu api.js
        // updateTarifa(tipoVehiculo, tipoServicio, precio)
        await api.updateTarifa(tipoVehiculo, tipoServicio, parseFloat(nuevoPrecio));
        
        console.log(`✅ Guardado: ${tipoVehiculo} -> ${tipoServicio}: ${nuevoPrecio}`);
      } catch (error) {
        console.error('Error al guardar:', error);
        alert('Error al guardar el cambio. Verifica tu conexión.');
      }
    }
  }
}
</script>

<style scoped>
.input-group-sm { min-width: 100px; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }
input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
input[type=number] { -moz-appearance: textfield; }
</style>
