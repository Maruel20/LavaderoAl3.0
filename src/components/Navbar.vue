<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
    <div class="container-fluid">
      <router-link class="navbar-brand fw-bold" to="/">
        <i class="bi bi-droplet-fill me-2"></i>
        Lavadero AL
      </router-link>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/" exact-active-class="active">
              <i class="bi bi-speedometer2 me-1"></i>
              Dashboard
            </router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/servicios" active-class="active">
              <i class="bi bi-water me-1"></i>
              Servicios
            </router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/convenios" active-class="active">
              <i class="bi bi-file-earmark-text me-1"></i>
              Convenios
            </router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/inventario" active-class="active">
              <i class="bi bi-box-seam me-1"></i>
              Inventario
            </router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/empleados" active-class="active">
              <i class="bi bi-person-badge me-1"></i>
              Empleados
            </router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/liquidaciones" active-class="active">
              <i class="bi bi-cash-coin me-1"></i>
              Liquidaciones
            </router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/tarifas" active-class="active">
              <i class="bi bi-tag me-1"></i>
              Tarifas
            </router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/reportes" active-class="active">
              <i class="bi bi-graph-up me-1"></i>
              Reportes
            </router-link>
          </li>
        </ul>
        
        <div class="d-flex align-items-center text-white">
          <i class="bi bi-person-circle me-2"></i>
          <span class="me-3">{{ nombreUsuario }}</span>
          <button class="btn btn-outline-light btn-sm" @click="logout">
            <i class="bi bi-box-arrow-right"></i>
            Salir
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navbar',
  data() {
    return {
      nombreUsuario: 'Usuario'
    }
  },
  mounted() {
    this.cargarUsuario()
  },
  methods: {
    cargarUsuario() {
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          this.nombreUsuario = user.username || user.nombre || 'Usuario'
        }
      } catch (error) {
        console.error('Error al cargar usuario:', error)
        this.nombreUsuario = 'Usuario'
      }
    },
    logout() {
      if (confirm('¿Está seguro de que desea cerrar sesión?')) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        this.$router.push('/login')
      }
    }
  }
}
</script>

<style scoped>
.navbar {
  padding: 1rem 0;
}

.navbar-brand {
  font-size: 1.5rem;
}

.nav-link {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  margin: 0 0.2rem;
  transition: all 0.2s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}
</style>

