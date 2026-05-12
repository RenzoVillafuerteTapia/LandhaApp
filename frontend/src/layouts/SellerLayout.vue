<!-- Ruta: frontend/src/layouts/SellerLayout.vue -->
<template>
  <div class="app-shell">
    <aside class="sidebar seller-sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">⬡</span>
        <span class="brand-name">LandhaApp</span>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/seller" class="nav-item" active-class="active" exact>
          <span class="nav-icon">◈</span> Inicio
        </router-link>
        <router-link to="/seller/new-sale" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Nueva Venta
        </router-link>
        <router-link to="/seller/products" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Productos
        </router-link>
        <router-link to="/seller/stock" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Stock
        </router-link>
        <router-link to="/seller/customers" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Clientes
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userInitial }}</div>
          <div>
            <p class="user-name">{{ auth.user?.username }}</p>
            <p class="user-role">Vendedor</p>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout">Salir</button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const userInitial = computed(() => auth.user?.username?.[0]?.toUpperCase() || 'V')

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
/* Reutiliza los mismos estilos del AdminLayout, con acento diferente */
.app-shell { display: flex; min-height: 100vh; }
.sidebar {
  width: 220px; min-height: 100vh;
  background: var(--landha-metal-dark);
  display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; z-index: 100;
}
.sidebar-brand {
  display: flex; align-items: center; gap: 10px;
  padding: 1.5rem 1.25rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.brand-icon { font-size: 1.5rem; color: var(--landha-beige); }
.brand-name { font-size: 1.1rem; font-weight: 700; color: #fff; }
.sidebar-nav { flex: 1; padding: 1rem 0.75rem; }
.nav-item {
  display: flex; align-items: center; gap: 8px;
  padding: 0.6rem 0.75rem; border-radius: var(--radius-sm);
  color: rgba(255,255,255,0.75); font-size: 0.875rem;
  transition: background 0.15s; margin-bottom: 2px;
}
.nav-item:hover { background: rgba(255,255,255,0.1); color: #fff; }
.nav-item.active { background: rgba(255,255,255,0.15); color: #fff; font-weight: 500; }
.nav-icon { font-size: 0.75rem; opacity: 0.7; }
.sidebar-footer { padding: 1rem 1.25rem; border-top: 1px solid rgba(255,255,255,0.1); }
.user-info { display: flex; align-items: center; gap: 10px; margin-bottom: 0.75rem; }
.user-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--landha-metal); color: #fff;
  font-weight: 600; font-size: 0.875rem;
  display: flex; align-items: center; justify-content: center;
}
.user-name { color: #fff; font-size: 0.875rem; font-weight: 500; }
.user-role { color: rgba(255,255,255,0.5); font-size: 0.75rem; }
.logout-btn {
  width: 100%; padding: 0.5rem;
  border: 1px solid rgba(255,255,255,0.2); border-radius: var(--radius-sm);
  background: transparent; color: rgba(255,255,255,0.7); font-size: 0.8rem; cursor: pointer;
}
.logout-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }
.main-content { margin-left: 220px; flex: 1; background: var(--landha-cream); padding: 2rem; }
</style>