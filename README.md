# MoveGov

MoveGov is a life-event government service navigator for citizens permanently moving between Indian cities. The prototype organizes six address-linked government actions into one personalized journey, with deterministic recommendations, dependencies, official-source links, an application tracker, and retrieval-first assistance.

## Scope
- Aadhaar address update
- Voter residence/address update
- Vehicle RC address update
- Driving Licence address update
- Ration/benefit portability review
- PAN/address review

## Architecture
Streamlit → FastAPI → recommendation engine → service knowledge base → dependency engine → application tracker → retrieval-first assistant.

The LLM layer is intentionally behind a small interface. The default assistant is deterministic and metadata-backed so the prototype remains runnable without an API key.

## Quick start
1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open `http://localhost:8501` for the UI or `http://localhost:8000/docs` for the API.

## Local development
Use Python 3.11+, install `requirements.txt`, set `DATABASE_URL` to PostgreSQL (or use the SQLite fallback for tests), then run:
- `uvicorn app.api.main:app --reload`
- `streamlit run frontend/streamlit_app.py`

## Testing
`pytest -q`

## Government-source policy
The structured service records were seeded only with official-source references. Where an exact current requirement could vary by state, RTO, workflow or portal configuration, the product deliberately avoids asserting an exact fact and tells the user to verify it.

## Safety / limitations
MoveGov does not submit applications, access government databases, modify government records, determine legal eligibility, or represent any government department. The tracker is local prototype state only.

> MoveGov is a prototype coordination and navigation layer. It does not directly modify government records or represent official government systems.
