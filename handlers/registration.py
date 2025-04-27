from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.db import (
    get_profiles_by_telegram_id, delete_profiles_by_telegram_id,
    check_username_exists, add_user
)
from utils.keyboards import get_confirm_delete_keyboard
from utils.misc import delete_message_safe
from aiogram.types import CallbackQuery

router = Router()

class RegistrationStates(StatesGroup):
    confirm_delete = State()
    name = State()
    age = State()
    username = State()
    password = State()

def register_registration_handlers(dp):
    dp.include_router(router)

@router.callback_query(F.data == "register")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    await callback.message.edit_reply_markup()
    profiles = await get_profiles_by_telegram_id(telegram_id)
    if profiles:
        profile_list = "\n".join([f"🔸 <code>{p}</code>" for p in profiles])
        msg = await callback.message.answer(
            f"🔒 Sizda mavjud profillar:\n{profile_list}\n\nYangi profil yaratish uchun eskilarini o‘chirasizmi?",
            reply_markup=get_confirm_delete_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.confirm_delete)
        await state.update_data(prompt_id=msg.message_id)
    else:
        msg = await callback.message.answer("👤 Ism va familiyangizni kiriting:")
        await state.set_state(RegistrationStates.name)
        await state.update_data(prompt_id=msg.message_id)

@router.callback_query(RegistrationStates.confirm_delete, F.data == "confirm_delete_yes")
async def confirm_delete(callback: CallbackQuery, state: FSMContext):
    await delete_profiles_by_telegram_id(callback.from_user.id)
    msg = await callback.message.answer("👤 Endi ism va familiyangizni kiriting:")
    await state.set_state(RegistrationStates.name)
    await state.update_data(prompt_id=msg.message_id)

@router.callback_query(RegistrationStates.confirm_delete, F.data == "confirm_delete_no")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Ro‘yxatdan o‘tish bekor qilindi.")
    await state.clear()

@router.message(RegistrationStates.name)
async def ask_age(message: types.Message, state: FSMContext):
    await delete_message_safe(message.bot, message.chat.id, message.message_id)
    parts = message.text.strip().split()
    if len(parts) < 1:
        return await message.answer("❗️ Iltimos, ism va familiya kiriting.")
    await state.update_data(name=parts[0], surname=parts[1] if len(parts) > 1 else "")
    msg = await message.answer("🎂 Yoshingizni kiriting:")
    await state.set_state(RegistrationStates.age)
    await state.update_data(prompt_id=msg.message_id)

@router.message(RegistrationStates.age)
async def ask_username(message: types.Message, state: FSMContext):
    age = message.text.strip()
    if not age.isdigit() or not (5 <= int(age) <= 120):
        return await message.answer("❗️ Yosh 5-120 oralig‘ida bo‘lishi kerak.")
    await state.update_data(age=int(age))
    msg = await message.answer("👤 Username tanlang:")
    await state.set_state(RegistrationStates.username)
    await state.update_data(prompt_id=msg.message_id)

@router.message(RegistrationStates.username)
async def ask_password(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if not username or len(username) < 3:
        return await message.answer("❗️ Username kamida 3 belgidan iborat bo‘lishi kerak.")
    if await check_username_exists(username):
        return await message.answer("❗️ Bu username band. Boshqasini tanlang.")
    await state.update_data(username=username)
    msg = await message.answer("🔑 Parol kiriting (kamida 6 belgi):")
    await state.set_state(RegistrationStates.password)
    await state.update_data(prompt_id=msg.message_id)

@router.message(RegistrationStates.password)
async def complete_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = message.text.strip()
    if len(password) < 6:
        return await message.answer("❗️ Parol kamida 6 belgi bo‘lishi kerak.")
    user_data = {
        "name": data["name"],
        "surname": data["surname"],
        "age": data["age"],
        "username": data["username"],
        "password": password,
        "telegram_id": message.from_user.id
    }
    user_id = await add_user(user_data)
    await message.answer(f"🎉 Ro‘yxatdan o‘tdingiz!\nSizning ID'ingiz: <code>{user_id}</code>", parse_mode="HTML")
    await state.clear()
