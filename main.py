import streamlit as st
import pandas as pd
try:
    from scenes import get_scene_module, SCENE_TITLES, get_default_params
    SCENES_AVAILABLE = True
except ImportError:
    SCENES_AVAILABLE = False
    SCENE_TITLES = {}
    def get_scene_module(scene_id):
        return None
    def get_default_params(scene_id):
        return {}
from auth import login, get_user_role, logout
from db import (
    create_session, join_session, get_session_params, 
    submit_bid, get_bids, get_user_info, get_all_sessions, delete_session, session_exists
)

st.set_page_config(page_title="Electricity Market Simulation", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'session_code' not in st.session_state:
    st.session_state['session_code'] = None

# Login page
if not st.session_state['logged_in']:
    login()
    st.stop()

# Top bar
st.sidebar.title("Electricity Market Simulation Platform")
st.sidebar.write(f"Logged in as: {st.session_state['username']} ({st.session_state['role']})")
if st.sidebar.button("Logout"):
    logout()
    st.rerun()

# Check if current session still exists
if st.session_state['session_code'] and not session_exists(st.session_state['session_code']):
    st.error(f"Session {st.session_state['session_code']} no longer exists. It may have been deleted or expired.")
    st.session_state['session_code'] = None
    st.rerun()

# Teacher/Admin view
if st.session_state['role'] == 'teacher':
    st.header("Classroom Session Management")
    
    # Create New Session
    st.write("## Create New Session")
    if SCENES_AVAILABLE:
        scene_id = st.selectbox("Select Scenario", list(SCENE_TITLES.keys()), format_func=lambda x: f"{x}: {SCENE_TITLES[x]}")
        params = get_default_params(scene_id)
        with st.form("session_params_form"):
            param_inputs = {}
            for k, v in params.items():
                param_inputs[k] = st.number_input(k, value=v)
            submitted = st.form_submit_button("Create Session")
            if submitted:
                session_code = create_session(scene_id, param_inputs)
                st.success(f"Session created! Session code: {session_code}")
                st.rerun()  # Refresh to show new session
    else:
        st.error("Scenes module not available")
    
    # Existing Sessions Management
    st.write("## Existing Sessions")
    all_sessions = get_all_sessions()
    if not all_sessions:
        st.info("No sessions created yet.")
    else:
        # Display sessions in a more interactive way
        for session in all_sessions:
            with st.expander(f"Session {session['code']} - Scenario {session['scene_id']}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Session Code:** {session['code']}")
                    st.write(f"**Scenario:** {SCENE_TITLES.get(session['scene_id'], f'Scenario {session['scene_id']}')}")
                    
                    # View details button
                    if st.button(f"View Details", key=f"view_{session['code']}"):
                        st.session_state['session_code'] = session['code']
                        st.rerun()
                
                with col2:
                    # Delete session button
                    if st.button(f"Delete", key=f"delete_{session['code']}"):
                        delete_session(session['code'])
                        st.success(f"Session {session['code']} deleted!")
                        st.rerun()
                
                with col3:
                    # Join session button (for testing)
                    if st.button(f"Join", key=f"join_{session['code']}"):
                        st.session_state['session_code'] = session['code']
                        st.rerun()
    
    # Show session details if selected
    if st.session_state['session_code']:
        st.write(f"### Session Details: {st.session_state['session_code']}")
        session_params = get_session_params(st.session_state['session_code'])
        if session_params is None:
            st.error("Session not found!")
            st.session_state['session_code'] = None
            st.rerun()
        
        st.write("#### Session Parameters")
        st.json(session_params)
        
        bids = get_bids(st.session_state['session_code'])
        st.write("#### Current Bids")
        if bids:
            df_bids = pd.DataFrame(bids)
            st.dataframe(df_bids)
        else:
            st.info("No bids submitted yet.")
        
        # Run scenario logic and show results
        scene_mod = get_scene_module(session_params['scene_id'])
        if scene_mod:
            scene_mod.teacher_view(session_params, bids)
        else:
            st.error("Scenario module not available")

# Student view
elif st.session_state['role'] == 'student':
    st.header("Join Classroom Session")
    if not st.session_state['session_code']:
        all_sessions = get_all_sessions()
        if not all_sessions:
            st.info("No available sessions. Please wait for the teacher to create one.")
        else:
            st.write("## Available Sessions")
            df_sessions = pd.DataFrame(all_sessions)
            selected = st.radio("Select a session to join:", df_sessions['code'].tolist(), format_func=lambda x: f"{x} (Scenario {df_sessions[df_sessions['code']==x]['scene_id'].values[0]})")
            if st.button("Join Selected Session"):
                user_info = join_session(selected, st.session_state['username'])
                if user_info is not None:
                    st.session_state['session_code'] = selected
                    st.success(f"Joined session {selected}")
                    st.rerun()
                else:
                    st.warning("You have already joined this session.")
    if st.session_state['session_code']:
        user_info = get_user_info(st.session_state['session_code'], st.session_state['username'])
        if not user_info:
            st.error("Session not found or you are not a member!")
            st.session_state['session_code'] = None
            st.rerun()
        
        st.write(f"### Your Role: {user_info}")
        # Show bid submission form
        if not user_info.get('bid_submitted', False):
            min_price = user_info['MC']
            price = st.number_input("Enter your offer price (must be >= MC)", min_value=min_price)
            if st.button("Submit Bid"):
                if submit_bid(st.session_state['session_code'], st.session_state['username'], price):
                    st.success("Bid submitted! Waiting for results...")
                    st.rerun()
                else:
                    st.error("Failed to submit bid. Session may have been deleted.")
        else:
            st.info("You have submitted your bid. Please wait for the teacher to publish results.")
        # Show current market status
        session_params = get_session_params(st.session_state['session_code'])
        if session_params is None:
            st.error("Session not found!")
            st.session_state['session_code'] = None
            st.rerun()
        
        bids = get_bids(st.session_state['session_code'])
        scene_mod = get_scene_module(session_params['scene_id'])
        if scene_mod:
            scene_mod.student_view(session_params, bids, user_info)
        else:
            st.error("Scenario module not available") 