"""Katalog mantig'ining tez tekshiruvi: python test_catalog.py"""
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

    print(f"OK: {len(CATEGORIES)} ta katalog, {len(GROUPS)} ta guruh")


if __name__ == "__main__":
    demo()
