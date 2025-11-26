<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1">Configuración de Tarifas</h2>
        <p class="text-muted">Gestiona los precios por vehículo y servicio (Sincronizado con BD)</p>
      </div>
      <button class="btn btn-outline-primary btn-sm" @click="recargarTarifas" :disabled="loading">
        <i class="bi bi-arrow-clockwise" :class="{ 'spin': loading }"></i> Refrescar
      </button>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger m-3">
          <i class="bi bi-exclamation-triangle me-2"></i> {{ error }}
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
                <td class="fw-bold text-capitalize">{{ tarifa.tipoVehiculo }}</td>
                
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
        
        <div v-if="!loading && tarifasProcesadas.length === 0" class="alert alert-warning mt-3">
          <i class="bi bi-exclamation-triangle"></i> No se encontraron tarifas. Revisa la base de datos.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useApi } from '@/composables/useApi'

// 1. Estado local
const tarifasProcesadas = ref([])

// 2. Función para cargar y transformar datos
const cargarDatos = async () => {
  const res = await api.getTarifas()
  const listaPlana = res.data || res

  if (!Array.isArray(listaPlana)) return []

  const agrupado = {}

  listaPlana.forEach(item => {
    const vehiculo = item.tipo_vehiculo
    
    if (!agrupado[vehiculo]) {
      agrupado[vehiculo] = {
        tipoVehiculo: vehiculo,
        // Valores iniciales por si faltan en BD
        lavado_simple: 0,
        lavado_completo: 0,
        encerado: 0,
        lavado_motor: 0,
        pulido: 0,
        descontaminacion: 0
      }
    }

    if (item.tipo_servicio) {
      agrupado[vehiculo][item.tipo_servicio] = item.precio
    }
  })

  tarifasProcesadas.value = Object.values(agrupado)
  return tarifasProcesadas.value
}

// 3. Usar Composable
const { loading, error, exec: recargarTarifas } = useApi(cargarDatos)

// 4. Ciclo de vida
onMounted(() => {
  recargarTarifas()
})

// 5. Acciones (Actualización)
const actualizarPrecio = async (tipoVehiculo, tipoServicio, nuevoPrecio) => {
  if (nuevoPrecio < 0) return

  try {
    // Llamada directa sin useApi para no bloquear toda la tabla con loading global
    await api.updateTarifa(tipoVehiculo, tipoServicio, parseFloat(nuevoPrecio))
    console.log(`✅ Precio actualizado: ${tipoVehiculo} - ${tipoServicio}`)
  } catch (e) {
    console.error('Error al guardar:', e)
    alert('Error al guardar el cambio. Verifica tu conexión.')
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
