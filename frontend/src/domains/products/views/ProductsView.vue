<!-- Ruta: frontend/src/domains/products/views/ProductsView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Productos</h1>
        <p class="text-muted">Catálogo de accesorios y herrajes</p>
      </div>
      <button class="btn btn-primary" @click="openModal()">+ Nuevo producto</button>
    </div>

    <div class="search-bar">
      <input v-model="search" type="text" class="field-input" placeholder="Buscar por nombre o código..." />
    </div>

    <div v-if="loading" class="loading">Cargando productos...</div>

    <div v-else class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Código</th>
            <th>Nombre</th>
            <th>Categoría</th>
            <th>Unidad</th>
            <th>Precio</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in filteredProducts" :key="product.id">
            <td><code class="code-tag">{{ product.code }}</code></td>
            <td>{{ product.name }}</td>
            <td>{{ product.category_name || '—' }}</td>
            <td>{{ product.unit }}</td>
            <td class="price">S/ {{ product.price.toFixed(2) }}</td>
            <td>
              <span :class="['badge', product.is_active ? 'badge-success' : 'badge-danger']">
                {{ product.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <button class="btn-icon" @click="openModal(product)">Editar</button>
            </td>
          </tr>
          <tr v-if="filteredProducts.length === 0">
            <td colspan="7" class="empty-state">No se encontraron productos.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editing ? 'Editar producto' : 'Nuevo producto' }}</h2>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>

        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="field-grid">
            <div class="field">
              <label class="field-label">Código *</label>
              <input v-model="form.code" type="text" class="field-input" required />
            </div>
            <div class="field">
              <label class="field-label">Unidad</label>
              <input v-model="form.unit" type="text" class="field-input" placeholder="UND, PAR, KG..." />
            </div>
          </div>

          <div class="field">
            <label class="field-label">Nombre *</label>
            <input v-model="form.name" type="text" class="field-input" required />
          </div>

          <div class="field">
            <label class="field-label">Descripción</label>
            <textarea v-model="form.description" class="field-input" rows="2"></textarea>
          </div>

          <div class="field-grid">
            <div class="field">
              <label class="field-label">Precio (S/) *</label>
              <input v-model.number="form.price" type="number" step="0.01" class="field-input" required />
            </div>
            <div class="field">
              <label class="field-label">Categoría</label>
              <select v-model="form.category_id" class="field-input">
                <option :value="null">Sin categoría</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
          </div>

          <div v-if="formError" class="error-alert">{{ formError }}</div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '@/core/http'

const products = ref([])
const categories = ref([])
const loading = ref(true)
const search = ref('')
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')

const form = ref({ code: '', name: '', description: '', unit: 'UND', price: 0, category_id: null })

const filteredProducts = computed(() => {
  if (!search.value) return products.value
  const s = search.value.toLowerCase()
  return products.value.filter(p =>
    p.name.toLowerCase().includes(s) || p.code.toLowerCase().includes(s)
  )
})

onMounted(async () => {
  await Promise.all([loadProducts(), loadCategories()])
  loading.value = false
})

async function loadProducts() {
  const { data } = await http.get('/products?active_only=false')
  products.value = data
}

async function loadCategories() {
  const { data } = await http.get('/products/categories')
  categories.value = data
}

function openModal(product = null) {
  formError.value = ''
  if (product) {
    editing.value = product
    form.value = { ...product }
  } else {
    editing.value = null
    form.value = { code: '', name: '', description: '', unit: 'UND', price: 0, category_id: null }
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editing.value = null
}

async function handleSubmit() {
  formError.value = ''
  saving.value = true
  try {
    if (editing.value) {
      await http.patch(`/products/${editing.value.id}`, form.value)
    } else {
      await http.post('/products', form.value)
    }
    await loadProducts()
    closeModal()
  } catch (e) {
    formError.value = e.response?.data?.error || 'Error al guardar el producto.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 1.5rem;
}
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--landha-brown); }

.search-bar { margin-bottom: 1rem; max-width: 400px; }

.data-table-wrapper {
  background: #fff; border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm); overflow: hidden;
}

.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  background: var(--landha-beige); padding: 0.75rem 1rem;
  text-align: left; font-size: 0.8rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.5px;
  color: var(--landha-brown);
}
.data-table td {
  padding: 0.875rem 1rem; border-bottom: 1px solid var(--landha-gray-light);
  font-size: 0.875rem;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: var(--landha-cream); }

.code-tag {
  background: var(--landha-beige); padding: 2px 8px;
  border-radius: 4px; font-size: 0.8rem; color: var(--landha-brown);
}

.price { font-weight: 600; color: var(--landha-brown); }

.badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 500;
}
.badge-success { background: #d1fae5; color: var(--landha-success); }
.badge-danger { background: #fee2e2; color: var(--landha-danger); }

.btn { padding: 0.6rem 1.25rem; border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: background 0.15s; }
.btn-primary { background: var(--landha-brown); color: #fff; }
.btn-primary:hover { background: var(--landha-brown-light); }
.btn-secondary { background: var(--landha-gray-light); color: var(--landha-black); }
.btn-icon { background: none; border: 1px solid var(--landha-beige-dark); border-radius: var(--radius-sm); padding: 4px 12px; font-size: 0.8rem; cursor: pointer; color: var(--landha-brown); }
.btn-icon:hover { background: var(--landha-beige); }

.loading { text-align: center; padding: 3rem; color: var(--landha-gray); }
.empty-state { text-align: center; padding: 2rem; color: var(--landha-gray); }

/* Modal */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}
.modal {
  background: #fff; border-radius: var(--radius-lg); padding: 2rem;
  width: 540px; max-height: 90vh; overflow-y: auto;
  box-shadow: var(--shadow-lg);
}
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-header h2 { font-size: 1.1rem; font-weight: 600; color: var(--landha-brown); }
.modal-close { background: none; border: none; font-size: 1.25rem; cursor: pointer; color: var(--landha-gray); }
.modal-form { display: flex; flex-direction: column; gap: 1rem; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.375rem; }
.field-label { font-size: 0.8rem; font-weight: 500; color: var(--landha-black); }
.field-input {
  padding: 0.65rem 0.875rem; border: 1.5px solid var(--landha-beige-dark);
  border-radius: var(--radius-md); font-size: 0.875rem; outline: none;
  background: var(--landha-cream); transition: border-color 0.15s;
}
.field-input:focus { border-color: var(--landha-brown); background: #fff; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.5rem; }
.error-alert { padding: 0.75rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: var(--radius-sm); color: var(--landha-danger); font-size: 0.875rem; }
</style>