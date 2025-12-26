import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# SEC REQUIREMENT: Use a professional-looking email header
HEADERS = {'User-Agent': "financial_analyst_pro@yourdomain.com"}

st.set_page_config(page_title="TickerTotal: Deep SEC", layout="wide")
st.title("🏛️ TickerTotal: Every-Metric SEC Terminal")

with st.sidebar:
    st.header("⚙️ Data Settings")
    view_mode = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
    years_to_show = st.slider("History (Years):", 1, 20, 10)
    user_color = st.color_picker("Chart Primary Color", "#00FFAA")
    st.divider()
    st.info("This engine pulls every GAAP tag from the official SEC EDGAR database.")

@st.cache_data
def get_sec_map():
    res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    return {v['ticker']: str(v['cik_str']).zfill(10) for k, v in res.json().items()}

ticker = st.text_input("Enter Ticker (e.g., TSLA, NVDA):", "AAPL").upper()
cik_map = get_sec_map()

if ticker in cik_map:
    try:
        cik = cik_map[ticker]
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        raw_facts = requests.get(url, headers=HEADERS).json()['facts']['us-gaap']

        # THE "EVERYTHING" ENGINE: Flattens every tag into a DataFrame
        all_metrics_data = {}
        target_form = "10-K" if "Annual" in view_mode else "10-Q"

        for tag, content in raw_facts.items():
            if 'units' in content and 'USD' in content['units']:
                df_points = pd.DataFrame(content['units']['USD'])
                # Filter for the specific form (10-K or 10-Q)
                df_points = df_points[df_points['form'] == target_form]
                
                if not df_temp.empty:
                    # Use the 'end' date for perfect chronological sorting
                    df_points['end'] = pd.to_datetime(df_points['end'])
                    # Deduplicate: Keep only the most recent filing for each date
                    df_points = df_points.sort_values('end').drop_duplicates('end', keep='last')
                    all_metrics_data[tag] = df_points.set_index('end')['val']

        # Create the Master Table (Every metric is a column)
        master_df = pd.DataFrame(all_metrics_data).sort_index()
        
        # SLICE: Accurately apply the years_to_show slider
        slice_amt = years_to_show if target_form == "10-K" else years_to_show * 4
        display_df = master_df.tail(slice_amt).copy()

        # FORMATTING: Change date display based on Annual vs Quarterly
        if target_form == "10-K":
            display_df.index = display_df.index.strftime('%Y')
        else:
            display_df.index = display_df.index.strftime('%Y-Q%q')

        # --- DYNAMIC GLOSSARY & CHARTING ---
        st.divider()
        all_found_tags = sorted(list(master_df.columns))
        
        st.subheader("🔍 All-Metric Glossary")
        selected = st.multiselect(
            "Search and Add ANY Metric (e.g. 'CostOfGoods', 'IncomeTax', 'ResearchAndDevelopment'):",
            options=all_found_tags,
            default=[t for t in ["Revenues", "NetIncomeLoss", "Assets"] if t in all_found_tags]
        )

        if not display_df.empty and selected:
            fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group',
                         color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA"])
            
            fig.update_layout(
                xaxis=dict(type='category', title="Fiscal Period (Time)"),
                yaxis=dict(title="Value (USD)"),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Data Table View
            with st.expander("📂 View Raw Data Values"):
                st.dataframe(display_df[selected])

    except Exception as e:
        st.error(f"Waiting for SEC data stream... ({e})")
else:
    st.warning("Ticker not found. Please use a valid US Stock Ticker.")