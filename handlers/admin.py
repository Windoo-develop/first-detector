import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from database import reset_subscription
from .states import UserState


router = Router()
logger = logging.getLogger(__name__)

ADMIN_USERNAME = "murcielagod"


def _is_admin(user) -> bool:
    if not user or not user.username:
        return False
    return user.username.lower() == ADMIN_USERNAME


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="♻️ Сбросить подписку",
                    callback_data="admin_reset_subscription",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✖️ Закрыть",
                    callback_data="admin_close",
                )
            ],
        ]
    )


async def _send_admin_panel(message: Message) -> None:
    await message.answer(
        "Админ-панель\n\nВыберите действие:",
        reply_markup=admin_keyboard(),
    )


@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    if not _is_admin(message.from_user):
        await message.answer("⛔️ Доступ запрещён.")
        return

    await state.clear()
    await _send_admin_panel(message)


@router.callback_query(F.data == "admin_reset_subscription")
async def admin_reset_subscription_prompt(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user):
        await callback.answer("Доступ запрещён", show_alert=True)
        return

    await state.set_state(UserState.admin_waiting_reset_user_id)
    await callback.message.answer(
        "Отправьте Telegram user_id пользователя, которому нужно сбросить подписку."
    )
    await callback.answer()


@router.callback_query(F.data == "admin_close")
async def admin_close_panel(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user):
        await callback.answer("Доступ запрещён", show_alert=True)
        return

    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        logger.debug("failed to delete admin panel message")

    await callback.answer("Панель закрыта")


@router.message(UserState.admin_waiting_reset_user_id)
async def admin_reset_subscription_by_user_id(message: Message, state: FSMContext):
    if not _is_admin(message.from_user):
        await state.clear()
        await message.answer("⛔️ Доступ запрещён.")
        return

    user_id_raw = (message.text or "").strip()

    if not user_id_raw.isdigit():
        await message.answer("Введите корректный числовой user_id.")
        return

    target_user_id = int(user_id_raw)
    was_reset = reset_subscription(target_user_id)

    if not was_reset:
        await message.answer(
            "Пользователь не найден. Проверьте user_id и отправьте его снова."
        )
        return

    await state.clear()
    await message.answer(
        f"✅ Подписка для пользователя `{target_user_id}` сброшена.",
        reply_markup=admin_keyboard(),
        parse_mode="Markdown",
    )
