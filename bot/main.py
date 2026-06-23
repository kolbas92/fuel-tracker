# bot/main.py
import asyncio
import logging
import socket
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import settings
from bot.handlers import start, find, report

logging.basicConfig(level=logging.INFO)

async def main():
    # Force IPv4 — Docker containers often lack IPv6 routing
    connector = aiohttp.TCPConnector(family=socket.AF_INET)
    session = AiohttpSession(connector=connector)
    bot = Bot(token=settings.bot_token, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(find.router)
    dp.include_router(report.router)

    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
