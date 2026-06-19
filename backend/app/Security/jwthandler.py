# JWT 
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request, status, Response
import uuid
from uuid import uuid4
from ..database.redis import is_jti_in_blacklist
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.database import get_db
from ..model.models import User
from datetime import datetime, timedelta, timezone
from ..schemas.auth import TokenData
from ..config.config import get_config


system = get_config()
SECRET_KEY = system.secret_key.get_secret_value()
ALGORITHM = system.algorithms


def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=7)) -> str:
    encoded_jwt = jwt.encode(
        {
            **data,
            "jti": str(uuid4()),
            "exp": datetime.now(timezone.utc) + expires_delta
        },
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


# This function verifies the JWT token signature and checks the Redis blacklist
async def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        verified:bool | None =payload.get("verified")
        jti: str | None = payload.get("jti")

        if not verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please verify Email. Check Your Mail"
            )
        if user_id is None or  await is_jti_in_blacklist(jti) :
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or expired session"
            )

        return TokenData(user_id=user_id,jti=jti)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired session"
        )


# Sets the access token in cookies securely
def set_auth_cookies(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  
        samesite="none", 
        max_age=system.ACCESS_TOKEN_EXPIRE_MINUTE * 60,
    )


# Dependency guard to identify the user based on incoming cookies
