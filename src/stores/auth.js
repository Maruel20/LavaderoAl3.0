import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // 1. Estado (State)
  // Inicializamos leyendo de localStorage para no perder sesión al recargar
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)

  // 2. Getters (Computed)
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.rol === 'admin')

  // 3. Acciones (Actions)
  function setAuth(userData, tokenData) {
    user.value = userData
    token.value = tokenData
    
    // Persistencia
    localStorage.setItem('token', tokenData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function logout() {
    user.value = null
    token.value = null
    
    // Limpieza
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    // Opcional: Redirigir aquí o en el componente
    window.location.href = '/login' 
  }

  async function login(username, password) {
    try {
      // Usamos tu servicio API existente
      const data = await api.login(username, password)
      
      if (data.success) {
        setAuth(data.user, data.token)
        return true
      }
      return false
    } catch (error) {
      throw error
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout
  }
})
