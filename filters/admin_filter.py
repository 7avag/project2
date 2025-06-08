from aiogram import types
from aiogram.filters import BaseFilter
from config.settings import settings

class IsAdminFilter(BaseFilter):
    """
    Фильтр, проверяющий, является ли пользователь администратором.
    """

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in settings.ADMINS
