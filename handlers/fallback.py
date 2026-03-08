import logging

from aiogram import Router
from aiogram.types import Message

from database import get_user
from .texts import TEXT

router = Router()
logger = logging.getLogger(__name__)


@router.message()
async def handle_unknown_message(message: Message) -> None:
    """
    Обработчик сообщений, которые не подходят
    ни под один из зарегистрированных handlers.
    """

    user_id = message.from_user.id
    language = "ru"  # язык по умолчанию

    try:
        user_data = get_user(user_id)

        # Если пользователь есть в базе — берем язык
        if user_data is not None:
            language = user_data[1]

    except Exception as error:
        logger.warning(
            "Failed to fetch user %s from database: %s",
            user_id,
            error
        )

    # Получаем текст ответа в зависимости от языка
    response_text = TEXT.get("unknown", {}).get(language)

    if not response_text:
        # fallback если в словаре нет нужного языка
        response_text = TEXT["unknown"]["ru"]

    await message.answer(response_text)