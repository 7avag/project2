# services/api_client.py

import aiohttp
import asyncio
from aiocache import cached, Cache
from config.settings import settings
from utils.logger import logger

class APIClient:
    """
    Клиент для работы с внешними API.
    """

    BASE_URL = "https://api.chucknorris.io/jokes"

    @cached(ttl=settings.CACHE_TTL, cache=Cache.MEMORY)
    async def get_random_joke(self) -> str:
        """
        Возвращает случайную шутку. Результаты кэшируются в памяти в течение CACHE_TTL секунд.
        """
        timeout = aiohttp.ClientTimeout(total=settings.API_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = f"{self.BASE_URL}/random"
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"API {url} вернул статус {resp.status}")
                        return "Не удалось получить шутку. Попробуйте позже."
                    data = await resp.json()
                    return data.get("value", "Шутка не найдена.")
            except asyncio.TimeoutError:
                logger.exception("Таймаут при запросе к API шуток.")
                return "API слишком долго не отвечает. Попробуйте позже."
            except Exception:
                logger.exception("Ошибка при запросе к API шуток.")
                return "Произошла ошибка при получении шутки."
