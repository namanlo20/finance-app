import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
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
</style>
""", unsafe_allow_html=True)

def format_number(num):
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

@st.cache_data(ttl=300)
def get_quote(ticker):
    """Get quote - PREMIUM"""
    url = f"{BASE_URL}/quote/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        else:
            st.error(f"Quote API Error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        st.error(f"Quote error: {str(e)}")
    return None

@st.cache_data(ttl=1800)
def get_profile(ticker):
    """Get company profile"""
    url = f"{BASE_URL}/profile/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_income_statement(ticker, period='annual', limit=5):
    """Get income statement"""
    url = f"{BASE_URL}/income-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
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
    url = f"{BASE_URL}/balance-sheet-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
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
    url = f"{BASE_URL}/cash-flow-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
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
    """Get historical prices - FIXED"""
    url = f"{BASE_URL}/historical-price-full/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data and 'historical' in data:
                df = pd.DataFrame(data['historical'])
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    cutoff = datetime.now() - timedelta(days=years*365)
                    df = df[df['date'] >= cutoff]
                    return df
    except Exception as e:
        st.error(f"Price history error: {str(e)}")
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_ratios_ttm(ticker):
    """Get TTM ratios for P/E and P/S"""
    url = f"{BASE_URL}/ratios-ttm/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                return data[0]
    except:
        pass
    return None

# ============= HEADER =============
st.title("💰 Finance Made Simple")
st.caption("Premium FMP Data")

# ============= SIMPLE TEST =============
ticker = st.text_input("Enter ticker to test:", "AAPL")

if st.button("Test API"):
    with st.spinner("Fetching data..."):
        
        # Test 1: Quote
        st.subheader("1️⃣ Testing Quote")
        quote = get_quote(ticker)
        if quote:
            st.success(f"✅ Quote works! Price: ${quote.get('price', 0):.2f}")
            st.json(quote)
        else:
            st.error("❌ Quote failed")
        
        # Test 2: Profile
        st.subheader("2️⃣ Testing Profile")
        profile = get_profile(ticker)
        if profile:
            st.success(f"✅ Profile works! Company: {profile.get('companyName', 'N/A')}")
            st.json(profile)
        else:
            st.error("❌ Profile failed")
        
        # Test 3: Historical Price
        st.subheader("3️⃣ Testing Historical Price")
        hist = get_historical_price(ticker, 1)
        if not hist.empty:
            st.success(f"✅ Historical works! {len(hist)} data points")
            st.dataframe(hist.head())
        else:
            st.error("❌ Historical failed")
        
        # Test 4: Ratios TTM
        st.subheader("4️⃣ Testing Ratios TTM (P/E, P/S)")
        ratios = get_ratios_ttm(ticker)
        if ratios:
            pe = ratios.get('peRatioTTM', 0)
            ps = ratios.get('priceToSalesRatioTTM', 0)
            st.success(f"✅ Ratios work! P/E: {pe:.2f}, P/S: {ps:.2f}")
            st.json(ratios)
        else:
            st.error("❌ Ratios failed")
        
        # Test 5: Income Statement
        st.subheader("5️⃣ Testing Income Statement")
        income = get_income_statement(ticker, 'annual', 3)
        if not income.empty:
            st.success(f"✅ Income statement works! {len(income)} periods")
            st.dataframe(income[['date', 'revenue', 'netIncome']].head())
        else:
            st.error("❌ Income statement failed")
        
        # Test 6: Cash Flow
        st.subheader("6️⃣ Testing Cash Flow")
        cash = get_cash_flow(ticker, 'annual', 3)
        if not cash.empty:
            st.success(f"✅ Cash flow works! {len(cash)} periods")
            st.dataframe(cash[['date', 'freeCashFlow', 'operatingCashFlow']].head())
        else:
            st.error("❌ Cash flow failed")

st.divider()
st.info("""
**If all tests pass:** Your premium API is working! The full app will work.
**If tests fail:** Check the error messages above.
**Note:** Your FMP dashboard should show API calls increasing.
""")

st.write("**Check your FMP dashboard:** https://site.financialmodelingprep.com/developer/docs")
st.write("If you see API calls increasing there, everything is working!")
