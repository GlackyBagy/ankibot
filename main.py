import asyncio
import types

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import preferences
from envvars import TG_TOKEN
from locales import t
from middleware.authorization import AuthMiddleware
from web import anki_client, jisho_client, libretranslate_client

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

dp.update.outer_middleware(AuthMiddleware())

NATIVE_LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
    ("de", "Deutsch"),
    ("ja", "日本語"),
    ("es", "Español"),
]
NATIVE_LANGUAGE_LABELS = dict(NATIVE_LANGUAGES)

BOT_UI_LANGUAGES = {"ru"}

# Deck is named after the language code the translator returns for the
# entered word, except English uses the 3-letter "eng" instead of "en".
DECK_NAME_OVERRIDES = {"en": "eng"}

# user_id -> Jisho entries awaiting a user's choice via inline keyboard
PENDING_JISHO_RESULTS: dict[int, list[dict]] = {}


def _ui_language(native_code: str) -> str:
    return native_code if native_code in BOT_UI_LANGUAGES else "en"


def _native_language_keyboard():
    builder = InlineKeyboardBuilder()
    for code, label in NATIVE_LANGUAGES:
        builder.button(text=label, callback_data=f"native:{code}")
    builder.adjust(2)
    return builder.as_markup()


@dp.message(Command("start", "set_native"))
async def menu(message: types.Message):
    await message.answer(
        t("choose_native", "en"),
        reply_markup=_native_language_keyboard(),
    )


@dp.callback_query(F.data.startswith("native:"))
async def set_native_language(callback: types.CallbackQuery):
    code = callback.data.split(":", 1)[1]
    label = NATIVE_LANGUAGE_LABELS[code]

    await preferences.save_native(callback.from_user.id, code)

    ui_lang = _ui_language(code)
    await callback.message.edit_text(t("native_saved", ui_lang, language=label))
    await callback.answer()


def _jisho_label(entry: dict) -> str:
    label = f"{jisho_client.kanji(entry)} - {jisho_client.meaning(entry)}"
    return label if len(label) <= 60 else label[:59] + "…"


async def _save_japanese_entry(entry: dict) -> tuple[str, str, str]:
    kanji = jisho_client.kanji(entry)
    reading = jisho_client.reading(entry)
    meaning = jisho_client.meaning(entry)

    deck_name = DECK_NAME_OVERRIDES.get("ja", "ja")
    await anki_client.ensure_deck(deck_name)
    await anki_client.add_basic_note(deck_name, front=kanji, back=f"{reading} — {meaning}")
    await anki_client.add_basic_note(deck_name, front=meaning, back=f"{kanji} ({reading})")
    await anki_client.sync()

    return kanji, reading, meaning


async def _handle_japanese_word(message: types.Message, ui_lang: str, word: str) -> None:
    results = await jisho_client.search_words(word)
    if not results:
        await message.answer(t("jisho_not_found", ui_lang, word=word))
        return

    common = [entry for entry in results if entry.get("is_common")]

    # Auto-pick only the unambiguous case: a single result, and it's common.
    if len(common) == 1 and len(results) == 1:
        kanji, reading, meaning = await _save_japanese_entry(common[0])
        await message.answer(t("word_added_japanese", ui_lang, kanji=kanji, reading=reading, meaning=meaning))
        return

    # 2+ common results -> offer only those. Otherwise (0 or 1 common mixed
    # with non-common ones) -> offer everything, since there's no clean pick.
    options = common if len(common) > 1 else results

    PENDING_JISHO_RESULTS[message.from_user.id] = options
    builder = InlineKeyboardBuilder()
    for index, entry in enumerate(options):
        builder.button(text=_jisho_label(entry), callback_data=f"jisho:{index}")
    builder.adjust(1)
    await message.answer(t("jisho_choose", ui_lang), reply_markup=builder.as_markup())


@dp.message(F.text)
async def add_word(message: types.Message):
    native = await preferences.get_native(message.from_user.id)
    if native is None:
        await message.answer(t("choose_native", "en"), reply_markup=_native_language_keyboard())
        return

    ui_lang = _ui_language(native)
    text = message.text

    detected = await libretranslate_client.detect_language(text)

    if detected == "ja":
        await _handle_japanese_word(message, ui_lang, text)
        return

    translated = await libretranslate_client.translate(text, source=detected, target=native)

    deck_name = DECK_NAME_OVERRIDES.get(detected, detected)
    await anki_client.ensure_deck(deck_name)
    await anki_client.add_basic_reversed_note(deck_name, front=text, back=translated)
    await anki_client.sync()

    await message.answer(t("word_added", ui_lang, deck=deck_name, translation=translated))


@dp.callback_query(F.data.startswith("jisho:"))
async def choose_japanese_word(callback: types.CallbackQuery):
    index = int(callback.data.split(":", 1)[1])
    common = PENDING_JISHO_RESULTS.pop(callback.from_user.id, None)

    native = await preferences.get_native(callback.from_user.id)
    ui_lang = _ui_language(native) if native else "en"

    if common is None or index >= len(common):
        await callback.answer(t("jisho_expired", ui_lang), show_alert=True)
        return

    kanji, reading, meaning = await _save_japanese_entry(common[index])
    await callback.message.edit_text(
        t("word_added_japanese", ui_lang, kanji=kanji, reading=reading, meaning=meaning)
    )
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
