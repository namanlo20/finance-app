import streamlit as st
import pandas as pd
import requests
import plotly.express as px
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

QUIRKY = {
    "Total Revenue": ["💰 Top line!"],
    "NetIncomeLoss": ["✅ Bottom line!"],
    "Free Cash Flow": ["💵 REAL CASH!"]
}

DEFINITIONS = {
    "Total Revenue": "Total sales",
    "NetIncomeLoss": "Bottom line profit",
    "Free Cash Flow": "Op CF - CapEx"
}

@st.cache_data
def get_sec_map():
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    data = r.json()
    ticker_to_cik = {v['ticker']: str(v['cik_str']).zfill(10) for k, v in data.items()}
    ticker_to_name = {v['ticker']: v['title'] for k, v in data.items()}
    name_to_ticker = {v['title'].upper(): v['ticker'] for k, v in data.items()}
    return ticker_to_cik, ticker_to_name, name_to_ticker

@st.cache_data(ttl=300)
def get_stock_info(ticker):
    import yfinance as yf
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        'price': info.get('currentPrice', 0),
        'change': info.get('regularMarketChangePercent', 0),
        'prev': info.get('previousClose', 0),
        'cap': info.get('marketCap', 0),
        'pe': info.get('trailingPE', 0),
        'fpe': info.get('forwardPE', 0)
    }

@st.cache_data(ttl=300)
def get_fcf(ticker, period):
    import yfinance as yf
    stock = yf.Ticker(ticker)
    
    cf = stock.cashflow if period == "Annual" else stock.quarterly_cashflow
    
    if cf is not None and not cf.empty:
        cf = cf.T.sort_index()
        result = pd.DataFrame(index=cf.index)
        
        if 'Operating Cash Flow' in cf.columns and 'Capital Expenditure' in cf.columns:
            result['Free Cash Flow'] = cf['Operating Cash Flow'] + cf['Capital Expenditure']
        
        if 'Operating Cash Flow' in cf.columns:
            result['Operating Cash Flow'] = cf['Operating Cash Flow']
        
        result.index = result.index.strftime('%Y' if period == "Annual" else '%Y-Q%q')
        return result
    
    return pd.DataFrame()

ticker_map, ticker_names, name_to_ticker = get_sec_map()

st.title("🚀 SEC Terminal Pro")

tab1, tab2 = st.tabs(["📊 Analysis", "💎 Checklist"])

with tab2:
    st.header("💎 Investment Checklist")
    st.markdown("1. Free Cash Flow\n2. Operating Income\n3. Margins >60%")

with tab1:
    search = st.text_input("🔍 Ticker or Company:", "NVDA").upper()
    
    if search in name_to_ticker:
        ticker = name_to_ticker[search]
        name = search.title()
    elif search in ticker_map:
        ticker = search
        name = ticker_names.get(ticker, ticker)
    else:
        ticker = search
        name = search
    
    if ticker in ticker_map:
        st.subheader(f"{name} ({ticker})")
    
    view = st.radio("View:", ["Metrics", "Ratios", "Insights"], horizontal=True)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
        years = st.slider("Years:", 1, 10, 5)
        form = "10-K" if "Annual" in freq else "10-Q"
        period = "Annual" if "Annual" in freq else "Quarterly"
        quirky = st.toggle("🔥 Unhinged Mode", False)
    
    if ticker in ticker_map:
        info = get_stock_info(ticker)
        
        cap = info['cap']
        gdp = 28e12
        pct = (cap / gdp) * 100
        
        if cap >= 1e12:
            cap_str = f"${cap/1e12:,.2f} Trillion"
            note = f"Worth {pct:.1f}% of US GDP! 🇺🇸"
        elif cap >= 1e9:
            cap_str = f"${cap/1e9:,.1f} Billion"
            note = f"{pct:.3f}% of US GDP"
        else:
            cap_str = f"${cap/1e6:,.1f} Million"
            note = "Tiny vs US GDP"
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Price", f"${info['price']:.2f}", f"{info['change']:.2f}%")
        c2.metric("Prev Close", f"${info['prev']:.2f}")
        c3.metric("Market Cap", cap_str, help=note)
        c4.metric("P/E", f"{info['pe']:.2f}" if info['pe'] > 0 else "N/A")
        c5.metric("Fwd P/E", f"{info['fpe']:.2f}" if info['fpe'] > 0 else "N/A")
        
        try:
            cik = ticker_map[ticker]
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            data = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']
            
            dfs = {}
            for tag, content in data.items():
                if 'units' in content and 'USD' in content['units']:
                    d = pd.DataFrame(content['units']['USD'])
                    d = d[d['form'] == form]
                    if not d.empty:
                        d['end'] = pd.to_datetime(d['end'])
                        d = d.sort_values(['end', 'filed']).drop_duplicates('end', keep='last')
                        dfs[tag] = d.set_index('end')['val']
            
            df = pd.DataFrame(dfs).sort_index()
            
            for r in ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]:
                if r in df.columns:
                    df["Total Revenue"] = df[r]
                    break
            
            if 'Total Revenue' in df.columns and 'CostOfRevenue' in df.columns:
                df['GrossProfit'] = df['Total Revenue'] - df['CostOfRevenue']
            
            df = df.tail(years if form == "10-K" else years*4)
            df.index = df.index.strftime('%Y' if form == "10-K" else '%Y-Q%q')
            
            fcf = get_fcf(ticker, period)
            if not fcf.empty:
                fcf = fcf.tail(years if period == "Annual" else years*4)
            
            if view == "Metrics":
                st.markdown("### 💧 Statement of Cash Flows")
                
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.write("**Statement of Cash Flows**")
                    if not fcf.empty:
                        opts = list(fcf.columns)
                        sel = st.multiselect("Select:", opts, default=opts[:2], key="cf")
                    else:
                        st.warning("No data")
                        sel = []
                
                with c2:
                    if sel and not fcf.empty:
                        if quirky:
                            for m in sel:
                                if m in QUIRKY:
                                    st.info(random.choice(QUIRKY[m]))
                        
                        colors = {'Free Cash Flow': '#00D9FF', 'Operating Cash Flow': '#FF6B9D'}
                        fig = px.bar(fcf, x=fcf.index, y=sel, barmode='group',
                                   color_discrete_sequence=[colors.get(m, '#FFC837') for m in sel])
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                        paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📖 Definitions"):
                            for m in sel:
                                if m in DEFINITIONS:
                                    st.write(f"**{m}**: {DEFINITIONS[m]}")
                
                st.divider()
                
                st.markdown("### 💵 Income Statement")
                
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.write("**Income Statement**")
                    opts = [c for c in ['Total Revenue', 'OperatingIncomeLoss', 'NetIncomeLoss'] if c in df.columns]
                    sel = st.multiselect("Select:", opts, default=opts, key="inc")
                
                with c2:
                    if sel:
                        if quirky:
                            for m in sel:
                                if m in QUIRKY:
                                    st.info(random.choice(QUIRKY[m]))
                        fig = px.bar(df, x=df.index, y=sel, barmode='group')
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                        paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                
                st.markdown("### 🏦 Balance Sheet")
                
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.write("**Balance Sheet**")
                    opts = [c for c in ['Assets', 'Liabilities', 'StockholdersEquity'] if c in df.columns]
                    sel = st.multiselect("Select:", opts, default=opts, key="bal")
                
                with c2:
                    if sel:
                        fig = px.bar(df, x=df.index, y=sel, barmode='group')
                        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                        paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
            
            elif view == "Ratios":
                c1, c2 = st.columns([1, 3])
                
                with c1:
                    st.markdown("### 📊 What to Look For:")
                    st.markdown("""
                    **Gross Margin:**
                    - Software: 70-90%
                    - Retail: 20-40%
                    
                    **Operating Margin:**
                    - Software: >20%
                    - Mfg: >10%
                    
                    **Net Margin:**
                    - Tech: 15-25%
                    - Retail: 2-5%
                    """)
                
                with c2:
                    st.markdown("### 📊 Financial Ratios")
                    ratios = pd.DataFrame(index=df.index)
                    
                    if 'GrossProfit' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Gross Margin %'] = (df['GrossProfit'] / df['Total Revenue'] * 100).round(2)
                    if 'OperatingIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Operating Margin %'] = (df['OperatingIncomeLoss'] / df['Total Revenue'] * 100).round(2)
                    if 'NetIncomeLoss' in df.columns and 'Total Revenue' in df.columns:
                        ratios['Net Margin %'] = (df['NetIncomeLoss'] / df['Total Revenue'] * 100).round(2)
                    
                    if not ratios.empty:
                        mx = ratios.max().max()
                        mn = ratios.min().min()
                        y_min = min(0, mn - 5)
                        y_max = mx + 10
                        
                        fig = px.bar(ratios, x=ratios.index, y=list(ratios.columns), barmode='group')
                        fig.update_layout(height=500, yaxis=dict(range=[y_min, y_max]),
                                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
            
            elif view == "Insights":
                st.markdown("### 💎 Key Metrics")
                
                if not fcf.empty and 'Free Cash Flow' in fcf.columns:
                    fig = px.bar(fcf, x=fcf.index, y=['Free Cash Flow'], barmode='group',
                               color_discrete_sequence=['#00D9FF'])
                    fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', 
                                    paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    latest = fcf['Free Cash Flow'].iloc[-1]
                    
                    if abs(latest) >= 1e9:
                        s = f"${latest/1e9:,.1f} Billion"
                    elif abs(latest) >= 1e6:
                        s = f"${latest/1e6:,.1f} Million"
                    else:
                        s = f"${latest:,.0f}"
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Latest FCF", s)
                    
                    if latest > 0:
                        c2.success("✅ Positive!")
                    else:
                        c2.error("🚨 Negative!")
                else:
                    st.error("No FCF data")
        
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Ticker not found")
