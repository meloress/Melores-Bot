from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from data.config import BOT_TOKEN

# Bot obyekti
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

# Dispatcher (Routerlarni boshqaruvchi)
dp = Dispatcher(storage=MemoryStorage())