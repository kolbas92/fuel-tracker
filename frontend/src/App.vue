<!-- frontend/src/App.vue -->
<template>
  <div class="app">
    <div class="map-placeholder">
      <div class="map-placeholder__inner">
        <span class="map-placeholder__icon">🗺️</span>
        <p class="map-placeholder__title">Карта временно недоступна</p>
        <p class="map-placeholder__sub">Используйте Telegram-бот для поиска заправок</p>
        <a class="map-placeholder__btn" href="https://t.me/zapravka_gde_bot" target="_blank">
          Открыть бот
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: #f5f5f5; }
.app { min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.map-placeholder {
  display: flex; align-items: center; justify-content: center;
  width: 100%; min-height: 100vh; background: #f0f4f8;
}
.map-placeholder__inner {
  text-align: center; padding: 2rem;
  background: #fff; border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  max-width: 360px; width: 90%;
}
.map-placeholder__icon { font-size: 3rem; display: block; margin-bottom: 1rem; }
.map-placeholder__title { font-size: 1.25rem; font-weight: 600; color: #1a1a2e; margin-bottom: 0.5rem; }
.map-placeholder__sub { color: #666; font-size: 0.95rem; margin-bottom: 1.5rem; }
.map-placeholder__btn {
  display: inline-block; padding: 0.75rem 1.5rem;
  background: #229ED9; color: #fff; border-radius: 10px;
  text-decoration: none; font-weight: 600; font-size: 1rem;
  transition: background 0.2s;
}
.map-placeholder__btn:hover { background: #1a8bbf; }
</style>
