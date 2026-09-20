"""Telegram command and message handlers."""

from __future__ import annotations

from collections import defaultdict
import os

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from fastapi import HTTPException

from app.security import MAX_UPLOAD_BYTES
from bot.localization import DEFAULT_LANGUAGE, LANGUAGES, text
from bot.service import analyze_telegram_file, analyze_text_content, format_result


router = Router(name="scamshield")
user_languages: dict[int, str] = defaultdict(lambda: DEFAULT_LANGUAGE)
SUPPORT_CONTACT = os.getenv("SUPPORT_CONTACT", "не указан")


def _language(message: Message) -> str:
    return user_languages[message.chat.id]


def _language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"language:{code}")]
            for code, label in LANGUAGES.items()
        ]
    )


@router.message(CommandStart())
async def start(message: Message) -> None:
    language = _language(message)
    await message.answer(
        f"{text(language, 'welcome')}\n\n{text(language, 'help')}\n\n"
        f"<i>{text(language, 'start_notice')}</i>"
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(text(_language(message), "help"))


@router.message(Command("privacy"))
async def privacy_command(message: Message) -> None:
    """Show the pilot privacy notice before a user sends potentially sensitive content."""
    await message.answer(
        text(_language(message), "privacy", support_contact=SUPPORT_CONTACT)
    )


@router.message(Command("language"))
async def language_command(message: Message) -> None:
    language = _language(message)
    await message.answer(text(language, "choose_language"), reply_markup=_language_keyboard())


@router.callback_query(F.data.startswith("language:"))
async def choose_language(callback: CallbackQuery) -> None:
    language = callback.data.split(":", maxsplit=1)[1]
    if language not in LANGUAGES or callback.message is None:
        await callback.answer()
        return
    user_languages[callback.message.chat.id] = language
    await callback.message.edit_text(text(language, "language_saved", language=LANGUAGES[language]))
    await callback.answer()


async def _send_analysis(message: Message, analysis) -> None:
    language = _language(message)
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await message.answer(text(language, "processing"))
    try:
        result = await analysis
        await message.answer(format_result(result, language))
    except ValueError as error:
        if str(error) == "unsupported_format":
            await message.answer(text(language, "unsupported"))
        elif str(error) == "file_too_large":
            await message.answer(text(language, "too_large", limit_mb=str(MAX_UPLOAD_BYTES // (1024 * 1024))))
        elif str(error) == "text_too_long":
            await message.answer(text(language, "too_long"))
        else:
            await message.answer(text(language, "failed"))
    except HTTPException as error:
        if error.status_code == 413:
            await message.answer(text(language, "too_large", limit_mb=str(MAX_UPLOAD_BYTES // (1024 * 1024))))
        else:
            await message.answer(text(language, "failed"))
    except Exception:
        await message.answer(text(language, "failed"))


@router.message(F.text & ~F.text.startswith("/"))
async def analyze_text(message: Message) -> None:
    await _send_analysis(message, analyze_text_content(message.text))


@router.message(F.photo)
async def analyze_photo(message: Message, bot: Bot) -> None:
    largest_photo = message.photo[-1]
    await _send_analysis(
        message,
        analyze_telegram_file(
            bot,
            file_id=largest_photo.file_id,
            filename="telegram_photo.jpg",
            caption=message.caption,
        ),
    )


@router.message(F.document)
async def analyze_document(message: Message, bot: Bot) -> None:
    document = message.document
    if document.file_size and document.file_size > MAX_UPLOAD_BYTES:
        language = _language(message)
        await message.answer(text(language, "too_large", limit_mb=str(MAX_UPLOAD_BYTES // (1024 * 1024))))
        return
    await _send_analysis(
        message,
        analyze_telegram_file(
            bot,
            file_id=document.file_id,
            filename=document.file_name or "uploaded_file",
            caption=message.caption,
        ),
    )


@router.message(F.audio)
async def analyze_audio(message: Message, bot: Bot) -> None:
    audio = message.audio
    if audio.file_size and audio.file_size > MAX_UPLOAD_BYTES:
        language = _language(message)
        await message.answer(text(language, "too_large", limit_mb=str(MAX_UPLOAD_BYTES // (1024 * 1024))))
        return
    await _send_analysis(
        message,
        analyze_telegram_file(
            bot,
            file_id=audio.file_id,
            filename=audio.file_name or "telegram_audio.mp3",
            caption=message.caption,
        ),
    )


@router.message()
async def unsupported_content(message: Message) -> None:
    await message.answer(text(_language(message), "unsupported"))
