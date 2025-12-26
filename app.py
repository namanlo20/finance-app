import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.write("VERSION 2.0 - Updated with stock price and news")
HEADERS = {'User-Agent': "pro_analyst_v6@outlook.com"}

st.set_page_config(page_title="SEC Terminal Pro", layout="wide")

METRIC_DEFINITIONS = {
    "Total Revenue": "The total income generated from sales of goods or services before any expenses are deducted. This is the top line of the income statement.",
    "NetIncomeLoss": "The bottom line profit or loss after all expenses, taxes, and costs are subtracted from revenue. This shows actual profitability.",
    "OperatingIncomeLoss": "Profit from core business operations, excluding taxes and interest. Shows how profitable the main business activities are.",
    "CostOfRevenue": "Direct costs of producing goods or services sold. Includes materials, labor, and manufacturing costs.",
    "GrossProfit": "Revenue minus Cost of Revenue. Shows profit before operating expenses are deducted.",
    "OperatingExpenses": "Costs of running the business like salaries, rent, marketing, and R&D. Does not include COGS.",
    "ResearchAndDevelopmentExpense": "Money spent on developing new products and improving existing ones. Critical for tech companies.",
    "SellingGeneralAndAdministrativeExpense": "Costs for sales teams, marketing, executives, legal, and administrative staff.",
    "Assets": "Everything the company owns: cash, inventory, property, equipment, and investments.",
    "Liabilities": "Everything the company owes: loans, accounts payable, and other debts.",
    "StockholdersEquity": "Assets minus Liabilities. The net worth owned by shareholders.",
    "CashAndCashEquivalentsAtCarryingValue": "Liquid cash and short-term investments that can be quickly converted to cash.",
    "AssetsCurrent": "Assets that can be converted to cash within one year like cash, inventory, and receivables.",
    "LiabilitiesCurrent": "Debts that must be paid within one year.",
    "NetCashProvidedByUsedInOperatingActivities": "Cash generated from normal business operations. Shows if the business generates cash.",
    "NetCashProvidedByUsedInInvestingActivities": "Cash used for investments in equipment, property, or other companies.",
    "NetCashProvidedByUsedInFinancingActivities": "Cash from borrowing, repaying debt, or issuing and buying back stock.",
    "ShareBasedCompensation": "Non-cash compensation given to employees in the form of stock or options. Important for calculating true free cash flow.",
    "PaymentsToAcquirePropertyPlantAndEquipment": "Capital expenditures - money spent on physical assets like buildings, equipment, and technology.",
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

RATIO_DEFINITIONS = {
    "Gross Margin %": "Gross Profit divided by Revenue times 100. Shows what percent of revenue remains after production costs. Higher is better.",
    "Operating Margin %": "Operating Income divided by Revenue times 100. Shows profitability from core operations. Higher indicates efficiency.",
    "Net Profit Margin %": "Net Income divided by Revenue times 100. The ultimate profitability metric showing what percent of revenue becomes profit.",
    "Current Ratio": "Current Assets divided by Current Liabilities. Measures ability to pay short-term debts. Above 1.0 is good, above 2.0 is strong.",
    "Debt-to-Equity": "Total Liabilities divided by Stockholders Equity. Shows financial leverage. Lower is generally safer.",
    "Equity Ratio %": "Equity divided by Assets times 100. Shows what percent of assets are owned outright versus financed by debt.",
    "ROA %": "Net Income divided by Total Assets times 100. Shows how efficiently assets generate profit.",
    "ROE %": "Net Income divided by Equity times 100. Return generated on shareholders investment. Key metric for investors.",
}

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
            'previous_close': quote.get('previousClose', 0)
        }
    except:
        return None

@st.cache_data(ttl=3600)
def get_company_news(ticker):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token=demo"
        response = requests.get(url)
        news = response.json()
        return news[:5] if news else []
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

st.title("SEC History: The Unbroken Revenue Build")
st.caption("Your one-stop shop for financial data - built for beginners")

col1, col2 = st.columns([3, 1])
with col1:
    search_input = st.text_input("Enter Ticker or Company Name:", "NVDA").upper()
    if search_input in name_map:
        ticker = name_map[search_input]
        st.success(f"Found: {search_input} -> Ticker: {ticker}")
    elif search_input in ticker_map:
        ticker = search_input
    else:
        matches = [name for name in name_map.keys() if search_input in name]
        if matches:
            st.warning(f"Did you mean? {', '.join(matches[:5])}")
        ticker = search_input

with col2:
    view_mode = st.radio("View:", ["Metrics", "Ratios", "Key Insights"], label_visibility="collapsed")

if ticker in ticker_map:
    stock_data = get_stock_price(ticker)
    if stock_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"${stock_data['price']:.2f}", 
                     f"{stock_data['change']:.2f} ({stock_data['change_percent']:.2f}%)")
        with col2:
            st.metric("Previous Close", f"${stock_data['previous_close']:.2f}")
        with col3:
            news = get_company_news(ticker)
            st.metric("Recent News", f"{len(news)} articles")
        with col4:
            st.metric("Data Source", "SEC EDGAR")

with st.sidebar:
    st.header("Terminal Settings")
    freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
    years_to_show = st.slider("History Length (Years):", 1, 20, 10)
    target_form = "10-K" if "Annual" in freq else "10-Q"
    
    st.divider()
    st.subheader("Key Metrics to Watch")
    st.info("These metrics give you the clearest picture of a company's financial health:")
    st.write("**Free Cash Flow After SBC**: Operating cash flow minus stock-based compensation and capital expenditures. Shows true cash generation.")
    st.write("**Operating Income**: Profit from core business before interest and taxes. Best measure of operational efficiency.")
    st.write("**Operating Margin %**: Operating income as a percentage of revenue. Higher is better.")
    
    st.divider()
    st.subheader("About This Tool")
    st.info("This terminal pulls data directly from SEC EDGAR filings. Select metrics to visualize financial performance over time.")

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
        
        revenue_variants = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "SalesRevenueGoodsNet", "RevenueFromContractWithCustomerIncludingAssessedTax"]
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
                income_metrics = [m for m in available if m in ['Total Revenue', 'NetIncomeLoss', 'OperatingIncomeLoss', 'GrossProfit', 'CostOfRevenue', 'OperatingExpenses', 'ResearchAndDevelopmentExpense', 'SellingGeneralAndAdministrativeExpense']]
                balance_metrics = [m for m in available if m in ['Assets', 'Liabilities', 'StockholdersEquity', 'AssetsCurrent', 'LiabilitiesCurrent', 'CashAndCashEquivalentsAtCarryingValue']]
                cashflow_metrics = [m for m in available if m in ['NetCashProvidedByUsedInOperatingActivities', 'NetCashProvidedByUsedInInvestingActivities', 'NetCashProvidedByUsedInFinancingActivities', 'ShareBasedCompensation', 'PaymentsToAcquirePropertyPlantAndEquipment']]
                
                st.subheader(f"{ticker} Financial Performance")
                col1, col2, col3 = st.columns(3)
                with col1:
                    income_selected = st.multiselect("Income Statement:", options=income_metrics, default=[m for m in ['Total Revenue', 'NetIncomeLoss', 'OperatingIncomeLoss'] if m in income_metrics])
                with col2:
                    balance_selected = st.multiselect("Balance Sheet:", options=balance_metrics, default=[])
                with col3:
                    cashflow_selected = st.multiselect("Cash Flow Statement:", options=cashflow_metrics, default=[])
                
                selected = income_selected + balance_selected + cashflow_selected
                
                if selected:
                    with st.expander("What do these metrics mean?", expanded=True):
                        for metric in selected:
                            if metric in METRIC_DEFINITIONS:
                                st.write(f"**{metric}**: {METRIC_DEFINITIONS[metric]}")
                    
                    fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group', color_discrete_sequence=px.colors.qualitative.Bold)
                    fig.update_layout(xaxis=dict(type='category', title="Fiscal Period"), yaxis=dict(title="USD"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=500)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander("Raw Data Table"):
                        formatted = display_df[selected].copy()
                        for col in formatted.columns:
                            formatted[col] = formatted[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
                        st.dataframe(formatted, use_container_width=True)
            
            elif view_mode == "Ratios":
                ratios_df = calculate_ratios(display_df)
                if not ratios_df.empty:
                    st.subheader(f"{ticker} Financial Ratios")
                    available_ratios = list(ratios_df.columns)
                    selected_ratios = st.multiselect("Select Financial Ratios:", options=available_ratios, default=available_ratios[:3] if len(available_ratios) >= 3 else available_ratios)
                    if selected_ratios:
                        with st.expander("Understanding these ratios", expanded=True):
                            for ratio in selected_ratios:
                                if ratio in RATIO_DEFINITIONS:
                                    st.write(f"**{ratio}**: {RATIO_DEFINITIONS[ratio]}")
                        fig = go.Figure()
                        for ratio in selected_ratios:
                            fig.add_trace(go.Scatter(x=ratios_df.index, y=ratios_df[ratio], mode='lines+markers', name=ratio, line=dict(width=3), marker=dict(size=8)))
                        fig.update_layout(xaxis=dict(type='category', title="Fiscal Period"), yaxis=dict(title="Ratio Value"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        with st.expander("Ratio Data Table"):
                            st.dataframe(ratios_df[selected_ratios], use_container_width=True)
                else:
                    st.warning("Not enough data to calculate ratios. Try selecting a longer timeframe or different frequency.")
            
            else:
                st.subheader(f"{ticker} Key Insights Dashboard")
                custom_metrics = calculate_custom_metrics(display_df)
                
                if not custom_metrics.empty:
                    available_custom = list(custom_metrics.columns)
                    st.write("**Critical Metrics for Investors:**")
                    selected_custom = st.multiselect("Select Key Metrics:", options=available_custom, default=available_custom)
                    
                    if selected_custom:
                        fig = px.line(custom_metrics, x=custom_metrics.index, y=selected_custom, markers=True)
                        fig.update_layout(xaxis=dict(type='category', title="Fiscal Period"), yaxis=dict(title="USD"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if 'OperatingIncomeLoss' in display_df.columns:
                            ratios = calculate_ratios(display_df)
                            if 'Operating Margin %' in ratios.columns:
                                col1, col2 = st.columns(2)
                                with col1:
                                    latest_margin = ratios['Operating Margin %'].iloc[-1]
                                    st.metric("Latest Operating Margin", f"{latest_margin:.2f}%")
                                with col2:
                                    if len(ratios) > 1:
                                        prev_margin = ratios['Operating Margin %'].iloc[-2]
                                        margin_change = latest_margin - prev_margin
                                        st.metric("Margin Trend", f"{margin_change:+.2f}%", delta=f"{margin_change:.2f}%")
                        
                        with st.expander("Data Table"):
                            formatted = custom_metrics[selected_custom].copy()
                            for col in formatted.columns:
                                formatted[col] = formatted[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
                            st.dataframe(formatted, use_container_width=True)
                else:
                    st.warning("Not enough cash flow data available to calculate custom metrics.")
            
            if view_mode == "Metrics":
                news = get_company_news(ticker)
                if news:
                    st.divider()
                    st.subheader("Recent News")
                    for article in news:
                        with st.expander(f"{article.get('headline', 'No title')[:100]}..."):
                            st.write(f"**Source:** {article.get('source', 'Unknown')}")
                            st.write(f"**Date:** {datetime.fromtimestamp(article.get('datetime', 0)).strftime('%Y-%m-%d %H:%M')}")
                            st.write(article.get('summary', 'No summary available'))
                            if article.get('url'):
                                st.markdown(f"[Read more]({article['url']})")
        else:
            st.warning("No data found for this timeframe. Try adjusting the history length or frequency.")
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.info("Tip: Make sure the ticker is valid and the company has filed SEC reports.")
else:
    st.info("Enter a valid ticker or company name to start exploring financial data!")
    with st.expander("How to search"):
        st.write("By Ticker: Enter stock symbols like AAPL, MSFT, TSLA")
        st.write("By Name: Enter company names like APPLE INC, MICROSOFT CORP")
        st.write("The tool will try to find matches automatically!")