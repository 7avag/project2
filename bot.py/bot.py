# bot.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import settings
from utils.logger import logger
from routers.commands import router as commands_router
from filters.admin_filter import IsAdminFilter
from middlewares.throttling import ThrottlingMiddleware

async def main():
    # Создаём бота и диспетчер без parse_mode
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация middleware
    dp.message.middleware(ThrottlingMiddleware())

    # Регистрация фильтров
    dp.message.filter(IsAdminFilter())

    # Регистрация всех роутеров
    dp.include_router(commands_router)

    # Запуск polling
    try:
        logger.info("Бот запускается...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
