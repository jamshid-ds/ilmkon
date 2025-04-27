import asyncpg
import logging
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

db_pool = None

async def create_db_pool():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            user=DB_USER, password=DB_PASSWORD, database=DB_NAME,
            host=DB_HOST, port=DB_PORT, min_size=1, max_size=10
        )
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50),
                    surname VARCHAR(50),
                    age SMALLINT,
                    username VARCHAR(30) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    id_unique VARCHAR(7) UNIQUE NOT NULL,
                    telegram_id BIGINT,
                    registration_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            """)
        logging.info("✅ DB pool va users jadvali tayyor.")
    except Exception as e:
        logging.critical(f"❌ DB ulanishda xatolik: {e}", exc_info=True)

async def close_db_pool():
    if db_pool:
        await db_pool.close()
        logging.info("🛑 DB pool yopildi.")

async def add_user(data: dict):
    from utils.misc import hash_password, generate_unique_id
    async with db_pool.acquire() as conn:
        unique_id = generate_unique_id()
        hashed_pwd = hash_password(data['password'])
        return await conn.fetchval("""
            INSERT INTO users (name, surname, age, username, password, id_unique, telegram_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id_unique;
        """, data['name'], data['surname'], data['age'], data['username'], hashed_pwd, unique_id, data['telegram_id'])

async def get_user_by_username(username: str):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE username = $1", username)

async def check_username_exists(username: str):
    async with db_pool.acquire() as conn:
        return await conn.fetchval("SELECT EXISTS(SELECT 1 FROM users WHERE username = $1)", username)

async def get_profiles_by_telegram_id(telegram_id: int):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT username FROM users WHERE telegram_id = $1", telegram_id)
        return [r['username'] for r in rows]

async def delete_profiles_by_telegram_id(telegram_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE telegram_id = $1", telegram_id)
