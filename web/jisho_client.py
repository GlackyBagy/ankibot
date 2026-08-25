import aiohttp

SEARCH_URL = "https://jisho.org/api/v1/search/words"


async def search_words(keyword: str) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(SEARCH_URL, params={"keyword": keyword}) as resp:
            resp.raise_for_status()
            body = await resp.json()
            return body["data"]


def kanji(entry: dict) -> str:
    japanese = entry["japanese"][0]
    return japanese.get("word") or japanese["reading"]


def reading(entry: dict) -> str:
    return entry["japanese"][0]["reading"]


def meaning(entry: dict) -> str:
    return ", ".join(entry["senses"][0]["english_definitions"])
