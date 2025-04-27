from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from utils.keyboards import get_start_keyboard

router = Router()

def register_common_handlers(dp):
    dp.include_router(router)

@router.message(CommandStart())
async def handle_start(message: types.Message):
    user_name = message.from_user.full_name
    await message.answer(
        f"👋 Assalomu alaykum, {user_name}!\n\nQuyidagilardan birini tanlang:",
        reply_markup=get_start_keyboard()
    )
    await message.answer("🎤 Mohirdev haqida savolingiz bo‘lsa, menga <b>ovozli xabar</b> yuboring.", parse_mode="HTML")

@router.message(Command("help"))
async def handle_help(message: types.Message):
    await message.answer(
        "🆘 Yordam:\n"
        "1. Ro'yxatdan o'tish yoki tizimga kirish uchun tugmalardan foydalaning.\n"
        "2. Mohirdev platformasi bo'yicha savol berish uchun menga ovozli xabar yuboring.\n"
        "3. Savolingiz matnga aylantiriladi va javob ovozli shaklda qaytariladi."
    )
