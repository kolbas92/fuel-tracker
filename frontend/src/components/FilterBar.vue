<!-- frontend/src/components/FilterBar.vue -->
<template>
  <div class="filter-bar">
    <button
      v-for="[code, label] in FUELS"
      :key="code"
      :class="['btn', { active: modelValue === code }]"
      @click="$emit('update:modelValue', modelValue === code ? null : code)"
    >{{ label }}</button>
  </div>
</template>

<script setup>
defineProps({ modelValue: String })
defineEmits(['update:modelValue'])

const FUELS = [['92','АИ-92'], ['95','АИ-95'], ['98','АИ-98'], ['dt','ДТ'], ['gas','Газ']]
</script>

<style scoped>
.filter-bar {
  position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 6px; z-index: 1000;
  background: #1e293b; padding: 8px 12px; border-radius: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.4);
}
.btn {
  padding: 4px 12px; border-radius: 16px; border: 1px solid #334155;
  background: transparent; color: #94a3b8; font-size: 13px; cursor: pointer;
  transition: all .15s;
}
.btn.active, .btn:hover { background: #334155; color: #e2e8f0; }
</style>
