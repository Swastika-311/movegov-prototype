from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, UserProfile
from app.api.schemas.models import RelocationCreate

router = APIRouter(prefix='/relocation', tags=['relocation'])


def _payload(user: User):
    return {
        'id': user.id,
        'name': user.name,
        'current_city': user.current_city,
        'destination_city': user.destination_city,
        'state': user.state,
        'move_date': user.move_date,
        'move_type': user.move_type,
        'reason': user.reason,
    }


@router.post('')
def create_relocation(payload: RelocationCreate, db: Session = Depends(get_db)):
    u = User(
        name='Relocation Citizen',
        current_city=payload.current_city,
        destination_city=payload.destination_city,
        state=payload.state,
        move_date=payload.move_date,
        move_type=payload.move_type,
        reason=payload.reason,
    )
    db.add(u)
    db.flush()
    db.add(UserProfile(user_id=u.id))
    db.commit()
    db.refresh(u)
    return _payload(u)


@router.patch('/{relocation_id}')
def update_relocation(relocation_id: int, payload: RelocationCreate, db: Session = Depends(get_db)):
    u = db.get(User, relocation_id)
    if not u:
        raise HTTPException(404, 'Relocation not found')
    u.current_city = payload.current_city
    u.destination_city = payload.destination_city
    u.state = payload.state
    u.move_date = payload.move_date
    u.move_type = payload.move_type
    u.reason = payload.reason
    if not u.profile:
        db.add(UserProfile(user_id=u.id))
    db.commit()
    db.refresh(u)
    return _payload(u)


@router.get('/{relocation_id}')
def get_relocation(relocation_id: int, db: Session = Depends(get_db)):
    u = db.get(User, relocation_id)
    if not u:
        raise HTTPException(404, 'Relocation not found')
    return _payload(u)
