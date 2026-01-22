from database.db import db

# ---------------------------------------------------------
# USER (FOYDALANUVCHI)
# ---------------------------------------------------------
async def add_user(telegram_id: int, full_name: str, username: str, phone: str, region: str):
    """Foydalanuvchini qo'shish yoki yangilash (Username bilan)"""
    sql = """
    INSERT INTO users (telegram_id, full_name, username, phone, region, last_lesson_id, last_remont_id, last_about_id)
    VALUES ($1, $2, $3, $4, $5, 0, 0, 0)
    ON CONFLICT (telegram_id) DO UPDATE 
    SET full_name = $2, username = $3, phone = $4, region = $5;
    """
    await db.execute(sql, telegram_id, full_name, username, phone, region)

async def select_user(telegram_id: int):
    return await db.fetch("SELECT * FROM users WHERE telegram_id = $1", telegram_id)

async def get_all_users():
    return await db.fetch_all("SELECT telegram_id, full_name FROM users")

async def update_user_lesson(telegram_id: int, lesson_id: int):
    sql = "UPDATE users SET last_lesson_id = $1 WHERE telegram_id = $2"
    await db.execute(sql, lesson_id, telegram_id)

async def update_user_remont(telegram_id: int, lesson_id: int):
    sql = "UPDATE users SET last_remont_id = $1 WHERE telegram_id = $2"
    await db.execute(sql, lesson_id, telegram_id)

async def update_user_about(telegram_id: int, lesson_id: int):
    sql = "UPDATE users SET last_about_id = $1 WHERE telegram_id = $2"
    await db.execute(sql, lesson_id, telegram_id)

# ---------------------------------------------------------
# MEDIA FILES
# ---------------------------------------------------------
async def update_media(key: str, file_id: str, caption: str = None):
    sql = """
    INSERT INTO media_files (file_key, file_id, caption)
    VALUES ($1, $2, $3)
    ON CONFLICT (file_key) DO UPDATE SET file_id = $2, caption = $3;
    """
    await db.execute(sql, key, file_id, caption)

async def get_media(key: str):
    return await db.fetch("SELECT * FROM media_files WHERE file_key = $1", key)

# ---------------------------------------------------------
# LESSONS (Yangi uylar)
# ---------------------------------------------------------
async def add_lesson(lesson_id: int, file_id: str, caption: str):
    sql = """
    INSERT INTO lessons (id, file_id, caption)
    VALUES ($1, $2, $3)
    ON CONFLICT (id) DO UPDATE SET file_id = $2, caption = $3;
    """
    await db.execute(sql, lesson_id, file_id, caption)

async def get_lesson(lesson_id: int):
    return await db.fetch("SELECT * FROM lessons WHERE id = $1", lesson_id)

# ---------------------------------------------------------
# REMONT LESSONS
# ---------------------------------------------------------
async def add_remont_lesson(lesson_id: int, file_id: str, caption: str):
    sql = """
    INSERT INTO remont_lessons (id, file_id, caption)
    VALUES ($1, $2, $3)
    ON CONFLICT (id) DO UPDATE SET file_id = $2, caption = $3;
    """
    await db.execute(sql, lesson_id, file_id, caption)

async def get_remont_lesson(lesson_id: int):
    return await db.fetch("SELECT * FROM remont_lessons WHERE id = $1", lesson_id)

# ---------------------------------------------------------
# ABOUT LESSONS (Biz haqimizda)
# ---------------------------------------------------------
async def add_about_lesson(lesson_id: int, file_id: str, caption: str):
    sql = """
    INSERT INTO about_lessons (id, file_id, caption)
    VALUES ($1, $2, $3)
    ON CONFLICT (id) DO UPDATE SET file_id = $2, caption = $3;
    """
    await db.execute(sql, lesson_id, file_id, caption)

async def get_about_lesson(lesson_id: int):
    return await db.fetch("SELECT * FROM about_lessons WHERE id = $1", lesson_id)

# ---------------------------------------------------------
# ADMIN PANEL VA STATISTIKA
# ---------------------------------------------------------

# Admin tekshirish
async def check_if_admin_exists(telegram_id: int):
    return await db.fetch("SELECT telegram_id FROM admins WHERE telegram_id = $1", telegram_id)

# Admin qo'shish/o'chirish
async def add_admin(telegram_id: int, username: str):
    sql = """
    INSERT INTO admins (telegram_id, username, created_at)
    VALUES ($1, $2, NOW())
    ON CONFLICT (telegram_id) DO NOTHING;
    """
    await db.execute(sql, telegram_id, username)

async def delete_admin(telegram_id: int):
    await db.execute("DELETE FROM admins WHERE telegram_id = $1", telegram_id)

async def get_all_admins_list():
    return await db.fetch_all("SELECT * FROM admins")

async def get_admin(telegram_id: int):
    return await db.fetch("SELECT * FROM admins WHERE telegram_id = $1", telegram_id)

# --- DASHBOARD STATISTIKA ---
async def set_zamer_flag(telegram_id: int):
    await db.execute("UPDATE users SET zamer_requested = TRUE WHERE telegram_id = $1", telegram_id)

async def get_dashboard_stats():
    sql = """
    SELECT 
        COUNT(*) as total_users,
        SUM(CASE WHEN created_at::date = CURRENT_DATE THEN 1 ELSE 0 END) as new_today,
        SUM(CASE WHEN last_remont_id > 0 THEN 1 ELSE 0 END) as funnel_remont,
        SUM(CASE WHEN last_about_id > 0 THEN 1 ELSE 0 END) as funnel_about,
        SUM(CASE WHEN zamer_requested = TRUE THEN 1 ELSE 0 END) as funnel_zamer
    FROM users;
    """
    return await db.fetch(sql)

async def get_lessons_count():
    count_lessons = await db.fetch("SELECT COUNT(*) FROM lessons")
    count_remont = await db.fetch("SELECT COUNT(*) FROM remont_lessons")
    count_about = await db.fetch("SELECT COUNT(*) FROM about_lessons")
    return {
        "lessons": count_lessons['count'],
        "remont": count_remont['count'],
        "about": count_about['count']
    }

async def get_full_users_data():
    sql = """
    SELECT 
        telegram_id, full_name, username, phone, region, created_at,
        zamer_requested, last_lesson_id, last_remont_id, last_about_id
    FROM users ORDER BY created_at DESC;
    """
    return await db.fetch_all(sql)

# ---------------------------------------------------------
# CRM (QIDIRUV VA FILTERLAR)
# ---------------------------------------------------------

# Telefon bo'yicha qidirish
async def get_user_by_phone(phone: str):
    sql = "SELECT * FROM users WHERE phone LIKE $1"
    return await db.fetch(sql, f"%{phone}%")

# Username bo'yicha qidirish (YANGI)
async def get_user_by_username(username: str):
    clean_username = username.replace("@", "").strip()
    sql = "SELECT * FROM users WHERE username ILIKE $1"
    return await db.fetch(sql, clean_username)

# Ban status
async def update_ban_status(telegram_id: int, is_banned: bool):
    await db.execute("UPDATE users SET is_banned = $1 WHERE telegram_id = $2", is_banned, telegram_id)

# VIP users (Zamer bosganlar)
async def get_vip_users():
    return await db.fetch_all("SELECT * FROM users WHERE zamer_requested = TRUE ORDER BY created_at DESC LIMIT 10")

# ---------------------------------------------------------
# MAILING (XABAR YUBORISH UCHUN)
# ---------------------------------------------------------

# 1. Hudud bo'yicha ID larni olish
async def get_users_by_region(region_name: str):
    sql = "SELECT telegram_id FROM users WHERE region = $1 AND is_banned = FALSE"
    return await db.fetch_all(sql, region_name)

# 2. Zamer so'raganlarni olish
async def get_users_by_zamer():
    sql = "SELECT telegram_id FROM users WHERE zamer_requested = TRUE AND is_banned = FALSE"
    return await db.fetch_all(sql)

# 3. Faqat Remont bo'limiga o'tganlarni olish (Qiziqqanlar)
async def get_users_by_remont_interest():
    sql = "SELECT telegram_id FROM users WHERE last_remont_id > 0 AND is_banned = FALSE"
    return await db.fetch_all(sql)

# 4. Barcha aktiv userlar (Ban olmaganlar)
async def get_active_users():
    sql = "SELECT telegram_id FROM users WHERE is_banned = FALSE"
    return await db.fetch_all(sql)

# ---------------------------------------------------------
# SHABLONLAR (TEMPLATES)
# ---------------------------------------------------------

async def add_template(name: str, msg_type: str, file_id: str = None, caption: str = None):
    sql = """
    INSERT INTO mailing_templates (name, msg_type, file_id, caption)
    VALUES ($1, $2, $3, $4)
    """
    await db.execute(sql, name, msg_type, file_id, caption)

async def get_all_templates():
    return await db.fetch_all("SELECT * FROM mailing_templates ORDER BY created_at DESC")

async def get_template(template_id: int):
    return await db.fetch("SELECT * FROM mailing_templates WHERE id = $1", template_id)

async def delete_template(template_id: int):
    await db.execute("DELETE FROM mailing_templates WHERE id = $1", template_id)

async def update_active_section(telegram_id: int, section: str):
    await db.execute("UPDATE users SET active_section = $1 WHERE telegram_id = $2", section, telegram_id)

async def update_last_message_id(telegram_id: int, message_id: int):
    await db.execute("UPDATE users SET last_message_id = $1 WHERE telegram_id = $2", message_id, telegram_id)    
