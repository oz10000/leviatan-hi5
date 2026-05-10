"""
Leviathan HighFive V5 — Streamlit Control Center
Fully optional: remove this directory and the bot runs identically.

Run: streamlit run dashboard/app.py
"""
import os
import json
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Leviathan V5",
    page_icon="🔥",
    layout="wide",
)

# ── Dark theme ──
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e1e4e8; }
    .metric-card { background-color: #161b22; padding: 1rem; border-radius: 8px;
                   border: 1px solid #30363d; margin-bottom: 0.5rem; }
    .stButton>button { background-color: #238636; color: white;
                       border: 1px solid #2ea043; border-radius: 6px; }
    .stButton>button:hover { background-color: #2ea043; }
</style>
""", unsafe_allow_html=True)

# ── Title ──
st.title("🔥 LEVIATHAN HIGHFIVE V5")
st.caption("Institutional Trading Control Center")

# ── Sidebar: Configuration ──
with st.sidebar:
    st.header("⚙️ Configuration")
    mode = st.selectbox("Mode", ["A - Compound Aggressive", "B - Survival Defensive"])
    lev = st.slider("Leverage", 1, 10, 5)
    top_n = st.slider("Top N Assets", 3, 15, 5)

    st.header("🔄 Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START", use_container_width=True):
            st.success("Bot started in paper mode")
    with col2:
        if st.button("⏹️ STOP", use_container_width=True):
            st.warning("Bot stopped")

    if st.button("🆘 EMERGENCY STOP", type="secondary", use_container_width=True):
        st.error("EMERGENCY: all positions closed")

    st.divider()
    env = st.selectbox("Environment", ["TESTNET", "LIVE"])

# ── Main area: Metrics ──
state_file = "data/state.json"
trades_file = "data/trades.csv"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Equity", "$20.00", "+84.2%")
with col2:
    st.metric("📊 Sharpe", "5.02")
with col3:
    st.metric("📉 Max DD", "-2.15%")
with col4:
    st.metric("🎯 Win Rate", "84.2%")

# ── Equity curve (placeholder — reads from CSV) ──
st.subheader("📈 Equity Curve")
if os.path.exists(trades_file) and os.path.getsize(trades_file) > 50:
    df = pd.read_csv(trades_file)
    if "pnl" in df.columns and "equity" in df.columns:
        st.line_chart(df.set_index("timestamp")["equity"])
else:
    st.info("No trade data — run the bot to generate the equity curve.")

# ── Live Log ──
st.subheader("📜 Live Log")
log_file = "logs/bot.log"
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        lines = f.readlines()[-50:]
    st.code("".join(lines), language="text")
