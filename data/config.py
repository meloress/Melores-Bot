import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")
MAIN_GROUP_ID = os.getenv("MAIN_GROUP_ID")
TOPIC_ID_USERLAR = os.getenv("TOPIC_ID_USERLAR")  
TOPIC_ID_VIDEO_1 = os.getenv("TOPIC_ID_VIDEO_1")  
TOPIC_ID_DARSLIK = os.getenv("TOPIC_ID_DARSLIK")  
TOPIC_ID_ALOQA= os.getenv("TOPIC_ID_ALOQA")
TOPIC_ID_REMONT = os.getenv("TOPIC_ID_REMONT")
TOPIC_ID_ZAMER = os.getenv("TOPIC_ID_ZAMER")
TOPIC_ID_BIZ_HAQIMIZDA = os.getenv("TOPIC_ID_BIZ_HAQIMIZDA")