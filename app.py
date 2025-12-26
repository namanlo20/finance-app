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
    "Total Revenue": ["💰 The big kahuna!", "🎰 Revenue baby!", "📈 Top line dreams!"],
    "NetIncomeLoss": ["✅ Money printer or dumpster fire?", "💸 Bottom line truth!", "🎯 Reality check!"],
    "OperatingIncomeLoss": ["🏭 Can they run a business?", "⚙️ No accounting tricks here!", "💼 Walking the walk!"],
    "Gross Margin %": ["📊 High margins = pricing power!", "💪 Premium or commodity?", "🎨 Not a commodity!"]
}

METRIC_DEFINITIONS = {
    "Total Revenue": "Total income from sales before expenses.",
    "NetIncomeLoss": "Bottom line profit after all expenses.",
    "OperatingIncomeLoss": "Profit from core operations.",
    "CostOfRevenue": "Direct costs of producing goods/services.",
    "GrossProfit": "Revenue minus Cost of Revenue.",
    "OperatingExpenses": "Business running costs.",
    "NetCashProvidedByUsedInOperatingActivities": "Cash from operations.",
    "NetCashProvidedByUsedInInvestingActivities": "Cash used for investments.",
    "NetCashProvidedByUsedInFinancingActivities": "Cash from financing activities.",
    "ShareBasedCompensation": "Stock-based compensation expense.",
    "PaymentsToAcquirePropertyPlantAndEquipment": "Capital expenditures (CapEx).",
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

def calculate_custom_metrics(df):
    custom = pd.DataFrame(index=df.index)
    ocf = df.get('NetCashProvidedByUsedInOperatingActivities', pd.Series(dtype=float))
    sbc = df.get('ShareBasedCompensation', pd.Series(dtype=float))
    capex = df.get('PaymentsToAcquirePropertyPlantAndEquipment', pd.Series(dtype=float))
    if not ocf.empty:
        custom['Operating Cash Flow'] = ocf
    if not ocf.empty and not capex.empty:
        custom['Free Cash Flow'] = ocf - capex.abs()
    if not ocf.empty and not sbc.empty and not capex.empty:
        custom['FCF After SBC'] = ocf - sbc - capex.abs()
    return custom

@st.cache_data(ttl=300)
def get_stock_quote(ticker):
    try:
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=price,summaryDetail,defaultKeyStatistics"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.json()
        
        price_data = data['quoteSummary']['result'][0]['price']
        summary = data['quoteSummary']['result'][0].get('summaryDetail', {})
        stats = data['quoteSummary']['result'][0].get('defaultKeyStatistics', {})
        
        market_cap = price_data.get('marketCap', {}).get('raw', 0)
        shares = stats.get('sharesOutstanding', {}).get('raw', 0)
        
        return {
            'price': price_data.get('regularMarketPrice', {}).get('raw', 0),
            'change': price_data.get('regularMarketChange', {}).get('raw', 0),
            'change_percent': price_data.get('regularMarketChangePercent', {}).get('raw', 0),
            'previous_close': price_data.get('regularMarketPreviousClose', {}).get('raw', 0),
            'market_cap': market_cap if market_cap > 0 else (shares * price_data.get('regularMarketPrice', {}).get('raw', 0)),
            'pe_ratio': summary.get('trailingPE', {}).get('raw', 0),
            'forward_pe': summary.get('forwardPE', {}).get('raw', 0),
        }
    except Exception as e:
        st.warning(f"Could not fetch full data for {ticker}: {e}")
        return None

@st.cache_data(ttl=300)
def get_multiple_stock_quotes(tickers):
    results = {}
    for ticker in tickers:
        data = get_stock_quote(ticker)
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
    
    **1. Free Cash Flow After SBC (Stock-Based Compensation)**
    - This is THE most honest metric. It shows real cash generation after accounting for dilution.
    - Formula: Operating Cash Flow - Stock-Based Comp - CapEx
    - Why: Tech companies love to hide dilution. This metric doesn't let them.
    
    **2. Operating Income**
    - Shows if the core business actually makes money.
    - Strips out financial engineering and one-time items.
    - Look for consistent growth, not volatility.
    
    **3. Gross Margin %**
    - High margins (>60%) = pricing power and moat
    - Low margins (<20%) = commodity business getting squeezed
    - Expanding margins = getting better with scale
    
    **4. Operating Margin %**
    - After all operating expenses, what's left?
    - Target: >20% for software, >10% for most others
    - Trend matters more than absolute number
    
    **5. Revenue Growth Rate**
    - Growing >20% YoY = exciting
    - Growing <5% YoY = mature/struggling
    - Decelerating growth = red flag
    
    **6. Current Ratio**
    - Can they pay bills? Above 1.5 is healthy.
    - Below 1.0 = potential liquidity crisis
    
    **7. Debt-to-Equity**
    - Lower is safer (generally <0.5 for tech)
    - High debt in downturns = danger zone
    
    ### 🚨 Red Flags I Always Check:
    - Declining gross margins (losing pricing power)
    - Negative free cash flow for multiple years
    - Stock-based comp >30% of revenue (massive dilution)
    - Revenue growing but cash flow shrinking (fake growth)
    - High debt + low margins (death spiral potential)
    
    ### 💡 Pro Tip:
    Use the "Insights" tab to quickly see FCF After SBC trends. If it's consistently negative or declining while revenue grows, that's a major red flag! 🚩
    """)

with tab2:
    st.header("🎯 Sector Explorer")
    selected_sector = st.selectbox("Select Sector:", list(SECTOR_STOCKS.keys()))
    if selected_sector:
        with st.spinner(f"Loading {selected_sector} sector data..."):
            sector_tickers = SECTOR_STOCKS[selected_sector]
            sector_data = get_multiple_stock_quotes(sector_tickers)
            
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
                display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
                display_df['Change %'] = display_df['Change %'].apply(lambda x: f"{x:.2f}%")
                display_df['Market Cap'] = display_df['Market Cap'].apply(lambda x: f"${x/1e9:.2f}B" if x > 0 else "N/A")
                display_df['P/E Ratio'] = display_df['P/E Ratio'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
                display_df['Forward P/E'] = display_df['Forward P/E'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
                
                st.dataframe(display_df, use_container_width=True, height=600)

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
        stock_data = get_stock_quote(ticker)
        if stock_data:
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Price", f"${stock_data['price']:.2f}", f"{stock_data['change_percent']:.2f}%")
            col2.metric("Prev Close", f"${stock_data['previous_close']:.2f}")
            mc = stock_data.get('market_cap', 0)
            col3.metric("Market Cap", f"${mc/1e9:.1f}B" if mc > 0 else "N/A")
            pe = stock_data.get('pe_ratio', 0)
            col4.metric("P/E Ratio", f"{pe:.2f}" if pe > 0 else "N/A")
            fpe = stock_data.get('forward_pe', 0)
            col5.metric("Forward P/E", f"{fpe:.2f}" if fpe > 0 else "N/A")
            
            chart_data = get_stock_chart_data(ticker, '1y')
            if chart_data is not None:
                fig = px.area(chart_data, x='Date', y='Price', title=f'{ticker} Price Chart (1 Year)')
                fig.update_layout(height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig, use_container_width=True)

    with st.sidebar:
        st.header("⚙️ Settings")
        freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
        years_to_show = st.slider("History:", 1, 20, 10)
        target_form = "10-K" if "Annual" in freq else "10-Q"
        quirky_mode = st.toggle("🔥 Unhinged Mode", value=False)
        
        st.divider()
        st.markdown("### 💡 Quick Tips")
        st.info("**FCF After SBC**: Most honest cash metric\n\n**Operating Margin**: Pricing power indicator\n\n**Current Ratio**: Liquidity health check")

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
                display_df.index = display_df.index.strftime('%Y' if target_form == "10-K" else '%Y-Q%q')
                
                if view_mode == "Metrics":
                    available = list(display_df.columns)
                    income_metrics = [m for m in available if m in ['Total Revenue', 'NetIncomeLoss', 'OperatingIncomeLoss', 'GrossProfit', 'CostOfRevenue', 'OperatingExpenses']]
                    cashflow_metrics = [m for m in available if m in ['NetCashProvidedByUsedInOperatingActivities', 'NetCashProvidedByUsedInInvestingActivities', 'NetCashProvidedByUsedInFinancingActivities', 'ShareBasedCompensation', 'PaymentsToAcquirePropertyPlantAndEquipment']]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        income_selected = st.multiselect("Income Statement:", options=income_metrics, default=income_metrics[:3] if len(income_metrics) >= 3 else income_metrics)
                    with col2:
                        cashflow_selected = st.multiselect("Cash Flow:", options=cashflow_metrics, default=[])
                    
                    selected = income_selected + cashflow_selected
                    
                    if selected:
                        if quirky_mode:
                            for metric in selected:
                                if metric in QUIRKY_COMMENTS:
                                    st.info(random.choice(QUIRKY_COMMENTS[metric]))
                        
                        with st.expander("📖 Definitions"):
                            for metric in selected:
                                if metric in METRIC_DEFINITIONS:
                                    st.write(f"**{metric}**: {METRIC_DEFINITIONS[metric]}")
                        
                        fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group')
                        max_val = display_df[selected].max().max()
                        fig.update_layout(
                            height=500,
                            yaxis=dict(range=[0, max_val * 1.15]),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                elif view_mode == "Ratios":
                    ratios_df = calculate_ratios(display_df)
                    if not ratios_df.empty:
                        available_ratios = list(ratios_df.columns)
                        selected_ratios = st.multiselect("Select Ratios:", options=available_ratios, default=available_ratios[:3] if len(available_ratios) >= 3 else available_ratios)
                        if selected_ratios:
                            fig = px.bar(ratios_df, x=ratios_df.index, y=selected_ratios, barmode='group')
                            max_val = ratios_df[selected_ratios].max().max()
                            fig.update_layout(
                                height=500,
                                yaxis=dict(range=[0, max_val * 1.15]),
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Not enough data for ratios.")
                
                elif view_mode == "Insights":
                    custom_metrics = calculate_custom_metrics(display_df)
                    if not custom_metrics.empty:
                        st.subheader("💎 Key Investment Metrics")
                        available_custom = list(custom_metrics.columns)
                        selected_custom = st.multiselect("Critical Metrics:", options=available_custom, default=available_custom)
                        if selected_custom:
                            fig = px.bar(custom_metrics, x=custom_metrics.index, y=selected_custom, barmode='group', color_discrete_sequence=['#00D9FF', '#FF6B9D', '#FFC837'])
                            max_val = custom_metrics[selected_custom].max().max()
                            fig.update_layout(
                                height=500,
                                yaxis=dict(range=[0, max_val * 1.15]),
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            if 'FCF After SBC' in custom_metrics.columns:
                                latest_fcf = custom_metrics['FCF After SBC'].iloc[-1]
                                if len(custom_metrics) > 1:
                                    prev_fcf = custom_metrics['FCF After SBC'].iloc[-2]
                                    growth = ((latest_fcf - prev_fcf) / abs(prev_fcf) * 100) if prev_fcf != 0 else 0
                                    
                                    col1, col2 = st.columns(2)
                                    col1.metric("Latest FCF After SBC", f"${latest_fcf/1e9:.2f}B", f"{growth:+.1f}%")
                                    
                                    if latest_fcf > 0:
                                        col2.success("✅ Positive free cash flow after dilution!")
                                    else:
                                        col2.error("🚨 Negative free cash flow - burning cash!")
                    else:
                        st.warning("Not enough cash flow data available.")
                
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