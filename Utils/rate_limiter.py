# BackEnd/Utils/rate_limiter.py
import redis.asyncio as redis
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from BackEnd.Utils.config import settings  # Replace with your actual config import path

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

redis_client = None


async def init_rate_limiter():
    global redis_client
    try:
        # Initialize Redis client without ssl=True
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        print("Redis rate limiter connected successfully.")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        redis_client = None


async def api_rate_limit(token: str = Depends(oauth2_scheme)):
    if redis_client is None:
        # Redis is unavailable; fallback - no rate limiting
        return

    user_id = token  # Adjust if you extract user_id differently

    key = f"rate_limit:{user_id}"
    try:
        current = await redis_client.get(key)
        if current and int(current) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, slow down!"
            )
        pipe = redis_client.pipeline()
        pipe.incr(key, amount=1)
        pipe.expire(key, 10)
        await pipe.execute()
    except Exception:
        # Fail silently on Redis errors
        pass


def rate_limit_dep(name: str):
    async def dependency():
        return await api_rate_limit(name)

    return dependency
