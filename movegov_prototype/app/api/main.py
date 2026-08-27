from fastapi import FastAPI
from app.db.database import Base, engine
from app.db.seed import seed_if_empty
from app.api.routes import users, services, recommendations, applications, chat, relocation
Base.metadata.create_all(bind=engine)
seed_if_empty()
app = FastAPI(title='MoveGov API', version='1.0.0')
app.include_router(users.router); app.include_router(relocation.router); app.include_router(services.router); app.include_router(recommendations.router); app.include_router(applications.router); app.include_router(chat.router)
@app.get('/health')
def health(): return {'status':'ok','product':'MoveGov'}
