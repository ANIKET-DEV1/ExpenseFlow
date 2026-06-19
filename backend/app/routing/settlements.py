from fastapi import APIRouter, Depends,Response, Request,Query
from ..Security.deps import get_current_user
from ..repository.featureRepo import settlementsRepo
from ..schemas import feature
from ..utils.cache import cache_service
from ..model import models
from ..rate_limiter import limiter

settlement = APIRouter(prefix="/settlements",tags=["Settlements manager"])

@settlement.get("/View_debt", response_model=list[feature.DebtResponse])
@limiter.limit("120/minute")
async def view_settlement(request: Request,
                          response:Response,
                           settlement_obj: settlementsRepo = Depends(),
                             curr_user: models.User = Depends(get_current_user)):
    cache_key = f"user:{curr_user.id}:settlement"
    cached_settlements = cache_service.get(cache_key)
    if cached_settlements:
        return cached_settlements
    data= await settlement_obj.view_debt(curr_user.id)
    serializable_data = [
        feature.DebtResponse.model_validate(item).model_dump(mode="json") 
        for item in data
    ]
    cache_service.set(cache_key, serializable_data, expire_seconds=300)
    return data

@settlement.post("/Add_debt", response_model=feature.DebtResponse)
@limiter.limit("120/minute")
async def add_settlement(request: Request, 
                         response:Response,
                         settlement: feature.DebtCreate,
                           settlement_obj: settlementsRepo = Depends(), 
                           curr_user: models.User = Depends(get_current_user)):
    data= await settlement_obj.add_debt(settlement, curr_user)
    cache_key = f"user:{curr_user.id}:settlement"
    cache_service.delete(cache_key)
    return data


@settlement.put("/update_debt", response_model=feature.DebtResponse)
@limiter.limit("120/minute")
async def update_settlement(request: Request, 
                            response:Response,
                            settlement: feature.DebtUpdate, 
                            int_id:int ,
                            settlement_obj: settlementsRepo = Depends(), 
                            curr_user: models.User = Depends(get_current_user)):
    cache_key = f"user:{curr_user.id}:settlement"
    data= await settlement_obj.update_debt(int_id, settlement, curr_user)
    cache_service.delete(cache_key)
    return data
@settlement.delete("/delete_debt")
@limiter.limit("120/minute")
async def del_settlement(request: Request,
                         response:Response,
                          del_id: int,
                            settlement_obj: settlementsRepo = Depends(),
                              curr_user: models.User = Depends(get_current_user)):
    cache_key = f"user:{curr_user.id}:settlement"
    deleted = await settlement_obj.delete_debt(del_id, curr_user)
    cache_service.delete(cache_key)
    return {"deleted": True, "id": deleted.id}