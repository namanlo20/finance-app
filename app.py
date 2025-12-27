import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
import random

HEADERS = {'User-Agent': "pro_analyst_v6@outlook.com"}
st.set_page_config(page_title="SEC Terminal Pro", layout="wide", page_icon="🚀")

def format_number(num):
    """Format with commas and B/M"""
    if abs(num) >= 1e9:
        return f"${num/1e9:,.1f}B"
    elif abs(num) >= 1e6:
        return f"${num/1e6:,.1f}M"
    else:
        return f"${num:,.0f}"

QUIRKY_COMMENTS = {
    "Total Revenue": ["💰 The big kahuna!", "🎰 Revenue baby!"],
    "NetIncomeLoss": ["✅ The moment of truth!", "💸 Bottom line time!"],
    "OperatingIncomeLoss": ["🏭 Core business profit!", "⚙️ Business model check!"],
    "Free Cash Flow": ["💵 ACTUAL cash generated!", "🔥 FCF = Real money!"],
    "ShareBasedCompensation": ["🎭 Dilution alert!", "💸 The Silicon Valley special!"]
}

METRIC_DEFINITIONS = {
    "Total Revenue": "Total sales before expenses",
    "NetIncomeLoss": "Bottom line profit after all expenses",
    "OperatingIncomeLoss": "Profit from core operations",
    "Free Cash Flow": "Operating Cash Flow minus CapEx - the REAL cash generated",
    "ShareBasedCompensation": "Stock-based pay - dilutes shareholders",
}

@st.cache_data
def get_sec_map():
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    data = r.json()
    ticker_to_cik = {v['ticker']: str(v['cik_str']).zfill(10) for k, v in data.items()}
    return ticker_to_cik

@st.cache_data(ttl=300)
def get_stock_data(ticker):
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'change_percent': info.get('regularMarketChangePercent', 0),
            'previous_close': info.get('previousClose', 0),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'forward_pe': info.get('forwardPE', 0),
        }
    except:
        return None

ticker_map = get_sec_map()

st.title("🚀 SEC Terminal Pro")
st.caption("Your no-BS financial analysis platform")

tab1, tab2 = st.tabs(["📊 Company Analysis", "💎 Investment Checklist"])

with tab2:
    st.header("💎 My Investment Checklist")
    st.markdown("""
    ### What to Look For:
    **1. Free Cash Flow** - Operating CF minus CapEx (most honest metric)
    **2. Operating Income** - Core business profit
    **3. Gross Margin %** - High (>60%) = pricing power
    **4. Operating Margin %** - Target: >20% for software
    **5. Revenue Growth** - >20% YoY = exciting
    """)

with tab1:
    ticker = st.text_input("🔍 Enter Ticker:", "NVDA").upper()
    view_mode = st.radio("View:", ["Metrics", "Ratios", "Insights"], horizontal=True)
    
    if ticker in ticker_map:
        stock_data = get_stock_data(ticker)
        if stock_data:
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Price", f"${stock_data['price']:.2f}", f"{stock_data['change_percent']:.2f}%")
            col2.metric("Prev Close", f"${stock_data['previous_close']:.2f}")
            col3.metric("Market Cap", format_number(stock_data['market_cap']))
            col4.metric("P/E Ratio", f"{stock_data['pe_ratio']:.2f}" if stock_data['pe_ratio'] > 0 else "N/A")
            col5.metric("Forward P/E", f"{stock_data['forward_pe']:.2f}" if stock_data['forward_pe'] > 0 else "N/A")
    
    with st.sidebar:
        st.header("⚙️ Settings")
        freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
        years = st.slider("Years:", 1, 10, 5)
        target_form = "10-K" if "Annual" in freq else "10-Q"
        quirky = st.toggle("🔥 Unhinged Mode", value=False)
    
    if ticker in ticker_map:
        try:
            cik = ticker_map[ticker]
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            data = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']
            
            # Build dataframe
            dfs = {}
            for tag, content in data.items():
                if 'units' in content and 'USD' in content['units']:
                    df = pd.DataFrame(content['units']['USD'])
                    df = df[df['form'] == target_form]
                    if not df.empty:
                        df['end'] = pd.to_datetime(df['end'])
                        df = df.sort_values(['end', 'filed']).drop_duplicates('end', keep='last')
                        dfs[tag] = df.set_index('end')['val']
            
            df = pd.DataFrame(dfs).sort_index().tail(years if target_form == "10-K" else years*4)
            
            # Add revenue
            for rev_tag in ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]:
                if rev_tag in df.columns:
                    df["Total Revenue"] = df[rev_tag]
                    break
            
            # Calculate Gross Profit
            if 'Total Revenue' in df.columns and 'CostOfRevenue' in df.columns:
                df['GrossProfit'] = df['Total Revenue'] - df['CostOfRevenue']
            
            # CALCULATE FREE CASH FLOW - THIS IS THE KEY FIX
            ocf_col = 'NetCashProvidedByUsedInOperatingActivities'
            capex_col = 'PaymentsToAcquirePropertyPlantAndEquipment'
            
            if ocf_col in df.columns and capex_col in df.columns:
                df['Free Cash Flow'] = df[ocf_col] - df[capex_col].abs()
            
            # Format index
            df.index = df.index.strftime('%Y' if target_form == "10-K" else '%Y-Q%q')
            
            if view_mode == "Metrics":
                # CASH FLOW
                st.markdown("### 💧 Statement of Cash Flows")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    cf_options = [c for c in ['Free Cash Flow', 'ShareBasedCompensation', ocf_col, capex_col] if c in df.columns]
                    cf_selected = st.multiselect("Select:", cf_options, default=['Free Cash Flow', 'ShareBasedCompensation'] if 'Free Cash Flow' in cf_options else cf_options[:2], key="cf")
                
                with col2:
                    if cf_selected:
                        if quirky:
                            for m in cf_selected:
                                if m in QUIRKY_COMMENTS:
                                    st.info(random.choice(QUIRKY_COMMENTS[m]))
                        
                        colors = {'Free Cash Flow': '#00D9FF', 'ShareBasedCompensation': '#FF6B9D'}
                        fig = px.bar(df, x=df.index, y=cf_selected, barmode='group',
                                   color_discrete_sequence=[colors.get(m, '#FFC837') for m in cf_selected])
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📖 Definitions"):
                            for m in cf_selected:
                                if m in METRIC_DEFINITIONS:
                                    st.write(f"**{m}**: {METRIC_DEFINITIONS[m]}")
                
                st.divider()
                
                # INCOME STATEMENT
                st.markdown("### 💵 Income Statement")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    inc_options = [c for c in ['Total Revenue', 'OperatingIncomeLoss', 'NetIncomeLoss'] if c in df.columns]
                    inc_selected = st.multiselect("Select:", inc_options, default=inc_options[:3], key="inc")
                
                with col2:
                    if inc_selected:
                        if quirky:
                            for m in inc_selected:
                                if m in QUIRKY_COMMENTS:
                                    st.info(random.choice(QUIRKY_COMMENTS[m]))
                        
                        fig = px.bar(df, x=df.index, y=inc_selected, barmode='group')
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📖 Definitions"):
                            for m in inc_selected:
                                if m in METRIC_DEFINITIONS:
                                    st.write(f"**{m}**: {METRIC_DEFINITIONS[m]}")
                
                st.divider()
                
                # BALANCE SHEET
                st.markdown("### 🏦 Balance Sheet")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    bal_options = [c for c in ['Assets', 'Liabilities', 'StockholdersEquity'] if c in df.columns]
                    bal_selected = st.multiselect("Select:", bal_options, default=bal_options[:3], key="bal")
                
                with col2:
                    if bal_selected:
                        fig = px.bar(df, x=df.index, y=bal_selected, barmode='group')
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
            
            elif view_mode == "Ratios":
                st.markdown("### 📊 Financial Ratios")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown("### 📊 What to Look For:")
                    st.markdown("""
                    **Gross Margin:**
                    - Software: 70-90% = Excellent
                    - Retail: 20-40% = Normal
                    
                    **Operating Margin:**
                    - Software: >20% = Strong
                    - Manufacturing: >10% = Good
                    
                    **Net Margin:**
                    - Tech: 15-25% = Healthy
                    - Retail: 2-5% = Normal
                    
                    💡 Higher = Better
                    """)
                
                with col2:
                    ratios = pd.DataFrame(index=df.index)
                    if 'GrossProfit' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Gross Margin %'] = (df['GrossProfit'] / df['Total Revenue'] * 100).round(2)
                    if 'OperatingIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Operating Margin %'] = (df['OperatingIncomeLoss'] / df['Total Revenue'] * 100).round(2)
                    if 'NetIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Net Margin %'] = (df['NetIncomeLoss'] / df['Total Revenue'] * 100).round(2)
                    
                    if not ratios.empty:
                        fig = px.bar(ratios, x=ratios.index, y=list(ratios.columns), barmode='group')
                        fig.update_layout(height=400, yaxis=dict(range=[ratios.min().min()*1.1, ratios.max().max()*1.1]))
                        st.plotly_chart(fig, use_container_width=True)
            
            elif view_mode == "Insights":
                st.markdown("### 💎 Key Investment Metrics")
                
                if 'Free Cash Flow' in df.columns:
                    metrics = ['Free Cash Flow']
                    if 'OperatingIncomeLoss' in df.columns:
                        metrics.append('OperatingIncomeLoss')
                    
                    fig = px.bar(df, x=df.index, y=metrics, barmode='group',
                               color_discrete_sequence=['#00D9FF', '#FF6B9D'])
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    latest = df['Free Cash Flow'].iloc[-1]
                    col1, col2 = st.columns(2)
                    col1.metric("Latest FCF", format_number(latest))
                    if latest > 0:
                        col2.success("✅ Positive FCF!")
                    else:
                        col2.error("🚨 Negative FCF!")
                else:
                    st.error("No FCF data available")
        
        except Exception as e:
            st.error(f"Error: {e}")