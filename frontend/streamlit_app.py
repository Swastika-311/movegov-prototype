import os
import requests
import streamlit as st
from datetime import date

API = os.getenv('API_BASE_URL', 'http://localhost:8000')
st.set_page_config(page_title='LifeNav', page_icon='🧭', layout='wide')

st.markdown('''<style>
.block-container{max-width:1200px;padding-top:2rem}
.hero{padding:2.5rem;border-radius:20px;background:#151a23;border:1px solid #303846;box-shadow:0 8px 30px rgba(0,0,0,.18)}
.hero h1,.hero h3,.hero p{color:#f8fafc!important}.hero h1{font-size:3.2rem;margin-bottom:.5rem}.hero h3{font-size:1.5rem}.hero p{font-size:1.05rem;color:#d7dee8!important}
.card{padding:1.2rem;border:1px solid #303846;border-radius:14px;margin:.7rem 0;background:#151a23;color:#f1f5f9;box-shadow:0 4px 14px rgba(0,0,0,.18)}
.card h3,.card p{color:#f1f5f9!important}.card a{color:#93c5fd!important}.badge{display:inline-block;padding:.2rem .6rem;border-radius:999px;background:#30394a;color:#e2e8f0;font-size:.8rem}.muted{color:#cbd5e1!important}
.stTextInput input,.stTextArea textarea,.stDateInput input{color:#f8fafc!important;background:#151a23!important;border:1px solid #475569!important;-webkit-text-fill-color:#f8fafc!important}
.stTextInput input:focus,.stTextArea textarea:focus,.stDateInput input:focus{border-color:#ff4b4b!important;box-shadow:0 0 0 1px #ff4b4b!important}
.stTextInput label,.stTextArea label,.stDateInput label,.stSelectbox label,.stCheckbox label,.stRadio label{color:#f1f5f9!important}
.stSelectbox div[data-baseweb="select"]>div{color:#f8fafc!important;background:#151a23!important;border:1px solid #475569!important}.stSelectbox div[data-baseweb="select"] span{color:#f8fafc!important}
.stCheckbox label p,.stRadio label p{color:#f1f5f9!important}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] span{color:#e5e7eb!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label p{color:#e5e7eb!important}
.stButton>button{font-weight:600}.dashboard-title{color:#f8fafc!important}.dashboard-subtitle{color:#cbd5e1!important}
.tracker-item{padding:1rem 1.2rem;margin:.6rem 0;border:1px solid #303846;border-radius:14px;background:#151a23}.tracker-done{border-color:#365c46;background:#13231a}
.tracker-item h3,.tracker-item p{color:#f8fafc!important}.tracker-item .done-label{color:#86efac!important;font-weight:700}
</style>''', unsafe_allow_html=True)


def api(method, path, **kwargs):
    r = requests.request(method, API + path, timeout=10, **kwargs)
    r.raise_for_status()
    return r.json()


def ensure_user():
    if 'user_id' in st.session_state:
        return
    try:
        st.session_state.user_id = api('POST', '/users', json={
            'name':'Demo Citizen','current_city':'Prayagraj','destination_city':'Lucknow',
            'state':'Uttar Pradesh','move_date':str(date.today()),'move_type':'Permanent',
            'reason':'Employment','vehicle':True,'voter':True,'benefits':True,
            'student':False,'property':False})['id']
    except requests.RequestException as exc:
        st.error(f'Could not start the LifeNav journey: {exc}')
        st.stop()


def go(page):
    st.session_state.page = page
    st.rerun()


def build_plan(user_id):
    recs = api('POST', '/recommendations', params={'user_id': user_id})
    st.session_state.recommendations = recs
    return recs


def set_done(user_id, service_id, done, apps):
    app = next((x for x in apps if x['service_id'] == service_id), None)
    if done:
        if app:
            api('PATCH', f"/applications/{app['id']}", json={'status':'Done'})
        else:
            api('POST', '/applications', json={'user_id':user_id,'service_id':service_id})
            new_apps = api('GET', f'/applications/{user_id}')
            created = next((x for x in new_apps if x['service_id'] == service_id), None)
            if created:
                api('PATCH', f"/applications/{created['id']}", json={'status':'Done'})
    elif app:
        api('PATCH', f"/applications/{app['id']}", json={'status':'Not Started'})


ensure_user()
pages = ['Home','Relocation setup','Personal context','Dashboard','Journey tracker','Ask LifeNav']
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
st.sidebar.title('LifeNav')
st.sidebar.caption('Your life-event government navigator')
selected_page = st.sidebar.radio('Journey', pages, index=pages.index(st.session_state.page))
if selected_page != st.session_state.page:
    st.session_state.page = selected_page
    st.rerun()
page = st.session_state.page

if page == 'Home':
    st.markdown('<div class="hero"><h1>LifeNav</h1><h3>Government services, organized around your life event.</h3><p>Navigate a move with one personalized checklist, official sources, dependencies and a prototype progress tracker.</p></div>', unsafe_allow_html=True)
    st.write('')
    if st.button('Start Relocation Journey', type='primary'):
        go('Relocation setup')
    st.info('Demo mode: all citizen/application data is synthetic. LifeNav is not a government website and does not submit applications or modify government records.')

elif page == 'Relocation setup':
    u = api('GET', f"/users/{st.session_state.user_id}")
    st.header('Relocation setup')
    with st.form('reloc'):
        c1, c2 = st.columns(2)
        cur = c1.text_input('Current city', u['current_city'])
        dest = c2.text_input('Destination city', u['destination_city'])
        d = st.date_input('Move date', date.fromisoformat(u['move_date']) if u.get('move_date') else date.today())
        typ = st.selectbox('Move type', ['Permanent','Temporary'], index=0 if u['move_type'] == 'Permanent' else 1)
        reason = st.text_input('Reason', u['reason'])
        if st.form_submit_button('Save and continue', type='primary'):
            if not cur.strip() or not dest.strip() or not reason.strip():
                st.error('Please complete current city, destination city and reason.')
            else:
                api('PATCH', f"/relocation/{st.session_state.user_id}", json={
                    'current_city':cur.strip(),'destination_city':dest.strip(),'state':u['state'],
                    'move_date':str(d),'move_type':typ,'reason':reason.strip()})
                go('Personal context')

elif page == 'Personal context':
    u = api('GET', f"/users/{st.session_state.user_id}")
    p = u['profile']
    st.header('Personal context')
    vehicle = st.checkbox('Do you own a vehicle?', p['vehicle'])
    voter = st.checkbox('Are you registered as a voter?', p['voter'])
    benefits = st.checkbox('Do you receive government benefits?', p['benefits'])
    student = st.checkbox('Are you a student?', p['student'])
    prop = st.checkbox('Do you need to review other address-linked records?', p['property'])
    if st.button('Build my plan', type='primary'):
        try:
            api('POST', f"/users/{st.session_state.user_id}/profile", json={
                'vehicle':vehicle,'voter':voter,'benefits':benefits,'student':student,'property':prop})
            build_plan(st.session_state.user_id)
            go('Dashboard')
        except requests.RequestException as exc:
            st.error(f'Could not build your personalized plan: {exc}')

elif page == 'Dashboard':
    try:
        u = api('GET', f"/users/{st.session_state.user_id}")
        recs = api('GET', f"/recommendations/{u['id']}")
        if not recs:
            recs = build_plan(u['id'])
        apps = api('GET', f"/applications/{u['id']}")
    except requests.RequestException as exc:
        st.error(f'Could not load your personalized dashboard: {exc}')
        st.stop()
    st.markdown('<h1 class="dashboard-title">Your personalized LifeNav dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="dashboard-subtitle">{u["current_city"]} → {u["destination_city"]} · {u["move_type"]} · {u["reason"]}</p>', unsafe_allow_html=True)
    completed = sum(a['status'] in {'Completed','Done'} for a in apps)
    st.progress(completed / max(len(recs), 1), text=f'{completed}/{len(recs)} tracked actions completed')
    if recs:
        st.success(f'Your plan is ready — {len(recs)} government-service actions match your move and profile.')
    else:
        st.warning('No personalized actions matched the current profile. Return to Personal context and review your answers.')
    for r in recs:
        a = next((x for x in apps if x['service_id'] == r['service_id']), None)
        status = a['status'] if a else 'Not Started'
        st.markdown(f"<div class='card'><h3>{r['service_name']} <span class='badge'>{r['priority']}</span></h3><p>{r['reason']}</p><p class='muted'>{r['applicability']} · Status: {status}</p><a href='{r['source']['url']}' target='_blank'>Official source ↗</a></div>", unsafe_allow_html=True)
        if st.button(f"View details · {r['service_id']}", key=r['service_id']):
            st.session_state.detail = r['service_id']
            st.rerun()
    if 'detail' in st.session_state:
        s = api('GET', f"/services/{st.session_state.detail}")
        st.divider(); st.subheader(s['service_name']); st.write(s['description'])
        st.write('**Why relevant:**', s['why_relevant']); st.write('**Process:**', s['process']); st.write('**Documents / requirements**')
        for x in s['requirements']:
            st.write('•', x['requirement'], ':', x['description'])
        st.write('**Dependencies**')
        for x in (s['dependencies'] or []):
            st.write('•', x['service_id'], ':', x['description'])
        st.markdown(f"[Official service]({s['official_url']}) · [Source]({s['source_url']})")
        a = next((x for x in apps if x['service_id'] == s['service_id']), None)
        if not a and st.button('Start', key='start_' + s['service_id']):
            api('POST', '/applications', json={'user_id':u['id'],'service_id':s['service_id']})
            st.rerun()
        if a:
            statuses = ['Not Started','Preparing','Submitted','Under Processing','Action Required','Completed','Done']
            ns = st.selectbox('Update status', statuses, index=statuses.index(a['status']) if a['status'] in statuses else 0, key='status_' + s['service_id'])
            if st.button('Save status', key='save_' + s['service_id']):
                api('PATCH', f"/applications/{a['id']}", json={'status':ns})
                st.rerun()

elif page == 'Journey tracker':
    try:
        u = api('GET', f"/users/{st.session_state.user_id}")
        recs = api('GET', f"/recommendations/{u['id']}")
        if not recs:
            recs = build_plan(u['id'])
        apps = api('GET', f"/applications/{u['id']}")
    except requests.RequestException as exc:
        st.error(f'Could not load your journey checklist: {exc}')
        st.stop()
    st.header('Journey tracker')
    st.caption('Tick an item when you finish it. The status is saved and stays synchronized with your Dashboard.')
    for i, r in enumerate(recs, 1):
        a = next((x for x in apps if x['service_id'] == r['service_id']), None)
        done = bool(a and a['status'] == 'Done')
        tracker_class = 'tracker-done' if done else ''
        done_label = '<p class="done-label">✓ Done</p>' if done else '<p class="muted">Not completed yet</p>'
        tracker_html = f"<div class='tracker-item {tracker_class}'><h3>{i}. {r['service_name']}</h3><p>{r['reason']}</p>{done_label}</div>"
        st.markdown(tracker_html, unsafe_allow_html=True)
        checked = st.checkbox('Mark as Done', value=done, key=f"journey_done_{r['service_id']}")
        if checked != done:
            try:
                set_done(u['id'], r['service_id'], checked, apps)
                st.rerun()
            except requests.RequestException as exc:
                st.error(f'Could not update {r["service_name"]}: {exc}')
    completed = 0
    for r in recs:
        app = next((x for x in apps if x['service_id'] == r['service_id']), None)
        if app and app['status'] == 'Done':
            completed += 1
    st.progress(completed / max(len(recs), 1), text=f'{completed}/{len(recs)} items marked Done')
    st.subheader('Shared dependency')
    st.write('One document may support multiple services. Address proof is shown as a shared dependency where the official workflow indicates it may be relevant.')

elif page == 'Ask LifeNav':
    st.header('Ask LifeNav')
    st.caption('Official-source retrieval first. LifeNav does not determine government eligibility independently.')
    q = st.chat_input('Ask a relocation question…')
    if q:
        try:
            out = api('POST', '/chat', json={'user_id':st.session_state.user_id,'message':q})
            st.chat_message('user').write(q)
            st.chat_message('assistant').write(out['answer'])
            for s in out.get('sources', []):
                st.caption(f"Source: {s['name']} — {s['url']}")
        except requests.RequestException as exc:
            st.error(f'Unable to reach LifeNav right now: {exc}')
