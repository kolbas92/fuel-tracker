# bot/handlers/find.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import FindFuel
from bot.keyboards import fuel_type_keyboard, location_or_city_keyboard, cancel_keyboard, main_menu
from bot.geocode import geocode
from bot import client as api

router = Router()

FUEL_LABELS = {"92": "АИ-92", "95": "АИ-95", "98": "АИ-98", "dt": "ДТ", "gas": "Газ"}

@router.message(F.text == "🔍 Найти топливо")
async def find_start(message: Message, state: FSMContext):
    await state.set_state(FindFuel.waiting_fuel_type)
    await message.answer("Какой вид топлива ищешь?", reply_markup=fuel_type_keyboard())

@router.callback_query(FindFuel.waiting_fuel_type, F.data == "cancel")
async def find_cancel_fuel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Отменено.", reply_markup=main_menu())
    await callback.answer()

@router.callback_query(FindFuel.waiting_fuel_type, F.data.startswith("fuel:"))
async def find_fuel_chosen(callback: CallbackQuery, state: FSMContext):
    fuel_type = callback.data.split(":")[1]
    await state.update_data(fuel_type=fuel_type)
    await state.set_state(FindFuel.waiting_location)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Выбран: {FUEL_LABELS[fuel_type]}\n\nКак указать местоположение?",
        reply_markup=location_or_city_keyboard(),
    )
    await callback.answer()

# --- waiting_location: GPS or choose text mode ---

@router.message(FindFuel.waiting_location, F.text == "❌ Отмена")
async def find_cancel_location(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu())

@router.message(FindFuel.waiting_location, F.text == "✏️ Ввести город или район")
async def find_switch_to_city(message: Message, state: FSMContext):
    await state.set_state(FindFuel.waiting_city)
    await message.answer(
        "Введи город или район (например: Лиски, Воронеж):",
        reply_markup=cancel_keyboard(),
    )

@router.message(FindFuel.waiting_location, F.location)
async def find_location_received(message: Message, state: FSMContext):
    lat, lon = message.location.latitude, message.location.longitude
    await _search_and_reply(message, state, lat, lon)

# --- waiting_city: text geocoding ---

@router.message(FindFuel.waiting_city, F.text == "❌ Отмена")
async def find_cancel_city(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu())

@router.message(FindFuel.waiting_city, F.text)
async def find_city_received(message: Message, state: FSMContext):
    coords = await geocode(message.text)
    if coords is None:
        await message.answer(
            "😔 Не удалось найти такой населённый пункт. Попробуй ещё раз.\n"
            "Например: Лиски, Воронеж, Россошь"
        )
        return
    await _search_and_reply(message, state, *coords)

# --- shared logic ---

async def _search_and_reply(message: Message, state: FSMContext, lat: float, lon: float):
    data = await state.get_data()
    await state.clear()
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

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=main_menu())
