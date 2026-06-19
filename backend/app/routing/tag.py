from fastapi import APIRouter,Depends,HTTPException,status,Response, Request
from ..repository.featureRepo import features
from ..Security import deps as jwt
from ..schemas import feature
from ..model import models

tags = APIRouter(prefix="/tags",tags=["Tag_manager"])
from ..rate_limiter import limiter

@tags.get("/view_tags", response_model=list[feature.TagResponse])
@limiter.limit("120/minute")
async def view_tags(request: Request,
                    response:Response,
                     feature_repo: features = Depends(),
                    current_user:models.User = Depends(jwt.get_current_user)):
    data= await feature_repo.view_tags(user_id=current_user.id)
    return data
    

@tags.post("/add_tags")
@limiter.limit("120/minute")
async def add_tags(request: Request,
                   response:Response,
    tag: feature.TagCreate,
    feature_repo: features = Depends(),
    current_user: models.User = Depends(jwt.get_current_user)):
   
    new_tag = await feature_repo.add_tags(tag=tag, user_id=current_user.id)
    return {"Message":"Succesfully Added",
            "tag":new_tag}

@tags.delete("/delete_tag")
@limiter.limit("120/minute")
async def del_tags(request: Request, 
                   response:Response,
                   tag: str,
                   feature_repo: features = Depends(),
                   current_user: models.User = Depends(jwt.get_current_user)):
    
    data=await feature_repo.del_tag(tag_name=tag.lower(), user= current_user.id)
    if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No data found")
    return {"Message":"Deleted"}
    