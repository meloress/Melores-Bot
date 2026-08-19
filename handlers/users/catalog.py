from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton,
    InputMediaPhoto, InputMediaVideo
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.catalog import CATEGORIES, GROUPS, PAGE_SIZE
from database.queries import (
    get_catalog_page,
    count_catalog,
    count_all_catalogs,
    update_active_section,
)

router = Router()


# --------------------------------------------------------
# 1. "📚 КАТАЛОГ" -> Guruhlar
# --------------------------------------------------------
@router.message(F.text == "📚 Каталог")
async def catalog_root(message: Message):
    await message.answer(
        "📚 <b>Мелорес каталоги</b>\n\n"
        "Қайси йўналиш қизиқтиради? 👇",
        reply_markup=await build_groups_kb()
    )


@router.callback_query(F.data == "cat:root")
async def catalog_root_call(call: CallbackQuery):
    await call.message.edit_text(
        "📚 <b>Мелорес каталоги</b>\n\n"
        "Қайси йўналиш қизиқтиради? 👇",
        reply_markup=await build_groups_kb()
    )
    await call.answer()


async def build_groups_kb():
    counts = await count_all_catalogs()
    builder = InlineKeyboardBuilder()
    for group_key, (title, keys) in GROUPS.items():
        total = sum(counts.get(k, 0) for k in keys)
        builder.button(text=f"{title} ({total})", callback_data=f"cat:g:{group_key}")
    builder.adjust(1)
    return builder.as_markup()


# --------------------------------------------------------
# 2. GURUH -> Kataloglar ro'yxati
# --------------------------------------------------------
@router.callback_query(F.data.startswith("cat:g:"))
async def catalog_group(call: CallbackQuery):
    group_key = call.data.split(":")[2]
    title, keys = GROUPS[group_key]
    counts = await count_all_catalogs()

    builder = InlineKeyboardBuilder()
    for key in keys:
        count = counts.get(key, 0)
        label = f"{CATEGORIES[key]} ({count})" if count else CATEGORIES[key]
        builder.button(text=label, callback_data=f"cat:c:{key}:0")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Орқага", callback_data="cat:root"))

    await call.message.edit_text(
        f"{title}\n\nКеракли бўлимни танланг 👇",
        reply_markup=builder.as_markup()
    )
    await call.answer()


# --------------------------------------------------------
# 3. KATALOG -> Albom yuborish (10 talab)
# --------------------------------------------------------
@router.callback_query(F.data.startswith("cat:c:"))
async def catalog_page(call: CallbackQuery):
    _, _, key, offset = call.data.split(":")
    offset = int(offset)

    if key not in CATEGORIES:
        await call.answer("Бўлим топилмади")
        return

    await update_active_section(call.from_user.id, f"catalog:{key}")

    # Eski boshqaruv xabaridagi tugmalarni olib tashlaymiz
    try:
        if offset == 0:
            await call.message.delete()
        else:
            await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await call.answer()
    await send_catalog_page(call.bot, call.from_user.id, key, offset)


async def send_catalog_page(bot, chat_id, key, offset):
    name = CATEGORIES[key]
    total = await count_catalog(key)
    group_key = next(g for g, (_, keys) in GROUPS.items() if key in keys)

    # ----------------------------------------------------
    # A) BO'LIM BO'SH
    # ----------------------------------------------------
    if total == 0:
        builder = InlineKeyboardBuilder()
        builder.button(text="📐 Замер белгилаш", callback_data="go_to_zamer_process")
        builder.button(text="🔙 Каталоглар", callback_data=f"cat:g:{group_key}")
        builder.adjust(1)
        await bot.send_message(
            chat_id,
            f"{name}\n\n"
            "🕐 <b>Бу бўлим тез орада тўлдирилади.</b>\n\n"
            "Шу орада ўлчовга ёзилсангиз, мутахассисимиз сизга мос вариантларни кўрсатади 👇",
            reply_markup=builder.as_markup()
        )
        return

    items = await get_catalog_page(key, offset, PAGE_SIZE)
    if not items:
        return

    last = offset + len(items)
    caption = f"{name}\n📷 {offset + 1}-{last} / {total}"

    # ----------------------------------------------------
    # B) MEDIA YUBORISH
    # ----------------------------------------------------
    try:
        if len(items) == 1:
            item = items[0]
            send = bot.send_photo if item['media_type'] == "photo" else bot.send_video
            await send(chat_id, item['file_id'], caption=caption)
        else:
            media = [
                (InputMediaPhoto if it['media_type'] == "photo" else InputMediaVideo)(
                    media=it['file_id'],
                    caption=caption if i == 0 else None
                )
                for i, it in enumerate(items)
            ]
            await bot.send_media_group(chat_id, media)
    except Exception as e:
        print(f"Каталог юборишда хатолик ({chat_id}, {key}): {e}")
        await bot.send_message(chat_id, "⚠️ Расмларни юборишда хатолик. Бироздан сўнг қайта уриниб кўринг.")
        return

    # ----------------------------------------------------
    # C) BOSHQARUV TUGMALARI (albomga tugma qo'yib bo'lmaydi)
    # ----------------------------------------------------
    builder = InlineKeyboardBuilder()
    remaining = total - last
    if remaining > 0:
        builder.button(
            text=f"🟢 Яна {min(remaining, PAGE_SIZE)} та кўриш ⬇️",
            callback_data=f"cat:c:{key}:{last}"
        )
    builder.button(text="📐 Замер белгилаш", callback_data="go_to_zamer_process")
    builder.button(text="🔙 Каталоглар", callback_data=f"cat:g:{group_key}")
    builder.adjust(1)

    footer = (
        f"✅ <b>{name}</b> — ҳаммаси кўрсатилди ({total} та)\n\n"
        "Ёқганини танладингизми? Ўлчовга ёзилинг 👇"
        if remaining <= 0 else
        f"{name} · {last}/{total} кўрсатилди"
    )
    await bot.send_message(chat_id, footer, reply_markup=builder.as_markup())
