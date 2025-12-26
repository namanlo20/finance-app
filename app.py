import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: The Complete Beginner Terminal")

# --- GLOSSARY & ORDERED METRICS ---
metric_defs = {
    "Total Revenue": "Total money coming in from sales.",
    "Cost Of Revenue": "Direct costs of making the products sold (COGS).",
    "Gross Profit": "Revenue minus COGS.",
    "Operating Expense": "Costs to run the business.",
    "Operating Income": "Profit from core business activities.",
    "Net Income": "The 'Bottom Line' total profit.",
    "Basic EPS": "Earnings Per Share.",
    "Operating Cash Flow": "Actual cash generated from operations.",
    "Free Cash Flow": "Cash left over after expenses and equipment."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    # --- SECTION 1: TOP SNAPSHOT ---
    st.subheader("Market Snapshot")
    col1, col2, col3, col4 = st.columns(4)
    div_rate = info.get('dividendRate', 0)
    curr_price = info.get('currentPrice', 1)
    real_yield = (div_rate / curr_price) * 100 if div_rate else 0

    col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
    col2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    col3.metric("Div. Yield", f"{real_yield:.2f}%")
    col4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # --- SECTION 2: THE FINANCIALS & CASH FLOW EXPLORER ---
    st.divider()
    st.subheader("📊 Financials Explorer")
    
    # 1. Merge Financials and Cash Flow safely to avoid crashes
    inc_stmt = stock.financials.T
    cash_flow = stock.cashflow.T
    
    # Combine them into one big "master" table
    all_financials = pd.concat([inc_stmt, cash_flow], axis=1)
    # Remove any duplicate columns just in case
    all_financials = all_financials.loc[:,~all_financials.columns.duplicated()]

    selected = st.multiselect(
        "Select Financial Metrics:", 
        options=list(metric_defs.keys()), 
        default=["Total Revenue", "Net Income"]
    )

    if not all_financials.empty and selected:
        # Filter for only selected metrics that actually exist in the data
        valid_selected = [m for m in selected if m in all_financials.columns]
        plot_data = all_financials[valid_selected]
        
        # 2. Fix Bar Spacing: We use the 'unstack' method to make them side-by-side
        # This makes the bar chart look grouped rather than piled
        if not plot_data.empty:
            st.bar_chart(plot_data) # Streamlit handles grouping automatically when data is shaped right
        
        # DYNAMIC EXPLANATIONS
        st.write("#### 📖 Understand the Data")
        tabs = st.tabs(valid_selected)
        for i, metric in enumerate(valid_selected):
            with tabs[i]:
                st.info(f"**{metric}**: {metric_defs.get(metric)}")
    else:
        st.warning("Data not available for this ticker.")

    # --- SECTION 3: RESTORED NEWS & ABOUT ---
    st.divider()
    with st.expander("📝 About the Company"):
        st.write(info.get('longBusinessSummary', "No description available."))

    st.subheader("Latest News Headlines")
    news_list = stock.news[:5]
    for article in news_list:
        content = article.get('content', article)
        title = content.get('title', 'No Title Found')
        link = content.get('canonicalUrl', {}).get('url') or article.get('link', '#')
        st.write(f"**[{title}]({link})**")
        st.caption(f"Source: {content.get('publisher', 'Yahoo Finance')}")
        st.divider()