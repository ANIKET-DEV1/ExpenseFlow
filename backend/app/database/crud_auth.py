import uuid

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..Security.password import PasswordHasher
from fastapi import HTTPException, status

from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from ..model import models
from ..schemas import user as user_schema

async def register_user(db: AsyncSession, user_data: user_schema.UserCreate)->models.User:
    try:
        duplicate_check =await db.execute(
            select(models.User).where(
                (models.User.email == user_data.email) | 
                (models.User.username == user_data.username)
            )
        )

        if duplicate_check.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or Email already registered"
            )

        hashed_password = PasswordHasher.hash(user_data.password.get_secret_value())
        db_user = models.User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password 
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return  db_user

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity constraint failure: User already exists"
        )
    except DataError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input data format error: Field length boundaries exceeded"
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal database transactional error occurred: \n {e}"
        )
    
async def login(db:AsyncSession,user_data:user_schema.UserLogin):
    try:
        result=await db.execute(
            select(models.User).where(
                user_data.username==models.User.username
            ))
        user=result.scalar()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Username Doesn't Exist")
        hashed_password=user.password
        passw =  PasswordHasher.verify(user_data.password.get_secret_value(),hashed_password)
        if passw:
            return user
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password credential"
        ) 
    
    except SQLAlchemyError as e:
       
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            
            detail="Database error occurred during authentication"
        )


async def update_verify_email(db:AsyncSession,user_id:uuid.UUID):
    try:
        result = await db.execute(select(models.User).where(models.User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User account not found.")
        if user.verified_status:
           raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Already Verified!")
        user.verified_status = True
        await db.commit()
        return user
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during authentication"
        )
    
async def update_password(db:AsyncSession,user_id:uuid.UUID,cred=user_schema.UserPasswordReset):
    try:
        result = await db.execute(select(models.User).where(models.User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User account not found.")
        
        if PasswordHasher.verify(cred.new_password.get_secret_value(),user.password):
            return user
        
        hashed_password = PasswordHasher.hash(cred.new_password.get_secret_value())
        user.password=hashed_password
        await db.commit()
        return user
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during authentication"
        )

async def _get_user(db:AsyncSession,cred:user_schema.ResetPasswordRequest):
    try :
        result = await db.execute(select(models.User).where(models.User.email == cred))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User account not found.")
        
        return  user
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during authentication"
        )
    



