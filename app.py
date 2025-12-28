import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from difflib import get_close_matches
import numpy as np

# ============= CONFIGURATION =============
FMP_API_KEY = "9rZXN8pHaPyiCjFHWCVBxQmyzftJbRrj"
# NEW API BASE URL - FMP changed this!
BASE_URL = "https://financialmodelingprep.com/api/v4"

st.set_page_config(page_title="Finance Made Simple", layout="wide", page_icon="💰")

st.markdown("""
<style>
.main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
h1, h2, h3 { color: white !important; }
.stMetric { background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; }
.why-box { 
    background: rgba(255,255,255,0.1); 
    padding: 20px; 
    border-radius: 10px; 
    border-left: 5px solid #00D9FF;
    margin: 10px 0;
}
.personal-budget {
    background: rgba(255,215,0,0.2);
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #FFD700;
}
</style>
""", unsafe_allow_html=True)

# ============= SIMPLE EXPLANATIONS =============

SIMPLE_EXPLANATIONS = {
    "fcfAfterSBC": {
        "title": "Free Cash Flow After Stock Comp",
        "simple": "The REAL cash a company generates",
        "why": """
        **Think of it like YOUR paycheck:**
        
        Imagine you make $5,000/month (that's like Revenue).
        - You pay $3,000 in bills (that's Expenses)
        - You have $2,000 left (that's Free Cash Flow)
        
        BUT WAIT! You also promised to give your babysitter $500 in gift cards instead of cash.
        Those gift cards cost you money, but they're not "cash" expenses.
        
        **Your REAL take-home pay = $2,000 - $500 = $1,500**
        
        That's FCF After SBC - the most HONEST number!
        """,
        "personal_budget": """
        **Your Personal Budget:**
        - Income: $5,000
        - Bills: $3,000  
        - Left over: $2,000
        - Gift cards promised: $500
        - **Real take-home: $1,500** ← This is FCF After SBC
        """
    }
}

def format_number(num):
    """Format large numbers"""
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

def show_why_it_matters(metric_key):
    """Show explanation"""
    if metric_key in SIMPLE_EXPLANATIONS:
        exp = SIMPLE_EXPLANATIONS[metric_key]
        st.markdown(f"""
        <div class="why-box">
        <h4>💡 Why {exp['title']} Matters</h4>
        <p><strong>{exp['simple']}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📚 Learn More"):
            st.markdown(exp['why'])
            if 'personal_budget' in exp:
                st.markdown(f"""
                <div class="personal-budget">
                {exp['personal_budget']}
                </div>
                """, unsafe_allow_html=True)

# ============= FMP API FUNCTIONS (UPDATED FOR V4) =============

@st.cache_data(ttl=300)
def get_quote(ticker):
    """Get real-time quote - using v3 endpoint (still supported)"""
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=300)
def get_profile(ticker):
    """Get company profile"""
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=300)
def get_income_statement(ticker, period='annual', limit=10):
    """Get income statement"""
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def get_cash_flow(ticker, period='annual', limit=10):
    """Get cash flow statement"""
    url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                if 'freeCashFlow' in df.columns and 'stockBasedCompensation' in df.columns:
                    df['fcfAfterSBC'] = df['freeCashFlow'] - df['stockBasedCompensation']
                return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def get_financial_ratios(ticker, period='annual', limit=10):
    """Get financial ratios"""
    url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def get_historical_price(ticker, years=5):
    """Get historical prices"""
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'historical' in data:
                df = pd.DataFrame(data['historical'])
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                cutoff = datetime.now() - timedelta(days=years*365)
                df = df[df['date'] >= cutoff]
                return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_news(ticker):
    """Get news"""
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&limit=15&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=3600)
def get_all_tickers():
    """Get available tickers"""
    url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return {item['symbol']: item.get('name', item['symbol']) for item in data[:5000]}  # Limit to 5000
    except:
        pass
    return {}

def smart_search(search_term):
    """Simple ticker validation"""
    search_term = search_term.upper().strip()
    
    # Common ticker fixes
    COMMON_FIXES = {
        'APPLE': 'AAPL',
        'MICROSOFT': 'MSFT',
        'GOOGLE': 'GOOGL',
        'AMAZON': 'AMZN',
        'TESLA': 'TSLA',
        'META': 'META',
        'NVIDIA': 'NVDA',
        'APLE': 'AAPL',
        'MICROSFT': 'MSFT',
        'GOOGL': 'GOOGL',
        'TESLS': 'TSLA'
    }
    
    if search_term in COMMON_FIXES:
        return COMMON_FIXES[search_term]
    
    return search_term

# ============= MAIN APP =============

if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "NVDA"

col1, col2 = st.columns([3, 1])
with col1:
    st.title("💰 Finance Made Simple")
    st.caption("AI-Powered Stock Analysis for Everyone | No Finance Degree Required")
with col2:
    st.markdown("### 🤖 AI-Ready")
    st.caption("Powered by FMP API")

# Search
search = st.text_input(
    "🔍 Search by Company Name or Ticker:",
    st.session_state.selected_ticker,
    help="Try: AAPL, Apple, MSFT, Microsoft, NVDA"
)

if search:
    ticker = smart_search(search)
    st.session_state.selected_ticker = ticker
else:
    ticker = st.session_state.selected_ticker

# Get data
profile = get_profile(ticker)
quote = get_quote(ticker)

if profile:
    st.subheader(f"📈 {profile.get('companyName', ticker)} ({ticker})")
    
    description = profile.get('description', '')
    if description:
        with st.expander("ℹ️ What does this company do?"):
            st.write(description[:500] + "...")
    
    st.caption(f"**Sector:** {profile.get('sector', 'N/A')} | **Industry:** {profile.get('industry', 'N/A')}")
else:
    st.subheader(f"{ticker}")

view = st.radio("Choose View:", ["📊 Key Metrics", "📈 Financial Ratios", "📰 Latest News"], horizontal=True)

with st.sidebar:
    st.header("⚙️ Settings")
    period_type = st.radio("Time Period:", ["Annual", "Quarterly"])
    period = 'annual' if period_type == "Annual" else 'quarter'
    years = st.slider("Years:", 1, 10, 5)
    
    st.divider()
    st.markdown("### 📚 Quick Reference")
    st.info("""
    **FCF After SBC**: #1 metric
    **Gross Margin**: Pricing power
    **P/E Ratio**: Valuation
    **Debt/Equity**: Risk level
    """)

if quote:
    # Price chart
    price_data = get_historical_price(ticker, 5)
    if not price_data.empty:
        fig = px.area(price_data, x='date', y='close', title=f'{ticker} Stock Price - Last 5 Years')
        fig.update_layout(height=250, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
    
    # Metrics
    price = quote.get('price', 0)
    change = quote.get('changesPercentage', 0)
    mkt_cap = quote.get('marketCap', 0)
    pe = quote.get('pe', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Price", f"${price:.2f}", f"{change:+.2f}%")
    col2.metric("Market Cap", format_number(mkt_cap))
    col3.metric("P/E Ratio", f"{pe:.2f}" if pe > 0 else "N/A")
    col4.metric("52W High", f"${quote.get('yearHigh', 0):.2f}")
    
    st.divider()

# Views
income_df = get_income_statement(ticker, period, years*4 if period == 'quarter' else years)
cash_df = get_cash_flow(ticker, period, years*4 if period == 'quarter' else years)
ratios_df = get_financial_ratios(ticker, period, years*4 if period == 'quarter' else years)

if view == "📊 Key Metrics":
    if not cash_df.empty:
        st.markdown("## 💵 Free Cash Flow After Stock Compensation")
        show_why_it_matters('fcfAfterSBC')
        
        metrics = []
        if 'fcfAfterSBC' in cash_df.columns:
            metrics.append('fcfAfterSBC')
        if 'freeCashFlow' in cash_df.columns:
            metrics.append('freeCashFlow')
        
        if metrics:
            plot_df = cash_df[['date'] + metrics].copy()
            plot_df['date'] = plot_df['date'].dt.strftime('%Y')
            plot_df = plot_df.set_index('date')
            
            name_map = {'fcfAfterSBC': 'FCF After Stock Comp', 'freeCashFlow': 'Free Cash Flow'}
            plot_df.columns = [name_map.get(c, c) for c in plot_df.columns]
            
            fig = px.bar(plot_df, x=plot_df.index, y=plot_df.columns.tolist(), barmode='group',
                       color_discrete_sequence=['#9D4EDD', '#00D9FF'])
            
            max_val = plot_df.max().max()
            min_val = plot_df.min().min()
            y_min = min_val * 1.2 if min_val < 0 else 0
            y_max = max_val * 1.15
            
            fig.update_layout(height=400, yaxis=dict(range=[y_min, y_max]),
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
            
            if 'fcfAfterSBC' in cash_df.columns:
                latest = cash_df['fcfAfterSBC'].iloc[-1]
                col1, col2 = st.columns(2)
                col1.metric("Latest FCF After SBC", format_number(latest))
                
                if latest > 0:
                    col2.success("✅ Positive - Generating real cash!")
                else:
                    col2.error("🚨 Negative - Burning cash!")
    
    st.divider()
    
    if not income_df.empty and 'revenue' in income_df.columns:
        st.markdown("## 💰 Revenue Growth")
        
        plot_df = income_df[['date', 'revenue']].copy()
        plot_df['date'] = plot_df['date'].dt.strftime('%Y')
        plot_df = plot_df.set_index('date')
        
        fig = px.bar(plot_df, x=plot_df.index, y='revenue')
        fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        
        if len(income_df) >= 2:
            first = income_df['revenue'].iloc[0]
            last = income_df['revenue'].iloc[-1]
            years_span = len(income_df) - 1
            cagr = ((last / first) ** (1/years_span) - 1) * 100
            
            col1, col2 = st.columns(2)
            col1.metric("Revenue Growth (CAGR)", f"{cagr:+.1f}%/year")
            
            if cagr > 20:
                col2.success("🚀 Excellent growth!")
            elif cagr > 10:
                col2.info("✅ Solid growth")
            else:
                col2.warning("😴 Slow growth")

elif view == "📈 Financial Ratios":
    st.markdown("## 📊 Profitability Ratios")
    
    if not ratios_df.empty:
        ratios_to_plot = []
        ratio_map = {}
        
        if 'grossProfitRatio' in ratios_df.columns:
            ratios_to_plot.append('grossProfitRatio')
            ratio_map['grossProfitRatio'] = 'Gross Margin %'
        if 'operatingIncomeRatio' in ratios_df.columns:
            ratios_to_plot.append('operatingIncomeRatio')
            ratio_map['operatingIncomeRatio'] = 'Operating Margin %'
        if 'netProfitMargin' in ratios_df.columns:
            ratios_to_plot.append('netProfitMargin')
            ratio_map['netProfitMargin'] = 'Net Margin %'
        
        if ratios_to_plot:
            plot_df = ratios_df[['date'] + ratios_to_plot].copy()
            plot_df['date'] = plot_df['date'].dt.strftime('%Y')
            
            for col in ratios_to_plot:
                plot_df[col] = plot_df[col] * 100
            
            plot_df = plot_df.set_index('date')
            plot_df.columns = [ratio_map.get(c, c) for c in plot_df.columns]
            
            fig = px.line(plot_df, x=plot_df.index, y=plot_df.columns.tolist(), markers=True)
            fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                            paper_bgcolor='rgba(0,0,0,0)', font_color='white', yaxis_title="(%)")
            st.plotly_chart(fig, use_container_width=True)
            
            latest = plot_df.iloc[-1]
            st.markdown("### Latest Margins:")
            cols = st.columns(len(latest))
            for i, (name, value) in enumerate(latest.items()):
                cols[i].metric(name, f"{value:.1f}%")

elif view == "📰 Latest News":
    st.markdown(f"## 📰 Latest News for {ticker}")
    
    news = get_news(ticker)
    if news:
        for i, article in enumerate(news[:10]):
            with st.expander(f"{i+1}. {article.get('title', 'No title')[:80]}..."):
                st.write(f"**Source:** {article.get('site', 'Unknown')}")
                pub_date = article.get('publishedDate', '')
                if pub_date:
                    try:
                        date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                        st.write(f"**Date:** {date_obj.strftime('%B %d, %Y')}")
                    except:
                        pass
                
                summary = article.get('text', '')
                st.write(summary[:400] + "..." if len(summary) > 400 else summary)
                
                if article.get('url'):
                    st.markdown(f"[Read full article →]({article['url']})")
    else:
        st.info("No recent news available.")

st.markdown("---")
st.caption("💰 Finance Made Simple | Powered by FMP API")
