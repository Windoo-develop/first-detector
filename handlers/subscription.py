import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database import activate_subscription, get_user
from .texts import TEXT
from .start import instruction_keyboard
from .states import UserState


router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(UserState.waiting_subscription, F.data == "subscribe")
async def on_subscribe_clicked(callback: CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id

    if not user_id:
        logger.warning("subscribe callback without user id")
        await callback.answer()
        return

    try:
        activate_subscription(user_id)
        await state.set_state(UserState.ready)
    except Exception as exc:
        logger.error("activate_subscription error for %s: %s", user_id, exc)
        await callback.answer("Something went wrong")
        return

    user = None

    try:
        user = get_user(user_id)
    except Exception as exc:
        logger.warning("get_user failed for %s: %s", user_id, exc)

    lang = "ru"

    if user:
        try:
            lang = user[1]
        except Exception:
            logger.debug("unexpected user record format: %s", user)

    text = TEXT.get("sub_ok", {}).get(lang)

    if not text:
        text = TEXT["sub_ok"]["ru"]

    keyboard = instruction_keyboard(lang)

    # удаляем сообщение с кнопкой подписки
    try:
        await callback.message.delete()
    except Exception:
        pass

    # отправляем новое сообщение
    await callback.message.answer(
        text,
        reply_markup=keyboard
    )

    await callback.answer(cache_time=2)