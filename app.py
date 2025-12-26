import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: The Pro Terminal")

# Sidebar
with st.sidebar:
    st.header("🎨 Dashboard Styles")
    user_color = st.color_picker("Pick a Chart Color", "#00FFAA")

# Simplified Metric Names for 2025 Stability
metric_defs = {
    "Total Revenue": "Total money coming in.",
    "Net Income": "Final profit after all costs.",
    "Free Cash Flow": "Cash left after expenses/equipment."
}

ticker = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker:
    stock = yf.Ticker(ticker)
    
    # 1. THE DATA FETCH (Simple & Safe)
    try:
        # Merge financials and cashflow tables
        df = pd.concat([stock.financials.T, stock.cashflow.T], axis=1)
        df = df.loc[:,~df.columns.duplicated()] # Remove duplicates
        df.index = pd.to_datetime(df.index).year # Use years only
    except:
        st.error("Data fetch failed. Trying basic info...")
        df = pd.DataFrame()

    # 2. MARKET SNAPSHOT
    info = stock.info
    c1, c2, c3 = st.columns(3)
    c1.metric("Price", f"${info.get('currentPrice', 'N/A')}")
    c2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    c3.metric("Risk", info.get('overallRisk', 'N/A'))

    # 3. THE "SPACING FIX" CHART
    st.subheader("📊 Financials Explorer")
    selected = st.multiselect("Pick Metrics:", options=list(metric_defs.keys()), default=["Total Revenue", "Net Income"])
    
    if not df.empty and selected:
        valid = [m for m in selected if m in df.columns]
        if valid:
            # PLOTLY GROUPED BARS (Side-by-Side)
            fig = px.bar(df, x=df.index, y=valid, barmode='group',
                         color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1"])
            
            # This 'bargap' ensures they aren't skinny and have no huge space
            fig.update_layout(bargap=0.2, bargroupgap=0.05, xaxis_title="Year")
            st.plotly_chart(fig, use_container_width=True)
            
            # Explanation Tabs
            tabs = st.tabs(valid)
            for i, m in enumerate(valid):
                with tabs[i]: st.info(f"**{m}**: {metric_defs[m]}")

    # 4. NEWS (Simple list)
    st.divider()
    st.subheader("Latest News")
    for a in stock.news[:3]:
        st.write(f"**[{a.get('title', 'News')}]({a.get('link', '#')})**")