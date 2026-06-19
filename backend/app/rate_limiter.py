from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import jwt, JWTError
from fastapi import Request
from .config.config import get_config
from .Security.jwthandler import SECRET_KEY, ALGORITHM
system=get_config()

def rate_limit_key(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        return get_remote_address(request)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            return f"user:{user_id}"
    except JWTError:
        return get_remote_address(request)
    return get_remote_address(request)



limiter = Limiter(
    key_func=rate_limit_key,
    storage_uri=system.redis_url,  
    strategy="fixed-window",
    headers_enabled=True,
)