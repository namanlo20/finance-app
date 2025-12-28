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
BASE_URL = "https://financialmodelingprep.com/api/v3"

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
        
        🚨 **Why companies hide this:**
        Tech companies pay employees in stock to avoid reporting it as an expense.
        It makes profits look bigger, but it DILUTES your ownership!
        """,
        "personal_budget": """
        **Your Personal Budget:**
        - Income: $5,000
        - Bills: $3,000
        - Left over: $2,000
        - Gift cards promised: $500
        - **Real take-home: $1,500** ← This is FCF After SBC
        """
    },
    "freeCashFlow": {
        "title": "Free Cash Flow",
        "simple": "Money left after paying bills and investing in the business",
        "why": """
        **Like your savings after rent and car payments:**
        
        You earn money → Pay rent → Pay for car/house repairs → What's left is YOUR free cash
        
        Company earns money → Pays operating costs → Buys equipment → What's left is FREE CASH FLOW
        
        💡 **Why it matters:**
        - Companies can use this to pay dividends
        - Buy back stock
        - Grow the business
        - Pay off debt
        
        ⚠️ **Red flag:** If FCF is negative, company is burning cash (not sustainable!)
        """,
        "personal_budget": """
        **Your Budget:**
        - Monthly income: $5,000
        - Rent + bills: $3,000
        - Car payment: $500
        - **Free cash: $1,500** ← You can save or invest this
        """
    },
    "revenue": {
        "title": "Revenue (Top Line)",
        "simple": "Total money coming in before any costs",
        "why": """
        **Like your gross income before taxes:**
        
        If you're a freelancer making $100,000/year, that's your revenue.
        You haven't paid taxes, business expenses, or anything yet.
        
        💡 **Why it matters:**
        - Shows if company is growing
        - Growing revenue = more customers or higher prices
        
        ⚠️ **Not the full picture:** Revenue doesn't mean profit!
        """,
        "personal_budget": """
        **Your Income:**
        - Salary: $60,000/year
        - Side hustle: $10,000/year
        - **Total revenue: $70,000** ← Before taxes/expenses
        """
    },
    "netIncome": {
        "title": "Net Income (Bottom Line)",
        "simple": "Actual profit after ALL expenses",
        "why": """
        **Like your money left after paying everything:**
        
        You earn $5,000 → Pay taxes, rent, food, insurance, etc. → $800 left
        That $800 is your "net income"
        
        💡 **Why it matters:**
        - Shows if company is actually profitable
        - Can be manipulated with accounting tricks
        
        ⚠️ **Better metric:** FCF After SBC (harder to fake!)
        """,
        "personal_budget": """
        **After everything:**
        - Income: $5,000
        - All expenses: $4,200
        - **Net income: $800** ← True profit
        """
    }
}

RATIO_EXPLANATIONS = {
    "Gross Margin": {
        "what": "Profit margin after cost of goods sold",
        "good": "High = Pricing power (can charge premium prices)",
        "targets": "Software: 70-90% | Retail: 20-40% | Manufacturing: 30-50%",
        "example": "Apple sells iPhone for $1,000, costs $430 to make → 57% gross margin"
    },
    "Operating Margin": {
        "what": "Profit margin from core business operations",
        "good": "High = Efficient operations",
        "targets": "Software: >20% | Retail: 5-10% | Manufacturing: 10-15%",
        "example": "Microsoft: For every $100 in sales, $42 is operating profit"
    },
    "Net Margin": {
        "what": "Bottom line profit margin",
        "good": "High = Very profitable overall",
        "targets": "Tech: 15-25% | Retail: 2-5% | Healthcare: 10-15%",
        "example": "Google: Keeps $21 of every $100 earned as profit"
    },
    "ROE": {
        "what": "Return on shareholder equity",
        "good": "High = Efficiently using shareholder money",
        "targets": ">15% is good, >20% is excellent",
        "example": "15% ROE = Every $100 invested generates $15 profit annually"
    }
}

DCF_EXPLANATION = """
### 💰 DCF Calculator (Discounted Cash Flow)

**What is DCF in simple terms?**

Imagine your friend wants to sell you a lemonade stand.
- The stand makes $100/year
- How much would you pay for it?

**DCF answers this question for stocks!**

**The formula (simplified):**
1. Estimate future cash flows (5-10 years)
2. Add them all up
3. Divide by number of shares
4. That's the "fair value" per share

**Example:**
- Company generates $10B free cash flow/year
- You expect 10% annual growth
- Over 10 years, that's worth ~$175B
- Divided by 1B shares = $175/share fair value
- Stock price is $150 → UNDERVALUED! 🎯

**Why it matters:**
If fair value > current price → Stock might be cheap!
If fair value < current price → Stock might be expensive!

**⚠️ Warning:** DCF is sensitive to assumptions (garbage in = garbage out)
"""

ANALYST_TARGET_EXPLANATION = """
### 🎯 Analyst Price Targets

**What are these?**
Professional Wall Street analysts predict where the stock price will be in 12 months.

**How to read:**
- **High:** Most optimistic prediction
- **Average:** Consensus view
- **Low:** Most pessimistic prediction

**Example:**
If stock is $100 and average target is $120 → Analysts expect 20% upside

**⚠️ Important:**
- Analysts are often wrong
- They work for banks with conflicts of interest
- Use as ONE data point, not the only one
"""

#============= HELPER FUNCTIONS =============

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
    """Show explanation for a metric"""
    if metric_key in SIMPLE_EXPLANATIONS:
        exp = SIMPLE_EXPLANATIONS[metric_key]
        
        st.markdown(f"""
        <div class="why-box">
        <h4>💡 Why {exp['title']} Matters</h4>
        <p><strong>{exp['simple']}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📚 Learn More (Click to Expand)"):
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
    """Get list of ALL stocks"""
    url = f"{BASE_URL}/stock/list?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
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
        return {}

@st.cache_data(ttl=300)
def smart_search_ticker(search_term):
    """Smart search with typo handling"""
    search_term = search_term.upper().strip()
    all_stocks = get_all_stocks()
    
    if search_term in all_stocks and len(search_term) <= 5:
        return search_term, all_stocks[search_term]
    
    if search_term in all_stocks:
        return all_stocks[search_term], search_term
    
    tickers = [k for k in all_stocks.keys() if len(k) <= 5]
    close_tickers = get_close_matches(search_term, tickers, n=1, cutoff=0.7)
    if close_tickers:
        ticker = close_tickers[0]
        return ticker, all_stocks[ticker]
    
    names = [k for k in all_stocks.keys() if len(k) > 5]
    close_names = get_close_matches(search_term, names, n=1, cutoff=0.6)
    if close_names:
        name = close_names[0]
        return all_stocks[name], name
    
    for key, value in all_stocks.items():
        if len(key) > 5 and search_term in key:
            return value, key
    
    return search_term, search_term

@st.cache_data(ttl=300)
def get_quote(ticker):
    url = f"{BASE_URL}/quote/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data and len(data) > 0:
            return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=300)
def get_profile(ticker):
    url = f"{BASE_URL}/profile/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data and len(data) > 0:
            return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=300)
def get_analyst_estimates(ticker):
    """Get analyst price targets"""
    url = f"{BASE_URL}/analyst-estimates/{ticker}?limit=4&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data if data else []
    except:
        return []

@st.cache_data(ttl=300)
def get_price_target(ticker):
    """Get price target consensus"""
    url = f"{BASE_URL}/price-target-consensus?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data and len(data) > 0:
            return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=300)
def get_income_statement(ticker, period='annual', limit=10):
    url = f"{BASE_URL}/income-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
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
def get_balance_sheet(ticker, period='annual', limit=10):
    url = f"{BASE_URL}/balance-sheet-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
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
    url = f"{BASE_URL}/cash-flow-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
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
    url = f"{BASE_URL}/ratios/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
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
def get_historical_price(ticker, years=10):
    url = f"{BASE_URL}/historical-price-full/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'historical' in data:
            df = pd.DataFrame(data['historical'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            cutoff_date = datetime.now() - timedelta(days=years*365)
            df = df[df['date'] >= cutoff_date]
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_news(ticker):
    url = f"{BASE_URL}/stock_news?tickers={ticker}&limit=20&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data if data else []
    except:
        return []

def calculate_simple_dcf(fcf_current, growth_rate, discount_rate, years, shares_outstanding):
    """Simple DCF calculation"""
    future_fcf = []
    for year in range(1, years + 1):
        fcf = fcf_current * ((1 + growth_rate) ** year)
        pv = fcf / ((1 + discount_rate) ** year)
        future_fcf.append(pv)
    
    total_pv = sum(future_fcf)
    terminal_value = (fcf_current * ((1 + growth_rate) ** years) * (1 + 0.03)) / (discount_rate - 0.03)
    terminal_pv = terminal_value / ((1 + discount_rate) ** years)
    
    enterprise_value = total_pv + terminal_pv
    price_per_share = enterprise_value / shares_outstanding if shares_outstanding > 0 else 0
    
    return price_per_share, enterprise_value

# ============= MAIN APP =============

if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "NVDA"

# Header with branding
col1, col2 = st.columns([3, 1])
with col1:
    st.title("💰 Finance Made Simple")
    st.caption("AI-Powered Stock Analysis for Everyone | No Finance Degree Required")
with col2:
    st.markdown("### 🤖 AI-Ready")
    st.caption("Powered by FMP API")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Company Deep Dive", 
    "🎯 Sector Explorer", 
    "💎 Investment Checklist",
    "📚 Finance 101"
])

# ============= TAB 4: FINANCE 101 =============
with tab4:
    st.header("📚 Finance 101: Learn the Basics")
    
    st.markdown("### 🎓 Key Concepts Everyone Should Know")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💵 Cash Flow Metrics")
        for key in ['freeCashFlow', 'fcfAfterSBC']:
            if key in SIMPLE_EXPLANATIONS:
                exp = SIMPLE_EXPLANATIONS[key]
                with st.expander(f"📖 {exp['title']}"):
                    st.write(f"**Simple:** {exp['simple']}")
                    st.markdown(exp['why'])
                    if 'personal_budget' in exp:
                        st.markdown(exp['personal_budget'])
        
        st.markdown("#### 📊 Profitability Metrics")
        for key in ['revenue', 'netIncome']:
            if key in SIMPLE_EXPLANATIONS:
                exp = SIMPLE_EXPLANATIONS[key]
                with st.expander(f"📖 {exp['title']}"):
                    st.write(f"**Simple:** {exp['simple']}")
                    st.markdown(exp['why'])
                    if 'personal_budget' in exp:
                        st.markdown(exp['personal_budget'])
    
    with col2:
        st.markdown("#### 📈 Financial Ratios")
        for ratio_name, ratio_exp in RATIO_EXPLANATIONS.items():
            with st.expander(f"📊 {ratio_name}"):
                st.write(f"**What it is:** {ratio_exp['what']}")
                st.write(f"**Why it's good:** {ratio_exp['good']}")
                st.write(f"**Target values:** {ratio_exp['targets']}")
                st.info(f"💡 Example: {ratio_exp['example']}")
        
        with st.expander("💰 DCF Valuation"):
            st.markdown(DCF_EXPLANATION)
        
        with st.expander("🎯 Analyst Price Targets"):
            st.markdown(ANALYST_TARGET_EXPLANATION)

# ============= TAB 3: CHECKLIST =============
with tab3:
    st.header("💎 Your Investment Checklist")
    st.markdown("""
    ### ✅ What to Look For (In Order of Importance):
    
    **1. FCF After SBC** ⭐⭐⭐
    - Most honest cash metric
    - Should be positive and growing
    - If negative for 3+ years → RED FLAG 🚨
    
    **2. Revenue Growth**
    - >20% YoY = Exciting 🚀
    - 10-20% = Solid growth ✅
    - <5% = Struggling or mature 😴
    
    **3. Gross Margin**
    - Software: >70% = Excellent
    - Hardware: >40% = Good
    - Retail: >25% = Decent
    
    **4. Operating Margin**
    - Should be stable or growing
    - Shrinking margins = losing pricing power
    
    **5. Debt Level**
    - Total Debt / Equity < 0.5 = Conservative
    - > 2.0 = Risky (depends on industry)
    
    ### 🚨 RED FLAGS (Avoid These!):
    
    - ❌ Negative FCF for 3+ years
    - ❌ Stock comp > 30% of revenue
    - ❌ Declining gross margins
    - ❌ Revenue growing but FCF shrinking
    - ❌ Inconsistent earnings (up and down randomly)
    - ❌ High debt + low FCF
    """)

# ============= TAB 2: SECTOR EXPLORER =============
with tab2:
    st.header("🎯 Sector Explorer")
    st.caption("Browse companies by sector, ranked by market cap")
    
    SECTORS = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "ADBE", "CRM", "ORCL", "INTC", "AMD"],
        "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "ABT", "MRK", "DHR", "LLY", "BMY"],
        "Financial": ["JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "SCHW", "AXP", "USB"],
        "Consumer": ["AMZN", "TSLA", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "COST"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL"],
        "Industrial": ["BA", "CAT", "GE", "HON", "UNP", "UPS", "LMT", "RTX", "DE", "MMM"],
    }
    
    selected_sector = st.selectbox("Choose a sector:", list(SECTORS.keys()))
    
    if selected_sector:
        tickers = SECTORS[selected_sector]
        rows = []
        
        with st.spinner(f"Loading {selected_sector} companies..."):
            for ticker in tickers:
                quote = get_quote(ticker)
                if quote:
                    rows.append({
                        "Ticker": ticker,
                        "Company": quote.get('name', ticker)[:30],
                        "Price": quote.get('price', 0),
                        "Change %": quote.get('changesPercentage', 0),
                        "Market Cap": quote.get('marketCap', 0),
                        "P/E": quote.get('pe', 0)
                    })
        
        if rows:
            df = pd.DataFrame(rows)
            df = df.sort_values('Market Cap', ascending=False)
            
            display_df = df.copy()
            display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
            display_df['Change %'] = display_df['Change %'].apply(lambda x: f"{x:+.2f}%")
            display_df['Market Cap'] = display_df['Market Cap'].apply(format_number)
            display_df['P/E'] = display_df['P/E'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            st.markdown("### 🔍 Analyze a Company")
            col1, col2 = st.columns([3, 1])
            with col1:
                selected = st.selectbox("Choose company:", df['Ticker'].tolist(), 
                                       format_func=lambda x: f"{df[df['Ticker']==x]['Company'].values[0]} ({x})")
            with col2:
                if st.button("Analyze →", type="primary", use_container_width=True):
                    st.session_state.selected_ticker = selected
                    st.rerun()

# ============= TAB 1: COMPANY ANALYSIS =============
with tab1:
    search = st.text_input(
        "🔍 Search by Company Name or Ticker (typos OK!):",
        st.session_state.selected_ticker,
        help="Try: Apple, AAPL, Microsft (typo), etc."
    )
    
    if search:
        ticker, company_name = smart_search_ticker(search)
        st.session_state.selected_ticker = ticker
    else:
        ticker = st.session_state.selected_ticker
    
    profile = get_profile(ticker)
    if profile:
        company_name = profile.get('companyName', ticker)
        st.subheader(f"📈 {company_name} ({ticker})")
        
        # Company description
        description = profile.get('description', '')
        if description:
            with st.expander("ℹ️ What does this company do?"):
                st.write(description[:500] + "..." if len(description) > 500 else description)
        
        sector = profile.get('sector', 'N/A')
        industry = profile.get('industry', 'N/A')
        st.caption(f"**Sector:** {sector} | **Industry:** {industry}")
    else:
        st.subheader(f"{ticker}")
    
    view = st.radio("Choose View:", ["📊 Key Metrics", "📈 Financial Ratios", "💰 Valuation (DCF)", "📰 Latest News"], horizontal=True)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        period_type = st.radio("Time Period:", ["Annual", "Quarterly"])
        period = 'annual' if period_type == "Annual" else 'quarter'
        years = st.slider("Years of History:", 1, 10, 5)
        
        st.divider()
        st.markdown("### 📚 Quick Reference")
        st.info("""
        **FCF After SBC**: #1 metric
        **Gross Margin**: Pricing power
        **P/E Ratio**: Valuation (lower = cheaper)
        **Debt/Equity**: Financial risk
        """)
    
    # Get data
    quote = get_quote(ticker)
    income_df = get_income_statement(ticker, period, years*4 if period == 'quarter' else years)
    cash_df = get_cash_flow(ticker, period, years*4 if period == 'quarter' else years)
    balance_df = get_balance_sheet(ticker, period, years*4 if period == 'quarter' else years)
    ratios_df = get_financial_ratios(ticker, period, years*4 if period == 'quarter' else years)
    
    if quote:
        # Stock chart
        price_data = get_historical_price(ticker, 5)
        if not price_data.empty:
            fig = px.area(price_data, x='date', y='close', title=f'{ticker} Stock Price - Last 5 Years')
            fig.update_layout(height=250, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
        
        # Key stats
        price = quote.get('price', 0)
        change_pct = quote.get('changesPercentage', 0)
        market_cap = quote.get('marketCap', 0)
        pe = quote.get('pe', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"${price:.2f}", f"{change_pct:+.2f}%")
        col2.metric("Market Cap", format_number(market_cap))
        col3.metric("P/E Ratio", f"{pe:.2f}" if pe > 0 else "N/A",
                   help="Price divided by Earnings. Lower = cheaper (usually)")
        
        # Analyst price targets
        price_target = get_price_target(ticker)
        if price_target:
            avg_target = price_target.get('targetConsensus', 0)
            if avg_target > 0:
                upside = ((avg_target - price) / price) * 100
                col4.metric("Analyst Target", f"${avg_target:.2f}", f"{upside:+.1f}% upside",
                           help="Average of all Wall Street analyst price targets")
        
        st.divider()
    
    # ============= VIEW: KEY METRICS =============
    if view == "📊 Key Metrics":
        if not cash_df.empty:
            st.markdown("## 💵 Most Important Metric: FCF After Stock Comp")
            show_why_it_matters('fcfAfterSBC')
            
            # Chart
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
                plot_df.columns = [name_map.get(col, col) for col in plot_df.columns]
                
                fig = px.bar(plot_df, x=plot_df.index, y=plot_df.columns.tolist(), barmode='group',
                           color_discrete_sequence=['#9D4EDD', '#00D9FF'])
                
                max_val = plot_df.max().max()
                min_val = plot_df.min().min()
                y_min = min_val * 1.2 if min_val < 0 else 0
                y_max = max_val * 1.15
                
                fig.update_layout(height=400, yaxis=dict(range=[y_min, y_max]),
                                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig, use_container_width=True)
                
                # Latest values
                if 'fcfAfterSBC' in cash_df.columns:
                    latest = cash_df['fcfAfterSBC'].iloc[-1]
                    col1, col2 = st.columns(2)
                    col1.metric("Latest FCF After SBC", format_number(latest))
                    
                    if latest > 0:
                        col2.success("✅ Positive - Company generating real cash!")
                    else:
                        col2.error("🚨 Negative - Company burning cash!")
        
        st.divider()
        
        # Revenue
        if not income_df.empty and 'revenue' in income_df.columns:
            st.markdown("## 💰 Revenue (Money Coming In)")
            show_why_it_matters('revenue')
            
            plot_df = income_df[['date', 'revenue']].copy()
            plot_df['date'] = plot_df['date'].dt.strftime('%Y')
            plot_df = plot_df.set_index('date')
            
            fig = px.bar(plot_df, x=plot_df.index, y='revenue')
            fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
            
            # Growth rate
            if len(income_df) >= 2:
                first_rev = income_df['revenue'].iloc[0]
                last_rev = income_df['revenue'].iloc[-1]
                years_span = len(income_df) - 1
                cagr = ((last_rev / first_rev) ** (1/years_span) - 1) * 100
                
                col1, col2 = st.columns(2)
                col1.metric("Revenue Growth (CAGR)", f"{cagr:+.1f}%/year")
                
                if cagr > 20:
                    col2.success("🚀 Excellent growth!")
                elif cagr > 10:
                    col2.info("✅ Solid growth")
                else:
                    col2.warning("😴 Slow growth")
    
    # ============= VIEW: RATIOS =============
    elif view == "📈 Financial Ratios":
        st.markdown("## 📊 Profitability Ratios (How Efficient is This Business?)")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 💡 What to Look For:")
            for ratio_name, ratio_exp in RATIO_EXPLANATIONS.items():
                with st.expander(ratio_name):
                    st.write(f"**{ratio_exp['what']}**")
                    st.write(f"✅ {ratio_exp['good']}")
                    st.write(f"🎯 {ratio_exp['targets']}")
        
        with col2:
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
                    plot_df.columns = [ratio_map.get(col, col) for col in plot_df.columns]
                    
                    fig = px.line(plot_df, x=plot_df.index, y=plot_df.columns.tolist(), markers=True)
                    fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                    paper_bgcolor='rgba(0,0,0,0)', font_color='white', yaxis_title="Percentage (%)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Latest values
                    latest = plot_df.iloc[-1]
                    st.markdown("### Latest Margins:")
                    cols = st.columns(len(latest))
                    for i, (name, value) in enumerate(latest.items()):
                        cols[i].metric(name, f"{value:.1f}%")
    
    # ============= VIEW: DCF VALUATION =============
    elif view == "💰 Valuation (DCF)":
        st.markdown("## 💰 DCF Calculator: Is This Stock Cheap or Expensive?")
        st.markdown(DCF_EXPLANATION)
        
        if not cash_df.empty and 'freeCashFlow' in cash_df.columns:
            latest_fcf = cash_df['freeCashFlow'].iloc[-1]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🎛️ Adjust Your Assumptions:")
                growth = st.slider("Expected FCF Growth Rate (%/year)", 0, 50, 10) / 100
                discount = st.slider("Discount Rate (your required return %)", 5, 20, 10) / 100
                years_proj = st.slider("Projection Years", 5, 15, 10)
            
            with col2:
                # Get shares outstanding
                if profile and profile.get('mktCap') and quote:
                    shares = profile.get('mktCap', 0) / quote.get('price', 1) if quote.get('price', 0) > 0 else 1e9
                else:
                    shares = 1e9  # Default 1B shares
                
                fair_value, enterprise_val = calculate_simple_dcf(latest_fcf, growth, discount, years_proj, shares)
                
                st.markdown("### 📊 Valuation Results:")
                st.metric("Current FCF", format_number(latest_fcf))
                st.metric("Calculated Fair Value", f"${fair_value:.2f}/share")
                
                if quote:
                    current_price = quote.get('price', 0)
                    if current_price > 0:
                        upside = ((fair_value - current_price) / current_price) * 100
                        st.metric("Current Price", f"${current_price:.2f}")
                        st.metric("Upside/Downside", f"{upside:+.1f}%")
                        
                        if upside > 20:
                            st.success("✅ Potentially UNDERVALUED!")
                        elif upside < -20:
                            st.error("🚨 Potentially OVERVALUED!")
                        else:
                            st.info("⚖️ Fairly valued")
                
                st.caption("⚠️ DCF is very sensitive to assumptions. Use multiple valuation methods!")
    
    # ============= VIEW: NEWS =============
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
                            st.write(f"**Published:** {date_obj.strftime('%B %d, %Y at %I:%M %p')}")
                        except:
                            st.write(f"**Published:** {pub_date}")
                    
                    summary = article.get('text', 'No summary')
                    st.write(summary[:400] + "..." if len(summary) > 400 else summary)
                    
                    if article.get('url'):
                        st.markdown(f"[📖 Read full article]({article['url']})")
        else:
            st.info("No recent news available.")

st.markdown("---")
st.caption("💰 Finance Made Simple | Powered by FMP API | Data updates in real-time")
