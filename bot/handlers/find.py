# bot/handlers/find.py
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import FindFuel
from bot.keyboards import (
    fuel_type_keyboard, location_or_city_keyboard, cancel_keyboard,
    station_choice_keyboard, share_keyboard, main_menu,
)
from bot.geocode import geocode
from bot.config import settings
from bot import client as api

router = Router()

FUEL_LABELS = {"92": "АИ-92", "95": "АИ-95", "98": "АИ-98", "dt": "ДТ", "gas": "Газ"}

def _ago(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return ""
    mins = int((datetime.now(timezone.utc) - dt).total_seconds() // 60)
    if mins < 1:
        return "только что"
    if mins < 60:
        return f"{mins} мин назад"
    hours = mins // 60
    if hours < 24:
        return f"{hours} ч назад"
    return f"{hours // 24} дн назад"

def _format_station(s: dict) -> str:
    lines = [f"⛽ <b>{s['name']}</b>"]
    if s.get("address"):
        lines.append(f"📍 {s['address']}")
    lines.append("")

    fuel_status = s.get("fuel_status", [])
    if fuel_status:
        for f in fuel_status:
            label = FUEL_LABELS.get(f["fuel_type"], f["fuel_type"])
            if f["has_fuel"] is True:
                mark = "✅ есть"
            elif f["has_fuel"] is False:
                mark = "❌ нет"
            else:
                mark = "❔ неизвестно"
            price = f" · {f['median_price']:.2f} ₽/л" if f.get("median_price") else ""
            lines.append(f"{label}: {mark}{price}")
    else:
        lines.append("Пока нет свежих репортов по топливу.")

    comments = s.get("comments", [])
    if comments:
        lines.append("")
        lines.append("💬 <b>Комментарии:</b>")
        for c in comments:
            when = _ago(c.get("created_at", ""))
            suffix = f" <i>({when})</i>" if when else ""
            lines.append(f"• {c['text']}{suffix}")

    return "\n".join(lines)

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
    fuel_type = data["fuel_type"]

    stations = await api.get_nearby(lat, lon, fuel_type=fuel_type)
    if not stations:
        await state.clear()
        await message.answer(
            "😔 Рядом нет заправок с данными по этому виду топлива.\n"
            "Сообщи сам через 📝 Сообщить!",
            reply_markup=main_menu(),
        )
        return

    await state.set_state(FindFuel.waiting_station)
    await message.answer(
        f"⛽ <b>Заправки с {FUEL_LABELS[fuel_type]} рядом.</b>\n"
        "Выбери заправку, чтобы посмотреть статус и комментарии:",
        parse_mode="HTML",
        reply_markup=station_choice_keyboard(stations),
    )

@router.callback_query(FindFuel.waiting_station, F.data == "cancel")
async def find_cancel_station(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Отменено.", reply_markup=main_menu())
    await callback.answer()

@router.callback_query(FindFuel.waiting_station, F.data.startswith("station:"))
async def find_station_detail(callback: CallbackQuery, state: FSMContext):
    station_id = callback.data.split(":", 1)[1]
    await state.clear()
    status = await api.get_station_status(station_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        _format_station(status), parse_mode="HTML", reply_markup=main_menu()
    )
    await callback.message.answer(
        "Знаешь, где ещё есть топливо? Поделись ботом 👇",
        reply_markup=share_keyboard(settings.bot_username),
    )
    await callback.answer()
