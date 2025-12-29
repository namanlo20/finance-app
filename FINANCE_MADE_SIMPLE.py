import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from difflib import get_close_matches

# ============= CONFIGURATION =============
FMP_API_KEY = "9rZXN8pHaPyiCjFHWCVBxQmyzftJbRrj"
BASE_URL = "https://financialmodelingprep.com/stable"

st.set_page_config(page_title="Finance Made Simple", layout="wide", page_icon="💰")

st.markdown("""
<style>
.main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
h1, h2, h3 { color: white !important; }
.stMetric { background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ============= METRIC DISPLAY NAMES =============
METRIC_NAMES = {
    # Cash Flow
    'freeCashFlow': 'Free Cash Flow',
    'operatingCashFlow': 'Operating Cash Flow',
    'investingCashFlow': 'Investing Cash Flow',
    'financingCashFlow': 'Financing Cash Flow',
    'capitalExpenditure': 'Capital Expenditures (CapEx)',
    'stockBasedCompensation': 'Stock-Based Compensation',
    'dividendsPaid': 'Dividends Paid',
    'commonStockRepurchased': 'Stock Buybacks',
    'debtRepayment': 'Debt Repayment',
    'changeInWorkingCapital': 'Change in Working Capital',
    'depreciationAndAmortization': 'Depreciation & Amortization',
    'fcfAfterSBC': 'FCF After Stock Comp',
    
    # Income Statement
    'revenue': 'Revenue',
    'costOfRevenue': 'Cost of Revenue (COGS)',
    'grossProfit': 'Gross Profit',
    'researchAndDevelopmentExpenses': 'R&D Expenses',
    'sellingGeneralAndAdministrativeExpenses': 'SG&A Expenses',
    'operatingExpenses': 'Operating Expenses',
    'operatingIncome': 'Operating Income',
    'netIncome': 'Net Income',
    'ebitda': 'EBITDA',
    'interestExpense': 'Interest Expense',
    'incomeTaxExpense': 'Income Tax Expense',
    
    # Balance Sheet
    'totalAssets': 'Total Assets',
    'cashAndCashEquivalents': 'Cash & Cash Equivalents',
    'totalCurrentAssets': 'Current Assets',
    'totalLiabilities': 'Total Liabilities',
    'totalDebt': 'Total Debt',
    'longTermDebt': 'Long-Term Debt',
    'shortTermDebt': 'Short-Term Debt',
    'totalStockholdersEquity': 'Shareholders Equity',
    'retainedEarnings': 'Retained Earnings',
    'inventory': 'Inventory',
    'netReceivables': 'Accounts Receivable'
}

def format_number(num):
    if pd.isna(num) or num == 0:
        return "N/A"
    if abs(num) >= 1e12:
        return f"${num/1e12:,.2f}T"
    elif abs(num) >= 1e9:
        return f"${num/1e9:,.1f}B"
    elif abs(num) >= 1e6:
        return f"${num/1e6:,.1f}M"
    else:
        return f"${num:,.0f}"

def get_available_metrics(df):
    """Get all numeric columns for dropdown"""
    if df.empty:
        return []
    exclude = ['date', 'symbol', 'reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period']
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    available = [col for col in numeric_cols if col not in exclude]
    return [(METRIC_NAMES.get(col, col.title()), col) for col in available]

# ============= API FUNCTIONS =============
@st.cache_data(ttl=300)
def get_quote(ticker):
    url = f"{BASE_URL}/quote?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except:
        return None

@st.cache_data(ttl=1800)
def get_profile(ticker):
    url = f"{BASE_URL}/profile?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except:
        return None

@st.cache_data(ttl=3600)
def get_income_statement(ticker, period='annual', limit=5):
    url = f"{BASE_URL}/income-statement?symbol={ticker}&period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_balance_sheet(ticker, period='annual', limit=5):
    url = f"{BASE_URL}/balance-sheet-statement?symbol={ticker}&period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_cash_flow(ticker, period='annual', limit=5):
    url = f"{BASE_URL}/cash-flow-statement?symbol={ticker}&period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_historical_price(ticker, years=5):
    url = f"{BASE_URL}/historical-price-eod/light?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if data and isinstance(data, list):
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            cutoff = datetime.now() - timedelta(days=years*365)
            df = df[df['date'] >= cutoff]
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_key_metrics(ticker):
    url = f"{BASE_URL}/key-metrics?symbol={ticker}&period=annual&limit=1&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data and len(data) > 0:
            return data[0]
    except:
        pass
    return None

# ============= STATE =============
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "AAPL"

# ============= HEADER =============
st.title("💰 Finance Made Simple")
st.caption("Premium FMP Data - AI-Powered Analysis")

# ============= MAIN APP =============
ticker_input = st.text_input("🔍 Enter Stock Ticker:", st.session_state.selected_ticker)

if ticker_input:
    ticker = ticker_input.upper()
    st.session_state.selected_ticker = ticker
    
    # Fetch data
    quote = get_quote(ticker)
    profile = get_profile(ticker)
    
    if quote and profile:
        company_name = profile.get('companyName', ticker)
        
        st.subheader(f"📈 {company_name} ({ticker})")
        
        # Company description
        description = profile.get('description', '')
        if description:
            with st.expander("ℹ️ What does this company do?"):
                st.write(description[:500] + "..." if len(description) > 500 else description)
        
        # Main metrics
        price = quote.get('price', 0)
        change_pct = quote.get('changesPercentage', 0)
        market_cap = quote.get('marketCap', 0)
        pe = quote.get('pe', 0)
        
        # Get P/S from key metrics
        key_metrics = get_key_metrics(ticker)
        ps = 0
        if key_metrics:
            ps = key_metrics.get('priceToSalesRatioTTM', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"${price:.2f}", f"{change_pct:+.2f}%")
        col2.metric("Market Cap", format_number(market_cap))
        col3.metric("P/E Ratio", f"{pe:.2f}" if pe and pe > 0 else "N/A",
                   help="Price-to-Earnings. Lower = cheaper. Good: 15-25")
        col4.metric("P/S Ratio", f"{ps:.2f}" if ps and ps > 0 else "N/A",
                   help="Price-to-Sales. Tech: 5-10 | Retail: 0.5-2")
        
        st.divider()
        
        # Stock Price Chart
        st.markdown(f"### 📈 {company_name} - Stock Price (5 Years)")
        price_data = get_historical_price(ticker, 5)
        
        if not price_data.empty and 'price' in price_data.columns:
            fig = px.area(price_data, x='date', y='price')
            fig.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis_title="",
                yaxis_title="Price ($)",
                showlegend=False,
                yaxis=dict(rangemode='tozero'),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            fig.update_traces(fillcolor='rgba(157, 78, 221, 0.3)', line_color='#9D4EDD', line_width=2)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Stock price data not available")
        
        st.divider()
        
        # CASH FLOW WITH DROPDOWN
        st.markdown(f"### 💵 {company_name} - Cash Flow Statement")
        cash_df = get_cash_flow(ticker, 'annual', 5)
        
        if not cash_df.empty:
            # Add computed metric
            if 'stockBasedCompensation' in cash_df.columns and 'freeCashFlow' in cash_df.columns:
                cash_df['fcfAfterSBC'] = cash_df['freeCashFlow'] - abs(cash_df['stockBasedCompensation'])
            
            available = get_available_metrics(cash_df)
            
            if available:
                st.markdown("**📊 Select 3 metrics to display:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    m1_display = st.selectbox("Metric 1:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'FCF After Stock Comp'), 0),
                        key="cf1")
                    m1 = next(c for d, c in available if d == m1_display)
                
                with col2:
                    m2_display = st.selectbox("Metric 2:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'Free Cash Flow'), min(1, len(available)-1)),
                        key="cf2")
                    m2 = next(c for d, c in available if d == m2_display)
                
                with col3:
                    m3_display = st.selectbox("Metric 3:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'Operating Cash Flow'), min(2, len(available)-1)),
                        key="cf3")
                    m3 = next(c for d, c in available if d == m3_display)
                
                plot_df = cash_df[['date', m1, m2, m3]].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y')
                
                fig = go.Figure()
                colors = ['#9D4EDD', '#00D9FF', '#FF69B4']
                
                for i, (col, name) in enumerate([(m1, m1_display), (m2, m2_display), (m3, m3_display)]):
                    fig.add_trace(go.Bar(x=plot_df['date'], y=plot_df[col], name=name, marker_color=colors[i]))
                
                fig.update_layout(
                    title=f"{company_name} - Cash Flow",
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    yaxis=dict(rangemode='tozero'),
                    margin=dict(l=20, r=20, t=60, b=20),
                    legend=dict(orientation="h", y=1.02)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                cols = st.columns(3)
                for i, (col, name) in enumerate([(m1, m1_display), (m2, m2_display), (m3, m3_display)]):
                    cols[i].metric(f"Latest {name}", format_number(cash_df[col].iloc[-1]))
        else:
            st.warning("⚠️ Cash flow data not available")
        
        st.divider()

# INCOME STATEMENT WITH DROPDOWN
        st.markdown(f"### 💰 {company_name} - Income Statement")
        income_df = get_income_statement(ticker, 'annual', 5)
        
        if not income_df.empty:
            available = get_available_metrics(income_df)
            
            if available:
                st.markdown("**📊 Select 3 metrics to display:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    m1_display = st.selectbox("Metric 1:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'Revenue'), 0),
                        key="inc1")
                    m1 = next(c for d, c in available if d == m1_display)
                
                with col2:
                    m2_display = st.selectbox("Metric 2:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'Operating Income'), min(1, len(available)-1)),
                        key="inc2")
                    m2 = next(c for d, c in available if d == m2_display)
                
                with col3:
                    m3_display = st.selectbox("Metric 3:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'Net Income'), min(2, len(available)-1)),
                        key="inc3")
                    m3 = next(c for d, c in available if d == m3_display)
                
                plot_df = income_df[['date', m1, m2, m3]].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y')
                
                fig = go.Figure()
                colors = ['#00D9FF', '#FFD700', '#9D4EDD']
                
                for i, (col, name) in enumerate([(m1, m1_display), (m2, m2_display), (m3, m3_display)]):
                    fig.add_trace(go.Bar(x=plot_df['date'], y=plot_df[col], name=name, marker_color=colors[i]))
                
                fig.update_layout(
                    title=f"{company_name} - Income Statement",
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    yaxis=dict(rangemode='tozero'),
                    margin=dict(l=20, r=20, t=60, b=20),
                    legend=dict(orientation="h", y=1.02)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                cols = st.columns(3)
                for i, (col, name) in enumerate([(m1, m1_display), (m2, m2_display), (m3, m3_display)]):
                    cols[i].metric(f"Latest {name}", format_number(income_df[col].iloc[-1]))
        else:
            st.warning("⚠️ Income statement data not available")
        
        st.divider()
        
        # BALANCE SHEET WITH DROPDOWN
        st.markdown(f"### 🏦 {company_name} - Balance Sheet")
        balance_df = get_balance_sheet(ticker, 'annual', 5)
        
        if not balance_df.empty:
            available = get_available_metrics(balance_df)
            
            if available:
                st.markdown("**📊 Select 3 metrics to display:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    m1_display = st.selectbox("Metric 1:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'Total Assets'), 0),
                        key="bal1")
                    m1 = next(c for d, c in available if d == m1_display)
                
                with col2:
                    m2_display = st.selectbox("Metric 2:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'Total Liabilities'), min(1, len(available)-1)),
                        key="bal2")
                    m2 = next(c for d, c in available if d == m2_display)
                
                with col3:
                    m3_display = st.selectbox("Metric 3:", [d for d, _ in available],
                        index=next((i for i, (d, _) in enumerate(available) if d == 'Shareholders Equity'), min(2, len(available)-1)),
                        key="bal3")
                    m3 = next(c for d, c in available if d == m3_display)
                
                plot_df = balance_df[['date', m1, m2, m3]].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y')
                
                fig = go.Figure()
                colors = ['#00D9FF', '#FF6B6B', '#FFD700']
                
                for i, (col, name) in enumerate([(m1, m1_display), (m2, m2_display), (m3, m3_display)]):
                    fig.add_trace(go.Bar(x=plot_df['date'], y=plot_df[col], name=name, marker_color=colors[i]))
                
                fig.update_layout(
                    title=f"{company_name} - Balance Sheet",
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    yaxis=dict(rangemode='tozero'),
                    margin=dict(l=20, r=20, t=60, b=20),
                    legend=dict(orientation="h", y=1.02)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                cols = st.columns(3)
                for i, (col, name) in enumerate([(m1, m1_display), (m2, m2_display), (m3, m3_display)]):
                    cols[i].metric(f"Latest {name}", format_number(balance_df[col].iloc[-1]))
        else:
            st.warning("⚠️ Balance sheet data not available")
        
    elif quote:
        st.warning(f"Found quote data for {ticker} but no company profile")
    else:
        st.error(f"❌ No data found for ticker: {ticker}")
        st.info("💡 Try a different ticker like: AAPL, MSFT, GOOGL, TSLA, AMZN")

st.divider()
st.caption("💰 Finance Made Simple | FMP Premium | Real-time Data")
st.caption("⚠️ For educational purposes only. Not financial advice.")
