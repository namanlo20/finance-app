import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# SEC REQUIREMENT: You must identify yourself or they will block the IP
HEADERS = {'User-Agent': "independent_researcher_v1@yourdomain.com"}

st.set_page_config(page_title="SEC Terminal", layout="wide")
st.title("🏛️ SEC Historical Terminal")

@st.cache_data
def get_tickers():
    # Fetch the mapping of Tickers to CIK numbers
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in r.json().items()}

# --- 1. SETUP ---
ticker_map = get_tickers()
ticker = st.text_input("Enter Ticker (e.g. NVDA, AAPL, MSFT):", "NVDA").upper()

with st.sidebar:
    st.header("⚙️ Settings")
    freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
    years = st.slider("History Length:", 1, 20, 10)
    target_form = "10-K" if "Annual" in freq else "10-Q"

if ticker in ticker_map:
    try:
        cik = ticker_map[ticker]
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            raw_facts = response.json()['facts']['us-gaap']
            master_df = pd.DataFrame()

            # --- 2. DYNAMIC DATA HARVESTING ---
            # We scan every tag available for this specific company
            for tag, content in raw_facts.items():
                if 'units' in content and 'USD' in content['units']:
                    data_points = content['units']['USD']
                    temp_df = pd.DataFrame(data_points)
                    
                    # Filter by form type (10-K or 10-Q)
                    temp_df = temp_df[temp_df['form'] == target_form]
                    
                    if not temp_df.empty:
                        # Clean up dates and keep the most recent filing for each period
                        temp_df['end'] = pd.to_datetime(temp_df['end'])
                        temp_df = temp_df.sort_values(['end', 'filed']).drop_duplicates('end', keep='last')
                        # Add to our master collection
                        master_df[tag] = temp_df.set_index('end')['val']

            # --- 3. UI & VISUALIZATION ---
            if not master_df.empty:
                master_df = master_df.sort_index()
                
                # Format Axis Labels
                display_df = master_df.tail(years if target_form == "10-K" else years * 4).copy()
                if target_form == "10-K":
                    display_df.index = display_df.index.strftime('%Y')
                else:
                    display_df.index = display_df.index.strftime('%Y-Q%q')

                st.subheader(f"📊 {ticker} Historical Metrics")
                
                # The Glossary: Every tag found for this company is now searchable
                all_tags = sorted(list(master_df.columns))
                selected = st.multiselect(
                    "Search Glossary (e.g. Revenues, CostOfGoods, OperatingIncome):",
                    options=all_tags,
                    default=[t for t in ["Revenues", "NetIncomeLoss", "OperatingIncomeLoss"] if t in all_tags]
                )

                if selected:
                    fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group')
                    fig.update_layout(xaxis=dict(type='category', title="Fiscal Period"), hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander("📂 View Raw Data"):
                        st.table(display_df[selected].iloc[::-1]) # Show newest first in table
            else:
                st.warning(f"No {target_form} data found for this ticker.")
        else:
            st.error(f"SEC API Error: {response.status_code}")

    except Exception as e:
        st.error(f"Critical System Error: {e}")
else:
    st.info("Waiting for ticker...")