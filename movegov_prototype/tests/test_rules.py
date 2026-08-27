from app.core.rules import recommendation_service_ids

def test_permanent_voter(): assert 'voter_residence' in recommendation_service_ids({'move_type':'Permanent','voter':True,'vehicle':False,'benefits':False,'student':False})
def test_permanent_vehicle(): assert 'vehicle_rc_address' in recommendation_service_ids({'move_type':'Permanent','voter':False,'vehicle':True,'benefits':False,'student':False})
def test_no_vehicle(): assert 'vehicle_rc_address' not in recommendation_service_ids({'move_type':'Permanent','voter':True,'vehicle':False,'benefits':False,'student':False})
def test_no_voter(): assert 'voter_residence' not in recommendation_service_ids({'move_type':'Permanent','voter':False,'vehicle':True,'benefits':False,'student':False})
def test_benefits(): assert 'benefit_portability' in recommendation_service_ids({'move_type':'Permanent','voter':False,'vehicle':False,'benefits':True,'student':False})
def test_temporary():
    ids=recommendation_service_ids({'move_type':'Temporary','voter':True,'vehicle':True,'benefits':True,'student':False}); assert ids==[]
