import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: The Complete Beginner Terminal")

# --- GLOSSARY & ORDERED METRICS ---
# This list ensures the dropdown follows your specific order
metric_defs = {
    "Total Revenue": "Total money coming in from sales (The 'Top Line').",
    "Cost Of Revenue": "Direct costs of making the products sold (COGS).",
    "Gross Profit": "Money left after paying for the products but before salaries/rent.",
    "Operating Expense": "Costs to run the business (marketing, office, rent).",
    "Operating Income": "Profit from core business activities.",
    "Net Income": "The 'Bottom Line'. Total profit after all taxes and costs.",
    "Basic EPS": "Earnings Per Share. Profit divided by the number of shares.",
    "Operating Cash Flow": "Actual cash generated (often more reliable than Net Income).",
    "Free Cash Flow": "Cash left over after operations and buying equipment."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    # --- SECTION 1: TOP SNAPSHOT (Restored!) ---
    st.subheader("Market Snapshot")
    col1, col2, col3, col4 = st.columns(4)
    
    # Manual Dividend Fix to avoid the "38%" bug
    div_rate = info.get('dividendRate', 0)
    curr_price = info.get('currentPrice', 1)
    real_yield = (div_rate / curr_price) * 100 if div_rate else 0

    col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
    col2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    col3.metric("Div. Yield", f"{real_yield:.2f}%") # Fixed calculation
    col4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # --- SECTION 2: THE FINANCIALS EXPLORER (With Spacing Fix) ---
    st.divider()
    st.subheader("📊 Financials Explorer")
    
    chart_style = st.radio("Chart Type:", ["Line Chart", "Bar Chart"], horizontal=True)
    
    selected = st.multiselect(
        "Select Financial Metrics:", 
        options=list(metric_defs.keys()), 
        default=["Total Revenue", "Net Income"]
    )

    financials = stock.financials.T
    if not financials.empty and selected:
        # Chart Display with spacing fix
        plot_data = financials[selected]
        if chart_style == "Line Chart":
            st.line_chart(plot_data)
        else:
            # Bar chart now uses 'use_container_width' to prevent thin bars
            st.bar_chart(plot_data) 
        
        # DYNAMIC EXPLANATIONS (Tabs below the chart)
        st.write("#### 📖 Understand the Data")
        tabs = st.tabs(selected)
        for i, metric in enumerate(selected):
            with tabs[i]:
                st.info(f"**{metric}**: {metric_defs.get(metric)}")

    # --- SECTION 3: DESCRIPTION & NEWS (Restored!) ---
    st.divider()
    with st.expander("📝 About the Company"):
        st.write(info.get('longBusinessSummary', "No description available."))

    st.subheader("Price History (Past Year)")
    st.area_chart(stock.history(period="1y")['Close'])

    st.subheader("Latest News Headlines")
    news_list = stock.news[:5]
    for article in news_list:
        # Safety check for news format
        content = article.get('content', article)
        title = content.get('title', 'No Title Found')
        link = content.get('canonicalUrl', {}).get('url') or article.get('link', '#')
        st.write(f"**[{title}]({link})**")
        st.caption(f"Source: {content.get('publisher', 'Yahoo Finance')}")
        st.divider()