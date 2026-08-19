import asyncio

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from data.catalog import CATEGORIES
from data.config import CATALOG_GROUP_ID, SUPER_ADMIN_ID
from database.queries import (
    bind_catalog_topic,
    get_topic_category,
    add_catalog_item,
    count_catalog,
    count_all_catalogs,
    get_all_topic_bindings,
    clear_catalog,
    check_if_admin_exists,
)

router = Router()

# Katalog buyruqlari va media faqat katalog guruhida ishlaydi
IN_CATALOG_GROUP = F.chat.id == CATALOG_GROUP_ID

# ponytail: albom (media_group) uchun bitta tasdiq xabari yuborish uchun
# oxirgi ko'rilgan guruh ID si eslab qolinadi. Albomlar ketma-ket kelgani uchun
# bitta o'zgaruvchi yetarli; eng yomon holatda ortiqcha tasdiq xabari chiqadi.
_last_group_id = None


async def _is_admin(user_id: int) -> bool:
    return user_id == SUPER_ADMIN_ID or bool(await check_if_admin_exists(user_id))


# -----------------------------------------------------------
# 0. /id — shu chat va topic ID sini ko'rsatadi (har joyda ishlaydi)
# -----------------------------------------------------------
@router.message(Command("id"))
async def show_ids(message: Message):
    lines = [f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>"]
    if message.message_thread_id is not None:
        lines.append(f"🧵 <b>Topic ID:</b> <code>{message.message_thread_id}</code>")
    if message.chat.id != CATALOG_GROUP_ID:
        lines.append(
            f"\n⚠️ Katalog guruhi hozir: <code>{CATALOG_GROUP_ID}</code>\n"
            f"Agar katalog shu yerda bo'lsa, .env ga "
            f"<code>CATALOG_GROUP_ID={message.chat.id}</code> yozing va botni qayta ishga tushiring."
        )
    await message.reply("\n".join(lines))


# -----------------------------------------------------------
# 1. /kataloglar — mavjud kalitlar ro'yxati
# -----------------------------------------------------------
@router.message(Command("kataloglar"), IN_CATALOG_GROUP)
async def list_categories(message: Message):
    lines = [f"<code>{key}</code> — {name}" for key, name in CATEGORIES.items()]
    await message.reply(
        "📋 <b>Katalog kalitlari:</b>\n\n" + "\n".join(lines) +
        "\n\n➕ Topic ichida <code>/bind kalit</code> yozing."
    )


# -----------------------------------------------------------
# 2. /bind <kalit> — shu topicni katalogga bog'lash
# -----------------------------------------------------------
@router.message(Command("bind"), IN_CATALOG_GROUP)
async def bind_topic(message: Message, command: CommandObject):
    if not await _is_admin(message.from_user.id):
        await message.reply("⛔️ Faqat adminlar uchun.")
        return

    args = (command.args or "").split()
    key = args[0] if args else None

    if key not in CATEGORIES:
        await message.reply(
            "❌ Noto'g'ri kalit.\n"
            "Misol: <code>/bind garderob</code> (topic ichida)\n"
            "Yoki: <code>/bind garderob 81</code> (istalgan joydan, ID bilan)\n"
            "Kalitlar ro'yxati: /kataloglar"
        )
        return

    # Topic ID ni 2-argumentdan olamiz, bo'lmasa hozirgi topicdan
    if len(args) > 1:
        if not args[1].lstrip("-").isdigit():
            await message.reply("❌ Topic ID raqam bo'lishi kerak. Misol: <code>/bind garderob 81</code>")
            return
        thread_id = int(args[1])
    elif message.message_thread_id is not None:
        thread_id = message.message_thread_id
    else:
        await message.reply(
            "❌ Topic ichida yozing yoki ID ni ko'rsating: <code>/bind garderob 81</code>"
        )
        return

    await bind_catalog_topic(thread_id, key)
    total = await count_catalog(key)
    await message.reply(
        f"✅ <b>Topic #{thread_id} → '{CATEGORIES[key]}'</b>\n\n"
        f"📦 Hozir bazada: {total} ta media\n"
        f"📸 Endi shu topicka tashlanadigan <b>yangi</b> rasm/videolar avtomatik saqlanadi.\n"
        f"⚠️ Topicda allaqachon turgan eski rasmlarni bot ko'ra olmaydi — ularni qayta yuborish kerak."
    )


# -----------------------------------------------------------
# 3. /katalog_stat — har katalogda nechta media bor
# -----------------------------------------------------------
@router.message(Command("katalog_stat"), IN_CATALOG_GROUP)
async def catalog_stats(message: Message):
    counts = await count_all_catalogs()
    binds = await get_all_topic_bindings()
    lines = []
    for key, name in CATEGORIES.items():
        topic = f"#{binds[key]}" if key in binds else "❗️боғланмаган"
        lines.append(f"{'✅' if counts.get(key) else '⚪️'} {name} — <b>{counts.get(key, 0)}</b> · {topic}")

    await message.reply(
        "📊 <b>Katalog holati</b>\n\n" + "\n".join(lines) +
        f"\n\n📦 Jami: <b>{sum(counts.values())}</b> ta media"
    )


# -----------------------------------------------------------
# 4. /katalog_tozala — shu topicdagi katalogni tozalash
# -----------------------------------------------------------
# Guruhdan rasm o'chirilsa Telegram botga xabar bermaydi. Shuning uchun
# katalogni yangilash = tozalash + qaytadan tashlash.
@router.message(Command("katalog_tozala"), IN_CATALOG_GROUP)
async def clear_topic_catalog(message: Message):
    if not await _is_admin(message.from_user.id):
        await message.reply("⛔️ Faqat adminlar uchun.")
        return

    key = await get_topic_category(message.message_thread_id or 0)
    if not key:
        await message.reply("❌ Bu topic hech qaysi katalogga bog'lanmagan.")
        return

    total = await count_catalog(key)
    await clear_catalog(key)
    await message.reply(
        f"🗑 <b>{CATEGORIES.get(key, key)}</b> tozalandi ({total} ta o'chirildi).\n"
        f"📸 Rasmlarni qaytadan tashlashingiz mumkin."
    )


# -----------------------------------------------------------
# 5. AVTOMATIK SAQLASH (bog'langan topicdagi har rasm/video)
# -----------------------------------------------------------
async def bound_topic(message: Message):
    """Filtr: topic katalogga bog'langan bo'lsa {'key': ...} qaytaradi.
    Bog'lanmagan bo'lsa False — xabar boshqa handlerlarga o'tib ketaveradi."""
    if message.message_thread_id is None:
        return False
    key = await get_topic_category(message.message_thread_id)
    return {"key": key} if key else False


async def _report_saved(message: Message, key: str, delay: float):
    """Albom to'liq kelib bo'lgach bitta tasdiq xabari yuboradi"""
    await asyncio.sleep(delay)
    total = await count_catalog(key)
    try:
        await message.reply(f"✅ Saqlandi · <b>{CATEGORIES.get(key, key)}</b> — jami {total} ta")
    except Exception as e:
        print(f"Katalog tasdig'ini yuborishda xatolik: {e}")


@router.message(IN_CATALOG_GROUP, F.photo | F.video, bound_topic)
async def save_catalog_media(message: Message, key: str):
    global _last_group_id

    if message.photo:
        media_type, file_id = "photo", message.photo[-1].file_id
    else:
        media_type, file_id = "video", message.video.file_id

    await add_catalog_item(
        category=key,
        media_type=media_type,
        file_id=file_id,
        caption=message.caption,
        src_msg_id=message.message_id,
    )

    # Albomning har rasmiga javob bermaymiz — faqat birinchisiga,
    # u ham albom to'liq kelib bo'lishini kutib (son to'g'ri chiqishi uchun).
    if message.media_group_id:
        if message.media_group_id == _last_group_id:
            return
        _last_group_id = message.media_group_id
        asyncio.create_task(_report_saved(message, key, delay=3.0))
    else:
        await _report_saved(message, key, delay=0)
