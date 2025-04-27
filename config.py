import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

assert BOT_TOKEN, "BOT_TOKEN yo'q"
assert DB_HOST and DB_PORT and DB_NAME and DB_USER and DB_PASSWORD, "Bazaga ulanish uchun .env to'liq emas"
assert GEMINI_API_KEY, "Gemini API kaliti kerak"
