<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <Navbar v-if="!esRutaLogin" />
    
    <div class="flex-grow-1">
      <router-view />
    </div>

    <Footer v-if="!esRutaLogin" />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue' // Importar el Footer

export default {
  name: 'App',
  components: {
    Navbar,
    Footer // Registrar el componente
  },
  computed: {
    esRutaLogin() {
      // Oculta el menú y el footer si la ruta es '/login'
      return this.$route.path === '/login';
    }
  }
}
</script>

<style>
/* Estilo base para fondo gris suave en todo el sistema */
body {
  background-color: #f8f9fa; 
}
</style>