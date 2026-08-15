# app/ai/tools.py
from ..repository.featureRepo import expensesRepo,features
from fastapi import Depends

import uuid
from ..schemas import feature as tool
async def add_expense_tool(data:tool.ExpenseCreate,
                           user_id: uuid.UUID,
                           to_expense:expensesRepo=Depends()):
    return await to_expense.add_expense(expense_data=data,user_id=user_id)


async def add_tag_tool(data:tool.TagCreate,
                        user_id: uuid.UUID,
                        to_tag:features=Depends()):

    return await to_tag.add_tags(tag=data,user_id=user_id)


async def get_expense_summary_tool(user_id:uuid.UUID,
                                   to_expense:expensesRepo=Depends()):
    return await to_expense.view_expense(user_id=user_id)


async def get_tag_summary_tool(user_id:uuid.UUID,
                               to_tag:features=Depends()):
    return await to_tag.view_tags(user_id=user_id)


READ_TOOLS = {"get_expense_summary_tool","get_tag_summary_tool"}    
WRITE_TOOLS = {"add_expense_tool","add_tag_tool"}           