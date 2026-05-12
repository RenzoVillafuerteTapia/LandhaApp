<!-- Ruta: frontend/src/layouts/AdminLayout.vue -->
<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">⬡</span>
        <span class="brand-name">LandhaApp</span>
      </div>

      <nav class="sidebar-nav">
        <p class="nav-section-label">Principal</p>
        <router-link to="/" class="nav-item" active-class="active" exact>
          <span class="nav-icon">◈</span> Dashboard
        </router-link>

        <p class="nav-section-label">Catálogo</p>
        <router-link to="/products" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Productos
        </router-link>
        <router-link to="/categories" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Categorías
        </router-link>

        <p class="nav-section-label">Inventario</p>
        <router-link to="/stock" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Stock
        </router-link>
        <router-link to="/transfers" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Transferencias
        </router-link>

        <p class="nav-section-label">Ventas</p>
        <router-link to="/new-sale" class="nav-item nav-item-highlight" active-class="active">
          <span class="nav-icon">◈</span> Nueva venta
        </router-link>
        <router-link to="/sales" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Historial de ventas
        </router-link>
        <router-link to="/customers" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Clientes
        </router-link>

        <p class="nav-section-label">Administración</p>
        <router-link to="/users" class="nav-item" active-class="active">
          <span class="nav-icon">◈</span> Usuarios
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userInitial }}</div>
          <div>
            <p class="user-name">{{ auth.user?.username }}</p>
            <p class="user-role">Administrador</p>
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
const userInitial = computed(() => auth.user?.username?.[0]?.toUpperCase() || 'A')

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  min-height: 100vh;
  background: var(--landha-brown);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0;
  z-index: 100;
  overflow-y: auto;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 1.5rem 1.25rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  flex-shrink: 0;
}

.brand-icon { font-size: 1.5rem; color: var(--landha-beige); }
.brand-name { font-size: 1.1rem; font-weight: 700; color: #fff; letter-spacing: 0.5px; }

.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
}

.nav-section-label {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: rgba(255,255,255,0.4);
  padding: 0.75rem 0.5rem 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.6rem 0.75rem;
  border-radius: var(--radius-sm);
  color: rgba(255,255,255,0.75);
  font-size: 0.875rem;
  transition: background 0.15s, color 0.15s;
  margin-bottom: 2px;
}

.nav-item:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.nav-item.active {
  background: rgba(255,255,255,0.15);
  color: #fff;
  font-weight: 500;
}

/* Destacar Nueva Venta */
.nav-item-highlight {
  background: rgba(255,255,255,0.1);
  color: #fff;
  font-weight: 600;
  border: 1px solid rgba(255,255,255,0.2);
}

.nav-item-highlight:hover {
  background: rgba(255,255,255,0.2);
}

.nav-item-highlight.active {
  background: rgba(255,255,255,0.25);
  border-color: rgba(255,255,255,0.4);
}

.nav-icon { font-size: 0.75rem; opacity: 0.7; }

.sidebar-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid rgba(255,255,255,0.1);
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.75rem;
}

.user-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: var(--landha-wood);
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.user-name { color: #fff; font-size: 0.875rem; font-weight: 500; }
.user-role { color: rgba(255,255,255,0.5); font-size: 0.75rem; }

.logout-btn {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: var(--radius-sm);
  background: transparent;
  color: rgba(255,255,255,0.7);
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.15s;
}

.logout-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.main-content {
  margin-left: 240px;
  flex: 1;
  min-height: 100vh;
  background: var(--landha-cream);
  padding: 2rem;
}
</style>