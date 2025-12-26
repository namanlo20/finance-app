import streamlit as st
import pandas as pd
import requests
import plotly.express as px

HEADERS = {'User-Agent': "pro_terminal_researcher@yourdomain.com"}

st.set_page_config(page_title="SEC Time Machine", layout="wide")
st.title("🏛️ SEC Historical Terminal (20-Year Focus)")

with st.sidebar:
    st.header("⚙️ Settings")
    view_mode = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
    # This slider now controls the graph accurately
    years_to_show = st.slider("Years of History:", 1, 20, 10)
    user_color = st.color_picker("Chart Primary Color", "#00FFAA")

@st.cache_data
def get_sec_map():
    res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in res.json().items()}

ticker = st.text_input("Enter Ticker:", "AAPL").upper()
cik_map = get_sec_map()

if ticker in cik_map:
    try:
        cik = cik_map[ticker]
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        all_facts = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']

        # THE "SMART TIMELINE" ENGINE: Uses end-dates, not labels
        def get_metric(tag_list, form_type):
            master_df = pd.DataFrame()
            for tag in tag_list:
                if tag in all_facts:
                    units = all_facts[tag].get('units', {}).get('USD', [])
                    temp = pd.DataFrame(units)
                    # FILTER: Keep only the official forms
                    temp = temp[temp['form'] == form_type]
                    if not temp.empty:
                        master_df = pd.concat([master_df, temp])
            
            if not master_df.empty:
                # DEDUPLICATION: Take the most recent filing for each period end-date
                master_df = master_df.sort_values('end').drop_duplicates('end', keep='last')
                # Convert 'end' string to actual date for proper sorting
                master_df['end'] = pd.to_datetime(master_df['end'])
                return master_df.set_index('end')['val']
            return pd.Series()

        form = "10-K" if "Annual" in view_mode else "10-Q"
        
        # Build Table
        df = pd.DataFrame()
        df["Revenue"] = get_metric(["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"], form)
        df["Net Income"] = get_metric(["NetIncomeLoss"], form)
        df["Income Tax"] = get_metric(["IncomeTaxExpenseBenefit"], form)

        # FINAL SORTING & SLICING: This makes the slider work!
        df = df.sort_index(ascending=True) # Oldest -> Newest
        slice_count = years_to_show if form == "10-K" else years_to_show * 4
        display_df = df.tail(slice_count)

        # Convert index back to readable strings for Plotly
        display_df.index = display_df.index.strftime('%Y-%m-%d')

        # --- CHART ---
        st.divider()
        selected = st.multiselect("Active Metrics:", df.columns.tolist(), default=["Revenue", "Net Income"])

        if not display_df.empty and selected:
            fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group',
                         color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1"])
            
            fig.update_layout(
                xaxis=dict(type='category', title="Reporting Period End-Date"),
                yaxis=dict(title="Value (USD)"),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Waiting for SEC stream... ({e})")
else:
    st.warning("Ticker not found.")