import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import Particles from "@tsparticles/vue3";
import { loadSlim } from "@tsparticles/slim";

// 配置 axios 允许跨域携带 cookie
axios.defaults.withCredentials = true

const app = createApp(App)

app.use(router)
app.use(ElementPlus)
app.use(Particles, {
  init: async (engine) => {
    await loadSlim(engine);
  },
});

app.mount('#app')
