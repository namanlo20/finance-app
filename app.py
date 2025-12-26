import streamlit as st
import yfinance as yf

# 1. Branding & SEO Setup
st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: The Simple Stock Explainer")

# 2. Search Box
ticker_symbol = st.text_input("Enter a Stock Ticker:", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    
    # 3. Market Snapshot
    st.subheader("Market Snapshot")
    col1, col2, col3, col4 = st.columns(4)
    info = stock.info
    
    # Use .get() to avoid "KeyError" crashes if data is missing
    col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
    col2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    col3.metric("Div. Yield", f"{info.get('dividendYield', 0) * 100:.2f}%")
    col4.metric("Risk Score", info.get('overallRisk', 'N/A'))

    # 4. Simple Explainer for Beginners
    with st.expander("📝 What does this company actually do?"):
        st.write(info.get('longBusinessSummary', "No description available."))

    # 5. Interactive Chart
    st.subheader("Price History (Past Year)")
    history = stock.history(period="1y")
    st.area_chart(history['Close'])

    # 6. Safety-First News Feed (Fixes common KeyErrors)
    st.subheader(f"Latest News for {ticker_symbol}")
    news = stock.news[:5] 
    for article in news:
        # Check if 'content' exists (new yfinance format) or use old format
        content = article.get('content', article)
        title = content.get('title', 'No Title')
        
        # Extract URL safely from nested structures
        url = content.get('canonicalUrl', {}).get('url') or article.get('link', '#')
        
        st.write(f"**[{title}]({url})**")
        st.caption(f"Source: {content.get('publisher', 'Unknown')}")
        st.divider()