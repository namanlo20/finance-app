import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

HEADERS = {'User-Agent': "pro_analyst_v6@outlook.com"}

st.set_page_config(page_title="SEC Terminal Pro", layout="wide", page_icon="🚀")

QUIRKY_COMMENTS = {
    "Total Revenue": [
        "💰 The big kahuna! This is how much money is flowing through the door before anyone takes their cut.", 
        "🎰 Revenue baby! Like the casino's total handle before the house takes its share.", 
        "📈 This is the top line - where dreams are made (or crushed).",
        "🚀 Top-line energy! If this ain't growing, nothing else matters.",
        "💸 The money printer goes BRRRR! Or does it?"
    ],
    "NetIncomeLoss": [
        "✅ The moment of truth - are we printing money or burning it?", 
        "💸 Bottom line time! This is what's LEFT after everyone gets paid.", 
        "🎯 Net income: Where the rubber meets the road and BS meets reality.",
        "🔥 This is the 'show me the money' line. Everything above was just foreplay.",
        "💎 If this is red year after year, they're cosplaying as a charity."
    ],
    "OperatingIncomeLoss": [
        "🏭 Core business profit - can they actually run a business or nah?", 
        "⚙️ This shows if the business model actually works without accounting tricks.", 
        "💼 Operating income: The 'can you walk the walk' metric.",
        "🎪 Strip away the financial circus and THIS is what the business actually makes.",
        "💪 This is like asking: if you took away all the fancy stuff, does the core business slap?"
    ],
    "Gross Margin %": [
        "📊 High margins = pricing power = they're not getting squeezed.", 
        "💪 Gross margin: Can they charge premium or are they a commodity?", 
        "🎨 The art of not being a commodity business, quantified.",
        "👑 High margins? They're royalty. Low margins? They're fighting for scraps.",
        "🔥 If this is >60%, they've got a moat. If it's <20%, they're McDonald's (no offense, Ronald)."
    ],
    "Free Cash Flow": [
        "💵 This is ACTUAL cash the business generates after paying the bills and buying stuff.", 
        "🔥 FCF = The cash left over for buybacks, dividends, or world domination.", 
        "💎 If this is negative for years, they're burning through cash like a tech startup in 2021.",
        "🎰 Free Cash Flow: The ONLY metric that doesn't lie. Cash is king, baby.",
        "💰 This is 'can they actually fund themselves?' money. Everything else is accounting theater.",
        "⚡ THE most honest metric. Operating cash minus CapEx = real money they can actually use.",
        "🚨 If this is red, they're bleeding cash. If it's green and growing? Chef's kiss.",
        "💎 This is the 'show me the money' metric. Revenue is vanity, profit is sanity, but cash is REALITY."
    ],
    "ShareBasedCompensation": [
        "🎭 Stock-based comp: AKA 'we're paying people by diluting YOU, the shareholder'",
        "💸 The Silicon Valley special! Employees get rich, shareholders get diluted.",
        "🚨 If this is >20% of revenue, they're basically printing shares like the Fed prints money.",
        "⚠️ High SBC = Your slice of the pie gets smaller every quarter. Math doesn't lie.",
        "🎪 When SBC is massive, the company is a cash piñata for employees, not investors."
    ]
}

METRIC_DEFINITIONS = {
    "Total Revenue": "Total income from sales before expenses.",
    "NetIncomeLoss": "Bottom line profit after all expenses.",
    "OperatingIncomeLoss": "Profit from core operations.",
    "CostOfRevenue": "Direct costs of producing goods/services.",
    "GrossProfit": "Revenue minus Cost of Revenue.",
    "OperatingExpenses": "Business running costs.",
    "NetCashProvidedByUsedInOperatingActivities": "Cash from operations - the lifeblood of a business.",
    "NetCashProvidedByUsedInInvestingActivities": "Cash used for investments in equipment or acquisitions.",
    "NetCashProvidedByUsedInFinancingActivities": "Cash from debt, equity, or buybacks.",
    "ShareBasedCompensation": "Stock-based compensation expense - dilution in disguise.",
    "PaymentsToAcquirePropertyPlantAndEquipment": "Capital expenditures (CapEx) - money spent on assets.",
    "Free Cash Flow": "Operating Cash Flow minus CapEx - cash available for growth or returns. This is the REAL cash the business generates.",
    "Assets": "Total assets - everything the company owns.",
    "Liabilities": "Total liabilities - everything the company owes.",
    "StockholdersEquity": "Shareholders' equity - the net worth owned by shareholders.",
}

SECTOR_STOCKS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "ADBE", "CRM", "ORCL"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "ABT", "MRK", "DHR"],
    "Financial": ["JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "SCHW"],
    "Consumer": ["AMZN", "TSLA", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO"],
    "Industrial": ["BA", "CAT", "GE", "HON", "UNP", "UPS", "LMT", "RTX"],
}

def calculate_ratios(df):
    ratios = pd.DataFrame(index=df.index)
    if 'GrossProfit' in df.columns and 'Total Revenue' in df.columns:
        ratios['Gross Margin %'] = (df['GrossProfit'] / df['Total Revenue'] * 100).round(2)
    if 'OperatingIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
        ratios['Operating Margin %'] = (df['OperatingIncomeLoss'] / df['Total Revenue'] * 100).round(2)
    if 'NetIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
        ratios['Net Profit Margin %'] = (df['NetIncomeLoss'] / df['Total Revenue'] * 100).round(2)
    return ratios

def calculate_fcf_metrics(df):
    fcf_metrics = pd.DataFrame(index=df.index)
    ocf = df.get('NetCashProvidedByUsedInOperatingActivities', pd.Series(dtype=float))
    capex = df.get('PaymentsToAcquirePropertyPlantAndEquipment', pd.Series(dtype=float))
    
    # Simple FCF calculation: Operating Cash Flow - CapEx
    if not ocf.empty and not capex.empty:
        fcf_metrics['Free Cash Flow'] = ocf - capex.abs()
    
    return fcf_metrics

@st.cache_data(ttl=300)
def get_stock_data_yfinance(ticker):
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if info:
            return {
                'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'previous_close': info.get('previousClose', info.get('regularMarketPreviousClose', 0)),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', info.get('forwardPE', 0)),
                'forward_pe': info.get('forwardPE', 0),
            }
    except Exception as e:
        st.sidebar.warning(f"yfinance error: {str(e)}")
    
    try:
        url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey=demo"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data and len(data) > 0:
            item = data[0]
            return {
                'price': item.get('price', 0),
                'change': item.get('change', 0),
                'change_percent': item.get('changesPercentage', 0),
                'previous_close': item.get('previousClose', 0),
                'market_cap': item.get('marketCap', 0),
                'pe_ratio': item.get('pe', 0),
                'forward_pe': 0,
            }
    except Exception as e:
        st.sidebar.error(f"API error: {str(e)}")
    
    return None

@st.cache_data(ttl=300)
def get_multiple_stock_data(tickers):
    results = {}
    for ticker in tickers:
        data = get_stock_data_yfinance(ticker)
        if data:
            results[ticker] = data
    return results

@st.cache_data(ttl=300)
def get_stock_chart_data(ticker, period='1y'):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={period}&interval=1d"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.json()
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        prices = result['indicators']['quote'][0]['close']
        dates = [datetime.fromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps]
        return pd.DataFrame({'Date': dates, 'Price': prices})
    except:
        return None

@st.cache_data(ttl=300)
def calculate_historical_return(ticker, period='5y'):
    try:
        chart_data = get_stock_chart_data(ticker, period)
        if chart_data is not None and not chart_data.empty:
            start_price = chart_data['Price'].iloc[0]
            end_price = chart_data['Price'].iloc[-1]
            return (end_price / start_price) - 1
    except:
        return None

@st.cache_data(ttl=1800)
def get_company_news(ticker):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now()-timedelta(days=30)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token=demo"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            news_list = response.json()
            news_list = sorted(news_list, key=lambda x: x.get('datetime', 0), reverse=True)
            return news_list[:10] if news_list else []
    except:
        return []

@st.cache_data
def get_sec_map():
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    data = r.json()
    ticker_to_cik = {v['ticker']: str(v['cik_str']).zfill(10) for k, v in data.items()}
    name_to_ticker = {v['title'].upper(): v['ticker'] for k, v in data.items()}
    return ticker_to_cik, name_to_ticker

ticker_map, name_map = get_sec_map()

st.markdown("""
<style>
.main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
h1, h2, h3 { color: white !important; }
.stMetric { background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; }
.stTabs [data-baseweb="tab"] { color: white; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 SEC Terminal Pro: Where Finance Meets Fun")
st.caption("Your no-BS financial analysis platform")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Company Analysis", "🎯 Sector Explorer", "💎 My Investment Checklist", "💼 My Portfolio"])

with tab4:
    st.header("💼 My Investment Portfolio")
    st.info("Portfolio tracking coming soon! Track multiple positions, cost basis, and returns all in one place.")

with tab3:
    st.header("💎 My Investment Checklist")
    st.subheader("🔥 The Metrics That Actually Matter")
    st.markdown("""
    ### What I Look For When Investing:
    
    **1. Free Cash Flow**
    - Formula: Operating Cash Flow - CapEx
    - THE most honest metric showing real cash generation
    
    **2. Operating Income**
    - Core business profit before financial engineering
    - Look for consistent growth
    
    **3. Gross Margin %**
    - High margins (>60%) = pricing power
    - Low margins (<20%) = commodity business
    
    **4. Operating Margin %**
    - Target: >20% for software, >10% for others
    
    **5. Revenue Growth**
    - >20% YoY = exciting
    - <5% YoY = struggling
    
    ### 🚨 Red Flags:
    - Declining gross margins
    - Negative FCF for multiple years
    - Stock comp >30% of revenue
    - Revenue growing but cash flow shrinking
    """)

with tab2:
    st.header("🎯 Sector Explorer")
    selected_sector = st.selectbox("Select Sector:", list(SECTOR_STOCKS.keys()))
    if selected_sector:
        with st.spinner(f"Loading {selected_sector} sector data..."):
            sector_tickers = SECTOR_STOCKS[selected_sector]
            sector_data = get_multiple_stock_data(sector_tickers)
            
            if sector_data:
                sector_df = pd.DataFrame([
                    {
                        "Ticker": ticker,
                        "Price": data['price'],
                        "Change %": data['change_percent'],
                        "Market Cap": data.get('market_cap', 0),
                        "P/E Ratio": data.get('pe_ratio', 0),
                        "Forward P/E": data.get('forward_pe', 0),
                    }
                    for ticker, data in sector_data.items()
                ])
                
                sort_by = st.radio("Sort by:", ["Market Cap", "Price", "Change %", "P/E Ratio"], horizontal=True)
                sector_df = sector_df.sort_values(by=sort_by, ascending=False)
                
                display_df = sector_df.copy()
                display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
                display_df['Change %'] = display_df['Change %'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
                display_df['Market Cap'] = display_df['Market Cap'].apply(lambda x: f"${x/1e9:.1f}B" if x > 1e6 else "N/A")
                display_df['P/E Ratio'] = display_df['P/E Ratio'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
                display_df['Forward P/E'] = display_df['Forward P/E'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
                
                st.dataframe(display_df, use_container_width=True, height=600)
            else:
                st.warning("Could not load sector data. Try again in a moment.")

with tab1:
    search_input = st.text_input("🔍 Enter Ticker:", "NVDA").upper()
    if search_input in name_map:
        ticker = name_map[search_input]
        st.success(f"Found: {ticker}")
    elif search_input in ticker_map:
        ticker = search_input
    else:
        ticker = search_input

    view_mode = st.radio("View:", ["Metrics", "Ratios", "Insights", "News"], horizontal=True)

    if ticker in ticker_map:
        stock_data = get_stock_data_yfinance(ticker)
        if stock_data:
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Price", f"${stock_data['price']:.2f}", f"{stock_data['change_percent']:.2f}%")
            col2.metric("Prev Close", f"${stock_data['previous_close']:.2f}")
            
            mc = stock_data.get('market_cap', 0)
            mc_tooltip = "🏢 Market Cap = Stock price × total shares. This is the company's total value. Think of it as the price tag to buy the entire company. Bigger number = bigger company (duh)."
            col3.metric("Market Cap", f"${mc/1e9:.1f}B" if mc > 1e6 else "Calculating...", help=mc_tooltip)
            
            pe = stock_data.get('pe_ratio', 0)
            pe_tooltip = "💵 P/E Ratio = How much you're paying for every $1 of profit. If P/E is 30, you're paying $30 for every $1 the company earns. Lower = cheaper (usually). High P/E? People expect big growth. Low P/E? Either a bargain or trouble."
            col4.metric("P/E Ratio", f"{pe:.2f}" if pe > 0 else "N/A", help=pe_tooltip)
            
            fpe = stock_data.get('forward_pe', 0)
            fpe_tooltip = "🔮 Forward P/E = Same as P/E but based on FUTURE earnings (next 12 months). It's like P/E but with a crystal ball. If Forward P/E < P/E, Wall Street thinks they'll make more money soon. If Forward P/E > P/E, uh oh... earnings might be slowing down."
            col5.metric("Forward P/E", f"{fpe:.2f}" if fpe > 0 else "N/A", help=fpe_tooltip)
            
            st.divider()
            
            # Historical return calculator
            col1, col2 = st.columns([1, 2])
            with col1:
                investment_amount = st.number_input("💰 If I invested:", min_value=1, value=100, step=50)
                time_period = st.selectbox("Time period:", ["1y", "2y", "5y", "10y"], index=2)
            
            with col2:
                historical_return = calculate_historical_return(ticker, time_period)
                if historical_return is not None:
                    future_value = investment_amount * (1 + historical_return)
                    profit = future_value - investment_amount
                    st.success(f"📈 Your ${investment_amount} would be worth **${future_value:.2f}** today!")
                    st.info(f"🎯 Profit: **${profit:.2f}** ({historical_return*100:.1f}% return)")
                else:
                    st.warning("Could not calculate historical returns.")

    with st.sidebar:
        st.header("⚙️ Settings")
        freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
        years_to_show = st.slider("History:", 1, 20, 10)
        target_form = "10-K" if "Annual" in freq else "10-Q"
        
        st.divider()
        st.subheader("📈 Chart Settings")
        chart_timeframe = st.selectbox("Stock Chart Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"], index=3)
        sync_with_financials = st.checkbox("Sync chart with financial history", value=False)
        
        if sync_with_financials:
            if years_to_show <= 1:
                chart_timeframe = "1y"
            elif years_to_show <= 2:
                chart_timeframe = "2y"
            elif years_to_show <= 5:
                chart_timeframe = "5y"
            else:
                chart_timeframe = "10y"
        
        st.divider()
        quirky_mode = st.toggle("🔥 Unhinged Mode", value=False)
        
        st.divider()
        st.markdown("### 💡 Quick Tips")
        st.info("**Free Cash Flow**: Most honest cash metric (Op CF - CapEx)\n\n**Operating Margin**: Pricing power indicator\n\n**SBC**: Watch for excessive dilution")

    if ticker in ticker_map:
        chart_data = get_stock_chart_data(ticker, chart_timeframe)
        if chart_data is not None:
            fig = px.area(chart_data, x='Date', y='Price', title=f'{ticker} Price Chart ({chart_timeframe})')
            fig.update_layout(height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)

    if ticker in ticker_map:
        try:
            cik = ticker_map[ticker]
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            raw_facts = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']
            
            master_dict = {}
            for tag, content in raw_facts.items():
                if 'units' in content and 'USD' in content['units']:
                    df_pts = pd.DataFrame(content['units']['USD'])
                    df_pts = df_pts[df_pts['form'] == target_form]
                    if not df_pts.empty:
                        df_pts['end'] = pd.to_datetime(df_pts['end'])
                        df_pts = df_pts.sort_values(['end', 'filed']).drop_duplicates('end', keep='last')
                        master_dict[tag] = df_pts.set_index('end')['val']
            
            master_df = pd.DataFrame(master_dict).sort_index()
            
            revenue_variants = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]
            found_rev_tags = [t for t in revenue_variants if t in master_df.columns]
            if found_rev_tags:
                master_df["Total Revenue"] = master_df[found_rev_tags].bfill(axis=1).iloc[:, 0]
            
            if 'Total Revenue' in master_df.columns and 'CostOfRevenue' in master_df.columns:
                master_df['GrossProfit'] = master_df['Total Revenue'] - master_df['CostOfRevenue']
            
            cutoff_date = datetime.now() - timedelta(days=years_to_show*365)
            display_df = master_df[master_df.index >= cutoff_date].copy()
            if display_df.empty:
                display_df = master_df.tail(years_to_show if target_form == "10-K" else years_to_show * 4).copy()
            
            if not display_df.empty:
                # NOW convert index to strings for display
                display_df.index = display_df.index.strftime('%Y' if target_form == "10-K" else '%Y-Q%q')
                
                if view_mode == "Metrics":
                    available = list(display_df.columns)
                    income_metrics = [m for m in available if m in ['Total Revenue', 'NetIncomeLoss', 'OperatingIncomeLoss', 'GrossProfit', 'CostOfRevenue', 'OperatingExpenses']]
                    balance_metrics = [m for m in available if m in ['Assets', 'Liabilities', 'StockholdersEquity', 'AssetsCurrent', 'LiabilitiesCurrent']]
                    cashflow_metrics = [m for m in available if m in ['NetCashProvidedByUsedInOperatingActivities', 'NetCashProvidedByUsedInInvestingActivities', 'NetCashProvidedByUsedInFinancingActivities', 'ShareBasedCompensation', 'PaymentsToAcquirePropertyPlantAndEquipment']]
                    
                    # Always include Free Cash Flow as an option (we calculate it on the fly)
                    fcf_metrics = ['Free Cash Flow']
                    
                    # === CASH FLOW FIRST (TOP) ===
                    col_left, col_right = st.columns([1, 3])
                    with col_left:
                        st.subheader("💧 Statement of Cash Flows")
                        default_cf = [m for m in ['Free Cash Flow', 'ShareBasedCompensation'] if m in cashflow_metrics or m in fcf_metrics]
                        cashflow_selected = st.multiselect("Select metrics:", options=cashflow_metrics + fcf_metrics, default=default_cf, key="cf")
                    
                    with col_right:
                        st.markdown("### 💧 Statement of Cash Flows")
                        if cashflow_selected:
                            if quirky_mode:
                                for metric in cashflow_selected:
                                    if metric in QUIRKY_COMMENTS:
                                        st.info(random.choice(QUIRKY_COMMENTS[metric]))
                            
                            # Build cf_df with selected metrics
                            cf_df = pd.DataFrame(index=display_df.index)
                            
                            for metric in cashflow_selected:
                                if metric == 'Free Cash Flow':
                                    # Calculate FCF on the fly: OCF - CapEx
                                    if 'NetCashProvidedByUsedInOperatingActivities' in display_df.columns and 'PaymentsToAcquirePropertyPlantAndEquipment' in display_df.columns:
                                        ocf = display_df['NetCashProvidedByUsedInOperatingActivities']
                                        capex = display_df['PaymentsToAcquirePropertyPlantAndEquipment']
                                        cf_df['Free Cash Flow'] = ocf - capex.abs()
                                elif metric in display_df.columns:
                                    cf_df[metric] = display_df[metric]
                            
                            # Only plot metrics that have data
                            metrics_with_data = [m for m in cf_df.columns if not cf_df[m].isna().all()]
                            
                            if metrics_with_data:
                                # Use distinct colors for FCF vs SBC
                                color_map = {
                                    'Free Cash Flow': '#00D9FF',  # Bright cyan
                                    'ShareBasedCompensation': '#FF6B9D',  # Pink
                                }
                                colors = [color_map.get(m, '#FFC837') for m in metrics_with_data]
                                
                                fig = px.bar(cf_df[metrics_with_data], x=cf_df.index, y=metrics_with_data, barmode='group', 
                                           color_discrete_sequence=colors)
                                max_val = cf_df[metrics_with_data].max().max()
                                min_val = cf_df[metrics_with_data].min().min()
                                y_range = [min_val * 1.1 if min_val < 0 else 0, max_val * 1.15]
                                fig.update_layout(height=400, yaxis=dict(range=y_range), plot_bgcolor='rgba(0,0,0,0)', 
                                                paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=True)
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Show definitions right below the chart
                                with st.expander("📖 Metric Definitions"):
                                    for metric in metrics_with_data:
                                        if metric in METRIC_DEFINITIONS:
                                            st.write(f"**{metric}**: {METRIC_DEFINITIONS[metric]}")
                            else:
                                st.warning("No data available for selected metrics.")
                    
                    st.divider()
                    
                    # === INCOME STATEMENT SECOND (MIDDLE) ===
                    col_left, col_right = st.columns([1, 3])
                    with col_left:
                        st.subheader("💵 Income Statement")
                        default_income = [m for m in ['Total Revenue', 'OperatingIncomeLoss', 'NetIncomeLoss'] if m in income_metrics]
                        income_selected = st.multiselect("Select metrics:", options=income_metrics, default=default_income, key="income")
                    
                    with col_right:
                        st.markdown("### 💵 Income Statement")
                        if income_selected:
                            if quirky_mode:
                                for metric in income_selected:
                                    if metric in QUIRKY_COMMENTS:
                                        st.info(random.choice(QUIRKY_COMMENTS[metric]))
                            
                            fig = px.bar(display_df, x=display_df.index, y=income_selected, barmode='group', color_discrete_sequence=px.colors.qualitative.Bold)
                            max_val = display_df[income_selected].max().max()
                            min_val = display_df[income_selected].min().min()
                            y_range = [min_val * 1.1 if min_val < 0 else 0, max_val * 1.15]
                            fig.update_layout(height=400, yaxis=dict(range=y_range), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=True)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show definitions in expander below the chart
                            with st.expander("📖 Metric Definitions"):
                                for metric in income_selected:
                                    if metric in METRIC_DEFINITIONS:
                                        st.write(f"**{metric}**: {METRIC_DEFINITIONS[metric]}")
                    
                    st.divider()
                    
                    # === BALANCE SHEET LAST (BOTTOM) ===
                    col_left, col_right = st.columns([1, 3])
                    with col_left:
                        st.subheader("🏦 Balance Sheet")
                        default_balance = [m for m in ['Assets', 'StockholdersEquity', 'Liabilities'] if m in balance_metrics]
                        balance_selected = st.multiselect("Select metrics:", options=balance_metrics, default=default_balance, key="balance")
                    
                    with col_right:
                        st.markdown("### 🏦 Balance Sheet")
                        if balance_selected:
                            if quirky_mode:
                                for metric in balance_selected:
                                    if metric in QUIRKY_COMMENTS:
                                        st.info(random.choice(QUIRKY_COMMENTS[metric]))
                            
                            fig = px.bar(display_df, x=display_df.index, y=balance_selected, barmode='group', color_discrete_sequence=px.colors.qualitative.Set2)
                            max_val = display_df[balance_selected].max().max()
                            min_val = display_df[balance_selected].min().min()
                            y_range = [min_val * 1.1 if min_val < 0 else 0, max_val * 1.15]
                            fig.update_layout(height=400, yaxis=dict(range=y_range), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=True)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show definitions in expander below the chart
                            with st.expander("📖 Metric Definitions"):
                                for metric in balance_selected:
                                    if metric in METRIC_DEFINITIONS:
                                        st.write(f"**{metric}**: {METRIC_DEFINITIONS[metric]}")
                    
                    with st.expander("📂 Raw Data"):
                        all_selected = income_selected + balance_selected + cashflow_selected
                        if all_selected:
                            formatted = display_df[[m for m in all_selected if m in display_df.columns]].copy()
                            for col in formatted.columns:
                                formatted[col] = formatted[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
                            st.dataframe(formatted, use_container_width=True)
                
                elif view_mode == "Ratios":
                    ratios_df = calculate_ratios(display_df)
                    if not ratios_df.empty:
                        available_ratios = list(ratios_df.columns)
                        selected_ratios = st.multiselect("Select Ratios:", options=available_ratios, default=available_ratios[:3] if len(available_ratios) >= 3 else available_ratios)
                        if selected_ratios:
                            fig = px.bar(ratios_df, x=ratios_df.index, y=selected_ratios, barmode='group', color_discrete_sequence=px.colors.qualitative.Pastel)
                            max_val = ratios_df[selected_ratios].max().max()
                            fig.update_layout(height=500, yaxis=dict(range=[0, max_val * 1.15]), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                            st.plotly_chart(fig, use_container_width=True)
                            
                            with st.expander("📂 Data Table"):
                                st.dataframe(ratios_df[selected_ratios], use_container_width=True)
                    else:
                        st.warning("Not enough data for ratios.")
                
                elif view_mode == "Insights":
                    fcf_df = calculate_fcf_metrics(display_df)
                    if not fcf_df.empty:
                        st.subheader("💎 Key Investment Metrics")
                        available_fcf = list(fcf_df.columns)
                        
                        if 'OperatingIncomeLoss' in display_df.columns:
                            available_fcf.append('OperatingIncomeLoss')
                        
                        selected_insights = st.multiselect("Critical Metrics:", options=available_fcf, default=available_fcf[:2] if len(available_fcf) >= 2 else available_fcf)
                        
                        if selected_insights:
                            plot_df = pd.DataFrame(index=display_df.index)
                            for metric in selected_insights:
                                if metric in fcf_df.columns:
                                    plot_df[metric] = fcf_df[metric]
                                elif metric in display_df.columns:
                                    plot_df[metric] = display_df[metric]
                            
                            fig = px.bar(plot_df, x=plot_df.index, y=selected_insights, barmode='group', color_discrete_sequence=['#00D9FF', '#FF6B9D', '#FFC837'])
                            max_val = plot_df[selected_insights].max().max()
                            min_val = plot_df[selected_insights].min().min()
                            y_range = [min_val * 1.1 if min_val < 0 else 0, max_val * 1.15]
                            
                            fig.update_layout(height=500, yaxis=dict(range=y_range), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                            st.plotly_chart(fig, use_container_width=True)
                            
                            if 'Free Cash Flow' in fcf_df.columns:
                                latest_fcf = fcf_df['Free Cash Flow'].iloc[-1]
                                if len(fcf_df) > 1:
                                    prev_fcf = fcf_df['Free Cash Flow'].iloc[-2]
                                    growth = ((latest_fcf - prev_fcf) / abs(prev_fcf) * 100) if prev_fcf != 0 else 0
                                    
                                    col1, col2 = st.columns(2)
                                    col1.metric("Latest Free Cash Flow", f"${latest_fcf/1e9:.2f}B", f"{growth:+.1f}%")
                                    
                                    if latest_fcf > 0:
                                        col2.success("✅ Positive free cash flow!")
                                    else:
                                        col2.error("🚨 Negative free cash flow!")
                    else:
                        st.warning("Not enough cash flow data. Company must report Operating Cash Flow and CapEx.")
                
                elif view_mode == "News":
                    st.subheader(f"📰 Latest News for {ticker}")
                    news = get_company_news(ticker)
                    if news:
                        for i, article in enumerate(news):
                            with st.expander(f"{i+1}. {article.get('headline', 'No title')[:80]}..."):
                                st.write(f"**Source:** {article.get('source', 'Unknown')}")
                                st.write(f"**Date:** {datetime.fromtimestamp(article.get('datetime', 0)).strftime('%Y-%m-%d')}")
                                st.write(article.get('summary', 'No summary')[:300])
                                if article.get('url'):
                                    st.markdown(f"[Read more]({article['url']})")
                    else:
                        st.info("No recent news available.")
            else:
                st.warning("No data for this timeframe.")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("Enter a valid ticker!")