import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Pro Terminal", layout="wide")

# Sidebar for controls
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Enter Symbol", "AAPL").upper()
time_period = st.sidebar.selectbox("Select Timeframe", ["1mo", "6mo", "1y", "5y"])

if ticker:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # 1. Elegant Header
    st.title(f"📊 {info.get('longName', ticker)}")
    
    # 2. Metric Tiles (Elevates the look)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Price", f"${info.get('currentPrice')}", f"{info.get('revenueGrowth')}%")
    col2.metric("52W High", f"${info.get('fiftyTwoWeekHigh')}")
    col3.metric("P/E Ratio", info.get('trailingPE'))
    col4.metric("Analyst Target", f"${info.get('targetMeanPrice')}")

    # 3. Interactive Chart
    st.subheader("Price History")
    data = stock.history(period=time_period)
    st.area_chart(data['Close']) # Area charts look more modern than line charts

    # 4. Adding "Meat": Major Holders or News
    st.subheader("Major Institutional Holders")
    st.write(stock.institutional_holders)
    