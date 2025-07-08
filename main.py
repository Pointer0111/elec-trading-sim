import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd
import re

# ------------------ 数据文件和工具 ------------------
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def ensure_json_file(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump(default, f)
    return path

SCENARIOS_FILE = ensure_json_file('scenarios.json', [])
PARTICIPANTS_FILE = ensure_json_file('participants.json', {})
BIDS_FILE = ensure_json_file('bids.json', {})
USERS_FILE = ensure_json_file('users.json', {})

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# ------------------ 数据文件和工具 ------------------

# 初始化默认用户
DEFAULT_USERS = {
    'teacher1': {'password': 'teachpass', 'role': 'teacher', 'full_name': 'Teacher One'},
    'student1': {'password': 'studpass1', 'role': 'student', 'full_name': 'Student One'},
    'student2': {'password': 'studpass2', 'role': 'student', 'full_name': 'Student Two'}
}
def ensure_default_users():
    users = load_json(USERS_FILE)
    if not users:
        save_json(USERS_FILE, DEFAULT_USERS)
ensure_default_users()

# ------------------ 用户管理 ------------------
def register_user(username, password, role):
    users = load_json(USERS_FILE)
    if username in users:
        return False, "Username already exists."
    users[username] = {
        'password': password,
        'role': role,
        'full_name': username
    }
    save_json(USERS_FILE, users)
    return True, "Registration successful."

def verify_user(username, password):
    users = load_json(USERS_FILE)
    if username in users and users[username]['password'] == password:
        return True, users[username]['role']
    return False, None

# ------------------ 页面函数 ------------------
def login_page():
    st.title("Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            ok, role = verify_user(username, password)
            if ok:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['role'] = role
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with tab2:
        reg_user = st.text_input("Username", key="reg_user")
        reg_pw = st.text_input("Password", type="password", key="reg_pw")
        reg_pw2 = st.text_input("Confirm Password", type="password", key="reg_pw2")
        reg_role = st.selectbox("Role", ["student", "teacher"], key="reg_role")
        if st.button("Register"):
            if not reg_user or not reg_pw or not reg_pw2:
                st.error("Please fill all fields.")
            elif reg_pw != reg_pw2:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(reg_user, reg_pw, reg_role)
                if ok:
                    st.success(msg)
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = reg_user
                    st.session_state['role'] = reg_role
                    st.rerun()
                else:
                    st.error(msg)

def get_market_types():
    types = ["Single-price Clearing Market", "Pay-as-Bid", "Transmission Constraints", "CMSC", "Locational Pricing", "Fixed Costs", "Cost Recovery Guarantees", "Multi-Interval Optimization", "Planning Risk", "Day-Ahead Market + Two-Settlement"]
    return types

def scenarios_list_page():
    st.title("Experiment Scenarios")
    scenarios = load_json(SCENARIOS_FILE)
    if st.button("Refresh"):
        st.rerun()
    if st.session_state['role'] == 'teacher':
        with st.expander("Create New Scenario"):
            name = st.text_input("Scenario Name")
            desc = st.text_area("Description")
            demand = st.number_input("Demand (MW)", min_value=1, value=5, step=1, format="%d")
            market_types = get_market_types()
            market_type = st.selectbox("Market Type", market_types)
            if st.button("Create Scenario"):
                if not name.strip():
                    st.error("Scenario Name is required!")
                else:
                    scenarios.append({
                        'id': int(datetime.now().timestamp()),
                        'name': name,
                        'description': desc,
                        'demand': demand,
                        'status': 'active',
                        'participants': 0,
                        'created_at': datetime.now().strftime('%Y-%m-%d'),
                        'market_type': market_type,
                        'is_open': True
                    })
                    save_json(SCENARIOS_FILE, scenarios)
                    st.success("Scenario created!")
                    st.rerun()
    if not scenarios:
        st.info("No scenarios available.")
    else:
        cols = st.columns(2)
        for idx, scenario in enumerate(scenarios):
            with cols[idx % 2]:
                st.markdown(f"### {scenario['name']}")
                st.caption(scenario['description'])
                st.write(f"**Demand:** {scenario['demand']} MW")
                st.write(f"**Type:** {scenario.get('market_type', 'N/A')}")
                st.write(f"**Status:** :{'green' if scenario['status']=='active' else 'gray'}[{scenario['status'].capitalize()}]")
                st.write(f"**Participants:** {scenario.get('participants', 0)}")
                st.write(f"**Created:** {scenario['created_at']}")
                # 自定义按钮样式
                st.markdown('''
                <style>
                .custom-btn-row {display: flex; gap: 0.5em; margin-bottom: 1em;}
                .custom-btn {
                    flex: 1;
                    height: 2.5em;
                    border-radius: 8px;
                    border: 1.5px solid #d3d3d3;
                    background: #fff;
                    color: #333;
                    font-weight: 600;
                    font-size: 1em;
                    cursor: pointer;
                    transition: background 0.2s, color 0.2s, border 0.2s;
                }
                .custom-btn:hover { background: #f8f8f8; border-color: #aaa; }
                .custom-btn-danger { color: #fff; background: #e74c3c; border-color: #e74c3c; }
                .custom-btn-danger:hover { background: #c0392b; border-color: #c0392b; }
                .custom-btn-primary { color: #e74c3c; border-color: #e74c3c; }
                .custom-btn-primary:hover { background: #fdecea; }
                </style>
                ''', unsafe_allow_html=True)
                # 按钮逻辑
                btn_key = f"btn_{scenario['id']}"
                if 'btn_action' not in st.session_state:
                    st.session_state['btn_action'] = None
                st.markdown(f'''
                <div class="custom-btn-row">
                    <form action="" method="post">
                        <button class="custom-btn custom-btn-primary" name="action" value="join_{scenario['id']}" type="submit">Join Scenario</button>
                    </form>
                    <form action="" method="post">
                        <button class="custom-btn" name="action" value="view_{scenario['id']}" type="submit">View Details</button>
                    </form>
                    {f'''<form action="" method="post"><button class="custom-btn custom-btn-danger" name="action" value="delete_{scenario['id']}" type="submit">Delete</button></form>''' if st.session_state['role']=='teacher' else ''}
                </div>
                ''', unsafe_allow_html=True)
                # 处理按钮点击
                import streamlit as st2
                import sys
                if st.session_state.get('action', None):
                    action = st.session_state['action']
                    if action == f'join_{scenario["id"]}':
                        st.session_state['page'] = 'bidding'
                        st.session_state['selected_scenario'] = scenario['id']
                        join_scenario(scenario['id'])
                        st.session_state['action'] = None
                        st.experimental_rerun()
                    elif action == f'view_{scenario["id"]}':
                        st.session_state['page'] = 'detail'
                        st.session_state['selected_scenario'] = scenario['id']
                        st.session_state['action'] = None
                        st.experimental_rerun()
                    elif action == f'delete_{scenario["id"]}' and st.session_state['role']=='teacher':
                        scenarios = [s for s in scenarios if s['id'] != scenario['id']]
                        save_json(SCENARIOS_FILE, scenarios)
                        st.success("Scenario deleted!")
                        st.session_state['action'] = None
                        st.experimental_rerun()
                # 捕获表单提交
                import streamlit.web.server.websocket_headers as ws
                if ws._get_websocket_headers().get('content-type', '').startswith('application/x-www-form-urlencoded'):
                    import urllib.parse
                    import os
                    if 'CONTENT_LENGTH' in os.environ:
                        length = int(os.environ['CONTENT_LENGTH'])
                        post_data = sys.stdin.read(length)
                        post = urllib.parse.parse_qs(post_data)
                        if 'action' in post:
                            st.session_state['action'] = post['action'][0]

def scenario_detail_page():
    sid = st.session_state.get('selected_scenario')
    scenarios = load_json(SCENARIOS_FILE)
    scenario = next((s for s in scenarios if s['id'] == sid), None)
    participants = load_json(PARTICIPANTS_FILE).get(str(sid), [])
    bids = load_json(BIDS_FILE).get(str(sid), [])
    is_participant = st.session_state['username'] in [p['username'] for p in participants]
    if st.button("← Back"):
        set_page('scenarios')
    if not scenario:
        st.warning("No scenario selected or data not loaded.")
        return
    st.header("Scenario Details")
    st.subheader(scenario['name'])
    st.caption(scenario.get('description', 'No description provided'))
    st.write(f"**Demand:** {scenario['demand']} MW")
    st.write(f"**Status:** :{'green' if scenario['status']=='active' else 'gray'}[{scenario['status'].capitalize()}]")
    st.write(f"**Market Type:** {scenario.get('market_type', 'N/A')}")
    st.write(f"**Created:** {scenario['created_at']}")
    st.write(f"**Participants:** {len(participants)}")
    st.write(f"**Experiment Type:** {'Open' if scenario.get('is_open') else 'Class Limited'}")
    if scenario['status'] == 'active' and not is_participant:
        if st.button("Join Scenario"):
            join_scenario(sid)
    if scenario['status'] == 'active' and is_participant:
        if st.button("Submit Bids"):
            set_page('bidding')
    if scenario['status'] == 'completed':
        st.button("View Results")
    st.markdown("#### Participants")
    if participants:
        st.dataframe(pd.DataFrame(participants))
    else:
        st.info("No participants yet.")
    st.markdown("#### Bids Summary")
    if bids:
        st.write(f"**Total Bids:** {len(bids)}")
        st.write(f"**Average Price:** ${pd.DataFrame(bids)['price'].mean():.2f}")
    else:
        st.info("No bids yet.")
    st.markdown("#### Recent Bids")
    if bids:
        for bid in bids[:5]:
            st.write(f"{bid['username']} - ${bid['price']} | {bid['quantity']} MW ({bid['bid_type']})")
    else:
        st.info("No bids yet.")

def bidding_page():
    sid = st.session_state.get('selected_scenario')
    scenarios = load_json(SCENARIOS_FILE)
    scenario = next((s for s in scenarios if s['id'] == sid), None)
    my_bids = [b for b in load_json(BIDS_FILE).get(str(sid), []) if b['username'] == st.session_state['username']]
    if st.button("← Back"):
        set_page('scenarios')
    if not scenario:
        st.warning("Please select a scenario.")
        return
    st.header(f"Bidding for: {scenario['name']}")
    st.caption(scenario['description'])
    with st.form("bid_form"):
        price = st.number_input("Bid Price ($/MWh)", min_value=0, value=0, step=1, format="%d")
        quantity = st.number_input(
            "Bid Quantity (MW)",
            min_value=0,
            max_value=int(scenario['demand']),
            value=0,
            step=1,
            format="%d"
        )
        bid_type = st.selectbox("Bid Type", ["supply", "demand"])
        submitted = st.form_submit_button("Submit Bid")
        if submitted:
            bids = load_json(BIDS_FILE)
            bids.setdefault(str(sid), []).append({
                'username': st.session_state['username'],
                'price': price,
                'quantity': quantity,
                'bid_type': bid_type,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
            save_json(BIDS_FILE, bids)
            st.success(f"Bid submitted: ${price}/MWh, {quantity} MW, {bid_type}")
            st.rerun()
    st.markdown("#### Scenario Details")
    st.write(f"**Demand:** {scenario['demand']} MW")
    st.write(f"**Status:** {scenario['status']}")
    st.write(f"**Participants:** {scenario.get('participants', 0)}")
    st.write(f"**Created:** {scenario['created_at']}")
    st.markdown("#### My Previous Bids")
    if my_bids:
        for bid in my_bids:
            st.write(f"${bid['price']}/MWh - {bid['quantity']} MW ({bid['bid_type']})")
    else:
        st.info("No previous bids.")

# ------------------ 页面切换与主入口 ------------------
def set_page(page):
    st.session_state['page'] = page
    if page == 'scenarios':
        st.session_state['selected_scenario'] = None
    st.rerun()

def join_scenario(sid):
    participants = load_json(PARTICIPANTS_FILE)
    user = st.session_state['username']
    users = load_json(USERS_FILE)
    if user not in [p['username'] for p in participants.get(str(sid), [])]:
        participants.setdefault(str(sid), []).append({
            'username': user,
            'full_name': users[user]['full_name'],
            'role': users[user]['role'],
            'join_time': datetime.now().strftime('%Y-%m-%d')
        })
        save_json(PARTICIPANTS_FILE, participants)
    # 更新场景参与人数
    scenarios = load_json(SCENARIOS_FILE)
    for s in scenarios:
        if s['id'] == sid:
            s['participants'] = len(participants[str(sid)])
    save_json(SCENARIOS_FILE, scenarios)

# ------------------ 主入口 ------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'scenarios'
if 'selected_scenario' not in st.session_state:
    st.session_state['selected_scenario'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'role' not in st.session_state:
    st.session_state['role'] = ''

if not st.session_state['logged_in']:
    login_page()
    st.stop()

st.sidebar.title("Electricity Market Platform")
st.sidebar.write(f"User: {st.session_state['username']} ({st.session_state['role']})")
if st.sidebar.button("Logout"):
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['role'] = ''
    st.session_state['page'] = 'scenarios'
    st.session_state['selected_scenario'] = None
    st.rerun()

if st.session_state['page'] == 'scenarios':
    scenarios_list_page()
elif st.session_state['page'] == 'detail':
    scenario_detail_page()
elif st.session_state['page'] == 'bidding':
    bidding_page() 