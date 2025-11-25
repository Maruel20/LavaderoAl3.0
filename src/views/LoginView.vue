<template>
  <div class="login-container">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-5 col-lg-4">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <!-- Logo/Título -->
              <div class="text-center mb-4">
                <div class="login-icon mb-3">
                  <i class="bi bi-droplet-fill text-primary" style="font-size: 3rem;"></i>
                </div>
                <h3 class="fw-bold">Lavadero AL</h3>
                <p class="text-muted">Sistema de Gestión</p>
              </div>

              <!-- Formulario de Login -->
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="username" class="form-label">Usuario</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-person"></i>
                    </span>
                    <input
                      type="text"
                      class="form-control"
                      id="username"
                      v-model="formData.username"
                      placeholder="Ingrese su usuario"
                      required
                    />
                  </div>
                </div>

                <div class="mb-4">
                  <label for="password" class="form-label">Contraseña</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control"
                      id="password"
                      v-model="formData.password"
                      placeholder="Ingrese su contraseña"
                      required
                    />
                    <button
                      class="btn btn-outline-secondary"
                      type="button"
                      @click="showPassword = !showPassword"
                    >
                      <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                  </div>
                </div>

                <!-- Mensaje de error (se mostrará cuando haya backend) -->
                <div v-if="errorMessage" class="alert alert-danger" role="alert">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  {{ errorMessage }}
                </div>

                <!-- Botón de Login -->
                <button
                  type="submit"
                  class="btn btn-primary w-100 py-2 mb-3"
                  :disabled="isLoading"
                >
                  <span v-if="isLoading">
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Iniciando sesión...
                  </span>
                  <span v-else>
                    <i class="bi bi-box-arrow-in-right me-2"></i>
                    Iniciar Sesión
                  </span>
                </button>

                <!-- Recordar sesión -->
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="rememberMe"
                    v-model="formData.rememberMe"
                  />
                  <label class="form-check-label text-muted" for="rememberMe">
                    Recordar mi sesión
                  </label>
                </div>
              </form>

              <!-- Footer del card -->
              <div class="text-center mt-4 pt-3 border-top">
                <small class="text-muted">
                  <i class="bi bi-shield-check me-1"></i>
                  Acceso seguro al sistema
                </small>
              </div>
            </div>
          </div>

          <!-- Información adicional -->
          <div class="text-center mt-3">
            <small class="text-muted">
              ¿Problemas para acceder? Contacta al administrador
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'LoginView',
  data() {
    return {
      formData: {
        username: '',
        password: '',
        rememberMe: false
      },
      showPassword: false,
      isLoading: false,
      errorMessage: ''
    }
  },
  methods: {
    async handleLogin() {
      // Limpiar mensaje de error
      this.errorMessage = ''
      this.isLoading = true

      try {
        const data = await api.login(this.formData.username, this.formData.password)

        if (data.token && data.user) {
          // Guardar token en localStorage
          localStorage.setItem('token', data.token)
          localStorage.setItem('user', JSON.stringify(data.user))

          // Redirigir al dashboard
          this.$router.push('/dashboard')
        } else {
          this.errorMessage = 'Usuario o contraseña incorrectos'
        }

      } catch (error) {
        console.error('Error en login:', error)
        if (error.response && error.response.status === 401) {
          this.errorMessage = 'Usuario o contraseña incorrectos'
        } else {
          this.errorMessage = 'Error de conexión. Intente nuevamente.'
        }
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.card {
  border-radius: 1rem;
  backdrop-filter: blur(10px);
}

.login-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.input-group .form-control {
  border-left: none;
}

.input-group .form-control:focus {
  border-color: #ced4da;
  box-shadow: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
  transition: transform 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  transform: none;
}
</style>
