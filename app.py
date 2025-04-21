
import streamlit as st
import time
import requests
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email alert function
def send_email(subject, body):
    EMAIL_ADDRESS = "yourbot@gmail.com"  # Replace with your bot email
    APP_PASSWORD = "yourapppassword"     # Replace with your app password
    RECIPIENT_EMAIL = "youremail@example.com"  # Replace with your email

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Fetch historical prices from MEXC
def fetch_price_data():
    url = "https://api.mexc.com/api/v3/klines?symbol=FARTCOINUSDT&interval=1m&limit=50"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df

def calculate_ema_signals(df):
    df["EMA6"] = df["close"].ewm(span=6, adjust=False).mean()
    df["EMA12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["signal"] = np.where(df["EMA6"] > df["EMA12"], "BUY", "SELL")
    if df["signal"].iloc[-1] != df["signal"].iloc[-2]:
        return df["signal"].iloc[-1]
    return None

# Streamlit UI
st.set_page_config(page_title="Fartcoin EMA Trade App", layout="centered")
st.title("🚀 Fartcoin AI Signal App")

entry = st.number_input("Entry Price", step=0.0001, format="%.4f")
exit_price = st.number_input("Exit Price", step=0.0001, format="%.4f")
tp = st.number_input("Take Profit Price (optional)", step=0.0001, format="%.4f")
balance = st.number_input("Account Balance (USDT)", step=1.0)
leverage = 20

investment = balance * 0.1 * leverage if balance else 0
position_size = investment / entry if entry else 0
pnl = (exit_price - entry) * position_size if exit_price else 0
pnl_percent = (pnl / investment) * 100 if investment else 0

if entry and exit_price:
    st.metric("Projected PnL", f"{pnl:.2f} USDT", f"{pnl_percent:.2f}%")

# TradingView chart
st.markdown("### 📈 Live Fartcoin Chart")
chart = f'''
<iframe src="https://www.tradingview.com/widgetembed/?symbol=MEXC:FARTCOINUSDT&interval=1&theme=dark&style=1" width="100%" height="500" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
'''
st.components.v1.html(chart, height=500)

# Signal detection
df = fetch_price_data()
signal = calculate_ema_signals(df)

if signal:
    st.success(f"New Trade Signal: {signal}")
    send_email(f"Fartcoin Trade Signal: {signal}", f"New Signal: {signal} — check the chart for timing.")

# Auto-refresh every 5 seconds
st.markdown("⏳ Auto-refreshing every 5 seconds...")
time.sleep(5)
st.experimental_rerun()
