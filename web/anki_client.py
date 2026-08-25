import aiohttp

from envvars import ANKI_CONNECT_ADDRESS


class AnkiConnectError(Exception):
    pass


async def _invoke(action: str, **params) -> object:
    payload = {"action": action, "version": 6, "params": params}

    async with aiohttp.ClientSession() as session:
        async with session.post(ANKI_CONNECT_ADDRESS, json=payload) as resp:
            resp.raise_for_status()
            body = await resp.json()

    if body.get("error") is not None:
        raise AnkiConnectError(body["error"])
    return body["result"]


async def ensure_deck(deck_name: str) -> None:
    await _invoke("createDeck", deck=deck_name)


async def _add_note(deck_name: str, model_name: str, front: str, back: str) -> None:
    await _invoke(
        "addNote",
        note={
            "deckName": deck_name,
            "modelName": model_name,
            "fields": {"Front": front, "Back": back},
            "options": {"allowDuplicate": False},
            "tags": [],
        },
    )


async def add_basic_note(deck_name: str, front: str, back: str) -> None:
    await _add_note(deck_name, "Basic", front, back)


async def add_basic_reversed_note(deck_name: str, front: str, back: str) -> None:
    await _add_note(deck_name, "Basic (and reversed card)", front, back)
