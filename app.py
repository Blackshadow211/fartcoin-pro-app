
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
    EMAIL_ADDRESS = "remixbooster2@gmail.com"  # Replace with your bot email
    APP_PASSWORD = "xjlrszqzjtmvprfo"     # Replace with your app password
    RECIPIENT_EMAIL = "remixbooster2@gmail.com"  # Replace with your email

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
df = fetch_price_data()
if df.empty:
    st.error("Failed to fetch price data. Please try again later.")
    st.stop()

    url = "https://api.mexc.com/api/v3/klines?symbol=FARTCOINUSDT&interval=1m&limit=100"
    response = requests.get(url)
    if response.status_code == 200:
        raw_data = response.json()
        if not raw_data:
            return pd.DataFrame()  # Return empty if no data

        df = pd.DataFrame(raw_data, columns=[
            "timestamp", "open", "high", "low", "close", "volume", 
            "_", "_", "_", "_", "_", "_"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df["close"] = pd.to_numeric(df["close"])
        return df
    else:
        return pd.DataFrame()  # Return empty if request fails


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
