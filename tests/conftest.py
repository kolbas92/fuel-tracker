import os

import asyncio
import asyncpg
import pytest
from httpx import AsyncClient, ASGITransport

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/fuel_tracker_test",
)
os.environ.setdefault("API_KEY", "testkey")

from api.main import app
import api.db as db_module

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/fuel_tracker_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_pool():
    pool = await asyncpg.create_pool(TEST_DB_URL)
    # Drop leftovers from interrupted previous runs, then recreate
    async with pool.acquire() as conn:
        await conn.execute(
            "DROP VIEW IF EXISTS station_status; "
            "DROP TABLE IF EXISTS reports, stations, users CASCADE;"
        )
    with open("migrations/001_initial.sql") as f:
        sql = f.read()
    async with pool.acquire() as conn:
        await conn.execute(sql)
    yield pool
    async with pool.acquire() as conn:
        await conn.execute(
            "DROP VIEW IF EXISTS station_status; "
            "DROP TABLE IF EXISTS reports, stations, users CASCADE;"
        )
    await pool.close()


@pytest.fixture(autouse=True)
async def clean_tables(db_pool):
    yield
    async with db_pool.acquire() as conn:
        await conn.execute(
            "TRUNCATE reports, stations, users RESTART IDENTITY CASCADE"
        )


@pytest.fixture
async def client(db_pool):
    db_module._pool = db_pool
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
