"""
Telegram tarjimon bot: 20 ta tilga tarjima, manba tili avtomatik aniqlanadi.

    pip install -r requirements.txt
    export BOT_TOKEN="..."      # Windows: set BOT_TOKEN=...
    python bot.py
"""
import asyncio
import json
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from deep_translator import GoogleTranslator

TOKEN = os.getenv("BOT_TOKEN")            # tokenni kodga YOZMANG
MAX_CHARS = 4500
SETTINGS_FILE = Path("settings.json")

# Til qo'shish uchun shu ro'yxatga yangi qator qo'shing: "kod": "🏳️ Nom"
LANGS = {
    "uz": "🇺🇿 O‘zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English",
    "tr": "🇹🇷 Türkçe", "ar": "🇸🇦 العربية", "zh-CN": "🇨🇳 中文",
    "es": "🇪🇸 Español", "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch",
    "it": "🇮🇹 Italiano", "pt": "🇵🇹 Português", "ja": "🇯🇵 日本語",
    "ko": "🇰🇷 한국어", "hi": "🇮🇳 हिन्दी", "fa": "🇮🇷 فارسی",
    "kk": "🇰🇿 Қазақша", "ky": "🇰🇬 Кыргызча", "tg": "🇹🇯 Тоҷикӣ",
    "uk": "🇺🇦 Українська", "az": "🇦🇿 Azərbaycan",
}

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


# ---------- sozlamalar (foydalanuvchi tanlagan til) ----------
def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text("utf-8"))
    except Exception:
        return {}


SETTINGS = load_settings()


def get_target(uid: int) -> str:
    return SETTINGS.get(str(uid), "en")


def set_target(uid: int, code: str) -> None:
    SETTINGS[str(uid)] = code
    SETTINGS_FILE.write_text(json.dumps(SETTINGS), "utf-8")


# ---------- tugmalar ----------
def lang_kb() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=name, callback_data=f"to:{code}")
               for code, name in LANGS.items()]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]   # qatorda 2 tadan
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------- tarjima (bu funksiyani boshqa xizmatga almashtirish mumkin) ----------
def _translate(text: str, target: str) -> str:
    return GoogleTranslator(source="auto", target=target).translate(text)


# ---------- handlers ----------
@dp.message(CommandStart())
async def start(m: Message):
    await m.answer("Salom! Men tarjimon botman. Qaysi tilga tarjima qilay?\n"
                   "Tilni tanlang, so‘ng istalgan matnni yuboring "
                   "(manba tili avtomatik aniqlanadi):", reply_markup=lang_kb())


@dp.message(Command("lang"))
async def lang_cmd(m: Message):
    await m.answer("Qaysi tilga tarjima qilay?", reply_markup=lang_kb())


@dp.callback_query(F.data.startswith("to:"))
async def choose(c: CallbackQuery):
    code = c.data.split(":", 1)[1]
    if code not in LANGS:
        return await c.answer("Noma’lum til")
    set_target(c.from_user.id, code)
    await c.message.answer(f"Tarjima tili: {LANGS[code]} ✅\nEndi matn yuboring.")
    await c.answer()


@dp.message(F.text & ~F.text.startswith("/"))
async def translate(m: Message):
    if len(m.text) > MAX_CHARS:
        return await m.answer(f"Matn juda uzun (maksimum {MAX_CHARS} belgi).")
    target = get_target(m.from_user.id)
    try:
        result = await asyncio.to_thread(_translate, m.text, target)
        if not result:
            return await m.answer("Tarjima qilib bo‘lmadi. Boshqa matn yuborib ko‘ring.")
        await m.answer(f"{LANGS[target]}\n\n{result}")
    except Exception:
        logging.exception("Tarjima xatosi")
        await m.answer("Xatolik yuz berdi. Keyinroq urinib ko‘ring.")


async def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN muhit o‘zgaruvchisi o‘rnatilmagan.")
    await dp.start_polling(Bot(TOKEN))


if __name__ == "__main__":
    asyncio.run(main())
