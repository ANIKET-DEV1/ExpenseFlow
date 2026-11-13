from pydantic import BaseModel,Field

class user_message(BaseModel):
    role:str='user'
    prompt:str=Field(max_length=100)

class assistant_message(BaseModel):
    role:str='assistant'
    reply: str