<!-- Ruta: frontend/src/domains/auth/views/LoginView.vue -->
<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <div class="brand-logo">⬡</div>
        <h1 class="brand-title">LandhaApp</h1>
        <p class="brand-subtitle">Gestión de ventas e inventario</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="field">
          <label class="field-label">Usuario</label>
          <input
            v-model="form.username"
            type="text"
            class="field-input"
            placeholder="Tu usuario"
            autocomplete="username"
            required
          />
        </div>

        <div class="field">
          <label class="field-label">Contraseña</label>
          <input
            v-model="form.password"
            type="password"
            class="field-input"
            placeholder="Tu contraseña"
            autocomplete="current-password"
            required
          />
        </div>

        <div v-if="error" class="error-alert">{{ error }}</div>

        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? 'Ingresando...' : 'Ingresar' }}
        </button>
      </form>

      <p class="login-footer">LandhaApp © 2025 — Accesorios para muebles</p>
    </div>

    <div class="login-deco">
      <div class="deco-pattern"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const data = await auth.login(form.value.username, form.value.password)
    if (data.role === 'admin') router.push('/')
    else router.push('/seller')
  } catch (e) {
    error.value = e.response?.data?.error || 'Usuario o contraseña incorrectos.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: var(--landha-cream);
}

.login-card {
  width: 420px;
  min-height: 100vh;
  background: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 3rem 2.5rem;
  box-shadow: var(--shadow-lg);
  z-index: 1;
}

.login-brand {
  text-align: center;
  margin-bottom: 2.5rem;
}

.brand-logo {
  font-size: 3rem;
  color: var(--landha-brown);
  margin-bottom: 0.5rem;
}

.brand-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--landha-brown);
  margin-bottom: 0.25rem;
}

.brand-subtitle {
  color: var(--landha-gray);
  font-size: 0.875rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field { display: flex; flex-direction: column; gap: 0.375rem; }

.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--landha-black);
}

.field-input {
  padding: 0.75rem 1rem;
  border: 1.5px solid var(--landha-beige-dark);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  background: var(--landha-cream);
  color: var(--landha-black);
  outline: none;
  transition: border-color 0.15s;
}

.field-input:focus {
  border-color: var(--landha-brown);
  background: #fff;
}

.error-alert {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-sm);
  color: var(--landha-danger);
  font-size: 0.875rem;
}

.login-btn {
  padding: 0.875rem;
  background: var(--landha-brown);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  margin-top: 0.5rem;
}

.login-btn:hover:not(:disabled) { background: var(--landha-brown-light); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.login-footer {
  text-align: center;
  color: var(--landha-gray);
  font-size: 0.75rem;
  margin-top: 2rem;
}

.login-deco {
  flex: 1;
  background: var(--landha-brown);
  position: relative;
  overflow: hidden;
}

.deco-pattern {
  position: absolute;
  inset: 0;
  background-image:
    repeating-linear-gradient(
      45deg,
      rgba(255,255,255,0.03) 0px,
      rgba(255,255,255,0.03) 1px,
      transparent 1px,
      transparent 40px
    );
}
</style>