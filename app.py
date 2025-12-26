import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: The Pro Terminal")

# Sidebar
with st.sidebar:
    st.header("🎨 Styles")
    user_color = st.color_picker("Primary Bar Color", "#00FFAA")

# 1. SMART MAPPING (Finds data even if Yahoo changes labels)
metrics_to_find = {
    "Total Revenue": ["Total Revenue", "Revenue", "TotalRevenue"],
    "Net Income": ["Net Income", "NetIncome"],
    "Free Cash Flow": ["Free Cash Flow", "FreeCashFlow"],
    "Gross Profit": ["Gross Profit", "GrossProfit"],
    "Operating Cash Flow": ["Operating Cash Flow", "CashFlowFromOperations"]
}

metric_defs = {
    "Total Revenue": "Total money coming in (The 'Top Line').",
    "Net Income": "Final profit after all taxes and costs.",
    "Free Cash Flow": "Cash available for expansion or dividends.",
    "Gross Profit": "Money left after manufacturing costs.",
    "Operating Cash Flow": "Actual cash flowing from core business."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    # --- 2. MARKET SNAPSHOT ---
    st.subheader("Market Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    price = info.get('currentPrice', 1)
    div = info.get('dividendRate', 0)
    y_val = (div / price) * 100 if div else 0
    
    c1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
    c2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    c3.metric("Div. Yield", f"{y_val:.2f}%")
    c4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # --- 3. DATA CLEANING (The "Logic Fix") ---
    try:
        # Merge financials and cashflow
        all_raw = pd.concat([stock.financials.T, stock.cashflow.T], axis=1)
        all_raw = all_raw.loc[:, ~all_raw.columns.duplicated()]
        
        # Build clean table using our map
        clean_df = pd.DataFrame(index=all_raw.index)
        for display_name, options in metrics_to_find.items():
            for opt in options:
                if opt in all_raw.columns:
                    clean_df[display_name] = all_raw[opt]
                    break
        clean_df.index = pd.to_datetime(clean_df.index).year
    except:
        clean_df = pd.DataFrame()

    # --- 4. THE CHART & GLOSSARY TABS ---
    st.divider()
    st.subheader("📊 Financials Explorer")
    selected = st.multiselect("Pick Metrics:", options=list(metric_defs.keys()), default=["Total Revenue", "Net Income"])

    if not clean_df.empty and selected:
        valid_selected = [m for m in selected if m in clean_df.columns]
        plot_data = clean_df[valid_selected]
        
        # Side-by-Side Bar Chart
        fig = px.bar(
            plot_data, 
            x=plot_data.index, 
            y=plot_data.columns,
            barmode='group', # Side-by-Side Fix
            color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B"]
        )
        
        # Spacing Fix
        fig.update_layout(
            bargap=0.15, bargroupgap=0.05,
            xaxis=dict(type='category', title="Year"),
            yaxis=dict(title="Amount ($)")
        )
        st.plotly_chart(fig, use_container_width=True)

        # Glossary Tabs
        st.write("#### 📖 Glossary")
        tabs = st.tabs(valid_selected)
        for i, m in enumerate(valid_selected):
            with tabs[i]: st.info(f"**{m}**: {metric_defs.get(m)}")

    # --- 5. ABOUT & NEWS RESTORED ---
    st.divider()
    with st.expander("📝 About"):
        st.write(info.get('longBusinessSummary', "N/A"))

    st.subheader("Latest News")
    for article in stock.news[:4]:
        # Fix for empty titles
        title = article.get('title') or article.get('content', {}).get('title', "Latest Update")
        link = article.get('link') or article.get('content', {}).get('canonicalUrl', {}).get('url', "#")
        st.write(f"**[{title}]({link})**")
        st.divider()