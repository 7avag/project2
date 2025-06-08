# middlewares/throttling.py

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.dispatcher.flags import get_flag
import time

class ThrottlingMiddleware(BaseMiddleware):
    last_call = {}

    async def __call__(self, handler, event: TelegramObject, data: dict):
        user_id = event.from_user.id
        key = f"{user_id}:{handler.__name__}"
        now = time.time()

        if key in self.last_call and now - self.last_call[key] < 1.0:
            return  # игнорируем, если прошло < 1 сек
        self.last_call[key] = now
        return await handler(event, data)
