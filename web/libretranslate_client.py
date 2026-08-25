import aiohttp
from envvars import LIBRETRANSLATE_ADDRESS, LIBRETRANSLATE_API_KEY


class LibreTranslateError(Exception):
    pass


def _url(path: str) -> str:
    return LIBRETRANSLATE_ADDRESS + path


def _payload(**fields) -> dict:
    if LIBRETRANSLATE_API_KEY:
        fields["api_key"] = LIBRETRANSLATE_API_KEY
    return fields


async def detect_language(message: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(_url("/detect"), json=_payload(q=message)) as resp:
            body = await resp.json()
            if resp.status >= 400:
                raise LibreTranslateError(body.get("error", body))
            return body[0]["language"]


async def translate(text: str, source: str, target: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            _url("/translate"),
            json=_payload(q=text, source=source, target=target, format="text"),
        ) as resp:
            body = await resp.json()
            if resp.status >= 400:
                raise LibreTranslateError(body.get("error", body))
            return body["translatedText"]
