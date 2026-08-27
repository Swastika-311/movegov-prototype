from sqlalchemy.orm import Session
from app.db.models import GovernmentService, User, UserProfile
from .rules import recommendation_service_ids

def build_recommendations(db: Session, user: User):
    profile = user.profile
    if not profile:
        return []
    p = {'move_type': user.move_type, 'vehicle': profile.vehicle, 'voter': profile.voter, 'benefits': profile.benefits, 'student': profile.student}
    ids = recommendation_service_ids(p)
    services = {s.service_id: s for s in db.query(GovernmentService).filter(GovernmentService.service_id.in_(ids)).all()}
    result = []
    for sid in ids:
        s = services.get(sid)
        if not s: continue
        result.append({'service_id':s.service_id,'service_name':s.service_name,'priority':s.priority,'applicability':s.applicability,'reason':s.why_relevant,'dependencies':[{'service_id':d.dependency_service_id,'description':d.dependency_description} for d in s.dependencies],'source':{'name':s.department,'url':s.source_url}})
    return result
