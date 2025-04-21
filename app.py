
import streamlit as st
import time
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# Config
LEVERAGE = 20
EMAIL_ADDRESS = "remixbooster2@gmail.com"
APP_PASSWORD = "xjlrszqzjtmvprfo"
RECIPIENT_EMAIL = "remixbooster2@example.com"

st.set_page_config(page_title="Fartcoin Pro Trade Assistant", layout="centered")

st.title("🧠 Fartcoin Pro Trade Assistant")

st.sidebar.header("Trade Input")
entry = st.sidebar.number_input("Entry Price ($)", value=0.8500, format="%.6f")
exit_price = st.sidebar.number_input("Exit Price ($)", value=0.8700, format="%.6f")
tp = st.sidebar.number_input("Take Profit ($)", value=0.8900, format="%.6f")
balance = st.sidebar.number_input("Account Balance ($)", value=50.0)

# Calculations
position_size = balance * LEVERAGE
pnl = (exit_price - entry) * LEVERAGE / entry * 100
profit_loss = "Profit" if pnl > 0 else "Loss"

st.markdown(f"### 📊 PnL Analysis")
st.markdown(f"- Leverage: **{LEVERAGE}x**")
st.markdown(f"- Position Size: **${position_size:.2f}**")
st.markdown(f"- Expected Result: **{profit_loss}**")
st.markdown(f"- Projected PnL: **{pnl:.2f}%**")

# Function to send email alert
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.send_message(msg)

# Placeholder chart (MEXC data requires frontend iframe or custom integration)
st.markdown("### 📈 Live Fartcoin Chart (TradingView)")
st.components.v1.html("""
    <iframe src="https://www.tradingview.com/embed-widget/symbol-overview/?symbol=MEXC:FARTCOINUSDT" 
            width="100%" height="500" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
""", height=500)


# Auto-refresh
st_autorefresh = st.empty()
count = st_autorefresh.empty()
count.text("⏳ Auto-refreshing every 30 seconds...")
time.sleep(30)
st.experimental_rerun()
