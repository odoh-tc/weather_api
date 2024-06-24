import os
import aioredis
from dotenv import load_dotenv

load_dotenv()

class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.redis_client = None
        return cls._instance

    async def init(self):
        if self.redis_client is not None:
            return  # Redis is already initialized

        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))
        redis_password = os.getenv("REDIS_PASSWORD", None)

        try:
            self.redis_client = await aioredis.from_url(
                f"redis://{redis_host}:{redis_port}/{redis_db}",
                password=redis_password,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()  # Test the connection

        except Exception as e:
            print(f"Error initializing Redis: {e}")
            raise

    async def get_client(self):
        if self.redis_client is None:
            await self.init()

        if self.redis_client is None:
            raise RuntimeError("Redis client initialization failed.")

        return self.redis_client

redis_client = RedisClient()
