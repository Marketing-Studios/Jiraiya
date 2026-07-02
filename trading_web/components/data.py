# components/data.py
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd
import yfinance as yf

SUPPORTED_INTRADAY = ["1m", "2m", "5m", "15m"]

def list_supported_intervals():
    return SUPPORTED_INTRADAY

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
        start=start_dt, end=end_dt, interval=ivl,
        auto_adjust=False, actions=False
    )
    return _clean(df)

def fetch_daily(sym: str, period: str) -> pd.DataFrame:
    df = yf.Ticker(sym).history(
        period=period, interval="1d",
        auto_adjust=False, actions=False
    )
    return _clean(df)
