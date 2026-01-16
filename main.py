import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var not set")

# db obyekti: database/db.py ichida DB sinfi bo'lib, connect/create_tables/close metodlari mavjud deb hisoblaymiz
from database.db import db

async def main():
    # Loglarni yoqish
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # ---------------- BAZANI ULASH ----------------
    # >>> MUHIM: bu kod async def ichida bo'lishi shart <<< 
    await db.connect()       # Ulanish
    await db.create_tables() # Jadval yaratish (agar kerak bo'lsa)
    # ----------------------------------------------

    # Handlerlarni ro'yxatga olishni DB ulanishidan keyin bajaraylik
    from handlers import register_all_handlers
    register_all_handlers(dp)

    try:
        # aiogram v3: dp.start_polling() async funksiyadir
        await dp.start_polling(bot)
    finally:
        await db.close()                 # bazani uzish
        # aiogram v3 uchun:
        try:
            await bot.session.close()
        except Exception:
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
