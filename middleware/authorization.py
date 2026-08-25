from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from envvars import is_permitted_user


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: dict[str, Any]) -> Any:
        user = data.get('event_from_user')
        if user is not None and is_permitted_user(user.id):
            await handler(event, data)
