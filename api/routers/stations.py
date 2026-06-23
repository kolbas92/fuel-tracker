# api/routers/stations.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from uuid import UUID
import asyncpg
from api.db import get_pool
from api.schemas import StationCreate, StationOut, StationWithStatus, FuelStatus

router = APIRouter()

@router.post("", response_model=StationOut, status_code=201)
async def create_station(station: StationCreate, pool: asyncpg.Pool = Depends(get_pool)):
    async with pool.acquire() as conn:
        # Upsert user so FK constraint doesn't fail
        await conn.execute(
            "INSERT INTO users (telegram_id, first_name) VALUES ($1, 'User') ON CONFLICT DO NOTHING",
            station.added_by
        )
        row = await conn.fetchrow("""
            INSERT INTO stations (name, brand, address, location, added_by)
            VALUES ($1, $2, $3, ST_MakePoint($5, $4)::geography, $6)
            RETURNING id, osm_id, name, brand, address,
                      ST_Y(location::geometry) AS lat,
                      ST_X(location::geometry) AS lon
        """, station.name, station.brand, station.address,
             station.lat, station.lon, station.added_by)
    return dict(row)

@router.get("/nearby", response_model=list[StationOut])
async def nearby_stations(
    lat: float, lon: float,
    radius_km: float = 5.0,
    fuel_type: Optional[str] = None,
    pool: asyncpg.Pool = Depends(get_pool)
):
    radius_m = radius_km * 1000
    async with pool.acquire() as conn:
        if fuel_type:
            rows = await conn.fetch("""
                SELECT DISTINCT ON (s.id) s.id, s.osm_id, s.name, s.brand, s.address,
                       ST_Y(s.location::geometry) AS lat,
                       ST_X(s.location::geometry) AS lon,
                       ST_Distance(s.location, ST_MakePoint($2, $1)::geography) AS dist
                FROM stations s
                JOIN station_status ss ON ss.station_id = s.id AND ss.fuel_type = $3
                WHERE ST_DWithin(s.location, ST_MakePoint($2, $1)::geography, $4)
                ORDER BY s.id, dist
                LIMIT 10
            """, lat, lon, fuel_type, radius_m)
        else:
            rows = await conn.fetch("""
                SELECT id, osm_id, name, brand, address,
                       ST_Y(location::geometry) AS lat,
                       ST_X(location::geometry) AS lon,
                       ST_Distance(location, ST_MakePoint($2, $1)::geography) AS dist
                FROM stations
                WHERE ST_DWithin(location, ST_MakePoint($2, $1)::geography, $3)
                ORDER BY dist
                LIMIT 10
            """, lat, lon, radius_m)
    return [dict(r) for r in rows]

@router.get("", response_model=list[StationOut])
async def list_stations(
    min_lat: float, min_lon: float,
    max_lat: float, max_lon: float,
    pool: asyncpg.Pool = Depends(get_pool)
):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, osm_id, name, brand, address,
                   ST_Y(location::geometry) AS lat,
                   ST_X(location::geometry) AS lon
            FROM stations
            WHERE location && ST_MakeEnvelope($1, $2, $3, $4, 4326)::geography
            LIMIT 500
        """, min_lon, min_lat, max_lon, max_lat)
    return [dict(r) for r in rows]

@router.get("/{station_id}/status", response_model=StationWithStatus)
async def station_status(station_id: UUID, pool: asyncpg.Pool = Depends(get_pool)):
    async with pool.acquire() as conn:
        station = await conn.fetchrow("""
            SELECT id, osm_id, name, brand, address,
                   ST_Y(location::geometry) AS lat,
                   ST_X(location::geometry) AS lon
            FROM stations WHERE id = $1
        """, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        status_rows = await conn.fetch("""
            SELECT fuel_type, votes_yes, votes_no, median_price, last_report
            FROM station_status WHERE station_id = $1
        """, station_id)

    fuel_status = []
    for r in status_rows:
        total = r["votes_yes"] + r["votes_no"]
        has_fuel = None if total == 0 else (r["votes_yes"] > r["votes_no"])
        fuel_status.append(FuelStatus(
            fuel_type=r["fuel_type"],
            has_fuel=has_fuel,
            median_price=float(r["median_price"]) if r["median_price"] is not None else None,
            votes_yes=r["votes_yes"],
            votes_no=r["votes_no"],
            last_report=r["last_report"],
        ))

    return StationWithStatus(**dict(station), fuel_status=fuel_status)
