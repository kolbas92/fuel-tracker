# bot/handlers/report.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import ReportFuel
from bot.keyboards import (
    fuel_type_keyboard, location_request,
    yes_no_keyboard, station_choice_keyboard, main_menu,
)
from bot import client as api

router = Router()

FUEL_LABELS = {"92": "АИ-92", "95": "АИ-95", "98": "АИ-98", "dt": "ДТ", "gas": "Газ"}

@router.message(F.text == "📝 Сообщить")
async def report_start(message: Message, state: FSMContext):
    await state.set_state(ReportFuel.waiting_location)
    await message.answer("Отправь геолокацию:", reply_markup=location_request())

@router.message(ReportFuel.waiting_location, F.location)
async def report_location(message: Message, state: FSMContext):
    lat, lon = message.location.latitude, message.location.longitude
    stations = await api.get_nearby(lat, lon, radius_km=2.0)
    if not stations:
        await state.clear()
        await message.answer(
            "😔 Рядом (2 км) нет заправок в базе. Попробуй в другом месте.",
            reply_markup=main_menu(),
        )
        return
    await state.update_data(stations={s["id"]: s for s in stations[:5]})
    await state.set_state(ReportFuel.waiting_station)
    await message.answer("Выбери заправку:", reply_markup=station_choice_keyboard(stations))

@router.callback_query(ReportFuel.waiting_station, F.data.startswith("station:"))
async def report_station(callback: CallbackQuery, state: FSMContext):
    station_id = callback.data.split(":", 1)[1]
    await state.update_data(station_id=station_id)
    await state.set_state(ReportFuel.waiting_fuel_type)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Тип топлива:", reply_markup=fuel_type_keyboard())
    await callback.answer()

@router.callback_query(ReportFuel.waiting_fuel_type, F.data.startswith("fuel:"))
async def report_fuel_type(callback: CallbackQuery, state: FSMContext):
    fuel_type = callback.data.split(":")[1]
    await state.update_data(fuel_type=fuel_type)
    await state.set_state(ReportFuel.waiting_status)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"{FUEL_LABELS[fuel_type]} — есть на заправке?",
        reply_markup=yes_no_keyboard(),
    )
    await callback.answer()

@router.callback_query(ReportFuel.waiting_status, F.data.startswith("status:"))
async def report_status(callback: CallbackQuery, state: FSMContext):
    has_fuel = callback.data.split(":")[1] == "yes"
    await state.update_data(has_fuel=has_fuel)
    await callback.message.edit_reply_markup(reply_markup=None)

    if has_fuel:
        await state.set_state(ReportFuel.waiting_price)
        await callback.message.answer("Цена за литр (например: 54.20):")
    else:
        data = await state.get_data()
        await state.clear()
        await _save_report(callback.message, callback.from_user.id, data, has_fuel=False, price=None)
    await callback.answer()

@router.message(ReportFuel.waiting_price)
async def report_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введи положительное число, например: 54.20")
        return
    data = await state.get_data()
    await state.clear()
    await _save_report(message, message.from_user.id, data, has_fuel=True, price=price)

async def _save_report(message: Message, user_id: int, data: dict, *, has_fuel: bool, price: float | None):
    await api.create_report(
        station_id=data["station_id"],
        user_id=user_id,
        has_fuel=has_fuel,
        fuel_type=data["fuel_type"],
        price=price,
    )
    label = FUEL_LABELS[data["fuel_type"]]
    status_str = f"✅ есть · {price:.2f} ₽/л" if has_fuel else "❌ нет"
    await message.answer(
        f"✅ Репорт записан!\n{label} — {status_str}",
        reply_markup=main_menu(),
    )
