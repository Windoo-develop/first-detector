import logging
from pathlib import Path
from uuid import uuid4

from aiogram import Router, F, Bot
from aiogram.types import Message

from database import is_subscribed, get_user
from analysis import analyze_pcap
from .texts import TEXT


router = Router()
logger = logging.getLogger(__name__)

TEMP_DIR = Path("temp")
MAX_CAPTURE_SIZE_BYTES = 20 * 1024 * 1024


def _normalize_language(language: str | None) -> str:
    if language in {"ru", "en"}:
        return language
    return "ru"


def _get_user_language(user_data):
    if not user_data:
        return "ru"
    return _normalize_language(user_data[1])


def _is_valid_capture(filename: str):

    if not filename:
        return False

    filename = filename.lower()

    return filename.endswith(".pcap") or filename.endswith(".pcapng")


def _sanitize_filename(filename: str | None) -> str:
    if not filename:
        return "capture.pcap"

    sanitized = filename.replace("\\", "/").split("/")[-1]
    return sanitized or "capture.pcap"


def _build_temp_file_path(filename: str | None) -> Path:
    safe_name = _sanitize_filename(filename)
    suffix = Path(safe_name).suffix or ".pcap"
    return TEMP_DIR / f"{uuid4().hex}{suffix}"


@router.message(F.document)
async def process_capture_file(message: Message, bot: Bot):

    user_id = message.from_user.id

    user_data = get_user(user_id)
    lang = _get_user_language(user_data)

    if not is_subscribed(user_id):
        await message.answer(TEXT["no_sub"][lang])
        return

    document = message.document

    if not _is_valid_capture(document.file_name):
        await message.answer(TEXT["need_file"][lang])
        return

    if document.file_size and document.file_size > MAX_CAPTURE_SIZE_BYTES:
        await message.answer(TEXT["file_too_large"][lang])
        return

    file_path = None

    try:
        TEMP_DIR.mkdir(parents=True, exist_ok=True)

        file_path = _build_temp_file_path(document.file_name)

        logger.info(
            "user %s uploaded capture %s",
            user_id,
            document.file_name
        )

        await bot.download(document, destination=file_path)

        result = analyze_pcap(str(file_path))

        await message.answer(result)

    except Exception:
        logger.exception("error while processing capture")

        await message.answer(
            "Произошла ошибка при обработке файла. Попробуйте позже."
        )

    finally:

        try:
            if file_path and file_path.exists():
                file_path.unlink()
        except Exception:
            logger.warning("failed to delete temp file %s", file_path)
