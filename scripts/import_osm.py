#!/usr/bin/env python3
"""One-shot import of gas stations from OpenStreetMap (Overpass API) into PostgreSQL."""
import asyncio
import os
import httpx
import asyncpg
from dotenv import load_dotenv

load_dotenv()

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Bounding box: Western Russia (lat_min, lon_min, lat_max, lon_max)
BBOX = "47.0,27.0,62.0,55.0"

QUERY = f"""
[out:json][timeout:90];
node["amenity"="fuel"]({BBOX});
out body;
"""

async def run():
    db_url = os.environ["DATABASE_URL"]
    pool = await asyncpg.create_pool(db_url)

    print("Fetching stations from Overpass API…")
    async with httpx.AsyncClient(timeout=120) as http:
        resp = await http.post(OVERPASS_URL, data={"data": QUERY})
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
            lat, lon, osm_id = el["lat"], el["lon"], el["id"]

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
