from sqlalchemy.orm import Session
from app.db.models import GovernmentService, User
from .rules import evaluate_service_rules

def build_recommendations(db: Session, user: User):
    profile = user.profile
    if not profile:
        return []
    p = {'move_type':user.move_type,'move_scope':user.move_scope,'origin_state':user.origin_state,'destination_state':user.destination_state,'vehicle':profile.vehicle,'voter':profile.voter,'benefits':profile.benefits,'student':profile.student,'property':profile.property}
    rule_results = evaluate_service_rules(p)
    ids = [r['service_id'] for r in rule_results]
    services = {s.service_id: s for s in db.query(GovernmentService).filter(GovernmentService.service_id.in_(ids)).all()}
    result = []
    for rule_result in rule_results:
        sid = rule_result['service_id']
        s = services.get(sid)
        if not s: continue
        result.append({'service_id':s.service_id,'service_name':s.service_name,'priority':s.priority,'applicability':rule_result['applicability'],'reason':rule_result['reason'],'matched_conditions':rule_result['matched_conditions'],'jurisdiction_relevance':rule_result['jurisdiction_relevance'],'dependencies':[{'service_id':d.dependency_service_id,'description':d.dependency_description} for d in s.dependencies],'source':{'name':s.department,'url':s.source_url}})
    return result