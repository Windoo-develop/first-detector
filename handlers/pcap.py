import os
from aiogram import Router, F, Bot
from aiogram.types import Message

from database import is_subscribed, get_user
from .texts import TEXT
from analysis import analyze_pcap


router = Router()

@router.message(F.document)
async def handle_pcap(message: Message, bot: Bot):
    if not is_subscribed(message.from_user.id):
        user = get_user(message.from_user.id)
        lang = user[1] if user else "ru"
        await message.answer(TEXT["no_sub"][lang])
        return

    user = get_user(message.from_user.id)
    lang = user[1]

    document = message.document
    if not document.file_name.endswith((".pcap", ".pcapng")):
        await message.answer(TEXT["need_file"][lang])
        return

    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{document.file_unique_id}.pcap"

    await bot.download(document, destination=file_path)

    result = analyze_pcap(file_path)
    await message.answer(result)

    os.remove(file_path)