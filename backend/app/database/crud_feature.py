from datetime import datetime
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from ..model import models
from ..repository.Base import BaseRepository
from ..schemas import user as user_schema
from ..schemas import feature as feature_schema


class manage_tag(BaseRepository):
    
    async def get_tag(self, tag: feature_schema.TagCreate, user_id: uuid.UUID) -> uuid.UUID:
    
        try:
            clean_tag_name = tag.tag_name.strip().lower()
            query = select(models.UserTag.id).where(
                (models.UserTag.user_id == user_id) & 
                (models.UserTag.tag_name == clean_tag_name)
            )
            result = await self.db.execute(query)
            existing_tag_id = result.scalar_one_or_none()
            
            if not existing_tag_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"'{tag.tag_name}' is not available. Please create it first."
                )
            return existing_tag_id

        except HTTPException:
            # Re-raise HTTPExceptions directly to prevent an accidental session rollback
            raise
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An internal database transactional error occurred while searching tags: \n {e}"
            )
        
    async def create_standalone_tag(
        self, 
        tag: feature_schema.TagCreate, 
        user_id: uuid.UUID
    ) -> models.UserTag:
        """
        Idempotently fetches an existing tag or creates a completely new one 
        in a safe database atomic transaction block.
        """
        try:
            clean_tag_name = tag.tag_name.strip().lower()
            
            # Look up tag locally to avoid cross-class method call bugs
            query = select(models.UserTag).where(
                (models.UserTag.user_id == user_id) &
                (models.UserTag.tag_name == clean_tag_name)
            )
            result = await self.db.execute(query)
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                return existing_tag

            # Create a clean record if it's new
            new_tag = models.UserTag(
                tag_name=clean_tag_name,
                user_id=user_id
            )
            self.db.add(new_tag)
            await self.db.commit()
            await self.db.refresh(new_tag)
            return new_tag
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add independent tag: {e}"
            )

    async def View_tag(self, user_id: uuid.UUID) -> list[models.UserTag]:
        try:
           
            self.db.expire_all()

            query = select(models.UserTag).where(models.UserTag.user_id == user_id)
            result = await self.db.execute(query)
            existing_tags = result.scalars().all()
            
            if not existing_tags:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No tags available in your account."
                )
            return existing_tags

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An internal database transactional error occurred while loading views: \n {e}"
            )

    async def del_tag(self, tag: str, user_id: uuid.UUID) -> bool:
        try:
            clean_tag_name = tag.strip().lower()
            query = select(models.UserTag).where(
                (models.UserTag.user_id == user_id) & 
                (models.UserTag.tag_name == clean_tag_name)
            )
            result = await self.db.execute(query)
            db_tag = result.scalar_one_or_none()
            
            if db_tag is None:
                return False

            await self.db.delete(db_tag)
            await self.db.commit()
            return True
        
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Can't Delete this tag because it link with some Expenses"
            )


class manage_expense(BaseRepository):
    
    async def add_expense(self, expense_data: feature_schema.ExpenseCreate, user_id: uuid.UUID):
        try:
            clean_tag_name = expense_data.tag_name.strip().lower()
            
            tag_query = select(models.UserTag.id).where(
                (models.UserTag.user_id == user_id) & 
                (models.UserTag.tag_name == clean_tag_name)
            )
            tag_result = await self.db.execute(tag_query)
            resolved_tag_id = tag_result.scalar_one_or_none()
            
            if not resolved_tag_id:
                new_tag = models.UserTag(tag_name=clean_tag_name, user_id=user_id)
                self.db.add(new_tag)
                await self.db.flush() 
                resolved_tag_id = new_tag.id

            db_expense = models.UserExpense(
                user_id=user_id,
                category_id=resolved_tag_id,
                amount=expense_data.amount,
                payment_type=expense_data.payment_type.value.upper(),
                description=expense_data.description,
                expense_date=expense_data.expense_date,
            )
            self.db.add(db_expense)
            await self.db.commit()

            return feature_schema.ExpenseResponse(
                id=db_expense.id,
                tag_name=clean_tag_name, 
                amount=db_expense.amount,
                expense_date=db_expense.expense_date,
                description=db_expense.description,
                payment_type=expense_data.payment_type, 
                created_at=getattr(db_expense, 'created_at', datetime.now()) 
            )
        
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An internal database transactional error occurred while tracking expenses: \n {e}"
            )
    
    async def view_expense(self, user_id: uuid.UUID) -> list[models.UserExpense]:
        try:
            query = (
                select(models.UserExpense)
                .options(selectinload(models.UserExpense.category))
                .where(models.UserExpense.user_id == user_id)
            )
            
            all_tag = await self.db.execute(query)
            result = all_tag.scalars().all()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No matching transactional data found."
                )
            return result

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while viewing expenses: \n {e}"
            )
    
    async def delete_expense(self, expense_id: int, user_id: uuid.UUID):
        try:
            query = select(models.UserExpense).where(
                (models.UserExpense.user_id == user_id) &
                (models.UserExpense.id == expense_id)
            )
            result = await self.db.execute(query)
            check_expense = result.scalar_one_or_none()
            
            if not check_expense:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No expenses found matching this specific tracking ID."
                )
                
            await self.db.delete(check_expense)
            await self.db.commit()
            return check_expense
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error while deleting expense: {e}"
            )


class manage_settlements(BaseRepository):
    
    async def add_debt(self, debt_data: feature_schema.DebtCreate, user_id: uuid.UUID):
        try:
            db_debt = models.UserDebt(
                user_id=user_id,
                person_name=debt_data.person_name,
                amount=debt_data.amount,
                debt_date=debt_data.debt_date,
                debt_type=debt_data.debt_type,
                debt_status=debt_data.debt_status,
            )
            self.db.add(db_debt)
            await self.db.commit()
            await self.db.refresh(db_debt)
            return db_debt
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An internal database transactional error occurred while tracking settlements: \n {e}"
            )

    async def view_debts(self, user_id: uuid.UUID) -> list[models.UserDebt]:
        try:
            query = (
                select(models.UserDebt)
                .where(models.UserDebt.user_id == user_id)
                .execution_options(populate_existing=True)
            )
            result = await self.db.execute(query)
            debts = result.scalars().all()
            
            if not debts:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No settlement records found for this user account."
                )
            return debts
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An internal database transactional error occurred while loading metrics: \n {e}"
            )

    async def update_debt(self, debt_id: int, debt_data: feature_schema.DebtUpdate, user_id: uuid.UUID):
        try:
            query = select(models.UserDebt).where(
                (models.UserDebt.user_id == user_id) &
                (models.UserDebt.id == debt_id)
            )
            result = await self.db.execute(query)
            db_debt = result.scalar_one_or_none()
            
            if not db_debt:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Settlement record not found."
                )

            update_data = debt_data.model_dump(exclude_unset=True)
            if update_data.get("amount") == -1:
                update_data.pop("amount")
            if not update_data.get("person_name"):
                update_data.pop("person_name")
                
            for key, value in update_data.items():
                setattr(db_debt, key, value)

            await self.db.commit()
            await self.db.refresh(db_debt)
            return db_debt
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An internal database transactional error occurred during updating processing: \n {e}"
            )

    async def delete_debt(self, debt_id: int, user_id: uuid.UUID):
        try:
            query = select(models.UserDebt).where(
                (models.UserDebt.user_id == user_id) &
                (models.UserDebt.id == debt_id)
            )
            result = await self.db.execute(query)
            db_debt = result.scalar_one_or_none()
            
            if not db_debt:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Settlement record not found."
                )
            await self.db.delete(db_debt)
            await self.db.commit()
            return db_debt
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An internal database transactional error occurred during settlement removal: \n {e}"
            )