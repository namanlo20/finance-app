import streamlit as st
import pandas as pd
import requests

# Test API connection first
st.title("🔍 API Connection Test")

FMP_API_KEY = "9rZXN8pHaPyiCjFHWCVBxQmyzftJbRrj"
BASE_URL = "https://financialmodelingprep.com/api/v3"

st.write("Testing FMP API connection...")

# Test 1: Simple quote
try:
    url = f"{BASE_URL}/quote/AAPL?apikey={FMP_API_KEY}"
    st.write(f"Calling: {url[:80]}...")
    
    response = requests.get(url, timeout=10)
    st.write(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        st.success("✅ API Working!")
        st.json(data)
    else:
        st.error(f"❌ API returned status {response.status_code}")
        st.write(response.text[:500])
        
except requests.exceptions.Timeout:
    st.error("❌ Request timed out - Streamlit Cloud might be blocking external APIs")
    st.warning("""
    **Possible Issue:** Streamlit Cloud free tier blocks some external API calls.
    
    **Solutions:**
    1. Run locally on your computer (will work fine)
    2. Upgrade to Streamlit Cloud paid tier
    3. Use a different hosting platform (Heroku, Railway, etc.)
    """)
    
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.write(f"Error type: {type(e).__name__}")

# Test 2: Check network settings
st.divider()
st.write("### Network Configuration")
try:
    import socket
    hostname = socket.gethostname()
    st.write(f"Hostname: {hostname}")
    
    # Try to resolve FMP domain
    ip = socket.gethostbyname("financialmodelingprep.com")
    st.write(f"FMP IP: {ip}")
    st.success("✅ DNS resolution working")
except Exception as e:
    st.error(f"❌ DNS Error: {e}")
