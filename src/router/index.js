import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Synthesis',
    component: () => import('../views/Synthesis.vue')
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: () => import('../views/Portfolio.vue')
  },
  {
    path: '/performance',
    name: 'Performance',
    component: () => import('../views/Performance.vue')
  },
  {
    path: '/dividends',
    name: 'Dividends',
    component: () => import('../views/Dividends.vue')
  },
  {
    path: '/research',
    name: 'Research',
    component: () => import('../views/Research.vue')
  },
  {
    path: '/plan',
    name: 'Plan',
    component: () => import('../views/Plan.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
