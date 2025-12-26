import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TickerTotal", layout="wide")

# Sidebar Glossary
with st.sidebar:
    st.header("📖 Beginner Glossary")
    st.markdown("**Revenue**: Total money coming in.")
    st.markdown("**COGS**: The direct cost of making the products sold.")
    st.markdown("**Gross Profit**: Revenue minus COGS.")
    st.info("Tip: Use the 'Financials Explorer' below to see these on a graph!")

st.title("🔍 TickerTotal: The Simple Stock Explainer")

ticker_symbol = st.text_input("Enter a Stock Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    
    # --- SECTION 1: MARKET SNAPSHOT ---
    st.subheader("Market Snapshot")
    col1, col2, col3, col4 = st.columns(4)
    info = stock.info
    col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
    col2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    col3.metric("Div. Yield", f"{info.get('dividendYield', 0) * 100:.2f}%")
    col4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # --- SECTION 2: THE FINANCIALS EXPLORER (New!) ---
    st.divider()
    st.subheader("📊 Financials Explorer")
    st.write("Choose metrics to compare how the company's money moves over time.")

    # Fetch Income Statement
    financials = stock.financials.T # Transpose to make years the rows
    
    if not financials.empty:
        # Let users pick what they want to see
        # We use a default of Revenue and Cost Of Revenue
        available_metrics = financials.columns.tolist()
        selected_metrics = st.multiselect(
            "Select Metrics to Plot:", 
            options=available_metrics, 
            default=["Total Revenue", "Cost Of Revenue"] if "Total Revenue" in available_metrics else available_metrics[:2]
        )

        if selected_metrics:
            # Create a chart with the selected lines
            chart_data = financials[selected_metrics]
            st.line_chart(chart_data)
            st.caption("Data shown by fiscal year (past 4 years).")
    else:
        st.warning("Annual financial data not available for this ticker.")

    # --- SECTION 3: DESCRIPTION & NEWS ---
    st.divider()
    with st.expander("📝 What does this company actually do?"):
        st.write(info.get('longBusinessSummary', "No description available."))

    st.subheader("Price History (Past Year)")
    st.area_chart(stock.history(period="1y")['Close'])

    st.subheader(f"Latest News")
    for article in stock.news[:5]:
        content = article.get('content', article)
        st.write(f"**[{content.get('title', 'No Title')}]({content.get('canonicalUrl', {}).get('url') or article.get('link', '#')})**")
        st.divider()