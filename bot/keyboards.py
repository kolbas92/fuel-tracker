# bot/keyboards.py
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

FUEL_TYPES = [
    ("АИ-92", "92"), ("АИ-95", "95"), ("АИ-98", "98"),
    ("ДТ", "dt"), ("Газ", "gas"),
]

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Найти топливо"), KeyboardButton(text="📝 Сообщить")],
            [KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
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
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])

def yes_no_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Есть", callback_data="status:yes"),
        InlineKeyboardButton(text="❌ Нет",  callback_data="status:no"),
    ]])

def station_choice_keyboard(stations: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"⛽ {s['name']} ({s.get('dist', 0) / 1000:.1f} км)",
            callback_data=f"station:{s['id']}"
        )]
        for s in stations[:5]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
