// frontend/src/api.js
const BASE = import.meta.env.VITE_API_URL ?? '/api'

async function get(path, params = {}) {
  const url = new URL(BASE + path, location.origin)
  Object.entries(params).forEach(([k, v]) => v != null && url.searchParams.set(k, v))
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${res.status} ${path}`)
  return res.json()
}

export const getStations = (bounds) => get('/stations', {
  min_lat: bounds.getSouth(), min_lon: bounds.getWest(),
  max_lat: bounds.getNorth(), max_lon: bounds.getEast(),
})

export const getStationStatus = (id) => get(`/stations/${id}/status`)
