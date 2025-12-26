import streamlit as st
import pandas as pd
import requests
import plotly.express as px

HEADERS = {'User-Agent': "pro_analyst_v6@outlook.com"}

st.set_page_config(page_title="SEC Terminal Pro", layout="wide")
st.title("🏛️ SEC History: The Unbroken Revenue Build")

@st.cache_data
def get_sec_map():
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in r.json().items()}

ticker_map = get_sec_map()
ticker = st.text_input("Enter Ticker:", "NVDA").upper()

with st.sidebar:
    st.header("⚙️ Terminal Settings")
    freq = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
    years_to_show = st.slider("History Length (Years):", 1, 20, 10)
    target_form = "10-K" if "Annual" in freq else "10-Q"

if ticker in ticker_map:
    try:
        cik = ticker_map[ticker]
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        raw_facts = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']

        # 1. THE DATA HARVESTER
        master_dict = {}
        for tag, content in raw_facts.items():
            if 'units' in content and 'USD' in content['units']:
                df_pts = pd.DataFrame(content['units']['USD'])
                df_pts = df_pts[df_pts['form'] == target_form]
                if not df_pts.empty:
                    df_pts['end'] = pd.to_datetime(df_pts['end'])
                    df_pts = df_pts.sort_values(['end', 'filed']).drop_duplicates('end', keep='last')
                    master_dict[tag] = df_pts.set_index('end')['val']

        master_df = pd.DataFrame(master_dict).sort_index()

        # 2. THE SUPER-REVENUE MERGE (Fixes the "NVDA Zero" issue)
        # We look for ANY of these tags and combine them into one solid line
        revenue_variants = [
            "Revenues", 
            "RevenueFromContractWithCustomerExcludingAssessedTax", 
            "SalesRevenueNet", 
            "SalesRevenueGoodsNet",
            "RevenueFromContractWithCustomerIncludingAssessedTax"
        ]
        
        # This line creates the "Total Revenue" column by filling holes in one tag with data from others
        found_rev_tags = [t for t in revenue_variants if t in master_df.columns]
        if found_rev_tags:
            master_df["Total Revenue"] = master_df[found_rev_tags].bfill(axis=1).iloc[:, 0]
        else:
            master_df["Total Revenue"] = 0

        # 3. PREP THE DISPLAY
        slice_amt = years_to_show if target_form == "10-K" else years_to_show * 4
        display_df = master_df.tail(slice_amt).copy()
        
        # Label the time axis
        if not display_df.empty:
            display_df.index = display_df.index.strftime('%Y' if target_form == "10-K" else '%Y-Q%q')

            # 4. THE GRAPH
            all_tags = sorted(list(master_df.columns))
            st.subheader(f"📊 {ticker} Financial Performance")
            
            selected = st.multiselect(
                "Select Metrics (Revenue is pre-selected):",
                options=all_tags,
                default=[t for t in ["Total Revenue", "NetIncomeLoss", "OperatingIncomeLoss"] if t in all_tags]
            )

            if selected:
                fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group')
                fig.update_layout(xaxis=dict(type='category', title="Fiscal Period"), yaxis=dict(title="USD"))
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("📂 Raw Data Table"):
                    st.dataframe(display_df[selected])
        else:
            st.warning("No data found for this frequency. Try switching between Annual and Quarterly.")

    except Exception as e:
        st.error(f"Waiting for SEC stream... (Note: {e})")
else:
    st.info("Enter a valid ticker to start.")