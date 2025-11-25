<template>
  <div id="app">
    <Navbar v-if="!esRutaLogin" />
    
    <router-view />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue' // Asegúrate de crear este componente

export default {
  name: 'App',
  components: {
    Navbar
  },
  computed: {
    esRutaLogin() {
      // Oculta el menú si la ruta es '/login'
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

