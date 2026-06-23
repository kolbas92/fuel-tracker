import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_HEADERS = {"User-Agent": "fuel-tracker-bot/1.0 (geocode)"}

async def geocode(query: str) -> tuple[float, float] | None:
    async with httpx.AsyncClient(headers=_HEADERS, timeout=10) as client:
        resp = await client.get(NOMINATIM_URL, params={
            "q": query,
            "format": "json",
            "limit": 1,
            "countrycodes": "ru",
        })
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        return float(results[0]["lat"]), float(results[0]["lon"])
