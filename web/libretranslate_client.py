import aiohttp
from envvars import LIBRETRANSLATE_ADDRESS


def _url(path: str) -> str:
    return LIBRETRANSLATE_ADDRESS + path


async def detect_language(message: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(_url("/detect"), json={"q": message}) as resp:
            resp.raise_for_status()
            results = await resp.json()
            return results[0]["language"]


async def translate(text: str, source: str, target: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            _url("/translate"),
            json={"q": text, "source": source, "target": target, "format": "text"},
        ) as resp:
            resp.raise_for_status()
            body = await resp.json()
            return body["translatedText"]
