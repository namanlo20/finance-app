import streamlit as st
import pandas as pd
import requests
import plotly.express as px

HEADERS = {'User-Agent': "pro_financial_researcher_v4@outlook.com"}

st.set_page_config(page_title="SEC Total Terminal", layout="wide")
st.title("🏛️ SEC Pro Terminal (Fiscal-Year Aware)")

@st.cache_data
def get_tickers():
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in r.json().items()}

# --- UI SETUP ---
ticker_map = get_tickers()
ticker = st.text_input("Enter Ticker:", "NVDA").upper()

with st.sidebar:
    st.header("⚙️ Settings")
    freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
    years = st.slider("History Length (Years):", 1, 20, 10)
    target_form = "10-K" if "Annual" in freq else "10-Q"

if ticker in ticker_map:
    try:
        cik = ticker_map[ticker]
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        raw_facts = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']

        # --- 1. FISCAL-AWARE DATA HARVESTING ---
        master_data = {}
        for tag, content in raw_facts.items():
            if 'units' in content and 'USD' in content['units']:
                points = content['units']['USD']
                df_loop = pd.DataFrame(points)
                df_loop = df_loop[df_loop['form'] == target_form]
                
                if not df_loop.empty:
                    # Use 'end' date (actual fiscal end) instead of 'fy' (fiscal year label)
                    df_loop['end'] = pd.to_datetime(df_loop['end'])
                    # Filter: Keep only the most recent restatements
                    df_loop = df_loop.sort_values(['end', 'filed'], ascending=[True, False])
                    df_loop = df_loop.drop_duplicates('end', keep='first')
                    master_data[tag] = df_loop.set_index('end')['val']

        # Combine into one massive table
        master_df = pd.DataFrame(master_data).sort_index()
        
        # --- 2. DYNAMIC SLICE & LABELING ---
        slice_size = years if target_form == "10-K" else years * 4
        display_df = master_df.tail(slice_size).copy()

        # Intuitive Date Formatting
        if not display_df.empty:
            if target_form == "10-K":
                # For Annual, we show the year of the END date
                display_df.index = display_df.index.strftime('%Y')
            else:
                display_df.index = display_df.index.strftime('%Y-Q%q')

        # --- 3. DYNAMIC SEARCH & CHART ---
        st.divider()
        all_found = sorted(list(master_df.columns))
        
        st.subheader("🔍 Metrics Glossary Search")
        selected = st.multiselect(
            "Search for COGS, Operating Income, etc.:",
            options=all_found,
            default=[t for t in ["Revenues", "OperatingIncomeLoss", "NetIncomeLoss"] if t in all_found]
        )

        if not display_df.empty and selected:
            fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group')
            fig.update_layout(xaxis=dict(type='category', title="Fiscal Period"),
                              yaxis=dict(title="USD"), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📂 View Full Data Table"):
                st.dataframe(display_df[selected])

    except Exception as e:
        st.error(f"Error reading SEC records: {e}")
else:
    st.info("Enter ticker to begin.")