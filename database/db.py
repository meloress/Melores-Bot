import asyncpg
from config import DATABASE_URL

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

    async def create_tables(self):
        """Jadval yaratish"""
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone VARCHAR(20),
            region TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        await self.execute(sql)
        print("✅ Jadvallar tekshirildi/yaratildi")

    async def execute(self, sql, *args):
        """SQL buyruqlarni bajarish (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as connection:
            await connection.execute(sql, *args)

    async def fetch(self, sql, *args):
        """Ma'lumot olish (SELECT) - bitta qator"""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(sql, *args)

    async def fetch_all(self, sql, *args):
        """Ma'lumot olish (SELECT) - ko'p qator"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(sql, *args)

    async def close(self):
        """Ulanishni uzish"""
        if self.pool:
            await self.pool.close()

# Bitta obyekt yaratib olamiz
db = Database()