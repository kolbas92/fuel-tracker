# api/routers/reports.py
from fastapi import APIRouter, Depends, HTTPException
import asyncpg
from api.db import get_pool
from api.schemas import ReportCreate

router = APIRouter()

@router.post("", status_code=201)
async def create_report(report: ReportCreate, pool: asyncpg.Pool = Depends(get_pool)):
    async with pool.acquire() as conn:
        # Ensure user exists (bot may not have called /start)
        await conn.execute("""
            INSERT INTO users (telegram_id, first_name)
            VALUES ($1, 'User') ON CONFLICT DO NOTHING
        """, report.user_id)

        station_exists = await conn.fetchval(
            "SELECT 1 FROM stations WHERE id = $1", report.station_id
        )
        if not station_exists:
            raise HTTPException(status_code=404, detail="Station not found")

        await conn.execute("""
            INSERT INTO reports (station_id, user_id, has_fuel, fuel_type, price)
            VALUES ($1, $2, $3, $4, $5)
        """, report.station_id, report.user_id,
             report.has_fuel, report.fuel_type, report.price)

        await conn.execute("""
            UPDATE users SET report_count = report_count + 1 WHERE telegram_id = $1
        """, report.user_id)

    return {"ok": True}
