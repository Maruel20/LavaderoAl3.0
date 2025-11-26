import { ref } from 'vue'

/**
 * Composable para manejar peticiones asíncronas con estado reactivo.
 * @param {Function} apiCallback - La función del servicio (api.js) a ejecutar.
 * @param {Object} options - Opciones opcionales { initialData: [] }
 */
export function useApi(apiCallback, options = {}) {
  const data = ref(options.initialData || [])
  const error = ref(null)
  const loading = ref(false)

  const exec = async (...args) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiCallback(...args)
      // Si la respuesta tiene un campo 'data', lo usamos; si no, usamos la respuesta directa
      // Esto depende de si tu api.js devuelve response.data o response completo.
      // Ajustado a tu api.js actual que devuelve response.data.
      data.value = response
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Error desconocido'
      console.error("Error en useApi:", err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    error,
    loading,
    exec
  }
}