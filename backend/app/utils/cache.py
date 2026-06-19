import json
import logging
from typing import Any, Optional
import redis
from redis import exceptions,RedisClusterException,RedisError
from ..config.config import get_config

logger = logging.getLogger("uvicorn.error")
system = get_config()

class RedisCacheService:
    def __init__(self, redis_url: str = None):
        if not redis_url:
            redis_url = getattr(system, "redis_url", "redis://localhost:6379/0")
            
        self.client = redis.Redis.from_url(
            redis_url, 
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except exceptions.RedisError as e:
            logger.error(f"⚠️ Redis GET Error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        try:
            serialized_data = json.dumps(value)
            return self.client.set(key, serialized_data, ex=expire_seconds)
        except exceptions.RedisError as e:
            logger.error(f"⚠️ Redis SET Error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
       
        try:
            return bool(self.client.delete(key))
        except exceptions.RedisError as e:
            logger.error(f"⚠️ Redis DELETE Error for key '{key}': {e}")
            return False


cache_service = RedisCacheService()