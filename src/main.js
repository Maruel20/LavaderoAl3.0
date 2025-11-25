import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "./App.vue"
import router from "./router"

// Bootstrap CSS
import "bootstrap/dist/css/bootstrap.min.css"
// Bootstrap Icons
import "bootstrap-icons/font/bootstrap-icons.css"
import * as bootstrap from "bootstrap"

// Estilos personalizados
import "./assets/custom.css"

const app = createApp(App)

app.config.globalProperties.$bootstrap = bootstrap

app.use(createPinia())
app.use(router)

app.mount("#app")
