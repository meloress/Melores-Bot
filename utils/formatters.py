import re

def validate_phone(phone: str) -> str:
    """
    1. Agar raqam ichida harf bo'lsa -> None qaytaradi (XATO).
    2. Faqat raqam va '+' belgisi ruxsat etiladi.
    3. Uzunligi va formati tekshiriladi.
    """
    if re.search(r'[a-zA-Zа-яА-Я]', phone):
        return None

    cleaned = re.sub(r'\D', '', phone)

    if len(cleaned) == 9:
        return f"+998{cleaned}"
    elif len(cleaned) == 12 and cleaned.startswith("998"):
        return f"+{cleaned}"
    
    return None