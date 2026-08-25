LOCALES = {
    "ru": {
        "choose_native": "Выберите родной язык / Choose your native language:",
        "native_saved": "Родной язык сохранён: {language}",
        "word_added": "Добавлено в колоду «{deck}»: {translation}",
        "jisho_not_found": "Не нашлось распространённых слов для «{word}».",
        "jisho_choose": "Выберите нужное слово:",
        "jisho_expired": "Список устарел, попробуйте снова.",
        "word_added_japanese": "Добавлено: {kanji} ({reading}) — {meaning}",
    },
    "en": {
        "choose_native": "Выберите родной язык / Choose your native language:",
        "native_saved": "Native language saved: {language}",
        "word_added": 'Added to deck "{deck}": {translation}',
        "jisho_not_found": 'No common words found for "{word}".',
        "jisho_choose": "Choose the word you meant:",
        "jisho_expired": "This list expired, try again.",
        "word_added_japanese": "Added: {kanji} ({reading}) — {meaning}",
    },
}

DEFAULT_LOCALE = "en"


def t(key: str, lang: str, **kwargs) -> str:
    strings = LOCALES.get(lang, LOCALES[DEFAULT_LOCALE])
    template = strings.get(key, LOCALES[DEFAULT_LOCALE].get(key, key))
    return template.format(**kwargs) if kwargs else template
