from .Base import BaseRepository
from ..schemas import feature
import uuid
from ..model.models import User
from ..database.crud_feature import manage_tag, manage_expense, manage_settlements
from fastapi import HTTPException,status
from .mail_handling import NotificationService


class features(BaseRepository):
    async def add_tags(self, tag=feature.TagCreate,user_id=uuid.UUID):
        data= await manage_tag.create_standalone_tag(self,tag,user_id)
        if not data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Server Error ")
        return data
    
    async def view_tags(self,user_id=uuid.UUID):
        data = await manage_tag.View_tag(self,user_id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No data found")
        return data
    
    async def del_tag(self,tag_name:str ,user=uuid.UUID)->bool:
        return await manage_tag.del_tag(self,tag_name,user)
    

    
#============================== Expense===========================

class expensesRepo(BaseRepository):
    async def add_expense(self,expense=feature.ExpenseCreate,user=User):
        data=await manage_expense.add_expense(self,expense_data=expense,user_id=user.id)
        if not data:
            raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,
                                detail="Error Occur!")
        
        await NotificationService(self.tasks).send_mail(
            recipients=[user.email],
            subject="Your Expense Added Succesfully",
            context_data={
                
                "amount":data.amount,
                "description":data.description
            },
            template_name="mail_add_expense.html"
        )
        
        return data
    
    async def view_expense(Self,user_id=uuid.UUID)->list[feature.ExpenseResponse]:
        return  await manage_expense.view_expense(Self,user_id)
        
    async def del_expense(Self,expense_id=int,user=User):
        data = await manage_expense.delete_expense(Self,expense_id,user.id)
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        
        await NotificationService(Self.tasks).send_mail(
            recipients=[user.email],
            subject="Your Expense Deleted Succesfully",
            context_data={
                "id":data.id,
                "amount":data.amount,
                "username":user.username
            },
            template_name="mail_del_expense.html"
        )
        
        return data

#===================================Settlements================================
class settlementsRepo(BaseRepository):
    async def add_debt(Self, debt: feature.DebtCreate, user=User):
        data = await manage_settlements.add_debt(Self, debt_data=debt, user_id=user.id)
        if not data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Unable to add settlement record.")
        await NotificationService(Self.tasks).send_mail(
            recipients=[user.email],
            subject="Your Data Added Succesfully.",
            context_data={
                "id":data.id,
                "person":data.person_name,
                "amount":data.amount,
                "type":data.debt_type.value,
                "Status":data.debt_status.value,
                "date":data.debt_date
            },
            template_name="mail_add_debt.html"
        )
        return data

    async def view_debt(self, user_id: uuid.UUID) -> list[feature.DebtResponse]:
        return await manage_settlements.view_debts(self, user_id)

    async def update_debt(Self, debt_id: int, debt: feature.DebtUpdate, user=User):
        data= await manage_settlements.update_debt(Self, debt_id, debt, user.id)
        await NotificationService(Self.tasks).send_mail(
            recipients=[user.email],
            subject="Your Settlement Update Succesfully.",
            context_data={
                "id":data.id,
                "person":data.person_name,
                "amount":data.amount,
                "type":data.debt_type.value,
                "Status":data.debt_status.value,
                "date":data.debt_date
            },
            template_name="mail_update_debt.html"
        )

        return data

    async def delete_debt(Self, debt_id: int, user:User):
        data= await manage_settlements.delete_debt(Self, debt_id, user.id)
        await NotificationService(Self.tasks).send_mail(
            recipients=[user.email],
            subject="Your Settlement Update Succesfully.",
            context_data={
                "id":data.id,
                "person":data.person_name,
                "amount":data.amount,
                "type":data.debt_type.value,
            },
            template_name="mail_del_debt.html"
        )
        return data
