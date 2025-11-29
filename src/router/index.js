import { createRouter, createWebHistory } from "vue-router"
import LoginView from "../views/LoginView.vue"
import DashboardView from "../views/DashboardView.vue"
import ServiciosView from "../views/ServiciosView.vue"
import InventarioView from "../views/InventarioView.vue"
import EmpleadosView from "../views/EmpleadosView.vue"
import LiquidacionesView from "../views/LiquidacionesView.vue"
import ConveniosView from "../views/ConveniosView.vue"
import ReportesView from "../views/ReportesView.vue"
import TarifasView from "../views/TarifasView.vue"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 1. Redirigir la raíz "/" al dashboard
    {
      path: "/",
      redirect: "/dashboard"
    },
    // 2. Definir la ruta "/dashboard" explícitamente
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashboardView,
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/servicios",
      name: "servicios",
      component: ServiciosView,
    },
    {
      path: "/inventario",
      name: "inventario",
      component: InventarioView,
    },
    {
      path: "/empleados",
      name: "empleados",
      component: EmpleadosView,
    },
    {
      path: "/liquidaciones",
      name: "liquidaciones",
      component: LiquidacionesView,
    },
    {
      path: "/convenios",
      name: "convenios",
      component: ConveniosView,
    },
    {
      path: "/reportes",
      name: "reportes",
      component: ReportesView,
    },
    {
      path: "/tarifas",
      name: "tarifas",
      component: TarifasView,
    },
    // 3. Capturar cualquier ruta desconocida y mandar al dashboard (o login)
    { 
      path: '/:pathMatch(.*)*', 
      redirect: '/dashboard' 
    }
  ],
})

// Protección de rutas
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (!token && to.name !== 'login') {
    next({ name: 'login' })
  }
  else if (token && to.name === 'login') {
    next({ name: 'dashboard' })
  }
  else {
    next()
  }
})

export default router 
