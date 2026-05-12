<!-- Ruta: frontend/src/domains/sales/views/SalesView.vue -->
<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Historial de Ventas</h1>
        <p class="text-muted">{{ sales.length }} ventas registradas</p>
      </div>
    </div>

    <!-- Resumen rápido -->
    <div class="summary-cards" v-if="!loading">
      <div class="summary-card">
        <p class="summary-value">{{ sales.length }}</p>
        <p class="summary-label">Total ventas</p>
      </div>
      <div class="summary-card">
        <p class="summary-value">S/ {{ totalVentas.toFixed(2) }}</p>
        <p class="summary-label">Ingresos totales</p>
      </div>
      <div class="summary-card">
        <p class="summary-value">{{ totalUnidades }}</p>
        <p class="summary-label">Unidades vendidas</p>
      </div>
      <div class="summary-card">
        <p class="summary-value">S/ {{ promedioVenta.toFixed(2) }}</p>
        <p class="summary-label">Ticket promedio</p>
      </div>
    </div>

    <div v-if="loading" class="loading">Cargando ventas...</div>

    <div v-else class="sales-list">
      <div v-for="sale in sales" :key="sale.id" class="sale-card">
        <div class="sale-card-header">
          <div class="sale-id-block">
            <span class="sale-id">#{{ sale.id }}</span>
            <span class="sale-date">{{ formatDatePE(sale.created_at) }}</span>
          </div>
          <div class="sale-badges">
            <span class="badge badge-payment">{{ paymentLabel(sale.payment_method) }}</span>
            <span class="badge badge-success">{{ sale.status }}</span>
          </div>
        </div>

        <!-- Detalle de productos -->
        <div class="sale-items">
          <div v-for="detail in sale.details" :key="detail.product_id" class="sale-item-row">
            <span class="item-name">{{ productName(detail.product_id) }}</span>
            <span class="item-qty">{{ detail.quantity }} {{ productUnit(detail.product_id) }}</span>
            <span class="item-price">S/ {{ detail.unit_price.toFixed(2) }} c/u</span>
            <span class="item-subtotal">S/ {{ detail.subtotal.toFixed(2) }}</span>
          </div>
        </div>

        <!-- Totales de la venta -->
        <div class="sale-card-footer">
          <div class="sale-totals">
            <span class="total-detail">
              Op. gravada S/ {{ (sale.total / 1.18).toFixed(2) }} +
              IGV S/ {{ (sale.total - sale.total / 1.18).toFixed(2) }}
            </span>
            <span class="sale-total">Total: S/ {{ sale.total.toFixed(2) }}</span>
          </div>
          <button class="btn-voucher" @click="openVoucher(sale)">
            🧾 Ver comprobante
          </button>
        </div>
      </div>

      <div v-if="sales.length === 0" class="empty-state">
        No hay ventas registradas aún.
      </div>
    </div>

    <!-- Modal comprobante desde historial -->
    <div v-if="showVoucherModal && selectedSale" class="modal-backdrop" @click.self="showVoucherModal = false">
      <div class="voucher-modal">
        <div class="voucher-modal-header">
          <h2>Comprobante — Venta #{{ selectedSale.id }}</h2>
          <button class="modal-close" @click="showVoucherModal = false">✕</button>
        </div>

        <div v-if="loadingVoucher" class="loading">Cargando comprobante...</div>

        <div v-else-if="selectedInvoice" class="voucher-preview">
          <div class="voucher-header">
            <div class="voucher-company">
              <strong>LANDHAAPP</strong>
              <p>Accesorios para muebles y carpintería</p>
            </div>
            <div class="voucher-doc-info">
              <span :class="['voucher-type-badge', selectedInvoice.document_type]">
                {{ selectedInvoice.document_type === 'boleta' ? 'BOLETA DE VENTA' : 'FACTURA' }}
              </span>
              <strong class="voucher-number">{{ selectedInvoice.number }}</strong>
              <p class="voucher-date">{{ formatDatePE(selectedInvoice.issued_at) }}</p>
            </div>
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
              <tr v-for="d in selectedSale.details" :key="d.product_id">
                <td>{{ productName(d.product_id) }}</td>
                <td class="center">{{ d.quantity }}</td>
                <td class="right">S/ {{ d.unit_price.toFixed(2) }}</td>
                <td class="right">S/ {{ d.subtotal.toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>

          <div class="voucher-totals">
            <div class="voucher-total-row">
              <span>Op. gravada</span>
              <span>S/ {{ (selectedSale.total / 1.18).toFixed(2) }}</span>
            </div>
            <div class="voucher-total-row">
              <span>IGV (18%)</span>
              <span>S/ {{ (selectedSale.total - selectedSale.total / 1.18).toFixed(2) }}</span>
            </div>
            <div class="voucher-total-row voucher-grand-total">
              <span>TOTAL</span>
              <span>S/ {{ selectedSale.total.toFixed(2) }}</span>
            </div>
          </div>

          <div class="voucher-payment">
            Forma de pago: <strong>{{ paymentLabel(selectedSale.payment_method) }}</strong>
          </div>
        </div>

        <div v-else class="no-invoice">
          Esta venta no tiene comprobante emitido.
        </div>

        <div class="voucher-actions" v-if="selectedInvoice">
          <button class="btn btn-secondary" @click="printFromHistory(true)">🖨️ Ticket (58mm)</button>
          <button class="btn btn-secondary" @click="printFromHistory(false)">🖨️ Imprimir A4</button>
          <button class="btn btn-primary" @click="downloadFromHistory">⬇️ Descargar PDF</button>
        </div>
      </div>
    </div>

    <iframe id="print-frame-history" style="display:none"></iframe>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '@/core/http'

const sales = ref([])
const products = ref([])
const loading = ref(true)
const showVoucherModal = ref(false)
const selectedSale = ref(null)
const selectedInvoice = ref(null)
const loadingVoucher = ref(false)

onMounted(async () => {
  const [sRes, pRes] = await Promise.all([
    http.get('/sales'),
    http.get('/products?active_only=false'),
  ])
  sales.value = sRes.data
  products.value = pRes.data
  loading.value = false
})

const totalVentas = computed(() => sales.value.reduce((a, s) => a + s.total, 0))
const totalUnidades = computed(() => sales.value.reduce((a, s) => a + s.details.reduce((b, d) => b + d.quantity, 0), 0))
const promedioVenta = computed(() => sales.value.length ? totalVentas.value / sales.value.length : 0)

function productName(id) {
  return products.value.find(p => p.id === id)?.name || `Producto #${id}`
}

function productUnit(id) {
  return products.value.find(p => p.id === id)?.unit || 'uds'
}

function paymentLabel(method) {
  const labels = { cash: 'Efectivo', card: 'Tarjeta', transfer: 'Transferencia', yape: 'Yape/Plin' }
  return labels[method] || method
}

function formatDatePE(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('es-PE', {
    timeZone: 'America/Lima',
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

async function openVoucher(sale) {
  selectedSale.value = sale
  selectedInvoice.value = null
  showVoucherModal.value = true
  loadingVoucher.value = true
  try {
    const { data } = await http.get(`/billing/sale/${sale.id}`)
    selectedInvoice.value = data
  } catch {
    selectedInvoice.value = null
  } finally {
    loadingVoucher.value = false
  }
}

function getHistoryVoucherHTML(forTicket) {
  if (!selectedSale.value || !selectedInvoice.value) return ''
  const sale = selectedSale.value
  const inv = selectedInvoice.value
  const itemsHTML = sale.details.map(d => `
    <tr>
      <td>${productName(d.product_id)}</td>
      <td style="text-align:center">${d.quantity}</td>
      <td style="text-align:right">S/ ${d.unit_price.toFixed(2)}</td>
      <td style="text-align:right">S/ ${d.subtotal.toFixed(2)}</td>
    </tr>
  `).join('')

  const styles = forTicket
    ? `body{font-family:'Courier New',monospace;font-size:11px;width:58mm;margin:0 auto}table{width:100%;border-collapse:collapse;font-size:10px}th,td{padding:2px}.divider{border-top:1px dashed #000;margin:4px 0}`
    : `body{font-family:Arial,sans-serif;font-size:13px;max-width:700px;margin:40px auto;padding:0 20px}table{width:100%;border-collapse:collapse}th{background:#f5efe6;padding:8px;text-align:left}td{padding:8px;border-bottom:1px solid #eee}.divider{border-top:1px solid #ccc;margin:12px 0}`

  const opGravada = (sale.total / 1.18).toFixed(2)
  const igv = (sale.total - sale.total / 1.18).toFixed(2)

  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>${styles}</style></head><body>
  <div style="text-align:center;font-weight:bold;font-size:${forTicket ? '13' : '18'}px">LANDHAAPP</div>
  <p style="text-align:center;margin:2px 0">Accesorios para muebles</p>
  <div class="divider"></div>
  <p style="text-align:center"><strong>${inv.document_type === 'boleta' ? 'BOLETA DE VENTA' : 'FACTURA'}</strong></p>
  <p style="text-align:center"><strong>${inv.number}</strong></p>
  <p style="text-align:center">${formatDatePE(inv.issued_at)}</p>
  <div class="divider"></div>
  <table>
    <thead><tr><th>Descripción</th><th>Cant</th><th>P.U.</th><th>Total</th></tr></thead>
    <tbody>${itemsHTML}</tbody>
  </table>
  <div class="divider"></div>
  <p style="text-align:right">Op. gravada: S/ ${opGravada}</p>
  <p style="text-align:right">IGV (18%): S/ ${igv}</p>
  <p style="text-align:right"><strong>TOTAL: S/ ${sale.total.toFixed(2)}</strong></p>
  <div class="divider"></div>
  <p style="text-align:center">Pago: ${paymentLabel(sale.payment_method)}</p>
  <p style="text-align:center">Gracias por su preferencia</p>
  </body></html>`
}

function printFromHistory(forTicket) {
  const frame = document.getElementById('print-frame-history')
  frame.srcdoc = getHistoryVoucherHTML(forTicket)
  frame.onload = () => frame.contentWindow.print()
}

function downloadFromHistory() {
  const win = window.open('', '_blank')
  win.document.write(getHistoryVoucherHTML(false))
  win.document.close()
  win.onload = () => win.print()
}
</script>

<style scoped>
.page-header { margin-bottom: 1.5rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--landha-brown); }

.summary-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.summary-card { background: #fff; border-radius: var(--radius-lg); padding: 1.25rem; box-shadow: var(--shadow-sm); border-top: 3px solid var(--landha-brown); }
.summary-value { font-size: 1.5rem; font-weight: 700; color: var(--landha-brown); }
.summary-label { font-size: 0.75rem; color: var(--landha-gray); margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }

.sales-list { display: flex; flex-direction: column; gap: 1rem; }
.sale-card { background: #fff; border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden; }
.sale-card-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.25rem; border-bottom: 1px solid var(--landha-gray-light); }
.sale-id-block { display: flex; align-items: center; gap: 0.75rem; }
.sale-id { font-weight: 700; font-size: 1rem; color: var(--landha-brown); }
.sale-date { font-size: 0.8rem; color: var(--landha-gray); }
.sale-badges { display: flex; gap: 0.5rem; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; }
.badge-success { background: #d1fae5; color: var(--landha-success); }
.badge-payment { background: var(--landha-beige); color: var(--landha-brown); }

.sale-items { padding: 0.75rem 1.25rem; display: flex; flex-direction: column; gap: 0.25rem; }
.sale-item-row { display: grid; grid-template-columns: 1fr auto auto auto; gap: 1rem; align-items: center; padding: 0.375rem 0; border-bottom: 1px solid var(--landha-gray-light); font-size: 0.875rem; }
.sale-item-row:last-child { border-bottom: none; }
.item-name { font-weight: 500; }
.item-qty { color: var(--landha-gray); font-size: 0.8rem; }
.item-price { color: var(--landha-gray); font-size: 0.8rem; }
.item-subtotal { font-weight: 600; color: var(--landha-brown); text-align: right; }

.sale-card-footer { display: flex; justify-content: space-between; align-items: center; padding: 0.875rem 1.25rem; background: var(--landha-cream); }
.sale-totals { display: flex; flex-direction: column; gap: 2px; }
.total-detail { font-size: 0.75rem; color: var(--landha-gray); }
.sale-total { font-weight: 700; font-size: 1.05rem; color: var(--landha-brown); }
.btn-voucher { padding: 0.5rem 1rem; background: var(--landha-brown); color: #fff; border: none; border-radius: var(--radius-md); font-size: 0.8rem; cursor: pointer; transition: background 0.15s; }
.btn-voucher:hover { background: var(--landha-brown-light); }

.loading { text-align: center; padding: 3rem; color: var(--landha-gray); }
.empty-state { text-align: center; padding: 3rem; color: var(--landha-gray); background: #fff; border-radius: var(--radius-lg); }
.no-invoice { text-align: center; padding: 2rem; color: var(--landha-gray); }

/* Modal comprobante */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 300; padding: 1rem; }
.voucher-modal { background: #fff; border-radius: var(--radius-lg); width: 600px; max-height: 92vh; overflow-y: auto; box-shadow: var(--shadow-lg); }
.voucher-modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--landha-gray-light); }
.voucher-modal-header h2 { font-size: 1.1rem; font-weight: 600; color: var(--landha-brown); }
.modal-close { background: none; border: none; font-size: 1.25rem; cursor: pointer; color: var(--landha-gray); }

.voucher-preview { margin: 1rem 1.5rem; border: 1.5px solid var(--landha-beige-dark); border-radius: var(--radius-md); padding: 1.25rem; }
.voucher-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--landha-beige-dark); }
.voucher-company strong { font-size: 1.1rem; color: var(--landha-brown); }
.voucher-company p { font-size: 0.75rem; color: var(--landha-gray); margin-top: 2px; }
.voucher-doc-info { text-align: right; }
.voucher-type-badge { display: inline-block; padding: 2px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px; }
.voucher-type-badge.boleta { background: #dbeafe; color: #1e40af; }
.voucher-type-badge.factura { background: #fef3c7; color: #92400e; }
.voucher-number { display: block; font-size: 1rem; color: var(--landha-black); margin-top: 4px; }
.voucher-date { font-size: 0.75rem; color: var(--landha-gray); }
.voucher-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-bottom: 0.75rem; }
.voucher-table th { background: var(--landha-beige); padding: 6px 8px; text-align: left; font-size: 0.75rem; font-weight: 600; color: var(--landha-brown); }
.voucher-table td { padding: 6px 8px; border-bottom: 1px solid var(--landha-gray-light); }
.voucher-table .center { text-align: center; }
.voucher-table .right { text-align: right; }
.voucher-totals { border-top: 1px solid var(--landha-beige-dark); padding-top: 0.5rem; display: flex; flex-direction: column; gap: 0.2rem; }
.voucher-total-row { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--landha-gray); }
.voucher-grand-total { font-weight: 700; font-size: 1rem; color: var(--landha-brown); margin-top: 4px; }
.voucher-payment { font-size: 0.8rem; color: var(--landha-gray); margin-top: 0.75rem; padding-top: 0.5rem; border-top: 1px dashed var(--landha-beige-dark); }

.voucher-actions { display: flex; gap: 0.75rem; padding: 1rem 1.5rem 1.5rem; flex-wrap: wrap; justify-content: flex-end; border-top: 1px solid var(--landha-gray-light); }
.btn { padding: 0.6rem 1.1rem; border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: background 0.15s; }
.btn-primary { background: var(--landha-brown); color: #fff; }
.btn-primary:hover { background: var(--landha-brown-light); }
.btn-secondary { background: var(--landha-gray-light); color: var(--landha-black); }
.btn-secondary:hover { background: var(--landha-beige-dark); }
</style>