from pydantic import BaseModel, Field, EmailStr, SecretStr, model_validator
import uuid
from fastapi import HTTPException,status
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}
    
class User(BaseModel):
    username: str = Field(..., min_length=2, max_length=20, description="Username")
    email: EmailStr = Field(...,)
    
class UserCreate(User):
    password: SecretStr = Field(..., min_length=8, max_length=100) 
    confirm_password: SecretStr = Field(..., min_length=8, max_length=100) 
    @model_validator(mode="after")
    def verify_passwords_match(self) -> "UserCreate":
        pw = self.password.get_secret_value()
        confirm_pw = self.confirm_password.get_secret_value()
        if pw != confirm_pw:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="passwords do not match")
        return self
    
class UserPasswordReset(BaseModel):
    new_password: SecretStr = Field(..., min_length=8, max_length=100) 
    confirm_password: SecretStr = Field(..., min_length=8, max_length=100) 
    @model_validator(mode="after")
    def verify_passwords_match(self) -> "UserCreate":
        pw = self.new_password.get_secret_value()
        confirm_pw = self.confirm_password.get_secret_value()
        if pw != confirm_pw:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="passwords do not match")
        return self
    
class UserLogin(BaseModel):
    username: str = Field(..., min_length=2, max_length=20, description="Username")
    password: SecretStr = Field(..., min_length=8, max_length=100) 
    
class UserResponse(BaseSchema):
    id: uuid.UUID
    username: str
    email: EmailStr
    created_at: datetime