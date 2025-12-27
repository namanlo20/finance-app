import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
import random

HEADERS = {'User-Agent': "pro_analyst_v6@outlook.com"}
st.set_page_config(page_title="SEC Terminal Pro", layout="wide", page_icon="🚀")

st.markdown("""
<style>
.main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
h1, h2, h3 { color: white !important; }
.stMetric { background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

def format_large_number(num):
    """Format with commas - FIX #1"""
    if abs(num) >= 1e9:
        return f"${num/1e9:,.1f}B"  # The :, adds commas!
    elif abs(num) >= 1e6:
        return f"${num/1e6:,.1f}M"
    else:
        return f"${num:,.0f}"

QUIRKY_COMMENTS = {
    "Total Revenue": ["💰 Top line!", "🎰 Revenue baby!"],
    "NetIncomeLoss": ["✅ Bottom line!", "💸 Real profit!"],
    "OperatingIncomeLoss": ["🏭 Core business!", "⚙️ Can they run a business?"],
    "Free Cash Flow": ["💵 REAL CASH!", "🔥 Money they can use!"],
    "ShareBasedCompensation": ["🎭 Dilution alert!", "💸 Silicon Valley special!"]
}

METRIC_DEFINITIONS = {
    "Total Revenue": "Total sales before expenses",
    "NetIncomeLoss": "Bottom line profit",
    "OperatingIncomeLoss": "Profit from core operations",
    "Free Cash Flow": "Operating Cash Flow minus CapEx",
    "ShareBasedCompensation": "Stock comp - dilutes shareholders"
}

@st.cache_data
def get_sec_map():
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    data = r.json()
    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in data.items()}

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

@st.cache_data(ttl=300)
def get_fcf_from_yahoo(ticker, period="Annual"):
    """FIX #2: Get FCF from Yahoo Finance since SEC is failing"""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        
        if period == "Annual":
            cf = stock.cashflow
        else:
            cf = stock.quarterly_cashflow
        
        if cf is not None and not cf.empty:
            cf = cf.T.sort_index()
            fcf_data = pd.DataFrame(index=cf.index)
            
            if 'Operating Cash Flow' in cf.columns and 'Capital Expenditure' in cf.columns:
                fcf_data['Free Cash Flow'] = cf['Operating Cash Flow'] + cf['Capital Expenditure']  # CapEx is negative
            
            if 'Operating Cash Flow' in cf.columns:
                fcf_data['Operating Cash Flow'] = cf['Operating Cash Flow']
            
            # Format index
            fcf_data.index = fcf_data.index.strftime('%Y' if period == "Annual" else '%Y-Q%q')
            return fcf_data
    except:
        pass
    return pd.DataFrame()

ticker_map = get_sec_map()

st.title("🚀 SEC Terminal Pro")

tab1, tab2 = st.tabs(["📊 Company Analysis", "💎 Checklist"])

with tab2:
    st.header("💎 Investment Checklist")
    st.markdown("""
    ### What to Look For:
    1. **Free Cash Flow** - Real cash (Op CF - CapEx)
    2. **Operating Income** - Core business profit
    3. **Gross Margin %** - >60% = pricing power
    4. **Operating Margin %** - >20% for software
    5. **Revenue Growth** - >20% YoY = exciting
    """)

with tab1:
    ticker = st.text_input("🔍 Ticker:", "NVDA").upper()
    view = st.radio("View:", ["Metrics", "Ratios", "Insights"], horizontal=True)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
        years = st.slider("Years:", 1, 10, 5)
        target_form = "10-K" if "Annual" in freq else "10-Q"
        period_yahoo = "Annual" if "Annual" in freq else "Quarterly"
        quirky = st.toggle("🔥 Unhinged Mode", False)
    
    if ticker in ticker_map:
        stock_data = get_stock_data(ticker)
        if stock_data:
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Price", f"${stock_data['price']:.2f}", f"{stock_data['change_percent']:.2f}%")
            col2.metric("Prev Close", f"${stock_data['previous_close']:.2f}")
            # FIX #1: Market cap with COMMAS
            col3.metric("Market Cap", format_large_number(stock_data['market_cap']))
            col4.metric("P/E Ratio", f"{stock_data['pe_ratio']:.2f}" if stock_data['pe_ratio'] > 0 else "N/A")
            col5.metric("Forward P/E", f"{stock_data['forward_pe']:.2f}" if stock_data['forward_pe'] > 0 else "N/A")
        
        try:
            cik = ticker_map[ticker]
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            data = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']
            
            dfs = {}
            for tag, content in data.items():
                if 'units' in content and 'USD' in content['units']:
                    df = pd.DataFrame(content['units']['USD'])
                    df = df[df['form'] == target_form]
                    if not df.empty:
                        df['end'] = pd.to_datetime(df['end'])
                        df = df.sort_values(['end', 'filed']).drop_duplicates('end', keep='last')
                        dfs[tag] = df.set_index('end')['val']
            
            df = pd.DataFrame(dfs).sort_index()
            
            # Add revenue
            for rev_tag in ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]:
                if rev_tag in df.columns:
                    df["Total Revenue"] = df[rev_tag]
                    break
            
            # Gross Profit
            if 'Total Revenue' in df.columns and 'CostOfRevenue' in df.columns:
                df['GrossProfit'] = df['Total Revenue'] - df['CostOfRevenue']
            
            # Filter years
            df = df.tail(years if target_form == "10-K" else years*4)
            df.index = df.index.strftime('%Y' if target_form == "10-K" else '%Y-Q%q')
            
            # FIX #2: Get FCF from Yahoo Finance
            fcf_df = get_fcf_from_yahoo(ticker, period_yahoo)
            if not fcf_df.empty:
                fcf_df = fcf_df.tail(years if period_yahoo == "Annual" else years*4)
            
            if view == "Metrics":
                # FIX #3: STATEMENT NAMES NEXT TO CHARTS (NOT JUST SYMBOLS!)
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.subheader("Statement of Cash Flows")  # THE NAME!
                with col2:
                    st.markdown("### 💧 Statement of Cash Flows")  # THE NAME AGAIN!
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    if not fcf_df.empty:
                        cf_cols = list(fcf_df.columns)
                        cf_sel = st.multiselect("Select:", cf_cols, default=cf_cols[:2], key="cf")
                    else:
                        st.warning("No cash flow data")
                        cf_sel = []
                
                with col2:
                    if cf_sel and not fcf_df.empty:
                        if quirky:
                            for m in cf_sel:
                                if m in QUIRKY_COMMENTS:
                                    st.info(random.choice(QUIRKY_COMMENTS[m]))
                        
                        colors = {'Free Cash Flow': '#00D9FF', 'Operating Cash Flow': '#FF6B9D'}
                        fig = px.bar(fcf_df, x=fcf_df.index, y=cf_sel, barmode='group',
                                   color_discrete_sequence=[colors.get(m, '#FFC837') for m in cf_sel])
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                        paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📖 Definitions"):
                            for m in cf_sel:
                                if m in METRIC_DEFINITIONS:
                                    st.write(f"**{m}**: {METRIC_DEFINITIONS[m]}")
                
                st.divider()
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.subheader("Income Statement")  # THE NAME!
                with col2:
                    st.markdown("### 💵 Income Statement")  # THE NAME AGAIN!
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    inc_cols = [c for c in ['Total Revenue', 'OperatingIncomeLoss', 'NetIncomeLoss'] if c in df.columns]
                    inc_sel = st.multiselect("Select:", inc_cols, default=inc_cols, key="inc")
                
                with col2:
                    if inc_sel:
                        if quirky:
                            for m in inc_sel:
                                if m in QUIRKY_COMMENTS:
                                    st.info(random.choice(QUIRKY_COMMENTS[m]))
                        fig = px.bar(df, x=df.index, y=inc_sel, barmode='group')
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                        paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📖 Definitions"):
                            for m in inc_sel:
                                if m in METRIC_DEFINITIONS:
                                    st.write(f"**{m}**: {METRIC_DEFINITIONS[m]}")
                
                st.divider()
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.subheader("Balance Sheet")  # THE NAME!
                with col2:
                    st.markdown("### 🏦 Balance Sheet")  # THE NAME AGAIN!
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    bal_cols = [c for c in ['Assets', 'Liabilities', 'StockholdersEquity'] if c in df.columns]
                    bal_sel = st.multiselect("Select:", bal_cols, default=bal_cols, key="bal")
                
                with col2:
                    if bal_sel:
                        fig = px.bar(df, x=df.index, y=bal_sel, barmode='group')
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                        paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
            
            elif view == "Ratios":
                # FIX #5: MARGIN GUIDANCE ON SIDE
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown("### 📊 What to Look For:")
                    st.markdown("""
                    **Gross Margin:**
                    - Software: 70-90% = Excellent
                    - Retail: 20-40% = Normal
                    - Ex: Apple ~43%, Walmart ~25%
                    
                    **Operating Margin:**
                    - Software: >20% = Strong
                    - Manufacturing: >10% = Good
                    - Ex: Microsoft ~42%, Ford ~5%
                    
                    **Net Margin:**
                    - Tech: 15-25% = Healthy
                    - Retail: 2-5% = Normal
                    - Ex: Google ~21%, Target ~4%
                    
                    💡 **Higher = Better**
                    """)
                
                with col2:
                    st.markdown("### 📊 Financial Ratios")
                    ratios = pd.DataFrame(index=df.index)
                    
                    if 'GrossProfit' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Gross Margin %'] = (df['GrossProfit'] / df['Total Revenue'] * 100).round(2)
                    if 'OperatingIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Operating Margin %'] = (df['OperatingIncomeLoss'] / df['Total Revenue'] * 100).round(2)
                    if 'NetIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Net Margin %'] = (df['NetIncomeLoss'] / df['Total Revenue'] * 100).round(2)
                    
                    if not ratios.empty:
                        # FIX #4: PROPER Y-AXIS
                        max_val = ratios.max().max()
                        min_val = ratios.min().min()
                        y_min = min(0, min_val - 5)
                        y_max = max_val + 10
                        
                        fig = px.bar(ratios, x=ratios.index, y=list(ratios.columns), barmode='group')
                        fig.update_layout(height=500, yaxis=dict(range=[y_min, y_max]),
                                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
            
            elif view == "Insights":
                st.markdown("### 💎 Key Investment Metrics")
                
                # FIX #6: INSIGHTS WITH FCF FROM YAHOO
                if not fcf_df.empty and 'Free Cash Flow' in fcf_df.columns:
                    fig = px.bar(fcf_df, x=fcf_df.index, y=['Free Cash Flow'], barmode='group',
                               color_discrete_sequence=['#00D9FF'])
                    fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                    paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    latest = fcf_df['Free Cash Flow'].iloc[-1]
                    col1, col2 = st.columns(2)
                    col1.metric("Latest Free Cash Flow", format_large_number(latest))
                    
                    if latest > 0:
                        col2.success("✅ Positive FCF!")
                    else:
                        col2.error("🚨 Negative FCF!")
                else:
                    st.error("No FCF data")
        
        except Exception as e:
            st.error(f"Error: {e}")