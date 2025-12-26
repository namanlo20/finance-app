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
</style>
""", unsafe_allow_html=True)

st.title("🚀 SEC Terminal Pro: Where Finance Meets Fun")
st.caption("Your no-BS financial analysis platform")

tab1, tab2, tab3 = st.tabs(["📊 Company Analysis", "🎯 Sector Explorer", "💼 My Portfolio"])

with tab3:
    st.header("💼 My Investment Portfolio")
    st.info("Portfolio tracking coming soon!")

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
                }
                for ticker, data in sector_data.items()
            ])
            st.dataframe(sector_df, use_container_width=True, height=600)

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
        stock_data = get_stock_price(ticker)
        if stock_data:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Price", f"${stock_data['price']:.2f}", f"{stock_data['change_percent']:.2f}%")
            col2.metric("Prev Close", f"${stock_data['previous_close']:.2f}")
            mc = stock_data.get('market_cap', 0)
            col3.metric("Market Cap", f"${mc/1e9:.2f}B" if mc > 0 else "N/A")
            pe = stock_data.get('pe_ratio', 0)
            col4.metric("P/E", f"{pe:.2f}" if pe > 0 else "N/A")
            
            chart_data = get_stock_chart_data(ticker, '1y')
            if chart_data is not None:
                fig = px.area(chart_data, x='Date', y='Price', title=f'{ticker} Price Chart')
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
                        
                        with st.expander("📖 Definitions"):
                            for metric in selected:
                                if metric in METRIC_DEFINITIONS:
                                    st.write(f"**{metric}**: {METRIC_DEFINITIONS[metric]}")
                        
                        fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group')
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                
                elif view_mode == "Ratios":
                    ratios_df = calculate_ratios(display_df)
                    if not ratios_df.empty:
                        available_ratios = list(ratios_df.columns)
                        selected_ratios = st.multiselect("Select Ratios:", options=available_ratios, default=available_ratios[:3] if len(available_ratios) >= 3 else available_ratios)
                        if selected_ratios:
                            fig = px.bar(ratios_df, x=ratios_df.index, y=selected_ratios, barmode='group')
                            fig.update_layout(height=500)
                            st.plotly_chart(fig, use_container_width=True)
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
                    else:
                        st.warning("Not enough cash flow data.")
                
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