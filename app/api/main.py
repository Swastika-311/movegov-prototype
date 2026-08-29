from fastapi import FastAPI
from app.db.database import Base, SessionLocal, engine
from app.db.seed import seed_if_empty
from app.db.catalog_sync import sync_catalog
from app.api.routes import users, services, recommendations, applications, chat, relocation

Base.metadata.create_all(bind=engine)
seed_if_empty()
# Also synchronize an existing local database so a stale movegov.db cannot
# produce an empty personalized dashboard after the bundled catalog changes.
db = SessionLocal()
try:
    sync_catalog(db)
finally:
    db.close()

app = FastAPI(title='MoveGov API', version='1.0.0')
app.include_router(users.router)
app.include_router(relocation.router)
app.include_router(services.router)
app.include_router(recommendations.router)
app.include_router(applications.router)
app.include_router(chat.router)


@app.get('/health')
def health():
    return {'status': 'ok', 'product': 'MoveGov'}
