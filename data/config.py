import os
from dotenv import load_dotenv

# Lokal kompyuterda .env ni o'qish uchun
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")
ADMINS = os.getenv("ADMINS", "").split(",")