import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.users import start # Start handlerni import qilish
from database.db import db

async def main():
    # Loglarni yoqish
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routerni ulash
    dp.include_router(start.router)

    # ---------------- BAZANI ULASH ----------------
    await db.connect()       # Ulanish
    await db.create_tables() # Jadval yaratish
    # ----------------------------------------------

    try:
        await dp.start_polling(bot)
    finally:
        await db.close() # Bot o'chganda bazani ham uzish

if __name__ == "__main__":
    asyncio.run(main())