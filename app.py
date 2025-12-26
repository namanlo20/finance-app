import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# SEC REQUIREMENT: Identify yourself
HEADERS = {'User-Agent': "financial_data_pro@yourdomain.com"}

st.set_page_config(page_title="TickerTotal: SEC Pro", layout="wide")
st.title("🏛️ TickerTotal: Official SEC Pro Terminal")

with st.sidebar:
    st.header("⚙️ Terminal Settings")
    view_mode = st.radio("Filing Frequency:", ["Annual (10-K)", "Quarterly (10-Q)"])
    years_to_show = st.slider("History Length (Years):", 1, 15, 5)
    st.divider()
    user_color = st.color_picker("Main Theme Color", "#00FFAA")

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

        # --- 1. THE SMART SEARCH ENGINE ---
        def find_metric(tag_variants, form_type):
            for tag in tag_variants:
                if tag in all_facts:
                    data = pd.DataFrame(all_facts[tag]['units']['USD'])
                    data = data[data['form'] == form_type]
                    if not data.empty:
                        data['end'] = pd.to_datetime(data['end'])
                        # Take the latest filing for each period
                        return data.sort_values('end').drop_duplicates('end', keep='last').set_index('end')['val']
            return pd.Series()

        form = "10-K" if "Annual" in view_mode else "10-Q"
        
        # MAPPING THE "BASICS" (The most common SEC technical tags)
        df = pd.DataFrame()
        df["Revenue"] = find_metric(["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"], form)
        df["COGS"] = find_metric(["CostOfGoodsAndServicesSold", "CostOfRevenue"], form)
        df["Gross Profit"] = find_metric(["GrossProfit"], form)
        df["Operating Income"] = find_metric(["OperatingIncomeLoss"], form)
        df["Net Income"] = find_metric(["NetIncomeLoss"], form)
        df["Tax Expense"] = find_metric(["IncomeTaxExpenseBenefit"], form)

        # CHRONOLOGICAL CLEANUP
        df = df.sort_index(ascending=True)
        slice_count = years_to_show if form == "10-K" else years_to_show * 4
        display_df = df.tail(slice_count).copy()

        # INTUITIVE LABELS: 2024 vs 2024-Q1
        display_df.index = display_df.index.strftime('%Y' if form == "10-K" else '%Y-Q%q')

        # --- 2. THE DYNAMIC GLOSSARY (For everything else) ---
        st.divider()
        all_tags = sorted(list(all_facts.keys()))
        
        st.subheader("🔍 Financial Search & Glossary")
        selected = st.multiselect(
            "Add ANY specific SEC line item (e.g., 'Inventory', 'ResearchAndDevelopment'):",
            options=all_tags,
            default=["Revenues", "OperatingIncomeLoss", "NetIncomeLoss"]
        )

        # --- 3. CHARTING ---
        if not display_df.empty:
            # Check if selected tags are in our main df, if not, pull them live
            for s in selected:
                if s not in display_df.columns:
                    extra_data = find_metric([s], form)
                    if not extra_data.empty:
                        extra_data.index = extra_data.index.strftime('%Y' if form == "10-K" else '%Y-Q%q')
                        display_df[s] = extra_data

            fig = px.bar(display_df, x=display_df.index, y=selected, barmode='group',
                         color_discrete_sequence=[user_color, "#FF4B4B", "#1C83E1", "#FACA2B", "#AB63FA"])
            
            fig.update_layout(xaxis=dict(type='category', title="Fiscal Period"),
                              yaxis=dict(title="USD"), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Waiting for SEC stream for {ticker}... (Note: {e})")

else:
    st.warning("Please enter a valid US Stock Ticker.")