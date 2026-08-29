import os
from .retriever import retrieve

def answer(query, user_context, recommendations, applications):
    ids=[r['service_id'] for r in recommendations]
    docs=retrieve(query,ids or None)
    if not docs:
        return {'answer':'Information could not be verified from the available official sources.','sources':[]}
    q=query.lower()
    if 'first' in q or 'start' in q:
        high=[r for r in recommendations if r['priority']=='High']
        text='Start with the high-priority actions shown in your journey, especially those that are directly applicable to your profile. LifeNav does not submit applications for you.'
    elif 'document' in q:
        text='For the relevant services, use the documents listed in each service card. Where an exact document list is state- or workflow-specific, LifeNav marks it for verification rather than guessing.'
    else:
        d=docs[0]; text=f"{d['service_name']}: {d['why_relevant']} {d['process']}"
    return {'answer':text,'sources':[{'name':d['department'],'url':d['source_url'],'service_id':d['service_id']} for d in docs]}