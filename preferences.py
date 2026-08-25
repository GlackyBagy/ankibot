from configparser import ConfigParser

PREFS_FILE = "prefs.properties"


def _load() -> ConfigParser:
    config = ConfigParser()
    config.read(PREFS_FILE)
    return config


def _save(config: ConfigParser) -> None:
    with open(PREFS_FILE, "w") as f:
        config.write(f)


async def save_native(user_id: int, language: str) -> None:
    config = _load()
    section = str(user_id)
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, "native_language", language)
    _save(config)


async def get_native(user_id: int) -> str | None:
    config = _load()
    section = str(user_id)
    return config.get(section, "native_language", fallback=None)