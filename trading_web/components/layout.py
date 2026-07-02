# components/layout.py
import streamlit as st
import pandas as pd

def top_metrics(df: pd.DataFrame):
    st.markdown("#### Overview")
    col1, col2 = st.columns(2)
    last_px = float(df["Close"].iloc[-1]) if not df.empty else 0.0
    st.metric("Last Price", f"{last_px:,.2f}")
    with col1:
        st.metric("P&L Today", "₹0", delta="+0.0%")
    with col2:
        st.metric("Positions", "0")

def right_controls():
    st.markdown("#### Controls")
    st.checkbox("Show signals", value=True)
    st.checkbox("Show volume", value=False)
    st.selectbox("Theme", ["Light", "Dark"], index=0)
    st.button("Reset zoom")

def bottom_log():
    st.markdown("---")
    st.markdown("##### Activity")
    logs = st.session_state.get("logs", [])
    if logs:
        st.code("\n".join(logs[-10:]), language="text")
    else:
        st.caption("No recent activity.")
