from aiogram.fsm.state import StatesGroup, State

class RegisterState(StatesGroup):
    fullname = State()  # Ism kiritish
    phone = State()     # Telefon yuborish
    region = State()    # Viloyat tanlash