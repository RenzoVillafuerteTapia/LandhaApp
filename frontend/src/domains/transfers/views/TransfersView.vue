<!-- Ruta: frontend/src/domains/transfers/views/TransfersView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Transferencias de Stock</h1>
        <p class="text-muted">Movimientos entre Tienda y Almacén</p>
      </div>
      <button class="btn btn-primary" @click="showModal = true">+ Nueva transferencia</button>
    </div>

    <div v-if="loading" class="loading">Cargando transferencias...</div>

    <div v-else class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Origen → Destino</th>
            <th>Productos</th>
            <th>Estado</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in transfers" :key="t.id">
            <td><strong>#{{ t.id }}</strong></td>
            <td>{{ locationName(t.origin_id) }} → {{ locationName(t.destination_id) }}</td>
            <td>{{ t.details.length }} ítem(s)</td>
            <td><span class="badge badge-success">{{ t.status }}</span></td>
            <td>{{ formatDate(t.created_at) }}</td>
          </tr>
          <tr v-if="transfers.length === 0">
            <td colspan="5" class="empty-state">No hay transferencias registradas.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal nueva transferencia -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>Nueva transferencia</h2>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>

        <div class="modal-form">
          <div class="field-grid">
            <div class="field">
              <label class="field-label">Origen</label>
              <select v-model="form.origin_id" class="field-input">
                <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Destino</label>
              <select v-model="form.destination_id" class="field-input">
                <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
              </select>
            </div>
          </div>

          <div class="field">
            <label class="field-label">Notas</label>
            <input v-model="form.notes" type="text" class="field-input" placeholder="Opcional..." />
          </div>

          <div class="items-section">
            <div class="items-header">
              <p class="field-label">Productos a transferir</p>
              <button class="btn-sm" @click="addItem">+ Agregar</button>
            </div>
            <div v-for="(item, idx) in form.items" :key="idx" class="item-row">
              <select v-model="item.product_id" class="field-input">
                <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
              <input v-model.number="item.quantity" type="number" min="1" class="field-input qty-input" placeholder="Cantidad" />
              <button class="remove-btn" @click="form.items.splice(idx, 1)">✕</button>
            </div>
          </div>

          <div v-if="formError" class="error-alert">{{ formError }}</div>

          <div class="modal-actions">
            <button class="btn btn-secondary" @click="closeModal">Cancelar</button>
            <button class="btn btn-primary" :disabled="saving" @click="handleSubmit">
              {{ saving ? 'Procesando...' : 'Confirmar transferencia' }}
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

const transfers = ref([])
const locations = ref([])
const products = ref([])
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const formError = ref('')

const form = ref({ origin_id: null, destination_id: null, notes: '', items: [] })

onMounted(async () => {
  const [tRes, lRes, pRes] = await Promise.all([
    http.get('/transfers'),
    http.get('/inventory/locations'),
    http.get('/products'),
  ])
  transfers.value = tRes.data
  locations.value = lRes.data
  products.value = pRes.data
  if (locations.value.length >= 2) {
    form.value.origin_id = locations.value[0].id
    form.value.destination_id = locations.value[1].id
  }
  loading.value = false
})

function locationName(id) {
  return locations.value.find(l => l.id === id)?.name || id
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function addItem() {
  form.value.items.push({ product_id: products.value[0]?.id || null, quantity: 1 })
}

function closeModal() {
  showModal.value = false
  formError.value = ''
  form.value.items = []
}

async function handleSubmit() {
  formError.value = ''
  if (form.value.origin_id === form.value.destination_id) {
    formError.value = 'El origen y destino deben ser distintos.'
    return
  }
  if (form.value.items.length === 0) {
    formError.value = 'Agrega al menos un producto.'
    return
  }
  saving.value = true
  try {
    await http.post('/transfers', form.value)
    const { data } = await http.get('/transfers')
    transfers.value = data
    closeModal()
  } catch (e) {
    formError.value = e.response?.data?.error || 'Error al registrar la transferencia.'
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

.btn { padding: 0.6rem 1.25rem; border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; }
.btn-primary { background: var(--landha-brown); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--landha-brown-light); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: var(--landha-gray-light); color: var(--landha-black); }
.btn-sm { padding: 4px 12px; border-radius: var(--radius-sm); background: var(--landha-beige); border: 1px solid var(--landha-beige-dark); font-size: 0.8rem; cursor: pointer; color: var(--landha-brown); }

.loading { text-align: center; padding: 3rem; color: var(--landha-gray); }
.empty-state { text-align: center; padding: 2rem; color: var(--landha-gray); }

.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: var(--radius-lg); padding: 2rem; width: 560px; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-lg); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-header h2 { font-size: 1.1rem; font-weight: 600; color: var(--landha-brown); }
.modal-close { background: none; border: none; font-size: 1.25rem; cursor: pointer; color: var(--landha-gray); }
.modal-form { display: flex; flex-direction: column; gap: 1rem; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.375rem; }
.field-label { font-size: 0.8rem; font-weight: 500; color: var(--landha-black); }
.field-input { padding: 0.65rem 0.875rem; border: 1.5px solid var(--landha-beige-dark); border-radius: var(--radius-md); font-size: 0.875rem; outline: none; background: var(--landha-cream); }
.field-input:focus { border-color: var(--landha-brown); background: #fff; }
.items-section { display: flex; flex-direction: column; gap: 0.5rem; }
.items-header { display: flex; justify-content: space-between; align-items: center; }
.item-row { display: flex; gap: 0.5rem; align-items: center; }
.qty-input { max-width: 90px; }
.remove-btn { background: none; border: none; color: var(--landha-gray); cursor: pointer; font-size: 1rem; padding: 4px 8px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.5rem; }
.error-alert { padding: 0.75rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: var(--radius-sm); color: var(--landha-danger); font-size: 0.875rem; }
</style>