# bot/handlers/find.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import FindFuel
from bot.keyboards import fuel_type_keyboard, location_request, main_menu
from bot import client as api

router = Router()

FUEL_LABELS = {"92": "АИ-92", "95": "АИ-95", "98": "АИ-98", "dt": "ДТ", "gas": "Газ"}

@router.message(F.text == "🔍 Найти топливо")
async def find_start(message: Message, state: FSMContext):
    await state.set_state(FindFuel.waiting_fuel_type)
    await message.answer("Какой вид топлива ищешь?", reply_markup=fuel_type_keyboard())

@router.callback_query(FindFuel.waiting_fuel_type, F.data.startswith("fuel:"))
async def find_fuel_chosen(callback: CallbackQuery, state: FSMContext):
    fuel_type = callback.data.split(":")[1]
    await state.update_data(fuel_type=fuel_type)
    await state.set_state(FindFuel.waiting_location)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Выбран: {FUEL_LABELS[fuel_type]}\n\nОтправь геолокацию:",
        reply_markup=location_request(),
    )
    await callback.answer()

@router.message(FindFuel.waiting_location, F.location)
async def find_location_received(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    lat, lon = message.location.latitude, message.location.longitude
    fuel_type = data["fuel_type"]

    stations = await api.get_nearby(lat, lon, fuel_type=fuel_type)
    if not stations:
        await message.answer(
            "😔 Рядом нет заправок с данными по этому виду топлива.\n"
            "Сообщи сам через 📝 Сообщить!",
            reply_markup=main_menu(),
        )
        return

    lines = [f"⛽ <b>Ближайшие с {FUEL_LABELS[fuel_type]}:</b>\n"]
    for s in stations[:5]:
        dist_km = (s.get("dist") or 0) / 1000
        name = s.get("name") or "Заправка"
        lines.append(f"• {name} — {dist_km:.1f} км")
    lines.append("\n<i>Открой карту для подробностей 🗺️</i>")

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=main_menu())
