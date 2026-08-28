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
Streamlit → FastAPI → PostgreSQL → recommendation engine → service knowledge base → dependency engine → application tracker → retrieval-first assistant.

The LLM layer is intentionally behind a small interface. The default assistant is deterministic and metadata-backed, so the prototype remains runnable without an API key.

## Docker quick start
Requirements: Docker Desktop with the Linux engine running.

```bash
git clone https://github.com/Swastika-311/movegov-prototype.git
cd movegov-prototype
docker compose up --build
```

Then open:
- UI: http://localhost:8501
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

No `.env` file is required for the default deterministic assistant. If you later add an LLM provider, set `LLM_PROVIDER`, `LLM_API_KEY`, and `LLM_MODEL` in a local `.env` file; `.env` is ignored by Git.

To run in the background:

```bash
docker compose up --build -d
```

To view logs:

```bash
docker compose logs -f
```

To stop the stack:

```bash
docker compose down
```

To stop and remove the PostgreSQL data volume as well (destructive):

```bash
docker compose down -v
```

## Local development
Use Python 3.11+, install `requirements.txt`, set `DATABASE_URL` to PostgreSQL (or use the SQLite fallback for tests), then run:
- `uvicorn app.api.main:app --reload`
- `streamlit run frontend/streamlit_app.py`

## Testing

```bash
pytest -q
```

## Government-source policy
The structured service records were seeded only with official-source references. Where an exact current requirement could vary by state, RTO, workflow or portal configuration, the product deliberately avoids asserting an exact fact and tells the user to verify it.

## Safety / limitations
MoveGov does not submit applications, access government databases, modify government records, determine legal eligibility, or represent any government department. The tracker is local prototype state only.

> MoveGov is a prototype coordination and navigation layer. It does not directly modify government records or represent official government systems.
