# BackEnd/Utils/redis.py

import logging
from redis import asyncio as aioredis  # use redis-py asyncio client
from BackEnd.Utils.config import settings

logger = logging.getLogger(__name__)


def get_redis_client():
    try:
        redis_url_str = str(settings.REDIS_URL)
        client = aioredis.from_url(
            redis_url_str,
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30,
        )
        logger.info("Redis client created successfully")
        return client
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")
        return None


redis_client = get_redis_client()


async def check_redis():
    try:
        redis = await get_redis_client()
        pong = await redis.ping()
        return {"status": pong}
    except Exception as e:
        logger.error(f"Redis ping failed: {str(e)}")
        return {"status": False, "error": str(e)}
