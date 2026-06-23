# api/schemas.py
from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

VALID_FUEL_TYPES = {"92", "95", "98", "dt", "gas"}

class StationCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    address: Optional[str] = None
    lat: float
    lon: float
    added_by: int  # telegram_id

class FuelStatus(BaseModel):
    fuel_type: str
    has_fuel: Optional[bool]
    median_price: Optional[float]
    votes_yes: int
    votes_no: int
    last_report: Optional[datetime]

class StationOut(BaseModel):
    id: UUID
    osm_id: Optional[int]
    name: str
    brand: Optional[str]
    address: Optional[str]
    lat: float
    lon: float
    dist: Optional[float] = None  # distance in meters, only set by /nearby endpoint

class CommentOut(BaseModel):
    text: str
    fuel_type: str
    has_fuel: bool
    created_at: datetime

class StationWithStatus(StationOut):
    fuel_status: list[FuelStatus]
    comments: list[CommentOut] = []

class ReportCreate(BaseModel):
    station_id: UUID
    user_id: int
    has_fuel: bool
    fuel_type: str
    price: Optional[float] = None
    comment: Optional[str] = None

    @field_validator("fuel_type")
    @classmethod
    def validate_fuel_type(cls, v: str) -> str:
        if v not in VALID_FUEL_TYPES:
            raise ValueError(f"fuel_type must be one of {VALID_FUEL_TYPES}")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("price must be positive")
        return v

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v[:280] if v else None
