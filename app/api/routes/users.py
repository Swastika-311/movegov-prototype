from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, UserProfile
from app.api.schemas.models import UserCreate
router=APIRouter(prefix='/users',tags=['users'])
@router.post('')
def create_user(payload: UserCreate, db: Session=Depends(get_db)):
    u=User(name=payload.name,current_city=payload.origin_city,destination_city=payload.destination_city,state=payload.destination_state,origin_city=payload.origin_city,origin_state=payload.origin_state,destination_state=payload.destination_state,move_scope=payload.move_scope,move_date=payload.move_date,move_type=payload.move_type,reason=payload.reason); db.add(u); db.flush(); db.add(UserProfile(user_id=u.id,vehicle=payload.vehicle,voter=payload.voter,benefits=payload.benefits,student=payload.student,property=payload.property)); db.commit(); return {'id':u.id,'move_scope':u.move_scope}@router.get('/{user_id}')
def get_user(user_id:int,db:Session=Depends(get_db)):
    u=db.get(User,user_id)
    if not u: raise HTTPException(404,'User not found')
    origin_city=u.origin_city or u.current_city; origin_state=u.origin_state or u.state; destination_state=u.destination_state or u.state
    move_scope='intra_state' if origin_state.casefold() == destination_state.casefold() else 'interstate'
    return {'id':u.id,'name':u.name,'origin_city':origin_city,'origin_state':origin_state,'destination_city':u.destination_city,'destination_state':destination_state,'move_scope':move_scope,'current_city':origin_city,'state':destination_state,'move_date':u.move_date,'move_type':u.move_type,'reason':u.reason,'profile':{'vehicle':u.profile.vehicle,'voter':u.profile.voter,'benefits':u.profile.benefits,'student':u.profile.student,'property':u.profile.property}}@router.post('/{user_id}/profile')
def update_profile(user_id:int,payload:dict,db:Session=Depends(get_db)):
    u=db.get(User,user_id)
    if not u: raise HTTPException(404,'User not found')
    for k in ['vehicle','voter','benefits','student','property']:
        if k in payload: setattr(u.profile,k,bool(payload[k]))
    db.commit(); return {'status':'updated'}
