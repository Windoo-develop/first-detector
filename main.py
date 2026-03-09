import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage
import os
from handlers import router
from database import init_db

storage = MemoryStorage()
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
  await init_db()
  bot = Bot(token=BOT_TOKEN)
  dp = Dispatcher(storage=storage)

  dp.include_router(router)

  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())