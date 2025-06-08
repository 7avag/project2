import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMINS: set[int] = set(map(int, os.getenv("ADMINS", "").split(","))) if os.getenv("ADMINS") else set()
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", 10))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 60))
    STORAGE_PATH: str = "storage/storage.json"
    LANGUAGES: tuple[str, str] = ("en", "ru")

settings = Settings()
