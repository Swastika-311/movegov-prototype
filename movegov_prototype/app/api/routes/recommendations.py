from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.core.recommendation_engine import build_recommendations
router=APIRouter(prefix='/recommendations',tags=['recommendations'])
@router.post('')
def recommendations(user_id:int,db:Session=Depends(get_db)):
    u=db.get(User,user_id)
    if not u: raise HTTPException(404,'User not found')
    return build_recommendations(db,u)
@router.get('/{user_id}')
def get_recommendations(user_id:int,db:Session=Depends(get_db)):
    u=db.get(User,user_id)
    if not u: raise HTTPException(404,'User not found')
    return build_recommendations(db,u)
@router.get('/{user_id}/dependencies/{service_id}')
def dependencies(user_id:int,service_id:str,db:Session=Depends(get_db)):
    from app.core.dependency_engine import get_dependencies
    if not db.get(User,user_id): raise HTTPException(404,'User not found')
    return get_dependencies(db,service_id)
