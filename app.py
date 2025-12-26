import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import yfinance as yf

# SEC REQUIREMENT: Identify yourself
HEADERS = {'User-Agent': "pro_analyst_tool@yourdomain.com"} 

st.set_page_config(page_title="TickerTotal: SEC Deep Dive", layout="wide")
st.title("🏛️ TickerTotal: 100% Disclosure Terminal")

# --- SIDEBAR: GLOBAL SETTINGS ---
with st.sidebar:
    st.header("⚙️ Terminal Controls")
    view_mode = st.radio("Filing Type:", ["Annual (10-K)", "Quarterly (10-Q)"])
    # This slider now filters the data AFTER pulling everything
    years_to_show = st.slider("Max Years to Display:", 1, 20, 10)
    user_color = st.color_picker("Chart Primary Color", "#00FFAA")
    st.info("Pulling every recorded US-GAAP tag from SEC EDGAR.")

@st.cache_data
def get_sec_map():
    res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in res.json().items()}

ticker_symbol = st.text_input("Enter Ticker:", "TSLA").upper()
cik_map = get_sec_map()

if ticker_symbol in cik_map:
    # 1. REAL-TIME SNAPSHOT
    stock = yf.Ticker(ticker_symbol)
    price = stock.info.get('currentPrice', 'N/A')
    st.subheader(f"⚡ {ticker_symbol} Live: ${price}")

    # 2. THE RECURSIVE SEC ENGINE
    try:
        cik = cik_map[ticker_symbol]
        facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        raw_data = requests.get(facts_url, headers=HEADERS).json()
        all_facts = raw_data['facts']['us-gaap']

        # This list will hold every valid metric we find
        full_dataset = {}
        form_filter = "10-K" if "Annual" in view_mode else "10-Q"

        # LOOP THROUGH EVERY TAG IN THE SEC DATABASE FOR THIS COMPANY
        for tag, content in all_facts.items():
            if 'units' in content and 'USD' in content['units']:
                data_points = content['units']['USD']
                # Convert to DataFrame and filter by form
                temp_df = pd.DataFrame(data_points)
                temp_df = temp_df[temp_df['form'] == form_filter]
                
                if not temp_df.empty:
                    # Create a unique label for time (Year + Quarter)
                    temp_df['label'] = temp_df['fy'].astype(str) + " " + temp_df['fp']
                    # Keep only the most recent value for each period
                    clean_series = temp_df.drop_duplicates('label', keep='last').set_index('label')['val']
                    full_dataset[tag] = clean_series

        # Combine into one massive Master Table
        master_df = pd.DataFrame(full_dataset)
        master_df = master_df.sort_index(ascending=True) # Oldest to Newest
        master_df = master_df.tail(years_to_show if "Annual" in view_mode else years_to_show * 4)

        # 3. DYNAMIC SEARCH & CHARTING
        st.divider()
        st.write("### 🔍 Search & Visualize Every SEC Metric")
        
        # All available US-GAAP tags found for this company
        available_tags = sorted(list(master_df.columns))
        
        # Searchable multiselect
        selected_metrics = st.multiselect(
            "Select any accounting tag (e.g., 'IncomeTax', 'Inventory', 'ResearchAndDevelopment'):",
            options=available_tags,
            default=[t for t in ["Revenues", "NetIncomeLoss"] if t in available_tags]
        )

        if selected_metrics:
            fig = px.bar(
                master_df, 
                x=master_df.index, 
                y=selected_metrics, 
                barmode='group',
                color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA"]
            )
            fig.update_layout(
                xaxis=dict(type='category', title="Fiscal Period"),
                yaxis=dict(title="Value (USD)"),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

        # 4. DATA TABLE PREVIEW
        with st.expander("📂 View Raw Data Table"):
            st.dataframe(master_df[selected_metrics])

    except Exception as e:
        st.error(f"Could not pull deep data: {e}")

    # 5. REAL-TIME NEWS
    st.divider()
    st.subheader(f"📰 Latest {ticker_symbol} Headlines")
    for art in stock.news[:5]:
        st.markdown(f"**[{art.get('title')}]({art.get('link')})**")
        st.caption(f"Source: {art.get('publisher')}")
        st.divider()