from datetime import timedelta
from typing import Optional
from BackEnd.Utils.security import create_access_token, decode_token
from BackEnd.Utils.redis import get_redis_client


class TokenStore:
    def __init__(self):
        self.refresh_token_prefix = "refresh_token:"
        self.blacklist_prefix = "blacklist:"
        self.redis = get_redis_client()
        if self.redis is None:
            raise RuntimeError("Redis client not initialized")

    async def init(self):
        self.redis = await get_redis_client()

    async def store_refresh_token(self, user_id: str, token: str, expires_in: int) -> None:
        expires_seconds = int(timedelta(days=expires_in).total_seconds())
        await self.redis.setex(
            f"{self.refresh_token_prefix}{token}",
            expires_seconds,
            user_id
        )
        print(f"[DEBUG] Refresh token stored for user_id={user_id}, token={token[:10]}…")

    async def get_user_for_refresh_token(self, token: str) -> Optional[str]:
        return await self.redis.get(f"{self.refresh_token_prefix}{token}")

    async def revoke_token(self, token: str, expires_in: int) -> None:
        expires_seconds = int(timedelta(days=expires_in).total_seconds())
        await self.redis.setex(
            f"{self.blacklist_prefix}{token}",
            expires_seconds,
            "1"
        )
        print(f"[DEBUG] Refresh token revoked: {token[:10]}…")

    async def is_token_revoked(self, token: str) -> bool:
        key = f"{self.blacklist_prefix}{token}"
        return bool(await self.redis.exists(key))

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        if await self.is_token_revoked(refresh_token):
            print("[DEBUG] Attempted refresh with a revoked token.")
            return None

        user_id = await self.get_user_for_refresh_token(refresh_token)
        if not user_id:
            print("[DEBUG] Refresh token not found in store.")
            return None

        try:
            payload = decode_token(refresh_token)
        except Exception as e:
            print(f"[DEBUG] Refresh token validation failed: {e}")
            return None

        subject = payload.get("sub") or payload.get("email") or user_id
        new_access = create_access_token({"sub": subject})

        print(f"[DEBUG] Issued new access token for subject={subject}.")
        return new_access


# Singleton usage
# Use this pattern:
# from BackEnd.Utils.token_store import token_store
# await token_store.init()
token_store = TokenStore()