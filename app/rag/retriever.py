import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def retrieve(query:str,service_ids=None,top_k=3):
    data=json.loads((ROOT/'data/services.json').read_text())
    terms=set(query.lower().split())
    scored=[]
    for d in data:
        if service_ids and d['service_id'] not in service_ids: continue
        text=' '.join([d['service_name'],d['description'],d['why_relevant'],d['process']]).lower()
        score=sum(1 for t in terms if len(t)>2 and t in text)
        if score: scored.append((score,d))
    scored.sort(key=lambda x:x[0],reverse=True)
    return [d for _,d in scored[:top_k]]
