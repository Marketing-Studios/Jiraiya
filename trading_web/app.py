# app.py
import os
import base64
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ---------- PAGE ----------
st.set_page_config(page_title="PsYcGoD (AI Trader)", layout="wide")  # wide layout [docs] [1]

def apply_css_file(path: str):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)  # inject CSS [2]
    else:
        st.write(f"CSS not found: {path}")  # debug

def set_divine_background(img_path: str):
    """
    Sets a custom background image for the Streamlit app using the specified image path.

    Parameters:
        img_path (str): The file path to the background image.
    """
    if not os.path.exists(img_path):
        st.write(f"Background missing at: {img_path}")  # debug
        return
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    css = f"""
        <style>
        .stApp::before {{
            content:"";
            position:fixed; inset:0;
            background-image:
              radial-gradient(80% 120% at 10% 10%, rgba(120,0,255,0.20), transparent 40%),
              radial-gradient(80% 120% at 90% 90%, rgba(0,255,220,0.18), transparent 40%),
              url("data:image/png;base64,{b64}");
            background-size:cover;
            background-position:center;
            opacity:0.22; z-index:-1;
            filter:saturate(120%) hue-rotate(8deg);
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)  # page-level background via base64 [3]

# call helpers right after defining them
os.makedirs("assets", exist_ok=True)          # ensure folder exists [docs] [1]
apply_css_file("assets/styles.css")           # optional custom styles [2]
set_divine_background("assets/psy_bg.png") # exact image path required [3]
# --- continue with the rest of your file below ---
# ---------- DATA FETCH ----------
def _clean(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    for c in ["Open", "High", "Low", "Close"]:
        if c in df:
            df = df[df[c] > 0]
    return df

def fetch_intraday(sym: str, ivl: str, days: int) -> pd.DataFrame:
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=days)
    df = yf.Ticker(sym).history(
        start=start_dt, end=end_dt, interval=ivl, auto_adjust=False, actions=False
    )
    return _clean(df)

def fetch_daily(sym: str, period: str) -> pd.DataFrame:
    df = yf.Ticker(sym).history(
        period=period, interval="1d", auto_adjust=False, actions=False
    )
    return _clean(df)

# ---------- HEADER ----------
st.markdown('<div class="app-header">🤖 PsYcGoD (AI Trader)</div>', unsafe_allow_html=True)

# ---------- CONTROLS ----------
left, mid, right = st.columns([2, 2, 2], gap="small")
with left:
    ticker = st.text_input(
        "Symbol (e.g., RELIANCE.NS, TCS.NS, INFY.NS)", "RELIANCE.NS"
    ).strip().upper()
with mid:
    mode = st.selectbox("Mode", ["Intraday", "Daily"], index=0)
with right:
    if mode == "Intraday":
        interval = st.selectbox("Interval", ["1m", "2m", "5m", "15m"], index=2)
        lookback = st.selectbox("Lookback (days)", [1, 3, 5, 7, 10, 14], index=2)
    else:
        interval = "1d"
        lookback = None

bar1, bar2, bar3 = st.columns([1, 1, 1], gap="small")
with bar1:
    run_btn = st.button("Load / Refresh", type="primary", key="run")
with bar2:
    st.button("Start Auto Refresh", key="auto")
with bar3:
    st.button("Clear Signals", key="clear")

# ---------- DATA STATE ----------
if run_btn:
    if mode == "Intraday":
        df = fetch_intraday(ticker, interval, lookback or 5)
        title = f"{ticker} • {interval}, last {lookback or 5}d"
        if df is None or df.empty:
            st.warning("Intraday empty; showing daily 1mo fallback.")
            df = fetch_daily(ticker, "1mo")
            title = f"{ticker} • 1mo (fallback)"
    else:
        df = fetch_daily(ticker, "1mo")
        title = f"{ticker} • 1mo (1d)"
    st.session_state["df"] = df
    st.session_state["title"] = title

df = st.session_state.get("df", pd.DataFrame())
title = st.session_state.get("title", "Load data")

# ---------- LAYOUT ----------
L, C, R = st.columns([0.18, 0.64, 0.18], gap="small")

with L:
    st.markdown('<div class="panel"><div class="panel-title">PL Summary</div>', unsafe_allow_html=True)
    st.metric("Total P&L", "₹0.00", delta="+0.00%")
    st.metric("Today’s P&L", "₹0.00", delta="-0.00%")
    st.metric("Equity P&L", "₹0.00", delta="+0.00%")
    st.markdown("</div>", unsafe_allow_html=True)

with C:
    if not df.empty:
        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"], high=df["High"],
                low=df["Low"], close=df["Close"],
                increasing_line_color="#00e5a0",
                decreasing_line_color="#ff4d6d",
                increasing_fillcolor="#00e5a0",
                decreasing_fillcolor="#ff4d6d",
            )
        )
        # Demo signal markers
        idx = np.arange(3, len(df.index), 13)
        jdx = np.arange(9, len(df.index), 13)
        if len(idx):
            fig.add_scatter(
                x=df.index[idx], y=df["Low"].iloc[idx],
                mode="markers", name="Buy",
                marker=dict(color="#00ffd1", size=9, line=dict(width=1.5, color="#021b1f")),
            )
        if len(jdx):
            fig.add_scatter(
                x=df.index[jdx], y=df["High"].iloc[jdx],
                mode="markers", name="Sell",
                marker=dict(color="#ff4d6d", size=9, line=dict(width=1.5, color="#2a0b13")),
            )
        fig.update_layout(
            template="plotly_dark",
            height=560,
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis_rangeslider_visible=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            title=title,
            font=dict(color="#d8f3ff"),
        )
        st.markdown('<div class="panel chart-panel">', unsafe_allow_html=True)
        st.plotly_chart(fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Click Load / Refresh to draw the chart.")

with R:
    st.markdown('<div class="panel"><div class="panel-title">Controls</div>', unsafe_allow_html=True)
    st.checkbox("Dry Run", value=True, key="dry")
    st.checkbox("Alerts", value=False, key="alerts")
    st.selectbox("Strategy", ["Val’s Logic", "Mean Revert", "Breakout"], index=0, key="strat")
    st.button("Detect Regime", key="regime")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown('<div class="footer-log">UI ready • style=psychedelic • divine_bg=on</div>', unsafe_allow_html=True)

