import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import CadastroView from '../views/CadastroView.vue'
import CarteirinhaView from '../views/CarteirinhaView.vue' // <--- Importar aqui

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: LoginView },
    { path: '/login', redirect: '/' },
    { path: '/cadastro', name: 'cadastro', component: CadastroView },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    
    // Nova rota do Associado:
    { 
      path: '/minha-carteirinha', 
      name: 'minha-carteirinha', 
      component: CarteirinhaView 
    }
  ]
})

export default router