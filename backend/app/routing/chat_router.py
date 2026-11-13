from fastapi import APIRouter,Depends,HTTPException,status
from ..security.deps import get_current_user
from ..schemas.chatbot import user_message,assistant_message
from ..ai import agent
from ..repository.featureRepo import expensesRepo,tag_repo,settlementsRepo
ai=APIRouter(prefix="/ai",tags=["ExpenseAI"])

@ai.post("/chat")
async def chat(prompt:user_message,
               expenseobj:expensesRepo= Depends(),
               tagObj:tag_repo=Depends(),
               debtObj:settlementsRepo=Depends(),
               curr_user=Depends(get_current_user)):
    data=await agent.agent_call(prompt,{"expense_repo": expenseobj,
                                        "tag_repo": tagObj,
                                        "debt_repo":debtObj,
                                        "current_user":curr_user})
    if not data:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Hey Sorry This Feature Dont Exist Yet")
    return data

