# bot/client.py
import httpx
from bot.config import settings

_HEADERS = {"X-API-Key": settings.api_key}

async def get_nearby(lat: float, lon: float, *, fuel_type: str = None, radius_km: float = 5.0) -> list[dict]:
    params = {"lat": lat, "lon": lon, "radius_km": radius_km}
    if fuel_type:
        params["fuel_type"] = fuel_type
    async with httpx.AsyncClient(timeout=10) as http:
        r = await http.get(f"{settings.api_url}/stations/nearby", params=params)
        r.raise_for_status()
        return r.json()

async def get_station_status(station_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as http:
        r = await http.get(f"{settings.api_url}/stations/{station_id}/status")
        r.raise_for_status()
        return r.json()

async def create_report(*, station_id: str, user_id: int, has_fuel: bool,
                         fuel_type: str, price: float = None) -> dict:
    async with httpx.AsyncClient(timeout=10) as http:
        r = await http.post(
            f"{settings.api_url}/reports",
            json={"station_id": station_id, "user_id": user_id,
                  "has_fuel": has_fuel, "fuel_type": fuel_type, "price": price},
            headers=_HEADERS,
        )
        r.raise_for_status()
        return r.json()
