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

### 3. Login
- **Teacher:**  
  Username: `teacher1`  
  Password: `teachpass`  
  Only one teacher account is supported.
- **Student:**  
  No registration or password required.  
  Simply enter your name and click 'Enter as Student' to join the platform.

## Adding More Scenarios
- Add a new file in `