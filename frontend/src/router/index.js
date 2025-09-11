// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/reset-password/:email',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPassword.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workflows',
    name: 'Workflows',
    component: () => import('@/views/Workflows.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workflows/new',
    name: 'NewWorkflow',
    component: () => import('@/views/WorkflowEditor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workflows/:id',
    name: 'EditWorkflow',
    component: () => import('@/views/WorkflowEditor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workflows/:id/execute',
    name: 'ExecuteWorkflow',
    component: () => import('@/views/WorkflowExecution.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/integrations',
    name: 'Integrations',
    component: () => import('@/views/Integrations.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/integrations/new',
    name: 'NewIntegration',
    component: () => import('@/views/IntegrationForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/integrations/:id',
    name: 'EditIntegration',
    component: () => import('@/views/IntegrationForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/executions',
    name: 'Executions',
    component: () => import('@/views/Executions.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/executions/:id',
    name: 'ExecutionDetails',
    component: () => import('@/views/ExecutionDetails.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/demo/trigger-action',
    name: 'TriggerActionDemo',
    component: () => import('@/views/TriggerActionDemo.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
