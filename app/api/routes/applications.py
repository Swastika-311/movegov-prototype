from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, GovernmentService, Application
from app.api.schemas.models import ApplicationCreate, ApplicationPatch

router = APIRouter(prefix='/applications', tags=['applications'])
VALID = {'Not Started', 'Preparing', 'Submitted', 'Under Processing', 'Action Required', 'Completed'}


@router.post('')
def create(payload: ApplicationCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(404, 'User not found')
    s = db.query(GovernmentService).filter_by(service_id=payload.service_id).first()
    if not s:
        raise HTTPException(404, 'Service not found')
    existing = db.query(Application).filter_by(user_id=payload.user_id, service_id=s.id).first()
    if existing:
        return {'id': existing.id, 'status': existing.status, 'service_id': s.service_id}
    a = Application(user_id=payload.user_id, service_id=s.id)
    db.add(a)
    db.commit()
    db.refresh(a)
    return {'id': a.id, 'status': a.status, 'service_id': s.service_id}


@router.patch('/{application_id}')
def patch(application_id: int, payload: ApplicationPatch, db: Session = Depends(get_db)):
    if payload.status not in VALID:
        raise HTTPException(400, 'Invalid status')
    a = db.get(Application, application_id)
    if not a:
        raise HTTPException(404, 'Application not found')
    a.status = payload.status
    db.commit()
    db.refresh(a)
    return {'id': a.id, 'status': a.status}


@router.get('/{user_id}')
def list_user(user_id: int, db: Session = Depends(get_db)):
    if not db.get(User, user_id):
        raise HTTPException(404, 'User not found')
    return [
        {'id': a.id, 'service_id': a.service.service_id, 'service_name': a.service.service_name, 'status': a.status}
        for a in db.query(Application).filter_by(user_id=user_id).all()
    ]
