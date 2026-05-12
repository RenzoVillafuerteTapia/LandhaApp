<!-- Ruta: frontend/src/domains/dashboard/views/SellerDashboardView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Bienvenido, {{ auth.user?.username }}</h1>
        <p class="text-muted">Panel de vendedor — LandhaApp</p>
      </div>
    </div>

    <div class="quick-links">
      <div class="links-grid">
        <router-link to="/seller/new-sale" class="quick-card primary">
          <span class="quick-icon">🛒</span>
          <span>Nueva venta</span>
        </router-link>
        <router-link to="/seller/products" class="quick-card">
          <span class="quick-icon">📦</span>
          <span>Consultar productos</span>
        </router-link>
        <router-link to="/seller/stock" class="quick-card">
          <span class="quick-icon">🏪</span>
          <span>Consultar stock</span>
        </router-link>
        <router-link to="/seller/customers" class="quick-card">
          <span class="quick-icon">👥</span>
          <span>Clientes</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
</script>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--landha-metal-dark); }

.links-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  max-width: 600px;
}

.quick-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  box-shadow: var(--shadow-sm);
  color: var(--landha-brown);
  font-weight: 600;
  font-size: 1rem;
  transition: box-shadow 0.15s, transform 0.15s;
  text-align: center;
}

.quick-card.primary {
  background: var(--landha-brown);
  color: #fff;
}

.quick-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.quick-icon { font-size: 2.5rem; }
</style>