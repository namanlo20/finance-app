import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px  # New powerful charting library

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: Pro Beginner Terminal")

# --- SIDEBAR: COLOR & SETTINGS ---
with st.sidebar:
    st.header("🎨 Dashboard Styles")
    # Let users choose the color for their main bars
    user_color = st.color_picker("Pick a Primary Chart Color", "#636EFA")
    st.divider()
    st.info("Tip: Grouped bars show your chosen metrics side-by-side for easy comparison.")

# --- GLOSSARY & ORDERED METRICS ---
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
    
    # 1. DATA MERGING (Combine Financials + Cash Flow)
    all_data = pd.concat([stock.financials.T, stock.cashflow.T], axis=1)
    all_data = all_data.loc[:,~all_data.columns.duplicated()]

    # 2. MARKET SNAPSHOT (Restored)
    info = stock.info
    st.subheader("Market Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Price", f"${info.get('currentPrice', 'N/A')}")
    c2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    
    div_rate = info.get('dividendRate', 0)
    curr_price = info.get('currentPrice', 1)
    real_yield = (div_rate / curr_price) * 100 if div_rate else 0
    c3.metric("Div. Yield", f"{real_yield:.2f}%")
    c4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # 3. ADVANCED GROUPED BAR CHART
    st.divider()
    st.subheader("📊 Side-by-Side Financials")
    
    selected = st.multiselect("Pick Metrics:", options=list(metric_defs.keys()), default=["Total Revenue", "Net Income"])
    
    if not all_data.empty and selected:
        # Prepare data for Plotly (Must be 'melted' for best grouping)
        plot_df = all_data[selected].copy()
        plot_df.index = plot_df.index.strftime('%Y') # Just show the year
        
        # Create the Plotly Grouped Bar Chart
        fig = px.bar(
            plot_df, 
            x=plot_df.index, 
            y=selected, 
            barmode='group', # THIS puts bars side-by-side
            color_discrete_sequence=[user_color, "#EF553B", "#00CC96", "#AB63FA"] # Uses your picker + defaults
        )
        
        # Professional Spacing & Styling
        fig.update_layout(
            bargap=0.15, 
            bargroupgap=0.1, 
            xaxis_title="Fiscal Year",
            yaxis_title="Amount ($)",
            legend_title="Metric",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True) # Forces stretch to fill screen

        # 4. EXPLANATION TABS & NEWS (Restored)
        st.write("#### 📖 Understand the Data")
        tabs = st.tabs(selected)
        for i, m in enumerate(selected):
            with tabs[i]: st.info(f"**{m}**: {metric_defs.get(m)}")

    st.divider()
    with st.expander("📝 About"):
        st.write(info.get('longBusinessSummary', "N/A"))

    st.subheader("Latest News")
    for article in stock.news[:3]:
        content = article.get('content', article)
        st.write(f"**[{content.get('title', 'N/A')}]({content.get('canonicalUrl', {}).get('url') or article.get('link', '#')})**")
        st.divider()