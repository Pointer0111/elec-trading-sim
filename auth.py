import streamlit as st
import hashlib
import json
import os

# File-based user database
USER_DB_FILE = "users_db.json"

def load_users():
    """Load users from file"""
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to file"""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, role):
    """Register a new user"""
    users = load_users()
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        'password_hash': hash_password(password),
        'role': role
    }
    save_users(users)
    return True, "Registration successful"

def verify_user(username, password):
    """Verify user credentials and return role"""
    users = load_users()
    if username in users:
        user_data = users[username]
        if user_data['password_hash'] == hash_password(password):
            return True, user_data['role']
    return False, None

def login():
    st.title("Electricity Market Simulation Platform")
    
    # Create tabs for login and register
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if username and password:
                success, role = verify_user(username, password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = role
                    st.session_state['username'] = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Please enter both username and password.")
    
    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        reg_role = st.selectbox("Role", ["student", "teacher"], key="reg_role")
        
        if st.button("Register"):
            if reg_username and reg_password and reg_password_confirm:
                if reg_password != reg_password_confirm:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    success, message = register_user(reg_username, reg_password, reg_role)
                    if success:
                        st.success(message)
                        # Auto-login after registration
                        st.session_state['logged_in'] = True
                        st.session_state['role'] = reg_role
                        st.session_state['username'] = reg_username
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.error("Please fill in all fields.")

def get_user_role():
    return st.session_state.get('role', None)

def logout():
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['session_code'] = None

# Initialize with default users if no users exist
def init_default_users():
    users = load_users()
    if not users:
        # Create default teacher and student accounts
        default_users = {
            'teacher': {
                'password_hash': hash_password('teachpass'),
                'role': 'teacher'
            },
            'student': {
                'password_hash': hash_password('studpass1'),
                'role': 'student'
            },
        }
        save_users(default_users)

# Initialize default users on startup
init_default_users() 