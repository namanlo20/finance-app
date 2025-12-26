import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: Pro Beginner Terminal")

# --- SIDEBAR: COLOR SETTINGS ---
with st.sidebar:
    st.header("🎨 Dashboard Styles")
    user_color = st.color_picker("Pick a Primary Chart Color", "#636EFA")
    st.info("Bars are now 'Grouped' side-by-side for easier reading.")

# Ordered metrics as you requested
metric_defs = {
    "Total Revenue": "Total money coming in.",
    "Cost Of Revenue": "Direct costs of making products.",
    "Net Income": "Final profit after all costs.",
    "Operating Cash Flow": "Actual cash from operations.",
    "Free Cash Flow": "Cash left after expenses/equipment."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    
    # 1. STABLE DATA FETCH (Merged Statements)
    # We use a try-except block so one missing table doesn't kill the whole app
    try:
        all_data = pd.concat([stock.financials.T, stock.cashflow.T], axis=1)
        all_data = all_data.loc[:,~all_data.columns.duplicated()]
    except:
        st.error("Could not fetch full financial tables. Yahoo might be rate-limiting.")
        all_data = pd.DataFrame()

    # 2. MARKET SNAPSHOT
    info = stock.info
    st.subheader("Market Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    # Manual Dividend Fix
    div_rate = info.get('dividendRate', 0)
    curr_price = info.get('currentPrice', 1)
    real_yield = (div_rate / curr_price) * 100 if div_rate else 0

    c1.metric("Price", f"${info.get('currentPrice', 'N/A')}")
    c2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    c3.metric("Div. Yield", f"{real_yield:.2f}%")
    c4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # 3. PROFESSIONAL GROUPED BAR CHART
    st.divider()
    st.subheader("📊 Side-by-Side Financials")
    selected = st.multiselect("Pick Metrics:", options=list(metric_defs.keys()), default=["Total Revenue", "Net Income"])
    
    if not all_data.empty and selected:
        valid_selected = [m for m in selected if m in all_data.columns]
        if valid_selected:
            plot_df = all_data[valid_selected].copy()
            plot_df.index = plot_df.index.strftime('%Y')
            
            fig = px.bar(
                plot_df, 
                x=plot_df.index, 
                y=valid_selected, 
                barmode='group', # MAKES BARS SIDE-BY-SIDE
                color_discrete_sequence=[user_color, "#EF553B", "#00CC96", "#AB63FA"]
            )
            
            # SPACING FIX: No more thin bars or huge gaps
            fig.update_layout(
                bargap=0.15, 
                bargroupgap=0.05,
                xaxis_title="Fiscal Year",
                yaxis_title="Amount ($)",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. EXPLANATION TABS (Restored)
            st.write("#### 📖 Understand the Data")
            tabs = st.tabs(valid_selected)
            for i, m in enumerate(valid_selected):
                with tabs[i]: st.info(f"**{m}**: {metric_defs.get(m)}")
        else:
            st.warning("Selected metrics not found for this ticker.")

    # 5. NEWS (Restored with safety checks)
    st.divider()
    st.subheader("Latest News")
    for article in stock.news[:3]:
        content = article.get('content', article)
        title = content.get('title', 'No Title')
        link = content.get('canonicalUrl', {}).get('url') or article.get('link', '#')
        st.write(f"**[{title}]({link})**")
        st.divider()