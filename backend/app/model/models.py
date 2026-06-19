import uuid
import enum
from datetime import datetime, date
from typing import List
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, Date, Numeric, UniqueConstraint, func, Text, String, UUID, Integer, ForeignKey, Enum,Boolean

from ..database.database import Base

class DebtType(str, enum.Enum):
    LENT = "lent"
    BORROWED = "borrowed"

class DebtStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"

class PaymentType(str,enum.Enum):
    CASH="CASH"
    UPI="UPI"
    CARD="CARD"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False
    )
    password: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    verified_status:Mapped[bool]=mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # --- RELATIONSHIPS (All perfectly synced) ---
    expenses: Mapped[List["UserExpense"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    tags: Mapped[List["UserTag"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    debts: Mapped[List["UserDebt"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    

class UserTag(Base):
    __tablename__ = "tags"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    tag_name: Mapped[str] = mapped_column(String(20) , nullable=False)
    
    # --- RELATIONSHIPS ---
    user: Mapped["User"] = relationship(back_populates="tags")
    expenses: Mapped[List["UserExpense"]] = relationship(back_populates="category")
    __table_args__ = (
        UniqueConstraint("tag_name", "user_id", name="uq_user_tag_name"),
        
        CheckConstraint("tag_name = LOWER(tag_name)", name="ck_tag_name_lowercase"),
    )

class UserExpense(Base):
    __tablename__ = "expenses"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    payment_type:Mapped[PaymentType]=mapped_column(Enum(PaymentType, name="Payment_type_enum", values_callable=lambda x: [e.value for e in x]),
                                                   nullable=True,
                                                   default=PaymentType.CASH,  
                                                    server_default=PaymentType.CASH.value)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    # --- RELATIONSHIPS ---
    user: Mapped["User"] = relationship(back_populates="expenses")
    category: Mapped["UserTag"] = relationship(back_populates="expenses")

    @property
    def tag_name(self) -> str:
        if self.category:
            return self.category.tag_name
        return "Uncategorized"
    
class UserDebt(Base):
    __tablename__ = "debt"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    person_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    debt_date: Mapped[date] = mapped_column(Date, nullable=False)
    debt_type: Mapped[DebtType] = mapped_column(
        Enum(DebtType, name="debt_type_enum", values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    debt_status: Mapped[DebtStatus] = mapped_column(
        Enum(DebtStatus, name="debt_status_enum", values_callable=lambda x: [e.value for e in x]), 
        nullable=False,
        default=DebtStatus.PENDING 
    )
    
    # --- RELATIONSHIPS ---
    user: Mapped["User"] = relationship(back_populates="debts")