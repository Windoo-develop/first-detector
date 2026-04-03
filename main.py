import asyncio
import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database import init_db
from handlers import router
from handlers.start import setup_bot_commands

storage = MemoryStorage()

load_dotenv()
load_dotenv(Path("id.env"))
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    init_db()

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN is not configured. Set it in the environment, .env, or id.env."
        )

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.include_router(router)

    try:
        await setup_bot_commands(bot)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
