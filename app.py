import streamlit as st

import pandas as pd

import requests

import plotly.express as px



# SEC REQUIREMENT: Identify yourself to avoid 403 blocks

HEADERS = {'User-Agent': "financial_research_terminal@outlook.com"}



st.set_page_config(page_title="TickerTotal: SEC Disclosure", layout="wide")

st.title("🏛️ TickerTotal: Full SEC Disclosure Terminal")



# --- SIDEBAR: SYSTEM CONTROLS ---

with st.sidebar:

    st.header("⚙️ Terminal Settings")

    view_mode = st.radio("Filing Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])

    years_to_show = st.slider("History Length (Years):", 1, 20, 10)

    st.divider()

    user_color = st.color_picker("Primary Metric Color", "#00FFAA")

    st.info("Direct data stream from SEC.gov EDGAR (XBRL).")



@st.cache_data

def get_sec_map():

    res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)

    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in res.json().items()}



ticker_input = st.text_input("Enter US Ticker:", "AAPL").upper()

cik_map = get_sec_map()



if ticker_input in cik_map:

    try:

        cik = cik_map[ticker_input]

        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

        raw_data = requests.get(url, headers=HEADERS).json()

        all_gaap_facts = raw_data['facts']['us-gaap']



        # --- 1. RECURSIVE DATA DISCOVERY ENGINE ---

        master_data = {}

        target_form = "10-K" if "Annual" in view_mode else "10-Q"



        for tag, content in all_gaap_facts.items():

            if 'units' in content and 'USD' in content['units']:

                points = content['units']['USD']

                df_temp = pd.DataFrame(points)

                # Filter for the user's chosen frequency

                df_temp = df_temp[df_temp['form'] == target_form]

                

                if not df_temp.empty:

                    # Create a smart chronological index based on the end-date

                    df_temp['end'] = pd.to_datetime(df_temp['end'])

                    # Handle restatements by taking the most recent 'accn'

                    df_temp = df_temp.sort_values(['end', 'filed'], ascending=[True, False])

                    df_temp = df_temp.drop_duplicates('end', keep='first')

                    

                    master_data[tag] = df_temp.set_index('end')['val']



        # Create one massive table of every GAAP tag found

        master_df = pd.DataFrame(master_data).sort_index()

        

        # SLICE: Take exactly the history requested

        slice_size = years_to_show if target_form == "10-K" else years_to_show * 4

        display_df = master_df.tail(slice_size).copy()



        # --- 2. INTUITIVE AXIS FORMATTING ---

        if target_form == "10-K":

            display_df.index = display_df.index.strftime('%Y')

        else:

            display_df.index = display_df.index.strftime('%Y-Q%q')



        # --- 3. DYNAMIC SEARCHABLE GLOSSARY & CHART ---

        st.divider()

        all_found_metrics = sorted(list(master_df.columns))

        

        st.subheader("🔍 Metrics Discovery")

        selected = st.multiselect(

            "Search every metric in the SEC database (e.g., 'CostOfGoods', 'ResearchAndDevelopment', 'IncomeTax'):",

            options=all_found_metrics,

            default=[t for t in ["Revenues", "NetIncomeLoss", "Assets"] if t in all_found_metrics]

        )



        if not display_df.empty and selected:

            fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group',

                         color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA"])

            

            fig.update_layout(

                xaxis=dict(type='category', title="Fiscal Period (Oldest -> Newest)"),

                yaxis=dict(title="Value (USD)"),

                hovermode="x unified",

                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)

            )

            st.plotly_chart(fig, use_container_width=True)



        # --- 4. DATA TABLE ---

        with st.expander("📂 View Raw SEC Data Table"):

            st.dataframe(display_df[selected])



    except Exception as e:

        st.error(f"The SEC stream for {ticker_input} is currently unavailable or the ticker is invalid.")

else:

    st.warning("Please enter a valid ticker (e.g., TSLA, NVDA, MSFT).")