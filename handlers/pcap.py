import os
import logging
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.types import Message

from database import is_subscribed, get_user
from analysis import analyze_pcap
from .texts import TEXT


router = Router()
logger = logging.getLogger(__name__)

TEMP_DIR = Path("temp")


def _get_user_language(user_data):
    """Возвращает язык пользователя или ru по умолчанию."""
    if not user_data:
        return "ru"
    return user_data[1]


def _is_valid_capture(filename: str) -> bool:
    """Проверяет расширение файла захвата."""
    if not filename:
        return False

    filename = filename.lower()
    return filename.endswith(".pcap") or filename.endswith(".pcapng")


@router.message(F.document)
async def process_capture_file(message: Message, bot: Bot) -> None:
    """
    Обрабатывает файл сетевого захвата, отправленный пользователем.
    Поддерживаются форматы .pcap и .pcapng.
    """

    user_id = message.from_user.id
    user_data = get_user(user_id)
    lang = _get_user_language(user_data)

    # Проверка подписки
    if not is_subscribed(user_id):
        await message.answer(TEXT["no_sub"][lang])
        return

    document = message.document

    if not _is_valid_capture(document.file_name):
        await message.answer(TEXT["need_file"][lang])
        return

    try:
        TEMP_DIR.mkdir(exist_ok=True)

        file_path = TEMP_DIR / f"{document.file_unique_id}.pcap"

        logger.info(
            "User %s uploaded capture file %s",
            user_id,
            document.file_name
        )

        await bot.download(document, destination=file_path)

        # анализ файла
        analysis_result = analyze_pcap(str(file_path))

        await message.answer(analysis_result)

    except Exception as error:
        logger.exception("Error while processing capture file")

        await message.answer(
            "Произошла ошибка при обработке файла. Попробуйте позже."
        )

    finally:
        # удаляем временный файл
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            logger.warning("Failed to delete temporary file %s", file_path)