from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")],
        [InlineKeyboardButton(text="🔑 Kirish", callback_data="login")]
    ])

def get_confirm_delete_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o‘chir", callback_data="confirm_delete_yes")],
        [InlineKeyboardButton(text="❌ Yo‘q, ortga", callback_data="confirm_delete_no")]
    ])
