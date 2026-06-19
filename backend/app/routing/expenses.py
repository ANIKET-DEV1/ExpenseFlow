from fastapi import APIRouter,Depends,HTTPException, Request,status,Response
from ..Security.deps import get_current_user
from ..schemas import feature
from ..repository.featureRepo import expensesRepo
from ..model import models
from ..rate_limiter import limiter
from ..utils.cache import cache_service

expense = APIRouter(prefix="/expenses",tags=["Expense_Manager"])


@expense.get("/view_expenses",response_model=list[feature.ExpenseResponse])
@limiter.limit("120/minute")
async def view_expense(request:Request,
                       response: Response,
                       expenseobj:expensesRepo=Depends(), 
                       current_user:models.User=Depends(get_current_user)):
    cache_key = f"user:{current_user.id}:expenses"
    #Check REDISSS
    cached_expenses = cache_service.get(cache_key)
    if cached_expenses:
        return cached_expenses
    #IF NOT FOUND THEN GOES TO DB
    data= await expenseobj.view_expense(current_user.id)
    #PUT IN CACHE
    serializable_data = [
        feature.ExpenseResponse.model_validate(item).model_dump(mode="json") 
        for item in data
    ]
    cache_service.set(cache_key, serializable_data, expire_seconds=300)

    return data
    

@expense.post("/add_expenses",response_model=feature.ExpenseResponse)
@limiter.limit("120/minute")
async def add_expense(request: Request, expense: feature.ExpenseCreate,
                      response: Response,
                       expenseobj:expensesRepo=Depends(), 
                       current_user:models.User=Depends(get_current_user)):
    
    data = await expenseobj.add_expense(expense, current_user)
    if not data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error!")
    cache_key = f"user:{current_user.id}:expenses"
    cache_service.delete(cache_key)

    return data

@expense.delete("/delete_expense")
@limiter.limit("120/minute")
async def del_expense(request: Request, response: Response,
                      expenseId:int, 
                      expenseobj:expensesRepo=Depends(), 
                      current_user:models.User=Depends(get_current_user)):
    cache_key = f"user:{current_user.id}:expenses"
    data= await expenseobj.del_expense(expenseId,current_user)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    cache_service.delete(cache_key)
    return {"Deleted":data}
    
