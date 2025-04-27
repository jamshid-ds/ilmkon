from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers.common import register_common_handlers
from handlers.registration import register_registration_handlers
from handlers.login import register_login_handlers
from handlers.voice import register_voice_handlers
from handlers.common import register_common_handlers
from database.db import create_db_pool, close_db_pool
from services.rag import initialize_rag_models

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def on_startup():
    await create_db_pool()
    await initialize_rag_models()
    print("✅ Bot ishga tushdi")

async def on_shutdown():
    await close_db_pool()
    await bot.session.close()
    print("🛑 Bot to'xtadi")

def register_all_handlers():
    register_common_handlers(dp)
    register_registration_handlers(dp)
    register_login_handlers(dp)
    register_voice_handlers(dp)

async def start_bot():
    register_all_handlers()
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()
