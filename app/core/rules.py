from collections.abc import Callable
Condition = Callable[[dict], bool]

def _normalized(value: object) -> str: return str(value or '').strip().casefold()
def _move_scope(profile: dict) -> str:
    origin, destination = _normalized(profile.get('origin_state')), _normalized(profile.get('destination_state'))
    if origin and destination: return 'intra_state' if origin == destination else 'interstate'
    explicit = _normalized(profile.get('move_scope'))
    return explicit if explicit in {'intra_state', 'interstate'} else 'unknown'

CONDITIONS: dict[str, Condition] = {
    'permanent_move': lambda p: _normalized(p.get('move_type')) == 'permanent',
    'temporary_move': lambda p: _normalized(p.get('move_type')) == 'temporary',
    'intra_state': lambda p: _move_scope(p) == 'intra_state', 'interstate': lambda p: _move_scope(p) == 'interstate',
    'vehicle_owned': lambda p: bool(p.get('vehicle', False)), 'voter_registered': lambda p: bool(p.get('voter', False)),
    'benefits_relevant': lambda p: bool(p.get('benefits', False)), 'student': lambda p: bool(p.get('student', False)), 'property_review': lambda p: bool(p.get('property', False)),
}
# Applicability only; verified requirements and source material remain in data/services.json.
SERVICE_RULES = (
    {'service_id':'aadhaar_address','conditions':('permanent_move',),'applicability':'may_apply','reason':'A permanent relocation may make the address recorded in Aadhaar outdated; review the verified service guidance before acting.'},
    {'service_id':'voter_residence','conditions':('permanent_move','voter_registered'),'applicability':'required','reason':'You reported a permanent relocation and voter registration, so a residence-shifting action is relevant.'},
    {'service_id':'vehicle_rc_address','conditions':('permanent_move','vehicle_owned'),'applicability':'required','reason':'You reported a permanent relocation and vehicle ownership, so the registered vehicle address should be reviewed through the applicable official workflow.'},
    {'service_id':'driving_license_address','conditions':('permanent_move',),'applicability':'may_apply','reason':'A permanent relocation may make the driving-licence address relevant to review; availability and requirements depend on the applicable state workflow.'},
    {'service_id':'benefit_portability','conditions':('permanent_move','benefits_relevant'),'applicability':'may_apply','reason':'You reported benefits or entitlements, so portability and destination-record arrangements may need review.'},
    {'service_id':'pan_address_review','conditions':('permanent_move',),'applicability':'review','reason':'A permanent move can affect address-linked PAN records or jurisdiction; this is a review action, not a claim that an update is always mandatory.'},
)
def jurisdiction_relevance(profile: dict) -> str:
    return {'interstate':'interstate relocation','intra_state':'intra-state relocation'}.get(_move_scope(profile),'relocation scope not yet confirmed')
def evaluate_service_rules(profile: dict) -> list[dict]:
    scope, results = _move_scope(profile), []
    for rule in SERVICE_RULES:
        if all(CONDITIONS[name](profile) for name in rule['conditions']):
            matched=list(rule['conditions']) + ([scope] if scope in {'intra_state','interstate'} else [])
            results.append({'service_id':rule['service_id'],'applicability':rule['applicability'],'reason':rule['reason'],'matched_conditions':matched,'jurisdiction_relevance':jurisdiction_relevance(profile)})
    return results
def recommendation_service_ids(profile: dict) -> list[str]: return [r['service_id'] for r in evaluate_service_rules(profile)]