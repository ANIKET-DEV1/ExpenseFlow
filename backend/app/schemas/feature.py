from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator
from typing import Optional, List
import uuid
from datetime import datetime, date
from decimal import Decimal
from ..model.models import DebtStatus,DebtType,PaymentType
class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}

class ExpenseCreate(BaseModel):
    tag_name: str = Field(..., min_length=2, max_length=50)
    amount: float = Field(..., gt=0)
    description: str | None = None
    payment_type: PaymentType
    expense_date: date 

    @field_validator("tag_name")
    @classmethod
    def normalize_tag_name(cls, value: str) -> str:
        return value.strip().lower()

class ExpenseResponse(BaseSchema):
    id: int
    tag_name:str 
    amount: Decimal
    expense_date: date
    description: str|None = Field(None, max_length=300)
    payment_type:PaymentType | None = None
    created_at: datetime


class TagCreate(BaseModel):
    tag_name: str = Field(..., min_length=2, max_length=20)
    @field_validator("tag_name")
    @classmethod
    def normalize_tag_name(cls, value: str) -> str:
        return value.strip().lower()

class TagResponse(BaseSchema):
    id: uuid.UUID
    tag_name: str

class DebtCreate(BaseModel):
    person_name: str = Field(..., min_length=2, max_length=50)
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    debt_date: date
    debt_type: DebtType
    debt_status: DebtStatus = DebtStatus.PENDING
    @field_validator("debt_type")
    @classmethod
    def normalize_debt_type(cls, value: str) -> str:
        return value.strip().lower()

class DebtResponse(BaseSchema):
    id: int
    person_name: str
    amount: Decimal
    debt_date: date
    debt_type: DebtType
    debt_status: DebtStatus

class DebtUpdate(BaseModel):
    person_name: str|None 
    amount: Decimal|None = -1.00
    debt_type: DebtType|None
    debt_status: DebtStatus| None
    @field_validator("person_name")
    @classmethod
    def normalize_person_type(cls, value: str) -> str:
        return None if value=="string" else None
    