import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import get_user, create_or_update_user
from .texts import TEXT


router = Router()
log = logging.getLogger(__name__)


# ссылка на инструкцию вынесена отдельно,
# чтобы ее было проще менять
WIRESHARK_GUIDE_URL = "https://first-detector-site.vercel.app"


def instruction_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Кнопка со ссылкой на инструкцию Wireshark.
    """

    if lang == "ru":
        label = "📘 Инструкция Wireshark ↗"
    else:
        label = "📘 Wireshark Guide ↗"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=label,
                    url=WIRESHARK_GUIDE_URL
                )
            ]
        ]
    )


def language_keyboard():
    kb = InlineKeyboardBuilder()

    # кнопки выбора языка
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.button(text="🇬🇧 English", callback_data="lang_en")

    kb.adjust(2)

    return kb.as_markup()


def subscription_keyboard(lang: str):
    kb = InlineKeyboardBuilder()

    if lang == "en":
        button_text = "💳 Subscribe"
    else:
        button_text = "💳 Оформить подписку"

    kb.button(text=button_text, callback_data="subscribe")

    return kb.as_markup()


@router.message(CommandStart())
async def start_command(message: Message):
    """
    Точка входа пользователя в бота.
    """

    user_id = message.from_user.id

    try:
        user = get_user(user_id)
    except Exception as e:
        log.warning("could not fetch user %s: %s", user_id, e)
        user = None

    if user is not None:
        lang = user[1]
        subscribed = user[2]

        # пользователь уже оплатил
        if subscribed == 1:
            await message.answer(
                TEXT["sub_ok"][lang],
                reply_markup=instruction_keyboard(lang)
            )
            return

    # если пользователь новый или без подписки
    start_text = TEXT["start"]["ru"] + "\n\n" + TEXT["start"]["en"]

    await message.answer(
        start_text,
        reply_markup=language_keyboard()
    )


@router.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery):
    """
    Пользователь выбирает язык интерфейса.
    """

    user_id = callback.from_user.id
    raw = callback.data

    # callback_data имеет формат lang_xx
    parts = raw.split("_")

    if len(parts) != 2:
        log.warning("unexpected callback format: %s", raw)
        await callback.answer()
        return

    lang = parts[1]

    try:
        create_or_update_user(user_id, lang)
    except Exception as e:
        log.error("failed to save language for %s: %s", user_id, e)

    await callback.message.answer(
        TEXT["need_sub"][lang],
        reply_markup=subscription_keyboard(lang)
    )

    await callback.answer()