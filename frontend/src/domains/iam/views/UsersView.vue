<!-- Ruta: frontend/src/domains/iam/views/UsersView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Usuarios</h1>
        <p class="text-muted">Gestión de accesos al sistema</p>
      </div>
      <button class="btn btn-primary" @click="openModal()">+ Nuevo usuario</button>
    </div>

    <div v-if="loading" class="loading">Cargando usuarios...</div>

    <div v-else class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Nombre completo</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td><strong>{{ user.username }}</strong></td>
            <td>{{ user.full_name }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span :class="['badge', user.role_name === 'admin' ? 'badge-brown' : 'badge-metal']">
                {{ user.role_name }}
              </span>
            </td>
            <td>
              <span :class="['badge', user.is_active ? 'badge-success' : 'badge-danger']">
                {{ user.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <button class="btn-icon" @click="openModal(user)">Editar</button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="empty-state">No hay usuarios registrados.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editing ? 'Editar usuario' : 'Nuevo usuario' }}</h2>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-form">
          <div class="field">
            <label class="field-label">Usuario *</label>
            <input v-model="form.username" type="text" class="field-input" :disabled="!!editing" required />
          </div>
          <div class="field">
            <label class="field-label">Nombre completo *</label>
            <input v-model="form.full_name" type="text" class="field-input" required />
          </div>
          <div class="field">
            <label class="field-label">Email *</label>
            <input v-model="form.email" type="email" class="field-input" required />
          </div>
          <div class="field">
            <label class="field-label">{{ editing ? 'Nueva contraseña (opcional)' : 'Contraseña *' }}</label>
            <input v-model="form.password" type="password" class="field-input" />
          </div>
          <div class="field">
            <label class="field-label">Rol *</label>
            <select v-model="form.role_id" class="field-input">
              <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
            </select>
          </div>
          <div v-if="formError" class="error-alert">{{ formError }}</div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="closeModal">Cancelar</button>
            <button class="btn btn-primary" :disabled="saving" @click="handleSubmit">
              {{ saving ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/core/http'

const users = ref([])
const roles = ref([])
const loading = ref(true)
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')
const form = ref({ username: '', full_name: '', email: '', password: '', role_id: null })

onMounted(async () => {
  await loadData()
  loading.value = false
})

async function loadData() {
  const [uRes, rRes] = await Promise.all([
    http.get('/auth/users'),
    http.get('/auth/roles').catch(() => ({ data: [] })),
  ])
  users.value = uRes.data
  // Extraer roles únicos de los usuarios si el endpoint de roles no existe
  if (rRes.data.length === 0) {
    const seen = new Set()
    users.value.forEach(u => {
      if (!seen.has(u.role_id)) {
        seen.add(u.role_id)
        roles.value.push({ id: u.role_id, name: u.role_name })
      }
    })
  } else {
    roles.value = rRes.data
  }
}

function openModal(user = null) {
  formError.value = ''
  if (user) {
    editing.value = user
    form.value = { username: user.username, full_name: user.full_name, email: user.email, password: '', role_id: user.role_id }
  } else {
    editing.value = null
    form.value = { username: '', full_name: '', email: '', password: '', role_id: roles.value[0]?.id }
  }
  showModal.value = true
}

function closeModal() { showModal.value = false; editing.value = null }

async function handleSubmit() {
  formError.value = ''
  saving.value = true
  try {
    if (editing.value) {
      const payload = { ...form.value }
      if (!payload.password) delete payload.password
      delete payload.username
      await http.patch(`/auth/users/${editing.value.id}`, payload)
    } else {
      await http.post('/auth/users', form.value)
    }
    await loadData()
    closeModal()
  } catch (e) {
    formError.value = e.response?.data?.error || 'Error al guardar.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--landha-brown); }
.data-table-wrapper { background: #fff; border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: var(--landha-beige); padding: 0.75rem 1rem; text-align: left; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--landha-brown); }
.data-table td { padding: 0.875rem 1rem; border-bottom: 1px solid var(--landha-gray-light); font-size: 0.875rem; }
.data-table tr:last-child td { border-bottom: none; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; }
.badge-success { background: #d1fae5; color: var(--landha-success); }
.badge-danger { background: #fee2e2; color: var(--landha-danger); }
.badge-brown { background: var(--landha-beige); color: var(--landha-brown); }
.badge-metal { background: #e2e8f0; color: var(--landha-metal-dark); }
.btn { padding: 0.6rem 1.25rem; border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; }
.btn-primary { background: var(--landha-brown); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--landha-brown-light); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: var(--landha-gray-light); color: var(--landha-black); }
.btn-icon { background: none; border: 1px solid var(--landha-beige-dark); border-radius: var(--radius-sm); padding: 4px 12px; font-size: 0.8rem; cursor: pointer; color: var(--landha-brown); }
.loading { text-align: center; padding: 3rem; color: var(--landha-gray); }
.empty-state { text-align: center; padding: 2rem; color: var(--landha-gray); }
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: var(--radius-lg); padding: 2rem; width: 480px; box-shadow: var(--shadow-lg); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-header h2 { font-size: 1.1rem; font-weight: 600; color: var(--landha-brown); }
.modal-close { background: none; border: none; font-size: 1.25rem; cursor: pointer; color: var(--landha-gray); }
.modal-form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.375rem; }
.field-label { font-size: 0.8rem; font-weight: 500; color: var(--landha-black); }
.field-input { padding: 0.65rem 0.875rem; border: 1.5px solid var(--landha-beige-dark); border-radius: var(--radius-md); font-size: 0.875rem; outline: none; background: var(--landha-cream); }
.field-input:focus { border-color: var(--landha-brown); background: #fff; }
.field-input:disabled { opacity: 0.6; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.5rem; }
.error-alert { padding: 0.75rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: var(--radius-sm); color: var(--landha-danger); font-size: 0.875rem; }
</style>