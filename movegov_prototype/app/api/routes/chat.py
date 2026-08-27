from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.core.recommendation_engine import build_recommendations
from app.agents.movegov_agent import ask
from app.api.schemas.models import ChatRequest
router=APIRouter(prefix='/chat',tags=['chat'])
@router.post('')
def chat(payload:ChatRequest,db:Session=Depends(get_db)):
    u=db.get(User,payload.user_id)
    if not u: raise HTTPException(404,'User not found')
    recs=build_recommendations(db,u)
    apps=[{'service_id':a.service.service_id,'status':a.status} for a in u.applications]
    return ask(payload.message,{'current_city':u.current_city,'destination_city':u.destination_city,'move_type':u.move_type},recs,apps)
