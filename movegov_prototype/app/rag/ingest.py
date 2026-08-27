"""Lightweight ingestion hook. The prototype keeps official-source metadata in data/services.json.
A production version can chunk downloaded official documents into a vector index here."""
def ingest():
    return {'status':'ready','mode':'metadata-backed retrieval'}
