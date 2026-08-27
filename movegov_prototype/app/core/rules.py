SERVICES = {
    'voter_residence': lambda p: p['move_type'].lower() == 'permanent' and p['voter'],
    'vehicle_rc_address': lambda p: p['move_type'].lower() == 'permanent' and p['vehicle'],
    'aadhaar_address': lambda p: p['move_type'].lower() == 'permanent',
    'benefit_portability': lambda p: p['move_type'].lower() == 'permanent' and p['benefits'],
    'pan_address_review': lambda p: p['move_type'].lower() == 'permanent',
    'driving_license_address': lambda p: p['move_type'].lower() == 'permanent',
}

def recommendation_service_ids(profile: dict) -> list[str]:
    return [sid for sid, rule in SERVICES.items() if rule(profile)]
