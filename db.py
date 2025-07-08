import streamlit as st
import random
import string
import json
import os
from datetime import datetime

# File-based storage for sharing between browser sessions
DB_FILE = "sessions_db.json"

def load_db():
    """Load database from file"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'sessions': {}, 'user_sessions': {}}
    return {'sessions': {}, 'user_sessions': {}}

def save_db(data):
    """Save database to file"""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_session(scene_id, params):
    db = load_db()
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    db['sessions'][code] = {
        'scene_id': scene_id,
        'params': params,
        'bids': {},  # username: {'MC':..., 'price':..., 'bid_submitted':...}
        'created_at': datetime.now().isoformat()
    }
    save_db(db)
    return code

def get_all_sessions():
    db = load_db()
    return [{'code': k, 'scene_id': v['scene_id']} for k, v in db['sessions'].items()]

def join_session(session_code, username):
    db = load_db()
    if session_code in db['sessions']:
        # Assign MC for demo (random, in real use from teacher param)
        if username not in db['sessions'][session_code]['bids']:
            mc = random.randint(20, 80)
            db['sessions'][session_code]['bids'][username] = {'MC': mc, 'bid_submitted': False}
            db['user_sessions'][username] = session_code
            save_db(db)
            return db['sessions'][session_code]['bids'][username]
        else:
            return None  # already joined
    return None

def get_session_params(session_code):
    db = load_db()
    session_data = db['sessions'][session_code]
    return session_data['params'] | {'scene_id': session_data['scene_id']}

def get_bids(session_code):
    db = load_db()
    return [dict(username=k, **v) for k, v in db['sessions'][session_code]['bids'].items()]

def submit_bid(session_code, username, price):
    db = load_db()
    bids = db['sessions'][session_code]['bids']
    if username in bids:
        bids[username]['price'] = price
        bids[username]['bid_submitted'] = True
        save_db(db)

def get_user_info(session_code, username):
    db = load_db()
    return db['sessions'][session_code]['bids'].get(username, {})

def clear_old_sessions():
    """Clear sessions older than 24 hours"""
    db = load_db()
    current_time = datetime.now()
    to_delete = []
    for code, session in db['sessions'].items():
        created_at = datetime.fromisoformat(session['created_at'])
        if (current_time - created_at).total_seconds() > 86400:  # 24 hours
            to_delete.append(code)
    
    for code in to_delete:
        del db['sessions'][code]
    
    if to_delete:
        save_db(db)

# Clean old sessions on startup
clear_old_sessions() 