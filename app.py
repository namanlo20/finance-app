import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: Ultimate Pro Terminal")

with st.sidebar:
    st.header("🎨 Dashboard Styles")
    user_color = st.color_picker("Primary Bar Color", "#00FFAA")
    st.divider()
    st.info("Top Metrics are prioritized. Statements & Ratios follow below.")

# 1. ORGANIZED METRICS & GLOSSARY
# Your preferred metrics are at the top
metric_defs = {
    "Total Revenue": "Total money from sales (Top Line).",
    "Net Income": "Final profit after all taxes and costs.",
    "Free Cash Flow": "Cash available for expansion or dividends.",
    "Operating Cash Flow": "Cash flowing from core business operations.",
    "Gross Profit": "Money left after manufacturing costs.",
    # Ratios & Calculations
    "Gross Margin %": "Profitability percentage after production costs.",
    "Net Profit Margin %": "The percentage of revenue that is actual profit.",
    "Debt to Equity": "Total Debt divided by Shareholders Equity (Risk measure).",
    "FCF per Share": "Free Cash Flow available for every single share outstanding.",
    "Current Ratio": "Ability to pay short-term debts with short-term assets.",
    # Full Statement Categories
    "Operating Expense": "Costs to run the business (Marketing, Rent, Salaries).",
    "EBIT": "Earnings Before Interest and Taxes.",
    "Total Assets": "Everything the company owns.",
    "Total Liabilities": "Everything the company owes.",
    "Total Debt": "Combined short and long-term borrowed money.",
    "Cash & Equivalents": "Liquid money available in the bank.",
    "Stockholders Equity": "The net value of the company owned by shareholders."
}

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    # --- 2. MARKET SNAPSHOT ---
    st.subheader("Market Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    price = info.get('currentPrice', 1)
    shares = info.get('sharesOutstanding', 1)
    div = info.get('dividendRate', 0)
    y_val = (div / price) * 100 if div else 0
    
    c1.metric("Current Price", f"${price}")
    c2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    c3.metric("Div. Yield", f"{y_val:.2f}%")
    c4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # --- 3. THE "STATEMENT RECONSTRUCTION" ENGINE ---
    try:
        # Fetch all raw statements
        fin = stock.financials.T
        cf = stock.cashflow.T
        bs = stock.balance_sheet.T
        all_raw = pd.concat([fin, cf, bs], axis=1)
        all_raw = all_raw.loc[:, ~all_raw.columns.duplicated()]

        # Helper to find columns safely
        def find(names):
            for n in names:
                if n in all_raw.columns: return all_raw[n]
            return pd.Series(0, index=all_raw.index)

        # Map Raw Data to our Clean Table
        df = pd.DataFrame(index=all_raw.index)
        df["Total Revenue"] = find(["Total Revenue", "Revenue"])
        df["Net Income"] = find(["Net Income"])
        df["Free Cash Flow"] = find(["Free Cash Flow"])
        df["Operating Cash Flow"] = find(["Operating Cash Flow", "Total Cash From Operating Activities"])
        df["Gross Profit"] = find(["Gross Profit"])
        df["Operating Expense"] = find(["Operating Expenses"])
        df["EBIT"] = find(["EBIT"])
        df["Total Assets"] = find(["Total Assets"])
        df["Total Liabilities"] = find(["Total Liabilities Net Minority Interest", "Total Liabilities"])
        df["Total Debt"] = find(["Total Debt"])
        df["Stockholders Equity"] = find(["Stockholders Equity"])
        df["Cash & Equivalents"] = find(["Cash And Cash Equivalents", "Cash"])

        # --- 4. MANUAL RATIO CALCULATIONS ---
        df["Gross Margin %"] = (df["Gross Profit"] / df["Total Revenue"]) * 100
        df["Net Profit Margin %"] = (df["Net Income"] / df["Total Revenue"]) * 100
        df["Debt to Equity"] = df["Total Debt"] / df["Stockholders Equity"]
        df["FCF per Share"] = df["Free Cash Flow"] / shares
        df["Current Ratio"] = find(["Current Assets"]) / find(["Current Liabilities"])
        
        df.index = pd.to_datetime(df.index).year
    except:
        df = pd.DataFrame()

    # --- 5. THE CHART & GLOSSARY ---
    st.divider()
    st.subheader("📊 Advanced Financials Explorer")
    selected = st.multiselect("Select Metrics to Compare:", options=list(metric_defs.keys()), default=["Total Revenue", "Net Income", "Free Cash Flow"])

    if not df.empty and selected:
        valid_selected = [m for m in selected if m in df.columns]
        plot_data = df[valid_selected]
        
        # Plotly Grouped Bar Chart
        fig = px.bar(
            plot_data, x=plot_data.index, y=plot_data.columns,
            barmode='group',
            color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA", "#00CC96"]
        )
        
        fig.update_layout(
            bargap=0.15, bargroupgap=0.05,
            xaxis=dict(type='category', title="Year"),
            yaxis=dict(title="Value ($ or Ratio)"),
            margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Auto-Glossary Tabs
        st.write("#### 📖 Metric Dictionary")
        tabs = st.tabs(valid_selected)
        for i, m in enumerate(valid_selected):
            with tabs[i]: st.info(f"**{m}**: {metric_defs.get(m)}")

    # --- 6. ABOUT & NEWS ---
    st.divider()
    with st.expander("📝 About the Company"):
        st.write(info.get('longBusinessSummary', "N/A"))

    st.subheader("Latest News Headlines")
    for article in stock.news[:5]:
        title = article.get('title') or article.get('content', {}).get('title', "Latest Update")
        link = article.get('link') or article.get('content', {}).get('canonicalUrl', {}).get('url', "#")
        st.write(f"**[{title}]({link})**")
        st.divider()