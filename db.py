import streamlit as st
import random
import string

# In-memory DB for demo; replace with persistent DB in production
if 'sessions' not in st.session_state:
    st.session_state['sessions'] = {}
if 'user_sessions' not in st.session_state:
    st.session_state['user_sessions'] = {}

def create_session(scene_id, params):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    st.session_state['sessions'][code] = {
        'scene_id': scene_id,
        'params': params,
        'bids': {},  # username: {'MC':..., 'price':..., 'bid_submitted':...}
    }
    return code

def get_all_sessions():
    return [{'code': k, 'scene_id': v['scene_id']} for k, v in st.session_state['sessions'].items()]

def join_session(session_code, username):
    sessions = st.session_state['sessions']
    if session_code in sessions:
        # Assign MC for demo (random, in real use from teacher param)
        if username not in sessions[session_code]['bids']:
            mc = random.randint(20, 80)
            sessions[session_code]['bids'][username] = {'MC': mc, 'bid_submitted': False}
            st.session_state['user_sessions'][username] = session_code
            return sessions[session_code]['bids'][username]
        else:
            return None  # already joined
    return None

def get_session_params(session_code):
    return st.session_state['sessions'][session_code]['params'] | {'scene_id': st.session_state['sessions'][session_code]['scene_id']}

def get_bids(session_code):
    return [dict(username=k, **v) for k, v in st.session_state['sessions'][session_code]['bids'].items()]

def submit_bid(session_code, username, price):
    bids = st.session_state['sessions'][session_code]['bids']
    if username in bids:
        bids[username]['price'] = price
        bids[username]['bid_submitted'] = True

def get_user_info(session_code, username):
    return st.session_state['sessions'][session_code]['bids'].get(username, {}) 