from aiogram.utils.keyboard import InlineKeyboardBuilder

def regions_kb():
    builder = InlineKeyboardBuilder()
    
    regions = [
        "📍 Toshkent shahri", "📍 Toshkent viloyati", 
        "📍 Andijon", "📍 Buxoro", 
        "📍 Farg'ona", "📍 Jizzax", 
        "📍 Xorazm", "📍 Namangan", 
        "📍 Navoiy", "📍 Qashqadaryo", 
        "📍 Samarqand", "📍 Sirdaryo", 
        "📍 Surxondaryo", "📍 Qoraqalpog'iston"
    ]
    
    for region in regions:
        clean_name = region.replace("📍 ", "")
        builder.button(text=region, callback_data=f"reg:{clean_name}")
    
    builder.adjust(2) 
    return builder.as_markup()