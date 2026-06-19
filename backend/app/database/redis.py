from redis.asyncio import Redis
from ..config.config import get_config

system = get_config()

_redis_client = Redis.from_url(
    system.redis_url,
    decode_responses=True
)


async def add_jti_to_blacklist(jti: str):
    return await _redis_client.set(f"blacklist:{jti}", "blacklisted")

async def is_jti_in_blacklist(jti: str) -> bool:
    return await _redis_client.exists(f"blacklist:{jti}")


async def mail_send(email) -> bool:
    redis_email = f"email:{email}"
    return await _redis_client.set(redis_email, "true", ex=18000)

async def is_mail_send(email) -> bool:
    redis_key = f"email:{email}"
    return await _redis_client.exists(redis_key)

async def mail_work_done(email) -> bool:
    redis_key = f"email:{email}"
    return await _redis_client.delete(redis_key)