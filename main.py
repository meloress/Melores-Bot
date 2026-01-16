import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from data.config import BOT_TOKEN
from handlers.users import start # Start handlerni import qilish
from database.db import db

async def main():
    # Loglarni yoqish
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var not set")

# Eslatma: database.db faylingiz HANDLERLARNI import qilmasligi kerak
from database.db import db

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # ---------------- BAZANI ULASH ----------------
    # DB moduli boshqa modullarni import qilmasligi kerak (circular import bo'lmasin)
    await db.connect()       # Ulanish
    await db.create_tables() # Jadval yaratish
    # ----------------------------------------------

    # Handlerlarni import va ro'yxatdan o'tkazishni bazani ulagandan keyin qilamiz
    # shunda import vaqtida DB/handlers o'rtasida sikl paydo bo'lmaydi.
    from handlers import register_all_handlers
    register_all_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()  # Agar aiogram boshqa versiya bo'lsa, kerak bo'lsa bot.close() ga almashtiring

if __name__ == "__main__":
    asyncio.run(main())

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
