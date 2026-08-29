import json
from datetime import date
from pathlib import Path
from sqlalchemy.orm import Session
from .models import GovernmentService, ServiceRequirement, ServiceDependency, Source

ROOT = Path(__file__).resolve().parents[2]


def sync_catalog(db: Session) -> int:
    """Upsert the bundled official government-service catalog into the local DB."""
    data = json.loads((ROOT / 'data' / 'services.json').read_text(encoding='utf-8'))
    count = 0
    for item in data:
        service = db.query(GovernmentService).filter_by(service_id=item['service_id']).first()
        if service is None:
            service = GovernmentService(service_id=item['service_id'])
            db.add(service)
            db.flush()

        for key in (
            'service_name', 'department', 'category', 'description',
            'trigger_conditions', 'applicability', 'priority', 'why_relevant',
            'process', 'official_url', 'source_url'
        ):
            setattr(service, key, item[key])
        service.source_last_verified = date.fromisoformat(item['source_last_verified'])
        db.flush()

        db.query(ServiceRequirement).filter_by(service_id=service.id).delete(synchronize_session=False)
        db.query(ServiceDependency).filter_by(service_id=service.id).delete(synchronize_session=False)
        db.query(Source).filter_by(service_id=service.id).delete(synchronize_session=False)

        for req in item.get('requirements', []):
            db.add(ServiceRequirement(service_id=service.id, **req))
        for dep in item.get('dependencies', []):
            db.add(ServiceDependency(service_id=service.id, **dep))
        db.add(Source(
            service_id=service.id,
            source_name=item['department'],
            source_url=item['source_url'],
            source_type='official',
            verified_date=service.source_last_verified,
        ))
        count += 1

    db.commit()
    return count
