import streamlit as st
import requests

FMP_API_KEY = "9rZXN8pHaPyiCjFHWCVBxQmyzftJbRrj"

st.title("🔍 FMP Premium API Tester")
st.write("Testing ALL possible endpoint formats for your $69 premium account")

ticker = "AAPL"

# ============= TEST 1: /stable with /quote/{ticker} =============
st.header("Test 1: /stable/quote/{ticker}")
url1 = f"https://financialmodelingprep.com/stable/quote/{ticker}?apikey={FMP_API_KEY}"
st.code(url1)
try:
    r = requests.get(url1, timeout=10)
    st.write(f"Status: {r.status_code}")
    if r.status_code == 200:
        st.success("✅ WORKS!")
        st.json(r.json())
    else:
        st.error(f"❌ Failed: {r.text[:300]}")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")

st.divider()

# ============= TEST 2: /api/v3/quote/{ticker} =============
st.header("Test 2: /api/v3/quote/{ticker}")
url2 = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_API_KEY}"
st.code(url2)
try:
    r = requests.get(url2, timeout=10)
    st.write(f"Status: {r.status_code}")
    if r.status_code == 200:
        st.success("✅ WORKS!")
        st.json(r.json())
    else:
        st.error(f"❌ Failed: {r.text[:300]}")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")

st.divider()

# ============= TEST 3: /api/v4/quote/{ticker} =============
st.header("Test 3: /api/v4/quote/{ticker}")
url3 = f"https://financialmodelingprep.com/api/v4/quote/{ticker}?apikey={FMP_API_KEY}"
st.code(url3)
try:
    r = requests.get(url3, timeout=10)
    st.write(f"Status: {r.status_code}")
    if r.status_code == 200:
        st.success("✅ WORKS!")
        st.json(r.json())
    else:
        st.error(f"❌ Failed: {r.text[:300]}")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")

st.divider()

# ============= TEST 4: /stable/quote?symbol={ticker} =============
st.header("Test 4: /stable/quote?symbol={ticker}")
url4 = f"https://financialmodelingprep.com/stable/quote?symbol={ticker}&apikey={FMP_API_KEY}"
st.code(url4)
try:
    r = requests.get(url4, timeout=10)
    st.write(f"Status: {r.status_code}")
    if r.status_code == 200:
        st.success("✅ WORKS!")
        st.json(r.json())
    else:
        st.error(f"❌ Failed: {r.text[:300]}")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")

st.divider()

# ============= TEST 5: /api/v3/quote?symbol={ticker} =============
st.header("Test 5: /api/v3/quote?symbol={ticker}")
url5 = f"https://financialmodelingprep.com/api/v3/quote?symbol={ticker}&apikey={FMP_API_KEY}"
st.code(url5)
try:
    r = requests.get(url5, timeout=10)
    st.write(f"Status: {r.status_code}")
    if r.status_code == 200:
        st.success("✅ WORKS!")
        st.json(r.json())
    else:
        st.error(f"❌ Failed: {r.text[:300]}")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")

st.divider()

st.header("📊 Summary")
st.info("""
Whichever test shows ✅ WORKS is the correct endpoint format!
Then we'll use that for the full app.

Also check your FMP dashboard to see if calls are registering:
https://site.financialmodelingprep.com/developer/docs
""")
