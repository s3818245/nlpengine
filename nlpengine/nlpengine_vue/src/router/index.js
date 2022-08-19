import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '../views/MainPage.vue'

const routes = [
  {
    path: '/',
    name: 'MainPage',
    component: () => import('../views/MainPage.vue')
  },
  {
    path: '/dbconnect',
    name: 'DatabaseConnect',
    component: () => import('../views/DatabaseConnect.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
