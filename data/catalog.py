# Kataloglar ro'yxati.
# Yangi katalog qo'shish: shu yerga 1 qator yozing, guruhda topic ochib /bind <kalit> qiling.

CATEGORIES = {
    # 🛋 Mebel bo'limlari
    "garderob":   "🚪 Гардероб ва шкаф",
    "prixojka":   "🏠 Прихожка мебель",
    "polniy_uy":  "🏡 Полный уй",
    "spalniy":    "🛏 Спальный мебель",
    "zal":        "📺 Зал учун мебель",
    "sanuzel":    "🚿 Санузел мебель",
    "detskiy":    "👶 Детский мебель",
    "kuxnya":     "🍳 Нео ва Классика кухня",
    "akril_kux":  "🚪 Эшик акрил кухня",
    "yumshoq":    "🛋 Юмшоқ мебель",
    "eshik":      "🚪 Эшиклар",
    "hotel":      "🏨 Отель учун мебель",
    "ofis":       "💼 Офис мебель",
    # 🎨 Material va fasadlar
    "akril":      "🎨 Акрил каталоги",
    "rover":      "🚪 Rover фасад турлари",
    "ruchka":     "🔩 Ручкалар каталоги",
    "obshivka":   "🪵 Обшивкалар",
}

GROUPS = {
    "mebel": ("🛋 Мебель бўлимлари", [
        "garderob", "prixojka", "polniy_uy", "spalniy", "zal", "sanuzel",
        "detskiy", "kuxnya", "akril_kux", "yumshoq", "eshik",
        "hotel", "ofis",
    ]),
    "material": ("🎨 Материал ва фасадлар", [
        "akril", "rover", "ruchka", "obshivka",
    ]),
}

PAGE_SIZE = 10  # Telegram albomga max 10 ta media sig'adi
