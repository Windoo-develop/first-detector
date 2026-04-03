import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.fsm.context import FSMContext

from database import get_user, create_or_update_user, add_user
from .texts import TEXT
from .states import UserState


router = Router()
log = logging.getLogger(__name__)

WIRESHARK_GUIDE_URL = "https://first-detector-site.vercel.app"


async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Restart bot"),
            BotCommand(command="language", description="Change language"),
            BotCommand(command="subscribe", description="Open subscription"),
            BotCommand(command="admin", description="Admin panel"),
        ]
    )


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


def get_user_context(user) -> tuple[str | None, int]:
    if not user:
        return None, 0
    lang = user[1] if len(user) > 1 and user[1] else None
    subscribed = user[2] if len(user) > 2 and user[2] else 0
    return lang, subscribed


async def _send_language_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(UserState.choosing_language)
    start_text = TEXT["start"]["ru"] + " / " + TEXT["start"]["en"]
    await message.answer(
        start_text,
        reply_markup=language_keyboard()
    )


async def _send_subscription_prompt(
    message: Message,
    state: FSMContext,
    lang: str,
) -> None:
    await state.set_state(UserState.waiting_subscription)
    await message.answer(
        TEXT["need_sub"][lang],
        reply_markup=subscription_keyboard(lang)
    )


async def send_ready_prompt(message: Message, state: FSMContext, lang: str) -> None:
    await state.set_state(UserState.ready)
    await message.answer(
        TEXT["sub_ok"][lang],
        reply_markup=instruction_keyboard(lang)
    )


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    if user is None:
        add_user(user_id)
        await _send_language_prompt(message, state)
        return

    lang, subscribed = get_user_context(user)

    if lang is None:
        await _send_language_prompt(message, state)
        return
    
    if subscribed == 0:
        await _send_subscription_prompt(message, state, lang)
        return

    await send_ready_prompt(message, state, lang)


@router.message(Command("language"))
async def change_language_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user(user_id) is None:
        add_user(user_id)

    await state.clear()
    await _send_language_prompt(message, state)


@router.message(Command("subscribe"))
async def subscribe_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user is None:
        add_user(user_id)
        await _send_language_prompt(message, state)
        return

    lang, subscribed = get_user_context(user)

    if lang is None:
        await _send_language_prompt(message, state)
        return

    if subscribed:
        await send_ready_prompt(message, state, lang)
        return

    await _send_subscription_prompt(message, state, lang)


@router.callback_query(
    F.data.startswith("lang_")
)
async def language_selected(callback: CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user = get_user(user_id)
    _, subscribed = get_user_context(user)

    create_or_update_user(user_id, lang)

    # удаляем сообщение с кнопками языка
    try:
        await callback.message.delete()
    except Exception:
        pass

    if subscribed:
        await send_ready_prompt(callback.message, state, lang)
    else:
        await state.set_state(UserState.waiting_subscription)
        await callback.message.answer(
            TEXT["need_sub"][lang],
            reply_markup=subscription_keyboard(lang)
        )

    await callback.answer()
