from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.api.schemas.models import RelocationCreate
router=APIRouter(prefix='/relocation',tags=['relocation'])
@router.post('')
def create_relocation(payload:RelocationCreate,db:Session=Depends(get_db)):
    u=User(name='Relocation Citizen',current_city=payload.origin_city,destination_city=payload.destination_city,state=payload.destination_state,origin_city=payload.origin_city,origin_state=payload.origin_state,destination_state=payload.destination_state,move_scope=payload.move_scope,move_date=payload.move_date,move_type=payload.move_type,reason=payload.reason)
    db.add(u); db.commit(); db.refresh(u); return {'id':u.id,'origin_city':u.origin_city,'origin_state':u.origin_state,'destination_city':u.destination_city,'destination_state':u.destination_state,'move_scope':u.move_scope,'move_type':u.move_type}
@router.get('/{relocation_id}')
def get_relocation(relocation_id:int,db:Session=Depends(get_db)):
    u=db.get(User,relocation_id)
    if not u: raise HTTPException(404,'Relocation not found')
    origin_city=u.origin_city or u.current_city; origin_state=u.origin_state or u.state; destination_state=u.destination_state or u.state
    return {'id':u.id,'origin_city':origin_city,'origin_state':origin_state,'destination_city':u.destination_city,'destination_state':destination_state,'move_scope':'intra_state' if origin_state.casefold() == destination_state.casefold() else 'interstate','move_date':u.move_date,'move_type':u.move_type,'reason':u.reason}