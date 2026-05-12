<!-- Ruta: frontend/src/domains/sales/views/NewSaleView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Nueva Venta</h1>
        <p class="text-muted">Registra la venta y genera el comprobante</p>
      </div>
    </div>

    <div class="sale-layout">
      <!-- Panel izquierdo -->
      <div class="sale-panel">

        <!-- Búsqueda de productos -->
        <div class="panel-section">
          <h3 class="section-title">Productos</h3>
          <input v-model="productSearch" type="text" class="field-input"
            placeholder="Buscar por nombre o código..." />
          <div class="product-list">
            <div v-for="product in filteredProducts" :key="product.id"
              class="product-row" @click="addToCart(product)">
              <div>
                <p class="product-name">{{ product.name }}</p>
                <code class="code-tag">{{ product.code }}</code>
              </div>
              <span class="product-price">S/ {{ Number(product.price).toFixed(2) }}</span>
            </div>
            <p v-if="filteredProducts.length === 0" class="empty-hint">Sin resultados.</p>
          </div>
        </div>

        <!-- Ubicación -->
        <div class="panel-section">
          <h3 class="section-title">Ubicación de venta</h3>
          <select v-model="selectedLocation" class="field-input">
            <option v-for="loc in locations" :key="loc.id" :value="loc.id">
              {{ loc.name }}
            </option>
          </select>
        </div>

        <!-- Método de pago -->
        <div class="panel-section">
          <h3 class="section-title">Método de pago</h3>
          <div class="payment-grid">
            <button v-for="m in paymentMethods" :key="m.value"
              :class="['payment-btn', paymentMethod === m.value ? 'active' : '']"
              @click="paymentMethod = m.value">
              {{ m.icon }} {{ m.label }}
            </button>
          </div>
        </div>

        <!-- Cliente -->
        <div class="panel-section">
          <h3 class="section-title">Cliente</h3>

          <div class="customer-mode-tabs">
            <button :class="['tab-btn', customerMode === 'search' ? 'active' : '']"
              @click="customerMode = 'search'">Cliente registrado</button>
            <button :class="['tab-btn', customerMode === 'new' ? 'active' : '']"
              @click="customerMode = 'new'">Datos rápidos</button>
          </div>

          <!-- Buscar cliente existente -->
          <div v-if="customerMode === 'search'" class="customer-search">
            <input v-model="customerSearch" type="text" class="field-input"
              placeholder="Buscar por nombre, DNI o RUC..." />
            <div v-if="filteredCustomers.length > 0" class="customer-dropdown">
              <div v-for="c in filteredCustomers" :key="c.id"
                class="customer-option" @click="selectCustomer(c)">
                <div class="customer-option-main">
                  <span class="customer-option-name">{{ c.name }}</span>
                  <span :class="['doc-badge', c.document_type === 'RUC' ? 'ruc' : 'dni']">
                    {{ c.document_type }}
                  </span>
                </div>
                <span class="customer-option-doc">{{ c.document_number }}</span>
              </div>
            </div>
            <div v-if="selectedCustomer" class="selected-customer">
              <div class="selected-customer-info">
                <strong>{{ selectedCustomer.name }}</strong>
                <span :class="['doc-badge', selectedCustomer.document_type === 'RUC' ? 'ruc' : 'dni']">
                  {{ selectedCustomer.document_type }}
                </span>
                <span class="doc-number">{{ selectedCustomer.document_number }}</span>
                <span v-if="selectedCustomer.business_name" class="business-name">
                  {{ selectedCustomer.business_name }}
                </span>
              </div>
              <button class="clear-btn" @click="clearCustomer">✕</button>
            </div>
          </div>

          <!-- Datos rápidos (cliente nuevo sin registrar) -->
          <div v-if="customerMode === 'new'" class="quick-customer">
            <div class="field-grid">
              <div class="field">
                <label class="field-label">Tipo</label>
                <select v-model="quickCustomer.document_type" class="field-input">
                  <option value="DNI">DNI</option>
                  <option value="RUC">RUC</option>
                </select>
              </div>
              <div class="field">
                <label class="field-label">Nro. documento</label>
                <input v-model="quickCustomer.document_number" type="text" class="field-input" />
              </div>
            </div>
            <div class="field">
              <label class="field-label">Nombre / Razón social</label>
              <input v-model="quickCustomer.name" type="text" class="field-input"
                placeholder="Nombre del cliente" />
            </div>
          </div>
        </div>
      </div>

      <!-- Panel derecho: carrito y comprobante -->
      <div class="cart-panel">
        <h3 class="section-title">Detalle de venta</h3>

        <div class="cart-items">
          <div v-for="(item, idx) in cart" :key="idx" class="cart-item">
            <div class="cart-item-info">
              <p class="cart-item-name">{{ item.name }}</p>
              <p class="cart-item-code">{{ item.code }}</p>
            </div>
            <div class="cart-item-controls">
              <button class="qty-btn" @click="decreaseQty(idx)">−</button>
              <span class="qty-value">{{ item.quantity }}</span>
              <button class="qty-btn" @click="increaseQty(idx)">+</button>
            </div>
            <div class="cart-item-right">
              <span class="cart-item-price">S/ {{ (item.unit_price * item.quantity).toFixed(2) }}</span>
              <button class="remove-btn" @click="removeFromCart(idx)">✕</button>
            </div>
          </div>
          <p v-if="cart.length === 0" class="empty-hint">Selecciona productos del panel izquierdo.</p>
        </div>

        <!-- Totales -->
        <div class="cart-totals">
          <div class="total-row">
            <span>Subtotal (sin IGV)</span>
            <span>S/ {{ subtotalSinIgv.toFixed(2) }}</span>
          </div>
          <div class="total-row">
            <span>IGV (18%)</span>
            <span>S/ {{ igv.toFixed(2) }}</span>
          </div>
          <div class="total-row total-final">
            <span>Total</span>
            <span>S/ {{ total.toFixed(2) }}</span>
          </div>
        </div>

        <!-- Tipo de comprobante -->
        <div class="voucher-section">
          <h3 class="section-title">Comprobante</h3>
          <div class="doc-type-selector">
            <button :class="['doc-btn', docType === 'boleta' ? 'active' : '']"
              @click="docType = 'boleta'">
              📄 Boleta
            </button>
            <button :class="['doc-btn', docType === 'factura' ? 'active' : '']"
              @click="docType = 'factura'">
              🧾 Factura
            </button>
          </div>

          <!-- Aviso factura sin RUC -->
          <div v-if="docType === 'factura' && !customerHasRuc" class="warning-alert">
            ⚠️ Para factura necesitas seleccionar un cliente con RUC.
          </div>
        </div>

        <div v-if="saleError" class="error-alert">{{ saleError }}</div>

        <button class="btn btn-primary w-full btn-lg"
          :disabled="cart.length === 0 || saving || (docType === 'factura' && !customerHasRuc)"
          @click="handleSale">
          {{ saving ? 'Procesando...' : `Registrar venta · S/ ${total.toFixed(2)}` }}
        </button>
      </div>
    </div>

    <!-- ─── Modal comprobante ─────────────────────────────────── -->
    <div v-if="showVoucherModal" class="modal-backdrop">
      <div class="voucher-modal">
        <div class="voucher-modal-header">
          <h2>✅ Venta registrada</h2>
          <p class="text-muted">Comprobante generado correctamente</p>
        </div>

        <!-- Preview del comprobante -->
        <div class="voucher-preview" id="voucher-print">
          <div class="voucher-header">
            <div class="voucher-company">
              <strong>LANDHAAPP</strong>
              <p>Accesorios para muebles y carpintería</p>
            </div>
            <div class="voucher-doc-info">
              <span :class="['voucher-type-badge', lastInvoice.document_type]">
                {{ lastInvoice.document_type === 'boleta' ? 'BOLETA DE VENTA' : 'FACTURA' }}
              </span>
              <strong class="voucher-number">{{ lastInvoice.number }}</strong>
              <p class="voucher-date">{{ formatDatePE(lastInvoice.issued_at) }}</p>
            </div>
          </div>

          <div class="voucher-customer" v-if="lastSaleCustomer">
            <p><strong>Cliente:</strong> {{ lastSaleCustomer.name }}</p>
            <p v-if="lastSaleCustomer.document_type">
              <strong>{{ lastSaleCustomer.document_type }}:</strong> {{ lastSaleCustomer.document_number }}
            </p>
            <p v-if="lastSaleCustomer.business_name">
              <strong>Razón social:</strong> {{ lastSaleCustomer.business_name }}
            </p>
          </div>

          <table class="voucher-table">
            <thead>
              <tr>
                <th>Descripción</th>
                <th>Cant.</th>
                <th>P. Unit.</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in lastCart" :key="item.product_id">
                <td>{{ item.name }}</td>
                <td class="center">{{ item.quantity }}</td>
                <td class="right">S/ {{ item.unit_price.toFixed(2) }}</td>
                <td class="right">S/ {{ (item.unit_price * item.quantity).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>

          <div class="voucher-totals">
            <div class="voucher-total-row">
              <span>Op. gravada</span>
              <span>S/ {{ lastSaleTotals.subtotal.toFixed(2) }}</span>
            </div>
            <div class="voucher-total-row">
              <span>IGV (18%)</span>
              <span>S/ {{ lastSaleTotals.tax.toFixed(2) }}</span>
            </div>
            <div class="voucher-total-row voucher-grand-total">
              <span>TOTAL</span>
              <span>S/ {{ lastSaleTotals.total.toFixed(2) }}</span>
            </div>
          </div>

          <div class="voucher-payment">
            Forma de pago: <strong>{{ paymentLabel(lastSaleTotals.payment_method) }}</strong>
          </div>

          <div class="voucher-footer">
            <p>Gracias por su preferencia</p>
            <p class="small">LandhaApp — Sistema de gestión de ventas</p>
          </div>
        </div>

        <!-- Acciones -->
        <div class="voucher-actions">
          <button class="btn btn-secondary" @click="printTicket">
            🖨️ Imprimir ticket (58mm)
          </button>
          <button class="btn btn-secondary" @click="printA4">
            🖨️ Imprimir A4
          </button>
          <button class="btn btn-primary" @click="downloadPDF">
            ⬇️ Descargar PDF
          </button>
          <button class="btn btn-ghost" @click="closeVoucherModal">
            Cerrar
          </button>
        </div>
      </div>
    </div>

    <!-- Iframe oculto para impresión ticket -->
    <iframe id="print-frame" style="display:none"></iframe>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '@/core/http'

const products = ref([])
const locations = ref([])
const customers = ref([])
const cart = ref([])
const productSearch = ref('')
const customerSearch = ref('')
const selectedLocation = ref(null)
const paymentMethod = ref('cash')
const docType = ref('boleta')
const saving = ref(false)
const saleError = ref('')
const showVoucherModal = ref(false)
const customerMode = ref('search')
const selectedCustomer = ref(null)
const quickCustomer = ref({ document_type: 'DNI', document_number: '', name: '' })

const lastInvoice = ref({})
const lastCart = ref([])
const lastSaleTotals = ref({ subtotal: 0, tax: 0, total: 0, payment_method: 'cash' })
const lastSaleCustomer = ref(null)

const paymentMethods = [
  { value: 'cash', label: 'Efectivo', icon: '💵' },
  { value: 'card', label: 'Tarjeta', icon: '💳' },
  { value: 'transfer', label: 'Transferencia', icon: '🏦' },
  { value: 'yape', label: 'Yape/Plin', icon: '📱' },
]

onMounted(async () => {
  const [prodRes, locRes, custRes] = await Promise.all([
    http.get('/products'),
    http.get('/inventory/locations'),
    http.get('/customers'),
  ])
  products.value = prodRes.data
  locations.value = locRes.data
  customers.value = custRes.data
  if (locations.value.length) selectedLocation.value = locations.value[0].id
})

const filteredProducts = computed(() => {
  const s = productSearch.value.toLowerCase()
  if (!s) return products.value
  return products.value.filter(p =>
    p.name.toLowerCase().includes(s) || p.code.toLowerCase().includes(s)
  )
})

const filteredCustomers = computed(() => {
  const s = customerSearch.value.toLowerCase()
  if (!s || selectedCustomer.value) return []
  return customers.value.filter(c =>
    c.name.toLowerCase().includes(s) ||
    (c.document_number || '').includes(s)
  ).slice(0, 6)
})

const customerHasRuc = computed(() => {
  if (selectedCustomer.value) return selectedCustomer.value.document_type === 'RUC'
  if (customerMode.value === 'new') return quickCustomer.value.document_type === 'RUC'
  return false
})

// Precio ingresado incluye IGV — separamos para mostrar desglose
const total = computed(() => cart.value.reduce((acc, i) => acc + i.unit_price * i.quantity, 0))
const subtotalSinIgv = computed(() => total.value / 1.18)
const igv = computed(() => total.value - subtotalSinIgv.value)

function addToCart(product) {
  const existing = cart.value.find(i => i.product_id === product.id)
  if (existing) { existing.quantity++ }
  else {
    cart.value.push({
      product_id: product.id,
      name: product.name,
      code: product.code,
      unit_price: Number(product.price),
      quantity: 1,
    })
  }
}

function increaseQty(idx) { cart.value[idx].quantity++ }
function decreaseQty(idx) {
  if (cart.value[idx].quantity > 1) cart.value[idx].quantity--
  else removeFromCart(idx)
}
function removeFromCart(idx) { cart.value.splice(idx, 1) }

function selectCustomer(c) {
  selectedCustomer.value = c
  customerSearch.value = ''
}

function clearCustomer() {
  selectedCustomer.value = null
  customerSearch.value = ''
}

function paymentLabel(method) {
  const m = paymentMethods.find(p => p.value === method)
  return m ? m.label : method
}

function formatDatePE(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('es-PE', {
    timeZone: 'America/Lima',
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

async function handleSale() {
  saleError.value = ''
  saving.value = true

  try {
    // Resolver customer_id
    let customerId = null
    if (customerMode.value === 'search' && selectedCustomer.value) {
      customerId = selectedCustomer.value.id
    } else if (customerMode.value === 'new' && quickCustomer.value.name) {
      // Registrar cliente rápido
      const { data } = await http.post('/customers', {
        name: quickCustomer.value.name,
        document_type: quickCustomer.value.document_type,
        document_number: quickCustomer.value.document_number,
      })
      customerId = data.id
      customers.value.push(data)
    }

    // Registrar venta — precios ya incluyen IGV
    const saleRes = await http.post('/sales', {
      location_id: selectedLocation.value,
      items: cart.value.map(i => ({
        product_id: i.product_id,
        quantity: i.quantity,
        unit_price: i.unit_price,
      })),
      payment_method: paymentMethod.value,
      customer_id: customerId,
    })

    // Emitir comprobante
    const invRes = await http.post('/billing/issue', {
      sale_id: saleRes.data.sale_id,
      document_type: docType.value,
    })

    // Guardar datos para modal
    lastInvoice.value = invRes.data
    lastCart.value = [...cart.value]
    lastSaleTotals.value = {
      subtotal: subtotalSinIgv.value,
      tax: igv.value,
      total: total.value,
      payment_method: paymentMethod.value,
    }
    lastSaleCustomer.value = selectedCustomer.value || (
      quickCustomer.value.name ? { ...quickCustomer.value } : null
    )

    // Limpiar formulario
    cart.value = []
    selectedCustomer.value = null
    customerSearch.value = ''
    quickCustomer.value = { document_type: 'DNI', document_number: '', name: '' }
    showVoucherModal.value = true

  } catch (e) {
    saleError.value = e.response?.data?.error || 'Error al registrar la venta.'
  } finally {
    saving.value = false
  }
}

function closeVoucherModal() {
  showVoucherModal.value = false
}

function getVoucherHTML(forTicket = false) {
  const customer = lastSaleCustomer.value
  const itemsHTML = lastCart.value.map(i => `
    <tr>
      <td>${i.name}</td>
      <td style="text-align:center">${i.quantity}</td>
      <td style="text-align:right">S/ ${i.unit_price.toFixed(2)}</td>
      <td style="text-align:right">S/ ${(i.unit_price * i.quantity).toFixed(2)}</td>
    </tr>
  `).join('')

  const ticketStyles = forTicket ? `
    body { font-family: 'Courier New', monospace; font-size: 11px; width: 58mm; margin: 0 auto; }
    table { width: 100%; border-collapse: collapse; font-size: 10px; }
    th, td { padding: 2px; }
    .company { font-size: 13px; font-weight: bold; text-align: center; }
    .divider { border-top: 1px dashed #000; margin: 4px 0; }
  ` : `
    body { font-family: Arial, sans-serif; font-size: 13px; max-width: 700px; margin: 40px auto; padding: 0 20px; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #f5efe6; padding: 8px; text-align: left; }
    td { padding: 8px; border-bottom: 1px solid #eee; }
    .company { font-size: 18px; font-weight: bold; }
    .divider { border-top: 1px solid #ccc; margin: 12px 0; }
  `

  return `<!DOCTYPE html><html><head><meta charset="UTF-8">
  <style>${ticketStyles}</style></head><body>
  <div class="company">LANDHAAPP</div>
  <p style="text-align:center;margin:2px 0">Accesorios para muebles</p>
  <div class="divider"></div>
  <p style="text-align:center"><strong>${lastInvoice.value.document_type === 'boleta' ? 'BOLETA DE VENTA' : 'FACTURA'}</strong></p>
  <p style="text-align:center"><strong>${lastInvoice.value.number}</strong></p>
  <p style="text-align:center">${formatDatePE(lastInvoice.value.issued_at)}</p>
  <div class="divider"></div>
  ${customer ? `<p><strong>${customer.document_type}:</strong> ${customer.document_number || ''}</p>
  <p><strong>Cliente:</strong> ${customer.name}</p>
  ${customer.business_name ? `<p><strong>Razón social:</strong> ${customer.business_name}</p>` : ''}
  <div class="divider"></div>` : ''}
  <table>
    <thead><tr><th>Descripción</th><th>Cant</th><th>P.U.</th><th>Total</th></tr></thead>
    <tbody>${itemsHTML}</tbody>
  </table>
  <div class="divider"></div>
  <p style="text-align:right">Op. gravada: S/ ${lastSaleTotals.value.subtotal.toFixed(2)}</p>
  <p style="text-align:right">IGV (18%): S/ ${lastSaleTotals.value.tax.toFixed(2)}</p>
  <p style="text-align:right"><strong>TOTAL: S/ ${lastSaleTotals.value.total.toFixed(2)}</strong></p>
  <div class="divider"></div>
  <p style="text-align:center">Pago: ${paymentLabel(lastSaleTotals.value.payment_method)}</p>
  <p style="text-align:center">Gracias por su preferencia</p>
  </body></html>`
}

function printA4() {
  const frame = document.getElementById('print-frame')
  frame.srcdoc = getVoucherHTML(false)
  frame.onload = () => { frame.contentWindow.print() }
}

function printTicket() {
  const frame = document.getElementById('print-frame')
  frame.srcdoc = getVoucherHTML(true)
  frame.onload = () => { frame.contentWindow.print() }
}

async function downloadPDF() {
  // Usa el API de impresión del navegador guardando como PDF
  const win = window.open('', '_blank')
  win.document.write(getVoucherHTML(false))
  win.document.close()
  win.onload = () => { win.print() }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--landha-brown); }

.sale-layout { display: grid; grid-template-columns: 1fr 420px; gap: 1.5rem; align-items: start; }

.sale-panel { display: flex; flex-direction: column; gap: 1rem; }
.panel-section { background: #fff; border-radius: var(--radius-lg); padding: 1.25rem; box-shadow: var(--shadow-sm); }
.section-title { font-size: 0.75rem; font-weight: 600; color: var(--landha-brown); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.8px; }

.product-list { max-height: 260px; overflow-y: auto; margin-top: 0.75rem; }
.product-row { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0.5rem; border-radius: var(--radius-sm); cursor: pointer; transition: background 0.1s; }
.product-row:hover { background: var(--landha-beige); }
.product-name { font-size: 0.875rem; font-weight: 500; }
.product-price { font-weight: 600; color: var(--landha-brown); font-size: 0.875rem; white-space: nowrap; }

.payment-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
.payment-btn { padding: 0.6rem; border: 1.5px solid var(--landha-beige-dark); border-radius: var(--radius-md); background: var(--landha-cream); cursor: pointer; font-size: 0.8rem; transition: all 0.15s; }
.payment-btn.active { border-color: var(--landha-brown); background: var(--landha-brown); color: #fff; font-weight: 600; }

/* Customer */
.customer-mode-tabs { display: flex; gap: 0.25rem; margin-bottom: 0.75rem; background: var(--landha-gray-light); border-radius: var(--radius-md); padding: 3px; }
.tab-btn { flex: 1; padding: 0.4rem 0.5rem; border: none; border-radius: var(--radius-sm); background: transparent; font-size: 0.8rem; cursor: pointer; color: var(--landha-gray); transition: all 0.15s; }
.tab-btn.active { background: #fff; color: var(--landha-brown); font-weight: 600; box-shadow: var(--shadow-sm); }

.customer-search { position: relative; }
.customer-dropdown { position: absolute; z-index: 50; width: 100%; background: #fff; border: 1.5px solid var(--landha-beige-dark); border-radius: var(--radius-md); box-shadow: var(--shadow-md); margin-top: 4px; max-height: 220px; overflow-y: auto; }
.customer-option { padding: 0.6rem 0.875rem; cursor: pointer; transition: background 0.1s; border-bottom: 1px solid var(--landha-gray-light); }
.customer-option:last-child { border-bottom: none; }
.customer-option:hover { background: var(--landha-beige); }
.customer-option-main { display: flex; align-items: center; gap: 0.5rem; }
.customer-option-name { font-size: 0.875rem; font-weight: 500; }
.customer-option-doc { font-size: 0.75rem; color: var(--landha-gray); }

.doc-badge { display: inline-block; padding: 1px 7px; border-radius: 10px; font-size: 0.7rem; font-weight: 700; }
.doc-badge.dni { background: #dbeafe; color: #1d4ed8; }
.doc-badge.ruc { background: #fef3c7; color: #92400e; }

.selected-customer { display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 0.875rem; background: var(--landha-beige); border-radius: var(--radius-md); margin-top: 0.5rem; }
.selected-customer-info { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; font-size: 0.875rem; }
.doc-number { color: var(--landha-gray); font-size: 0.8rem; }
.business-name { color: var(--landha-gray); font-size: 0.8rem; font-style: italic; }
.clear-btn { background: none; border: none; color: var(--landha-gray); cursor: pointer; font-size: 1rem; padding: 4px; }

.quick-customer { display: flex; flex-direction: column; gap: 0.75rem; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; }
.field-label { font-size: 0.75rem; font-weight: 500; color: var(--landha-black); }

/* Cart */
.cart-panel { background: #fff; border-radius: var(--radius-lg); padding: 1.5rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1rem; position: sticky; top: 1rem; }
.cart-items { display: flex; flex-direction: column; gap: 0.25rem; min-height: 80px; max-height: 300px; overflow-y: auto; }
.cart-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0; border-bottom: 1px solid var(--landha-gray-light); }
.cart-item-info { flex: 1; min-width: 0; }
.cart-item-name { font-size: 0.875rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cart-item-code { font-size: 0.7rem; color: var(--landha-gray); }
.cart-item-controls { display: flex; align-items: center; gap: 4px; }
.qty-btn { width: 24px; height: 24px; border-radius: 4px; border: 1px solid var(--landha-beige-dark); background: var(--landha-cream); cursor: pointer; font-size: 1rem; display: flex; align-items: center; justify-content: center; line-height: 1; }
.qty-value { min-width: 24px; text-align: center; font-size: 0.875rem; font-weight: 600; }
.cart-item-right { display: flex; align-items: center; gap: 4px; }
.cart-item-price { min-width: 70px; text-align: right; font-size: 0.875rem; font-weight: 600; color: var(--landha-brown); }
.remove-btn { background: none; border: none; color: var(--landha-gray); cursor: pointer; font-size: 0.8rem; padding: 2px 4px; }

.cart-totals { border-top: 2px solid var(--landha-beige-dark); padding-top: 0.75rem; display: flex; flex-direction: column; gap: 0.3rem; }
.total-row { display: flex; justify-content: space-between; font-size: 0.875rem; color: var(--landha-gray); }
.total-final { font-weight: 700; font-size: 1.1rem; color: var(--landha-brown); margin-top: 0.25rem; }

.voucher-section { border-top: 1px solid var(--landha-gray-light); padding-top: 1rem; }
.doc-type-selector { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; }
.doc-btn { flex: 1; padding: 0.65rem; border: 2px solid var(--landha-beige-dark); border-radius: var(--radius-md); background: var(--landha-cream); cursor: pointer; font-size: 0.875rem; transition: all 0.15s; }
.doc-btn.active { border-color: var(--landha-brown); background: var(--landha-brown); color: #fff; font-weight: 600; }

.btn { padding: 0.65rem 1.25rem; border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: background 0.15s; }
.btn-primary { background: var(--landha-brown); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--landha-brown-light); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: var(--landha-gray-light); color: var(--landha-black); }
.btn-secondary:hover { background: var(--landha-beige-dark); }
.btn-ghost { background: transparent; color: var(--landha-gray); text-decoration: underline; }
.btn-lg { padding: 0.875rem; font-size: 1rem; }
.w-full { width: 100%; }

.error-alert { padding: 0.75rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: var(--radius-sm); color: var(--landha-danger); font-size: 0.875rem; }
.warning-alert { padding: 0.6rem 0.875rem; background: #fef3c7; border: 1px solid #fcd34d; border-radius: var(--radius-sm); color: #92400e; font-size: 0.8rem; }

.code-tag { font-size: 0.75rem; background: var(--landha-beige); padding: 1px 6px; border-radius: 4px; color: var(--landha-brown); }
.empty-hint { text-align: center; color: var(--landha-gray); font-size: 0.875rem; padding: 1rem 0; }

/* ── Modal comprobante ── */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 300; padding: 1rem; }
.voucher-modal { background: #fff; border-radius: var(--radius-lg); width: 600px; max-height: 92vh; overflow-y: auto; box-shadow: var(--shadow-lg); display: flex; flex-direction: column; }
.voucher-modal-header { padding: 1.5rem 1.5rem 0; }
.voucher-modal-header h2 { font-size: 1.2rem; font-weight: 700; color: var(--landha-success); }

/* Preview comprobante */
.voucher-preview { margin: 1rem 1.5rem; border: 1.5px solid var(--landha-beige-dark); border-radius: var(--radius-md); padding: 1.25rem; }
.voucher-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--landha-beige-dark); }
.voucher-company strong { font-size: 1.1rem; color: var(--landha-brown); }
.voucher-company p { font-size: 0.75rem; color: var(--landha-gray); margin-top: 2px; }
.voucher-doc-info { text-align: right; }
.voucher-type-badge { display: inline-block; padding: 2px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px; }
.voucher-type-badge.boleta { background: #dbeafe; color: #1e40af; }
.voucher-type-badge.factura { background: #fef3c7; color: #92400e; }
.voucher-number { display: block; font-size: 1rem; color: var(--landha-black); margin-top: 4px; }
.voucher-date { font-size: 0.75rem; color: var(--landha-gray); margin-top: 2px; }
.voucher-customer { background: var(--landha-cream); padding: 0.75rem; border-radius: var(--radius-sm); margin-bottom: 0.75rem; font-size: 0.875rem; }
.voucher-customer p { margin: 2px 0; }
.voucher-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-bottom: 0.75rem; }
.voucher-table th { background: var(--landha-beige); padding: 6px 8px; text-align: left; font-size: 0.75rem; font-weight: 600; color: var(--landha-brown); }
.voucher-table td { padding: 6px 8px; border-bottom: 1px solid var(--landha-gray-light); }
.voucher-table .center { text-align: center; }
.voucher-table .right { text-align: right; }
.voucher-totals { border-top: 1px solid var(--landha-beige-dark); padding-top: 0.5rem; display: flex; flex-direction: column; gap: 0.2rem; }
.voucher-total-row { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--landha-gray); }
.voucher-grand-total { font-weight: 700; font-size: 1rem; color: var(--landha-brown); margin-top: 4px; }
.voucher-payment { font-size: 0.8rem; color: var(--landha-gray); margin-top: 0.75rem; padding-top: 0.5rem; border-top: 1px dashed var(--landha-beige-dark); }
.voucher-footer { text-align: center; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px dashed var(--landha-beige-dark); }
.voucher-footer p { font-size: 0.8rem; color: var(--landha-gray); margin: 2px 0; }
.voucher-footer .small { font-size: 0.7rem; }

.voucher-actions { display: flex; gap: 0.75rem; padding: 1rem 1.5rem 1.5rem; flex-wrap: wrap; justify-content: flex-end; border-top: 1px solid var(--landha-gray-light); }
</style>