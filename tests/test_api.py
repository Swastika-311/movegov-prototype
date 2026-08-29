import os
os.environ['DATABASE_URL']='sqlite:///./test_movegov.db'
from fastapi.testclient import TestClient
from app.db.database import Base, engine
Base.metadata.create_all(engine)
from app.db.seed import seed_if_empty
seed_if_empty()
from app.api.main import app
client=TestClient(app)

def test_health(): assert client.get('/health').status_code==200

def test_sources_attached():
    r=client.get('/recommendations/1'); assert r.status_code==200; assert all(x['source']['url'] for x in r.json())

def test_recommendations_include_deterministic_rule_explanations():
    r=client.get('/recommendations/1'); assert r.status_code==200
    assert all({'service_id','applicability','reason','matched_conditions','priority','dependencies','jurisdiction_relevance'} <= item.keys() for item in r.json())
    assert {item['applicability'] for item in r.json()} <= {'required','may_apply','review'}

def test_dependencies():
    r=client.get('/services/voter_residence'); assert r.status_code==200; assert r.json()['dependencies']

def test_application_status_changes():
    r=client.post('/applications',json={'user_id':1,'service_id':'voter_residence'}); assert r.status_code==200
    aid=r.json()['id']; r=client.patch(f'/applications/{aid}',json={'status':'Submitted'}); assert r.json()['status']=='Submitted'

def test_unknown_info_no_hallucination():
    r=client.post('/chat',json={'user_id':1,'message':'What is the exact fee and deadline for a fictional MoveGov service?'})
    assert 'could not be verified' in r.json()['answer'].lower() or r.json()['sources']
