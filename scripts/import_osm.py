#!/usr/bin/env python3
"""One-shot import of gas stations from OpenStreetMap (Overpass API) into PostgreSQL."""
import asyncio
import os
import httpx
import asyncpg
from dotenv import load_dotenv

load_dotenv()

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_HEADERS = {"User-Agent": "fuel-tracker-bot/1.0 (osm import)"}

# Bounding box: Western Russia (lat_min, lon_min, lat_max, lon_max)
BBOX = "47.0,27.0,62.0,55.0"

QUERY = f"""
[out:json][timeout:120];
(
  node["amenity"="fuel"]({BBOX});
  way["amenity"="fuel"]({BBOX});
);
out body center;
"""

async def run():
    db_url = os.environ["DATABASE_URL"]
    pool = await asyncpg.create_pool(db_url)

    print("Fetching stations from Overpass API…")
    mirrors = [
        OVERPASS_URL,
        "https://overpass.openstreetmap.ru/cgi/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]
    async with httpx.AsyncClient(timeout=180, headers=OVERPASS_HEADERS) as http:
        for url in mirrors:
            resp = await http.post(url, data={"data": QUERY})
            if resp.status_code == 200:
                break
            print(f"  {url} returned {resp.status_code}, trying next…")
        resp.raise_for_status()
        elements = resp.json().get("elements", [])

    print(f"Found {len(elements)} stations in OSM")
    imported = skipped = 0

    async with pool.acquire() as conn:
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("brand") or "Заправка"
            brand = tags.get("brand")
            street = tags.get("addr:street", "")
            house = tags.get("addr:housenumber", "")
            address = f"{street}, {house}".strip(", ") or None
            # node → lat/lon directly; way → center.lat/center.lon
            center = el.get("center", {})
            lat = el.get("lat") or center.get("lat")
            lon = el.get("lon") or center.get("lon")
            osm_id = el["id"]
            if lat is None or lon is None:
                skipped += 1
                continue

            try:
                await conn.execute("""
                    INSERT INTO stations (osm_id, name, brand, address, location)
                    VALUES ($1, $2, $3, $4, ST_MakePoint($6, $5)::geography)
                    ON CONFLICT (osm_id) DO NOTHING
                """, osm_id, name, brand, address, lat, lon)
                imported += 1
            except Exception as exc:
                print(f"  Skip osm_id={osm_id}: {exc}")
                skipped += 1

    print(f"Done: imported={imported}, skipped={skipped}")
    await pool.close()

if __name__ == "__main__":
    asyncio.run(run())
