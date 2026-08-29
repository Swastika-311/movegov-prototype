import os
import requests
import streamlit as st
from datetime import date

API = os.getenv('API_BASE_URL', 'http://localhost:8000')
st.set_page_config(page_title='MoveGov', page_icon='🧭', layout='wide')
st.markdown('''<style>
.block-container{max-width:1200px;padding-top:2rem}
.hero{padding:2rem;border-radius:20px;background:linear-gradient(135deg,#eef5ff,#f8fbff);border:1px solid #dbe7f5}
.card{padding:1rem;border:1px solid #d1d5db;border-radius:14px;margin:.5rem 0;background:#ffffff}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:999px;background:#eef2ff;font-size:.8rem;color:#1e293b}
.muted{color:#475569}

/* Keep all form controls readable in both light and dark browser/Streamlit themes. */
div[data-baseweb="input"]{background-color:#ffffff !important;border:1px solid #94a3b8 !important;border-radius:8px !important}
div[data-baseweb="input"] input{color:#111827 !important;background-color:#ffffff !important;-webkit-text-fill-color:#111827 !important;caret-color:#111827 !important}
div[data-baseweb="select"] > div{background-color:#ffffff !important;color:#111827 !important;border:1px solid #94a3b8 !important}
div[data-baseweb="select"] span{color:#111827 !important}
div[data-baseweb="textarea"] textarea{color:#111827 !important;background-color:#ffffff !important;-webkit-text-fill-color:#111827 !important;caret-color:#111827 !important;border:1px solid #94a3b8 !important}
input[type="date"]{color:#111827 !important;background-color:#ffffff !important;-webkit-text-fill-color:#111827 !important}
.stTextInput label,.stDateInput label,.stSelectbox label,.stCheckbox label,.stTextArea label{color:#111827 !important;font-weight:600 !important}
.stTextInput [data-testid="InputInstructions"],.stDateInput [data-testid="InputInstructions"]{color:#475569 !important}
.stCheckbox span{color:#111827 !important}
button[kind="primary"]{font-weight:700 !important}

/* Make dashboard content readable and comfortable on narrow screens. */
@media (max-width:700px){
  .block-container{padding:1rem .75rem !important}
  .hero{padding:1.25rem !important}
  .card{padding:.85rem !important}
}
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
            'name': 'Demo Citizen', 'current_city': 'Prayagraj', 'destination_city': 'Lucknow',
            'state': 'Uttar Pradesh', 'move_date': str(date.today()), 'move_type': 'Permanent',
            'reason': 'Employment', 'vehicle': True, 'voter': True, 'benefits': True,
            'student': False, 'property': False,
        })['id']
    except requests.RequestException as exc:
        st.error(f'Could not start the demo journey: {exc}')
        st.stop()


def go(page):
    st.session_state.page = page
    st.rerun()


def build_plan(user_id):
    """Force recommendation generation before opening the dashboard."""
    recs = api('POST', '/recommendations', params={'user_id': user_id})
    st.session_state.recommendations = recs
    return recs


ensure_user()
pages = ['Home', 'Relocation setup', 'Personal context', 'Dashboard', 'Journey tracker', 'Ask MoveGov']
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

st.sidebar.title('MoveGov')
selected_page = st.sidebar.radio('Journey', pages, index=pages.index(st.session_state.page))
if selected_page != st.session_state.page:
    st.session_state.page = selected_page
    st.rerun()
page = st.session_state.page

if page == 'Home':
    st.markdown('<div class="hero"><h1>MoveGov</h1><h3>Government services, organized around your life event.</h3><p>Navigate a move with one personalized checklist, official sources, dependencies and a prototype progress tracker.</p></div>', unsafe_allow_html=True)
    if st.button('Start Relocation Journey', type='primary'):
        go('Relocation setup')
    st.info('Demo mode: all citizen/application data is synthetic. MoveGov is not a government website and does not submit applications or modify government records.')

elif page == 'Relocation setup':
    u = api('GET', f"/users/{st.session_state.user_id}")
    st.header('Relocation setup')
    with st.form('reloc'):
        c1, c2 = st.columns(2)
        cur = c1.text_input('Current city', u['current_city'])
        dest = c2.text_input('Destination city', u['destination_city'])
        d = st.date_input('Move date', date.fromisoformat(u['move_date']) if u.get('move_date') else date.today())
        typ = st.selectbox('Move type', ['Permanent', 'Temporary'], index=0 if u['move_type'] == 'Permanent' else 1)
        reason = st.text_input('Reason', u['reason'])
        if st.form_submit_button('Save and continue', type='primary'):
            if not cur.strip() or not dest.strip() or not reason.strip():
                st.error('Please complete current city, destination city and reason.')
            else:
                api('PATCH', f"/relocation/{st.session_state.user_id}", json={
                    'current_city': cur.strip(), 'destination_city': dest.strip(),
                    'state': u['state'], 'move_date': str(d), 'move_type': typ, 'reason': reason.strip(),
                })
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
                'vehicle': vehicle, 'voter': voter, 'benefits': benefits, 'student': student, 'property': prop,
            })
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

    st.header('Personalized dashboard')
    st.caption(f"{u['current_city']} → {u['destination_city']} · {u['move_type']} · {u['reason']}")
    completed = sum(a['status'] == 'Completed' for a in apps)
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
        st.divider()
        st.subheader(s['service_name'])
        st.write(s['description'])
        st.write('**Why relevant:**', s['why_relevant'])
        st.write('**Process:**', s['process'])
        st.write('**Documents / requirements**')
        for x in s['requirements']:
            st.write('•', x['requirement'], ':', x['description'])
        st.write('**Dependencies**')
        for x in (s['dependencies'] or []):
            st.write('•', x['service_id'], ':', x['description'])
        st.markdown(f"[Official service]({s['official_url']}) · [Source]({s['source_url']})")
        a = next((x for x in apps if x['service_id'] == s['service_id']), None)
        if not a and st.button('Start', key='start_' + s['service_id']):
            api('POST', '/applications', json={'user_id': u['id'], 'service_id': s['service_id']})
            st.rerun()
        if a:
            statuses = ['Not Started', 'Preparing', 'Submitted', 'Under Processing', 'Action Required', 'Completed']
            ns = st.selectbox('Update status', statuses, index=statuses.index(a['status']), key='status_' + s['service_id'])
            if st.button('Save status', key='save_' + s['service_id']):
                api('PATCH', f"/applications/{a['id']}", json={'status': ns})
                st.rerun()

elif page == 'Journey tracker':
    u = api('GET', f"/users/{st.session_state.user_id}")
    recs = api('GET', f"/recommendations/{u['id']}")
    apps = api('GET', f"/applications/{u['id']}")
    st.header('Journey tracker')
    st.info('MoveGov prototype tracker — not connected to government application status APIs.')
    for i, r in enumerate(recs, 1):
        a = next((x for x in apps if x['service_id'] == r['service_id']), None)
        status = a['status'] if a else 'Not Started'
        st.write(f"**{i}. {r['service_name']}** — {status}")
    st.subheader('Shared dependency')
    st.write('One document may support multiple services. Address proof is shown as a shared dependency where the official workflow indicates it may be relevant.')

elif page == 'Ask MoveGov':
    st.header('Ask MoveGov')
    st.caption('Official-source retrieval first. MoveGov does not determine government eligibility independently.')
    q = st.chat_input('Ask a relocation question…')
    if q:
        try:
            out = api('POST', '/chat', json={'user_id': st.session_state.user_id, 'message': q})
            st.chat_message('user').write(q)
            st.chat_message('assistant').write(out['answer'])
            for s in out.get('sources', []):
                st.caption(f"Source: {s['name']} — {s['url']}")
        except requests.RequestException as exc:
            st.error(f'Unable to reach MoveGov right now: {exc}')
