# bot/handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards import main_menu, start_inline
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
    channel_kb = start_inline(settings.channel_url)
    if channel_kb:
        await message.answer(
            "📢 Подпишись на канал — там сводки по наличию топлива:",
            reply_markup=channel_kb,
        )

@router.message(lambda m: m.text == "ℹ️ Помощь")
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🔍 <b>Найти топливо</b> — введи город/район, получишь ближайшие заправки\n"
        "📝 <b>Сообщить</b> — введи город/район, выбери заправку, укажи наличие и цену\n\n"
        "Данные актуальны 24 часа после репорта.",
        parse_mode="HTML",
    )
