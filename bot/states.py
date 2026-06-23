# bot/states.py
from aiogram.fsm.state import State, StatesGroup

class FindFuel(StatesGroup):
    waiting_fuel_type = State()
    waiting_city      = State()

class ReportFuel(StatesGroup):
    waiting_city      = State()
    waiting_station   = State()
    waiting_fuel_type = State()
    waiting_status    = State()
    waiting_price     = State()
