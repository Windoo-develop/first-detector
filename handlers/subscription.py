import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import activate_subscription, get_user
from .texts import TEXT
from .start import instruction_keyboard


router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "subscribe")
async def on_subscribe_clicked(callback: CallbackQuery):
    """
    Обработчик кнопки подписки.
    """

    user_id = callback.from_user.id

    # иногда Telegram может прислать callback без пользователя
    if not user_id:
        logger.warning("subscribe callback without user id")
        await callback.answer()
        return

    # активируем подписку
    try:
        activate_subscription(user_id)
    except Exception as exc:
        logger.error("activate_subscription error for %s: %s", user_id, exc)
        await callback.answer("Something went wrong")
        return

    # пробуем получить пользователя из базы
    user_record = None
    try:
        user_record = get_user(user_id)
    except Exception as exc:
        logger.warning("get_user failed for %s: %s", user_id, exc)

    # язык по умолчанию
    lang = "ru"

    if user_record is not None:
        try:
            lang = user_record[1]
        except Exception:
            logger.debug("user record has unexpected format: %s", user_record)

    text = TEXT.get("sub_ok", {}).get(lang)

    if not text:
        # fallback если перевод отсутствует
        text = TEXT["sub_ok"]["ru"]

    keyboard = instruction_keyboard(lang)

    # сначала пробуем отредактировать сообщение
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard
        )
    except Exception as exc:
        # Telegram иногда не позволяет редактировать сообщение
        logger.info("edit_text failed (%s), sending new message", exc)

        try:
            await callback.message.answer(
                text,
                reply_markup=keyboard
            )
        except Exception as send_error:
            logger.error("failed to send confirmation message: %s", send_error)

    await callback.answer()