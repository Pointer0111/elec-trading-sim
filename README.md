# Electricity Market Simulation Platform

This is an interactive teaching platform for electricity market trading simulation, built with Streamlit. It supports login, teacher/student roles, scenario parameter setting, student bidding, and real-time market visualization.

## Features
- Login system (teacher/student)
- Teacher: create classroom sessions, set scenario parameters, view results
- Student: join session, submit bids, view market results
- Scenario 1 implemented: Single-price Clearing Market (more scenarios can be added)
- Real-time supply curve, MCP, and profit visualization

## Quick Start

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Run the platform
```
streamlit run main.py
```

### 3. Login Accounts
- Teacher:  
  Username: `teacher1`  
  Password: `teachpass`  
  Role: `teacher`
- Student:  
  Username: `student1`  
  Password: `studpass1`  
  Role: `student`
  
  Username: `student2`  
  Password: `studpass2`  
  Role: `student`

## Adding More Scenarios
- Add a new file in `scenes/` (e.g., `scene2.py`) and register it in `scenes/__init__.py`.

## Notes
- All data is stored in memory for demo purposes. For production, replace with a persistent database.
- The UI is in English for international users. 