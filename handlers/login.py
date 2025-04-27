from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.db import get_user_by_username
from utils.misc import check_password

router = Router()

class LoginStates(StatesGroup):
    username = State()
    password = State()

def register_login_handlers(dp):
    dp.include_router(router)

@router.callback_query(F.data == "login")
async def login_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    msg = await callback.message.answer("🧑‍💻 Username kiriting:")
    await state.set_state(LoginStates.username)
    await state.update_data(prompt_id=msg.message_id)

@router.message(LoginStates.username)
async def login_password(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    msg = await message.answer("🔐 Parol kiriting:")
    await state.set_state(LoginStates.password)
    await state.update_data(prompt_id=msg.message_id)

@router.message(LoginStates.password)
async def login_complete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user_by_username(data["username"])
    if user and check_password(message.text, user['password']):
        await message.answer(f"✅ Xush kelibsiz, <b>{user['name']}</b>!", parse_mode="HTML")
    else:
        await message.answer("❌ Login yoki parol noto‘g‘ri.")
    await state.clear()
