import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database import get_user, create_or_update_user, add_user
from .texts import TEXT
from .states import UserState


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
async def start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    if user is None:
        add_user(user_id)
        await state.set_state(UserState.choosing_language)
        start_text = TEXT["start"]["ru"] + " / " + TEXT["start"]["en"]
        await message.answer(
            start_text,
            reply_markup=language_keyboard()
        )
        return

    lang = user[1] if user[1] else None
    subscribed = user[2] if user[2] else 0

    if lang is None:
        await state.set_state(UserState.choosing_language)
        start_text = TEXT["start"]["ru"] + " / " + TEXT["start"]["en"]
        await message.answer(
            start_text,
            reply_markup=language_keyboard()
        )
        return
    
    if subscribed == 0:
        await state.set_state(UserState.waiting_subscription)
        await message.answer(
            TEXT["need_sub"][lang],
            reply_markup=subscription_keyboard(lang)
        )
        return
    else:
        await state.set_state(UserState.ready)
        await message.answer(
            TEXT["sub_ok"][lang],
            reply_markup=instruction_keyboard(lang)
        )


@router.callback_query(
    UserState.choosing_language,
    F.data.startswith("lang_")
)
async def language_selected(callback: CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]

    create_or_update_user(user_id, lang)

    await state.set_state(UserState.waiting_subscription)

    # удаляем сообщение с кнопками языка
    try:
        await callback.message.delete()
    except Exception:
        pass

    # отправляем новое сообщение
    await callback.message.answer(
        TEXT["need_sub"][lang],
        reply_markup=subscription_keyboard(lang)
    )

    await callback.answer()
