# bot/keyboards.py
from urllib.parse import quote
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

FUEL_TYPES = [
    ("АИ-92", "92"), ("АИ-95", "95"), ("АИ-98", "98"),
    ("ДТ", "dt"), ("Газ", "gas"),
]

_CANCEL_ROW = [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]

_SHARE_TEXT = (
    "⛽ «Бензина.нет» — бот показывает, где рядом есть топливо. "
    "Данные от водителей в реальном времени, помоги и ты!"
)

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Найти топливо"), KeyboardButton(text="📝 Сообщить")],
            [KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )

def share_keyboard(bot_username: str) -> InlineKeyboardMarkup:
    link = f"https://t.me/{bot_username}"
    share_url = f"https://t.me/share/url?url={quote(link)}&text={quote(_SHARE_TEXT)}"
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📤 Поделиться ботом", url=share_url)
    ]])

def comment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Пропустить")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def start_inline(channel_url: str) -> InlineKeyboardMarkup | None:
    if not channel_url:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📢 Наш канал", url=channel_url)
    ]])

def location_or_city_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Поделиться геолокацией", request_location=True)],
            [KeyboardButton(text="✏️ Ввести город или район")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def fuel_type_keyboard() -> InlineKeyboardMarkup:
    row1 = [InlineKeyboardButton(text=label, callback_data=f"fuel:{code}")
            for label, code in FUEL_TYPES[:3]]
    row2 = [InlineKeyboardButton(text=label, callback_data=f"fuel:{code}")
            for label, code in FUEL_TYPES[3:]]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, _CANCEL_ROW])

def yes_no_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Есть", callback_data="status:yes"),
            InlineKeyboardButton(text="❌ Нет",  callback_data="status:no"),
        ],
        _CANCEL_ROW,
    ])

def station_choice_keyboard(stations: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"⛽ {s['name']} ({s.get('dist', 0) / 1000:.1f} км)",
            callback_data=f"station:{s['id']}"
        )]
        for s in stations[:5]
    ]
    rows.append(_CANCEL_ROW)
    return InlineKeyboardMarkup(inline_keyboard=rows)
