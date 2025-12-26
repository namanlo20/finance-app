import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TickerTotal", layout="wide")

st.title("🔍 TickerTotal: The Simple Stock Explainer")

ticker_symbol = st.text_input("Enter a Stock Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    # --- FIXED DIVIDEND MATH ---
    div_rate = info.get('dividendRate', 0)
    curr_price = info.get('currentPrice', 1) # Avoid division by zero
    # Logic: If div_rate exists, calculate yield manually to avoid the 38% bug
    real_yield = (div_rate / curr_price) * 100 if div_rate else 0
    
    # --- SECTION 1: MARKET SNAPSHOT ---
    st.subheader("Market Snapshot")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
    col2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    # Display the fixed yield
    col3.metric("Div. Yield", f"{real_yield:.2f}%", help="Calculated as (Annual Dividend / Stock Price)")
    col4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # --- SECTION 2: FINANCIALS WITH CHART TOGGLE ---
    st.divider()
    st.subheader("📊 Financials Explorer")
    
    # 1. Added the Chart Type Option
    chart_type = st.radio("Choose Chart Style:", ["Line Chart", "Bar Chart"], horizontal=True)
    
    financials = stock.financials.T
    
    if not financials.empty:
        available_metrics = financials.columns.tolist()
        selected_metrics = st.multiselect(
            "Select Metrics:", 
            options=available_metrics, 
            default=["Total Revenue", "Cost Of Revenue"] if "Total Revenue" in available_metrics else available_metrics[:2]
        )

        if selected_metrics:
            chart_data = financials[selected_metrics]
            
            # 2. Toggle Logic
            if chart_type == "Line Chart":
                st.line_chart(chart_data)
            else:
                st.bar_chart(chart_data)
    else:
        st.warning("Financial data not available.")

    # --- SECTION 3: DESCRIPTION & NEWS ---
    st.divider()
    with st.expander("📝 What does this company actually do?"):
        st.write(info.get('longBusinessSummary', "No description available."))

    st.subheader("Price History")
    st.area_chart(stock.history(period="1y")['Close'])

    st.subheader("Latest News")
    for article in stock.news[:5]:
        content = article.get('content', article)
        st.write(f"**[{content.get('title', 'No Title')}]({content.get('canonicalUrl', {}).get('url') or article.get('link', '#')})**")
        st.divider()