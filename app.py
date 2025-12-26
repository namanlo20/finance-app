import streamlit as st
import yfinance as yf

# 1. Branding & SEO
st.set_page_config(page_title="TickerTotal", layout="wide")
st.title("🔍 TickerTotal: The Simple Stock Explainer")

# 2. Search Box
ticker_symbol = st.text_input("Enter a Stock Ticker (e.g., TSLA, AAPL, BTC-USD):", "AAPL").upper()

if ticker_symbol:
    stock = yf.Ticker(ticker_symbol)
    
    # 3. Key Metrics (The "At a Glance" Row)
    st.subheader("Market Snapshot")
    col1, col2, col3, col4 = st.columns(4)
    
    info = stock.info
    col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
    col2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
    col3.metric("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%")
    col4.metric("Analyst Target", f"${info.get('targetMeanPrice', 'N/A')}")

    # 4. Simple Explainer (For Beginners)
    with st.expander("📝 What does this company actually do?"):
        st.write(info.get('longBusinessSummary', "No description available."))

    # 5. Interactive Chart
    st.subheader("Price History (Past Year)")
    history = stock.history(period="1y")
    st.area_chart(history['Close'])

    # 6. Live News Feed
    st.subheader(f"Latest News for {ticker_symbol}")
    news = stock.news[:5] # Get the 5 most recent stories
    for article in news:
        st.write(f"**[{article['title']}]({article['link']})**")
        st.caption(f"Source: {article['publisher']}")
        st.divider()