from app.rag.service import answer

def ask(query,user_context,recommendations,applications):
    # Deterministic retrieval-first assistant. An external LLM can be added behind this interface.
    return answer(query,user_context,recommendations,applications)
