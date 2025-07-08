import streamlit as st
import pandas as pd
import plotly.graph_objs as go

default_params = {
    'demand': 5,  # MW
}

def teacher_view(params, bids):
    st.subheader("Single-price Clearing Market Result")
    if not bids:
        st.info("Waiting for students to submit bids...")
        return
    df = pd.DataFrame(bids)
    df = df.sort_values(by='price')
    df['cum_supply'] = range(1, len(df)+1)
    mcp_row = df[df['cum_supply'] >= params['demand']].head(1)
    if mcp_row.empty:
        st.warning("Not enough supply to meet demand!")
        return
    mcp = mcp_row['price'].values[0]
    df['dispatched'] = df['cum_supply'] <= params['demand']
    df['profit'] = (mcp - df['MC']).where(df['dispatched'], 0)
    st.write(f"**Market Clearing Price (MCP): ${mcp}**")
    st.dataframe(df[['username','MC','price','dispatched','profit']])
    # Supply curve plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['cum_supply'], y=df['price'], mode='lines+markers', name='Supply Curve'))
    fig.add_trace(go.Scatter(x=[params['demand']], y=[mcp], mode='markers', marker=dict(color='red', size=12), name='MCP'))
    fig.update_layout(xaxis_title='Cumulative Supply (MW)', yaxis_title='Price ($)', title='Supply Curve and MCP')
    st.plotly_chart(fig, use_container_width=True)
    # Profit bar chart
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df['username'], y=df['profit'], name='Profit'))
    fig2.add_trace(go.Bar(x=df['username'], y=df['MC'], name='MC'))
    fig2.update_layout(barmode='group', xaxis_title='Seller', yaxis_title='Amount ($)', title='Seller Profit and MC')
    st.plotly_chart(fig2, use_container_width=True)

def student_view(params, bids, user_info):
    st.subheader("Market Status")
    if not bids:
        st.info("Waiting for all students to submit bids...")
        return
    df = pd.DataFrame(bids)
    df = df.sort_values(by='price')
    df['cum_supply'] = range(1, len(df)+1)
    mcp_row = df[df['cum_supply'] >= params['demand']].head(1)
    if mcp_row.empty:
        st.warning("Not enough supply to meet demand!")
        return
    mcp = mcp_row['price'].values[0]
    st.write(f"**Market Clearing Price (MCP): ${mcp}**")
    dispatched = df[df['username'] == user_info['username']]['cum_supply'].values[0] <= params['demand']
    if dispatched:
        st.success(f"You are DISPATCHED! Your profit: ${mcp - user_info['MC']}")
    else:
        st.info("You are NOT dispatched.")
    st.dataframe(df[['username','MC','price','cum_supply']]) 