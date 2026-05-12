<!-- Ruta: frontend/src/domains/products/views/CategoriesView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Categorías</h1>
        <p class="text-muted">Clasificación de productos</p>
      </div>
      <button class="btn btn-primary" @click="openModal()">+ Nueva categoría</button>
    </div>

    <div v-if="loading" class="loading">Cargando...</div>

    <div v-else class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Nombre</th>
            <th>Descripción</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td>{{ cat.id }}</td>
            <td><strong>{{ cat.name }}</strong></td>
            <td>{{ cat.description || '—' }}</td>
            <td><button class="btn-icon" @click="openModal(cat)">Editar</button></td>
          </tr>
          <tr v-if="categories.length === 0">
            <td colspan="4" class="empty-state">No hay categorías registradas.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editing ? 'Editar categoría' : 'Nueva categoría' }}</h2>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-form">
          <div class="field">
            <label class="field-label">Nombre *</label>
            <input v-model="form.name" type="text" class="field-input" required />
          </div>
          <div class="field">
            <label class="field-label">Descripción</label>
            <input v-model="form.description" type="text" class="field-input" />
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

const categories = ref([])
const loading = ref(true)
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')
const form = ref({ name: '', description: '' })

onMounted(async () => {
  const { data } = await http.get('/products/categories')
  categories.value = data
  loading.value = false
})

function openModal(cat = null) {
  formError.value = ''
  editing.value = cat
  form.value = cat ? { ...cat } : { name: '', description: '' }
  showModal.value = true
}

function closeModal() { showModal.value = false; editing.value = null }

async function handleSubmit() {
  formError.value = ''
  saving.value = true
  try {
    await http.post('/products/categories', form.value)
    const { data } = await http.get('/products/categories')
    categories.value = data
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
.btn { padding: 0.6rem 1.25rem; border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; }
.btn-primary { background: var(--landha-brown); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--landha-brown-light); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: var(--landha-gray-light); color: var(--landha-black); }
.btn-icon { background: none; border: 1px solid var(--landha-beige-dark); border-radius: var(--radius-sm); padding: 4px 12px; font-size: 0.8rem; cursor: pointer; color: var(--landha-brown); }
.loading { text-align: center; padding: 3rem; color: var(--landha-gray); }
.empty-state { text-align: center; padding: 2rem; color: var(--landha-gray); }
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: var(--radius-lg); padding: 2rem; width: 440px; box-shadow: var(--shadow-lg); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-header h2 { font-size: 1.1rem; font-weight: 600; color: var(--landha-brown); }
.modal-close { background: none; border: none; font-size: 1.25rem; cursor: pointer; color: var(--landha-gray); }
.modal-form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.375rem; }
.field-label { font-size: 0.8rem; font-weight: 500; color: var(--landha-black); }
.field-input { padding: 0.65rem 0.875rem; border: 1.5px solid var(--landha-beige-dark); border-radius: var(--radius-md); font-size: 0.875rem; outline: none; background: var(--landha-cream); }
.field-input:focus { border-color: var(--landha-brown); background: #fff; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.5rem; }
.error-alert { padding: 0.75rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: var(--radius-sm); color: var(--landha-danger); font-size: 0.875rem; }
</style>