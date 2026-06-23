<!-- frontend/src/components/MapView.vue -->
<template>
  <div ref="mapEl" class="map"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import L from 'leaflet'
import { getStations } from '../api.js'

defineProps({ fuelType: String })
const emit = defineEmits(['station-click'])
const mapEl = ref(null)

const COLORS = { true: '#22c55e', false: '#ef4444', null: '#94a3b8' }

let map = null
const loaded = new Set()
const markerMap = {}

function makeIcon(color) {
  return L.divIcon({
    html: `<div style="width:14px;height:14px;border-radius:50%;background:${color};border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.5)"></div>`,
    className: '',
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  })
}

async function loadVisible() {
  if (!map) return
  try {
    const stations = await getStations(map.getBounds())
    for (const s of stations) {
      if (loaded.has(s.id)) continue
      loaded.add(s.id)
      const m = L.marker([s.lat, s.lon], { icon: makeIcon(COLORS[null]) })
        .addTo(map)
        .on('click', () => emit('station-click', s))
      markerMap[s.id] = m
    }
  } catch (e) {
    console.error('loadVisible', e)
  }
}

onMounted(() => {
  map = L.map(mapEl.value, { preferCanvas: true })
    .setView([55.75, 37.62], 9)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19,
  }).addTo(map)

  map.on('moveend', loadVisible)
  loadVisible()
})
</script>

<style scoped>
.map { width: 100%; height: 100vh; }
</style>
