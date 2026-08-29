import os
import requests
import streamlit as st
from datetime import date

API = os.getenv('API_BASE_URL', 'http://localhost:8000')
st.set_page_config(page_title='LifeNav', page_icon='🧭', layout='wide')
st.markdown('''<style>
.block-container{max-width:1200px;padding-top:2rem}.hero{padding:2.5rem;border-radius:20px;background:linear-gradient(135deg,#eaf3ff,#f7fbff);border:1px solid #cbdcf0}.hero h1,.hero h3,.hero p{color:#111827!important}.hero h1{font-size:3.2rem;margin-bottom:.5rem}.hero h3{font-size:1.5rem}.hero p{font-size:1.05rem}.card{padding:1.2rem;border:1px solid #d8dee8;border-radius:14px;margin:.7rem 0;background:#fff;color:#111827;box-shadow:0 2px 8px rgba(15,23,42,.05)}.card h3,.card p{color:#111827!important}.badge{display:inline-block;padding:.2rem .6rem;border-radius:999px;background:#e7eefc;color:#1e3a8a;font-size:.8rem}.muted{color:#475569!important}.stTextInput input,.stTextArea textarea,.stDateInput input{color:#111827!important;background:#fff!important;-webkit-text-fill-color:#111827!important}.stTextInput label,.stTextArea label,.stDateInput label,.stSelectbox label,.stCheckbox label,.stRadio label{color:#111827!important}.stSelectbox div[data-baseweb="select"]>div{color:#111827!important;background:#fff!important}.stSelectbox div[data-baseweb="select"] span{color:#111827!important}.stCheckbox label p,.stRadio label p{color:#111827!important}.stButton>button{font-weight:600}.dashboard-title{color:#111827!important}.dashboard-subtitle{color:#475569!important}</style>''', unsafe_allow_html=True)

def api(method, path, **kwargs):
    r = requests.request(method, API + path, timeout=10, **kwargs)
    r.raise_for_status()
    return r.json()

def ensure_user():
    if 'user_id' in st.session_state: return
    try:
        st.session_state.user_id = api('POST', '/users', json={'name':'Demo Citizen','current_city':'Prayagraj','destination_city':'Lucknow','state':'Uttar Pradesh','move_date':str(date.today()),'move_type':'Permanent','reason':'Employment','vehicle':True,'voter':True,'benefits':True,'student':False,'property':False})['id']
    except requests.RequestException as exc:
        st.error(f'Could not start the LifeNav journey: {exc}'); st.stop()

def go(page):
    st.session_state.page=page; st.rerun()

def build_plan(user_id):
    recs=api('POST','/recommendations',params={'user_id':user_id}); st.session_state.recommendations=recs; return recs

ensure_user()
pages=['Home','Relocation setup','Personal context','Dashboard','Journey tracker','Ask LifeNav']
if 'page' not in st.session_state: st.session_state.page='Home'
st.sidebar.title('LifeNav'); st.sidebar.caption('Your life-event government navigator')
selected_page=st.sidebar.radio('Journey',pages,index=pages.index(st.session_state.page))
if selected_page != st.session_state.page: st.session_state.page=selected_page; st.rerun()
page=st.session_state.page

if page=='Home':
    st.markdown('<div class="hero"><h1>LifeNav</h1><h3>Government services, organized around your life event.</h3><p>Navigate a move with one personalized checklist, official sources, dependencies and a prototype progress tracker.</p></div>',unsafe_allow_html=True)
    st.write('')
    if st.button('Start Relocation Journey',type='primary'): go('Relocation setup')
    st.info('Demo mode: all citizen/application data is synthetic. LifeNav is not a government website and does not submit applications or modify government records.')

elif page=='Relocation setup':
    u=api('GET',f"/users/{st.session_state.user_id}"); st.header('Relocation setup')
    with st.form('reloc'):
        c1,c2=st.columns(2); cur=c1.text_input('Current city',u['current_city']); dest=c2.text_input('Destination city',u['destination_city'])
        d=st.date_input('Move date',date.fromisoformat(u['move_date']) if u.get('move_date') else date.today()); typ=st.selectbox('Move type',['Permanent','Temporary'],index=0 if u['move_type']=='Permanent' else 1); reason=st.text_input('Reason',u['reason'])
        if st.form_submit_button('Save and continue',type='primary'):
            if not cur.strip() or not dest.strip() or not reason.strip(): st.error('Please complete current city, destination city and reason.')
            else:
                api('PATCH',f"/relocation/{st.session_state.user_id}",json={'current_city':cur.strip(),'destination_city':dest.strip(),'state':u['state'],'move_date':str(d),'move_type':typ,'reason':reason.strip()}); go('Personal context')

elif page=='Personal context':
    u=api('GET',f"/users/{st.session_state.user_id}"); p=u['profile']; st.header('Personal context')
    vehicle=st.checkbox('Do you own a vehicle?',p['vehicle']); voter=st.checkbox('Are you registered as a voter?',p['voter']); benefits=st.checkbox('Do you receive government benefits?',p['benefits']); student=st.checkbox('Are you a student?',p['student']); prop=st.checkbox('Do you need to review other address-linked records?',p['property'])
    if st.button('Build my plan',type='primary'):
        try:
            api('POST',f"/users/{st.session_state.user_id}/profile",json={'vehicle':vehicle,'voter':voter,'benefits':benefits,'student':student,'property':prop}); build_plan(st.session_state.user_id); go('Dashboard')
        except requests.RequestException as exc: st.error(f'Could not build your personalized plan: {exc}')

elif page=='Dashboard':
    try:
        u=api('GET',f"/users/{st.session_state.user_id}"); recs=api('GET',f"/recommendations/{u['id']}")
        if not recs: recs=build_plan(u['id'])
        apps=api('GET',f"/applications/{u['id']}")
    except requests.RequestException as exc: st.error(f'Could not load your personalized dashboard: {exc}'); st.stop()
    st.markdown('<h1 class="dashboard-title">Your personalized LifeNav dashboard</h1>',unsafe_allow_html=True)
    st.markdown(f'<p class="dashboard-subtitle">{u["current_city"]} → {u["destination_city"]} · {u["move_type"]} · {u["reason"]}</p>',unsafe_allow_html=True)
    completed=sum(a['status']=='Completed' for a in apps); st.progress(completed/max(len(recs),1),text=f'{completed}/{len(recs)} tracked actions completed')
    if recs: st.success(f'Your plan is ready — {len(recs)} government-service actions match your move and profile.')
    else: st.warning('No personalized actions matched the current profile. Return to Personal context and review your answers.')
    for r in recs:
        a=next((x for x in apps if x['service_id']==r['service_id']),None); status=a['status'] if a else 'Not Started'
        st.markdown(f"<div class='card'><h3>{r['service_name']} <span class='badge'>{r['priority']}</span></h3><p>{r['reason']}</p><p class='muted'>{r['applicability']} · Status: {status}</p><a href='{r['source']['url']}' target='_blank'>Official source ↗</a></div>",unsafe_allow_html=True)
        if st.button(f"View details · {r['service_id']}",key=r['service_id']): st.session_state.detail=r['service_id']; st.rerun()
    if 'detail' in st.session_state:
        s=api('GET',f"/services/{st.session_state.detail}"); st.divider(); st.subheader(s['service_name']); st.write(s['description']); st.write('**Why relevant:**',s['why_relevant']); st.write('**Process:**',s['process']); st.write('**Documents / requirements**')
        for x in s['requirements']: st.write('•',x['requirement'],':',x['description'])
        st.write('**Dependencies**')
        for x in (s['dependencies'] or []): st.write('•',x['service_id'],':',x['description'])
        st.markdown(f"[Official service]({s['official_url']}) · [Source]({s['source_url']})")
        a=next((x for x in apps if x['service_id']==s['service_id']),None)
        if not a and st.button('Start',key='start_'+s['service_id']): api('POST','/applications',json={'user_id':u['id'],'service_id':s['service_id']}); st.rerun()
        if a:
            statuses=['Not Started','Preparing','Submitted','Under Processing','Action Required','Completed']; ns=st.selectbox('Update status',statuses,index=statuses.index(a['status']),key='status_'+s['service_id'])
            if st.button('Save status',key='save_'+s['service_id']): api('PATCH',f"/applications/{a['id']}",json={'status':ns}); st.rerun()

elif page=='Journey tracker':
    u=api('GET',f"/users/{st.session_state.user_id}"); recs=api('GET',f"/recommendations/{u['id']}"); apps=api('GET',f"/applications/{u['id']}"); st.header('Journey tracker'); st.info('LifeNav prototype tracker — not connected to government application status APIs.')
    for i,r in enumerate(recs,1):
        a=next((x for x in apps if x['service_id']==r['service_id']),None); status=a['status'] if a else 'Not Started'; st.write(f"**{i}. {r['service_name']}** — {status}")
    st.subheader('Shared dependency'); st.write('One document may support multiple services. Address proof is shown as a shared dependency where the official workflow indicates it may be relevant.')

elif page=='Ask LifeNav':
    st.header('Ask LifeNav'); st.caption('Official-source retrieval first. LifeNav does not determine government eligibility independently.')
    q=st.chat_input('Ask a relocation question…')
    if q:
        try:
            out=api('POST','/chat',json={'user_id':st.session_state.user_id,'message':q}); st.chat_message('user').write(q); st.chat_message('assistant').write(out['answer'])
            for s in out.get('sources',[]): st.caption(f"Source: {s['name']} — {s['url']}")
        except requests.RequestException as exc: st.error(f'Unable to reach LifeNav right now: {exc}')
