from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.db import get_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    yield
    await close_pool()


app = FastAPI(title="Fuel Tracker API", version="1.0.0", lifespan=lifespan)
