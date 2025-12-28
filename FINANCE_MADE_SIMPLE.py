import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
from difflib import get_close_matches
import numpy as np

# ============= CONFIGURATION =============
FMP_API_KEY = "9rZXN8pHaPyiCjFHWCVBxQmyzftJbRrj"
BASE_URL = "https://financialmodelingprep.com/stable"

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
        - But wait! You also give your roommate $500 in IOUs instead of cash (that's Stock-Based Compensation)
        - **Your REAL cash left = $5,000 - $3,000 - $500 = $1,500**
        
        That's FCF After SBC! If this number is negative → company is burning cash 🔥
        """,
        "personal_budget": "If your monthly income is $5K but after bills AND IOUs you only have $200 left, that's your FCF After SBC."
    },
    "revenue": {
        "title": "Revenue",
        "simple": "Total money coming in the door",
        "why": "Like your total paycheck BEFORE any deductions. Growing revenue = company is selling more stuff ✅",
        "personal_budget": "Your gross salary before taxes and deductions."
    },
    "operatingIncome": {
        "title": "Operating Income",
        "simple": "Profit from core business operations",
        "why": "This shows if the company's MAIN business is profitable. Excludes interest, taxes, one-time events.",
        "personal_budget": "Your paycheck after regular bills, before credit card interest or tax refunds."
    },
    "netIncome": {
        "title": "Net Income",
        "simple": "Bottom line profit",
        "why": "The final profit after EVERYTHING. But beware: can be manipulated with accounting tricks!",
        "personal_budget": "What's left after ALL expenses, taxes, everything."
    }
}

RATIO_EXPLANATIONS = {
    "Gross Margin": {
        "what": "How much profit per dollar of sales",
        "good": "High margins = pricing power",
        "targets": "Tech: 60-80% | Retail: 20-40%"
    },
    "Operating Margin": {
        "what": "Profit from core business / Revenue",
        "good": "Higher = more efficient",
        "targets": "Good: >15% | Excellent: >25%"
    },
    "Net Margin": {
        "what": "Final profit / Revenue",
        "good": "Higher = more money to bottom line",
        "targets": "Good: >10% | Excellent: >20%"
    },
    "ROE": {
        "what": "Return on Equity",
        "good": "Better use of investor capital",
        "targets": "Good: >15% | Excellent: >20%"
    },
    "ROA": {
        "what": "Return on Assets",
        "good": "Better asset utilization",
        "targets": "Good: >5% | Excellent: >10%"
    }
}

DCF_EXPLANATION = """
### 💰 Discounted Cash Flow (DCF) Valuation
**What is this?** A way to estimate what a stock is REALLY worth based on future cash flows.
**How it works:** 1) Estimate future cash flows 2) "Discount" them 3) Add them up = fair value
**⚠️ Warning:** DCF is sensitive to assumptions (garbage in = garbage out)
"""

GLOSSARY = {
    "FCF After SBC": "Free Cash Flow after Stock Comp - The REAL cash generated",
    "Revenue": "Total money from selling products/services",
    "Operating Income": "Profit from core business operations",
    "Net Income": "Bottom line profit after ALL expenses",
    "P/E Ratio": "Price divided by Earnings - valuation metric",
    "P/S Ratio": "Price divided by Sales. Lower = cheaper. Shows how much you pay for each $1 of revenue. Tech: 5-10 | Retail: 0.5-2",
    "Market Cap": "Total value of all shares",
    "Beta": "Stock volatility vs market (>1 = more volatile)",
    "Sharpe Ratio": "Risk-adjusted return (higher = better)",
    "Max Drawdown": "Biggest drop from peak (lower = better)",
    "CAGR": "Compound Annual Growth Rate - Average yearly growth rate over time. 20% CAGR = doubling every 3.6 years",
    "FCF per Share": "Free Cash Flow divided by shares outstanding. Shows cash generation per share you own"
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

def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate"""
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return None
    try:
        cagr = (((end_value / start_value) ** (1 / years)) - 1) * 100
        return cagr
    except:
        return None

def calculate_growth_rate(df, column, years=None):
    """Calculate growth rate for a metric over time"""
    if df.empty or column not in df.columns:
        return None
    
    valid_data = df[df[column] > 0].copy()
    if len(valid_data) < 2:
        return None
    
    valid_data = valid_data.sort_values('date')
    start_val = valid_data[column].iloc[0]
    end_val = valid_data[column].iloc[-1]
    
    if years is None:
        years = len(valid_data)
    
    return calculate_cagr(start_val, end_val, years)

def show_why_it_matters(metric_key):
    """Show explanation for a metric"""
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
                <strong>🏠 Like Your Personal Budget:</strong><br>
                {exp['personal_budget']}
                </div>
                """, unsafe_allow_html=True)

# ============= FMP API FUNCTIONS =============

@st.cache_data(ttl=3600)
def get_all_stocks():
    """Get list of stocks with fallback"""
    try:
        url = f"{BASE_URL}/search-name?query=&limit=5000&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=15)
        data = response.json()
        stocks = {}
        for stock in data:
            if stock.get('symbol') and stock.get('name'):
                symbol = stock['symbol'].upper()
                name = stock['name'].upper()
                stocks[symbol] = stock['name']
                stocks[name] = symbol
        return stocks
    except:
        return {
            "AAPL": "Apple Inc.", "APPLE": "AAPL", "MSFT": "Microsoft", "MICROSOFT": "MSFT",
            "GOOGL": "Alphabet", "GOOGLE": "GOOGL", "AMZN": "Amazon", "AMAZON": "AMZN",
            "NVDA": "NVIDIA", "NVIDIA": "NVDA", "META": "Meta", "FACEBOOK": "META",
            "TSLA": "Tesla", "TESLA": "TSLA", "JPM": "JPMorgan", "JPMORGAN": "JPM",
            "V": "Visa", "VISA": "V", "WMT": "Walmart", "WALMART": "WMT"
        }

def smart_search_ticker(search_term):
    """Smart search with company name support"""
    search_term = search_term.upper().strip()
    all_stocks = get_all_stocks()
    
    if search_term in all_stocks and len(search_term) <= 5:
        return search_term, all_stocks[search_term]
    
    if search_term in all_stocks:
        return all_stocks[search_term], search_term
    
    tickers = [k for k in all_stocks.keys() if len(k) <= 5]
    close_tickers = get_close_matches(search_term, tickers, n=1, cutoff=0.6)
    if close_tickers:
        return close_tickers[0], all_stocks[close_tickers[0]]
    
    names = [k for k in all_stocks.keys() if len(k) > 5]
    close_names = get_close_matches(search_term, names, n=1, cutoff=0.4)
    if close_names:
        return all_stocks[close_names[0]], close_names[0]
    
    for key, value in all_stocks.items():
        if len(key) > 5 and search_term in key:
            return value, key
    
    return search_term, search_term

@st.cache_data(ttl=3600)
def get_ratios_ttm(ticker):
    """Get TTM ratios including P/E, P/S - MOST RELIABLE"""
    url = f"{BASE_URL}/ratios-ttm/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data and len(data) > 0:
            return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=300)
def get_quote(ticker):
    """Get quote"""
    url = f"{BASE_URL}/quote?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except:
        return None

@st.cache_data(ttl=1800)
def get_profile(ticker):
    """Get company profile"""
    url = f"{BASE_URL}/profile?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except:
        return None

@st.cache_data(ttl=3600)
def get_income_statement(ticker, period='annual', limit=5):
    """Get income statement"""
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
    """Get balance sheet"""
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
    """Get cash flow"""
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
def get_financial_ratios(ticker, period='annual', limit=5):
    """Get financial ratios"""
    url = f"{BASE_URL}/ratios?symbol={ticker}&period={period}&limit={limit}&apikey={FMP_API_KEY}"
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
    """Get historical prices using correct endpoint"""
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
    except Exception as e:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_stock_news(ticker, limit=20):
    """Get stock news"""
    url = f"{BASE_URL}/stock-news?symbol={ticker}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.json() if response.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=3600)
def get_price_target(ticker):
    """Get price target"""
    url = f"{BASE_URL}/price-target-consensus?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except:
        return None

# ============= SECTOR DEFINITIONS =============
SECTORS = {
    "🏦 Financial Services": {
        "desc": "Banks, insurance, investment firms",
        "tickers": ["JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SCHW", "AXP", "USB"]
    },
    "💻 Technology": {
        "desc": "Software, hardware, semiconductors",
        "tickers": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "INTC"]
    },
    "🛒 Consumer": {
        "desc": "Retail, e-commerce, consumer goods",
        "tickers": ["AMZN", "TSLA", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "COST"]
    },
    "🏥 Healthcare": {
        "desc": "Pharma, biotech, medical devices",
        "tickers": ["UNH", "JNJ", "LLY", "ABBV", "MRK", "TMO", "ABT", "DHR", "PFE", "BMY"]
    },
    "🏭 Industrials": {
        "desc": "Manufacturing, aerospace, defense",
        "tickers": ["BA", "CAT", "HON", "UPS", "RTX", "LMT", "GE", "MMM", "DE", "EMR"]
    },
    "⚡ Energy": {
        "desc": "Oil, gas, renewable energy",
        "tickers": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL"]
    }
}

# ============= STATE =============
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "AAPL"

# ============= HEADER =============
col1, col2 = st.columns([4, 1])
with col1:
    st.title("💰 Finance Made Simple")
    st.caption("AI-Powered Stock Analysis for Everyone")
with col2:
    st.markdown("### 🤖 AI-Ready")
    st.caption("FMP Premium")

# ============= TABS =============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Company Analysis",
    "🎯 Sector Explorer",
    "📈 Portfolio Risk Analyzer",
    "✅ Investment Checklist",
    "📚 Finance 101"
])

# ============= TAB 2: SECTOR EXPLORER =============
with tab2:
    st.header("🎯 Sector Explorer")
    
    selected_sector = st.selectbox("Choose sector:", list(SECTORS.keys()))
    sector_info = SECTORS[selected_sector]
    st.info(f"**{selected_sector}** - {sector_info['desc']}")
    
    with st.spinner("Loading sector data..."):
        rows = []
        for ticker in sector_info['tickers']:
            quote = get_quote(ticker)
            ratios_ttm = get_ratios_ttm(ticker)
            
            if quote:
                pe = 0
                ps = 0
                
                if ratios_ttm:
                    pe = ratios_ttm.get('peRatioTTM', 0)
                    ps = ratios_ttm.get('priceToSalesRatioTTM', 0)
                
                if not pe or pe == 0:
                    pe = quote.get('pe', 0)
                
                rows.append({
                    "Ticker": ticker,
                    "Company": quote.get('name', ticker),
                    "Price": quote.get('price', 0),
                    "Change %": quote.get('changesPercentage', 0),
                    "Market Cap": quote.get('marketCap', 0),
                    "P/E": pe,
                    "P/S": ps
                })
        
        if rows:
            df = pd.DataFrame(rows)
            df = df.sort_values('Market Cap', ascending=False)
            
            col1, col2 = st.columns(2)
            
            valid_pes = df[df['P/E'] > 0]['P/E']
            if len(valid_pes) > 0:
                avg_pe = valid_pes.mean()
                col1.metric("📊 Sector Avg P/E", f"{avg_pe:.2f}", 
                         help="Compare individual P/Es to this average")
            
            valid_ps = df[df['P/S'] > 0]['P/S']
            if len(valid_ps) > 0:
                avg_ps = valid_ps.mean()
                col2.metric("📊 Sector Avg P/S", f"{avg_ps:.2f}",
                         help="Average Price-to-Sales for the sector")
            
            display_df = df.copy()
            display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
            display_df['Change %'] = display_df['Change %'].apply(lambda x: f"{x:+.2f}%")
            display_df['Market Cap'] = display_df['Market Cap'].apply(format_number)
            display_df['P/E'] = display_df['P/E'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
            display_df['P/S'] = display_df['P/S'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            st.markdown("### 🔍 Analyze a Company")
            col1, col2 = st.columns([3, 1])
            with col1:
                selected = st.selectbox("Choose:", df['Ticker'].tolist(), 
                                       format_func=lambda x: f"{df[df['Ticker']==x]['Company'].values[0]} ({x})")
            with col2:
                if st.button("Analyze →", type="primary", use_container_width=True):
                    st.session_state.selected_ticker = selected
                    st.switch_page("pages/company.py") if hasattr(st, 'switch_page') else st.rerun()


# ============= TAB 3: PORTFOLIO RISK ANALYZER =============
with tab3:
    st.header("📈 Portfolio Risk Analyzer")
    st.write("Analyze your portfolio's risk profile and potential drawdown")
    
    st.markdown("### 📝 Enter Your Holdings")
    num_stocks = st.number_input("How many stocks in your portfolio?", 1, 20, 3)
    
    portfolio = []
    for i in range(num_stocks):
        col1, col2 = st.columns([2, 1])
        with col1:
            ticker = st.text_input(f"Stock {i+1} Ticker:", key=f"ticker_{i}", 
                                  placeholder="e.g., AAPL")
        with col2:
            allocation = st.number_input(f"% of Portfolio:", 0, 100, 
                                        33 if i < 3 else 0, key=f"alloc_{i}")
        
        if ticker and allocation > 0:
            portfolio.append({"ticker": ticker.upper(), "allocation": allocation})
    
    if st.button("🔍 Analyze Portfolio Risk", type="primary"):
        if not portfolio:
            st.error("Please add at least one stock!")
        elif sum(p['allocation'] for p in portfolio) != 100:
            st.error(f"Allocations must sum to 100% (currently {sum(p['allocation'] for p in portfolio)}%)")
        else:
            with st.spinner("Analyzing portfolio..."):
                portfolio_data = []
                for item in portfolio:
                    quote = get_quote(item['ticker'])
                    if quote:
                        portfolio_data.append({
                            "ticker": item['ticker'],
                            "allocation": item['allocation'],
                            "beta": quote.get('beta', 1.0),
                            "pe": quote.get('pe', 0),
                            "marketCap": quote.get('marketCap', 0),
                            "name": quote.get('name', item['ticker'])
                        })
                
                if portfolio_data:
                    df = pd.DataFrame(portfolio_data)
                    
                    weighted_beta = sum(row['beta'] * row['allocation']/100 for _, row in df.iterrows())
                    avg_pe = df[df['pe'] > 0]['pe'].mean() if len(df[df['pe'] > 0]) > 0 else 0
                    total_market_cap = sum(row['marketCap'] * row['allocation']/100 for _, row in df.iterrows())
                    
                    st.markdown("### 📊 Portfolio Risk Profile")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Portfolio Beta", f"{weighted_beta:.2f}",
                               help="<1: Less volatile than market | >1: More volatile")
                    col2.metric("Avg P/E Ratio", f"{avg_pe:.1f}" if avg_pe > 0 else "N/A")
                    col3.metric("Weighted Market Cap", format_number(total_market_cap))
                    
                    st.divider()
                    
                    st.markdown("### 📉 Market Crash Scenarios")
                    
                    scenarios = [
                        {"name": "Minor Correction", "drop": -10, "desc": "Normal market volatility"},
                        {"name": "Bear Market", "drop": -20, "desc": "Significant downturn"},
                        {"name": "Market Crash", "drop": -30, "desc": "Severe recession"},
                        {"name": "Black Swan", "drop": -50, "desc": "2008-level crisis"}
                    ]
                    
                    for scenario in scenarios:
                        expected_drop = scenario['drop'] * weighted_beta
                        
                        if abs(expected_drop) > abs(scenario['drop']) * 1.2:
                            risk_level = "🔴 HIGH RISK"
                            color = "error"
                        elif abs(expected_drop) < abs(scenario['drop']) * 0.8:
                            risk_level = "🟢 LOW RISK"
                            color = "success"
                        else:
                            risk_level = "🟡 MODERATE RISK"
                            color = "info"
                        
                        with st.expander(f"{scenario['name']}: Market drops {scenario['drop']}%"):
                            st.write(f"**{scenario['desc']}**")
                            st.metric("Your Expected Loss", f"{expected_drop:.1f}%")
                            if color == "error":
                                st.error(f"{risk_level} - Your portfolio would likely drop MORE than the market")
                            elif color == "success":
                                st.success(f"{risk_level} - Your portfolio would likely drop LESS than the market")
                            else:
                                st.info(f"{risk_level} - Your portfolio would track the market closely")
                    
                    st.divider()
                    
                    st.markdown("### 🎯 Diversification Analysis")
                    
                    if len(portfolio_data) < 5:
                        st.warning(f"⚠️ You have only {len(portfolio_data)} stocks. Consider adding more for better diversification!")
                    elif len(portfolio_data) < 10:
                        st.info(f"✅ You have {len(portfolio_data)} stocks - decent diversification")
                    else:
                        st.success(f"🎉 You have {len(portfolio_data)} stocks - well diversified!")
                    
                    max_allocation = max(p['allocation'] for p in portfolio)
                    if max_allocation > 40:
                        st.error(f"🚨 {max_allocation}% in one stock is too concentrated! Aim for <20% per stock")
                    elif max_allocation > 25:
                        st.warning(f"⚠️ {max_allocation}% in one stock is somewhat concentrated")
                    else:
                        st.success(f"✅ Largest position is {max_allocation}% - good balance")
                    
                    st.markdown("### 📊 Portfolio Breakdown")
                    st.dataframe(df[['ticker', 'name', 'allocation', 'beta', 'pe']], use_container_width=True)
                    
                    st.markdown("### 💡 Recommendations")
                    if weighted_beta > 1.3:
                        st.info("🎯 Your portfolio is HIGH BETA (volatile). Consider adding defensive stocks like utilities or consumer staples to reduce risk.")
                    elif weighted_beta < 0.7:
                        st.info("🎯 Your portfolio is LOW BETA (stable). If you're young, you might want more growth stocks for higher returns.")
                    else:
                        st.success("🎯 Your portfolio has MODERATE BETA - balanced risk/reward profile!")

# ============= TAB 1: COMPANY ANALYSIS =============
with tab1:
    search = st.text_input(
        "🔍 Search by Company Name or Ticker:",
        st.session_state.selected_ticker,
        help="Try: Apple, AAPL, Microsoft, TSLA, etc."
    )
    
    if search:
        ticker, company_name = smart_search_ticker(search)
        st.session_state.selected_ticker = ticker
        if ticker != search.upper():
            st.success(f"✅ Found: {company_name} ({ticker})")
    else:
        ticker = st.session_state.selected_ticker
    
    profile = get_profile(ticker)
    if profile:
        company_name = profile.get('companyName', ticker)
        st.subheader(f"📈 {company_name} ({ticker})")
        
        description = profile.get('description', '')
        if description:
            with st.expander("ℹ️ What does this company do?"):
                st.write(description[:500] + "..." if len(description) > 500 else description)
        
        sector = profile.get('sector', 'N/A')
        industry = profile.get('industry', 'N/A')
        st.caption(f"**Sector:** {sector} | **Industry:** {industry}")
    else:
        company_name = ticker
        st.subheader(f"{ticker}")
    
    view = st.radio("Choose View:", [
        "📊 Key Metrics", 
        "🔀 Compare 2 Stocks",
        "📈 Financial Ratios", 
        "💰 Valuation (DCF)", 
        "📰 Latest News"
    ], horizontal=True)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        period_type = st.radio("Time Period:", ["Annual", "Quarterly"])
        period = 'annual' if period_type == "Annual" else 'quarter'
        years = st.slider("Years of History:", 1, 10, 5)
        
        st.divider()
        
        st.markdown("### 📈 Growth Metrics")
        
        income_df = get_income_statement(ticker, period, years*4 if period == 'quarter' else years)
        cash_df = get_cash_flow(ticker, period, years*4 if period == 'quarter' else years)
        
        if not income_df.empty:
            revenue_cagr = calculate_growth_rate(income_df, 'revenue', years)
            if revenue_cagr:
                st.metric("Revenue CAGR", f"{revenue_cagr:+.1f}%", 
                         help="Compound Annual Growth Rate for revenue")
            
            if 'netIncome' in income_df.columns:
                profit_cagr = calculate_growth_rate(income_df, 'netIncome', years)
                if profit_cagr:
                    st.metric("Profit CAGR", f"{profit_cagr:+.1f}%",
                             help="Compound Annual Growth Rate for net income")
        
        if not cash_df.empty and 'freeCashFlow' in cash_df.columns:
            fcf_cagr = calculate_growth_rate(cash_df, 'freeCashFlow', years)
            if fcf_cagr:
                st.metric("FCF CAGR", f"{fcf_cagr:+.1f}%",
                         help="Compound Annual Growth Rate for free cash flow")
        
        price_data = get_historical_price(ticker, years)
        if not price_data.empty and len(price_data) > 1:
            start_price = price_data['price'].iloc[0]
            end_price = price_data['price'].iloc[-1]
            price_growth = ((end_price - start_price) / start_price) * 100
            st.metric(f"Stock Price Growth ({years}Y)", f"{price_growth:+.1f}%",
                     help=f"Total return over {years} years")
        
        st.divider()
        st.markdown("### 📚 Quick Reference")
        st.info("""
        **CAGR**: Average yearly growth
        **FCF After SBC**: #1 metric
        **P/S Ratio**: Valuation by revenue
        **P/E Ratio**: Valuation by earnings
        """)
    
    quote = get_quote(ticker)
    ratios_ttm = get_ratios_ttm(ticker)
    balance_df = get_balance_sheet(ticker, period, years*4 if period == 'quarter' else years)
    ratios_df = get_financial_ratios(ticker, period, years*4 if period == 'quarter' else years)
    
    if quote:
        price = quote.get('price', 0)
        change_pct = quote.get('changesPercentage', 0)
        market_cap = quote.get('marketCap', 0)
        
        pe = None
        ps = None
        
        if ratios_ttm:
            pe = ratios_ttm.get('peRatioTTM', 0)
            ps = ratios_ttm.get('priceToSalesRatioTTM', 0)
        
        if not pe or pe == 0:
            pe = quote.get('pe', 0)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Current Price", f"${price:.2f}", f"{change_pct:+.2f}%")
        col2.metric("Market Cap", format_number(market_cap))
        
        col3.metric("P/E Ratio", f"{pe:.2f}" if pe and pe > 0 else "N/A",
                   help="Price-to-Earnings ratio. How expensive is the stock? Lower = cheaper. Good range: 15-25")
        
        col4.metric("P/S Ratio", f"{ps:.2f}" if ps and ps > 0 else "N/A",
                   help="Price-to-Sales ratio. Shows how much you pay for $1 of revenue. Lower = better value. Tech: 5-10 | Retail: 0.5-2")
        
        price_target = get_price_target(ticker)
        if price_target:
            avg_target = price_target.get('targetConsensus', 0)
            if avg_target > 0:
                upside = ((avg_target - price) / price) * 100
                col5.metric("Analyst Target", f"${avg_target:.2f}", f"{upside:+.1f}% upside",
                           help="Average Wall Street analyst 12-month price target")
        
        st.divider()
    
    if view == "📊 Key Metrics":
        
        st.markdown(f"### 📈 {company_name} - Stock Price History")
        price_data = get_historical_price(ticker, years)
        if not price_data.empty:
            y_column = 'price'
            
            chart_title = f'{company_name} - Stock Price ({years} Years)'
            
            fig = px.area(price_data, x='date', y=y_column, title=chart_title)
            fig.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis_title="",
                yaxis_title="Price ($)",
                showlegend=False,
                yaxis=dict(rangemode='tozero'),
                margin=dict(l=20, r=20, t=60, b=20),
                hoverlabel=dict(bgcolor="white", font_size=12, font_color="black")
            )
            fig.update_traces(fillcolor='rgba(157, 78, 221, 0.3)', line_color='#9D4EDD', line_width=2)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Stock price data not available")
        
        st.divider()
        
        st.markdown(f"### 💵 {company_name} - Cash Flow Statement")
        show_why_it_matters('fcfAfterSBC')
        
        if not cash_df.empty:
            if 'stockBasedCompensation' in cash_df.columns and 'freeCashFlow' in cash_df.columns:
                cash_df['fcfAfterSBC'] = cash_df['freeCashFlow'] - abs(cash_df['stockBasedCompensation'])
            
            metrics_to_plot = []
            metric_names = []
            
            if 'fcfAfterSBC' in cash_df.columns:
                metrics_to_plot.append('fcfAfterSBC')
                metric_names.append('FCF After SBC')
            if 'freeCashFlow' in cash_df.columns:
                metrics_to_plot.append('freeCashFlow')
                metric_names.append('Free Cash Flow')
            if 'operatingCashFlow' in cash_df.columns:
                metrics_to_plot.append('operatingCashFlow')
                metric_names.append('Operating Cash Flow')
            
            if metrics_to_plot:
                plot_df = cash_df[['date'] + metrics_to_plot].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y-%m' if period == 'quarter' else '%Y')
                
                fig = go.Figure()
                colors = ['#9D4EDD', '#00D9FF', '#FF69B4']
                
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    fig.add_trace(go.Bar(
                        x=plot_df['date'],
                        y=plot_df[metric],
                        name=name,
                        marker_color=colors[i % len(colors)]
                    ))
                
                fig.update_layout(
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="Period",
                    yaxis_title="Amount ($)",
                    yaxis=dict(rangemode='tozero'),
                    margin=dict(l=20, r=20, t=60, b=20),
                    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                cols = st.columns(len(metrics_to_plot))
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    cols[i].metric(f"Latest {name}", format_number(cash_df[metric].iloc[-1]))
        else:
            st.warning("⚠️ Cash flow data not available")
        
        st.divider()
        
        st.markdown(f"### 💰 {company_name} - Income Statement")
        show_why_it_matters('revenue')
        
        if not income_df.empty:
            metrics_to_plot = []
            metric_names = []
            
            if 'revenue' in income_df.columns:
                metrics_to_plot.append('revenue')
                metric_names.append('Revenue')
            if 'operatingIncome' in income_df.columns:
                metrics_to_plot.append('operatingIncome')
                metric_names.append('Operating Income')
            if 'netIncome' in income_df.columns:
                metrics_to_plot.append('netIncome')
                metric_names.append('Net Income')
            
            if metrics_to_plot:
                plot_df = income_df[['date'] + metrics_to_plot].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y-%m' if period == 'quarter' else '%Y')
                
                fig = go.Figure()
                colors = ['#00D9FF', '#FFD700', '#9D4EDD']
                
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    fig.add_trace(go.Bar(
                        x=plot_df['date'],
                        y=plot_df[metric],
                        name=name,
                        marker_color=colors[i % len(colors)]
                    ))
                
                fig.update_layout(
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="Period",
                    yaxis_title="Amount ($)",
                    yaxis=dict(rangemode='tozero'),
                    margin=dict(l=20, r=20, t=60, b=20),
                    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                if 'revenue' in income_df.columns:
                    col1.metric("Latest Revenue", format_number(income_df['revenue'].iloc[-1]))
                if 'operatingIncome' in income_df.columns:
                    col2.metric("Latest Op Income", format_number(income_df['operatingIncome'].iloc[-1]))
                if 'netIncome' in income_df.columns:
                    col3.metric("Latest Net Income", format_number(income_df['netIncome'].iloc[-1]))
        else:
            st.warning("⚠️ Income statement data not available")
        
        st.divider()
        
        st.markdown(f"### 🏦 {company_name} - Balance Sheet")
        
        if not balance_df.empty:
            metrics_to_plot = []
            metric_names = []
            
            if 'totalAssets' in balance_df.columns:
                metrics_to_plot.append('totalAssets')
                metric_names.append('Total Assets')
            if 'totalLiabilities' in balance_df.columns:
                metrics_to_plot.append('totalLiabilities')
                metric_names.append('Total Liabilities')
            if 'totalStockholdersEquity' in balance_df.columns:
                metrics_to_plot.append('totalStockholdersEquity')
                metric_names.append('Shareholders Equity')
            
            if metrics_to_plot:
                plot_df = balance_df[['date'] + metrics_to_plot].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y-%m' if period == 'quarter' else '%Y')
                
                fig = go.Figure()
                colors = ['#00D9FF', '#FF6B6B', '#FFD700']
                
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    fig.add_trace(go.Bar(
                        x=plot_df['date'],
                        y=plot_df[metric],
                        name=name,
                        marker_color=colors[i % len(colors)]
                    ))
                
                fig.update_layout(
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="Period",
                    yaxis_title="Amount ($)",
                    yaxis=dict(rangemode='tozero'),
                    margin=dict(l=20, r=20, t=60, b=20),
                    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                cols = st.columns(len(metrics_to_plot))
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    cols[i].metric(f"Latest {name}", format_number(balance_df[metric].iloc[-1]))
        else:
            st.warning("⚠️ Balance sheet data not available")
    
    elif view == "🔀 Compare 2 Stocks":
        st.markdown("## 🔀 Side-by-Side Stock Comparison")
        st.info("💡 Compare any two stocks across key metrics and charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stock1 = st.text_input("Stock 1:", value=ticker, key="compare_stock1")
            if stock1:
                ticker1, name1 = smart_search_ticker(stock1)
                if ticker1 != stock1.upper():
                    st.caption(f"✅ Found: {name1} ({ticker1})")
        
        with col2:
            stock2 = st.text_input("Stock 2:", placeholder="e.g., MSFT", key="compare_stock2")
            if stock2:
                ticker2, name2 = smart_search_ticker(stock2)
                if ticker2 != stock2.upper():
                    st.caption(f"✅ Found: {name2} ({ticker2})")
        
        if stock1 and stock2:
            quote1 = get_quote(ticker1)
            quote2 = get_quote(ticker2)
            
            if quote1 and quote2:
                ratios_ttm1 = get_ratios_ttm(ticker1)
                ratios_ttm2 = get_ratios_ttm(ticker2)
                ratios1 = get_financial_ratios(ticker1, 'annual', 1)
                ratios2 = get_financial_ratios(ticker2, 'annual', 1)
                cash1 = get_cash_flow(ticker1, 'annual', 1)
                cash2 = get_cash_flow(ticker2, 'annual', 1)
                
                st.divider()
                st.markdown("### 📊 Comprehensive Metrics Comparison")
                
                def get_metric_value(quote, ratios_ttm, ratios, cash, metric_name):
                    if metric_name == "P/E":
                        if ratios_ttm:
                            pe = ratios_ttm.get('peRatioTTM', 0)
                            if pe and pe > 0:
                                return f"{pe:.2f}"
                        return "N/A"
                    
                    elif metric_name == "P/S":
                        if ratios_ttm:
                            ps = ratios_ttm.get('priceToSalesRatioTTM', 0)
                            if ps and ps > 0:
                                return f"{ps:.2f}"
                        return "N/A"
                    
                    elif metric_name == "Gross Margin":
                        if not ratios.empty and 'grossProfitMargin' in ratios.columns:
                            margin = ratios['grossProfitMargin'].iloc[-1] * 100
                            return f"{margin:.1f}%"
                        return "N/A"
                    
                    elif metric_name == "Operating Margin":
                        if not ratios.empty and 'operatingProfitMargin' in ratios.columns:
                            margin = ratios['operatingProfitMargin'].iloc[-1] * 100
                            return f"{margin:.1f}%"
                        return "N/A"
                    
                    elif metric_name == "Net Margin":
                        if not ratios.empty and 'netProfitMargin' in ratios.columns:
                            margin = ratios['netProfitMargin'].iloc[-1] * 100
                            return f"{margin:.1f}%"
                        return "N/A"
                    
                    elif metric_name == "FCF":
                        if not cash.empty and 'freeCashFlow' in cash.columns:
                            fcf = cash['freeCashFlow'].iloc[-1]
                            return format_number(fcf)
                        return "N/A"
                    
                    elif metric_name == "FCF per Share":
                        if not cash.empty and 'freeCashFlow' in cash.columns:
                            fcf = cash['freeCashFlow'].iloc[-1]
                            shares = quote.get('sharesOutstanding', 0)
                            if fcf and shares and shares > 0:
                                fcf_per_share = fcf / shares
                                return f"${fcf_per_share:.2f}"
                        return "N/A"
                    
                    return "N/A"
                
                metrics_comparison = {
                    "Metric": [
                        "Price", 
                        "Market Cap", 
                        "P/E Ratio", 
                        "P/S Ratio",
                        "Change (Today)",
                        "Gross Margin",
                        "Operating Margin",
                        "Net Margin",
                        "FCF (TTM)",
                        "FCF per Share"
                    ],
                    ticker1: [
                        f"${quote1.get('price', 0):.2f}",
                        format_number(quote1.get('marketCap', 0)),
                        get_metric_value(quote1, ratios_ttm1, ratios1, cash1, "P/E"),
                        get_metric_value(quote1, ratios_ttm1, ratios1, cash1, "P/S"),
                        f"{quote1.get('changesPercentage', 0):+.2f}%",
                        get_metric_value(quote1, ratios_ttm1, ratios1, cash1, "Gross Margin"),
                        get_metric_value(quote1, ratios_ttm1, ratios1, cash1, "Operating Margin"),
                        get_metric_value(quote1, ratios_ttm1, ratios1, cash1, "Net Margin"),
                        get_metric_value(quote1, ratios_ttm1, ratios1, cash1, "FCF"),
                        get_metric_value(quote1, ratios_ttm1, ratios1, cash1, "FCF per Share")
                    ],
                    ticker2: [
                        f"${quote2.get('price', 0):.2f}",
                        format_number(quote2.get('marketCap', 0)),
                        get_metric_value(quote2, ratios_ttm2, ratios2, cash2, "P/E"),
                        get_metric_value(quote2, ratios_ttm2, ratios2, cash2, "P/S"),
                        f"{quote2.get('changesPercentage', 0):+.2f}%",
                        get_metric_value(quote2, ratios_ttm2, ratios2, cash2, "Gross Margin"),
                        get_metric_value(quote2, ratios_ttm2, ratios2, cash2, "Operating Margin"),
                        get_metric_value(quote2, ratios_ttm2, ratios2, cash2, "Net Margin"),
                        get_metric_value(quote2, ratios_ttm2, ratios2, cash2, "FCF"),
                        get_metric_value(quote2, ratios_ttm2, ratios2, cash2, "FCF per Share")
                    ]
                }
                
                comparison_df = pd.DataFrame(metrics_comparison)
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                
                st.divider()
                
                st.markdown("### 📈 Stock Price Comparison")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"#### {ticker1}")
                    price_data1 = get_historical_price(ticker1, years)
                    if not price_data1.empty:
                        fig1 = px.line(price_data1, x='date', y='price')
                        fig1.update_layout(
                            height=300,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white',
                            showlegend=False,
                            yaxis=dict(rangemode='tozero'),
                            margin=dict(l=20, r=20, t=20, b=20),
                            hoverlabel=dict(bgcolor="white", font_size=12, font_color="black")
                        )
                        fig1.update_traces(line_color='#9D4EDD', line_width=2)
                        st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.warning("Price data not available")
                
                with col2:
                    st.markdown(f"#### {ticker2}")
                    price_data2 = get_historical_price(ticker2, years)
                    if not price_data2.empty:
                        fig2 = px.line(price_data2, x='date', y='price')
                        fig2.update_layout(
                            height=300,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white',
                            showlegend=False,
                            yaxis=dict(rangemode='tozero'),
                            margin=dict(l=20, r=20, t=20, b=20),
                            hoverlabel=dict(bgcolor="white", font_size=12, font_color="black")
                        )
                        fig2.update_traces(line_color='#00D9FF', line_width=2)
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.warning("Price data not available")
                
                st.divider()
                
                st.markdown("### 💰 Revenue Comparison")
                
                income1 = get_income_statement(ticker1, period, years*4 if period == 'quarter' else years)
                income2 = get_income_statement(ticker2, period, years*4 if period == 'quarter' else years)
                
                if not income1.empty and not income2.empty and 'revenue' in income1.columns and 'revenue' in income2.columns:
                    plot_df1 = income1[['date', 'revenue']].copy()
                    plot_df1['date'] = plot_df1['date'].dt.strftime('%Y')
                    plot_df1['company'] = ticker1
                    
                    plot_df2 = income2[['date', 'revenue']].copy()
                    plot_df2['date'] = plot_df2['date'].dt.strftime('%Y')
                    plot_df2['company'] = ticker2
                    
                    combined = pd.concat([plot_df1, plot_df2])
                    
                    fig = px.bar(combined, x='date', y='revenue', color='company', barmode='group',
                                color_discrete_map={ticker1: '#9D4EDD', ticker2: '#00D9FF'})
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        yaxis=dict(rangemode='tozero'),
                        margin=dict(l=20, r=20, t=40, b=20),
                        hoverlabel=dict(bgcolor="white", font_size=12, font_color="black")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Revenue comparison not available for selected period")
                
                st.divider()
                st.markdown("### 🏆 Quick Comparison")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**💰 Valuation (Lower P/E = Better)**")
                    pe1_val = ratios_ttm1.get('peRatioTTM', 0) if ratios_ttm1 else 0
                    pe2_val = ratios_ttm2.get('peRatioTTM', 0) if ratios_ttm2 else 0
                    if pe1_val > 0 and pe2_val > 0:
                        if pe1_val < pe2_val:
                            st.success(f"🏆 {ticker1} ({pe1_val:.2f})")
                            st.info(f"{ticker2} ({pe2_val:.2f})")
                        else:
                            st.info(f"{ticker1} ({pe1_val:.2f})")
                            st.success(f"🏆 {ticker2} ({pe2_val:.2f})")
                    else:
                        st.info("P/E comparison not available")
                
                with col2:
                    st.markdown("**📈 Today's Performance**")
                    chg1 = quote1.get('changesPercentage', 0)
                    chg2 = quote2.get('changesPercentage', 0)
                    if chg1 > chg2:
                        st.success(f"🏆 {ticker1} ({chg1:+.2f}%)")
                        st.info(f"{ticker2} ({chg2:+.2f}%)")
                    else:
                        st.info(f"{ticker1} ({chg1:+.2f}%)")
                        st.success(f"🏆 {ticker2} ({chg2:+.2f}%)")
                
                with col3:
                    st.markdown("**🏢 Market Cap**")
                    cap1 = quote1.get('marketCap', 0)
                    cap2 = quote2.get('marketCap', 0)
                    if cap1 > cap2:
                        st.success(f"🏆 {ticker1} ({format_number(cap1)})")
                        st.info(f"{ticker2} ({format_number(cap2)})")
                    else:
                        st.info(f"{ticker1} ({format_number(cap1)})")
                        st.success(f"🏆 {ticker2} ({format_number(cap2)})")
            else:
                st.warning("Could not fetch data for one or both stocks")
        else:
            st.info("👆 Enter two stock tickers above to compare")
    
    elif view == "📈 Financial Ratios":
        st.markdown("## 📊 Profitability Ratios")
        
        if not ratios_df.empty:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### 💡 What to Look For:")
                for ratio_name, ratio_exp in RATIO_EXPLANATIONS.items():
                    with st.expander(ratio_name):
                        st.write(f"**{ratio_exp['what']}**")
                        st.write(f"✅ {ratio_exp['good']}")
                        st.write(f"🎯 {ratio_exp['targets']}")
            
            with col2:
                if 'grossProfitMargin' in ratios_df.columns:
                    latest = ratios_df['grossProfitMargin'].iloc[-1] * 100
                    st.metric("Gross Margin", f"{latest:.1f}%")
                
                if 'operatingProfitMargin' in ratios_df.columns:
                    latest = ratios_df['operatingProfitMargin'].iloc[-1] * 100
                    st.metric("Operating Margin", f"{latest:.1f}%")
                
                if 'netProfitMargin' in ratios_df.columns:
                    latest = ratios_df['netProfitMargin'].iloc[-1] * 100
                    st.metric("Net Margin", f"{latest:.1f}%")
                
                if 'returnOnEquity' in ratios_df.columns:
                    latest = ratios_df['returnOnEquity'].iloc[-1] * 100
                    st.metric("ROE", f"{latest:.1f}%")
                
                if 'returnOnAssets' in ratios_df.columns:
                    latest = ratios_df['returnOnAssets'].iloc[-1] * 100
                    st.metric("ROA", f"{latest:.1f}%")
        else:
            st.warning("Ratio data not available")
    
    elif view == "💰 Valuation (DCF)":
        st.markdown("## 💰 DCF Valuation")
        
        with st.expander("📚 What is DCF?"):
            st.markdown(DCF_EXPLANATION)
        
        col1, col2 = st.columns(2)
        with col1:
            growth_rate = st.slider("Growth Rate (%/year)", 0, 50, 15)
            terminal_growth = st.slider("Terminal Growth (%)", 0, 10, 3)
        
        with col2:
            discount_rate = st.slider("Discount Rate (%)", 5, 20, 10)
            years_forecast = st.slider("Forecast Years", 5, 15, 10)
        
        if not cash_df.empty and 'freeCashFlow' in cash_df.columns:
            latest_fcf = cash_df['freeCashFlow'].iloc[-1]
            
            if latest_fcf > 0:
                pv_fcf = 0
                for year in range(1, years_forecast + 1):
                    fcf = latest_fcf * ((1 + growth_rate/100) ** year)
                    pv = fcf / ((1 + discount_rate/100) ** year)
                    pv_fcf += pv
                
                terminal_value = (latest_fcf * ((1 + growth_rate/100) ** years_forecast) * 
                                (1 + terminal_growth/100)) / ((discount_rate - terminal_growth)/100)
                pv_terminal = terminal_value / ((1 + discount_rate/100) ** years_forecast)
                
                enterprise_value = pv_fcf + pv_terminal
                
                if quote:
                    shares = quote.get('sharesOutstanding', 0)
                    if shares > 0:
                        fair_value = enterprise_value / shares
                        current_price = quote.get('price', 0)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("DCF Fair Value", f"${fair_value:.2f}")
                        col2.metric("Current Price", f"${current_price:.2f}")
                        
                        if current_price > 0:
                            upside = ((fair_value - current_price) / current_price) * 100
                            col3.metric("Upside / Downside", f"{upside:+.1f}%")
                            
                            if upside > 20:
                                st.success("🚀 Potentially UNDERVALUED!")
                            elif upside < -20:
                                st.error("🚨 Potentially OVERVALUED!")
                            else:
                                st.info("✅ Fairly valued")
            else:
                st.warning("Negative FCF - DCF not applicable")
        else:
            st.warning("Cash flow data not available")
    
    elif view == "📰 Latest News":
        st.markdown("## 📰 Latest News")
        
        news = get_stock_news(ticker, 15)
        if news:
            for article in news[:10]:
                with st.expander(f"📰 {article.get('title', 'No title')}"):
                    st.write(f"**Published:** {article.get('publishedDate', 'Unknown')}")
                    st.write(article.get('text', 'No summary')[:300] + "...")
                    url = article.get('url', '')
                    if url:
                        st.markdown(f"[Read full article]({url})")
        else:
            st.info("No recent news available")

# ============= TAB 4: CHECKLIST =============
with tab4:
    st.header("✅ Investment Checklist")
    st.write("Quick check before investing")
    
    ticker_check = st.text_input("Enter ticker:", value=st.session_state.selected_ticker)
    
    if st.button("Analyze"):
        quote = get_quote(ticker_check)
        ratios = get_financial_ratios(ticker_check, 'annual', 1)
        cash = get_cash_flow(ticker_check, 'annual', 1)
        
        if quote and not ratios.empty:
            st.subheader(f"📊 {quote.get('name', ticker_check)} ({ticker_check})")
            
            checks = []
            
            if not ratios.empty and 'netProfitMargin' in ratios.columns:
                margin = ratios['netProfitMargin'].iloc[-1]
                checks.append(("✅ Profitable (>10% margin)" if margin > 0.1 else "❌ Low profitability", margin > 0.1))
            
            if not cash.empty and 'freeCashFlow' in cash.columns:
                fcf = cash['freeCashFlow'].iloc[-1]
                checks.append(("✅ Positive free cash flow" if fcf > 0 else "❌ Negative FCF", fcf > 0))
            
            pe = quote.get('pe', 0)
            if 0 < pe < 30:
                checks.append(("✅ Reasonable P/E (<30)", True))
            elif pe > 30:
                checks.append(("⚠️ High P/E (>30)", False))
            
            mcap = quote.get('marketCap', 0)
            checks.append(("✅ Large cap (>$10B)" if mcap > 10e9 else "⚠️ Small/mid cap", mcap > 10e9))
            
            for check, passed in checks:
                if passed:
                    st.success(check)
                else:
                    st.warning(check)
            
            passed_count = sum(1 for _, p in checks if p)
            total = len(checks)
            
            st.divider()
            st.metric("Score", f"{passed_count}/{total}")
            
            if passed_count >= total * 0.75:
                st.success("🎉 Strong candidate!")
            elif passed_count >= total * 0.5:
                st.info("🤔 Mixed signals")
            else:
                st.error("🚨 Many red flags")

# ============= TAB 5: FINANCE 101 =============
with tab5:
    st.header("📚 Finance 101")
    st.write("Learn key financial terms")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Income & Cash Flow")
        for term in ["FCF After SBC", "Revenue", "Operating Income", "Net Income", "CAGR", "FCF per Share"]:
            with st.expander(term):
                st.write(GLOSSARY[term])
    
    with col2:
        st.markdown("### 📊 Valuation & Risk")
        for term in ["P/E Ratio", "P/S Ratio", "Market Cap", "Beta", "Sharpe Ratio", "Max Drawdown"]:
            with st.expander(term):
                st.write(GLOSSARY[term])

st.divider()
st.caption("💡 Finance Made Simple | FMP Premium | Real-time data")
st.caption("⚠️ Educational purposes only. Not financial advice. Do your own research.")
