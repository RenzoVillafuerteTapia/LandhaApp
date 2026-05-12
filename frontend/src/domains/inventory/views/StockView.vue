<!-- Ruta: frontend/src/domains/inventory/views/StockView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Control de Stock</h1>
        <p class="text-muted">Inventario por ubicación — Tienda y Almacén</p>
      </div>
      <button class="btn btn-primary" @click="openAdjustModal()">+ Ingresar stock</button>
    </div>

    <!-- Filtro por ubicación -->
    <div class="filter-bar">
      <button
        :class="['filter-btn', selectedLocation === null ? 'active' : '']"
        @click="selectLocation(null)"
      >
        Todas las ubicaciones
      </button>
      <button
        v-for="loc in locations"
        :key="loc.id"
        :class="['filter-btn', selectedLocation === loc.id ? 'active' : '']"
        @click="selectLocation(loc.id)"
      >
        {{ loc.name }}
      </button>
    </div>

    <!-- Resumen por ubicación -->
    <div class="location-cards" v-if="!loading">
      <div class="location-card" v-for="loc in locations" :key="loc.id">
        <div class="location-card-header">
          <span class="location-icon">{{ loc.type === 'store' ? '🏪' : '🏭' }}</span>
          <div>
            <p class="location-name">{{ loc.name }}</p>
            <p class="location-type">{{ loc.type === 'store' ? 'Punto de venta' : 'Almacén central' }}</p>
          </div>
        </div>
        <div class="location-stats">
          <div class="location-stat">
            <span class="stat-value">{{ stockByLocation(loc.id).length }}</span>
            <span class="stat-label">productos</span>
          </div>
          <div class="location-stat">
            <span class="stat-value">{{ totalUnits(loc.id) }}</span>
            <span class="stat-label">unidades</span>
          </div>
          <div class="location-stat">
            <span class="stat-value zero">{{ zeroStock(loc.id) }}</span>
            <span class="stat-label">sin stock</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">Cargando stock...</div>

    <!-- Tabla de stock -->
    <div v-else class="data-table-wrapper">
      <div class="table-toolbar">
        <input
          v-model="search"
          type="text"
          class="field-input search-input"
          placeholder="Buscar producto..."
        />
        <span class="table-count">{{ filteredStock.length }} registros</span>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th>Producto</th>
            <th>Ubicación</th>
            <th>Cantidad</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredStock" :key="`${item.product_id}-${item.location_id}`">
            <td>
              <div class="product-cell">
                <span class="product-name">{{ productName(item.product_id) }}</span>
                <code class="product-code">{{ productCode(item.product_id) }}</code>
              </div>
            </td>
            <td>
              <span class="location-pill">
                {{ item.location_name }}
              </span>
            </td>
            <td>
              <span :class="['qty-badge', quantityClass(item.quantity)]">
                {{ item.quantity }} uds
              </span>
            </td>
            <td>
              <span v-if="item.quantity === 0" class="badge badge-danger">Sin stock</span>
              <span v-else-if="item.quantity < 5" class="badge badge-warning">Stock bajo</span>
              <span v-else class="badge badge-success">Disponible</span>
            </td>
            <td>
              <button class="btn-icon" @click="openAdjustModal(item)">
                Ajustar
              </button>
            </td>
          </tr>
          <tr v-if="filteredStock.length === 0">
            <td colspan="5" class="empty-state">
              {{ allStock.length === 0 ? 'No hay stock registrado. Usa "Ingresar stock" para comenzar.' : 'Sin resultados para la búsqueda.' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal ajuste de stock -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ adjustTarget ? 'Ajustar stock' : 'Ingresar stock' }}</h2>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>

        <div class="modal-form">
          <div class="field">
            <label class="field-label">Producto *</label>
            <select v-model="form.product_id" class="field-input" :disabled="!!adjustTarget">
              <option :value="null" disabled>Selecciona un producto</option>
              <option v-for="p in products" :key="p.id" :value="p.id">
                {{ p.name }} — {{ p.code }}
              </option>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Ubicación *</label>
            <select v-model="form.location_id" class="field-input" :disabled="!!adjustTarget">
              <option :value="null" disabled>Selecciona una ubicación</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                {{ loc.name }}
              </option>
            </select>
          </div>

          <!-- Stock actual si viene de ajuste -->
          <div v-if="adjustTarget" class="current-stock-info">
            <span class="info-label">Stock actual:</span>
            <span :class="['qty-badge', quantityClass(adjustTarget.quantity)]">
              {{ adjustTarget.quantity }} uds
            </span>
          </div>

          <div class="field">
            <label class="field-label">Tipo de movimiento</label>
            <div class="movement-type-selector">
              <button
                :class="['type-btn', form.movement_type === 'in' ? 'active-in' : '']"
                @click="form.movement_type = 'in'"
              >
                ↑ Entrada
              </button>
              <button
                :class="['type-btn', form.movement_type === 'out' ? 'active-out' : '']"
                @click="form.movement_type = 'out'"
              >
                ↓ Salida
              </button>
            </div>
          </div>

          <div class="field">
            <label class="field-label">Cantidad *</label>
            <input
              v-model.number="form.quantity"
              type="number"
              min="1"
              class="field-input"
              placeholder="Ej: 50"
            />
          </div>

          <div class="field">
            <label class="field-label">Notas (opcional)</label>
            <input
              v-model="form.notes"
              type="text"
              class="field-input"
              placeholder="Ej: Compra inicial, ajuste por conteo físico..."
            />
          </div>

          <!-- Preview del resultado -->
          <div v-if="adjustTarget && form.quantity > 0" class="preview-box">
            <span class="preview-label">Resultado estimado:</span>
            <span class="preview-value">
              {{ adjustTarget.quantity }}
              {{ form.movement_type === 'in' ? '+' : '−' }}
              {{ form.quantity }}
              =
              <strong>{{ form.movement_type === 'in' ? adjustTarget.quantity + form.quantity : adjustTarget.quantity - form.quantity }} uds</strong>
            </span>
          </div>

          <div v-if="formError" class="error-alert">{{ formError }}</div>
          <div v-if="formSuccess" class="success-alert">{{ formSuccess }}</div>

          <div class="modal-actions">
            <button class="btn btn-secondary" @click="closeModal">Cancelar</button>
            <button class="btn btn-primary" :disabled="saving" @click="handleSubmit">
              {{ saving ? 'Guardando...' : 'Confirmar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '@/core/http'

const allStock = ref([])
const locations = ref([])
const products = ref([])
const loading = ref(true)
const selectedLocation = ref(null)
const search = ref('')
const showModal = ref(false)
const adjustTarget = ref(null)
const saving = ref(false)
const formError = ref('')
const formSuccess = ref('')

const form = ref({
  product_id: null,
  location_id: null,
  quantity: 1,
  movement_type: 'in',
  notes: '',
})

onMounted(async () => {
  await loadAll()
  loading.value = false
})

async function loadAll() {
  const [stockRes, locRes, prodRes] = await Promise.all([
    http.get('/inventory/stock'),
    http.get('/inventory/locations'),
    http.get('/products?active_only=false'),
  ])
  allStock.value = stockRes.data
  locations.value = locRes.data
  products.value = prodRes.data
}

// Stock filtrado por ubicación seleccionada
const displayStock = computed(() => {
  if (selectedLocation.value === null) return allStock.value
  return allStock.value.filter(s => s.location_id === selectedLocation.value)
})

// Stock filtrado además por búsqueda
const filteredStock = computed(() => {
  if (!search.value) return displayStock.value
  const s = search.value.toLowerCase()
  return displayStock.value.filter(item => {
    const name = productName(item.product_id).toLowerCase()
    const code = productCode(item.product_id).toLowerCase()
    return name.includes(s) || code.includes(s)
  })
})

function stockByLocation(locationId) {
  return allStock.value.filter(s => s.location_id === locationId)
}

function totalUnits(locationId) {
  return stockByLocation(locationId).reduce((acc, s) => acc + s.quantity, 0)
}

function zeroStock(locationId) {
  return stockByLocation(locationId).filter(s => s.quantity === 0).length
}

function productName(productId) {
  return products.value.find(p => p.id === productId)?.name || `Producto #${productId}`
}

function productCode(productId) {
  return products.value.find(p => p.id === productId)?.code || ''
}

function quantityClass(qty) {
  if (qty === 0) return 'zero'
  if (qty < 5) return 'low'
  return 'ok'
}

async function selectLocation(locationId) {
  selectedLocation.value = locationId
}

function openAdjustModal(stockItem = null) {
  formError.value = ''
  formSuccess.value = ''
  adjustTarget.value = stockItem

  if (stockItem) {
    form.value = {
      product_id: stockItem.product_id,
      location_id: stockItem.location_id,
      quantity: 1,
      movement_type: 'in',
      notes: '',
    }
  } else {
    form.value = {
      product_id: null,
      location_id: locations.value[0]?.id || null,
      quantity: 1,
      movement_type: 'in',
      notes: '',
    }
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  adjustTarget.value = null
  formError.value = ''
  formSuccess.value = ''
}

async function handleSubmit() {
  formError.value = ''
  formSuccess.value = ''

  if (!form.value.product_id) {
    formError.value = 'Selecciona un producto.'
    return
  }
  if (!form.value.location_id) {
    formError.value = 'Selecciona una ubicación.'
    return
  }
  if (!form.value.quantity || form.value.quantity < 1) {
    formError.value = 'La cantidad debe ser mayor a 0.'
    return
  }

  saving.value = true
  try {
    await http.post('/inventory/stock/adjust', {
      product_id: form.value.product_id,
      location_id: form.value.location_id,
      quantity: form.value.quantity,
      movement_type: form.value.movement_type,
      notes: form.value.notes,
    })

    // Recargar stock
    const { data } = await http.get('/inventory/stock')
    allStock.value = data

    const action = form.value.movement_type === 'in' ? 'ingresadas' : 'retiradas'
    formSuccess.value = `✅ ${form.value.quantity} unidades ${action} correctamente.`

    // Cerrar tras 1.5s
    setTimeout(() => closeModal(), 1500)
  } catch (e) {
    formError.value = e.response?.data?.error || 'Error al ajustar el stock.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-header {
  display: flex; justify-content: space-between;
  align-items: flex-start; margin-bottom: 1.5rem;
}
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--landha-brown); }

.filter-bar { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.filter-btn {
  padding: 0.5rem 1rem; border-radius: 20px;
  border: 1.5px solid var(--landha-beige-dark);
  background: #fff; color: var(--landha-gray);
  font-size: 0.875rem; cursor: pointer; transition: all 0.15s;
}
.filter-btn.active { background: var(--landha-brown); border-color: var(--landha-brown); color: #fff; }
.filter-btn:hover:not(.active) { border-color: var(--landha-brown); color: var(--landha-brown); }

/* Location summary cards */
.location-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.location-card {
  background: #fff; border-radius: var(--radius-lg);
  padding: 1.25rem; box-shadow: var(--shadow-sm);
  border-top: 3px solid var(--landha-brown);
}
.location-card-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.location-icon { font-size: 1.75rem; }
.location-name { font-weight: 600; font-size: 1rem; color: var(--landha-brown); }
.location-type { font-size: 0.75rem; color: var(--landha-gray); }
.location-stats { display: flex; gap: 1.5rem; }
.location-stat { display: flex; flex-direction: column; }
.stat-value { font-size: 1.25rem; font-weight: 700; color: var(--landha-black); }
.stat-value.zero { color: var(--landha-danger); }
.stat-label { font-size: 0.7rem; color: var(--landha-gray); text-transform: uppercase; letter-spacing: 0.5px; }

/* Table */
.data-table-wrapper { background: #fff; border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden; }
.table-toolbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1rem 0; gap: 1rem; }
.search-input { max-width: 300px; }
.table-count { font-size: 0.8rem; color: var(--landha-gray); white-space: nowrap; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  background: var(--landha-beige); padding: 0.75rem 1rem;
  text-align: left; font-size: 0.8rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.5px; color: var(--landha-brown);
}
.data-table td { padding: 0.875rem 1rem; border-bottom: 1px solid var(--landha-gray-light); font-size: 0.875rem; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: var(--landha-cream); }

.product-cell { display: flex; flex-direction: column; gap: 2px; }
.product-name { font-weight: 500; }
.product-code { font-size: 0.75rem; background: var(--landha-beige); padding: 1px 6px; border-radius: 4px; color: var(--landha-brown); width: fit-content; }
.location-pill { display: inline-block; padding: 3px 10px; background: var(--landha-beige); border-radius: 20px; font-size: 0.8rem; color: var(--landha-brown); font-weight: 500; }

.qty-badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-weight: 600; font-size: 0.875rem; }
.qty-badge.ok { background: #d1fae5; color: var(--landha-success); }
.qty-badge.low { background: #fef3c7; color: var(--landha-warning); }
.qty-badge.zero { background: #fee2e2; color: var(--landha-danger); }

.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; }
.badge-success { background: #d1fae5; color: var(--landha-success); }
.badge-danger { background: #fee2e2; color: var(--landha-danger); }
.badge-warning { background: #fef3c7; color: var(--landha-warning); }

.btn { padding: 0.6rem 1.25rem; border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: background 0.15s; }
.btn-primary { background: var(--landha-brown); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--landha-brown-light); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: var(--landha-gray-light); color: var(--landha-black); }
.btn-icon { background: none; border: 1px solid var(--landha-beige-dark); border-radius: var(--radius-sm); padding: 4px 12px; font-size: 0.8rem; cursor: pointer; color: var(--landha-brown); transition: background 0.1s; }
.btn-icon:hover { background: var(--landha-beige); }

.loading { text-align: center; padding: 3rem; color: var(--landha-gray); }
.empty-state { text-align: center; padding: 2rem; color: var(--landha-gray); font-size: 0.875rem; }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: var(--radius-lg); padding: 2rem; width: 480px; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-lg); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-header h2 { font-size: 1.1rem; font-weight: 600; color: var(--landha-brown); }
.modal-close { background: none; border: none; font-size: 1.25rem; cursor: pointer; color: var(--landha-gray); }
.modal-form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.375rem; }
.field-label { font-size: 0.8rem; font-weight: 500; color: var(--landha-black); }
.field-input { padding: 0.65rem 0.875rem; border: 1.5px solid var(--landha-beige-dark); border-radius: var(--radius-md); font-size: 0.875rem; outline: none; background: var(--landha-cream); width: 100%; }
.field-input:focus { border-color: var(--landha-brown); background: #fff; }
.field-input:disabled { opacity: 0.6; cursor: not-allowed; }

.movement-type-selector { display: flex; gap: 0.5rem; }
.type-btn { flex: 1; padding: 0.65rem; border: 2px solid var(--landha-beige-dark); border-radius: var(--radius-md); background: var(--landha-cream); cursor: pointer; font-size: 0.875rem; font-weight: 500; transition: all 0.15s; }
.type-btn.active-in { border-color: var(--landha-success); background: #d1fae5; color: var(--landha-success); }
.type-btn.active-out { border-color: var(--landha-danger); background: #fee2e2; color: var(--landha-danger); }

.current-stock-info { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; background: var(--landha-cream); border-radius: var(--radius-md); border: 1px solid var(--landha-beige-dark); }
.info-label { font-size: 0.875rem; color: var(--landha-gray); }

.preview-box { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; background: var(--landha-beige); border-radius: var(--radius-md); }
.preview-label { font-size: 0.8rem; color: var(--landha-gray); }
.preview-value { font-size: 0.875rem; color: var(--landha-black); }

.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.5rem; }
.error-alert { padding: 0.75rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: var(--radius-sm); color: var(--landha-danger); font-size: 0.875rem; }
.success-alert { padding: 0.75rem; background: #d1fae5; border: 1px solid #6ee7b7; border-radius: var(--radius-sm); color: var(--landha-success); font-size: 0.875rem; }
</style>