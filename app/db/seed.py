import json
from datetime import date
from pathlib import Path
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, UserProfile, GovernmentService, ServiceRequirement, ServiceDependency, Source
ROOT=Path(__file__).resolve().parents[2]

def seed_if_empty():
    db=SessionLocal()
    try:
        if db.query(GovernmentService).count()==0:
            data=json.loads((ROOT/'data/services.json').read_text())
            for x in data:
                s=GovernmentService(service_id=x['service_id'],service_name=x['service_name'],department=x['department'],category=x['category'],description=x['description'],trigger_conditions=x['trigger_conditions'],applicability=x['applicability'],priority=x['priority'],why_relevant=x['why_relevant'],process=x['process'],official_url=x['official_url'],source_url=x['source_url'],source_last_verified=date.fromisoformat(x['source_last_verified']))
                db.add(s); db.flush()
                for r in x['requirements']: db.add(ServiceRequirement(service_id=s.id,**r))
                for d in x['dependencies']: db.add(ServiceDependency(service_id=s.id,**d))
                db.add(Source(service_id=s.id,source_name=x['department'],source_url=x['source_url'],source_type='official',verified_date=s.source_last_verified))
            db.commit()
        if not db.query(User).filter_by(name='Demo Citizen').first():
            u=User(name='Demo Citizen',current_city='Prayagraj',destination_city='Lucknow',state='Uttar Pradesh',origin_city='Prayagraj',origin_state='Uttar Pradesh',destination_state='Uttar Pradesh',move_scope='intra_state',move_date=date.today(),move_type='permanent',reason='Employment')
            db.add(u); db.flush(); db.add(UserProfile(user_id=u.id,vehicle=True,voter=True,benefits=True,student=False,property=False)); db.commit()
    finally: db.close()
