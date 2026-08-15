from fastapi import APIRouter,Depends,HTTPException,status
from ..security.deps import get_current_user
from ..ai import agent
ai=APIRouter(prefix="/ai",tags=["ExpenseAI"])

@ai.post("/chat")
async def chat(prompt:str,curr_user=Depends(get_current_user)):
    data=await agent.ask_gemini_with_tools(message=prompt)
    if not data:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Hey Sorry This Feature Dont Exist Yet")
    return data

