from os import getenv

TG_TOKEN = getenv("TG_TOKEN")

if TG_TOKEN is None:
    raise Exception("TG_TOKEN environment variable not set")

PERMITTED_USER_IDS = getenv("PERMITTED_USER_IDS")

if PERMITTED_USER_IDS is not None:
    PERMITTED_USER_IDS = [int(x) for x in PERMITTED_USER_IDS.split(",")]
else:
    raise Exception("PERMITTED_USER_IDS environment variable not set.")


def is_permitted_user(user_id: int) -> bool:
    return not PERMITTED_USER_IDS or user_id in PERMITTED_USER_IDS


ANKI_CONNECT_ADDRESS = getenv("ANKI_CONNECT_ADDRESS")

if ANKI_CONNECT_ADDRESS is None:
    raise Exception("ANKI_CONNECT_ADDRESS environment variable not set")

LIBRETRANSLATE_ADDRESS = getenv("LIBRETRANSLATE_ADDRESS")

if LIBRETRANSLATE_ADDRESS is None:
    raise Exception("LIBRETRANSLATE_ADDRESS environment variable not set")

LIBRETRANSLATE_API_KEY = getenv("LIBRETRANSLATE_API_KEY")
