from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import activate_subscription, get_user
from .texts import TEXT

router = Router()

@router.callback_query(F.data == "subscribe")
async def subscribe(call: CallbackQuery):
    activate_subscription(call.from_user.id)

    user = get_user(call.from_user.id)
    lang = user[1]

    await call.message.answer(TEXT["sub_ok"][lang])
    await call.answer()