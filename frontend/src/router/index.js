// Ruta: frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/domains/auth/views/LoginView.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/domains/dashboard/views/DashboardView.vue') },
      { path: 'products', name: 'Products', component: () => import('@/domains/products/views/ProductsView.vue') },
      { path: 'categories', name: 'Categories', component: () => import('@/domains/products/views/CategoriesView.vue') },
      { path: 'stock', name: 'Stock', component: () => import('@/domains/inventory/views/StockView.vue') },
      { path: 'transfers', name: 'Transfers', component: () => import('@/domains/transfers/views/TransfersView.vue') },
      { path: 'users', name: 'Users', component: () => import('@/domains/iam/views/UsersView.vue') },
      { path: 'customers', name: 'Customers', component: () => import('@/domains/customers/views/CustomersView.vue') },
      { path: 'sales', name: 'SalesAdmin', component: () => import('@/domains/sales/views/SalesView.vue') },
      { path: 'new-sale', name: 'NewSaleAdmin', component: () => import('@/domains/sales/views/NewSaleView.vue') },
    ]
  },
  {
    path: '/seller',
    component: () => import('@/layouts/SellerLayout.vue'),
    meta: { requiresAuth: true, roles: ['seller', 'admin'] },
    children: [
      { path: '', name: 'SellerDashboard', component: () => import('@/domains/dashboard/views/SellerDashboardView.vue') },
      { path: 'new-sale', name: 'NewSale', component: () => import('@/domains/sales/views/NewSaleView.vue') },
      { path: 'products', name: 'SellerProducts', component: () => import('@/domains/products/views/ProductsView.vue') },
      { path: 'stock', name: 'SellerStock', component: () => import('@/domains/inventory/views/StockView.vue') },
      { path: 'customers', name: 'SellerCustomers', component: () => import('@/domains/customers/views/CustomersView.vue') },
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()

  if (to.meta.public) return next()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) {
    if (auth.user?.role === 'seller') return next('/seller')
    return next('/')
  }

  next()
})

export default router