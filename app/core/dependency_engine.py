from sqlalchemy.orm import Session
from app.db.models import GovernmentService

def get_dependencies(db: Session, service_id: str):
    s = db.query(GovernmentService).filter_by(service_id=service_id).first()
    if not s: return None
    return [{'service_id':d.dependency_service_id,'description':d.dependency_description} for d in s.dependencies]
