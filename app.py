import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: The Complete Terminal")

# --- SIDEBAR: CUSTOM STYLE ---
with st.sidebar:
    st.header("🎨 Appearance")
    user_color = st.color_picker("Main Bar Color", "#00FFAA")
    st.info("Bars are 'Grouped' for easy side-by-side comparison.")

# Definitions for all your metrics
metric_defs = {
    "Total Revenue": "Total money coming in from sales.",
    "Cost Of Revenue": "Direct costs of making the products sold (COGS).",
    "Gross Profit": "Revenue minus direct production costs.",
    "Operating Income": "Profit from core business activities.",
    "Net Income": "The 'Bottom Line' total profit.",
    "Operating Cash Flow": "Actual cash generated from operations.",
    "Free Cash Flow": "Cash left over after all expenses and equipment."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    
    # --- 1. DATA MERGE (Safe Combining) ---
    try:
        # Merges Income Statement + Cash Flow so metrics like 'Free Cash Flow' work
        all_data = pd.concat([stock.financials.T, stock.cashflow.T], axis=1)
        all_data = all_data.loc[:, ~all_data.columns.duplicated()]
        all_data.index = pd.to_datetime(all_data.index).year # Set index to Year only
    except:
        st.error("Data fetch failed. Try another ticker.")
        all_data = pd.DataFrame()

    # --- 2. RESTORED: MARKET SNAPSHOT ---
    info = stock.info
    if 'currentPrice' in info:
        st.subheader("Market Snapshot")
        col1, col2, col3, col4 = st.columns(4)
        div = info.get('dividendRate', 0)
        yield_val = (div / info['currentPrice']) * 100 if div else 0

        col1.metric("Current Price", f"${info.get('currentPrice')}")
        col2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
        col3.metric("Div. Yield", f"{yield_val:.2f}%")
        col4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # --- 3. THE FINANCIALS EXPLORER (With Fixed Spacing) ---
    st.divider()
    st.subheader("📊 Financials Explorer")
    
    # Multiselect now correctly filters the data
    selected = st.multiselect(
        "Select Financial Metrics:", 
        options=list(metric_defs.keys()), 
        default=["Total Revenue", "Net Income"]
    )

    if not all_data.empty and selected:
        valid_selected = [m for m in selected if m in all_data.columns]
        if valid_selected:
            # PLOTLY: Forces side-by-side bars with 'barmode=group'
            fig = px.bar(
                all_data, 
                x=all_data.index, 
                y=valid_selected,
                barmode='group', 
                color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA"]
            )
            
            # SPACING FIX: Tightens the bars so they fill the space properly
            fig.update_layout(
                bargap=0.15, 
                bargroupgap=0.05,
                xaxis=dict(type='category', title="Year"),
                yaxis=dict(title="Amount ($)"),
                margin=dict(l=0, r=0, t=20, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

            # RESTORED: EXPLANATION TABS
            st.write("#### 📖 Understand the Data")
            tabs = st.tabs(valid_selected)
            for i, m in enumerate(valid_selected):
                with tabs[i]: st.info(f"**{m}**: {metric_defs.get(m)}")

    # --- 4. RESTORED: ABOUT & NEWS ---
    st.divider()
    with st.expander("📝 About the Company"):
        st.write(info.get('longBusinessSummary', "No description available."))

    st.subheader("Latest News")
    for article in stock.news[:4]:
        title = article.get('title', 'News Update')
        link = article.get('link', '#')
        st.markdown(f"**[{title}]({link})**")
        st.divider()