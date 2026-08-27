# Architecture

The prototype is intentionally monolithic. Streamlit is presentation only. FastAPI owns API contracts and orchestration. Recommendation logic is deterministic and cannot be overridden by the assistant. Government service knowledge is structured in JSON and seeded into PostgreSQL. Dependencies are explicit relationships. The assistant retrieves service records first and returns source URLs with procedural answers.
