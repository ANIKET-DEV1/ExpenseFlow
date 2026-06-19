from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, Depends
from ..Security import jwthandler as jwt
from ..database.database  import get_db
import uuid
class BaseRepository():
    def __init__(self,tasks:BackgroundTasks,db:AsyncSession=Depends(get_db)):
        self.db=db
        self.tasks=tasks
    