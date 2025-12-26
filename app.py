import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: 10-Year Pro Terminal")

# --- SIDEBAR: DYNAMIC CONTROLS ---
with st.sidebar:
    st.header("⚙️ Data Settings")
    view_mode = st.radio("Frequency:", ["Annual", "Quarterly"])
    years_to_show = st.slider("Years of History:", min_value=1, max_value=15, value=5)
    st.divider()
    user_color = st.color_picker("Primary Chart Color", "#00FFAA")

# Updated Dictionary for the Glossary
metric_defs = {
    "Total Revenue": "Total top-line money from sales.",
    "Net Income": "Bottom-line profit after all expenses.",
    "Free Cash Flow": "Cash available for expansion or dividends.",
    "Debt to Equity": "Total Debt / Shareholders Equity.",
    "FCF per Share": "Free Cash Flow for every share outstanding.",
    "Gross Margin %": "Profitability percentage after production costs."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    
    try:
        # 1. FETCH DATA
        if view_mode == "Annual":
            fin, cf, bs = stock.financials, stock.cashflow, stock.balance_sheet
        else:
            fin, cf, bs = stock.quarterly_financials, stock.quarterly_cashflow, stock.quarterly_balance_sheet

        # Merge all into one Master Table
        all_raw = pd.concat([fin, cf, bs], axis=0).T
        all_raw = all_raw.loc[:, ~all_raw.columns.duplicated()]
        
        # 2. BULLETPROOF DATA EXTRACTION
        def find_metric(possible_names):
            for name in possible_names:
                if name in all_raw.columns: return all_raw[name]
            return pd.Series(0.0, index=all_raw.index) # Return 0s if not found

        df = pd.DataFrame(index=all_raw.index)
        df["Total Revenue"] = find_metric(["Total Revenue", "Revenue", "TotalRevenue"])
        df["Net Income"] = find_metric(["Net Income", "NetIncome"])
        df["Free Cash Flow"] = find_metric(["Free Cash Flow", "FreeCashFlow"])
        
        # Manual Math for Ratios
        gross_profit = find_metric(["Gross Profit", "GrossProfit"])
        df["Gross Margin %"] = (gross_profit / df["Total Revenue"].replace(0, 1)) * 100
        
        total_debt = find_metric(["Total Debt", "TotalDebt"])
        equity = find_metric(["Stockholders Equity", "StockholdersEquity"])
        df["Debt to Equity"] = total_debt / equity.replace(0, 1)

        shares = stock.info.get('sharesOutstanding', 1)
        df["FCF per Share"] = df["Free Cash Flow"] / shares

        # 3. CHRONOLOGICAL FILTERING (Fix for "Backwards" & "Empty" charts)
        count = years_to_show if view_mode == "Annual" else (years_to_show * 4)
        df = df.iloc[:count] # Take most recent X periods
        df = df.sort_index(ascending=True) # Flip to Oldest -> Newest (Left to Right)
        
        if view_mode == "Annual":
            df.index = pd.to_datetime(df.index).year
        else:
            df.index = pd.to_datetime(df.index).strftime('%b %Y')

    except Exception as e:
        st.error(f"Data Fetching Issue: Yahoo Finance might be down or rate-limiting. Try again in 1 minute. Error: {e}")
        df = pd.DataFrame()

    # --- 4. THE CHART ---
    st.divider()
    selected = st.multiselect("Select Metrics:", options=list(metric_defs.keys()), default=["Total Revenue", "Net Income"])

    if not df.empty and selected:
        # Force categorical axis to fix "skinny bars"
        fig = px.bar(
            df, x=df.index, y=selected,
            barmode='group',
            color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA"]
        )
        
        fig.update_layout(
            bargap=0.15, bargroupgap=0.05,
            xaxis=dict(type='category', title="Time Period (Oldest → Newest)"),
            yaxis=dict(title="Value"),
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # 5. DYNAMIC GLOSSARY TABS
        tabs = st.tabs(selected)
        for i, m in enumerate(selected):
            with tabs[i]: st.info(f"**{m}**: {metric_defs.get(m)}")

    # 6. NEWS
    st.divider()
    st.subheader("Latest Headlines")
    for article in stock.news[:5]:
        title = article.get('title') or "Latest Market News"
        link = article.get('link') or "#"
        st.write(f"**[{title}]({link})**")