from pydantic import BaseModel,Field

class Send_message(BaseModel):
    prompt:str=Field(max_length=30)

class Response_message(BaseModel):
    reply: str