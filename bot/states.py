# bot/states.py
from aiogram.fsm.state import State, StatesGroup

class FindFuel(StatesGroup):
    waiting_fuel_type = State()
    waiting_location  = State()  # choose: GPS or text
    waiting_city      = State()  # text input mode
    waiting_station   = State()  # pick a station to see details

class ReportFuel(StatesGroup):
    waiting_location  = State()  # choose: GPS or text
    waiting_city      = State()  # text input mode
    waiting_station   = State()
    waiting_fuel_type = State()
    waiting_status    = State()
    waiting_price     = State()
    waiting_comment   = State()
