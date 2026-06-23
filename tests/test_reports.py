# tests/test_reports.py
import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio

async def _seed_station_and_user(db_pool, client):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (telegram_id, first_name) VALUES (42, 'Тест') ON CONFLICT DO NOTHING"
        )
        row = await conn.fetchrow("""
            INSERT INTO stations (name, location, added_by)
            VALUES ('Лукойл', ST_MakePoint(37.62, 55.75)::geography, 42)
            RETURNING id
        """)
    return str(row["id"])

async def test_create_report_fuel_present(client, db_pool):
    station_id = await _seed_station_and_user(db_pool, client)
    r = await client.post("/reports", json={
        "station_id": station_id,
        "user_id": 42,
        "has_fuel": True,
        "fuel_type": "95",
        "price": 54.20
    })
    assert r.status_code == 201
    assert r.json()["ok"] is True

async def test_create_report_no_fuel(client, db_pool):
    station_id = await _seed_station_and_user(db_pool, client)
    r = await client.post("/reports", json={
        "station_id": station_id,
        "user_id": 42,
        "has_fuel": False,
        "fuel_type": "92",
    })
    assert r.status_code == 201

async def test_report_invalid_fuel_type(client, db_pool):
    station_id = await _seed_station_and_user(db_pool, client)
    r = await client.post("/reports", json={
        "station_id": station_id,
        "user_id": 42,
        "has_fuel": True,
        "fuel_type": "INVALID",
        "price": 50.0
    })
    assert r.status_code == 422

async def test_report_aggregates_in_status(client, db_pool):
    station_id = await _seed_station_and_user(db_pool, client)
    # 2 yes, 1 no → status should be "has_fuel: true"
    for _ in range(2):
        await client.post("/reports", json={
            "station_id": station_id, "user_id": 42,
            "has_fuel": True, "fuel_type": "95", "price": 54.0
        })
    await client.post("/reports", json={
        "station_id": station_id, "user_id": 42,
        "has_fuel": False, "fuel_type": "95"
    })
    r = await client.get(f"/stations/{station_id}/status")
    assert r.status_code == 200
    fuel_status = r.json()["fuel_status"]
    row_95 = next(f for f in fuel_status if f["fuel_type"] == "95")
    assert row_95["has_fuel"] is True
    assert row_95["votes_yes"] == 2
    assert row_95["votes_no"] == 1
