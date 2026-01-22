import asyncpg
import sys
from data.config import DATABASE_URL

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Bazaga ulanish"""
        try:
            self.pool = await asyncpg.create_pool(dsn=DATABASE_URL)
            print("✅ PostgreSQL bazasiga ulandi")
        except Exception as e:
            print(f"❌ Bazaga ulanishda xatolik: {e}")
            sys.exit()

    async def create_tables(self):
        """Jadval yaratish va yangilash"""
        
        if not self.pool:
            print("⚠️ Baza ulanmagan, jadvallar yaratilmaydi.")
            return

        # ---------------------------------------------------------
        # 1. FOYDALANUVCHILAR JADVALI (USERS)
        # ---------------------------------------------------------
        await self.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            full_name TEXT,
            username TEXT,            -- Username
            phone TEXT,
            region TEXT,
            last_lesson_id INTEGER DEFAULT 0,  -- Yangi uylar
            last_remont_id INTEGER DEFAULT 0,  -- Remont
            last_about_id INTEGER DEFAULT 0,   -- Biz haqimizda
            zamer_requested BOOLEAN DEFAULT FALSE, -- Zamer bosganmi?
            is_banned BOOLEAN DEFAULT FALSE,       -- Ban olganmi?
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        
        # 1. Username
        try: await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT;") 
        except: pass
        
        # 2. Dars hisoblagichlari
        try: await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_lesson_id INTEGER DEFAULT 0;")
        except: pass
        try: await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_remont_id INTEGER DEFAULT 0;")
        except: pass
        try: await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_about_id INTEGER DEFAULT 0;")
        except: pass
        
        # 3. Zamer va Ban
        try: await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS zamer_requested BOOLEAN DEFAULT FALSE;")
        except: pass
        try: await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE;")
        except: pass


        # ---------------------------------------------------------
        # 2. MEDIA FILES (Fayl ID larni saqlash)
        # ---------------------------------------------------------
        await self.execute("""
        CREATE TABLE IF NOT EXISTS media_files (
            file_key TEXT PRIMARY KEY,
            file_id TEXT NOT NULL,
            caption TEXT
        );
        """)

        # ---------------------------------------------------------
        # 3. LESSONS (Yangi uylar videolari)
        # ---------------------------------------------------------
        await self.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY,
            file_id TEXT NOT NULL,
            caption TEXT
        );
        """)

        # ---------------------------------------------------------
        # 4. REMONT LESSONS
        # ---------------------------------------------------------
        await self.execute("""
        CREATE TABLE IF NOT EXISTS remont_lessons (
            id INTEGER PRIMARY KEY,
            file_id TEXT NOT NULL,
            caption TEXT
        );
        """)

        # ---------------------------------------------------------
        # 5. ABOUT LESSONS (Biz haqimizda videolari)
        # ---------------------------------------------------------
        await self.execute("""
        CREATE TABLE IF NOT EXISTS about_lessons (
            id INTEGER PRIMARY KEY,
            file_id TEXT NOT NULL,
            caption TEXT
        );
        """)

        # ---------------------------------------------------------
        # 6. ADMINS JADVALI
        # ---------------------------------------------------------
        await self.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # ---------------------------------------------------------
        # 7. MAILING TEMPLATES (SHABLONLAR)
        # ---------------------------------------------------------
        await self.execute("""
        CREATE TABLE IF NOT EXISTS mailing_templates (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,        -- Shablon nomi
            msg_type TEXT,             -- 'text', 'photo', 'video'
            file_id TEXT,              -- Agar media bo'lsa
            caption TEXT,              -- Matn
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # ---------------------------------------------------------
        # 🔥 8. MIGRATSIYA: YANGI KERAKLI USTUNLAR (VORONKA UCHUN)
        # ---------------------------------------------------------
        # Bu qism avtomatik ishlaydi va yo'q bo'lsa qo'shib qo'yadi
        
        try: 
            # User hozir qaysi bo'limda ekanligini bilish uchun ('lesson', 'remont', 'about')
            await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS active_section TEXT DEFAULT NULL;")
        except Exception as e: 
            print(f"Migratsiya (active_section): {e}")

        try: 
            # Oxirgi yuborilgan xabar ID sini saqlash (Tugmani o'chirish uchun)
            await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_message_id BIGINT DEFAULT 0;")
        except Exception as e: 
            print(f"Migratsiya (last_message_id): {e}")

        
        print("✅ Barcha jadvallar (Users, Media, Lessons, Remont, About, Admins, Templates) tayyor!")

    # ---------------------------------------------------------
    # YORDAMCHI FUNKSIYALAR
    # ---------------------------------------------------------
    async def execute(self, sql, *args):
        async with self.pool.acquire() as connection:
            await connection.execute(sql, *args)

    async def fetch(self, sql, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(sql, *args)

    async def fetch_all(self, sql, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(sql, *args)

    async def close(self):
        if self.pool:
            await self.pool.close()

db = Database()
