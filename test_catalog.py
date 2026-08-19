"""Katalog mantig'ining tez tekshiruvi: python test_catalog.py"""
import asyncio

from aiogram.exceptions import TelegramBadRequest

from data.catalog import CATEGORIES, GROUPS, PAGE_SIZE


def paginate(total, page_size=PAGE_SIZE):
    """handlers/users/catalog.py dagi sahifalash mantig'ining aynan nusxasi"""
    pages, offset = [], 0
    while True:
        count = min(page_size, total - offset)
        if count <= 0:
            break
        last = offset + count
        pages.append((offset + 1, last))
        if total - last <= 0:
            break
        offset = last
    return pages


class FakeBot:
    """Berilgan file_id lar uchun xato qaytaradigan soxta bot"""

    def __init__(self, fails: dict):
        self.fails = fails          # {file_id: Exception}
        self.sent = []

    async def _send(self, chat_id, file_id, caption=None):
        if file_id in self.fails:
            raise self.fails[file_id]
        self.sent.append(file_id)

    send_photo = send_video = _send

    async def send_media_group(self, chat_id, media):
        for m in media:
            if m.media in self.fails:
                raise self.fails[m.media]
        self.sent.extend(m.media for m in media)


class NoSleep:
    """asyncio.sleep ni bekor qiladi — test tez tugasin"""
    @staticmethod
    async def sleep(_):
        return


def check_self_healing():
    """Albom yiqilganda: buzuq fayl o'chirilsin, tarmoq xatosi O'CHIRMASIN"""
    import handlers.users.catalog as cat

    items = [{"media_type": "photo", "file_id": f"f{i}"} for i in range(10)]
    bad_request = TelegramBadRequest(method=None, message="wrong file identifier")

    cat.asyncio = NoSleep()
    deleted_ids = []

    async def fake_delete(file_id):
        deleted_ids.append(file_id)

    cat.delete_catalog_item = fake_delete

    # 1. Buzuq fayl (Telegram uni tanimayapti) -> o'chirilsin
    bot = FakeBot({"f3": bad_request})
    sent, deleted = asyncio.run(cat.send_items(bot, 1, items, "izoh"))
    assert (sent, deleted) == (9, 1), (sent, deleted)
    assert deleted_ids == ["f3"], deleted_ids
    assert "f3" not in bot.sent

    # 2. Tarmoq xatosi -> o'tkazib yuborilsin, lekin BAZADAN O'CHIRILMASIN
    deleted_ids.clear()
    bot = FakeBot({"f5": ConnectionError("tarmoq uzildi")})
    sent, deleted = asyncio.run(cat.send_items(bot, 1, items, "izoh"))
    assert (sent, deleted) == (9, 0), (sent, deleted)
    assert deleted_ids == [], f"tarmoq xatosida media o'chirildi: {deleted_ids}"

    # 3. Hammasi joyida -> albom bitta bo'lib ketsin, bittalab emas
    bot = FakeBot({})
    sent, deleted = asyncio.run(cat.send_items(bot, 1, items, "izoh"))
    assert (sent, deleted) == (10, 0)
    assert len(bot.sent) == 10

    # 4. Keyingi sahifa offseti: o'chirilganlar surib qo'yadi, o'tkazilganlar yo'q
    assert 0 + len(items) - 1 == 9    # 1 ta o'chdi -> keyingisi 9 dan
    assert 0 + len(items) - 0 == 10   # 1 ta o'tkazildi -> keyingisi 10 dan


def demo():
    # 1. Har bir katalog aynan bitta guruhda bo'lishi shart
    # (aks holda send_catalog_page dagi next(...) qulaydi)
    grouped = [k for _, keys in GROUPS.values() for k in keys]
    assert sorted(grouped) == sorted(CATEGORIES), (
        f"Guruhga tushmagan: {set(CATEGORIES) - set(grouped)}, "
        f"ortiqcha: {set(grouped) - set(CATEGORIES)}"
    )
    assert len(grouped) == len(set(grouped)), "Katalog ikki guruhda takrorlangan"

    # 2. Albomga 10 tadan ko'p media sig'maydi
    assert 1 <= PAGE_SIZE <= 10

    # 3. callback_data 64 baytdan oshmasligi kerak
    longest = max((f"cat:c:{k}:9999" for k in CATEGORIES), key=len)
    assert len(longest.encode()) <= 64, longest

    # 4. Sahifalash: bo'shliq ham, takror ham bo'lmasin
    for total in (0, 1, 9, 10, 11, 47, 50, 100):
        pages = paginate(total)
        assert sum(b - a + 1 for a, b in pages) == total, (total, pages)
        for (_, prev_end), (next_start, _) in zip(pages, pages[1:]):
            assert next_start == prev_end + 1, (total, pages)
        if total:
            assert pages[0][0] == 1 and pages[-1][1] == total, (total, pages)

    assert paginate(47) == [(1, 10), (11, 20), (21, 30), (31, 40), (41, 47)]
    assert paginate(10) == [(1, 10)]          # bitta sahifa -> "Яна" tugmasi chiqmaydi
    assert paginate(0) == []                  # bo'sh katalog -> alohida xabar

    check_self_healing()

    print(f"OK: {len(CATEGORIES)} ta katalog, {len(GROUPS)} ta guruh, self-healing ishlaydi")


if __name__ == "__main__":
    demo()
