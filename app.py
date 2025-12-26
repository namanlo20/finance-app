import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# SEC REQUIREMENT: Use a professional header to prevent blocking
HEADERS = {'User-Agent': "final_terminal_build@yourdomain.com"}

st.set_page_config(page_title="TickerTotal: Pro", layout="wide")
st.title("🏛️ TickerTotal: Final Professional Terminal")

with st.sidebar:
    st.header("⚙️ Terminal Settings")
    view_mode = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
    years_to_show = st.slider("History Length (Years):", 1, 20, 10)
    st.divider()
    user_color = st.color_picker("Chart Theme Color", "#00FFAA")

@st.cache_data
def get_sec_map():
    res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in res.json().items()}

ticker = st.text_input("Enter Ticker (e.g., NVDA, AAPL):", "AAPL").upper()
cik_map = get_sec_map()

if ticker in cik_map:
    try:
        cik = cik_map[ticker]
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        raw_facts = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']

        # --- 1. THE DATA RECOVERY ENGINE ---
        master_data = {}
        target_form = "10-K" if "Annual" in view_mode else "10-Q"

        for tag, content in raw_facts.items():
            if 'units' in content and 'USD' in content['units']:
                points = content['units']['USD']
                df_loop = pd.DataFrame(points)
                # Filter for chosen frequency
                df_loop = df_loop[df_loop['form'] == target_form]
                
                if not df_loop.empty:
                    df_loop['end'] = pd.to_datetime(df_loop['end'])
                    # Deduplicate: Keep most recent filing for each period
                    df_loop = df_loop.sort_values(['end', 'filed'], ascending=[True, False])
                    df_loop = df_loop.drop_duplicates('end', keep='first')
                    master_data[tag] = df_loop.set_index('end')['val']

        # Master Table (Every metric is a column)
        master_df = pd.DataFrame(master_data).sort_index()
        
        # SLICE: Take exactly the history requested
        slice_count = years_to_show if target_form == "10-K" else years_to_show * 4
        display_df = master_df.tail(slice_count).copy()

        # INTUITIVE LABELS: 2024 for Annual, 2024-Q1 for Quarterly
        if not display_df.empty:
            if target_form == "10-K":
                display_df.index = display_df.index.strftime('%Y')
            else:
                display_df.index = display_df.index.strftime('%Y-Q%q')

        # --- 2. THE GLOSSARY & SEARCH ---
        st.divider()
        all_found_tags = sorted(list(master_df.columns))
        
        st.subheader("🔍 Financial Search & Glossary")
        selected = st.multiselect(
            "Search for COGS, Operating Income, R&D, etc.:",
            options=all_found_tags,
            default=[t for t in ["Revenues", "NetIncomeLoss", "OperatingIncomeLoss"] if t in all_found_tags]
        )

        # --- 3. DYNAMIC CHARTING