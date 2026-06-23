<!-- frontend/src/App.vue -->
<template>
  <div class="app">
    <FilterBar v-model="fuelType" />
    <MapView :fuel-type="fuelType" @station-click="selected = $event" />
    <StationPopup v-if="selected" :station="selected" @close="selected = null" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FilterBar    from './components/FilterBar.vue'
import MapView      from './components/MapView.vue'
import StationPopup from './components/StationPopup.vue'

const fuelType = ref(null)
const selected = ref(null)
</script>
