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

WIRESHARK_GUIDE_URL = "https://first-detector-site.vercel.app"


def instruction_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == "ru":
        label = "📘 Инструкция Wireshark ↗"
    else:
        label = "📘 Wireshark Guide ↗"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, url=WIRESHARK_GUIDE_URL)]
        ]
    )


def language_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.button(text="🇬🇧 English", callback_data="lang_en")

    kb.adjust(2)
    return kb.as_markup()


def subscription_keyboard(lang: str):
    kb = InlineKeyboardBuilder()

    text = "💳 Subscribe" if lang == "en" else "💳 Оформить подписку"

    kb.button(text=text, callback_data="subscribe")

    return kb.as_markup()


@router.message(CommandStart())
async def start_command(message: Message):

    user_id = message.from_user.id

    try:
        user = get_user(user_id)
    except Exception as e:
        log.warning("failed to read user %s: %s", user_id, e)
        user = None

    # новый пользователь
    if user is None:
        start_text = TEXT["start"]["ru"] + " / " + TEXT["start"]["en"]

        await message.answer(
            start_text,
            reply_markup=language_keyboard()
        )
        return

    lang = user[1]
    subscribed = user[2]

    # пользователь есть, но без подписки
    if subscribed == 0:
        await message.answer(
            TEXT["need_sub"][lang],
            reply_markup=subscription_keyboard(lang)
        )
        return

    # пользователь уже подписан
    await message.answer(
        TEXT["sub_ok"][lang],
        reply_markup=instruction_keyboard(lang)
    )


@router.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery):

    user_id = callback.from_user.id
    raw = callback.data

    parts = raw.split("_")

    if len(parts) != 2:
        log.warning("unexpected callback format: %s", raw)
        await callback.answer()
        return

    lang = parts[1]

    try:
        create_or_update_user(user_id, lang)
    except Exception as e:
        log.error("cannot save language for %s: %s", user_id, e)

    try:
        await callback.message.edit_text(
            TEXT["need_sub"][lang],
            reply_markup=subscription_keyboard(lang)
        )
    except Exception:
        await callback.message.answer(
            TEXT["need_sub"][lang],
            reply_markup=subscription_keyboard(lang)
        )

    await callback.answer()