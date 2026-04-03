import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import get_user
from .start import (
    _send_language_prompt,
    _send_subscription_prompt,
    add_user,
    get_user_context,
    send_ready_prompt,
)

router = Router()
logger = logging.getLogger(__name__)


@router.message()
async def handle_unknown_message(message: Message, state: FSMContext) -> None:
    """
    Обработчик сообщений, которые не подходят
    ни под один из зарегистрированных handlers.
    """

    if message.text and message.text.startswith("/"):
        logger.debug("Ignoring unknown slash command: %s", message.text)
        return

    user_id = message.from_user.id

    try:
        user_data = get_user(user_id)
    except Exception as error:
        logger.warning(
            "Failed to fetch user %s from database: %s",
            user_id,
            error
        )
        user_data = None

    if user_data is None:
        add_user(user_id)
        await _send_language_prompt(message, state)
        return

    language, subscribed = get_user_context(user_data)

    if language is None:
        await _send_language_prompt(message, state)
        return

    if not subscribed:
        await _send_subscription_prompt(message, state, language)
        return

    await send_ready_prompt(message, state, language)
