from aiogram import Router
from aiogram.types import Message

from database import get_user
from .texts import TEXT

router = Router()

@router.message()
async def fallback(message: Message):
    user = get_user(message.from_user.id)
    lang = user[1] if user else "ru"

    await message.answer(TEXT["unknown"][lang])