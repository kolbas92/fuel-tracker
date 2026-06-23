# tests/test_stations.py
import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio

async def _seed_station(client, name="Лукойл", lat=55.75, lon=37.62):
    r = await client.post("/stations", json={
        "name": name, "brand": "Лукойл",
        "address": "ул. Тестовая, 1",
        "lat": lat, "lon": lon, "added_by": 1
    })
    assert r.status_code == 201
    return r.json()

async def _seed_user(db_pool, telegram_id=1):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (telegram_id, first_name) VALUES ($1, 'Test') ON CONFLICT DO NOTHING",
            telegram_id
        )

async def test_create_station(client, db_pool):
    await _seed_user(db_pool)
    s = await _seed_station(client)
    assert s["name"] == "Лукойл"
    assert abs(s["lat"] - 55.75) < 0.001
    assert "id" in s

async def test_list_stations_in_bbox(client, db_pool):
    await _seed_user(db_pool)
    await _seed_station(client, lat=55.75, lon=37.62)
    r = await client.get("/stations", params={
        "min_lat": 55.0, "min_lon": 37.0,
        "max_lat": 56.0, "max_lon": 38.0
    })
    assert r.status_code == 200
    assert len(r.json()) == 1

async def test_list_stations_outside_bbox_returns_empty(client, db_pool):
    await _seed_user(db_pool)
    await _seed_station(client, lat=55.75, lon=37.62)
    r = await client.get("/stations", params={
        "min_lat": 50.0, "min_lon": 30.0,
        "max_lat": 51.0, "max_lon": 31.0
    })
    assert r.status_code == 200
    assert r.json() == []

async def test_nearby_stations(client, db_pool):
    await _seed_user(db_pool)
    await _seed_station(client, lat=55.75, lon=37.62)
    r = await client.get("/stations/nearby", params={"lat": 55.75, "lon": 37.62, "radius_km": 1.0})
    assert r.status_code == 200
    assert len(r.json()) >= 1

async def test_nearby_with_fuel_type_filter(client, db_pool):
    await _seed_user(db_pool)
    await _seed_station(client, lat=55.75, lon=37.62)
    # No reports = station_status view has no rows for this station
    # So filtering by fuel_type should return empty (no matching status rows)
    r = await client.get("/stations/nearby", params={
        "lat": 55.75, "lon": 37.62, "radius_km": 1.0, "fuel_type": "95"
    })
    assert r.status_code == 200
    # No reports for this station, so fuel_type filter returns empty
    assert r.json() == []

async def test_station_status_not_found(client):
    r = await client.get(f"/stations/{uuid4()}/status")
    assert r.status_code == 404

async def test_station_status_no_reports(client, db_pool):
    await _seed_user(db_pool)
    s = await _seed_station(client)
    r = await client.get(f"/stations/{s['id']}/status")
    assert r.status_code == 200
    assert r.json()["fuel_status"] == []
