from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import GovernmentService
from app.core.dependency_engine import get_dependencies
router=APIRouter(prefix='/services',tags=['services'])
@router.get('')
def list_services(db:Session=Depends(get_db)):
    return db.query(GovernmentService).all()
@router.get('/{service_id}')
def service(service_id:str,db:Session=Depends(get_db)):
    s=db.query(GovernmentService).filter_by(service_id=service_id).first()
    if not s: raise HTTPException(404,'Service not found')
    return {'service_id':s.service_id,'service_name':s.service_name,'department':s.department,'description':s.description,'applicability':s.applicability,'priority':s.priority,'why_relevant':s.why_relevant,'requirements':[{'requirement':r.requirement,'description':r.description} for r in s.requirements],'dependencies':get_dependencies(db,service_id),'process':s.process,'official_url':s.official_url,'source_url':s.source_url,'source_last_verified':s.source_last_verified}
