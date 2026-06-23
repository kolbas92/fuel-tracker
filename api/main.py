from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.db import get_pool, close_pool
from api.routers import stations, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    yield
    await close_pool()


app = FastAPI(title="Fuel Tracker API", version="1.0.0", lifespan=lifespan)
app.include_router(stations.router, prefix="/stations", tags=["stations"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
