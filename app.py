import streamlit as st
import pandas as pd
import requests
import plotly.express as px

HEADERS = {'User-Agent': "pro_terminal_researcher@yourdomain.com"}

st.set_page_config(page_title="SEC Deep History", layout="wide")
st.title("🏛️ SEC Professional Financial Terminal")

with st.sidebar:
    st.header("⚙️ Settings")
    view_mode = st.radio("Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
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

        def get_metric(tag_list, form_type):
            master_df = pd.DataFrame()
            for tag in tag_list:
                if tag in all_facts:
                    units = all_facts[tag].get('units', {}).get('USD', [])
                    temp = pd.DataFrame(units)
                    temp = temp[temp['form'] == form_type]
                    if not temp.empty:
                        master_df = pd.concat([master_df, temp])
            
            if not master_df.empty:
                # Deduplicate by the end-date of the period
                master_df = master_df.sort_values('end').drop_duplicates('end', keep='last')
                master_df['end'] = pd.to_datetime(master_df['end'])
                return master_df.set_index('end')['val']
            return pd.Series()

        form = "10-K" if "Annual" in view_mode else "10-Q"
        
        # --- 1. THE DATA ENGINE: EVERY METRIC ---
        df = pd.DataFrame()
        df["Revenue"] = get_metric(["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"], form)
        df["COGS"] = get_metric(["CostOfGoodsAndServicesSold", "CostOfRevenue"], form)
        df["Net Income"] = get_metric(["NetIncomeLoss"], form)
        df["R&D"] = get_metric(["ResearchAndDevelopmentExpense"], form)
        df["Operating Cash Flow"] = get_metric(["NetCashProvidedByUsedInOperatingActivities"], form)
        df["CapEx"] = get_metric(["PaymentsToAcquirePropertyPlantAndEquipment"], form).abs()
        
        # CALCULATED METRICS
        df["Gross Margin"] = df["Revenue"] - df["COGS"]
        df["Free Cash Flow"] = df["Operating Cash Flow"] - df["CapEx"]
        df["Gross Margin %"] = (df["Gross Margin"] / df["Revenue"].replace(0, 1)) * 100

        # --- 2. THE FORMATTING ENGINE (Intuitive Axis) ---
        df = df.sort_index(ascending=True)
        slice_count = years_to_show if form == "10-K" else years_to_show * 4
        display_df = df.tail(slice_count).copy()

        # Switch label style based on view_mode
        if "Annual" in view_mode:
            display_df.index = display_df.index.strftime('%Y')
        else:
            display_df.index = display_df.index.strftime('%Y-Q%q')

        # --- 3. CHARTING ---
        st.divider()
        st.subheader(f"{ticker} Historical Performance ({view_mode})")
        
        # User can now pick from the full list of metrics
        metrics_options = [m for m in df.columns if not m.endswith('%')]
        selected = st.multiselect("Select Metrics:", metrics_options, default=["Revenue", "Net Income", "Free Cash Flow"])

        if not display_df.empty and selected:
            fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group',
                         color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FFD700", "#FF00FF"])
            
            fig.update_layout(
                xaxis=dict(type='category', title="Fiscal Period"),
                yaxis=dict(title="Value (USD)"),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show Margins on a separate line chart for clarity
            if st.checkbox("Show Gross Margin % Trend"):
                fig_m = px.line(display_df, x=display_df.index, y="Gross Margin %", markers=True)
                fig_m.update_traces(line_color=user_color)
                st.plotly_chart(fig_m, use_container_width=True)

    except Exception as e:
        st.error(f"Waiting for SEC data stream... ({e})")
else:
    st.warning("Please enter a valid ticker to pull historical SEC data.")