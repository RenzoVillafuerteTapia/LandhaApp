<!-- Ruta: frontend/src/domains/dashboard/views/DashboardView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="text-muted">Bienvenido, {{ auth.user?.username }}</p>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-info">
          <p class="stat-value">{{ stats.products }}</p>
          <p class="stat-label">Productos activos</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🛒</div>
        <div class="stat-info">
          <p class="stat-value">{{ stats.sales }}</p>
          <p class="stat-label">Ventas registradas</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <p class="stat-value">{{ stats.customers }}</p>
          <p class="stat-label">Clientes</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔄</div>
        <div class="stat-info">
          <p class="stat-value">{{ stats.transfers }}</p>
          <p class="stat-label">Transferencias</p>
        </div>
      </div>
    </div>

    <div class="quick-links">
      <h2 class="section-title">Accesos rápidos</h2>
      <div class="links-grid">
        <router-link to="/products" class="quick-card">
          <span class="quick-icon">📦</span>
          <span>Gestionar productos</span>
        </router-link>
        <router-link to="/stock" class="quick-card">
          <span class="quick-icon">🏪</span>
          <span>Ver stock</span>
        </router-link>
        <router-link to="/transfers" class="quick-card">
          <span class="quick-icon">🔄</span>
          <span>Transferencias</span>
        </router-link>
        <router-link to="/sales" class="quick-card">
          <span class="quick-icon">🛒</span>
          <span>Ver ventas</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import http from '@/core/http'

const auth = useAuthStore()
const stats = ref({ products: 0, sales: 0, customers: 0, transfers: 0 })

onMounted(async () => {
  try {
    const [prod, sales, customers, transfers] = await Promise.all([
      http.get('/products'),
      http.get('/sales'),
      http.get('/customers'),
      http.get('/transfers'),
    ])
    stats.value = {
      products: prod.data.length,
      sales: sales.data.length,
      customers: customers.data.length,
      transfers: transfers.data.length,
    }
  } catch (e) {
    // Si algún endpoint falla, dejamos en 0
  }
})
</script>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--landha-brown); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--landha-brown);
}

.stat-icon { font-size: 2rem; }
.stat-value { font-size: 1.75rem; font-weight: 700; color: var(--landha-brown); }
.stat-label { font-size: 0.8rem; color: var(--landha-gray); }

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--landha-brown);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.quick-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  box-shadow: var(--shadow-sm);
  color: var(--landha-brown);
  font-weight: 500;
  font-size: 0.875rem;
  transition: box-shadow 0.15s, transform 0.15s;
  text-align: center;
}

.quick-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.quick-icon { font-size: 2rem; }
</style>