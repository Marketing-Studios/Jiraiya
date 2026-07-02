# components/chart.py
import numpy as np
import plotly.graph_objects as go
import pandas as pd

def _fake_signals(df: pd.DataFrame):
    # Simple demo signals: green every 12th bar, red 6 bars after
    n = len(df.index)
    buys = list(range(3, n, 12))
    sells = list(range(9, n, 12))
    return buys, sells

def make_candles_with_signals(df: pd.DataFrame, title: str = ""):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"]
    )])
    buys, sells = _fake_signals(df)
    if buys:
        fig.add_scatter(
            x=df.index[buys], y=df["Low"].iloc[buys],
            mode="markers", marker=dict(color="green", size=8),
            name="Buy"
        )
    if sells:
        fig.add_scatter(
            x=df.index[sells], y=df["High"].iloc[sells],
            mode="markers", marker=dict(color="red", size=8),
            name="Sell"
        )
    fig.update_layout(
        title=title,
        height=520,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
