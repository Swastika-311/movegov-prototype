import pytest

from app.core.rules import CONDITIONS, SERVICE_RULES, evaluate_service_rules, recommendation_service_ids
from pydantic import ValidationError
from app.api.schemas.models import RelocationCreate

def test_benefits(): assert 'benefit_portability' in recommendation_service_ids({'move_type':'Permanent','voter':False,'vehicle':False,'benefits':True,'student':False})
def test_temporary():
    ids=recommendation_service_ids({'move_type':'Temporary','voter':True,'vehicle':True,'benefits':True,'student':False}); assert ids==[]


def service_map(profile):
    return {result['service_id']: result for result in evaluate_service_rules(profile)}


@pytest.mark.parametrize(
    ('profile', 'expected_ids'),
    [
        ({'move_type': 'permanent', 'vehicle': True, 'voter': True, 'benefits': True}, {'aadhaar_address', 'voter_residence', 'vehicle_rc_address', 'driving_license_address', 'benefit_portability', 'pan_address_review'}),
        ({'move_type': 'permanent', 'vehicle': True, 'voter': True, 'benefits': False}, {'aadhaar_address', 'voter_residence', 'vehicle_rc_address', 'driving_license_address', 'pan_address_review'}),
        ({'move_type': 'permanent', 'vehicle': False, 'voter': True, 'benefits': True}, {'aadhaar_address', 'voter_residence', 'driving_license_address', 'benefit_portability', 'pan_address_review'}),
        ({'move_type': 'permanent', 'vehicle': False, 'voter': False, 'benefits': False}, {'aadhaar_address', 'driving_license_address', 'pan_address_review'}),
        ({'move_type': 'temporary', 'vehicle': True, 'voter': True, 'benefits': True}, set()),
        ({'move_type': 'permanent', 'move_scope': 'interstate', 'vehicle': True, 'voter': True, 'benefits': True}, {'aadhaar_address', 'voter_residence', 'vehicle_rc_address', 'driving_license_address', 'benefit_portability', 'pan_address_review'}),
        ({'move_type': 'permanent', 'move_scope': 'intra_state', 'vehicle': True, 'voter': True, 'benefits': True}, {'aadhaar_address', 'voter_residence', 'vehicle_rc_address', 'driving_license_address', 'benefit_portability', 'pan_address_review'}),
        ({'move_type': 'permanent', 'move_scope': 'interstate', 'vehicle': False, 'voter': True}, {'aadhaar_address', 'voter_residence', 'driving_license_address', 'pan_address_review'}),
        ({'move_type': 'permanent', 'move_scope': 'intra_state', 'vehicle': False, 'voter': False}, {'aadhaar_address', 'driving_license_address', 'pan_address_review'}),
        ({'move_type': 'permanent'}, {'aadhaar_address', 'driving_license_address', 'pan_address_review'}),
    ],
)
def test_composed_applicability_matrix(profile, expected_ids):
    """Independent predicates compose without per-combination rule branches."""
    assert set(service_map(profile)) == expected_ids


def test_each_service_declares_named_independent_conditions():
    assert all(rule['conditions'] for rule in SERVICE_RULES)
    assert all(name in CONDITIONS for rule in SERVICE_RULES for name in rule['conditions'])


def test_result_includes_rule_explanation_and_jurisdiction_context():
    result = service_map({'move_type': 'permanent', 'move_scope': 'interstate', 'vehicle': True})['vehicle_rc_address']
    assert result['applicability'] == 'required'
    assert result['matched_conditions'] == ['permanent_move', 'vehicle_owned', 'interstate']
    assert result['jurisdiction_relevance'] == 'interstate relocation'
    assert result['reason']


def test_pan_is_review_not_an_always_mandatory_update():
    assert service_map({'move_type': 'permanent'})['pan_address_review']['applicability'] == 'review'


def test_known_states_override_a_conflicting_supplied_scope():
    result = service_map({'move_type': 'permanent', 'origin_state': 'Uttar Pradesh', 'destination_state': 'Uttar Pradesh', 'move_scope': 'interstate'})['aadhaar_address']
    assert result['jurisdiction_relevance'] == 'intra-state relocation'
    assert 'intra_state' in result['matched_conditions']