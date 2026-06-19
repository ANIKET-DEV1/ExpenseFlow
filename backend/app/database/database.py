from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from ..config.config import get_config

settings = get_config()
db_url = settings.database_url.get_secret_value()

if "?" in db_url:
    db_url = db_url.split("?")[0]
    
engine = create_async_engine(db_url,
                             connect_args={"ssl": True},
                              echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)
class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            yield session