import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: Pro Beginner Terminal")

ticker_symbol = st.text_input("Enter Ticker:", "AAPL").upper()

# --- DEFINITION DICTIONARY ---
metric_explanations = {
    "Total Revenue": "Total money a company brings in from sales before any expenses.",
    "Cost Of Revenue": "The direct costs of producing the goods or services sold (COGS).",
    "Gross Profit": "Revenue minus COGS. It shows how much profit is made on the products themselves.",
    "Operating Expense": "Costs to run the business (Rent, Salaries, Marketing).",
    "Operating Income": "Profit after taking out operating expenses. Shows core business health.",
    "Net Income": "The 'Bottom Line'. Total profit after ALL expenses and taxes are paid.",
    "Basic EPS": "Earnings Per Share. The portion of profit allocated to each share of stock.",
    "Operating Cash Flow": "Actual cash generated from business activities (often more reliable than Net Income).",
    "Free Cash Flow": "Cash left over after the company pays for its operations and equipment."
}

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    # 1. FIXED DIVIDEND YIELD
    div_rate = info.get('dividendRate', 0)
    curr_price = info.get('currentPrice', 1)
    real_yield = (div_rate / curr_price) * 100 if div_rate else 0
    
    # 2. SNAPSHOT METRICS
    cols = st.columns(4)
    cols[0].metric("Price", f"${info.get('currentPrice', 'N/A')}")
    cols[1].metric("Market Cap", f"{info.get('marketCap', 0):,}")
    cols[2].metric("Div. Yield", f"{real_yield:.2f}%") # Manual fix applied
    cols[3].metric("Risk Score", info.get('overallRisk', 'N/A'))

    # 3. ORDERED FINANCIALS EXPLORER
    st.divider()
    st.subheader("📊 Advanced Financials Explorer")
    
    # Selection in your specific order
    ordered_metrics = list(metric_explanations.keys())
    selected = st.multiselect("Pick Metrics to Compare:", options=ordered_metrics, default=["Total Revenue", "Net Income"])
    
    chart_style = st.radio("Chart Style:", ["Line", "Bar"], horizontal=True)

    financials = stock.financials.T
    if not financials.empty and selected:
        # Filter data based on selection
        plot_data = financials[selected]
        
        # 4. CHART SPACING FIX
        if chart_style == "Line":
            st.line_chart(plot_data, width="stretch")
        else:
            st.bar_chart(plot_data, width="stretch") # Stretches to prevent ugly gaps

        # 5. DYNAMIC EXPLANATION TABS
        st.write("### 📖 Understand the Data")
        tabs = st.tabs(selected) # Creates a tab for every selected metric
        for i, metric in enumerate(selected):
            with tabs[i]:
                st.info(f"**{metric}**: {metric_explanations.get(metric, 'Definition coming soon!')}")