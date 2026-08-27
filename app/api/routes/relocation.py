from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.api.schemas.models import RelocationCreate
router=APIRouter(prefix='/relocation',tags=['relocation'])
@router.post('')
def create_relocation(payload:RelocationCreate,db:Session=Depends(get_db)):
    u=User(name='Relocation Citizen',current_city=payload.current_city,destination_city=payload.destination_city,state=payload.state,move_date=payload.move_date,move_type=payload.move_type,reason=payload.reason)
    db.add(u); db.commit(); db.refresh(u); return {'id':u.id,'current_city':u.current_city,'destination_city':u.destination_city,'move_type':u.move_type}
@router.get('/{relocation_id}')
def get_relocation(relocation_id:int,db:Session=Depends(get_db)):
    u=db.get(User,relocation_id)
    if not u: raise HTTPException(404,'Relocation not found')
    return {'id':u.id,'current_city':u.current_city,'destination_city':u.destination_city,'state':u.state,'move_date':u.move_date,'move_type':u.move_type,'reason':u.reason}
