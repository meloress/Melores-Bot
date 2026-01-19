import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares.check_ban import BanCheckMiddleware
from data.config import BOT_TOKEN
from database.db import db
from handlers import register_all_handlers
from utils.scheduler import send_scheduled_lessons

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.message.middleware(BanCheckMiddleware())
    dp.callback_query.middleware(BanCheckMiddleware())
    print("⏳ Baza ulanmoqda...")
    await db.connect()
    await db.create_tables()
    print("✅ Baza ulandi!")

    register_all_handlers(dp)

    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    
    scheduler.add_job(send_scheduled_lessons, 'cron', hour=10, minute=0, args=[bot])
    scheduler.add_job(send_scheduled_lessons, 'cron', hour=16, minute=0, args=[bot])
    
    scheduler.start()
    print("⏰ Jadval (10:00 va 16:00) ishga tushdi...")

    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Bot ishga tushdi (eski xabarlar tozalandi)!")

    try:
        await dp.start_polling(bot)
    finally:
        print("🛑 Bot to'xtatilmoqda...")
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi!")