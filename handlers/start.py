from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import get_user, create_or_update_user
from .texts import TEXT

def get_instruction_keyboard(lang):
    if lang == "ru":
        text = "📘 Инструкция Wireshark ↗"
    else:
        text = "📘 Wireshark Guide ↗"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    url="first-detector-site.vercel.app"
                )
            ]
        ]
    )

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    user = get_user(message.from_user.id)
    if user:
      if user[2] == 1:
        lang = user[1]
        await message.answer(
            TEXT["sub_ok"][lang],
            reply_markup=get_instruction_keyboard(lang)
        )
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.button(text="🇬🇧 English", callback_data="lang_en")

    await message.answer(
        TEXT["start"]["ru"] + " / " + TEXT["start"]["en"],
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("lang_"))
async def choose_language(call: CallbackQuery):
    lang = call.data.split("_")[1]

    create_or_update_user(call.from_user.id, lang)

    kb = InlineKeyboardBuilder()
    kb.button(
        text="💳 Subscribe" if lang == "en" else "💳 Оформить подписку",
        callback_data="subscribe"
    )

    await call.message.answer(
        TEXT["need_sub"][lang],
        reply_markup=kb.as_markup()
    )
    await call.answer()