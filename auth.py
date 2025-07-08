import streamlit as st
import hashlib

# Simple in-memory user store for demo; replace with DB in production
def get_user_db():
    # username: (password_hash, role)
    return {
        'teacher1': (hashlib.sha256('teachpass'.encode()).hexdigest(), 'teacher'),
        'student1': (hashlib.sha256('studpass1'.encode()).hexdigest(), 'student'),
        'student2': (hashlib.sha256('studpass2'.encode()).hexdigest(), 'student'),
    }

def login():
    st.title("Login to Electricity Market Simulation Platform")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["teacher", "student"])
    if st.button("Login"):
        user_db = get_user_db()
        if username in user_db:
            pw_hash, user_role = user_db[username]
            if hashlib.sha256(password.encode()).hexdigest() == pw_hash and role == user_role:
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['username'] = username
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password or role.")
        else:
            st.error("User not found.")

def get_user_role():
    return st.session_state.get('role', None)

def logout():
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['session_code'] = None 