import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.filters import Command

from db import init_db
from handlers import router as handlers_router

# Ваш токен Telegram-бота
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    init_db()  # Ініціалізація бази даних
    dp.include_router(handlers_router)  # Підключення обробників
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
