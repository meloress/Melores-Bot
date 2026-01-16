from database.db import db

# Foydalanuvchini qo'shish
async def add_user(telegram_id: int, full_name: str, phone: str, region: str):
    sql = """
    INSERT INTO users (telegram_id, full_name, phone, region)
    VALUES ($1, $2, $3, $4)
    ON CONFLICT (telegram_id) DO UPDATE 
    SET full_name = $2, phone = $3, region = $4;
    """
    # ON CONFLICT: Agar user oldin bor bo'lsa, ma'lumotlarini yangilab qo'yadi
    await db.execute(sql, telegram_id, full_name, phone, region)

# Foydalanuvchini tekshirish
async def select_user(telegram_id: int):
    sql = "SELECT * FROM users WHERE telegram_id = $1"
    return await db.fetch(sql, telegram_id)