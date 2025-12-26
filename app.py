import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: Ultimate Pro Terminal")

# --- SIDEBAR: DYNAMIC CONTROLS ---
with st.sidebar:
    st.header("⚙️ Data Settings")
    view_mode = st.radio("Frequency:", ["Annual", "Quarterly"])
    
    # 5 is default, but user can pick ANY year from 1 to 15
    years_to_show = st.slider("Years of History:", min_value=1, max_value=15, value=5)
    
    st.divider()
    user_color = st.color_picker("Primary Chart Color", "#00FFAA")
    st.info("Charts now read Left-to-Right (Oldest to Newest).")

metric_defs = {
    "Total Revenue": "Total top-line money from sales.",
    "Net Income": "Bottom-line profit after all expenses.",
    "Free Cash Flow": "Cash available for expansion or dividends.",
    "Debt to Equity": "Total Debt / Shareholders Equity (Risk measure).",
    "FCF per Share": "Free Cash Flow for every share outstanding.",
    "Gross Margin %": "Profitability percentage after production costs."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    
    try:
        # 1. FETCH MAX HISTORY
        if view_mode == "Annual":
            fin, cf, bs = stock.get_financials(freq='yearly'), stock.get_cashflow(freq='yearly'), stock.get_balance_sheet(freq='yearly')
        else:
            fin, cf, bs = stock.get_financials(freq='quarterly'), stock.get_cashflow(freq='quarterly'), stock.get_balance_sheet(freq='quarterly')

        # Merge and remove duplicates
        all_raw = pd.concat([fin, cf, bs], axis=0).T
        all_raw = all_raw.loc[:, ~all_raw.columns.duplicated()]
        
        # 2. CALCULATE METRICS
        shares = stock.info.get('sharesOutstanding', 1)
        df = pd.DataFrame(index=all_raw.index)
        
        def safe_get(names):
            for n in names:
                if n in all_raw.columns: return all_raw[n]
            return pd.Series(0, index=all_raw.index)

        df["Total Revenue"] = safe_get(["Total Revenue", "Revenue"])
        df["Net Income"] = safe_get(["Net Income"])
        df["Free Cash Flow"] = safe_get(["Free Cash Flow"])
        df["Gross Margin %"] = (safe_get(["Gross Profit"]) / df["Total Revenue"]) * 100
        df["Debt to Equity"] = safe_get(["Total Debt"]) / safe_get(["Stockholders Equity"])
        df["FCF per Share"] = df["Free Cash Flow"] / shares

        # 3. CHRONOLOGICAL FILTERING
        # Slice based on slider
        count = years_to_show if view_mode == "Annual" else (years_to_show * 4)
        df = df.head(count)
        
        # SORT: Oldest -> Newest (Fixes the 'backwards' issue)
        df = df.sort_index(ascending=True) 
        
        # Format the dates for the chart labels
        if view_mode == "Annual":
            df.index = pd.to_datetime(df.index).year
        else:
            df.index = pd.to_datetime(df.index).strftime('%b %Y')

    except Exception as e:
        st.error(f"Waiting for data... ({e})")
        df = pd.DataFrame()

    # --- 4. THE CHART ---
    st.divider()
    selected = st.multiselect("Select Metrics:", options=list(metric_defs.keys()), default=["Total Revenue", "Net Income"])

    if not df.empty and selected:
        # Category axis forces thick bars even with 15 years of data
        fig = px.bar(
            df, x=df.index, y=selected,
            barmode='group',
            color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA"]
        )
        
        fig.update_layout(
            bargap=0.15, 
            bargroupgap=0.05,
            xaxis=dict(type='category', title="Time Period (Oldest to Newest)"),
            yaxis=dict(title="Financial Value"),
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