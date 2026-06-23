# tests/conftest.py
import os
import pathlib
import pytest
import asyncpg
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/fuel_tracker_test")
os.environ.setdefault("API_KEY", "testkey")

from api.main import app
import api.db as db_module

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/fuel_tracker_test"
MIGRATIONS = pathlib.Path(__file__).parent.parent / "migrations" / "001_initial.sql"


@pytest.fixture(scope="session")
async def db_pool():
    pool = await asyncpg.create_pool(TEST_DB_URL)
    async with pool.acquire() as conn:
        await conn.execute(
            "DROP VIEW IF EXISTS station_status; "
            "DROP TABLE IF EXISTS reports, stations, users CASCADE;"
        )
    async with pool.acquire() as conn:
        await conn.execute(MIGRATIONS.read_text())
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
        await conn.execute("TRUNCATE reports, stations, users RESTART IDENTITY CASCADE")


@pytest.fixture
async def client(db_pool):
    original = db_module._pool
    db_module._pool = db_pool
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c
    finally:
        db_module._pool = original
