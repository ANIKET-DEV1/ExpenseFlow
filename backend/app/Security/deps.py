# Dependices like get user and all.

from fastapi import Depends, HTTPException, Request, status
from .jwthandler import verify_token
import uuid
from ..database.redis import is_jti_in_blacklist
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.database import get_db
from ..model.models import User
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing"
        )

    token_data = await verify_token(token)
    
    try:
        user_uuid = uuid.UUID(str(token_data.user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier structure"
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user is None or await is_jti_in_blacklist(token_data.jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists"
        )
        
    return user

async def get_current_user_with_jti(request: Request, db: AsyncSession = Depends(get_db)) :
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing"
        )

    token_data = await verify_token(token)
    
    try:
        user_uuid = uuid.UUID(str(token_data.user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier structure"
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user is None or token_data.jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists"
        )
        
    return token_data