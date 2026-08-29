import json
import os
from pathlib import Path

os.environ['DATABASE_URL'] = 'sqlite:///./test_movegov.db'

from fastapi.testclient import TestClient
from app.db.database import Base, engine
from app.db.seed import seed_if_empty
from app.api.main import app

Base.metadata.create_all(engine)
seed_if_empty()
client = TestClient(app)


def demo_user_id():
    r = client.post('/users', json={
        'name': 'Test Citizen', 'current_city': 'Prayagraj', 'destination_city': 'Lucknow',
        'state': 'Uttar Pradesh', 'move_date': '2026-09-01', 'move_type': 'Permanent',
        'reason': 'Employment', 'vehicle': True, 'voter': True, 'benefits': True,
    })
    assert r.status_code == 200
    return r.json()['id']


def test_health():
    assert client.get('/health').status_code == 200


def test_government_dataset_has_required_official_records():
    path = Path(__file__).parents[1] / 'data' / 'government_data_catalog.json'
    data = json.loads(path.read_text())
    assert len(data['records']) >= 6
    assert all(x['official_service_url'].startswith('https://') for x in data['records'])
    assert all(x['official_source_url'].startswith('https://') for x in data['records'])


def test_sources_attached():
    uid = demo_user_id()
    r = client.get(f'/recommendations/{uid}')
    assert r.status_code == 200
    assert all(x['source']['url'] for x in r.json())


def test_dependencies():
    r = client.get('/services/voter_residence')
    assert r.status_code == 200
    assert r.json()['dependencies']
    assert r.json()['dependencies'][0]['service_id'] == 'address_proof'


def test_relocation_update_preserves_user_identity_and_profile():
    uid = demo_user_id()
    before = client.get(f'/users/{uid}').json()
    r = client.patch(f'/relocation/{uid}', json={
        'current_city': 'Prayagraj', 'destination_city': 'Kanpur', 'state': 'Uttar Pradesh',
        'move_date': '2026-09-10', 'move_type': 'Permanent', 'reason': 'Employment',
    })
    assert r.status_code == 200
    after = client.get(f'/users/{uid}').json()
    assert after['id'] == before['id'] == uid
    assert after['destination_city'] == 'Kanpur'
    assert 'profile' in after


def test_application_creation_is_idempotent():
    uid = demo_user_id()
    payload = {'user_id': uid, 'service_id': 'voter_residence'}
    first = client.post('/applications', json=payload)
    second = client.post('/applications', json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json()['id'] == second.json()['id']


def test_application_status_changes():
    uid = demo_user_id()
    r = client.post('/applications', json={'user_id': uid, 'service_id': 'voter_residence'})
    assert r.status_code == 200
    aid = r.json()['id']
    r = client.patch(f'/applications/{aid}', json={'status': 'Submitted'})
    assert r.status_code == 200
    assert r.json()['status'] == 'Submitted'


def test_unknown_info_no_hallucination():
    uid = demo_user_id()
    r = client.post('/chat', json={'user_id': uid, 'message': 'What is the exact fee and deadline for a fictional MoveGov service?'})
    assert r.status_code == 200
    assert 'could not be verified' in r.json()['answer'].lower() or r.json()['sources']
