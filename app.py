import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: The Complete Terminal")

# --- SIDEBAR STYLE ---
with st.sidebar:
    st.header("🎨 Styles")
    user_color = st.color_picker("Primary Bar Color", "#00FFAA")
    st.divider()
    st.markdown("### 📖 Quick Glossary")
    st.caption("Gross Margin: Profit % after making the product.")
    st.caption("Free Cash Flow: Real cash left to spend.")

# 1. THE BIG MAPPING (Ensures we find the right data regardless of Yahoo's labels)
metrics_to_find = {
    "Total Revenue": ["Total Revenue", "Revenue"],
    "Cost Of Revenue": ["Cost Of Revenue", "COGS"],
    "Gross Profit": ["Gross Profit"],
    "Operating Expense": ["Operating Expenses", "Total Operating Expenses"],
    "Operating Income": ["Operating Income"],
    "Net Income": ["Net Income"],
    "Basic EPS": ["Basic EPS", "EPS"],
    "Operating Cash Flow": ["Operating Cash Flow", "Total Cash From Operating Activities"],
    "Free Cash Flow": ["Free Cash Flow"]
}

metric_defs = {
    "Total Revenue": "Total money coming in.",
    "Cost Of Revenue": "Direct costs of production.",
    "Gross Profit": "Money left after manufacturing costs.",
    "Operating Expense": "Costs to keep the lights on and pay staff.",
    "Operating Income": "Core business profit.",
    "Net Income": "Final profit after taxes.",
    "Basic EPS": "Earnings per share.",
    "Operating Cash Flow": "Actual cash flowing into the bank.",
    "Free Cash Flow": "Cash available for expansion or dividends."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    
    # --- 2. THE MARKET SNAPSHOT ---
    info = stock.info
    st.subheader("Market Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    
    price = info.get('currentPrice', 1)
    div = info.get('dividendRate', 0)
    y_val = (div / price) * 100 if div else 0
    
    c1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
    c2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    c3.metric("Div. Yield", f"{y_val:.2f}%")
    c4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # --- 3. DATA CLEANING & MERGING ---
    try:
        raw_fin = stock.financials.T
        raw_cf = stock.cashflow.T
        all_raw = pd.concat([raw_fin, raw_cf], axis=1)
        all_raw = all_raw.loc[:, ~all_raw.columns.duplicated()]
        
        # Build a clean table based on our map
        clean_df = pd.DataFrame(index=all_raw.index)
        for display_name, options in metrics_to_find.items():
            for opt in options:
                if opt in all_raw.columns:
                    clean_df[display_name] = all_raw[opt]
                    break
        clean_df.index = pd.to_datetime(clean_df.index).year
    except:
        clean_df = pd.DataFrame()

    # --- 4. THE CHART (Grouped Bars & Color Fix) ---
    st.divider()
    st.subheader("📊 Financials Explorer")
    
    selected = st.multiselect("Select Metrics:", options=list(metric_defs.keys()), default=["Total Revenue", "Net Income"])

    if not clean_df.empty and selected:
        plot_data = clean_df[[m for m in selected if m in clean_df.columns]]
        
        # Plotly logic for Side-by-Side 
        fig = px.bar(
            plot_data, 
            x=plot_data.index, 
            y=plot_data.columns,
            barmode='group',
            color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA"]
        )
        
        fig.update_layout(
            bargap=0.15, bargroupgap=0.05,
            xaxis=dict(type='category', title="Year"),
            yaxis=dict(title="Amount ($)"),
            margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabs for definitions
        tabs = st.tabs(list(plot_data.columns))
        for i, m in enumerate(plot_data.columns):
            with tabs[i]: st.info(f"**{m}**: {metric_defs.get(m)}")

    # --- 5. ABOUT & NEWS RESTORED ---
    st.divider()
    with st.expander("📝 About the Company"):
        st.write(info.get('longBusinessSummary', "No description available."))

    st.subheader("Latest News Headlines")
    # Fix for empty news titles
    for article in stock.news[:5]:
        content = article.get('content', article)
        title = content.get('title') or article.get('title') or "Latest Market Update"
        link = content.get('canonicalUrl', {}).get('url') or article.get('link', '#')
        st.write(f"**[{title}]({link})**")
        st.caption(f"Source: {content.get('publisher', 'Finance News')}")
        st.divider()