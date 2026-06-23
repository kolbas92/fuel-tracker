# bot/handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards import main_menu
from bot.config import settings

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! ⛽\n\n"
        "Помогу найти заправку с топливом рядом или сообщить о статусе.\n\n"
        "Выбери действие:",
        reply_markup=main_menu(),
    )

@router.message(lambda m: m.text == "ℹ️ Помощь")
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🔍 <b>Найти топливо</b> — ближайшие заправки с нужным видом\n"
        "📝 <b>Сообщить</b> — сообщи о наличии и цене\n"
        "🗺️ <b>Карта</b> — открыть веб-карту\n\n"
        "Данные актуальны 24 часа после репорта.",
        parse_mode="HTML",
    )

@router.message(lambda m: m.text == "🗺️ Карта")
async def cmd_map(message: Message):
    await message.answer(
        f"🗺️ Открой карту в браузере:\n{settings.frontend_url}"
    )
