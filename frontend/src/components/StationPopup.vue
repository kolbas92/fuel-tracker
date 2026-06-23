<!-- frontend/src/components/StationPopup.vue -->
<template>
  <div class="popup" v-if="station">
    <button class="close" @click="$emit('close')">✕</button>
    <h3>{{ station.name }}</h3>
    <p class="meta">{{ [station.brand, station.address].filter(Boolean).join(' · ') }}</p>

    <div v-if="loading" class="loading">Загружаю…</div>
    <div v-else-if="status">
      <div v-if="status.fuel_status.length === 0" class="no-data">Нет репортов за 24ч</div>
      <div v-for="f in status.fuel_status" :key="f.fuel_type" class="fuel-row">
        <span class="dot" :style="{ background: dotColor(f.has_fuel) }"></span>
        <span class="type">{{ LABELS[f.fuel_type] }}</span>
        <span class="price">{{ f.median_price != null ? f.median_price.toFixed(2) + ' ₽' : '—' }}</span>
        <span class="time">{{ ago(f.last_report) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getStationStatus } from '../api.js'

const props = defineProps({ station: Object })
defineEmits(['close'])

const status = ref(null)
const loading = ref(false)

const LABELS = { '92': 'АИ-92', '95': 'АИ-95', '98': 'АИ-98', dt: 'ДТ', gas: 'Газ' }

const dotColor = (v) => v === true ? '#22c55e' : v === false ? '#ef4444' : '#94a3b8'

function ago(ts) {
  if (!ts) return ''
  const m = Math.round((Date.now() - new Date(ts)) / 60000)
  return m < 60 ? `${m}м` : `${Math.round(m / 60)}ч`
}

watch(() => props.station, async (s) => {
  if (!s) { status.value = null; return }
  loading.value = true
  try { status.value = await getStationStatus(s.id) }
  finally { loading.value = false }
}, { immediate: true })
</script>

<style scoped>
.popup {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  background: #1e293b; border-radius: 12px; padding: 16px 20px;
  min-width: 260px; max-width: 340px; z-index: 1000;
  box-shadow: 0 4px 24px rgba(0,0,0,.5);
}
.close { position: absolute; top: 10px; right: 12px; background: none; border: none;
         color: #94a3b8; font-size: 16px; cursor: pointer; }
h3 { font-size: 16px; margin-bottom: 4px; }
.meta { font-size: 12px; color: #64748b; margin-bottom: 12px; }
.fuel-row { display: flex; align-items: center; gap: 8px; padding: 4px 0;
            border-bottom: 1px solid #334155; font-size: 13px; }
.dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.type { flex: 1; font-weight: 600; }
.price { color: #a3e635; font-weight: 700; }
.time { font-size: 11px; color: #64748b; }
.loading, .no-data { color: #64748b; font-size: 13px; text-align: center; padding: 8px 0; }
</style>
