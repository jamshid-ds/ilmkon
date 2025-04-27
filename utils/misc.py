import random
import string
import bcrypt
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

# Unikal ID generatsiyasi (1 harf + 6 raqam)
def generate_unique_id():
    return random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=6))

# Parolni hashlash
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Parolni solishtirish
def check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception as e:
        logging.warning(f"Parol tekshirishda xatolik: {e}")
        return False

# Xabarni xavfsiz o'chirish
async def delete_message_safe(bot: Bot, chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except TelegramBadRequest as e:
        if "message to delete not found" not in str(e):
            logging.warning(f"Xabarni o‘chirishda xatolik: {e}")
