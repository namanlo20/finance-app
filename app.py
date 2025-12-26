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
        "📈 This is the top line - where dreams are made (or crushed)."
    ],
    "NetIncomeLoss": [
        "✅ The moment of truth - are we printing money or burning it?",
        "💸 Bottom line time! This is what's LEFT after everyone gets paid.",
        "🎯 Net income: Where the rubber meets the road and BS meets reality."
    ],
    "OperatingIncomeLoss": [
        "🏭 Core business profit - can they actually run a business or nah?",
        "⚙️ This shows if the business model actually works without accounting tricks.",
        "💼 Operating income: The 'can you walk the walk' metric."
    ],
    "FCF After SBC": [
        "🔥 THE REAL DEAL - this is cash after the Silicon Valley special (stock comp).",
        "💎 Free cash flow after SBC: No lies, no fluff, just COLD HARD CASH.",
        "🚨 This metric doesn't lie. It's cash generation on HARD MODE."
    ],
    "Gross Margin %": [
        "📊 High margins = pricing power = they're not getting squeezed.",
        "💪 Gross margin: Can they charge premium or are they a commodity?",
        "🎨 The art of not being a commodity business, quantified."
    ]
}

METRIC_DEFINITIONS = {
    "Total Revenue": "The total income generated from sales of goods or services before any expenses are deducted.",
    "NetIncomeLoss": "The bottom line profit or loss after all expenses, taxes, and costs are subtracted from revenue.",
    "OperatingIncomeLoss": "Profit from core business operations, excluding taxes and interest.",
    "CostOfRevenue": "Direct costs of producing goods or services sold.",
    "GrossProfit": "Revenue minus Cost of Revenue.",
    "OperatingExpenses": "Costs of running the business like salaries, rent, marketing, and R&D.",
    "ResearchAndDevelopmentExpense": "Money spent on developing new products.",
    "SellingGeneralAndAdministrativeExpense": "Costs for sales teams, marketing, executives, and administrative staff.",
    "Assets": "Everything the company owns.",
    "Liabilities": "Everything the company owes.",
    "StockholdersEquity": "Assets minus Liabilities. The net worth owned by shareholders.",
    "CashAndCashEquivalentsAtCarryingValue": "Liquid cash and short-term investments.",
    "AssetsCurrent": "Assets that can be converted to cash within one year.",
    "LiabilitiesCurrent": "Debts that must be paid within one year.",
    "NetCashProvidedByUsedInOperatingActivities": "Cash generated from normal business operations.",
    "NetCashProvidedByUsedInInvestingActivities": "Cash used for investments in equipment or property.",
    "NetCashProvidedByUsedInFinancingActivities": "Cash from borrowing, repaying debt, or issuing stock.",
    "ShareBasedCompensation": "Non-cash compensation given to employees in the form of stock.",
    "PaymentsToAcquirePropertyPlantAndEquipment": "Capital expenditures on physical assets.",
}

SECTOR_STOCKS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "ADBE", "CRM", "ORCL", "CSCO", "INTC", "AMD", "QCOM"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "ABT", "MRK", "DHR", "LLY", "BMY", "AMGN", "GILD"],
    "Financial": ["JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "SCHW", "AXP", "USB", "PNC", "TFC"],
    "Consumer": ["AMZN", "TSLA", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "TJX", "DG", "COST"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL"],
    "Industrial": ["BA", "CAT", "GE", "HON", "UNP", "UPS", "LMT", "RTX", "DE", "MMM"],
}

def calculate_ratios(df):
    ratios = pd.DataFrame(index=df.index)
    if 'GrossProfit' in df.columns and 'Total Revenue' in df.columns:
        ratios['Gross Margin %'] = (df['GrossProfit'] / df['Total Revenue'] * 100).round(2)
    if 'OperatingIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
        ratios['Operating Margin %'] = (df['OperatingIncomeLoss'] / df['Total Revenue'] * 100).round(2)
    if 'NetIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
        ratios['Net Profit Margin %'] = (df['NetIncomeLoss'] / df['Total Revenue'] * 100).round(2)
    if 'AssetsCurrent' in df.columns and 'LiabilitiesCurrent' in df.columns:
        ratios['Current Ratio'] = (df['AssetsCurrent'] / df['LiabilitiesCurrent']).round(2)
    if 'Liabilities' in df.columns and 'StockholdersEquity' in df.columns:
        ratios['Debt-to-Equity'] = (df['Liabilities'] / df['StockholdersEquity']).round(2)
    if 'Assets' in df.columns and 'StockholdersEquity' in df.columns:
        ratios['Equity Ratio %'] = (df['StockholdersEquity'] / df['Assets'] * 100).round(2)
    if 'NetIncomeLoss' in df.columns and 'Assets' in df.columns:
        ratios['ROA %'] = (df['NetIncomeLoss'] / df['Assets'] * 100).round(2)
    if 'NetIncomeLoss' in df.columns and 'StockholdersEquity' in df.columns:
        ratios['ROE %'] = (df['NetIncomeLoss'] / df['StockholdersEquity'] * 100).round(2)
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
def get_stock_price(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.json()
        quote = data['chart']['result'][0]['meta']
        return {
            'price': quote.get('regularMarketPrice', 0),
            'change': quote.get('regularMarketChange', 0),
            'change_percent': quote.get('regularMarketChangePercent', 0),
            'previous_close': quote.get('previousClose', 0),
            'market_cap': quote.get('marketCap', 0),
            'pe_ratio': quote.get('trailingPE', 0),
            'dividend_yield': quote.get('dividendYield', 0)
        }
    except:
        return None

@st.cache_data(ttl=300)
def get_multiple_stock_prices(tickers):
    results = {}
    for ticker in tickers:
        data = get_stock_price(ticker)
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
        df = pd.DataFrame({'Date': dates, 'Price': prices})
        return df
    except:
        return None

@st.cache_data(ttl=1800)
def get_company_news(ticker):
    try:
        news_list = []
        url1 = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now()-timedelta(days=30)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token=demo"
        response1 = requests.get(url1, timeout=5)
        if response1.status_code == 200:
            news_list.extend(response1.json())
        news_list = sorted(news_list, key=lambda x: x.get('datetime', 0), reverse=True)
        return news_list[:10] if news_list else []
    except:
        return []

@st.cache_data(ttl=3600)
def get_insider_trades(ticker):
    try:
        url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={ticker}&token=demo"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get('data', [])[:10]
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
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    h1, h2, h3 { color: white !important; }
    .stMetric { background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 SEC Terminal Pro: Where Finance Meets Fun")
st.caption("Your no-BS financial analysis platform")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Company Analysis", "🎯 Sector Explorer", "💼 My Portfolio", "🔥 Market Pulse"])

with tab3:
    st.header("💼 My Investment Portfolio")
    st.info("Portfolio tracking coming soon!")
    portfolio_input = st.text_input("Quick add tickers:", placeholder="AAPL, MSFT, GOOGL")
    if portfolio_input:
        tickers = [t.strip().upper() for t in portfolio_input.split(',')]
        st.success(f"Added: {', '.join(tickers)}")

with tab4:
    st.header("🔥 Market Pulse")
    st.info("Real-time market data coming soon!")

with tab2:
    st.header("🎯 Sector Explorer")
    selected_sector = st.selectbox("Select Sector:", list(SECTOR_STOCKS.keys()))
    
    if selected_sector:
        sector_tickers = SECTOR_STOCKS[selected_sector]
        sector_data = get_multiple_stock_prices(sector_tickers)
        
        if sector_data:
            sector_df = pd.DataFrame([
                {
                    "Ticker": ticker,
                    "Price": f"${data['price']:.2f}",
                    "Change %": f"{data['change_percent']:.2f}%",
                    "Market Cap": f"${data.get('market_cap', 0)/1e9:.2f}B" if data.get('market_cap', 0) > 0 else "N/A",
                    "P/E": f"{data.get('pe_ratio', 0):.2f}" if data.get('pe_ratio', 0) > 0 else "N/A"
                }
                for ticker, data in sector_data.items()
            ])
            st.dataframe(sector_df, use_container_width=True, height=600)

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        search_input = st.text_input("🔍 Enter Ticker:", "NVDA").upper()
        if search_input in name_map:
            ticker = name_map[search_input]
            st.success(f"Found: {ticker}")
        elif search_input in ticker_map:
            ticker = search_input
        else:
            ticker = search_input

    with col2:
        view_mode = st.radio("View:", ["Metrics", "Ratios", "Insights", "News"])

    if ticker in ticker_map:
        stock_data = get_stock_price(ticker)
        if stock_data:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Price", f"${stock_data['price']:.2f}", f"{stock_data['change_percent']:.2f}%")
            with col2:
                st.metric("Prev Close", f"${stock_data['previous_close']:.2f}")
            with col3:
                mc = stock_data.get('market_cap', 0)
                st.metric("Market Cap", f"${mc/1e9:.2f}B" if mc > 0 else "N/A")
            with col4:
                pe = stock_data.get('pe_ratio', 0)
                st.metric("P/E", f"{pe:.2f}" if pe > 0 else "N/A")
            
            chart_data = get_stock_chart_data(ticker, '1y')
            if chart_data is not None:
                fig = px.area(chart_data, x='Date', y='Price')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

    with st.sidebar:
        st.header("⚙️ Settings")
        freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
        years_to_show = st.slider("History:", 1, 20, 10)
        target_form = "10-K" if "Annual" in freq else "10-Q"
        quirky_mode = st.toggle("🔥 Unhinged Mode", value=False)
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
                    cashflow_metrics = [m for m in available if m in ['NetCashProvidedByUsedInOperatingActivities', 'NetCashProvidedByUsedInInvestingActivities', 'NetCashProvidedByUsedInFinancingActivities']]
                    
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
                                        
                                        with st.expander("📖 What these mean"):
                                            for metric in selected:
                                                if metric in METRIC_DEFINITIONS:
                                                    st.write(f"**{metric}**: {METRIC_DEFINITIONS[metric]}")
                                        
                                        fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group')
                                        fig.update_layout(height=500)
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        with st.expander("📂 Raw Data"):
                                            formatted = display_df[selected].copy()
                                            for col in formatted.columns:
                                                formatted[col] = formatted[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
                                            st.dataframe(formatted, use_container_width=True)
                
                elif view_mode == "Ratios":
                    ratios_df = calculate_ratios(display_df)
                    if not ratios_df.empty:
                        available_ratios = list(ratios_df.columns)
                        selected_ratios = st.multiselect("Select Ratios:", options=available_ratios, default=available_ratios[:3] if len(available_ratios) >= 3 else available_ratios)
                        if selected_ratios:
                            fig = px.bar(ratios_df, x=ratios_df.index, y=selected_ratios, barmode='group')
                            fig.update_layout(height=500)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            with st.expander("📂 Data"):
                                st.dataframe(ratios_df[selected_ratios], use_container_width=True)
                    else:
                        st.warning("Not enough data for ratios.")
                
                elif view_mode == "Insights":
                    custom_metrics = calculate_custom_metrics(display_df)
                    if not custom_metrics.empty:
                        available_custom = list(custom_metrics.columns)
                        selected_custom = st.multiselect("Key Metrics:", options=available_custom, default=available_custom)
                        if selected_custom:
                            fig = px.bar(custom_metrics, x=custom_metrics.index, y=selected_custom, barmode='group')
                            fig.update_layout(height=500)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            insider_trades = get_insider_trades(ticker)
                            if insider_trades:
                                st.subheader("👔 Insider Trading")
                                insider_df = pd.DataFrame([
                                    {
                                        "Name": t.get('name', 'Unknown'),
                                        "Position": t.get('position', 'N/A'),
                                        "Transaction": t.get('transactionCode', 'N/A'),
                                        "Shares": t.get('share', 0)
                                    }
                                    for t in insider_trades[:5]
                                ])
                                st.dataframe(insider_df, use_container_width=True)
                    else:
                        st.warning("Not enough cash flow data.")
                
                elif view_mode == "News":
                    st.subheader(f"📰 Latest News for {ticker}")
                    news = get_company_news(ticker)
                    if news:
                        for i, article in enumerate(news):
                            with st.expander(f"{i+1}. {article.get('headline', 'No title')[:80]}..."):
                                st.write(f"**Source:** {article.get('source', 'Unknown')}")
                                st.write(f"**Date:** {datetime.fromtimestamp(article.get('datetime', 0)).strftime('%Y-%m-%d %H:%M')}")
                                st.write(article.get('summary', 'No summary')[:300])
                                if article.get('url'):
                                    st.markdown(f"[Read more]({article['url']})")
                    else:
                        st.info("No recent news available.")
                    
                    st.divider()
                    st.subheader("🔔 Price Alerts (Coming Soon)")
                    alert_price = st.number_input(f"Alert me when {ticker} hits:", value=stock_data['price'] if stock_data else 0)
                    if st.button("Set Alert"):
                        st.success(f"Alert set for ${alert_price:.2f}!")
            else:
                st.warning("No data for this timeframe.")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("Enter a valid ticker!")