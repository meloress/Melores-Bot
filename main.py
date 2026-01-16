import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher

from database.db import db

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var topilmadi")

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 🔴 await FAQAT shu yerda bo'lishi mumkin
    await db.connect()
    await db.create_tables()

    # handlerlarni kechroq import qilamiz (circular import bo'lmasin)
    from handlers import register_all_handlers
    register_all_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        try:
            await bot.session.close()
        except Exception:
            pass

# 🔴 BU QATOR MAJBURIY
if __name__ == "__main__":
    asyncio.run(main())
