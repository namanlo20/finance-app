import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
from difflib import get_close_matches
import numpy as np

# ============= CONFIGURATION =============
import os
import json
import time

# Build stamp for deploy verification
BUILD_STAMP = os.getenv("RENDER_GIT_COMMIT", "")[:7] or str(int(time.time()))

# API Keys - Use environment variables (set these in Render dashboard)
# FMP_API_KEY: Your Financial Modeling Prep API key
# PERPLEXITY_API_KEY: Your Perplexity API key for AI risk analysis
FMP_API_KEY = os.environ.get("FMP_API_KEY", "")
BASE_URL = "https://financialmodelingprep.com/stable"  # Keep this hardcoded - it works!

# AI Configuration - Perplexity API for risk analysis
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
USE_AI_ANALYSIS = bool(PERPLEXITY_API_KEY)

# Portfolio Configuration - Starting cash for paper trading
STARTING_CASH = float(os.environ.get("STARTING_CASH", "100000"))

st.set_page_config(page_title="Investing Made Simple", layout="wide", page_icon="💰")



# --- GLOBAL UI THEME OVERRIDES (dropdowns = red background) ---
st.markdown("""
<style>
/* Make all Streamlit selectbox dropdown menus match the red theme (background + readable text) */
div[data-baseweb="popover"] ul[role="listbox"]{
  background: #ff4b4b !important;
  color: #ffffff !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
}
div[data-baseweb="popover"] li[role="option"]{
  background: #ff4b4b !important;
  color: #ffffff !important;
  font-weight: 600 !important;
}
div[data-baseweb="popover"] li[role="option"]:hover{
  background: #e63c3c !important;
  color: #ffffff !important;
}
div[data-baseweb="popover"] li[role="option"][aria-selected="true"]{
  background: #d83232 !important;
  color: #ffffff !important;
}
div[data-baseweb="select"] > div{
  background: #ff4b4b !important;
  color: #ffffff !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
}
div[data-baseweb="select"] span{
  color: #ffffff !important;
}
div[data-baseweb="select"] input{
  color: #ffffff !important;
}
/* Make sure the dropdown arrow is visible */
div[data-baseweb="select"] svg{
  fill: #ffffff !important;
}

/* Also style multiselect dropdowns (same baseweb) */
div[data-baseweb="select"]{
  border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)
# --- END GLOBAL UI THEME OVERRIDES ---

# ============= DARK/LIGHT MODE =============
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# ============= THEME STYLING =============
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
    /* DARK MODE - Pure Black Background with White Text */
    .main { background: #000000 !important; padding-top: 80px !important; }
    .stApp { background: #000000 !important; }
    [data-testid="stAppViewContainer"] { background: #000000 !important; padding-top: 80px !important; }
    [data-testid="stHeader"] { background: #000000 !important; }
    [data-testid="stSidebar"] { background: #0a0a0a !important; padding-top: 80px !important; }
    
    /* CRITICAL: Force white text on dark background */
    html, body, .stApp, [data-testid="stAppViewContainer"], 
    [data-testid="stSidebar"], p, span, div, label, li, td, th,
    .stMarkdown, .stText, [data-testid="stMarkdownContainer"],
    .element-container, .stRadio label, .stSelectbox label,
    .stTextInput label, .stSlider label, .stCheckbox label {
        color: #FFFFFF !important;
    }
    
    /* Sidebar expander titles and captions */
    [data-testid="stSidebar"] .stExpander summary, 
    [data-testid="stSidebar"] .stExpander p,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
    }
    
    /* SIDEBAR EXPANDER HEADERS - RED BACKGROUND FOR VISIBILITY */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        border: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        padding: 12px 15px !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
        background: linear-gradient(135deg, #FF6666 0%, #EE0000 100%) !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderContent"] {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 0 0 10px 10px !important;
        padding: 10px !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary span,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary p {
        color: #FFFFFF !important;
    }
    
    /* LIVE TICKER BAR - TOP OF PAGE */
    .ticker-bar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 40px !important;
        background: linear-gradient(90deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%) !important;
        border-bottom: 2px solid #FF4444 !important;
        z-index: 99999 !important;
        overflow: hidden !important;
        display: flex !important;
        align-items: center !important;
    }
    .ticker-content {
        display: flex !important;
        animation: scroll-left 60s linear infinite !important;
        white-space: nowrap !important;
    }
    .ticker-bar:hover .ticker-content {
        animation-play-state: paused !important;
    }
    @keyframes scroll-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    .ticker-item {
        display: inline-flex !important;
        align-items: center !important;
        padding: 0 20px !important;
        border-right: 1px solid rgba(255,255,255,0.2) !important;
    }
    .ticker-item .symbol {
        color: #00D9FF !important;
        font-weight: bold !important;
        margin-right: 8px !important;
    }
    .ticker-item .price {
        color: #FFFFFF !important;
        margin-right: 8px !important;
    }
    .ticker-item .change-up {
        color: #00FF00 !important;
    }
    .ticker-item .change-down {
        color: #FF4444 !important;
    }
    
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; }
    a { color: #00D9FF !important; }
    
    .stMetric { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; }
    .stMetric label, .stMetric [data-testid="stMetricValue"], .stMetric [data-testid="stMetricDelta"] {
        color: #FFFFFF !important;
    }
    
    /* Dataframe/Table text */
    .stDataFrame, .dataframe, table, tr, td, th { color: #FFFFFF !important; }
    
    /* UI CONTRAST AUDIT - Ensure all text is readable */
    /* Form labels and inputs */
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label,
    .stMultiSelect > label, .stSlider > label, .stCheckbox > label,
    .stRadio > label, .stTextArea > label, .stDateInput > label,
    .stTimeInput > label, .stFileUploader > label {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    /* Placeholder text */
    input::placeholder, textarea::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Info, warning, error, success boxes */
    .stAlert, [data-testid="stAlert"] {
        color: #FFFFFF !important;
    }
    .stAlert p, [data-testid="stAlert"] p {
        color: #FFFFFF !important;
    }
    
    /* Expander content */
    .streamlit-expanderContent, [data-testid="stExpanderContent"] {
        color: #FFFFFF !important;
    }
    .streamlit-expanderContent p, [data-testid="stExpanderContent"] p,
    .streamlit-expanderContent span, [data-testid="stExpanderContent"] span {
        color: #FFFFFF !important;
    }
    
    /* Tab labels */
    .stTabs [data-baseweb="tab-list"] button {
        color: #FFFFFF !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #00D9FF !important;
        border-bottom-color: #00D9FF !important;
    }
    
    /* Caption text */
    .stCaption, [data-testid="stCaption"] {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Code blocks */
    code, pre {
        color: #00D9FF !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Markdown text in various containers */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span {
        color: #FFFFFF !important;
    }
    
    /* Number input arrows */
    .stNumberInput button {
        color: #FFFFFF !important;
    }
    
    /* Select dropdown options */
    [data-baseweb="menu"] {
        background: #1a1a2e !important;
    }
    [data-baseweb="menu"] li {
        color: #FFFFFF !important;
    }
    [data-baseweb="menu"] li:hover {
        background: rgba(0, 217, 255, 0.2) !important;
    }
    
    .why-box { 
        background: rgba(255,255,255,0.1); 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #00D9FF;
        margin: 10px 0;
        color: #FFFFFF !important;
    }
    .personal-budget {
        background: rgba(255,215,0,0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        color: #FFFFFF !important;
    }
    .risk-warning {
        background: rgba(255,0,0,0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF0000;
        color: #FFFFFF !important;
    }
    .risk-good {
        background: rgba(0,255,0,0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00FF00;
        color: #FFFFFF !important;
    }
    .roast-box {
        background: rgba(255,100,100,0.2);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FF6B6B;
        margin: 15px 0;
        font-size: 1.1em;
        color: #FFFFFF !important;
    }
    .metric-explain {
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        font-size: 0.9em;
        border-left: 3px solid #00D9FF;
        color: #FFFFFF !important;
    }
    .sector-info {
        background: rgba(255,215,0,0.15);
        padding: 8px;
        border-radius: 6px;
        margin: 3px 0;
        font-size: 0.85em;
        border-left: 3px solid #FFD700;
        color: #FFFFFF !important;
    }
    .growth-note {
        background: rgba(0,255,150,0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00FF96;
        margin: 10px 0;
        font-size: 1em;
        color: #FFFFFF !important;
    }
    
    /* Tooltip styling for hover definitions */
    .ratio-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #00D9FF;
        margin-left: 5px;
    }
    .ratio-tooltip .tooltip-text {
        visibility: hidden;
        width: 300px;
        background-color: #1a1a2e;
        color: #FFFFFF;
        text-align: left;
        border-radius: 8px;
        padding: 15px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -150px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid #00D9FF;
        font-size: 14px;
        line-height: 1.5;
    }
    .ratio-tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* RED BUTTONS - Global styling for Analyze buttons and dropdowns */
    .stButton > button {
        background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF6666 0%, #EE0000 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.4) !important;
    }
    
    /* VIP BUTTON - Gold styling */
    button[data-testid="baseButton-secondary"]:has(div:contains("👑 Become a VIP")),
    button:has(p:contains("👑 Become a VIP")) {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000000 !important;
        border: 2px solid #FFD700 !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.5) !important;
    }
    button[data-testid="baseButton-secondary"]:has(div:contains("👑 Become a VIP")):hover,
    button:has(p:contains("👑 Become a VIP")):hover {
        background: linear-gradient(135deg, #FFED4E 0%, #FFB520 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6) !important;
    }
    
    /* SIGN UP BUTTON - Green styling */
    button:has(p:contains("📝 Sign Up")) {
        background: linear-gradient(135deg, #00C853 0%, #00A843 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    button:has(p:contains("📝 Sign Up")):hover {
        background: linear-gradient(135deg, #00E676 0%, #00C853 100%) !important;
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4) !important;
    }
    
    /* SIGN IN BUTTON - Blue styling */
    button:has(p:contains("🔐 Sign In")) {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    button:has(p:contains("🔐 Sign In")):hover {
        background: linear-gradient(135deg, #42A5F5 0%, #2196F3 100%) !important;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.4) !important;
    }
    
    /* RED SELECT/DROPDOWN styling */
    div[data-baseweb="select"] {
        background: #FF4444 !important;
        border: 2px solid #FF4444 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"]:hover {
        background: #FF6666 !important;
        border-color: #FF6666 !important;
        box-shadow: 0 0 10px rgba(255, 68, 68, 0.3) !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] [role="button"] {
        background: #FF4444 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    }
    
    /* Sidebar Navigation Buttons - Different style from main action buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.05) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        font-weight: normal !important;
        text-align: left !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0, 217, 255, 0.2) !important;
        border-color: #00D9FF !important;
        transform: translateX(5px) !important;
        box-shadow: none !important;
    }
    
    /* Expander styling in sidebar */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    /* RED TEXT INPUT styling */
    input[type="text"],
    input[type="number"],
    .stTextInput input,
    .stNumberInput input {
        background: #FF4444 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #FF4444 !important;
        border-radius: 8px !important;
    }
    input[type="text"]:focus,
    input[type="number"]:focus,
    .stTextInput input:focus,
    .stNumberInput input:focus {
        background: #FF6666 !important;
        border-color: #FF6666 !important;
        box-shadow: 0 0 10px rgba(255, 68, 68, 0.3) !important;
    }
    
    /* Fade-in animation for cards */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .fade-in {
        animation: fadeInUp 0.5s ease-out forwards;
    }
    
    /* Hover lift effect for cards */
    .lift-card {
        transition: all 0.3s ease !important;
    }
    .lift-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 30px rgba(0, 217, 255, 0.2) !important;
    }
    
    /* Live Ticker Bar styling */
    .ticker-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 35px;
        background: linear-gradient(90deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
        border-bottom: 1px solid #333;
        z-index: 9999;
        overflow: hidden;
        display: flex;
        align-items: center;
    }
    .ticker-content {
        display: flex;
        animation: scroll-left 60s linear infinite;
        white-space: nowrap;
    }
    .ticker-bar:hover .ticker-content {
        animation-play-state: paused;
    }
    @keyframes scroll-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    .ticker-item {
        display: inline-flex;
        align-items: center;
        padding: 0 20px;
        font-size: 13px;
        color: #FFFFFF;
    }
    .ticker-item .symbol {
        font-weight: bold;
        color: #00D9FF;
        margin-right: 8px;
    }
    .ticker-item .price {
        margin-right: 8px;
    }
    .ticker-item .change-up {
        color: #00FF00;
    }
    .ticker-item .change-down {
        color: #FF4444;
    }
    
    /* Add padding to main content for ticker bar */
    [data-testid="stAppViewContainer"] {
        padding-top: 40px !important;
    }
    
    /* Welcome popup styling */
    .welcome-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.9);
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .welcome-popup {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #00D9FF;
        border-radius: 20px;
        padding: 40px;
        max-width: 500px;
        text-align: center;
        animation: fadeInUp 0.5s ease-out;
    }
    .welcome-popup h1 {
        color: #FFFFFF;
        margin-bottom: 20px;
    }
    .welcome-popup ul {
        text-align: left;
        color: #FFFFFF;
        line-height: 2;
    }
    .welcome-btn {
        background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
        color: #FFFFFF !important;
        padding: 15px 40px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        margin-top: 20px !important;
    }
    .welcome-btn:hover {
        background: linear-gradient(135deg, #FF6666 0%, #EE0000 100%) !important;
    }
    
    /* Confetti animation */
    @keyframes confetti-fall {
        0% { transform: translateY(-100vh) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
    }
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        z-index: 10001;
        animation: confetti-fall 3s ease-out forwards;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    /* LIGHT MODE - White Background with Black Text */
    .main { background: #FFFFFF !important; padding-top: 80px !important; }
    .stApp { background: #FFFFFF !important; }
    [data-testid="stAppViewContainer"] { background: #FFFFFF !important; padding-top: 80px !important; }
    [data-testid="stHeader"] { background: #FFFFFF !important; }
    [data-testid="stSidebar"] { background: #F5F5F5 !important; padding-top: 80px !important; }
    
    /* Force black text on white background */
    html, body, .stApp, [data-testid="stAppViewContainer"], 
    [data-testid="stSidebar"], p, span, div, label, li, td, th,
    .stMarkdown, .stText, [data-testid="stMarkdownContainer"],
    .element-container, .stRadio label, .stSelectbox label,
    .stTextInput label, .stSlider label, .stCheckbox label {
        color: #000000 !important;
    }
    
    h1, h2, h3, h4, h5, h6 { color: #000000 !important; }
    a { color: #0066CC !important; }
    
    .stMetric { background: rgba(240,240,240,0.9); padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .stMetric label, .stMetric [data-testid="stMetricValue"], .stMetric [data-testid="stMetricDelta"] {
        color: #000000 !important;
    }
    
    /* Dataframe/Table text */
    .stDataFrame, .dataframe, table, tr, td, th { color: #000000 !important; }
    
    .why-box { 
        background: rgba(255,255,255,0.9); 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #00D9FF;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .personal-budget {
        background: rgba(255,235,180,0.9);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .risk-warning {
        background: rgba(255,200,200,0.9);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF0000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .risk-good {
        background: rgba(200,255,200,0.9);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00FF00;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .roast-box {
        background: rgba(255,220,220,0.9);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FF6B6B;
        margin: 15px 0;
        font-size: 1.1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .metric-explain {
        background: rgba(240,248,255,0.95);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        font-size: 0.9em;
        border-left: 3px solid #00D9FF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .sector-info {
        background: rgba(255,250,205,0.95);
        padding: 8px;
        border-radius: 6px;
        margin: 3px 0;
        font-size: 0.85em;
        border-left: 3px solid #FFD700;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .growth-note {
        background: rgba(200,255,220,0.95);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00DD88;
        margin: 10px 0;
        font-size: 1em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    
    /* RED BUTTONS - Global styling for Analyze buttons */
    .stButton > button {
        background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF6666 0%, #EE0000 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.4) !important;
    }
    
    /* VIP BUTTON - Gold styling */
    button[data-testid="baseButton-secondary"]:has(div:contains("👑 Become a VIP")),
    button:has(p:contains("👑 Become a VIP")) {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000000 !important;
        border: 2px solid #FFD700 !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.5) !important;
    }
    button[data-testid="baseButton-secondary"]:has(div:contains("👑 Become a VIP")):hover,
    button:has(p:contains("👑 Become a VIP")):hover {
        background: linear-gradient(135deg, #FFED4E 0%, #FFB520 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6) !important;
    }
    
    /* SIGN UP BUTTON - Green styling */
    button:has(p:contains("📝 Sign Up")) {
        background: linear-gradient(135deg, #00C853 0%, #00A843 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    button:has(p:contains("📝 Sign Up")):hover {
        background: linear-gradient(135deg, #00E676 0%, #00C853 100%) !important;
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4) !important;
    }
    
    /* SIGN IN BUTTON - Blue styling */
    button:has(p:contains("🔐 Sign In")) {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    button:has(p:contains("🔐 Sign In")):hover {
        background: linear-gradient(135deg, #42A5F5 0%, #2196F3 100%) !important;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.4) !important;
    }
    
    /* RED SELECT/DROPDOWN styling */
    div[data-baseweb="select"] {
        background: #FF4444 !important;
        border: 2px solid #FF4444 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"]:hover {
        background: #FF6666 !important;
        border-color: #FF6666 !important;
        box-shadow: 0 0 10px rgba(255, 68, 68, 0.3) !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] [role="button"] {
        background: #FF4444 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* RED TEXT INPUT styling */
    input[type="text"],
    input[type="number"],
    .stTextInput input,
    .stNumberInput input {
        background: #FF4444 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #FF4444 !important;
        border-radius: 8px !important;
    }
    input[type="text"]:focus,
    input[type="number"]:focus,
    .stTextInput input:focus,
    .stNumberInput input:focus {
        background: #FF6666 !important;
        border-color: #FF6666 !important;
        box-shadow: 0 0 10px rgba(255, 68, 68, 0.3) !important;
    }
    
    /* Sidebar Navigation Buttons - Different style from main action buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(0,0,0,0.05) !important;
        color: #1e1e1e !important;
        border: 1px solid rgba(0,0,0,0.2) !important;
        font-weight: normal !important;
        text-align: left !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0, 150, 255, 0.2) !important;
        border-color: #0096FF !important;
        transform: translateX(5px) !important;
        box-shadow: none !important;
    }
    
    /* Expander styling in sidebar */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(0,0,0,0.05) !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    /* Fix text visibility on dark backgrounds in light mode - VIP pricing cards */
    div[style*="background: #1a1a1a"] {
        color: #FFFFFF !important;
    }
    div[style*="background: #1a1a1a"] h3,
    div[style*="background: #1a1a1a"] p,
    div[style*="background: #1a1a1a"] strong {
        color: #FFFFFF !important;
    }
    div[style*="background: linear-gradient(135deg, #1a1a2e"] {
        color: #FFFFFF !important;
    }
    div[style*="background: linear-gradient(135deg, #1a1a2e"] h2,
    div[style*="background: linear-gradient(135deg, #1a1a2e"] p {
        color: #FFFFFF !important;
    }
    
    p, div, span, li { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# ============= METRIC EXPLANATIONS (FOR TOOLTIPS) =============
# "Dumb-User" 10-Word Definitions for Beginners
METRIC_EXPLANATIONS = {
    "P/E Ratio": {
        "short": "Price vs. Profit. How much you pay for $1 of earnings.",
        "explanation": "How much you pay for $1 of earnings. Lower = cheaper. Tech average: 25 | Value stocks: 15",
        "good": "15-25 is reasonable | >40 is expensive | <10 might be undervalued or troubled"
    },
    "P/S Ratio": {
        "short": "Price vs. Sales. Good for companies not yet profitable.",
        "explanation": "How much you pay for $1 of revenue. Useful when company isn't profitable yet.",
        "good": "Tech: 5-10 | Retail: 0.5-2 | Lower = better value"
    },
    "P/B Ratio": {
        "short": "Price vs. Book Value. What you pay for company's assets.",
        "explanation": "Stock price divided by book value per share. Shows if stock is cheap relative to assets.",
        "good": "<1.0 = Trading below asset value | 1-3 = Fair | >5 = Expensive"
    },
    "EV/EBITDA": {
        "short": "Enterprise Value vs. Operating Profit. Compares total company value.",
        "explanation": "Total company value (including debt) divided by operating earnings. Better than P/E for comparing companies with different debt levels.",
        "good": "<10 = Cheap | 10-15 = Fair | >20 = Expensive"
    },
    "Debt-to-Equity": {
        "short": "How much debt a company uses to grow. Lower is safer.",
        "explanation": "Measures financial leverage. High debt = risky during recessions.",
        "good": "<1.0 = Low debt (good) | 1-2 = Moderate | >2.0 = High risk"
    },
    "Current Ratio": {
        "short": "Can the company pay its bills? Above 1.5 is safe.",
        "explanation": "Current assets divided by current liabilities. Shows short-term financial health.",
        "good": ">2.0 = Very safe | 1.5-2.0 = Good | <1.0 = Risky"
    },
    "Quick Ratio": {
        "short": "Cash available to pay bills immediately. Above 1.0 is good.",
        "explanation": "Can the company pay short-term bills without selling inventory?",
        "good": ">1.5 = Excellent liquidity | 1.0-1.5 = Good | <1.0 = Potential cash problems"
    },
    "FCF per Share": {
        "short": "Real cash generated per share. Can't be faked with accounting.",
        "explanation": "Real cash generated per share you own. Unlike earnings, FCF can't be manipulated easily.",
        "good": "Positive = good | Growing FCF/share = excellent | Negative = burning cash"
    },
    "FCF Yield": {
        "short": "Free cash flow as % of stock price. Higher is better.",
        "explanation": "FCF per share divided by stock price. Shows cash return on investment.",
        "good": ">5% = Good yield | 3-5% = Average | <3% = Low yield"
    },
    "Gross Margin": {
        "short": "Profit kept after making the product. Shows pricing power.",
        "explanation": "Revenue minus cost of goods sold, as a percentage. Higher = better pricing power.",
        "good": ">50% = Strong | 30-50% = Average | <30% = Weak pricing power"
    },
    "Operating Margin": {
        "short": "Profit kept after bills are paid. Higher is more efficient.",
        "explanation": "Operating income divided by revenue. Shows how efficiently company runs.",
        "good": ">20% = Excellent | 10-20% = Good | <10% = Needs improvement"
    },
    "Net Margin": {
        "short": "Final profit after everything. The bottom line percentage.",
        "explanation": "Net income divided by revenue. The ultimate profitability measure.",
        "good": ">15% = Strong | 5-15% = Average | <5% = Thin margins"
    },
    "ROE": {
        "short": "Return on shareholder money. Buffett's favorite metric.",
        "explanation": "Net income divided by shareholder equity. Shows how well company uses investor money.",
        "good": ">20% = Excellent | 15-20% = Good | <10% = Poor"
    },
    "ROA": {
        "short": "Return on all assets. How efficiently company uses everything.",
        "explanation": "Net income divided by total assets. Shows overall efficiency.",
        "good": ">10% = Excellent | 5-10% = Good | <5% = Inefficient"
    },
    "RSI": {
        "short": "Speedometer for price. Over 70 is 'Hot,' under 30 is 'Cold'.",
        "explanation": "Relative Strength Index. Measures if stock is overbought or oversold.",
        "good": ">70 = Overbought (might drop) | 30-70 = Normal | <30 = Oversold (might rise)"
    },
    "Market Cap": {
        "short": "Total value of all shares. Shows company size.",
        "explanation": "Stock price × shares outstanding. Shows company size.",
        "good": ">$200B = Mega cap | $10-200B = Large cap | <$2B = Small cap (risky)"
    },
    "Beta": {
        "short": "Stock volatility vs market. Higher means more swings.",
        "explanation": "Measures how much stock moves relative to market.",
        "good": "<0.8 = Defensive | 1.0 = Moves with market | >1.3 = High volatility"
    }
}



# ============= COMPREHENSIVE METRIC EXPLANATIONS =============
FINANCIAL_METRICS_EXPLAINED = {
    # Income Statement Metrics
    "revenue": {
        "simple": "Total money coming in from sales",
        "why": "Shows if the company is growing its business. More revenue = more customers or higher prices."
    },
    "grossProfit": {
        "simple": "Revenue minus cost of making products",
        "why": "Shows profit before expenses. High gross profit = good pricing power or efficient production."
    },
    "operatingIncome": {
        "simple": "Profit from main business operations",
        "why": "Shows if core business is profitable. Excludes one-time items and interest payments."
    },
    "netIncome": {
        "simple": "Bottom line profit after everything",
        "why": "The real profit shareholders get. This is what matters most for stock value."
    },
    "ebitda": {
        "simple": "Earnings before interest, taxes, depreciation, amortization",
        "why": "Shows operating performance without accounting tricks. Good for comparing companies."
    },
    "eps": {
        "simple": "Earnings Per Share - profit divided by shares",
        "why": "Shows profit per share you own. Growing EPS usually means growing stock price."
    },
    
    # Cash Flow Metrics
    "operatingCashFlow": {
        "simple": "Cash generated from main business",
        "why": "Real cash coming in. Unlike earnings, cash can't be faked with accounting."
    },
    "freeCashFlow": {
        "simple": "Cash left after buying equipment and assets",
        "why": "Money available for dividends, buybacks, or growth. This is the gold standard metric."
    },
    "capitalExpenditure": {
        "simple": "Money spent on equipment and property",
        "why": "Shows investment in future growth. High CapEx = company investing heavily."
    },
    "dividendsPaid": {
        "simple": "Cash paid to shareholders",
        "why": "Direct return to investors. Consistent dividends = stable, mature company."
    },
    
    # Balance Sheet Metrics
    "totalAssets": {
        "simple": "Everything the company owns",
        "why": "Shows company size and resources. Growing assets = expanding business."
    },
    "totalLiabilities": {
        "simple": "Everything the company owes",
        "why": "Company's debts and obligations. High liabilities = more risk."
    },
    "totalStockholdersEquity": {
        "simple": "Company's net worth (Assets - Liabilities)",
        "why": "What's left for shareholders if company sold everything and paid all debts."
    },
    "cashAndCashEquivalents": {
        "simple": "Cash in the bank",
        "why": "Safety cushion. More cash = can survive tough times and invest in opportunities."
    },
    "totalDebt": {
        "simple": "All money borrowed",
        "why": "Debt must be repaid with interest. Too much debt = risky during recessions."
    },
    
    # Financial Ratios
    "grossProfitMargin": {
        "simple": "Gross Profit ÷ Revenue (as %)",
        "why": "Shows pricing power. 40%+ is strong. Tech companies often have 70%+."
    },
    "operatingProfitMargin": {
        "simple": "Operating Income ÷ Revenue (as %)",
        "why": "Shows operational efficiency. Higher = better at controlling costs."
    },
    "netProfitMargin": {
        "simple": "Net Income ÷ Revenue (as %)",
        "why": "Bottom line profitability. 15%+ is solid. 25%+ is excellent."
    },
    "returnOnEquity": {
        "simple": "Net Income ÷ Shareholder Equity (as %)",
        "why": "Return on your investment. 15%+ is good. 20%+ is great. Warren Buffett loves this."
    },
    "returnOnAssets": {
        "simple": "Net Income ÷ Total Assets (as %)",
        "why": "How efficiently company uses assets to generate profit. Higher = better."
    },
    "returnOnCapitalEmployed": {
        "simple": "Operating Profit ÷ Capital Employed (as %)",
        "why": "Shows how well company uses invested capital. 15%+ is strong."
    },
    "currentRatio": {
        "simple": "Current Assets ÷ Current Liabilities",
        "why": "Can company pay short-term bills? Above 1.5 = safe. Below 1.0 = risky."
    },
    "quickRatio": {
        "simple": "Quick Assets ÷ Current Liabilities",
        "why": "Stricter than current ratio (excludes inventory). Above 1.0 = good liquidity."
    },
    "debtToEquity": {
        "simple": "Total Debt ÷ Shareholder Equity",
        "why": "Debt risk level. Below 1.0 = safe. Above 2.0 = risky. Banks naturally higher."
    }
}


# ============= GAMIFICATION HELPERS (Robinhood-style) =============
def _ensure_basics_gamification_state():
    if "basics_xp" not in st.session_state:
        # If user has completions already, give baseline XP so progress doesn't feel empty
        st.session_state.basics_xp = len(st.session_state.get("completed_lessons", set())) * 10
    if "basics_badges" not in st.session_state:
        st.session_state.basics_badges = set()
    if "checkpoint_passed" not in st.session_state:
        st.session_state.checkpoint_passed = set()
    if "last_confetti_ts" not in st.session_state:
        st.session_state.last_confetti_ts = 0

def _award_xp(amount: int, reason: str = ""):
    _ensure_basics_gamification_state()
    st.session_state.basics_xp = int(st.session_state.basics_xp) + int(amount)
    if reason:
        try:
            st.toast(f"+{amount} XP — {reason}")
        except Exception:
            pass

def _level_from_xp(xp: int) -> int:
    return max(1, int(xp) // 100 + 1)

def _show_confetti_once(key: str):
    """
    Robinhood-style "confetti": we use a lightweight HTML/CSS burst + Streamlit balloons fallback.
    """
    now = int(time.time())
    # Debounce so reruns don't spam confetti
    if st.session_state.get("last_confetti_ts", 0) + 4 > now:
        return
    st.session_state.last_confetti_ts = now

    confetti_html = """
    <style>
    .confetti-wrap{position:fixed;left:0;top:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;overflow:hidden;}
    .confetti{position:absolute;top:-10px;width:10px;height:16px;opacity:.95;animation:fall 1.8s linear forwards;}
    @keyframes fall{
      0%{transform:translateY(0) rotate(0deg);opacity:1}
      100%{transform:translateY(110vh) rotate(720deg);opacity:0}
    }
    </style>
    <div class="confetti-wrap">
    """ + "".join([
        f'<div class="confetti" style="left:{i*5 % 100}vw; animation-delay:{(i%12)*0.05}s; background:rgb({255},{random.randint(30,80)},{random.randint(30,80)}); border-radius:{random.choice([2,8,50])}px;"></div>'
        for i in range(80)
    ]) + "</div>"
    st.markdown(confetti_html, unsafe_allow_html=True)
    try:
        st.balloons()
    except Exception:
        pass

def _render_robinhood_header():
    _ensure_basics_gamification_state()
    xp = int(st.session_state.basics_xp)
    lvl = _level_from_xp(xp)
    next_lvl_xp = lvl * 100
    progress = min(1.0, xp / next_lvl_xp) if next_lvl_xp else 0.0

    c1, c2, c3 = st.columns([1.1, 1.1, 1.8])
    with c1:
        st.markdown(f"### 🧩 Level {lvl}")
        st.progress(progress)
        st.caption(f"{xp} XP • Next level at {next_lvl_xp} XP")
    with c2:
        badges = st.session_state.get("basics_badges", set())
        st.markdown("### 🏅 Badges")
        if badges:
            st.write(" ".join([f"`M{b}`" for b in sorted(badges)]))
        else:
            st.caption("Finish a module checkpoint to earn badges.")
    with c3:
        st.markdown("### 🔥 Momentum")
        st.caption("Keep it simple: 1 lesson at a time. Finish a checkpoint to unlock a badge.")

# ============= END GAMIFICATION HELPERS =============

def get_metric_explanation(metric_key):
    """Get simple explanation for any metric"""
    # Normalize the key
    key = metric_key.lower().replace(' ', '').replace('_', '')
    
    # Try to find match
    for metric, details in FINANCIAL_METRICS_EXPLAINED.items():
        if metric.lower().replace(' ', '') == key:
            return details
    
    return None

# ============= ROAST DATABASE =============
ROASTS = {
    "meme_stocks": [
        "🦍 Diamond hands meet paper portfolio. The squeeze was 3 years ago, chief.",
        "💀 This portfolio is giving 'held through -90%' energy. You belong on r/wallstreetbets.",
        "🎮 GameStop called, they want their 2021 energy back.",
        "🍿 AMC? More like 'Already My Cash is gone'. This isn't a portfolio, it's a charity.",
        "🚀 'To the moon!' Yeah, the moon of financial ruin. Houston, we have a problem.",
        "🐶 Meme stocks in 2025? That's like bringing a Nokia to an iPhone fight.",
        "🤡 Your portfolio looks like it was assembled by a drunk dartboard.",
        "📉 Congrats! You've perfectly timed buying at the absolute top. That's almost impressive.",
    ],
    "high_debt": [
        "🚨 Your stocks have more debt than a med student. D/E > 3.0. Godspeed.",
        "💸 These companies are leveraged to the TITS. One rate hike away from bankruptcy.",
        "⚰️ High debt + high rates = financial death sentence. RIP your gains.",
        "💀 Your portfolio's debt-to-equity ratio is basically screaming for help.",
        "🏦 Banks are more stable than these debt-loaded disasters you call 'investments'.",
        "📊 Debt ratios this high? These companies are basically borrowing from tomorrow to survive today.",
        "🔥 High leverage works great... until it doesn't. And then you're broke.",
    ],
    "low_liquidity": [
        "💧 Quick ratio < 0.5? These companies can't even pay their bills. Financial anorexia.",
        "🏃 If there's a crash, these stocks can't run - they have no cash.",
        "💀 Low liquidity = high risk of bankruptcy. You're playing with fire.",
        "🚨 These companies are one bad quarter away from insolvency.",
        "💦 Cash is king. Your portfolio has none. Good luck!",
    ],
    "overvalued": [
        "🫠 P/E ratio of 180? What is this, 1999? 'This time it's different' - famous last words.",
        "📉 Paying 200x earnings for companies that don't make money. Peak euphoria energy.",
        "💸 You're paying Lamborghini prices for Pinto performance.",
        "🎈 These valuations are more inflated than my ego after 3 drinks.",
        "🤯 A P/E this high means you're betting on perfection. Spoiler: companies aren't perfect.",
        "📊 Overvalued stocks: because who needs profits when you have hype?",
    ],
    "concentrated": [
        "🎰 50% in one stock? That's not investing, that's gambling.",
        "🔥 All your eggs in one basket and the basket is on fire.",
        "🎲 Concentration builds wealth... until it destroys it. Diversify, dumbass.",
        "💣 One bad earnings report and your portfolio goes boom.",
        "🏴‍☠️ You're not diversified, you're just hoping and praying.",
    ],
    "good_portfolio": [
        "✅ Damn, actual due diligence? In THIS economy? Risk score: 18/100. Boring, stable, perfect.",
        "💰 Blue chips, low debt, good liquidity. You're either a boomer or actually smart. Respect.",
        "🎯 Solid fundamentals, reasonable valuations. You actually read a book, didn't you?",
        "👑 A well-diversified, low-risk portfolio? You must be fun at parties. (But rich.)",
        "🏆 This portfolio fucks. Low risk, high IQ. Chef's kiss.",
        "💎 Finally, someone who doesn't get their investment advice from TikTok.",
        "🧠 Big brain moves. This is what financial literacy looks like.",
    ],
    "moderate_risk": [
        "🟡 Moderate risk. Not terrible, not great. You're the financial equivalent of 'meh'.",
        "⚖️ Balanced portfolio with some red flags. You're playing both sides - might work out!",
        "🤔 Some sketchy picks mixed with solid ones. Is this diversification or confusion?",
        "📊 Not gonna lie, this could go either way. 50/50 shot.",
        "🎪 A little circus, a little strategy. Interesting choices.",
    ],
    "high_beta": [
        "🎢 Beta > 1.5? Your portfolio is a rollercoaster. Hope you don't get motion sickness.",
        "📉 High volatility = high anxiety. Buckle up, it's gonna be a bumpy ride.",
        "⚡ Your portfolio moves faster than my ex's mood swings.",
        "🌊 Volatility this high? You're basically surfing tsunamis.",
    ],
    "negative_fcf": [
        "💸 Negative free cash flow? These companies are bleeding money like a stuck pig.",
        "🔥 Cash burn rate this high means they're one bad quarter from GameOver.",
        "💀 No FCF? That's not a company, that's a money incinerator.",
    ],
    "small_cap_yolo": [
        "🎰 Small caps with no profits? You're basically buying lottery tickets.",
        "🚀 Penny stocks aren't investments, they're bets. And the house always wins.",
        "💀 Micro-cap garbage? Say goodbye to your money.",
    ]
}

ENCOURAGEMENT = [
    "💪 Strong picks! Keep doing your homework.",
    "🎯 Solid fundamentals. You're on the right track.",
    "✅ Low risk, high quality. This is the way.",
    "💎 Blue chip excellence. Boring but beautiful.",
    "🏆 Well done. Financial discipline is sexy.",
]

# ============= SIMPLE EXPLANATIONS =============
SIMPLE_EXPLANATIONS = {
    "fcfAfterSBC": {
        "title": "Free Cash Flow After Stock Comp",
        "simple": "The REAL cash a company generates",
        "why": """
        **Think of it like YOUR paycheck:**
        
        Imagine you make $5,000/month (that's like Revenue).
        - You pay $3,000 in bills (that's Expenses)
        - But wait! You also give your roommate $500 in IOUs instead of cash (that's Stock-Based Compensation)
        - **Your REAL cash left = $5,000 - $3,000 - $500 = $1,500**
        
        That's FCF After SBC! If this number is negative → company is burning cash 🔥
        """,
        "personal_budget": "If your monthly income is $5K but after bills AND IOUs you only have $200 left, that's your FCF After SBC."
    },
    "revenue": {
        "title": "Revenue",
        "simple": "Total money coming in the door",
        "why": "Like your total paycheck BEFORE any deductions. Growing revenue = company is selling more stuff ✅",
        "personal_budget": "Your gross salary before taxes and deductions."
    },
    "operatingIncome": {
        "title": "Operating Income",
        "simple": "Profit from core business operations",
        "why": "This shows if the company's MAIN business is profitable. Excludes interest, taxes, one-time events.",
        "personal_budget": "Your paycheck after regular bills, before credit card interest or tax refunds."
    },
    "netIncome": {
        "title": "Net Income",
        "simple": "Bottom line profit",
        "why": "The final profit after EVERYTHING. But beware: can be manipulated with accounting tricks!",
        "personal_budget": "What's left after ALL expenses, taxes, everything."
    }
}

RATIO_EXPLANATIONS = {
    "Gross Margin": {
        "what": "How much profit per dollar of sales",
        "good": "High margins = pricing power",
        "targets": "Tech: 60-80% | Retail: 20-40%"
    },
    "Operating Margin": {
        "what": "Profit from core business / Revenue",
        "good": "Higher = more efficient",
        "targets": "Good: >15% | Excellent: >25%"
    },
    "Net Margin": {
        "what": "Final profit / Revenue",
        "good": "Higher = more money to bottom line",
        "targets": "Good: >10% | Excellent: >20%"
    },
    "ROE": {
        "what": "Return on Equity",
        "good": "Better use of investor capital",
        "targets": "Good: >15% | Excellent: >20%"
    },
    "ROA": {
        "what": "Return on Assets",
        "good": "Better asset utilization",
        "targets": "Good: >5% | Excellent: >10%"
    }
}

DCF_EXPLANATION = """
### 💰 Discounted Cash Flow (DCF) Valuation
**What is this?** A way to estimate what a stock is REALLY worth based on future cash flows.
**How it works:** 1) Estimate future cash flows 2) "Discount" them 3) Add them up = fair value
**⚠️ Warning:** DCF is sensitive to assumptions (garbage in = garbage out)
"""

GLOSSARY = {
    "FCF After SBC": "Free Cash Flow after Stock Comp - The REAL cash generated",
    "Revenue": "Total money from selling products/services",
    "Operating Income": "Profit from core business operations",
    "Net Income": "Bottom line profit after ALL expenses",
    "P/E Ratio": "Price divided by Earnings - valuation metric",
    "P/S Ratio": "Price divided by Sales. Lower = cheaper. Shows how much you pay for each $1 of revenue. Tech: 5-10 | Retail: 0.5-2",
    "Market Cap": "Total value of all shares",
    "Beta": "Stock volatility vs market (>1 = more volatile)",
    "Sharpe Ratio": "Risk-adjusted return (higher = better)",
    "Max Drawdown": "Biggest drop from peak (lower = better)",
    "CAGR": "Compound Annual Growth Rate - Average yearly growth rate over time. 20% CAGR = doubling every 3.6 years",
    "FCF per Share": "Free Cash Flow divided by shares outstanding. Shows cash generation per share you own",
    "Debt-to-Equity": "Total debt divided by shareholder equity. Measures financial leverage. <1.0 = good, >2.0 = risky",
    "Quick Ratio": "Ability to pay short-term debts without selling inventory. >1.0 = good liquidity"
}

# ============= METRIC DISPLAY NAMES =============
METRIC_DISPLAY_NAMES = {
    'freeCashFlow': 'Free Cash Flow',
    'operatingCashFlow': 'Operating Cash Flow',
    'investingCashFlow': 'Investing Cash Flow',
    'financingCashFlow': 'Financing Cash Flow',
    'capitalExpenditure': 'Capital Expenditures (CapEx)',
    'stockBasedCompensation': 'Stock-Based Compensation',
    'dividendsPaid': 'Dividends Paid',
    'commonStockRepurchased': 'Stock Buybacks',
    'debtRepayment': 'Debt Repayment',
    'commonStockIssued': 'Stock Issued',
    'changeInWorkingCapital': 'Change in Working Capital',
    'depreciationAndAmortization': 'Depreciation & Amortization',
    'revenue': 'Revenue',
    'costOfRevenue': 'Cost of Revenue (COGS)',
    'grossProfit': 'Gross Profit',
    'researchAndDevelopmentExpenses': 'R&D Expenses',
    'sellingGeneralAndAdministrativeExpenses': 'SG&A Expenses',
    'operatingExpenses': 'Operating Expenses',
    'operatingIncome': 'Operating Income',
    'netIncome': 'Net Income',
    'ebitda': 'EBITDA',
    'interestExpense': 'Interest Expense',
    'incomeTaxExpense': 'Income Tax Expense',
    'eps': 'Earnings Per Share (EPS)',
    'epsdiluted': 'Diluted EPS',
    'totalAssets': 'Total Assets',
    'cashAndCashEquivalents': 'Cash & Cash Equivalents',
    'totalCurrentAssets': 'Current Assets',
    'totalLiabilities': 'Total Liabilities',
    'totalDebt': 'Total Debt',
    'longTermDebt': 'Long-Term Debt',
    'shortTermDebt': 'Short-Term Debt',
    'totalStockholdersEquity': 'Shareholders Equity',
    'retainedEarnings': 'Retained Earnings',
    'inventory': 'Inventory',
    'netReceivables': 'Accounts Receivable',
    'totalCurrentLiabilities': 'Current Liabilities',
    'fcfAfterSBC': 'FCF After Stock Compensation'
}

# ============= INDUSTRY BENCHMARKS =============
INDUSTRY_BENCHMARKS = {
    "Technology": {"pe": 25, "ps": 6, "debt_to_equity": 0.5, "quick_ratio": 1.5},
    "Financial Services": {"pe": 12, "ps": 2, "debt_to_equity": 3.0, "quick_ratio": 1.0},
    "Healthcare": {"pe": 20, "ps": 3, "debt_to_equity": 0.8, "quick_ratio": 1.2},
    "Consumer Cyclical": {"pe": 18, "ps": 1.5, "debt_to_equity": 1.0, "quick_ratio": 1.0},
    "Consumer Defensive": {"pe": 22, "ps": 1.0, "debt_to_equity": 0.7, "quick_ratio": 0.8},
    "Energy": {"pe": 15, "ps": 1.2, "debt_to_equity": 1.5, "quick_ratio": 1.0},
    "Industrials": {"pe": 18, "ps": 1.5, "debt_to_equity": 1.2, "quick_ratio": 1.1},
    "Communication Services": {"pe": 20, "ps": 3, "debt_to_equity": 1.5, "quick_ratio": 1.0},
    "Utilities": {"pe": 18, "ps": 2, "debt_to_equity": 2.0, "quick_ratio": 0.9},
    "Real Estate": {"pe": 30, "ps": 5, "debt_to_equity": 2.5, "quick_ratio": 1.0},
    "Basic Materials": {"pe": 15, "ps": 1.5, "debt_to_equity": 1.0, "quick_ratio": 1.2}
}



# ============= S&P 500 AVERAGE BENCHMARKS =============
SP500_BENCHMARKS = {
    'grossProfitMargin': 0.42,  # 42% average for S&P 500
    'operatingProfitMargin': 0.15,  # 15% average
    'netProfitMargin': 0.11,  # 11% average
    'returnOnEquity': 0.18,  # 18% average ROE
    'returnOnAssets': 0.07,  # 7% average ROA
    'returnOnCapitalEmployed': 0.12,  # 12% average ROCE
    'currentRatio': 1.5,  # 1.5x average
    'quickRatio': 1.0,  # 1.0x average
    'debtToEquity': 1.0  # 1.0x average D/E
}

# Meme stocks list
MEME_STOCKS = ["AMC", "GME", "BBBY", "WISH", "CLOV", "BB", "NOK", "SNDL", "NAKD", "WKHS"]

def format_number(num):
    """Format large numbers"""
    if pd.isna(num) or num == 0:
        return "N/A"
    if abs(num) >= 1e12:
        return f"${num/1e12:,.2f}T"
    elif abs(num) >= 1e9:
        return f"${num/1e9:,.1f}B"
    elif abs(num) >= 1e6:
        return f"${num/1e6:,.1f}M"
    else:
        return f"${num:,.0f}"

def explain_metric(metric_name, value, sector=None):
    """Generate explanation for a metric value"""
    exp = METRIC_EXPLANATIONS.get(metric_name)
    if not exp:
        return ""
    
    explanation = f"**{exp.get('short', '')}**\n\n{exp.get('explanation', '')}\n\n✅ {exp.get('good', '')}"
    
    if sector and sector in INDUSTRY_BENCHMARKS:
        if metric_name == "P/E Ratio":
            sector_avg = INDUSTRY_BENCHMARKS[sector]['pe']
            explanation += f"\n\n📊 **{sector} Average: {sector_avg:.1f}**"
        elif metric_name == "Debt-to-Equity":
            sector_avg = INDUSTRY_BENCHMARKS[sector]['debt_to_equity']
            explanation += f"\n\n📊 **{sector} Average: {sector_avg:.2f}**"
        elif metric_name == "Quick Ratio":
            sector_avg = INDUSTRY_BENCHMARKS[sector]['quick_ratio']
            explanation += f"\n\n📊 **{sector} Average: {sector_avg:.2f}**"
    
    return explanation

def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate"""
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return None
    try:
        cagr = (((end_value / start_value) ** (1 / years)) - 1) * 100
        return cagr
    except:
        return None

def calculate_growth_rate(df, column, years=None):
    """Calculate growth rate for a metric over time"""
    if df.empty or column not in df.columns:
        return None
    
    valid_data = df[df[column] > 0].copy()
    if len(valid_data) < 2:
        return None
    
    valid_data = valid_data.sort_values('date')
    start_val = valid_data[column].iloc[0]
    end_val = valid_data[column].iloc[-1]
    
    if years is None:
        years = len(valid_data)
    
    return calculate_cagr(start_val, end_val, years)


def create_financial_chart_with_growth(df, metrics, title, period_label, yaxis_title="Amount ($)"):
    """Create financial chart with y-axis padding and return growth rates"""
    if df.empty:
        return None, {}
    
    df_reversed = df.iloc[::-1].reset_index(drop=True)
    fig = go.Figure()
    colors = ['#00D9FF', '#FFD700', '#9D4EDD']
    growth_rates = {}
    
    for idx, metric in enumerate(metrics):
        if metric in df_reversed.columns:
            values = df_reversed[metric].values
            if len(values) >= 2 and values[0] != 0:
                growth_rate = ((values[0] - values[-1]) / abs(values[-1])) * 100
                growth_rates[metric] = growth_rate
            
            fig.add_trace(go.Bar(
                x=df_reversed['date'],
                y=values,
                name=metric.replace('_', ' ').title(),
                marker_color=colors[idx % len(colors)],
                text=[f'${val/1e9:.1f}B' if abs(val) >= 1e9 else f'${val/1e6:.1f}M' for val in values],
                textposition='outside',
                textfont=dict(size=10)
            ))
    
    all_values = []
    for metric in metrics:
        if metric in df_reversed.columns:
            all_values.extend(df_reversed[metric].values)
    
    if all_values:
        max_val = max(all_values)
        min_val = min(all_values)
        # Tighter Y-axis padding (5-7% above max) so bars nearly reach top
        y_range_max = max_val * 1.07 if max_val > 0 else max_val * 0.93
        y_range_min = min_val * 1.05 if min_val < 0 else 0
        fig.update_layout(yaxis=dict(range=[y_range_min, y_range_max]))
    
    fig.update_layout(
        title=title,
        xaxis_title=period_label,
        yaxis_title=yaxis_title,
        barmode='group',
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig, growth_rates

def create_ratio_trend_chart(df, metric_name, metric_column, title, sector=None):
    """Create line chart for financial ratio trends with S&P 500 and industry benchmarks"""
    if df.empty or metric_column not in df.columns:
        return None
    
    df_reversed = df.iloc[::-1].reset_index(drop=True)
    values = df_reversed[metric_column].values
    
    if 'margin' in metric_column.lower() or 'return' in metric_column.lower():
        values = values * 100
        y_suffix = '%'
        multiplier = 100
    else:
        y_suffix = ''
        multiplier = 1
    
    fig = go.Figure()
    
    # Add company line
    fig.add_trace(go.Scatter(
        x=df_reversed['date'],
        y=values,
        mode='lines+markers',
        name=metric_name,
        line=dict(color='#00D9FF', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(0, 217, 255, 0.2)'
    ))
    
    # Add S&P 500 benchmark line
    if metric_column in SP500_BENCHMARKS:
        sp500_value = SP500_BENCHMARKS[metric_column] * multiplier
        fig.add_trace(go.Scatter(
            x=df_reversed['date'],
            y=[sp500_value] * len(df_reversed),
            mode='lines',
            name='S&P 500 Avg',
            line=dict(color='#FFD700', width=2, dash='dash'),
            hovertemplate=f'S&P 500: {sp500_value:.1f}{y_suffix}<extra></extra>'
        ))
    
    # Add industry benchmark line if sector provided
    if sector and sector in INDUSTRY_BENCHMARKS:
        industry_data = INDUSTRY_BENCHMARKS[sector]
        
        # Map metric columns to industry benchmark keys
        metric_map = {
            'grossProfitMargin': None,  # Not in industry benchmarks
            'operatingProfitMargin': None,
            'netProfitMargin': None,
            'returnOnEquity': None,
            'returnOnAssets': None,
            'returnOnCapitalEmployed': None,
            'currentRatio': 'quick_ratio',  # Approximate
            'quickRatio': 'quick_ratio',
            'debtToEquity': 'debt_to_equity'
        }
        
        if metric_column in metric_map and metric_map[metric_column] and metric_map[metric_column] in industry_data:
            industry_value = industry_data[metric_map[metric_column]] * multiplier if multiplier == 100 else industry_data[metric_map[metric_column]]
            
            fig.add_trace(go.Scatter(
                x=df_reversed['date'],
                y=[industry_value] * len(df_reversed),
                mode='lines',
                name=f'{sector} Avg',
                line=dict(color='#9D4EDD', width=2, dash='dot'),
                hovertemplate=f'{sector}: {industry_value:.1f}{y_suffix}<extra></extra>'
            ))
    
    # Add growth annotation
    if len(values) >= 2 and values[0] != 0:
        growth = ((values[-1] - values[0]) / abs(values[0])) * 100
        fig.add_annotation(
            x=df_reversed['date'].iloc[-1],
            y=values[-1],
            text=f"Growth: {growth:+.1f}%",
            showarrow=True,
            arrowhead=2,
            bgcolor='rgba(0, 217, 255, 0.8)',
            font=dict(color='white')
        )
    
    fig.update_layout(
        title=title,
        xaxis_title='Period',
        yaxis_title=f'{metric_name} ({y_suffix})' if y_suffix else metric_name,
        height=400,
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig



# ============= MY FAVORITE METRICS & WHY =============
MY_TOP_5_METRICS = {
    'fcfAfterSBC': {
        'name': 'FCF After Stock Compensation',
        'why': "This is THE most important metric for me. It shows the true cash a company generates after accounting for stock-based compensation, which dilutes existing shareholders. Many companies hide dilution, but this reveals the real cash impact.",
        'rank': 1
    },
    'operatingIncome': {
        'name': 'Operating Income Growth',
        'why': "Shows if the core business is actually improving. Revenue can grow while operations lose money, but rising operating income means the business model works and is getting more efficient.",
        'rank': 2
    },
    'freeCashFlow': {
        'name': 'Free Cash Flow Growth',
        'why': "Cash is king. A company can manipulate earnings, but cash flow doesn't lie. Growing FCF means the company can fund growth, pay dividends, or buy back stock without taking on debt.",
        'rank': 3
    },
    'revenue': {
        'name': 'Revenue Growth',
        'why': "The top line tells you if the company is winning in its market. Consistent revenue growth means customers want the product and the company is taking market share.",
        'rank': 4
    },
    'quickRatio': {
        'name': 'Quick Ratio Growth',
        'why': "This tells me if the company can handle a crisis. A rising quick ratio means growing liquidity - they can pay bills even if revenue drops suddenly. It's the ultimate safety metric.",
        'rank': 5
    }
}

def show_why_these_metrics(metric_type="financial_statements"):
    """Display why I focus on these specific metrics"""
    if metric_type == "financial_statements":
        st.sidebar.markdown("### 💡 Why These Metrics?")
        st.sidebar.info("""
**I focus on cash flow metrics because:**
- Cash can't be manipulated like earnings
- FCF after SBC shows TRUE shareholder value
- Operating income reveals business quality
- Revenue growth shows market demand
- Quick ratio = safety cushion

These tell the real story!
        """)
        
        with st.sidebar.expander("🏆 My Top 5 Favorites"):
            for key, info in sorted(MY_TOP_5_METRICS.items(), key=lambda x: x[1]['rank']):
                st.markdown(f"**#{info['rank']}: {info['name']}**")
                st.caption(info['why'])
                st.markdown("---")

def get_available_metrics(df, exclude_cols=['date', 'symbol', 'reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period', 'link', 'finalLink']):
    """Get all numeric columns from dataframe for dropdown"""
    if df.empty:
        return []
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    available = [col for col in numeric_cols if col not in exclude_cols]
    
    return [(METRIC_DISPLAY_NAMES.get(col, col.replace('_', ' ').title()), col) for col in available]

def show_why_it_matters(metric_key):
    """Show explanation for a metric"""
    if metric_key in SIMPLE_EXPLANATIONS:
        exp = SIMPLE_EXPLANATIONS[metric_key]
        st.markdown(f"""
        <div class="why-box">
        <h4>💡 Why {exp['title']} Matters</h4>
        <p><strong>{exp['simple']}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📚 Learn More"):
            st.markdown(exp['why'])
            if 'personal_budget' in exp:
                st.markdown(f"""
                <div class="personal-budget">
                <strong>🏠 Like Your Personal Budget:</strong><br>
                {exp['personal_budget']}
                </div>
                """, unsafe_allow_html=True)

def calculate_debt_to_equity(balance_df):
    """Calculate Debt-to-Equity ratio"""
    try:
        if balance_df.empty:
            return 0
        
        latest = balance_df.iloc[-1]
        
        total_debt = latest.get('totalDebt', 0)
        equity = latest.get('totalStockholdersEquity', 0)
        
        if equity and equity > 0:
            return total_debt / equity
        
        return 0
    except:
        return 0

def calculate_quick_ratio(balance_df):
    """Calculate Quick Ratio"""
    try:
        if balance_df.empty:
            return 0
        
        latest = balance_df.iloc[-1]
        
        current_assets = latest.get('totalCurrentAssets', 0)
        inventory = latest.get('inventory', 0)
        current_liabilities = latest.get('totalCurrentLiabilities', 0)
        
        if current_liabilities and current_liabilities > 0:
            return (current_assets - inventory) / current_liabilities
        
        return 0
    except:
        return 0

def get_industry_benchmark(sector, metric):
    """Get industry benchmark"""
    if sector in INDUSTRY_BENCHMARKS:
        return INDUSTRY_BENCHMARKS[sector].get(metric, 0)
    return 0

def get_roast_comment(portfolio_data, total_risk_score):
    """Generate roast/comment based on portfolio - RANDOMIZED"""
    comments = []
    
    meme_count = sum(1 for stock in portfolio_data if stock['ticker'] in MEME_STOCKS)
    if meme_count > 0:
        comments.append(random.choice(ROASTS['meme_stocks']))
    
    avg_de = sum(stock['de_ratio'] for stock in portfolio_data if stock['de_ratio'] > 0) / max(len([s for s in portfolio_data if s['de_ratio'] > 0]), 1)
    if avg_de > 2.5:
        comments.append(random.choice(ROASTS['high_debt']))
    
    avg_qr = sum(stock['quick_ratio'] for stock in portfolio_data if stock['quick_ratio'] > 0) / max(len([s for s in portfolio_data if s['quick_ratio'] > 0]), 1)
    if avg_qr < 0.8:
        comments.append(random.choice(ROASTS['low_liquidity']))
    
    avg_pe = sum(stock['pe'] for stock in portfolio_data if stock['pe'] > 0) / max(len([s for s in portfolio_data if s['pe'] > 0]), 1)
    if avg_pe > 50:
        comments.append(random.choice(ROASTS['overvalued']))
    
    max_allocation = max(stock['allocation'] for stock in portfolio_data)
    if max_allocation > 40:
        comments.append(random.choice(ROASTS['concentrated']))
    
    avg_beta = sum(stock['beta'] * stock['allocation']/100 for stock in portfolio_data)
    if avg_beta > 1.5:
        comments.append(random.choice(ROASTS['high_beta']))
    
    if total_risk_score > 70:
        comments.insert(0, "🚨 **YIKES. Let's unpack this disaster:**")
    elif total_risk_score > 40:
        comments.insert(0, random.choice(ROASTS['moderate_risk']))
    elif total_risk_score < 25:
        comments.insert(0, random.choice(ROASTS['good_portfolio']))
    
    if not comments:
        return random.choice(ENCOURAGEMENT)
    
    return "\n\n".join(comments[:3])

def calculate_risk_score(ticker, quote, balance_df, cash_df, sector):
    """Calculate comprehensive risk score"""
    risk_score = 0
    risk_factors = []
    
    if ticker in MEME_STOCKS:
        risk_score += 25
        risk_factors.append(f"Meme stock detected ({ticker})")
    
    beta = quote.get('beta', 1.0) if quote else 1.0
    if beta > 1.5:
        risk_score += 30
        risk_factors.append("Very high volatility (Beta > 1.5)")
    elif beta > 1.2:
        risk_score += 20
        risk_factors.append("High volatility (Beta > 1.2)")
    elif beta > 1.0:
        risk_score += 10
        risk_factors.append("Moderate volatility (Beta > 1.0)")
    
    de_ratio = calculate_debt_to_equity(balance_df)
    industry_de = get_industry_benchmark(sector, 'debt_to_equity')
    
    if de_ratio > 3.0:
        risk_score += 30
        risk_factors.append(f"Extremely high debt (D/E: {de_ratio:.2f})")
    elif de_ratio > 2.0:
        risk_score += 20
        risk_factors.append(f"High debt (D/E: {de_ratio:.2f})")
    elif de_ratio > industry_de * 1.5:
        risk_score += 15
        risk_factors.append(f"Above-industry debt (D/E: {de_ratio:.2f} vs industry {industry_de:.2f})")
    
    quick_ratio = calculate_quick_ratio(balance_df)
    if quick_ratio < 0.5:
        risk_score += 20
        risk_factors.append(f"Liquidity crisis risk (Quick Ratio: {quick_ratio:.2f})")
    elif quick_ratio < 1.0:
        risk_score += 10
        risk_factors.append(f"Low liquidity (Quick Ratio: {quick_ratio:.2f})")
    
    if not cash_df.empty and 'freeCashFlow' in cash_df.columns:
        latest_fcf = cash_df['freeCashFlow'].iloc[-1]
        if latest_fcf < 0:
            risk_score += 20
            risk_factors.append("Burning cash (Negative FCF)")
        elif latest_fcf < cash_df['freeCashFlow'].mean() * 0.5:
            risk_score += 10
            risk_factors.append("Declining cash generation")
    
    return min(risk_score, 100), risk_factors

# ============= FMP API FUNCTIONS (OPTIMIZED WITH CACHING) =============

@st.cache_data(ttl=3600)
def get_all_stocks():
    """Get list of stocks with fallback"""
    try:
        url = f"{BASE_URL}/search-name?query=&limit=5000&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=15)
        data = response.json()
        stocks = {}
        for stock in data:
            if stock.get('symbol') and stock.get('name'):
                symbol = stock['symbol'].upper()
                name = stock['name'].upper()
                stocks[symbol] = stock['name']
                stocks[name] = symbol
        return stocks
    except:
        return {
            "AAPL": "Apple Inc.", "APPLE": "AAPL", "MSFT": "Microsoft", "MICROSOFT": "MSFT",
            "GOOGL": "Alphabet", "GOOGLE": "GOOGL", "AMZN": "Amazon", "AMAZON": "AMZN",
            "NVDA": "NVIDIA", "NVIDIA": "NVDA", "META": "Meta", "FACEBOOK": "META",
            "TSLA": "Tesla", "TESLA": "TSLA", "JPM": "JPMorgan", "JPMORGAN": "JPM",
            "V": "Visa", "VISA": "V", "WMT": "Walmart", "WALMART": "WMT"
        }

# ============= COMPANY NAME TO TICKER MAPPING =============
COMPANY_NAME_TO_TICKER = {
    # Magnificent 7
    "apple": "AAPL", "apple inc": "AAPL", "aapl": "AAPL",
    "microsoft": "MSFT", "microsoft corp": "MSFT", "msft": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL", "alphabet inc": "GOOGL", "googl": "GOOGL", "goog": "GOOGL",
    "amazon": "AMZN", "amazon.com": "AMZN", "amzn": "AMZN",
    "nvidia": "NVDA", "nvda": "NVDA",
    "meta": "META", "meta platforms": "META", "facebook": "META", "fb": "META",
    "tesla": "TSLA", "tsla": "TSLA",
    # Other popular stocks
    "netflix": "NFLX", "nflx": "NFLX",
    "disney": "DIS", "walt disney": "DIS", "dis": "DIS",
    "berkshire": "BRK.B", "berkshire hathaway": "BRK.B", "brk": "BRK.B",
    "jpmorgan": "JPM", "jp morgan": "JPM", "jpm": "JPM",
    "visa": "V",
    "mastercard": "MA", "ma": "MA",
    "walmart": "WMT", "wmt": "WMT",
    "costco": "COST", "cost": "COST",
    "coca-cola": "KO", "coca cola": "KO", "coke": "KO", "ko": "KO",
    "pepsi": "PEP", "pepsico": "PEP", "pep": "PEP",
    "intel": "INTC", "intc": "INTC",
    "amd": "AMD", "advanced micro devices": "AMD",
    "paypal": "PYPL", "pypl": "PYPL",
    "adobe": "ADBE", "adbe": "ADBE",
    "salesforce": "CRM", "crm": "CRM",
    "oracle": "ORCL", "orcl": "ORCL",
    "ibm": "IBM",
    "boeing": "BA", "ba": "BA",
    "chevron": "CVX", "cvx": "CVX",
    "exxon": "XOM", "exxon mobil": "XOM", "xom": "XOM",
    "pfizer": "PFE", "pfe": "PFE",
    "johnson & johnson": "JNJ", "j&j": "JNJ", "jnj": "JNJ",
    "unitedhealth": "UNH", "unh": "UNH",
    "home depot": "HD", "hd": "HD",
    "mcdonalds": "MCD", "mcd": "MCD",
    "nike": "NKE", "nke": "NKE",
    "starbucks": "SBUX", "sbux": "SBUX",
    "uber": "UBER",
    "airbnb": "ABNB", "abnb": "ABNB",
    "spotify": "SPOT", "spot": "SPOT",
    "zoom": "ZM", "zm": "ZM",
    "snowflake": "SNOW", "snow": "SNOW",
    "palantir": "PLTR", "pltr": "PLTR",
    "coinbase": "COIN", "coin": "COIN",
    "robinhood": "HOOD", "hood": "HOOD",
    "gamestop": "GME", "gme": "GME",
    "amc": "AMC", "amc entertainment": "AMC",
    "spy": "SPY", "s&p 500": "SPY", "s&p": "SPY",
    "qqq": "QQQ", "nasdaq": "QQQ",
}

# Magnificent 7 tickers for default news
MAG_7_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]

def resolve_company_to_ticker(query):
    """Convert company name or ticker to standardized ticker symbol"""
    if not query:
        return None
    
    query_lower = query.strip().lower()
    
    # Check direct mapping first
    if query_lower in COMPANY_NAME_TO_TICKER:
        return COMPANY_NAME_TO_TICKER[query_lower]
    
    # Check if it's already a valid ticker (uppercase)
    # Support tickers with dots (BRK.B) and dashes (BRK-B)
    query_upper = query.strip().upper()
    query_clean = query_upper.replace('.', '').replace('-', '')
    
    # Valid ticker patterns: 1-5 letters, optionally followed by .X or -X (class shares)
    # Examples: AAPL, MSFT, BRK.B, BRK-B, RDS.A
    if len(query_clean) <= 6 and query_clean.isalpha():
        # Normalize dash to dot for FMP API compatibility (BRK-B -> BRK.B)
        return query_upper.replace('-', '.')
    
    # Fuzzy match - check if query is contained in any company name
    for name, ticker in COMPANY_NAME_TO_TICKER.items():
        if query_lower in name or name in query_lower:
            return ticker
    
    # Default: return as-is (uppercase), normalize dashes to dots
    return query_upper.replace('-', '.')

def smart_search_ticker(search_term):
    """Smart search with company name support"""
    search_term = search_term.upper().strip()
    all_stocks = get_all_stocks()
    
    if search_term in all_stocks and len(search_term) <= 5:
        return search_term, all_stocks[search_term]
    
    if search_term in all_stocks:
        return all_stocks[search_term], search_term
    
    tickers = [k for k in all_stocks.keys() if len(k) <= 5]
    close_tickers = get_close_matches(search_term, tickers, n=1, cutoff=0.6)
    if close_tickers:
        return close_tickers[0], all_stocks[close_tickers[0]]
    
    names = [k for k in all_stocks.keys() if len(k) > 5]
    close_names = get_close_matches(search_term, names, n=1, cutoff=0.4)
    if close_names:
        return all_stocks[close_names[0]], close_names[0]
    
    for key, value in all_stocks.items():
        if len(key) > 5 and search_term in key:
            return value, key
    
    return search_term, search_term

@st.cache_data(ttl=300)
def get_quote(ticker):
    """Get quote"""
    url = f"{BASE_URL}/quote?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except:
        return None

@st.cache_data(ttl=1800)
def get_profile(ticker):
    """Get company profile"""
    url = f"{BASE_URL}/profile?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except:
        return None

def get_dividend_yield(ticker, price):
    """
    Dividend yield (%) from FMP profile endpoint.
    Uses lastDividend (fallback lastDiv). Assumes quarterly payouts (x4) for annualization.
    Fail-soft: returns None if missing.
    """
    try:
        if not price or price <= 0:
            return None
        
        # Get profile which has lastDiv field
        profile = get_profile(ticker)
        if not profile:
            return None
        last_div_raw = profile.get("lastDividend") or profile.get("lastDiv")
        last_div = float(last_div_raw) if last_div_raw not in (None, "") else None

        if last_div and last_div > 0:
            # Calculate yield: (annual dividend / price) * 100
            annual_div = last_div
            yield_pct = (annual_div / price) * 100
            
            # Sanity check (yields rarely > 20%)
            if 0 < yield_pct < 20:
                return yield_pct
        
        return None
        
    except Exception as e:
        return None


def get_company_logo(ticker):
    """Get company logo URL from FMP profile"""
    profile = get_profile(ticker)
    if profile and 'image' in profile and profile['image']:
        return profile['image']
    return None

def display_stock_with_logo(ticker, size=30):
    """Display stock ticker with logo inline using HTML"""
    logo_url = get_company_logo(ticker)
    if logo_url:
        return f'<img src="{logo_url}" width="{size}" height="{size}" style="vertical-align: middle; margin-right: 8px; border-radius: 4px;"> <strong>{ticker}</strong>'
    return f'<strong>{ticker}</strong>'

def get_stock_specific_news(ticker, limit=10):
    """Get STOCK-SPECIFIC news using Perplexity API (FMP news endpoint is legacy)"""
    import json
    
    perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY', '')
    if not perplexity_api_key:
        return []
    
    try:
        # Use Perplexity to get recent news about the stock
        perplexity_url = "https://api.perplexity.ai/chat/completions"
        perplexity_headers = {
            "Authorization": f"Bearer {perplexity_api_key}",
            "Content-Type": "application/json"
        }
        perplexity_payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "You are a financial news aggregator. Return ONLY a JSON array of news articles. No other text."},
                {"role": "user", "content": f"""Find the {limit} most recent news articles about {ticker} stock from the past 7 days.
Return ONLY a valid JSON array with this exact format (no other text):
[
  {{"title": "Article headline", "url": "https://source.com/article", "publishedDate": "2025-12-30", "source": "Source Name"}},
  ...
]
Include real URLs from reputable financial news sources like Reuters, Bloomberg, CNBC, Yahoo Finance, MarketWatch, etc."""}
            ],
            "max_tokens": 1500,
            "temperature": 0.1
        }
        
        response = requests.post(perplexity_url, headers=perplexity_headers, json=perplexity_payload, timeout=15)
        if response.status_code == 200:
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Try to parse JSON from the response
            try:
                # Find JSON array in the response
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    articles = json.loads(json_str)
                    if isinstance(articles, list) and len(articles) > 0:
                        return articles[:limit]
            except json.JSONDecodeError:
                pass
    except Exception as e:
        pass
    
    return []


def call_perplexity_json(prompt: str, max_tokens: int = 2000, temperature: float = 0.1) -> dict:
    """
    Calls Perplexity and returns parsed JSON dict if possible, else None.
    Enforces JSON-only responses with no markdown.
    
    Args:
        prompt: The user prompt (should instruct Perplexity to return JSON only)
        max_tokens: Maximum response tokens
        temperature: Response randomness (lower = more deterministic)
    
    Returns:
        dict if JSON parsed successfully, None otherwise
    """
    import json
    
    perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY', '')
    if not perplexity_api_key:
        return None
    
    try:
        perplexity_url = "https://api.perplexity.ai/chat/completions"
        perplexity_headers = {
            "Authorization": f"Bearer {perplexity_api_key}",
            "Content-Type": "application/json"
        }
        perplexity_payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "You are a technical assistant. Return ONLY valid JSON with no markdown, no code blocks, no preamble, no explanation. Just pure JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(perplexity_url, headers=perplexity_headers, json=perplexity_payload, timeout=20)
        
        if response.status_code == 200:
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if not content:
                return None
            
            # Try to parse JSON from the response
            try:
                # First try direct parse
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                content = content.strip()
                
                # Remove markdown code fences
                if content.startswith('```json'):
                    content = content[7:]
                elif content.startswith('```'):
                    content = content[3:]
                
                if content.endswith('```'):
                    content = content[:-3]
                
                content = content.strip()
                
                # Try parsing again
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Last resort: find JSON object/array
                    start_obj = content.find('{')
                    start_arr = content.find('[')
                    
                    if start_obj == -1 and start_arr == -1:
                        return None
                    
                    # Determine which comes first
                    if start_obj != -1 and (start_arr == -1 or start_obj < start_arr):
                        # Object
                        end = content.rfind('}')
                        if end > start_obj:
                            json_str = content[start_obj:end+1]
                            return json.loads(json_str)
                    else:
                        # Array
                        end = content.rfind(']')
                        if end > start_arr:
                            json_str = content[start_arr:end+1]
                            return json.loads(json_str)
                    
                    return None
        
        return None
    
    except Exception as e:
        return None


@st.cache_data(ttl=3600)
def get_earnings_calendar(ticker):
    """Get next earnings date"""
    url = f"{BASE_URL}/earnings-calendar?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                today = datetime.now()
                for earning in data:
                    earning_date = datetime.strptime(earning.get('date', ''), '%Y-%m-%d')
                    if earning_date >= today:
                        return earning
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_treasury_rates():
    """Get current treasury rates"""
    rates = {}
    
    try:
        url = f"{BASE_URL}/treasury?from=10Y&to=10Y&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                rates['10Y'] = data[0].get('yield', 0)
    except:
        rates['10Y'] = 0
    
    try:
        url = f"{BASE_URL}/treasury?from=2Y&to=2Y&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                rates['2Y'] = data[0].get('yield', 0)
    except:
        rates['2Y'] = 0
    
    try:
        url = f"{BASE_URL}/treasury?from=30Y&to=30Y&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                rates['30Y'] = data[0].get('yield', 0)
    except:
        rates['30Y'] = 0
    
    return rates

@st.cache_data(ttl=3600)
def get_sp500_performance():
    """Get S&P 500 YTD performance - FIXED"""
    try:
        url = f"{BASE_URL}/historical-price-eod/light?symbol=%5EGSPC&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                
                current_year = datetime.now().year
                ytd_data = df[df['date'].dt.year == current_year]
                
                if len(ytd_data) > 1:
                    price_col = 'close' if 'close' in ytd_data.columns else 'price'
                    start_price = ytd_data[price_col].iloc[0]
                    latest_price = ytd_data[price_col].iloc[-1]
                    
                    ytd_return = ((latest_price - start_price) / start_price) * 100
                    return ytd_return
                
                if len(df) > 252:
                    price_col = 'close' if 'close' in df.columns else 'price'
                    start_price = df[price_col].iloc[-252]
                    latest_price = df[price_col].iloc[-1]
                    annual_return = ((latest_price - start_price) / start_price) * 100
                    return annual_return
    except:
        pass
    
    try:
        url = f"{BASE_URL}/historical-price-eod/light?symbol=SPY&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                
                current_year = datetime.now().year
                ytd_data = df[df['date'].dt.year == current_year]
                
                if len(ytd_data) > 1:
                    price_col = 'close' if 'close' in ytd_data.columns else 'price'
                    start_price = ytd_data[price_col].iloc[0]
                    latest_price = ytd_data[price_col].iloc[-1]
                    
                    ytd_return = ((latest_price - start_price) / start_price) * 100
                    return ytd_return
    except:
        pass
    
    return 0

@st.cache_data(ttl=3600)
def get_price_target_summary(ticker):
    """Get price target summary"""
    url = f"{BASE_URL}/price-target-summary?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data and len(data) > 0 else None
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_price_target_consensus(ticker):
    """Get price target consensus from FMP stable API"""
    url = f"{BASE_URL}/price-target-consensus?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=86400)
def get_ai_price_target(ticker, company_name):
    """Fallback: Get price target from Perplexity AI if FMP has no data"""
    if not PERPLEXITY_API_KEY:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "user",
                    "content": f"What is the current average 12-month analyst price target for {company_name} ({ticker})? Just give me the dollar amount as a number, nothing else. If you don't know, say 'unknown'."
                }
            ],
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            import re
            match = re.search(r'\$?([\d,]+\.?\d*)', content)
            if match:
                price_str = match.group(1).replace(',', '')
                return float(price_str)
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_shares_float(ticker):
    """Get shares float"""
    url = f"{BASE_URL}/shares-float?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except:
        pass
    return {}

@st.cache_data(ttl=3600)
def get_ratios_ttm(ticker):
    """Get TTM ratios"""
    url = f"{BASE_URL}/ratios-ttm?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except:
        pass
    
    url2 = f"{BASE_URL}/ratios-ttm/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url2, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except:
        pass
    
    return {}

@st.cache_data(ttl=3600)
def get_income_statement(ticker, period='annual', limit=5):
    """Get income statement"""
    url = f"{BASE_URL}/income-statement?symbol={ticker}&period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_balance_sheet(ticker, period='annual', limit=5):
    """Get balance sheet"""
    url = f"{BASE_URL}/balance-sheet-statement?symbol={ticker}&period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_cash_flow(ticker, period='annual', limit=5):
    """Get cash flow"""
    url = f"{BASE_URL}/cash-flow-statement?symbol={ticker}&period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_financial_ratios(ticker, period='annual', limit=5):
    """Get financial ratios"""
    url = f"{BASE_URL}/ratios?symbol={ticker}&period={period}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_historical_price(ticker, years=5):
    """Get historical prices"""
    url = f"{BASE_URL}/historical-price-eod/light?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if data and isinstance(data, list):
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            cutoff = datetime.now() - timedelta(days=years*365)
            df = df[df['date'] >= cutoff]
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_historical_ohlc(ticker, years=5):
    """Get historical OHLC data for candlestick charts from FMP"""
    
    # Use the CORRECT endpoint from FMP docs: /historical-price-eod/full
    url = f"{BASE_URL}/historical-price-eod/full?symbol={ticker}&apikey={FMP_API_KEY}"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                cutoff = datetime.now() - timedelta(days=years*365)
                df = df[df['date'] >= cutoff]
                return df
    except:
        pass
    
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_price_target(ticker):
    """Get price target consensus"""
    url = f"{BASE_URL}/price-target-consensus?symbol={ticker}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0] if data and len(data) > 0 else None
    except:
        return None

def get_eps_ttm(ticker, income_df):
    """Get TTM EPS"""
    try:
        quarterly_df = get_income_statement(ticker, 'quarter', 4)
        
        if not quarterly_df.empty:
            if 'epsdiluted' in quarterly_df.columns:
                ttm_eps = quarterly_df['epsdiluted'].head(4).sum()
                if ttm_eps and ttm_eps > 0:
                    return ttm_eps
            
            if 'eps' in quarterly_df.columns:
                ttm_eps = quarterly_df['eps'].head(4).sum()
                if ttm_eps and ttm_eps > 0:
                    return ttm_eps
        
        if not income_df.empty:
            if 'epsdiluted' in income_df.columns:
                eps = income_df['epsdiluted'].iloc[-1]
                if eps and eps > 0:
                    return eps
            
            if 'eps' in income_df.columns:
                eps = income_df['eps'].iloc[-1]
                if eps and eps > 0:
                    return eps
        
        return 0
    except:
        return 0

def get_shares_outstanding(ticker, quote, shares_float_data):
    """Get shares outstanding"""
    if shares_float_data and isinstance(shares_float_data, dict):
        shares = shares_float_data.get('outstandingShares', 0)
        if shares and shares > 0:
            return shares
    
    if quote:
        shares = quote.get('sharesOutstanding', 0)
        if shares and shares > 0:
            return shares
    
    if quote:
        market_cap = quote.get('marketCap', 0)
        price = quote.get('price', 0)
        if market_cap and price and price > 0:
            return market_cap / price
    
    return 0

def calculate_fcf_per_share(ticker, cash_df, quote):
    """Calculate FCF per share with MULTIPLE FALLBACKS - FIXED"""
    try:
        shares_float_data = get_shares_float(ticker)
        shares = get_shares_outstanding(ticker, quote, shares_float_data)
        
        if not shares or shares <= 0:
            return 0
        
        if not cash_df.empty and 'freeCashFlow' in cash_df.columns:
            latest_fcf = cash_df['freeCashFlow'].iloc[-1]
            if latest_fcf and latest_fcf != 0:
                return latest_fcf / shares
        
        if not cash_df.empty:
            ocf = cash_df.get('operatingCashFlow', pd.Series([0])).iloc[-1] if 'operatingCashFlow' in cash_df.columns else 0
            capex = cash_df.get('capitalExpenditure', pd.Series([0])).iloc[-1] if 'capitalExpenditure' in cash_df.columns else 0
            
            if ocf and ocf != 0:
                fcf = ocf + capex
                if fcf != 0:
                    return fcf / shares
        
        if not cash_df.empty and 'netCashProvidedByOperatingActivities' in cash_df.columns:
            net_cash = cash_df['netCashProvidedByOperatingActivities'].iloc[-1]
            capex = cash_df.get('capitalExpenditure', pd.Series([0])).iloc[-1] if 'capitalExpenditure' in cash_df.columns else 0
            
            if net_cash and net_cash != 0:
                fcf = net_cash + capex
                if fcf != 0:
                    return fcf / shares
        
        quarterly_cash = get_cash_flow(ticker, 'quarter', 4)
        if not quarterly_cash.empty and 'freeCashFlow' in quarterly_cash.columns:
            ttm_fcf = quarterly_cash['freeCashFlow'].head(4).sum()
            if ttm_fcf and ttm_fcf != 0:
                return ttm_fcf / shares
        
        try:
            url = f"{BASE_URL}/key-metrics-ttm?symbol={ticker}&apikey={FMP_API_KEY}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    fcf_per_share = data[0].get('freeCashFlowPerShare', 0)
                    if fcf_per_share and fcf_per_share != 0:
                        return fcf_per_share
        except:
            pass
        
        return 0
        
    except:
        return 0

def get_pe_ratio(ticker, quote, ratios_ttm, income_df):
    """Calculate P/E ratio"""
    if quote:
        price = quote.get('price', 0)
        if price and price > 0:
            eps_ttm = get_eps_ttm(ticker, income_df)
            if eps_ttm and eps_ttm > 0:
                return price / eps_ttm
    
    if ratios_ttm and isinstance(ratios_ttm, dict):
        pe = ratios_ttm.get('peRatioTTM', 0)
        if pe and pe > 0:
            return pe
    
    if quote:
        pe = quote.get('pe', 0)
        if pe and pe > 0:
            return pe
    
    return 0

def get_ps_ratio(ticker, ratios_ttm):
    """Get P/S ratio"""
    if ratios_ttm and isinstance(ratios_ttm, dict):
        ps = ratios_ttm.get('priceToSalesRatioTTM', 0)
        if ps and ps > 0:
            return ps
    
    return 0

# ============= AI RISK ANALYSIS (PERPLEXITY API) =============
@st.cache_data(ttl=3600)
def get_ai_risk_analysis(ticker, company_name):
    """Use Perplexity API to analyze recent news and identify red/green flags"""
    if not USE_AI_ANALYSIS or not PERPLEXITY_API_KEY:
        return None
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Analyze the stock {ticker} ({company_name}) based on news from the last 30 days.

Provide your analysis in this EXACT format (use simple language a middle schooler would understand):

RED FLAGS (3 concerns/risks):
1. [First concern in 1-2 simple sentences]
2. [Second concern in 1-2 simple sentences]  
3. [Third concern in 1-2 simple sentences]

GREEN FLAGS (3 positive signs):
1. [First positive in 1-2 simple sentences]
2. [Second positive in 1-2 simple sentences]
3. [Third positive in 1-2 simple sentences]

OVERALL: [One sentence summary - is this stock looking good or risky right now?]

Remember: Use simple words like "the company is making less money" instead of "declining revenue margins"."""

        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "You are a helpful financial analyst who explains things simply for beginners. Always search for recent news about the company."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 800
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            return parse_ai_risk_response(content)
        else:
            return None
    except Exception as e:
        return None

def parse_ai_risk_response(content):
    """Parse the AI response into structured red/green flags"""
    if not content:
        return None
    
    result = {
        "red_flags": [],
        "green_flags": [],
        "overall": ""
    }
    
    lines = content.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if 'RED FLAG' in line.upper():
            current_section = 'red'
        elif 'GREEN FLAG' in line.upper():
            current_section = 'green'
        elif 'OVERALL' in line.upper():
            current_section = 'overall'
            if ':' in line:
                result['overall'] = line.split(':', 1)[1].strip()
        elif line and line[0].isdigit() and '.' in line[:3]:
            flag_text = line.split('.', 1)[1].strip() if '.' in line else line
            if current_section == 'red' and len(result['red_flags']) < 3:
                result['red_flags'].append(flag_text)
            elif current_section == 'green' and len(result['green_flags']) < 3:
                result['green_flags'].append(flag_text)
        elif current_section == 'overall' and not result['overall']:
            result['overall'] = line
    
    if len(result['red_flags']) < 3:
        result['red_flags'].extend(["No major concerns found in recent news"] * (3 - len(result['red_flags'])))
    if len(result['green_flags']) < 3:
        result['green_flags'].extend(["Stable performance reported"] * (3 - len(result['green_flags'])))
    if not result['overall']:
        result['overall'] = "Analysis based on recent news coverage."
    
    return result

# ============= AI CONTEXT BUILDER (SINGLE SOURCE OF TRUTH) =============
def build_ai_context(user_tier="free", risk_profile=None, time_horizon=5, ticker=None, page_context=None):
    """
    Build unified AI context for all AI calls.
    All AI features must go through this context builder.
    
    Args:
        user_tier: "free", "pro", or "ultimate"
        risk_profile: dict with risk quiz results (score, label, etc.)
        time_horizon: investment time horizon in years
        ticker: selected stock ticker
        page_context: current page/intent
    
    Returns:
        dict with all context needed for AI calls
    """
    # Get market sentiment from single source of truth (will be populated at runtime)
    # Note: get_global_market_sentiment() is defined later in the file
    market_sentiment_data = None
    try:
        # This will work at runtime when the function is available
        market_sentiment_data = get_global_market_sentiment()
    except:
        market_sentiment_data = {"score": 50, "label": "Neutral (Steady)", "color": "#FFFF44"}
    
    context = {
        "user_tier": user_tier,
        "risk_profile": risk_profile or {"score": 50, "label": "Moderate", "description": "Balanced approach"},
        "time_horizon": time_horizon,
        "ticker": ticker,
        "page_context": page_context,
        "market_sentiment": market_sentiment_data,
        "timestamp": datetime.now().isoformat()
    }
    
    if ticker:
        quote = get_quote(ticker)
        profile = get_profile(ticker)
        if quote:
            context["stock_data"] = {
                "price": quote.get("price"),
                "change_percent": quote.get("changesPercentage"),
                "market_cap": quote.get("marketCap"),
                "pe_ratio": quote.get("pe"),
                "sector": profile.get("sector") if profile else None
            }
    
    if 'paper_portfolio' in st.session_state:
        context["portfolio_snapshot"] = {
            "holdings_count": len(st.session_state.paper_portfolio.get("holdings", [])),
            "total_value": st.session_state.paper_portfolio.get("total_value", 10000)
        }
    
    return context

# ============= AI OUTPUT SCHEMAS =============
def get_investment_verdict_schema():
    """Fixed schema for Investment Verdict AI output"""
    return {
        "verdict": "BUY | HOLD | SELL",
        "confidence": "0-100",
        "reasoning": ["list of reasons"],
        "risks": ["list of risks"],
        "fair_value_range": ["low", "high"]
    }

def get_scenario_analysis_schema():
    """Fixed schema for Scenario Analysis AI output"""
    return {
        "scenario": "scenario name",
        "portfolio_impact": "Positive | Neutral | Negative",
        "key_drivers": ["list of drivers"],
        "vulnerabilities": ["list of vulnerabilities"],
        "assumptions": ["list of assumptions"]
    }

# ============= AI GUARDRAILS =============
AI_GUARDRAILS = """
IMPORTANT GUIDELINES:
- Never provide specific financial advice or exact price predictions
- Use ranges and scenarios instead of exact numbers
- Express uncertainty explicitly when appropriate
- Sometimes respond with "I can't answer that" for inappropriate questions
- Focus on education and analysis, not recommendations
- Always remind users this is not financial advice
"""

@st.cache_data(ttl=3600)
def call_ai_with_context(task_name, context, prompt_template):
    """
    Unified AI call function with caching and guardrails.
    All AI calls should go through this function.
    
    Args:
        task_name: identifier for the task (for caching)
        context: dict from build_ai_context()
        prompt_template: the prompt to send to AI
    
    Returns:
        AI response or None if error
    """
    if not USE_AI_ANALYSIS or not PERPLEXITY_API_KEY:
        return None
    
    cache_key = f"{task_name}_{context.get('ticker')}_{context.get('user_tier')}_{context.get('risk_profile', {}).get('label')}"
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"""You are an AI financial analyst assistant. 
User Context:
- Tier: {context.get('user_tier', 'free')}
- Risk Profile: {context.get('risk_profile', {}).get('label', 'Moderate')}
- Time Horizon: {context.get('time_horizon', 5)} years
- Current Page: {context.get('page_context', 'general')}

{AI_GUARDRAILS}

Respond in JSON format when asked for structured output."""

        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_template}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            return content
        else:
            return None
    except Exception as e:
        return None

def get_ai_investment_verdict(ticker, context):
    """Get AI investment verdict using unified context and schema"""
    if context.get('user_tier') == 'free':
        return {"error": "Investment verdicts require Pro or Ultimate tier"}
    
    prompt = f"""Analyze {ticker} and provide an investment verdict.

Return your analysis in this exact JSON format:
{{
    "verdict": "BUY" or "HOLD" or "SELL",
    "confidence": number from 0-100,
    "reasoning": ["reason 1", "reason 2", "reason 3"],
    "risks": ["risk 1", "risk 2"],
    "fair_value_range": [low_price, high_price]
}}

Consider the user's risk profile ({context.get('risk_profile', {}).get('label', 'Moderate')}) and time horizon ({context.get('time_horizon', 5)} years).
Use ranges, not exact predictions. This is educational analysis, not financial advice."""

    response = call_ai_with_context("investment_verdict", context, prompt)
    
    if response:
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
    
    return None

def get_ai_scenario_analysis(scenario_name, context):
    """Get AI scenario analysis using unified context and schema (Ultimate tier only)"""
    if context.get('user_tier') != 'ultimate':
        return {"error": "Scenario analysis requires Ultimate tier"}
    
    prompt = f"""Analyze how the "{scenario_name}" scenario would impact the user's portfolio.

Return your analysis in this exact JSON format:
{{
    "scenario": "{scenario_name}",
    "portfolio_impact": "Positive" or "Neutral" or "Negative",
    "key_drivers": ["driver 1", "driver 2", "driver 3"],
    "vulnerabilities": ["vulnerability 1", "vulnerability 2"],
    "assumptions": ["assumption 1", "assumption 2"]
}}

Consider the user's risk profile ({context.get('risk_profile', {}).get('label', 'Moderate')}) and holdings.
Use educational language. This is not financial advice."""

    response = call_ai_with_context("scenario_analysis", context, prompt)
    
    if response:
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
    
    return None

# ============= FOUR SCENARIOS INVESTMENT CALCULATOR =============
@st.cache_data(ttl=3600)
def get_historical_adjusted_prices(ticker, years=10):
    """Get historical adjusted close prices for accurate return calculations including dividends"""
    try:
        url = f"{BASE_URL}/historical-price-full/{ticker}?apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            historical = data.get('historical', [])
            if historical:
                df = pd.DataFrame(historical)
                df['date'] = pd.to_datetime(df['date'])
                cutoff = datetime.now() - timedelta(days=years*365)
                df = df[df['date'] >= cutoff]
                df = df.sort_values('date').reset_index(drop=True)
                if 'adjClose' in df.columns:
                    df['price'] = df['adjClose']
                elif 'close' in df.columns:
                    df['price'] = df['close']
                return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def calculate_four_scenarios(ticker, years=5, base_amount=100):
    """Calculate the four investment scenarios using adjusted close prices"""
    stock_data = get_historical_adjusted_prices(ticker, years)
    spy_data = get_historical_adjusted_prices("SPY", years)
    
    if stock_data.empty or spy_data.empty:
        return None
    
    results = {
        "timeline_years": years,
        "base_amount": base_amount,
        "scenarios": {}
    }
    
    stock_start = stock_data['price'].iloc[0]
    stock_end = stock_data['price'].iloc[-1]
    spy_start = spy_data['price'].iloc[0]
    spy_end = spy_data['price'].iloc[-1]
    
    if stock_start > 0:
        shares = base_amount / stock_start
        final_value = shares * stock_end
        results["scenarios"]["lump_stock"] = {
            "name": f"Lump Sum {ticker}",
            "invested": base_amount,
            "final_value": final_value,
            "return_pct": ((final_value - base_amount) / base_amount) * 100,
            "shares": shares
        }
    
    if spy_start > 0:
        shares = base_amount / spy_start
        final_value = shares * spy_end
        results["scenarios"]["lump_sp500"] = {
            "name": "Lump Sum S&P 500",
            "invested": base_amount,
            "final_value": final_value,
            "return_pct": ((final_value - base_amount) / base_amount) * 100,
            "shares": shares
        }
    
    biweekly_periods = years * 26
    total_invested = base_amount * biweekly_periods
    
    stock_interval = max(1, len(stock_data) // biweekly_periods)
    stock_shares = 0
    stock_invested = 0
    for i in range(0, min(len(stock_data), biweekly_periods * stock_interval), stock_interval):
        if i < len(stock_data) and stock_data['price'].iloc[i] > 0:
            stock_shares += base_amount / stock_data['price'].iloc[i]
            stock_invested += base_amount
    
    if stock_shares > 0:
        final_value = stock_shares * stock_end
        results["scenarios"]["dca_stock"] = {
            "name": f"Paycheck {ticker}",
            "invested": stock_invested,
            "final_value": final_value,
            "return_pct": ((final_value - stock_invested) / stock_invested) * 100 if stock_invested > 0 else 0,
            "shares": stock_shares,
            "payments": biweekly_periods
        }
    
    spy_interval = max(1, len(spy_data) // biweekly_periods)
    spy_shares = 0
    spy_invested = 0
    for i in range(0, min(len(spy_data), biweekly_periods * spy_interval), spy_interval):
        if i < len(spy_data) and spy_data['price'].iloc[i] > 0:
            spy_shares += base_amount / spy_data['price'].iloc[i]
            spy_invested += base_amount
    
    if spy_shares > 0:
        final_value = spy_shares * spy_end
        results["scenarios"]["dca_sp500"] = {
            "name": "Paycheck S&P 500",
            "invested": spy_invested,
            "final_value": final_value,
            "return_pct": ((final_value - spy_invested) / spy_invested) * 100 if spy_invested > 0 else 0,
            "shares": spy_shares,
            "payments": biweekly_periods
        }
    
    return results

def create_four_scenarios_chart(results, ticker):
    """Create a comparison chart for the four investment scenarios"""
    if not results or not results.get("scenarios"):
        return None
    
    scenarios = results["scenarios"]
    
    names = []
    invested = []
    final_values = []
    colors = []
    
    color_map = {
        "lump_stock": "#9D4EDD",
        "lump_sp500": "#FFD700",
        "dca_stock": "#00D9FF",
        "dca_sp500": "#00FF96"
    }
    
    for key in ["lump_stock", "lump_sp500", "dca_stock", "dca_sp500"]:
        if key in scenarios:
            s = scenarios[key]
            names.append(s["name"])
            invested.append(s["invested"])
            final_values.append(s["final_value"])
            colors.append(color_map.get(key, "#888888"))
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Amount Invested',
        x=names,
        y=invested,
        marker_color='rgba(150, 150, 150, 0.5)',
        text=[f'${v:,.0f}' for v in invested],
        textposition='inside'
    ))
    
    fig.add_trace(go.Bar(
        name='Final Value',
        x=names,
        y=final_values,
        marker_color=colors,
        text=[f'${v:,.0f}' for v in final_values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f"Four Scenarios: $100 Investment Comparison ({results['timeline_years']} Years)",
        xaxis_title="Investment Strategy",
        yaxis_title="Value ($)",
        barmode='group',
        height=450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    return fig

# ============= BEGINNER TOOLTIPS =============
BEGINNER_TOOLTIPS = {
    "P/E Ratio": "Think of it like buying a lemonade stand. If it makes $10/year profit and costs $150, the P/E is 15. Lower usually means cheaper!",
    "P/S Ratio": "How much you pay for each dollar the company earns in sales. Like paying $5 for a business that sells $1 of lemonade.",
    "Market Cap": "The total price tag of the whole company. Like if you wanted to buy ALL the shares, this is what it would cost.",
    "Debt-to-Equity": "How much the company borrowed vs what it actually owns. Like if you have a $200k house but owe $150k, your D/E is 0.75.",
    "Quick Ratio": "Can the company pay its bills RIGHT NOW without selling stuff? Above 1.0 = yes, they have enough cash.",
    "Free Cash Flow": "Money left over after paying all the bills. This is the real cash the company can use for anything.",
    "Beta": "How wild the stock price swings. Beta of 1 = moves with the market. Beta of 2 = twice as crazy!",
    "ROE": "Return on Equity - how good is the company at making money with what shareholders invested? 15%+ is solid.",
    "Gross Margin": "For every $1 in sales, how much is left after making the product? Higher = better pricing power.",
    "Net Margin": "For every $1 in sales, how much actual profit? 10%+ is good, 20%+ is excellent.",
    "EPS": "Earnings Per Share - profit divided by number of shares. More EPS = more profit for each share you own.",
    "Dividend Yield": "Free money! If you invest $100 and get $3/year in dividends, that's a 3% yield.",
    "Revenue": "Total money coming in from selling stuff. The 'top line' - everything starts here.",
    "Net Income": "The 'bottom line' profit after ALL expenses. This is what really matters for shareholders.",
    "Operating Income": "Profit from the main business, before interest and taxes. Shows if the core business works.",
    "EBITDA": "Earnings before some accounting stuff. Good for comparing companies in the same industry.",
    "Current Ratio": "Can the company pay bills due this year? Above 1.5 = comfortable, below 1 = might struggle.",
    "Interest Coverage": "Can the company afford its debt payments? Higher = safer. Below 2 = risky.",
    "Negative P/E": "This company is currently losing money, so it doesn't have a P/E ratio yet. Not necessarily bad for growth companies!"
}

def get_beginner_tooltip(metric_name):
    """Get a beginner-friendly tooltip for a metric"""
    return BEGINNER_TOOLTIPS.get(metric_name, f"A financial metric that helps evaluate the company's {metric_name.lower()}.")

# ============= LIVE TICKER BAR =============
TOP_100_TICKERS = [
    # Top 50 by market cap
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "JNJ",
    "V", "XOM", "JPM", "WMT", "MA", "PG", "HD", "CVX", "MRK", "ABBV",
    "LLY", "PEP", "KO", "COST", "AVGO", "TMO", "MCD", "CSCO", "ACN", "ABT",
    "DHR", "NKE", "ORCL", "VZ", "ADBE", "CRM", "INTC", "CMCSA", "PFE", "TXN",
    "AMD", "NFLX", "QCOM", "HON", "UPS", "PM", "IBM", "LOW", "CAT", "BA",
    # Next 50 popular stocks
    "GE", "SPGI", "RTX", "NEE", "AMAT", "BKNG", "ISRG", "NOW", "AXP", "SYK",
    "MDLZ", "GILD", "ADI", "LRCX", "REGN", "VRTX", "ZTS", "PANW", "SNPS", "KLAC",
    "CME", "CDNS", "SHW", "ETN", "BSX", "MO", "CI", "CB", "SO", "DUK",
    "MMC", "PLD", "ICE", "CL", "EOG", "APD", "MCK", "NOC", "WM", "USB",
    "FDX", "EMR", "PNC", "TGT", "NSC", "PSX", "ADP", "ITW", "GM", "F"
]

@st.cache_data(ttl=60)
def get_live_ticker_data():
    """Fetch live quotes for top 100 stocks in batches"""
    try:
        ticker_data = []
        # Fetch in batches of 50 (API limit)
        for i in range(0, len(TOP_100_TICKERS), 50):
            batch = TOP_100_TICKERS[i:i+50]
            tickers_str = ",".join(batch)
            url = f"{BASE_URL}/quote/{tickers_str}?apikey={FMP_API_KEY}"
            response = requests.get(url, timeout=15)
            data = response.json()
            for quote in data:
                if isinstance(quote, dict):
                    ticker_data.append({
                        "symbol": quote.get("symbol", ""),
                        "price": quote.get("price", 0),
                        "change_pct": quote.get("changesPercentage", 0)
                    })
        return ticker_data
    except:
        return [
            {"symbol": "AAPL", "price": 185.50, "change_pct": 1.2},
            {"symbol": "MSFT", "price": 378.25, "change_pct": -0.5},
            {"symbol": "GOOGL", "price": 141.80, "change_pct": 0.8},
            {"symbol": "AMZN", "price": 178.90, "change_pct": 1.5},
            {"symbol": "NVDA", "price": 495.20, "change_pct": 2.3},
            {"symbol": "META", "price": 505.15, "change_pct": -0.3},
            {"symbol": "TSLA", "price": 248.50, "change_pct": -1.8},
        ]

def render_live_ticker_bar():
    """Render the scrolling live ticker bar at the top of the page"""
    ticker_data = get_live_ticker_data()
    if not ticker_data:
        return
    
    ticker_items = ""
    for item in ticker_data:
        change_class = "change-up" if item["change_pct"] >= 0 else "change-down"
        change_sign = "+" if item["change_pct"] >= 0 else ""
        ticker_items += f'''
            <div class="ticker-item">
                <span class="symbol">{item["symbol"]}</span>
                <span class="price">${item["price"]:.2f}</span>
                <span class="{change_class}">{change_sign}{item["change_pct"]:.2f}%</span>
            </div>
        '''
    
    ticker_html = f'''
    <div class="ticker-bar">
        <div class="ticker-content">
            {ticker_items}
            {ticker_items}
        </div>
    </div>
    '''
    st.markdown(ticker_html, unsafe_allow_html=True)

def render_right_side_ticker():
    """Render the vertical scrolling stock ticker on the right side (desktop only)"""
    ticker_data = get_live_ticker_data()
    if not ticker_data:
        return
    
    ticker_items = ""
    for item in ticker_data:
        change_class = "change-up" if item["change_pct"] >= 0 else "change-down"
        change_sign = "+" if item["change_pct"] >= 0 else ""
        ticker_items += f'''
            <div class="right-ticker-item" onclick="window.location.href='?ticker={item["symbol"]}'">
                <span class="right-ticker-symbol">{item["symbol"]}</span>
                <span class="right-ticker-price">${item["price"]:.2f}</span>
                <span class="right-ticker-change {change_class}">{change_sign}{item["change_pct"]:.2f}%</span>
            </div>
        '''
    
    ticker_html = f'''
    <style>
    /* Right-side vertical ticker - desktop only */
    @media (min-width: 1200px) {{
        .right-ticker-rail {{
            position: fixed;
            top: 80px;
            right: 0;
            width: 180px;
            height: calc(100vh - 80px);
            background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
            border-left: 1px solid #333;
            z-index: 9998;
            overflow: hidden;
        }}
        .right-ticker-content {{
            animation: scroll-up 120s linear infinite;
        }}
        .right-ticker-rail:hover .right-ticker-content {{
            animation-play-state: paused;
        }}
        @keyframes scroll-up {{
            0% {{ transform: translateY(0); }}
            100% {{ transform: translateY(-50%); }}
        }}
        .right-ticker-item {{
            display: flex;
            flex-direction: column;
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            cursor: pointer;
            transition: background 0.2s ease;
        }}
        .right-ticker-item:hover {{
            background: rgba(0, 217, 255, 0.1);
        }}
        .right-ticker-symbol {{
            font-weight: bold;
            color: #00D9FF;
            font-size: 14px;
        }}
        .right-ticker-price {{
            color: #FFFFFF;
            font-size: 13px;
            margin-top: 2px;
        }}
        .right-ticker-change {{
            font-size: 12px;
            margin-top: 2px;
        }}
        .right-ticker-change.change-up {{
            color: #00FF00;
        }}
        .right-ticker-change.change-down {{
            color: #FF4444;
        }}
        /* Adjust main content to make room for right ticker */
        .main .block-container {{
            padding-right: 200px !important;
        }}
    }}
    @media (max-width: 1199px) {{
        .right-ticker-rail {{
            display: none !important;
        }}
    }}
    </style>
    <div class="right-ticker-rail">
        <div class="right-ticker-header" style="padding: 10px; background: #FF4444; color: white; font-weight: bold; text-align: center;">
            LIVE PRICES
        </div>
        <div class="right-ticker-content">
            {ticker_items}
            {ticker_items}
        </div>
    </div>
    '''
    st.markdown(ticker_html, unsafe_allow_html=True)

def get_chatbot_response(user_message, context=None):
    """Get AI response from Perplexity API for chatbot"""
    if not PERPLEXITY_API_KEY:
        return "I'm sorry, but the AI service is currently unavailable. Please try again later."
    
    # Build context-aware system prompt
    system_prompt = """You are a friendly, knowledgeable AI investment assistant for "Investing Made Simple". 
Your role is to help beginners understand investing concepts in simple terms.

Guidelines:
- Be concise and helpful (2-3 sentences max unless asked for detail)
- Use simple language that beginners can understand
- Never give specific financial advice or price predictions
- Always remind users to do their own research
- Be encouraging and supportive of their learning journey
"""
    
    # Add context if available
    if context:
        if context.get('current_page'):
            system_prompt += f"\nThe user is currently on the '{context['current_page']}' page."
        if context.get('selected_ticker'):
            system_prompt += f"\nThey are looking at {context['selected_ticker']} stock."
        if context.get('user_name'):
            system_prompt += f"\nThe user's name is {context['user_name']}."
        if context.get('risk_profile'):
            system_prompt += f"\nTheir risk profile is: {context['risk_profile']}."
        if context.get('unhinged_mode'):
            system_prompt += "\nUNHINGED MODE IS ON: Add some playful roast commentary to your responses. Be witty and sarcastic but still helpful. Make fun of common investing mistakes."
    
    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "I couldn't generate a response. Please try again.")
        else:
            return f"I'm having trouble connecting right now. Please try again in a moment."
    except Exception as e:
        return "I'm experiencing technical difficulties. Please try again later."

@st.dialog("🤖 AI Investment Assistant", width="large")
def chatbot_dialog():
    """AI Chatbot dialog using Streamlit's native dialog"""
    st.markdown("""
    <style>
    [data-testid="stDialog"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    [data-testid="stDialog"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    .chat-message-user {
        background: rgba(255, 68, 68, 0.25);
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
        color: white;
    }
    .chat-message-ai {
        background: rgba(0, 217, 255, 0.2);
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize chat messages if not exists
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "👋 Hi! I'm your AI investment assistant. Ask me anything about stocks, investing, or financial analysis!\n\n*Tip: I'm context-aware - I know what page you're on and what stock you're looking at!*"}
        ]
    
    # Display chat messages
    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Input area
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Ask me anything...", key="chatbot_input", label_visibility="collapsed", placeholder="Type your question here...")
    with col2:
        send_clicked = st.button("Send", use_container_width=True, type="primary")
    
    if send_clicked and user_input:
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        # Build context
        context = {
            "current_page": st.session_state.get("selected_page", "Home"),
            "selected_ticker": st.session_state.get("selected_ticker", None),
            "user_name": st.session_state.get("user_name", None),
            "risk_profile": st.session_state.get("risk_profile", None),
            "unhinged_mode": st.session_state.get("unhinged_mode", False)
        }
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = get_chatbot_response(user_input, context)
        
        # Add AI response
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Close button
    if st.button("❌ Close Chat", use_container_width=True):
        st.session_state.chatbot_open = False
        st.rerun()

def render_ai_chatbot():
    """Render the AI chatbot - uses clickable HTML form button and dialog"""
    if 'chatbot_open' not in st.session_state:
        st.session_state.chatbot_open = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Render clickable floating button using HTML form (no JS needed)
    # Visual polish: hover animation, tooltip, improved contrast
    st.markdown("""
    <style>
    /* Floating chatbot button - CLICKABLE with hover animation */
    .chatbot-float-btn {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        width: 65px !important;
        height: 65px !important;
        background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 999999 !important;
        box-shadow: 0 4px 25px rgba(255, 68, 68, 0.6) !important;
        border: 3px solid #FFFFFF !important;
        font-size: 32px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        animation: pulse 2s infinite !important;
    }
    .chatbot-float-btn:hover {
        transform: scale(1.15) rotate(10deg) !important;
        box-shadow: 0 8px 35px rgba(255, 68, 68, 0.9) !important;
        animation: none !important;
    }
    @keyframes pulse {
        0% { box-shadow: 0 4px 25px rgba(255, 68, 68, 0.6); }
        50% { box-shadow: 0 4px 35px rgba(255, 68, 68, 0.9); }
        100% { box-shadow: 0 4px 25px rgba(255, 68, 68, 0.6); }
    }
    .chatbot-form {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 999999 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Tooltip for chat button */
    .chatbot-tooltip {
        position: fixed !important;
        bottom: 100px !important;
        right: 20px !important;
        background: rgba(0, 0, 0, 0.85) !important;
        color: #FFFFFF !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        z-index: 999998 !important;
        white-space: nowrap !important;
        opacity: 0 !important;
        transition: opacity 0.3s ease !important;
        pointer-events: none !important;
    }
    .chatbot-form:hover + .chatbot-tooltip,
    .chatbot-form:focus-within + .chatbot-tooltip {
        opacity: 1 !important;
    }
    </style>
    <form method="get" class="chatbot-form">
        <button type="submit" name="open_chat" value="1" class="chatbot-float-btn" title="Ask questions about this stock or your portfolio">🤖</button>
    </form>
    <div class="chatbot-tooltip">Ask questions about this stock or your portfolio</div>
    """, unsafe_allow_html=True)
    
    # Show dialog if open
    if st.session_state.chatbot_open:
        chatbot_dialog()

# ============= WELCOME POPUP =============
def show_welcome_popup():
    """Show welcome popup for first-time users - dismisses on X click or after 10 seconds, never returns until refresh"""
    # Initialize session state
    if 'welcome_seen' not in st.session_state:
        st.session_state.welcome_seen = False
    
    # Check if popup was dismissed via query param (auto-dismiss via meta refresh)
    # Note: st.query_params.get() may return a list in some Streamlit versions
    dismiss_param = st.query_params.get("dismiss_welcome")
    if isinstance(dismiss_param, (list, tuple)):
        dismiss_param = dismiss_param[0] if dismiss_param else None
    
    if dismiss_param == "1":
        st.session_state.welcome_seen = True
        # Remove the query param (guard against KeyError)
        if "dismiss_welcome" in st.query_params:
            del st.query_params["dismiss_welcome"]
        st.rerun()
    
    # Only show popup if not seen
    if not st.session_state.welcome_seen:
        # CSS for popup overlay and styling + HTML with form-based X button
        st.markdown('''
        <style>
        .welcome-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            z-index: 10000;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .welcome-popup {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 2px solid #00D9FF;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            text-align: center;
            position: relative;
        }
        .welcome-close-form {
            position: absolute;
            top: 15px;
            right: 15px;
            margin: 0;
            padding: 0;
        }
        .welcome-close-btn {
            background: transparent;
            border: 2px solid #FF4444;
            color: #FF4444;
            font-size: 20px;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            padding: 0;
            line-height: 1;
        }
        .welcome-close-btn:hover {
            background: #FF4444;
            color: #FFFFFF;
        }
        .welcome-start-form {
            margin-top: 20px;
        }
        .welcome-start-btn {
            background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%);
            border: none;
            color: #FFFFFF;
            font-size: 18px;
            font-weight: bold;
            padding: 15px 40px;
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .welcome-start-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
        }
        </style>
        <!-- Auto-dismiss after 10 seconds using meta refresh (no JS needed, works in same tab) -->
        <meta http-equiv="refresh" content="10;url=?dismiss_welcome=1">
        <div class="welcome-overlay">
            <div class="welcome-popup">
                <!-- X button using HTML form GET submit (works in same tab, no JS needed) -->
                <form class="welcome-close-form" method="get">
                    <button class="welcome-close-btn" type="submit" name="dismiss_welcome" value="1">×</button>
                </form>
                <h1 style="color: #00D9FF; margin-bottom: 20px;">Welcome to Investing Made Simple!</h1>
                <p style="color: #FFFFFF; font-size: 16px; margin-bottom: 20px;">We've upgraded your experience:</p>
                <ul style="color: #FFFFFF; font-size: 14px; line-height: 2.2; text-align: left; padding-left: 20px;">
                    <li><strong>Market Mood:</strong> Check the speedometer to see if the market is fearful or greedy.</li>
                    <li><strong>Easy Search:</strong> Type 'Apple' or 'Tesla'—no need to memorize tickers!</li>
                    <li><strong>Simpler Metrics:</strong> Hover over any number for a 'Sweet & Simple' explanation.</li>
                    <li><strong>Live Updates:</strong> Watch the top ticker for real-time prices.</li>
                </ul>
                <!-- Let's Get Started button using HTML form GET submit -->
                <form class="welcome-start-form" method="get">
                    <button class="welcome-start-btn" type="submit" name="dismiss_welcome" value="1">Let's Get Started</button>
                </form>
            </div>
        </div>
        ''', unsafe_allow_html=True)

# ============= LOGOUT HELPER =============
def do_logout():
    """Logout helper function to sign out and clear session state"""
    try:
        if SUPABASE_ENABLED:
            supabase.auth.sign_out()
    except:
        pass
    
    # Clear all auth-related session state
    for k in ["user_id", "user_email", "is_logged_in", "is_founder", "first_name"]:
        st.session_state.pop(k, None)
    st.rerun()

# ============= LOGIN DIALOG =============
@st.dialog("🔐 Sign In", width="large")
def login_dialog():
    """Sign in dialog for existing users"""
    st.markdown("""
    <style>
    [data-testid="stDialog"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    [data-testid="stDialog"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stDialog"] label {
        color: #FFFFFF !important;
    }
    [data-testid="stDialog"] h1, [data-testid="stDialog"] h2, [data-testid="stDialog"] h3 {
        color: #FF4444 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### Welcome back!")
    st.markdown("*Sign in to access your saved progress*")
    
    email = st.text_input("Email Address", placeholder="john@example.com", key="login_email")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("❌ Cancel", use_container_width=True, type="secondary", key="login_cancel"):
            st.session_state.show_login_popup = False
            st.rerun()
    with col_btn2:
        if st.button("✅ Sign In", use_container_width=True, type="primary", key="login_submit"):
            if not SUPABASE_ENABLED:
                st.error("❌ Authentication service not available.")
                return
            if not email or not password:
                st.error("❌ Please enter email and password.")
                return
            
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res and res.user:
                    uid = res.user.id
                    st.session_state.user_id = uid
                    st.session_state.user_email = res.user.email
                    st.session_state.is_logged_in = True
                    
                    # Fetch first name from profiles table
                    try:
                        profile = supabase.table("profiles").select("first_name").eq("id", uid).single().execute()
                        st.session_state.first_name = (profile.data or {}).get("first_name") or ""
                    except:
                        st.session_state.first_name = ""
                    
                    # Fallback if missing
                    if not st.session_state.first_name:
                        st.session_state.first_name = (res.user.email or "").split("@")[0]
                    
                    # Founder flag derived from email
                    FOUNDER_EMAIL = (os.getenv("FOUNDER_EMAIL") or "").strip().lower()
                    st.session_state.is_founder = (res.user.email or "").strip().lower() == FOUNDER_EMAIL
                    
                    # Load user progress
                    load_user_progress()
                    
                    st.success(f"✅ Welcome back, {st.session_state.first_name}!")
                    st.session_state.show_login_popup = False
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")
            except Exception as e:
                msg = str(e)
                if "not confirmed" in msg.lower() or "email not confirmed" in msg.lower():
                    st.error("❌ Please verify your email first (check inbox), then sign in.")
                elif "invalid" in msg.lower() or "credentials" in msg.lower():
                    st.error("❌ Invalid email or password.")
                else:
                    st.error(f"❌ Login error: {msg}")

# ============= SIGNUP DIALOG =============
@st.dialog("📝 Create Your Account", width="large")
def signup_dialog():
    """Sign up dialog for new users"""
    st.markdown("""
    <style>
    [data-testid="stDialog"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    [data-testid="stDialog"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stDialog"] label {
        color: #FFFFFF !important;
    }
    [data-testid="stDialog"] h1, [data-testid="stDialog"] h2, [data-testid="stDialog"] h3 {
        color: #FF4444 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### Join Investing Made Simple today!")
    st.markdown("*Start your journey to financial freedom*")
    
    first_name = st.text_input("First Name", placeholder="John", key="signup_first_name")
    email = st.text_input("Email Address", placeholder="john@example.com", key="signup_email")
    
    col3, col4 = st.columns(2)
    with col3:
        phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567", key="signup_phone")
    with col4:
        age = st.number_input("Age", min_value=1, max_value=120, value=25, key="signup_age")
    
    password = st.text_input("Create Password", type="password", placeholder="Enter a strong password", key="signup_password")
    password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="signup_confirm")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("❌ Cancel", use_container_width=True, type="secondary", key="signup_cancel"):
            st.session_state.show_signup_popup = False
            st.rerun()
    with col_btn2:
        if st.button("✅ Create Account", use_container_width=True, type="primary", key="signup_submit"):
            # Validation
            if not all([first_name, email, phone, password, password_confirm]):
                st.error("❌ Please fill in all fields")
            elif age < 18:
                st.warning("🎂 You must be 18 or older to create an account.")
            elif password != password_confirm:
                st.error("❌ Passwords don't match")
            elif len(password) < 8:
                st.error("❌ Password must be at least 8 characters")
            elif "@" not in email or "." not in email:
                st.error("❌ Please enter a valid email address")
            else:
                if SUPABASE_ENABLED:
                    try:
                        response = supabase.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    "first_name": first_name,
                                    "phone": phone,
                                    "age": age
                                }
                            }
                        })
                        
                        if response.user:
                            uid = response.user.id
                            # Save first name to profiles table
                            supabase.table("profiles").upsert({
                                "id": uid,
                                "first_name": first_name
                            }).execute()
                            
                            if response.session:
                                # Email verification disabled - log in immediately
                                st.session_state.user_id = uid
                                st.session_state.user_email = email
                                st.session_state.first_name = first_name
                                st.session_state.is_logged_in = True
                                
                                # Founder flag
                                FOUNDER_EMAIL = (os.getenv("FOUNDER_EMAIL") or "").strip().lower()
                                st.session_state.is_founder = (email or "").strip().lower() == FOUNDER_EMAIL
                                
                                save_user_progress()
                                st.success("✅ Account created successfully!")
                                st.balloons()
                            else:
                                # Email verification required - still save profile
                                st.success("✅ Account created! Check your email to verify, then sign in.")
                                st.info("📧 Check inbox/spam for verification link.")
                            
                            st.session_state.show_signup_popup = False
                            st.rerun()
                        else:
                            st.error("❌ Error creating account.")
                    except Exception as e:
                        error_msg = str(e)
                        if "already registered" in error_msg.lower():
                            st.error("❌ This email is already registered. Please sign in instead.")
                        else:
                            st.error(f"❌ Error: {error_msg}")
                else:
                    st.error("❌ Authentication service not available.")


# ============= COFFEE COMPARISON CALCULATOR =============
def calculate_coffee_investment(ticker, weekly_amount, years=5):
    """Calculate what weekly coffee money would be worth if invested"""
    try:
        price_data = get_historical_price(ticker, years)
        if price_data.empty or 'price' not in price_data.columns:
            return None, None
        
        price_data = price_data.sort_values('date')
        start_price = price_data['price'].iloc[0]
        end_price = price_data['price'].iloc[-1]
        
        total_return = (end_price - start_price) / start_price
        weeks = years * 52
        total_invested = weekly_amount * weeks
        
        avg_weekly_return = (1 + total_return) ** (1 / weeks) - 1
        
        future_value = 0
        for week in range(weeks):
            weeks_remaining = weeks - week
            future_value += weekly_amount * ((1 + avg_weekly_return) ** weeks_remaining)
        
        return total_invested, future_value
    except:
        return None, None

def render_coffee_calculator(ticker, stock_name):
    """Render the coffee comparison calculator"""
    st.markdown("### ☕ The Power of Small Habits")
    st.markdown("*What if you invested your coffee money instead?*")
    
    weekly_amount = st.slider(
        "Weekly investment amount:",
        min_value=5,
        max_value=50,
        value=10,
        step=5,
        key=f"coffee_slider_{ticker}",
        help="How much you'd invest each week instead of buying coffee"
    )
    
    total_invested, future_value = calculate_coffee_investment(ticker, weekly_amount, 5)
    
    if total_invested and future_value:
        gain = future_value - total_invested
        gain_pct = (gain / total_invested) * 100
        
        st.markdown(f'''
        <div class="fade-in lift-card" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    border: 2px solid #00D9FF; border-radius: 15px; padding: 25px; margin: 20px 0;">
            <h4 style="color: #00D9FF; margin-bottom: 15px;">If you invested ${weekly_amount} (the cost of a coffee) into {stock_name} every week for the last 5 years...</h4>
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <p style="color: #888; font-size: 14px;">Total Invested</p>
                    <p style="color: #FFFFFF; font-size: 28px; font-weight: bold;">${total_invested:,.0f}</p>
                </div>
                <div>
                    <p style="color: #888; font-size: 14px;">You Would Have</p>
                    <p style="color: #00FF00; font-size: 28px; font-weight: bold;">${future_value:,.0f}</p>
                </div>
                <div>
                    <p style="color: #888; font-size: 14px;">Gain</p>
                    <p style="color: {"#00FF00" if gain > 0 else "#FF4444"}; font-size: 28px; font-weight: bold;">
                        {"+" if gain > 0 else ""}{gain_pct:.1f}%
                    </p>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.info(f"Unable to calculate coffee investment for {ticker}. Try a different stock.")

# ============= PROGRESS GAMIFICATION =============
def render_progress_bar(current_step, total_steps, section_name, disable_celebrations=False):
    """Render a progress bar with gamification"""
    progress = (current_step / total_steps) * 100
    
    st.markdown(f'''
    <div style="margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="color: #FFFFFF; font-size: 14px;">{section_name} Progress</span>
            <span style="color: #00D9FF; font-size: 14px;">{current_step}/{total_steps} Complete</span>
        </div>
        <div style="background: #333; border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #00D9FF 0%, #00FF00 100%); 
                        width: {progress}%; height: 100%; border-radius: 10px;
                        transition: width 0.5s ease;"></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if progress >= 100 and not disable_celebrations:
        st.balloons()
        st.success("🎉 Congratulations! You've completed this section!")

# ============= MARKET MOOD SPEEDOMETER =============
def create_fear_greed_gauge(sentiment_score):
    """Create a Fear & Greed speedometer gauge using Plotly"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sentiment_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Market Mood", 'font': {'size': 24, 'color': '#FFFFFF'}},
        number={'font': {'size': 40, 'color': '#FFFFFF'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#FFFFFF",
                    'tickfont': {'color': '#FFFFFF'}},
            'bar': {'color': "#00D9FF"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, 25], 'color': '#FF4444', 'name': 'Extreme Fear'},
                {'range': [25, 45], 'color': '#FF8844', 'name': 'Fear'},
                {'range': [45, 55], 'color': '#FFFF44', 'name': 'Neutral'},
                {'range': [55, 75], 'color': '#88FF44', 'name': 'Greed'},
                {'range': [75, 100], 'color': '#44FF44', 'name': 'Extreme Greed'}
            ],
            'threshold': {
                'line': {'color': "#FFFFFF", 'width': 4},
                'thickness': 0.75,
                'value': sentiment_score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def get_market_sentiment_label(score):
    """Get the label for a market sentiment score"""
    if score < 25:
        return "Extreme Fear (Market on Sale)", "#FF4444"
    elif score < 45:
        return "Fear", "#FF8844"
    elif score < 55:
        return "Neutral (Steady)", "#FFFF44"
    elif score < 75:
        return "Greed", "#88FF44"
    else:
        return "Extreme Greed (Over-hyped)", "#44FF44"

@st.cache_data(ttl=300)
def get_global_market_sentiment():
    """
    SINGLE SOURCE OF TRUTH for market sentiment.
    All components (sidebar, gauge, AI) must use this function.
    Cached for 5 minutes to ensure consistency across the app.
    """
    try:
        spy_data = get_historical_price("SPY", 1)
        if not spy_data.empty and 'price' in spy_data.columns and len(spy_data) >= 20:
            spy_data = spy_data.sort_values('date')
            current_price = spy_data['price'].iloc[-1]
            price_20d_ago = spy_data['price'].iloc[-20] if len(spy_data) >= 20 else spy_data['price'].iloc[0]
            
            momentum_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
            
            if momentum_20d <= -10:
                sentiment_score = 10
            elif momentum_20d <= -5:
                sentiment_score = 25
            elif momentum_20d <= -2:
                sentiment_score = 40
            elif momentum_20d <= 2:
                sentiment_score = 50
            elif momentum_20d <= 5:
                sentiment_score = 65
            elif momentum_20d <= 10:
                sentiment_score = 80
            else:
                sentiment_score = 90
            
            label, color = get_market_sentiment_label(sentiment_score)
            return {
                "score": sentiment_score,
                "label": label,
                "color": color,
                "momentum_20d": momentum_20d,
                "spy_price": current_price
            }
    except:
        pass
    
    return {
        "score": 50,
        "label": "Neutral (Steady)",
        "color": "#FFFF44",
        "momentum_20d": 0,
        "spy_price": None
    }

# ============= METRIC EXPLANATIONS =============
METRIC_EXPLANATIONS = {
    "FCF after Stock Comp": "The 'True Cash' left after paying employees in stock. This is the real money the company keeps.",
    "Free Cash Flow (FCF)": "The company's 'spare change' after paying all its bills. This is what's left for dividends, buybacks, or growth.",
    "Operating Cash Flow": "Money made from the core business engine. This shows if the main business actually generates cash.",
    "FCF / Share": "The amount of spare cash for every single share you own. Higher is better!",
    "Revenue Growth": "How fast the company's sales are growing. 10%+ is solid, 20%+ is excellent.",
    "Net Income Growth": "How fast profits are growing. Should ideally match or beat revenue growth.",
    "EPS Growth": "How fast earnings per share are growing. This directly affects stock price over time."
}

def render_metric_with_explanation(metric_name, value, explanation_key=None):
    """Render a metric with a hover explanation"""
    explanation = METRIC_EXPLANATIONS.get(explanation_key or metric_name, "")
    if explanation:
        st.markdown(f'''
        <div class="lift-card" style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 5px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #FFFFFF;">{metric_name}</span>
                <span class="ratio-tooltip" style="color: #00D9FF;">&#x3F;
                    <span class="tooltip-text">{explanation}</span>
                </span>
            </div>
            <p style="color: #00D9FF; font-size: 24px; font-weight: bold; margin: 5px 0;">{value}</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.metric(metric_name, value)

# ============= SECTOR DEFINITIONS =============
SECTORS = {
    "🏦 Financial Services": {
        "desc": "Banks, insurance, investment firms",
        "tickers": ["JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SCHW", "AXP", "USB"]
    },
    "💻 Technology": {
        "desc": "Software, hardware, semiconductors",
        "tickers": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "INTC"]
    },
    "🛒 Consumer": {
        "desc": "Retail, e-commerce, consumer goods",
        "tickers": ["AMZN", "TSLA", "WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "COST"]
    },
    "🏥 Healthcare": {
        "desc": "Pharma, biotech, medical devices",
        "tickers": ["UNH", "JNJ", "LLY", "ABBV", "MRK", "TMO", "ABT", "DHR", "PFE", "BMY"]
    },
    "🏭 Industrials": {
        "desc": "Manufacturing, aerospace, defense",
        "tickers": ["BA", "CAT", "HON", "UPS", "RTX", "LMT", "GE", "MMM", "DE", "EMR"]
    },
    "⚡ Energy": {
        "desc": "Oil, gas, renewable energy",
        "tickers": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL"]
    }
}

# ============= TOP 200 COMPANIES BY MARKET CAP (Static but reliable) =============
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_companies_from_screener(sector=None, limit=100):
    """
    Fetch companies from FMP Stock Screener API (stocks only, no ETFs)
    Returns list of dicts with 'symbol', 'companyName', 'sector', 'marketCap', 'price'
    """
    try:
        # Build URL with filters
        url = f"{BASE_URL}/company-screener?"
        params = {
            "marketCapMoreThan": 1000000000,  # $1B+ market cap
            "limit": limit * 2,  # Request more to account for ETF filtering
            "isEtf": "false",  # Exclude ETFs
            "apikey": FMP_API_KEY
        }
        
        # Add sector filter if specified
        if sector and sector != "Other":
            params["sector"] = sector
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                # Client-side filtering: Remove any remaining ETFs or funds
                stocks_only = []
                etf_keywords = ['ETF', 'Fund', 'Index Fund', 'Trust', 'iShares', 'Vanguard', 'SPDR']
                
                for company in data:
                    company_name = company.get('companyName', '')
                    symbol = company.get('symbol', '')
                    
                    # Skip if name contains ETF keywords
                    is_etf = any(keyword.lower() in company_name.lower() for keyword in etf_keywords)
                    
                    # Skip if symbol is all caps and 3-4 letters (common ETF pattern like VOO, SPY)
                    # But allow stocks like META, AAPL, etc.
                    if not is_etf:
                        stocks_only.append(company)
                    
                    # Stop when we have enough stocks
                    if len(stocks_only) >= limit:
                        break
                
                return stocks_only[:limit]
        
        return []
    except Exception as e:
        st.error(f"Stock Screener API error: {e}")
        return []

# ============= STATE =============
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "GOOGL"

if 'years_of_history' not in st.session_state:
    st.session_state.years_of_history = 5

if 'homepage_stock1' not in st.session_state:
    st.session_state.homepage_stock1 = "GOOGL"

if 'homepage_stock2' not in st.session_state:
    st.session_state.homepage_stock2 = "AMC"

# Initialize user_profile (always exists, even if quizzes not taken)
if 'user_profile' not in st.session_state:
    from datetime import datetime
    st.session_state.user_profile = {
        "experience_level": "unknown",
        "learning_style": "unknown",
        "risk_tier": "unknown",
        "risk_score": None,
        "time_horizon": None,
        "updated_at": datetime.now().isoformat()
    }

# ============= TRADE VALIDATION & PERSISTENCE =============
STARTING_CASH = 100000.0

def calculate_cash_from_db(user_id, portfolio_type='user'):
    """
    Calculate available cash from database trades (SOURCE OF TRUTH).
    Returns: (cash_available, error_message)
    """
    if not SUPABASE_ENABLED:
        return STARTING_CASH, None
    
    try:
        # Fetch all trades for this user/portfolio from DB
        query = supabase.table("trades").select("*")
        
        if portfolio_type == 'founder':
            # Founder trades are public, filter by portfolio_type only
            query = query.eq("portfolio_type", "founder")
        else:
            # User trades require user_id
            if not user_id:
                return STARTING_CASH, None
            query = query.eq("user_id", user_id).eq("portfolio_type", "user")
        
        result = query.order("timestamp", desc=False).execute()
        
        if not result.data:
            return STARTING_CASH, None
        
        # Calculate cash: Start with STARTING_CASH
        cash = STARTING_CASH
        for trade in result.data:
            if trade['trade_type'] == 'BUY':
                cash -= trade['total']
            elif trade['trade_type'] == 'SELL':
                cash += trade['total']
        
        return cash, None
        
    except Exception as e:
        error_msg = f"DB error calculating cash: {str(e)}"
        return STARTING_CASH, error_msg


def validate_and_insert_trade(user_id, portfolio_type, action, ticker, shares, price):
    """
    HARD VALIDATION: Check cash from DB, then insert if valid.
    Returns: (success: bool, message: str)
    
    CRITICAL: This function BLOCKS trades that would cause negative cash.
    """
    if not SUPABASE_ENABLED:
        return False, "⚠️ Database not available. Trades cannot be persisted."
    
    # Require user_id for user trades
    if portfolio_type == 'user' and not user_id:
        return False, "⚠️ You must be logged in to trade."
    
    # Calculate estimated cost
    estimated_cost = shares * price
    
    # For BUY trades: VALIDATE CASH FIRST
    if action == "Buy":
        cash_available, cash_error = calculate_cash_from_db(user_id, portfolio_type)
        
        if cash_error:
            return False, f"❌ Error: {cash_error}"
        
        # HARD BLOCK if insufficient funds
        if estimated_cost > cash_available:
            shortfall = estimated_cost - cash_available
            return False, (
                f"❌ **Insufficient Funds**\n\n"
                f"This trade requires **${estimated_cost:,.2f}**\n"
                f"but you only have **${cash_available:,.2f}** available.\n\n"
                f"You need **${shortfall:,.2f}** more.\n\n"
                f"Please reduce quantity or wait for funds."
            )
    
    # For SELL trades: Skip cash validation (always increases cash)
    # But we should validate position exists (TODO: implement position check)
    
    # ============= INSERT INTO DATABASE =============
    try:
        trade_data = {
            "portfolio_type": portfolio_type,
            "ticker": ticker.upper(),
            "trade_type": action.upper(),
            "quantity": float(shares),
            "price": float(price),
            "total": float(estimated_cost),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add user_id only for user trades
        if portfolio_type == 'user':
            trade_data["user_id"] = user_id
        else:
            # Founder trades: Use current logged-in user (must be founder)
            trade_data["user_id"] = user_id if user_id else None
        
        # Insert into DB
        result = supabase.table("trades").insert(trade_data).execute()
        
        if not result.data:
            return False, "❌ Trade failed to save to database."
        
        # Success!
        action_word = "Bought" if action == "Buy" else "Sold"
        return True, f"✅ {action_word} {shares} shares of {ticker} at ${price:.2f}"
        
    except Exception as e:
        return False, f"❌ Database error: {str(e)}"


def load_trades_from_db(user_id, portfolio_type='user'):
    """
    Load all trades from database for display.
    Returns: List of trade dicts
    """
    if not SUPABASE_ENABLED:
        return []
    
    try:
        query = supabase.table("trades").select("*")
        
        if portfolio_type == 'founder':
            query = query.eq("portfolio_type", "founder")
        else:
            if not user_id:
                return []
            query = query.eq("user_id", user_id).eq("portfolio_type", "user")
        
        result = query.order("timestamp", desc=True).execute()
        
        if not result.data:
            return []
        
        # Convert to display format
        trades = []
        for trade in result.data:
            trades.append({
                'date': trade['timestamp'][:16].replace('T', ' '),  # Format datetime
                'type': trade['trade_type'],
                'ticker': trade['ticker'],
                'shares': trade['quantity'],
                'price': trade['price'],
                'total': trade['total'],
                'gain_loss': trade.get('gain_loss', 0)
            })
        
        return trades
        
    except Exception as e:
        st.error(f"Error loading trades: {str(e)}")
        return []


def rebuild_portfolio_from_trades(transactions):
    """
    Rebuild portfolio positions from transaction history.
    Returns: List of position dicts [{ticker, shares, avg_price}]
    """
    positions = {}
    
    for txn in reversed(transactions):  # Process oldest first
        ticker = txn['ticker']
        shares = txn['shares']
        price = txn['price']
        
        if txn['type'] == 'BUY':
            if ticker in positions:
                # Update average cost
                old_shares = positions[ticker]['shares']
                old_avg = positions[ticker]['avg_price']
                total_shares = old_shares + shares
                total_cost = (old_shares * old_avg) + (shares * price)
                positions[ticker] = {
                    'shares': total_shares,
                    'avg_price': total_cost / total_shares
                }
            else:
                positions[ticker] = {
                    'shares': shares,
                    'avg_price': price
                }
        
        elif txn['type'] == 'SELL':
            if ticker in positions:
                positions[ticker]['shares'] -= shares
                # Remove if sold all shares
                if positions[ticker]['shares'] <= 0:
                    del positions[ticker]
    
    # Convert to list format
    portfolio = []
    for ticker, data in positions.items():
        portfolio.append({
            'ticker': ticker,
            'shares': data['shares'],
            'avg_price': data['avg_price']
        })
    
    return portfolio

# ============= SUPABASE CONFIGURATION =============
# Read from environment variables for security (set in Render dashboard)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

# Initialize Supabase client only if credentials are available
if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        SUPABASE_ENABLED = True
    except ImportError:
        SUPABASE_ENABLED = False
        st.warning("⚠️ Supabase library not installed. Run: pip install supabase")
    except Exception as e:
        SUPABASE_ENABLED = False
        st.error(f"⚠️ Supabase initialization failed: {str(e)}")
else:
    SUPABASE_ENABLED = False
    # Don't show warning - app works without authentication

# ============= USER PROGRESS PERSISTENCE =============
def save_user_progress():
    """Save user progress to Supabase user_state table"""
    if not SUPABASE_ENABLED:
        return False
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        return False
    
    try:
        # Collect state to persist (including Basics course progress and risk quiz)
        state_data = {
            "selected_ticker": st.session_state.get("selected_ticker", "GOOGL"),
            "paper_portfolio": st.session_state.get("paper_portfolio", {}),
            "risk_quiz_results": st.session_state.get("risk_quiz_results", {}),
            "unhinged_mode": st.session_state.get("unhinged_mode", False),
            "homepage_stock1": st.session_state.get("homepage_stock1", "GOOGL"),
            "homepage_stock2": st.session_state.get("homepage_stock2", "AMC"),
            # Save Basics course progress
            "completed_lessons": list(st.session_state.get("completed_lessons", set())),
            # Save Risk Quiz results
            "risk_tier": st.session_state.get("risk_tier"),
            "risk_score": st.session_state.get("risk_score"),
            "risk_quiz_completed_at": st.session_state.get("risk_quiz_completed_at"),
            # Save user profile
            "user_profile": st.session_state.get("user_profile", {}),
            "onboarding_profile": st.session_state.get("onboarding_profile", {}),
            # Save onboarding state
            "setup_prompt_dismissed": st.session_state.get("setup_prompt_dismissed", False),
            "onboarding_completed": st.session_state.get("onboarding_completed", False),
        }
        
        # Upsert to user_state table
        supabase.table("user_state").upsert({
            "user_id": user_id,
            "state": json.dumps(state_data),
            "updated_at": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        # Silently fail - don't break the app if persistence fails
        return False

def load_user_progress():
    """Load user progress from Supabase user_state table"""
    if not SUPABASE_ENABLED:
        return False
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        return False
    
    try:
        result = supabase.table("user_state").select("state").eq("user_id", user_id).execute()
        if result.data and len(result.data) > 0:
            state_data = json.loads(result.data[0].get("state", "{}"))
            
            # Restore state
            if "selected_ticker" in state_data:
                st.session_state.selected_ticker = state_data["selected_ticker"]
            if "paper_portfolio" in state_data:
                st.session_state.paper_portfolio = state_data["paper_portfolio"]
            if "risk_quiz_results" in state_data:
                st.session_state.risk_quiz_results = state_data["risk_quiz_results"]
            if "unhinged_mode" in state_data:
                st.session_state.unhinged_mode = state_data["unhinged_mode"]
            if "homepage_stock1" in state_data:
                st.session_state.homepage_stock1 = state_data["homepage_stock1"]
            if "homepage_stock2" in state_data:
                st.session_state.homepage_stock2 = state_data["homepage_stock2"]
            # Restore Basics course progress
            if "completed_lessons" in state_data:
                st.session_state.completed_lessons = set(state_data["completed_lessons"])
            # Restore Risk Quiz results
            if "risk_tier" in state_data:
                st.session_state.risk_tier = state_data["risk_tier"]
            if "risk_score" in state_data:
                st.session_state.risk_score = state_data["risk_score"]
            if "risk_quiz_completed_at" in state_data:
                st.session_state.risk_quiz_completed_at = state_data["risk_quiz_completed_at"]
                st.session_state.risk_quiz_submitted = True  # Mark as completed
            # Restore user profile
            if "user_profile" in state_data:
                st.session_state.user_profile = state_data["user_profile"]
            if "onboarding_profile" in state_data:
                st.session_state.onboarding_profile = state_data["onboarding_profile"]
                st.session_state.onboarding_completed = True
            # Restore onboarding state
            if "setup_prompt_dismissed" in state_data:
                st.session_state.setup_prompt_dismissed = state_data["setup_prompt_dismissed"]
            if "onboarding_completed" in state_data:
                st.session_state.onboarding_completed = state_data["onboarding_completed"]
            return True
    except Exception as e:
        # Silently fail - don't break the app if loading fails
        pass
    return False

def save_user_profile(user_id, first_name):
    """Save user profile to Supabase profiles table after signup"""
    if not SUPABASE_ENABLED or not user_id:
        return False
    
    try:
        supabase.table("profiles").upsert({
            "id": user_id,
            "first_name": first_name,
            "created_at": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        # Silently fail - profile save is not critical
        return False

# ============= UNHINGED MODE ROASTS (10 safe roasts) =============
UNHINGED_ROASTS = [
    "Oh, you're looking at meme stocks? Bold strategy, Cotton. Let's see if it pays off.",
    "Another day, another person thinking they can time the market. Spoiler: you can't.",
    "I see you're interested in this stock. Have you considered just burning your money? It's faster.",
    "Ah yes, the classic 'buy high, sell low' strategy. A true connoisseur.",
    "You know what they say: past performance doesn't guarantee future results. But you'll ignore that anyway.",
    "This stock has more red flags than a Soviet parade, but sure, let's analyze it.",
    "I'm not saying this is a bad investment, but my Magic 8-Ball just said 'Outlook not so good'.",
    "Diversification? Never heard of her. All in on one stock, baby!",
    "The market can stay irrational longer than you can stay solvent. Just a friendly reminder.",
    "Warren Buffett would be so proud... of your confidence, at least.",
]

def get_session_roast():
    """Get a roast for this session (max 1 per session)"""
    if st.session_state.get("roast_shown_this_session", False):
        return None
    if not st.session_state.get("unhinged_mode", False):
        return None
    # Check age restriction
    user_age = st.session_state.get("user_age", 25)
    if user_age < 18:
        return None
    
    st.session_state.roast_shown_this_session = True
    return random.choice(UNHINGED_ROASTS)

# ============= GLOBAL TICKER CONSISTENCY (B) =============
def set_active_ticker(ticker):
    """Set the global active ticker - single source of truth for all pages"""
    if ticker and isinstance(ticker, str):
        ticker = ticker.upper().strip()
        if ticker:
            st.session_state.selected_ticker = ticker
            # Save progress if logged in
            if st.session_state.get("user_id"):
                save_user_progress()
            return True
    return False

def get_active_ticker():
    """Get the current active ticker"""
    return st.session_state.get("selected_ticker", "GOOGL")

# ============= PERSONALIZATION PROFILE (A3) =============
def get_personalization_profile():
    """Get user's personalization profile based on onboarding quiz"""
    profile = st.session_state.get("onboarding_profile", {})
    return {
        "knowledge": profile.get("knowledge", "new"),
        "goal": profile.get("goal", "learn"),
        "horizon": profile.get("horizon", "5-10"),
        "drawdown": profile.get("drawdown", "uncomfortable"),
        "tone": profile.get("tone", "calm"),
        "simple_mode": profile.get("knowledge", "new") == "new",
        "risk_averse": profile.get("drawdown", "uncomfortable") in ["panic", "uncomfortable"],
        "unhinged_enabled": profile.get("tone", "calm") == "unhinged" and st.session_state.get("user_age", 25) >= 18
    }

def save_onboarding_profile(profile_data):
    """Save onboarding profile to session state and Supabase"""
    st.session_state.onboarding_profile = profile_data
    st.session_state.onboarding_completed = True
    
    # Build unified user profile
    build_user_profile()
    
    # Save to Supabase if logged in
    if SUPABASE_ENABLED and st.session_state.get("user_id"):
        try:
            user_id = st.session_state.get("user_id")
            state_data = {
                "selected_ticker": st.session_state.get("selected_ticker", "GOOGL"),
                "paper_portfolio": st.session_state.get("paper_portfolio", {}),
                "risk_quiz_results": st.session_state.get("risk_quiz_results", {}),
                "unhinged_mode": st.session_state.get("unhinged_mode", False),
                "homepage_stock1": st.session_state.get("homepage_stock1", "GOOGL"),
                "homepage_stock2": st.session_state.get("homepage_stock2", "AMC"),
                "onboarding_profile": profile_data,
                "onboarding_completed": True
            }
            supabase.table("user_state").upsert({
                "user_id": user_id,
                "state": json.dumps(state_data),
                "updated_at": datetime.now().isoformat()
            }).execute()
        except:
            pass

def build_user_profile():
    """Build unified user_profile object from onboarding and risk quiz data"""
    from datetime import datetime
    
    # Get onboarding data
    onboarding = st.session_state.get("onboarding_profile", {})
    
    # Map onboarding knowledge to experience_level
    knowledge_to_experience = {
        "new": "beginner",
        "some": "intermediate",
        "confident": "advanced"
    }
    experience_level = knowledge_to_experience.get(onboarding.get("knowledge"), "unknown")
    
    # Map onboarding goal to learning_style
    goal_to_learning = {
        "learn": "educational",
        "wealth": "practical",
        "trading": "technical",
        "exploring": "exploratory"
    }
    learning_style = goal_to_learning.get(onboarding.get("goal"), "unknown")
    
    # Get time horizon from onboarding
    time_horizon = onboarding.get("horizon", None)
    
    # Get risk quiz data
    risk_tier = st.session_state.get("risk_tier", "unknown")
    risk_score = st.session_state.get("risk_score", None)
    
    # Build profile object
    user_profile = {
        "experience_level": experience_level if st.session_state.get("onboarding_completed") else "unknown",
        "learning_style": learning_style if st.session_state.get("onboarding_completed") else "unknown",
        "risk_tier": risk_tier,
        "risk_score": risk_score,
        "time_horizon": time_horizon,
        "updated_at": datetime.now().isoformat()
    }
    
    # Store in session state
    st.session_state.user_profile = user_profile
    
    # Save to Supabase if logged in
    if st.session_state.get("is_logged_in", False):
        try:
            save_user_progress()
        except:
            pass  # Silent fallback
    
    return user_profile

def get_stock_volatility_tier(ticker):
    """
    Returns (volatility_tier, volatility_method)
    volatility_tier in {"low", "medium", "high", "unknown"}
    volatility_method in {"realized_returns", "market_cap_proxy", "unknown"}
    """
    from datetime import datetime, timedelta
    import numpy as np
    
    # Initialize vol_cache in session state if not exists
    if 'vol_cache' not in st.session_state:
        st.session_state.vol_cache = {}
    
    # Check cache (reuse if < 1 hour old)
    if ticker in st.session_state.vol_cache:
        cached = st.session_state.vol_cache[ticker]
        cached_time = datetime.fromisoformat(cached['updated_at'])
        if datetime.now() - cached_time < timedelta(hours=1):
            return (cached['tier'], cached['method'])
    
    # Try realized returns method (preferred)
    try:
        # Get ~1 year of daily price data (252 trading days)
        price_df = get_historical_adjusted_prices(ticker, years=1)
        
        if not price_df.empty and len(price_df) >= 60:
            # Compute daily returns
            prices = price_df['price'].values
            returns = np.diff(prices) / prices[:-1]
            
            # Compute standard deviation of daily returns
            std_dev = np.std(returns)
            
            # Map to tiers using fixed thresholds
            if std_dev < 0.018:
                tier = "low"
            elif std_dev < 0.032:
                tier = "medium"
            else:
                tier = "high"
            
            method = "realized_returns"
            
            # Cache result
            st.session_state.vol_cache[ticker] = {
                'tier': tier,
                'method': method,
                'updated_at': datetime.now().isoformat()
            }
            
            return (tier, method)
    except:
        pass
    
    # Fallback to market cap proxy
    try:
        profile = get_profile(ticker)
        if profile and 'mktCap' in profile:
            market_cap = profile['mktCap']
            
            if market_cap >= 200e9:
                tier = "low"
            elif market_cap >= 10e9:
                tier = "medium"
            else:
                tier = "high"
            
            method = "market_cap_proxy"
            
            # Cache result
            st.session_state.vol_cache[ticker] = {
                'tier': tier,
                'method': method,
                'updated_at': datetime.now().isoformat()
            }
            
            return (tier, method)
    except:
        pass
    
    # If neither works, return unknown
    return ("unknown", "unknown")

def get_fit_outcome(risk_tier, vol_tier):
    """
    Returns (status, message)
    status in {"fits", "partial", "mismatch", "unknown"}
    """
    # If risk_tier unknown
    if risk_tier == "unknown":
        return ("unknown", "Want a better fit check? Take the Risk Quiz so we can tailor warnings to you.")
    
    # If vol_tier unknown
    if vol_tier == "unknown":
        return ("unknown", "Fit check unavailable (insufficient volatility data).")
    
    # Fit matrix
    fit_matrix = {
        "Conservative": {
            "low": "fits",
            "medium": "partial",
            "high": "mismatch"
        },
        "Moderate": {
            "low": "fits",
            "medium": "fits",
            "high": "partial"
        },
        "Growth": {
            "low": "fits",
            "medium": "fits",
            "high": "fits"
        },
        "Aggressive": {
            "low": "fits",
            "medium": "fits",
            "high": "fits"
        }
    }
    
    status = fit_matrix.get(risk_tier, {}).get(vol_tier, "unknown")
    
    # Message templates
    messages = {
        "fits": "This generally matches your risk profile.",
        "partial": "This may still work for you, but expect bigger swings than your profile suggests.",
        "mismatch": "This may feel too volatile for your risk profile. Consider smaller sizing or diversification."
    }
    
    message = messages.get(status, "Fit check unavailable.")
    
    return (status, message)

def get_concentration_thresholds(risk_tier):
    """
    Returns (warning_threshold, strong_threshold) for a given risk tier
    """
    thresholds = {
        "Conservative": (0.15, 0.25),
        "Moderate": (0.25, 0.40),
        "Growth": (0.35, 0.55),
        "Aggressive": (0.50, 0.70),
        "unknown": (0.40, None)  # Warning only, no strong warning
    }
    return thresholds.get(risk_tier, (0.40, None))

def compute_portfolio_concentration(portfolio_positions):
    """
    Compute weight of each position in portfolio
    Returns dict: {ticker: weight (0-1)}
    """
    if not portfolio_positions:
        return {}
    
    # Calculate total portfolio value
    total_value = 0
    position_values = {}
    
    for pos in portfolio_positions:
        quote = get_quote(pos['ticker'])
        if quote:
            current_price = quote.get('price', 0)
            position_value = pos['shares'] * current_price
            position_values[pos['ticker']] = position_value
            total_value += position_value
    
    if total_value == 0:
        return {}
    
    # Calculate weights
    weights = {}
    for ticker, value in position_values.items():
        weights[ticker] = value / total_value
    
    return weights

def get_concentration_warning(ticker, weight, risk_tier):
    """
    Returns (severity, message)
    severity in {"none", "warning", "high"}
    """
    if weight is None or weight == 0:
        return ("none", "")
    
    warning_threshold, strong_threshold = get_concentration_thresholds(risk_tier)
    weight_pct = round(weight * 100)
    
    # Unknown risk tier
    if risk_tier == "unknown":
        if weight >= warning_threshold:
            return ("warning", f"ℹ️ This position is {weight_pct}% of your portfolio.\nTake the Risk Quiz to get personalized concentration warnings.")
        return ("none", "")
    
    # Strong warning
    if strong_threshold and weight >= strong_threshold:
        message = f"""🚨 **Concentration risk:**
This position is {weight_pct}% of your portfolio.
Based on your Risk Quiz ({risk_tier}), this may feel extremely volatile during drawdowns.
Consider diversifying or reducing position size."""
        return ("high", message)
    
    # Caution warning
    if weight >= warning_threshold:
        message = f"""⚠️ **Concentration warning:**
This position makes up {weight_pct}% of your portfolio.
Based on your {risk_tier} risk profile, this could increase volatility."""
        return ("warning", message)
    
    return ("none", "")

def update_concentration_flags(portfolio_positions):
    """
    Update st.session_state.concentration_flags with current portfolio concentration
    """
    weights = compute_portfolio_concentration(portfolio_positions)
    risk_tier = st.session_state.user_profile.get("risk_tier", "unknown")
    
    concentration_flags = {}
    for ticker, weight in weights.items():
        severity, _ = get_concentration_warning(ticker, weight, risk_tier)
        concentration_flags[ticker] = {
            "weight": weight,
            "severity": severity
        }
    
    st.session_state.concentration_flags = concentration_flags

def render_fit_check_panel(ticker=None):
    """Render Fit Check panel with real volatility-based fit assessment and concentration warnings"""
    if not ticker:
        return
    
    profile = st.session_state.user_profile
    risk_tier = profile.get("risk_tier", "unknown")
    
    st.markdown("### 🎯 Fit Check")
    
    # Get volatility tier
    vol_tier, vol_method = get_stock_volatility_tier(ticker)
    
    # Get fit outcome
    status, message = get_fit_outcome(risk_tier, vol_tier)
    
    # Check if user holds this stock in paper portfolio
    portfolio = st.session_state.get('portfolio', [])
    user_holds_stock = any(pos['ticker'] == ticker for pos in portfolio)
    concentration_severity = "none"
    concentration_message = ""
    
    if user_holds_stock:
        # Compute concentration
        weights = compute_portfolio_concentration(portfolio)
        weight = weights.get(ticker, 0)
        concentration_severity, concentration_message = get_concentration_warning(ticker, weight, risk_tier)
    
    # Display concentration warning first if high severity
    if concentration_severity == "high":
        st.error(concentration_message)
        # Volatility becomes secondary
        if status != "unknown":
            st.caption(f"Volatility fit: {message}")
    elif concentration_severity == "warning":
        st.warning(concentration_message)
        # Show volatility below
        if status == "unknown":
            st.info(f"ℹ️ **{message}**")
            if risk_tier == "unknown":
                if st.button("Take Risk Quiz", key=f"fit_check_cta_{ticker}"):
                    st.session_state.selected_page = "🧠 Risk Quiz"
                    st.rerun()
        elif status == "fits":
            st.caption(f"✅ Volatility: {message}")
        elif status == "partial":
            st.caption(f"⚠️ Volatility: {message}")
        elif status == "mismatch":
            st.caption(f"🚨 Volatility: {message}")
    else:
        # No concentration warning, show volatility normally
        if status == "unknown":
            st.info(f"ℹ️ **{message}**")
            if risk_tier == "unknown":
                if st.button("Take Risk Quiz", key=f"fit_check_cta_{ticker}"):
                    st.session_state.selected_page = "🧠 Risk Quiz"
                    st.rerun()
        elif status == "fits":
            st.success(f"✅ **Fits your profile**")
            st.caption(message)
        elif status == "partial":
            st.warning(f"⚠️ **Partially fits your profile**")
            st.caption(message)
        elif status == "mismatch":
            st.error(f"🚨 **Does not fit your profile**")
            st.caption(message)
    
    # Display technical details (small text)
    st.caption(f"Risk tier: **{risk_tier}** | Volatility: **{vol_tier}** (method: {vol_method})")

    """Render the site logo at top of page - centered, smaller size"""
    import base64
    
    # For deployment: User should add logo.png to their repo root
    logo_path = "logo.png"
    
    try:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(logo_path, width=300)  # Fixed width for smaller size
    except:
        # Fallback if image not found - show text logo
        st.markdown("""
        <div style="text-align: center; padding: 10px 0; margin-bottom: 10px;">
            <h3 style="color: #FF4444; margin: 0;">STOCKINVESTING.AI</h3>
            <p style="color: #888; margin: 5px 0; font-size: 0.9em;">
                <span style="color: #00D9FF;">LEARN</span> • 
                <span style="color: #FFD700;">INVEST</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_setup_nudge():
    """Render non-blocking setup nudge card"""
    if not st.session_state.get('onboarding_completed', False) and not st.session_state.get('setup_prompt_dismissed', False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #00D9FF;">
            <h3 style="color: #FFFFFF; margin: 0 0 5px 0;">Quick setup (60 seconds)</h3>
            <p style="color: #B0B0B0; margin: 0;">Personalize the site (not a test).</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start Setup", use_container_width=True, type="primary", key="nudge_start_setup"):
                st.session_state.show_onboarding_quiz = True
                st.rerun()
        with col2:
            if st.button("Skip for now", use_container_width=True, type="secondary", key="nudge_skip"):
                st.session_state.setup_prompt_dismissed = True
                # Save to Supabase if logged in
                if st.session_state.get('is_logged_in', False):
                    try:
                        save_user_progress()
                    except:
                        pass
                st.rerun()

# ============= 60-SECOND SETUP ONBOARDING (A1/A2) =============
@st.dialog("Let's personalize this in 60 seconds", width="large")
def onboarding_quiz_dialog():
    """60-Second Setup onboarding quiz modal"""
    st.markdown("### Personalize your experience")
    st.info("💡 **This helps us personalize how the site works for you.** It's not a test, and it doesn't affect what you can invest in.")
    
    # Question 1: Knowledge level
    knowledge = st.radio(
        "1. Your investment knowledge:",
        ["New - Just getting started", "Some experience - Know the basics", "Confident - Can read financials"],
        key="onboard_knowledge"
    )
    knowledge_map = {"New - Just getting started": "new", "Some experience - Know the basics": "some", "Confident - Can read financials": "confident"}
    
    # Question 2: Primary goal
    goal = st.radio(
        "2. What's your primary goal?",
        ["Learn basics", "Build long-term wealth", "Trading / speculation", "Just exploring"],
        key="onboard_goal"
    )
    goal_map = {"Learn basics": "learn", "Build long-term wealth": "wealth", "Trading / speculation": "trading", "Just exploring": "exploring"}
    
    # Question 3: Time horizon
    horizon = st.radio(
        "3. Your investment time horizon:",
        ["Less than 1 year", "1-5 years", "5-10 years", "10+ years"],
        key="onboard_horizon"
    )
    horizon_map = {"Less than 1 year": "<1", "1-5 years": "1-5", "5-10 years": "5-10", "10+ years": "10+"}
    
    # Question 4: Drawdown comfort
    drawdown = st.radio(
        "4. If your portfolio dropped 20%, you would:",
        ["Panic and sell", "Feel uncomfortable but hold", "Be fine with it", "Buy more (it's on sale!)"],
        key="onboard_drawdown"
    )
    drawdown_map = {"Panic and sell": "panic", "Feel uncomfortable but hold": "uncomfortable", "Be fine with it": "fine", "Buy more (it's on sale!)": "buy_more"}
    
    # Question 5: Tone mode (optional)
    tone = st.radio(
        "5. Preferred tone (optional):",
        ["Calm (default)", "Data-driven", "Unhinged (roast commentary)"],
        key="onboard_tone"
    )
    tone_map = {"Calm (default)": "calm", "Data-driven": "data", "Unhinged (roast commentary)": "unhinged"}
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Complete Setup", type="primary", use_container_width=True):
            profile = {
                "knowledge": knowledge_map.get(knowledge, "new"),
                "goal": goal_map.get(goal, "learn"),
                "horizon": horizon_map.get(horizon, "5-10"),
                "drawdown": drawdown_map.get(drawdown, "uncomfortable"),
                "tone": tone_map.get(tone, "calm")
            }
            save_onboarding_profile(profile)
            st.session_state.show_onboarding_quiz = False
            st.session_state.show_mission_1 = True
            st.rerun()
    
    with col2:
        if st.button("Skip", type="secondary", use_container_width=True):
            st.session_state.onboarding_skipped = True
            st.session_state.onboarding_completed = True
            st.session_state.setup_prompt_dismissed = True
            st.session_state.show_onboarding_quiz = False
            # Save to Supabase if logged in
            if st.session_state.get('is_logged_in', False):
                try:
                    save_user_progress()
                except:
                    pass
            st.rerun()

# ============= UPDATE PROFILE MODAL =============
@st.dialog("Update Your Profile", width="medium")
def update_profile_dialog():
    """Modal to choose which quiz to retake"""
    st.markdown("### Choose what to update")
    st.caption("Retake a quiz to refresh your personalized experience")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: rgba(0,217,255,0.1); border-radius: 10px; margin-bottom: 10px;">
            <div style="font-size: 40px; margin-bottom: 10px;">📋</div>
            <h4 style="color: #FFFFFF; margin: 0;">Setup Quiz</h4>
            <p style="color: #B0B0B0; font-size: 0.9em;">60 seconds</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Retake Setup Quiz", use_container_width=True, type="primary", key="retake_setup"):
            st.session_state.show_update_profile = False
            st.session_state.show_onboarding_quiz = True
            st.session_state.onboarding_completed = False
            st.session_state.onboarding_skipped = False
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: rgba(255,68,68,0.1); border-radius: 10px; margin-bottom: 10px;">
            <div style="font-size: 40px; margin-bottom: 10px;">🎯</div>
            <h4 style="color: #FFFFFF; margin: 0;">Risk Quiz</h4>
            <p style="color: #B0B0B0; font-size: 0.9em;">7 questions</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Retake Risk Quiz", use_container_width=True, type="secondary", key="retake_risk"):
            st.session_state.show_update_profile = False
            st.session_state.selected_page = "🧠 Risk Quiz"
            st.session_state.risk_quiz_submitted = False
            st.rerun()
    
    st.markdown("---")
    
    if st.button("Cancel", use_container_width=True, key="cancel_update"):
        st.session_state.show_update_profile = False
        st.rerun()

# ============= MISSION 1 CARD (A4) =============
@st.dialog("Mission 1: Add Your First Paper Position", width="large")
def mission_1_dialog():
    """Post-quiz Mission 1 card"""
    profile = get_personalization_profile()
    
    st.markdown("### Your first mission: Buy a stock (with fake money)")
    st.markdown("Paper trading lets you practice without risking real money.")
    
    # Suggest tickers based on profile
    if profile["knowledge"] == "new" or profile["risk_averse"]:
        st.markdown("**Recommended for beginners:**")
        suggestions = [("SPY", "S&P 500 ETF - Own 500 companies at once"), 
                      ("AAPL", "Apple - Tech giant, stable growth"),
                      ("MSFT", "Microsoft - Enterprise software leader")]
    else:
        st.markdown("**Popular picks:**")
        suggestions = [("GOOGL", "Alphabet - Search, AI, Cloud"),
                      ("NVDA", "NVIDIA - AI chip leader"),
                      ("META", "Meta - Social media, VR")]
    
    for ticker, desc in suggestions:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{ticker}** - {desc}")
        with col2:
            if st.button(f"Add {ticker}", key=f"mission1_{ticker}"):
                set_active_ticker(ticker)
                st.session_state.selected_page = "💼 Paper Portfolio"
                st.session_state.show_mission_1 = False
                st.session_state.mission_1_completed = True
                st.rerun()
    
    st.markdown("---")
    if st.button("Skip for now", type="secondary"):
        st.session_state.show_mission_1 = False
        st.rerun()

# ============= SUCCESS FEEDBACK MODAL (A5) =============
@st.dialog("Congratulations!", width="small")
def first_buy_success_dialog():
    """Success feedback after first paper trade"""
    st.markdown("### You just bought a business, not a lottery ticket.")
    st.markdown("Every share represents ownership in a real company.")
    
    ticker = get_active_ticker()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Understand this company", type="primary", use_container_width=True):
            st.session_state.selected_page = "📊 Company Analysis"
            st.session_state.show_first_buy_success = False
            st.rerun()
    with col2:
        if st.button("Check my risk fit", type="secondary", use_container_width=True):
            st.session_state.selected_page = "🧠 Risk Quiz"
            st.session_state.show_first_buy_success = False
            st.rerun()
    with col3:
        if st.button("Add another", type="secondary", use_container_width=True):
            st.session_state.show_first_buy_success = False
            st.rerun()

# ============= STOCK LOGO HELPER (H2) =============
@st.cache_data(ttl=86400)
def get_stock_logo_url(ticker):
    """Get stock logo URL from FMP profile - cached for 24 hours"""
    try:
        profile = get_profile(ticker)
        if profile and 'image' in profile:
            return profile['image']
    except:
        pass
    return None

# ============= CHECKPOINT QUIZ HELPER (G) =============
def render_checkpoint_quiz(quiz_id, question, options, correct_idx, explanation):
    """Render an optional checkpoint quiz - never blocks navigation"""
    quiz_key = f"quiz_{quiz_id}_answered"
    quiz_answer_key = f"quiz_{quiz_id}_answer"
    
    with st.expander(f"🧠 Quick Check: {question}", expanded=False):
        if st.session_state.get(quiz_key, False):
            # Already answered - show result
            user_answer = st.session_state.get(quiz_answer_key, -1)
            if user_answer == correct_idx:
                st.success(f"Correct! {explanation}")
            else:
                st.error(f"Not quite. The answer is: **{options[correct_idx]}**")
                st.info(explanation)
        else:
            # Show quiz
            for i, option in enumerate(options):
                if st.button(option, key=f"quiz_{quiz_id}_opt_{i}", use_container_width=True):
                    st.session_state[quiz_key] = True
                    st.session_state[quiz_answer_key] = i
                    # Save to Supabase if logged in
                    if st.session_state.get("user_id"):
                        save_user_progress()
                    st.rerun()
            st.caption("Optional - skip anytime!")

# Initialize onboarding state
if 'onboarding_completed' not in st.session_state:
    st.session_state.onboarding_completed = False
if 'onboarding_skipped' not in st.session_state:
    st.session_state.onboarding_skipped = False
if 'setup_prompt_dismissed' not in st.session_state:
    st.session_state.setup_prompt_dismissed = False
if 'show_mission_1' not in st.session_state:
    st.session_state.show_mission_1 = False
if 'show_first_buy_success' not in st.session_state:
    st.session_state.show_first_buy_success = False
if 'first_paper_trade_done' not in st.session_state:
    st.session_state.first_paper_trade_done = False
if 'show_update_profile' not in st.session_state:
    st.session_state.show_update_profile = False
if 'show_onboarding_quiz' not in st.session_state:
    st.session_state.show_onboarding_quiz = False

# ============= AUTH POPUP STATE =============
if 'show_login_popup' not in st.session_state:
    st.session_state.show_login_popup = False
if 'show_signup_popup' not in st.session_state:
    st.session_state.show_signup_popup = False

# ============= CHATBOT STATE =============
if 'chatbot_open' not in st.session_state:
    st.session_state.chatbot_open = False

# ============= TOP NAVIGATION BUTTONS =============
# Check for button clicks via query params (BEFORE rendering buttons)
action_param = st.query_params.get("nav_action")
if isinstance(action_param, (list, tuple)):
    action_param = action_param[0] if action_param else None

# Check for chat button click via query param
chat_param = st.query_params.get("open_chat")
if isinstance(chat_param, (list, tuple)):
    chat_param = chat_param[0] if chat_param else None

if chat_param == "1":
    st.session_state.chatbot_open = True
    if "open_chat" in st.query_params:
        del st.query_params["open_chat"]
    st.rerun()

# Set flag to prevent welcome popup when navigating
if action_param:
    st.session_state.welcome_seen = True

if action_param == "signup":
    st.session_state.show_signup_popup = True
    if "nav_action" in st.query_params:
        del st.query_params["nav_action"]
    st.rerun()
elif action_param == "login":
    st.session_state.show_login_popup = True
    if "nav_action" in st.query_params:
        del st.query_params["nav_action"]
    st.rerun()
elif action_param == "vip":
    st.session_state.selected_page = "👑 Become a VIP"
    if "nav_action" in st.query_params:
        del st.query_params["nav_action"]
    st.rerun()

# Top header with auth buttons (conditional based on login status)
st.markdown(f"""
<style>
.top-header {{
    position: fixed;
    top: 0;
    right: 0;
    left: 0;
    z-index: 9999999;
    background: {'#000000' if st.session_state.theme == 'dark' else '#FFFFFF'};
    padding: 10px 20px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}}
</style>
""", unsafe_allow_html=True)

# Create columns for header buttons at the top
header_cols = st.columns([6, 1, 1, 1] if not st.session_state.get("is_logged_in") else [7, 1.5, 1])
with header_cols[-1]:
    # VIP button always visible
    if st.button("👑 Become a VIP", key="header_vip_btn", use_container_width=True):
        st.session_state.selected_page = "👑 Become a VIP"
        st.rerun()

if st.session_state.get("is_logged_in"):
    # Logged in: show account dropdown
    with header_cols[-2]:
        first_name = st.session_state.get("first_name") or "Account"
        choice = st.selectbox(
            "",
            [f"👤 Hi, {first_name}", "Log out"],
            key="account_menu",
            label_visibility="collapsed"
        )
        if choice == "Log out":
            do_logout()
else:
    # Logged out: show Sign Up and Sign In buttons
    with header_cols[-3]:
        if st.button("📝 Sign Up", key="header_signup_btn", use_container_width=True):
            st.session_state.show_signup_popup = True
            st.rerun()
    with header_cols[-2]:
        if st.button("🔐 Sign In", key="header_login_btn", use_container_width=True):
            st.session_state.show_login_popup = True
            st.rerun()

# Add spacing for frozen bar
st.markdown("<div style='margin-bottom: 80px;'></div>", unsafe_allow_html=True)

# ============= LIVE TICKER BAR =============
render_live_ticker_bar()

# ============= RIGHT-SIDE VERTICAL TICKER (DESKTOP ONLY) =============
render_right_side_ticker()

# ============= AI CHATBOT (BOTTOM-RIGHT) =============
render_ai_chatbot()

# ============= WELCOME POPUP FOR FIRST-TIME USERS =============
show_welcome_popup()

# ============= AUTH POPUPS =============
if st.session_state.get('show_login_popup', False):
    login_dialog()
if st.session_state.get('show_signup_popup', False):
    signup_dialog()

# ============= UPDATE PROFILE MODAL =============
if st.session_state.get('show_update_profile', False):
    update_profile_dialog()

# ============= ONBOARDING QUIZ MODAL (USER-INITIATED) =============
if st.session_state.get('show_onboarding_quiz', False):
    onboarding_quiz_dialog()

# ============= LOGO =============
# Logo positioned above "Investing Made Simple" title, below top icons
try:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", width=600)  # Logo width
except:
    # Fallback text logo
    st.markdown("""
    <div style="text-align: center; padding: 10px 0; margin-bottom: 15px;">
        <h3 style="color: #FF4444; margin: 0; font-size: 1.5em;">STOCKINVESTING.AI</h3>
        <p style="color: #888; margin: 5px 0; font-size: 0.85em;">
            <span style="color: #00D9FF;">LEARN</span> • 
            <span style="color: #FFD700;">INVEST</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============= HEADER =============
col1, col2 = st.columns([3, 1])
with col1:
    st.title("💰 Investing Made Simple")
    st.caption("AI-Powered Stock Analysis for Everyone")
with col2:
    st.markdown("### 🤖 AI-Ready")
    st.caption("FMP Premium")



# ============= VERTICAL SIDEBAR NAVIGATION =============
with st.sidebar:
    st.markdown("## 📚 Navigation")
    
    # Global Timeline Picker
    st.markdown("### ⏱️ Timeline")
    selected_timeline = st.slider(
        "Years of History:",
        min_value=1,
        max_value=30,
        value=5,
        step=1,
        key="global_timeline",
        help="CAGR is the 'smoothed' average return. It shows what you earned every year, ignoring the scary zigs and zags."
    )
    st.session_state.years_of_history = selected_timeline
    
    st.markdown("---")
    
    # Initialize selected page in session state if not exists
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "🏠 Start Here"
    
    # 1. START HERE GROUP
    with st.expander("### 1. 📖 Start Here", expanded=True):
        st.caption("Learn the basics")
        start_here_tools = [
            "🏠 Start Here",
            "📖 Basics",
            "📚 Finance 101",
            "🧠 Risk Quiz"
        ]
        for tool in start_here_tools:
            if st.button(tool, key=f"btn_{tool}", use_container_width=True):
                st.session_state.selected_page = tool
                st.rerun()
    
    # 2. THE ANALYSIS GROUP
    with st.expander("### 2. 📊 The Analysis Group", expanded=False):
        st.caption("The meat of the site")
        analysis_tools = [
            "📊 Company Analysis",
            "📈 Financial Health",
            "📰 Market Intelligence",
            "📊 Market Overview"
        ]
        for tool in analysis_tools:
            if st.button(tool, key=f"btn_{tool}", use_container_width=True):
                st.session_state.selected_page = tool
                st.rerun()
    
    # 3. THE ACTION GROUP
    with st.expander("### 3. 🎯 The Action Group", expanded=False):
        st.caption("Track your progress")
        action_tools = [
            "📊 Pro Checklist",
            "👑 Ultimate",
            "💼 Paper Portfolio",
            "👤 Naman's Portfolio",
            "📜 Founder Track Record"
        ]
        for tool in action_tools:
            if st.button(tool, key=f"btn_{tool}", use_container_width=True):
                st.session_state.selected_page = tool
                st.rerun()
    
    # Get the selected page from session state
    selected_page = st.session_state.selected_page
    
    st.markdown("---")
    
    # ============= MARKET SENTIMENT (Below Action Group) =============
    st.markdown("### 📊 Market Sentiment")
    
    # USE SINGLE SOURCE OF TRUTH for market sentiment - ensures sync everywhere
    sidebar_sentiment = get_global_market_sentiment()
    sentiment_score = sidebar_sentiment["score"]
    sentiment_label = sidebar_sentiment["label"]
    sentiment_color = sidebar_sentiment["color"]
    momentum_20d = sidebar_sentiment.get("momentum_20d", 0)
    
    # Display gauge - same values as Market Intelligence page
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 10px;">
        <div style="font-size: 2em; font-weight: bold; color: {sentiment_color};">{sentiment_score}</div>
        <div style="font-size: 1.2em; color: {sentiment_color};">{sentiment_label}</div>
        <div style="font-size: 0.8em; margin-top: 5px;">S&P 500 20-day: {momentum_20d:+.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("Based on S&P 500 momentum. Not financial advice.")
    
    st.markdown("---")
    
    if 'analysis_view' not in st.session_state:
        st.session_state.analysis_view = "🌟 The Big Picture"
    
    
    # ============= TOGGLE THEME AT BOTTOM OF SIDEBAR =============
    st.markdown("---")
    if st.button("🌓 Toggle Theme", key="sidebar_theme_toggle", use_container_width=True):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
    
    # ============= UNHINGED MODE TOGGLE =============
    st.markdown("---")
    st.markdown("### 🔥 Settings")
    
    # Initialize unhinged_mode if not exists
    if 'unhinged_mode' not in st.session_state:
        st.session_state.unhinged_mode = False
    
    # Check age restriction for unhinged mode
    user_age = st.session_state.get("user_age", 25)
    if user_age < 18:
        st.caption("*Unhinged Mode requires age 18+*")
        st.session_state.unhinged_mode = False
    else:
        unhinged_enabled = st.toggle(
            "🔥 Unhinged Mode",
            value=st.session_state.unhinged_mode,
            key="unhinged_toggle",
            help="Enable playful roast commentary. For entertainment only!"
        )
        if unhinged_enabled != st.session_state.unhinged_mode:
            st.session_state.unhinged_mode = unhinged_enabled
            # Save progress when toggle changes
            save_user_progress()
            st.rerun()
    
    # ============= AUTHENTICATION =============
    st.markdown("---")
    st.markdown("### 🔐 Account")
    
    # Check if logged in
    if st.session_state.get("is_logged_in", False):
        # Show user info and logout
        first_name = st.session_state.get("first_name", "User")
        user_email = st.session_state.get("user_email", "")
        
        st.success(f"👤 {first_name}")
        st.caption(f"{user_email}")
        
        # Show founder badge if applicable
        if st.session_state.get("is_founder", False):
            st.info("👑 Founder Access")
        
        if st.button("🚪 Log Out", use_container_width=True, type="secondary", key="sidebar_logout_btn"):
            do_logout()
    else:
        # Show sign in / sign up buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Sign Up", use_container_width=True, type="primary", key="sidebar_signup_btn"):
                st.session_state.show_signup_popup = True
                st.rerun()
        with col2:
            if st.button("🔐 Sign In", use_container_width=True, type="secondary", key="sidebar_login_btn"):
                st.session_state.show_login_popup = True
                st.rerun()

# ============= HELPER FUNCTIONS FOR PAGES =============

def render_technical_quick_guide(price_data, ticker):
    """Render compact technical quick guide with mini visual examples"""
    with st.expander("📊 Technical Quick Guide (simple examples)"):
        st.caption("*Quick reference for the main indicators shown on this chart*")
        
        # Use last ~120 trading days for examples
        recent_data = price_data.tail(120).copy() if len(price_data) >= 120 else price_data.copy()
        
        if len(recent_data) < 20:
            st.warning("— Not enough data for visual examples")
            return
        
        # ========== SMA 50 ==========
        st.markdown("**SMA 50:** Average price over ~50 days (medium-term trend).")
        st.caption("*Often implies: price above SMA50 = trend stronger; below = weaker.*")
        
        try:
            close_col = 'close' if 'close' in recent_data.columns else 'price'
            # Use min_periods=1 to show line from start (will use fewer points at beginning)
            sma50 = recent_data[close_col].rolling(window=50, min_periods=1).mean()
            
            fig_sma50 = go.Figure()
            fig_sma50.add_trace(go.Scatter(
                x=recent_data['date'], y=recent_data[close_col],
                mode='lines', name='Price', line=dict(color='#9D4EDD', width=1.5)
            ))
            fig_sma50.add_trace(go.Scatter(
                x=recent_data['date'], y=sma50,
                mode='lines', name='SMA 50', line=dict(color='#FFA500', width=2)
            ))
            fig_sma50.update_layout(
                height=240, margin=dict(l=0, r=0, t=10, b=0),
                template='plotly_dark', showlegend=True, legend=dict(orientation="h", y=1.05),
                xaxis_title=None, yaxis_title="Price"
            )
            st.plotly_chart(fig_sma50, use_container_width=True)
        except:
            st.caption("— Chart not available")
        
        st.markdown("---")
        
        # ========== SMA 200 ==========
        st.markdown("**SMA 200:** Average price over ~200 days (long-term trend).")
        st.caption("*Often implies: above SMA200 = long-term bullish; below = long-term bearish.*")
        
        try:
            # Use full dataset for SMA calculation, then display last 200 days
            if len(price_data) >= 200:
                close_col = 'close' if 'close' in price_data.columns else 'price'
                # Calculate SMA 200 on full dataset with min_periods=1
                sma200 = price_data[close_col].rolling(window=200, min_periods=1).mean()
                
                # Display last 200 days
                display_data = price_data.tail(200).copy()
                display_sma200 = sma200.tail(200)
                
                fig_sma200 = go.Figure()
                fig_sma200.add_trace(go.Scatter(
                    x=display_data['date'], y=display_data[close_col],
                    mode='lines', name='Price', line=dict(color='#9D4EDD', width=1.5)
                ))
                fig_sma200.add_trace(go.Scatter(
                    x=display_data['date'], y=display_sma200,
                    mode='lines', name='SMA 200', line=dict(color='#9D4EDD', width=2, dash='dash')
                ))
                fig_sma200.update_layout(
                    height=240, margin=dict(l=0, r=0, t=10, b=0),
                    template='plotly_dark', showlegend=True, legend=dict(orientation="h", y=1.05),
                    xaxis_title=None, yaxis_title="Price"
                )
                st.plotly_chart(fig_sma200, use_container_width=True)
            else:
                st.caption("— Not enough data for SMA 200 example (need 200+ days)")
        except:
            st.caption("— Chart not available")
        
        st.markdown("---")
        
        # ========== RSI ==========
        st.markdown("**RSI (14):** Momentum meter (0–100).")
        st.caption("*Often implies: RSI > 70 = overheated; RSI < 30 = oversold.*")
        
        try:
            close_col = 'close' if 'close' in recent_data.columns else 'price'
            delta = recent_data[close_col].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=recent_data['date'], y=rsi,
                mode='lines', name='RSI', line=dict(color='#FFD700', width=2), fill='tozeroy'
            ))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, annotation_text="70")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, annotation_text="30")
            fig_rsi.update_layout(
                height=240, margin=dict(l=0, r=0, t=10, b=0),
                template='plotly_dark', showlegend=False,
                xaxis_title=None, yaxis_title="RSI", yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig_rsi, use_container_width=True)
        except:
            st.caption("— Chart not available")
        
        st.markdown("---")
        
        # ========== Volume ==========
        st.markdown("**Volume:** How many shares traded.")
        st.caption("*Often implies: breakouts with high volume are more 'real' than low-volume moves.*")
        
        try:
            if 'volume' in recent_data.columns:
                fig_vol = go.Figure()
                fig_vol.add_trace(go.Bar(
                    x=recent_data['date'], y=recent_data['volume'],
                    name='Volume', marker_color='#00BFFF', opacity=0.7
                ))
                fig_vol.update_layout(
                    height=240, margin=dict(l=0, r=0, t=10, b=0),
                    template='plotly_dark', showlegend=False,
                    xaxis_title=None, yaxis_title="Volume"
                )
                st.plotly_chart(fig_vol, use_container_width=True)
            else:
                st.caption("— Volume data not available")
        except:
            st.caption("— Chart not available")
        
        st.markdown("---")
        
        # ========== SUPPORT ==========
        st.markdown("**Support:** Price level where buying interest tends to emerge, preventing further decline.")
        st.caption("*Often implies: if price approaches support, it may bounce; breaking through support can signal weakness.*")
        
        try:
            close_col = 'close' if 'close' in recent_data.columns else 'price'
            
            # Calculate support as 15th percentile of recent prices
            support_level = recent_data[close_col].quantile(0.15)
            
            fig_support = go.Figure()
            fig_support.add_trace(go.Scatter(
                x=recent_data['date'], y=recent_data[close_col],
                mode='lines', name='Price', line=dict(color='#9D4EDD', width=1.5)
            ))
            # Add support line
            fig_support.add_hline(
                y=support_level, 
                line_dash="dot", 
                line_color="#00FF00", 
                line_width=2,
                annotation_text=f"Support ${support_level:.2f}",
                annotation_position="right"
            )
            # Highlight area below support
            fig_support.add_hrect(
                y0=recent_data[close_col].min() * 0.95, 
                y1=support_level,
                fillcolor="green", 
                opacity=0.1,
                line_width=0
            )
            fig_support.update_layout(
                height=240, margin=dict(l=0, r=0, t=10, b=0),
                template='plotly_dark', showlegend=True, legend=dict(orientation="h", y=1.05),
                xaxis_title=None, yaxis_title="Price"
            )
            st.plotly_chart(fig_support, use_container_width=True)
        except:
            st.caption("— Chart not available")
        
        st.markdown("---")
        
        # ========== RESISTANCE ==========
        st.markdown("**Resistance:** Price level where selling pressure tends to emerge, preventing further rise.")
        st.caption("*Often implies: if price approaches resistance, it may stall; breaking above resistance can signal strength.*")
        
        try:
            close_col = 'close' if 'close' in recent_data.columns else 'price'
            
            # Calculate resistance as 85th percentile of recent prices
            resistance_level = recent_data[close_col].quantile(0.85)
            
            fig_resistance = go.Figure()
            fig_resistance.add_trace(go.Scatter(
                x=recent_data['date'], y=recent_data[close_col],
                mode='lines', name='Price', line=dict(color='#9D4EDD', width=1.5)
            ))
            # Add resistance line
            fig_resistance.add_hline(
                y=resistance_level, 
                line_dash="dot", 
                line_color="#FF4B4B", 
                line_width=2,
                annotation_text=f"Resistance ${resistance_level:.2f}",
                annotation_position="right"
            )
            # Highlight area above resistance
            fig_resistance.add_hrect(
                y0=resistance_level, 
                y1=recent_data[close_col].max() * 1.05,
                fillcolor="red", 
                opacity=0.1,
                line_width=0
            )
            fig_resistance.update_layout(
                height=240, margin=dict(l=0, r=0, t=10, b=0),
                template='plotly_dark', showlegend=True, legend=dict(orientation="h", y=1.05),
                xaxis_title=None, yaxis_title="Price"
            )
            st.plotly_chart(fig_resistance, use_container_width=True)
        except:
            st.caption("— Chart not available")


def render_pro_glossary():
    """Legacy function - replaced by render_technical_quick_guide"""
    pass  # Kept for compatibility, no longer used


def build_pro_chart_prompt(ticker: str, context: dict, simple_mode: bool) -> str:
    """Build AI prompt for chart explanation based on ELI5 mode"""
    
    # Extract context
    current_price = context.get('current_price', 'N/A')
    sma_50 = context.get('sma_50', 'N/A')
    sma_200 = context.get('sma_200', 'N/A')
    rsi = context.get('rsi', 'N/A')
    recent_return = context.get('recent_return', 'N/A')
    
    if simple_mode:
        # ELI5 mode - beginner friendly
        prompt = f"""You are explaining stock charts to a complete beginner (like explaining to a 5-year-old).

Ticker: {ticker}
Current Price: ${current_price}
50-day average: ${sma_50}
200-day average: ${sma_200}
RSI (momentum): {rsi}
Recent change: {recent_return}%

Explain the chart in VERY SIMPLE terms:
1. What's the trend? (Is it going up, down, or sideways?)
2. Is it a good time to buy? (Use simple words like "maybe wait" or "looks interesting")
3. What should I watch for? (Explain ONE key thing to pay attention to)

Use simple words. No jargon. Explain like you're talking to someone who's never seen a stock chart before."""
    
    else:
        # Advanced mode - technical analysis
        prompt = f"""You are a professional technical analyst. Analyze this chart setup:

Ticker: {ticker}
Current Price: ${current_price}
SMA 50: ${sma_50}
SMA 200: ${sma_200}
RSI: {rsi}
Recent Return: {recent_return}%

Provide a concise technical analysis:
1. **Trend Assessment**: What's the current trend and strength?
2. **Key Levels**: Important support/resistance levels
3. **Momentum**: RSI interpretation and momentum signals
4. **Risk/Reward**: What traders should watch for

Be specific and actionable. Use technical terms appropriately."""
    
    return prompt


def calculate_pattern_features(price_data):
    """Calculate rule-based features for pattern detection"""
    try:
        # Ensure we have required columns
        if 'close' not in price_data.columns:
            return None
        
        # Get last 6 months of data (approx 126 trading days)
        recent_data = price_data.tail(126).copy()
        
        if len(recent_data) < 20:
            return None
        
        # Calculate features
        close = recent_data['close']
        
        # Moving averages
        ma_20 = close.rolling(window=20).mean().iloc[-1]
        ma_50 = close.rolling(window=50).mean().iloc[-1] if len(recent_data) >= 50 else ma_20
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Returns
        last_20d_return = ((close.iloc[-1] / close.iloc[-20]) - 1) * 100
        
        # Volatility regime
        vol_20d = close.pct_change().tail(20).std() * 100
        vol_60d = close.pct_change().tail(60).std() * 100 if len(recent_data) >= 60 else vol_20d
        
        # Trend strength (slope of MA20)
        ma20_series = close.rolling(window=20).mean().tail(20)
        if len(ma20_series) >= 2:
            trend_slope = (ma20_series.iloc[-1] - ma20_series.iloc[0]) / ma20_series.iloc[0] * 100
        else:
            trend_slope = 0
        
        # Current price
        current_price = close.iloc[-1]
        
        features = {
            'current_price': round(current_price, 2),
            'ma_20': round(ma_20, 2),
            'ma_50': round(ma_50, 2),
            'ma_20_vs_50': 'above' if ma_20 > ma_50 else 'below',
            'price_vs_ma20': round(((current_price / ma_20) - 1) * 100, 2),
            'rsi': round(current_rsi, 1),
            'rsi_zone': 'overbought' if current_rsi > 70 else ('oversold' if current_rsi < 30 else 'neutral'),
            'last_20d_return': round(last_20d_return, 2),
            'vol_20d': round(vol_20d, 2),
            'vol_60d': round(vol_60d, 2),
            'vol_regime': 'low' if vol_20d < vol_60d * 0.7 else ('high' if vol_20d > vol_60d * 1.3 else 'normal'),
            'trend_slope': round(trend_slope, 2),
            'trend_direction': 'up' if trend_slope > 2 else ('down' if trend_slope < -2 else 'sideways')
        }
        
        return features
    
    except Exception as e:
        st.error(f"Error calculating pattern features: {str(e)}")
        return None



def compute_technical_facts(df: pd.DataFrame) -> dict:
    """Deterministic 'facts' for chart + pattern explanations.
    Expects columns: close (required), and optionally open/high/low/volume.
    Fail-soft: returns keys with None when insufficient data.
    """
    facts = {
        "last_close": None,
        "return_5d": None,
        "return_20d": None,
        "return_60d": None,
        "sma50": None,
        "sma200": None,
        "pct_above_sma50": None,
        "pct_above_sma200": None,
        "days_above_sma50_last_60": None,
        "days_above_sma200_last_120": None,
        "sma50_slope": None,
        "sma200_slope": None,
        "rsi14_last": None,
        "rsi14_prev": None,
        "rsi_state": None,
        "rsi_trend": None,
        "vol_20d": None,
        "vol_60d": None,
        "vol_regime": None,
        "atr_pct": None,
        "vol_today": None,
        "vol_avg20": None,
        "volume_spike": None,
        "volume_spike_x": None,
        "volume_trend": None,
        "support_level": None,
        "resistance_level": None,
        "distance_to_support_pct": None,
        "distance_to_resistance_pct": None,
        "data_points": int(len(df)) if df is not None else 0,
    }

    if df is None or len(df) < 10 or "close" not in df.columns:
        return facts

    dfx = df.copy()
    close = pd.to_numeric(dfx["close"], errors="coerce").dropna()
    if len(close) < 10:
        return facts

    facts["last_close"] = float(close.iloc[-1])

    def _safe_ret(n: int):
        if len(close) <= n:
            return None
        base = close.iloc[-(n+1)]
        if base == 0 or pd.isna(base):
            return None
        return float((close.iloc[-1] / base - 1.0) * 100.0)

    facts["return_5d"] = _safe_ret(5)
    facts["return_20d"] = _safe_ret(20)
    facts["return_60d"] = _safe_ret(60)

    # SMAs
    if len(close) >= 50:
        sma50_series = close.rolling(50).mean()
        facts["sma50"] = float(sma50_series.iloc[-1])
        # slope as % over last 10 points of SMA (or fewer)
        tail = sma50_series.dropna().tail(10)
        if len(tail) >= 2 and tail.iloc[0] != 0:
            facts["sma50_slope"] = float((tail.iloc[-1] / tail.iloc[0] - 1.0) * 100.0)

    if len(close) >= 200:
        sma200_series = close.rolling(200).mean()
        facts["sma200"] = float(sma200_series.iloc[-1])
        tail = sma200_series.dropna().tail(10)
        if len(tail) >= 2 and tail.iloc[0] != 0:
            facts["sma200_slope"] = float((tail.iloc[-1] / tail.iloc[0] - 1.0) * 100.0)

    # % above SMAs + days above
    last_close = facts["last_close"]
    if facts["sma50"] is not None and facts["sma50"] != 0:
        facts["pct_above_sma50"] = float((last_close / facts["sma50"] - 1.0) * 100.0)
        last60 = close.tail(60)
        if len(last60) > 0:
            sma50_last60 = close.rolling(50).mean().tail(60)
            valid = (~sma50_last60.isna())
            facts["days_above_sma50_last_60"] = int(((last60 > sma50_last60) & valid).sum())

    if facts["sma200"] is not None and facts["sma200"] != 0:
        facts["pct_above_sma200"] = float((last_close / facts["sma200"] - 1.0) * 100.0)
        last120 = close.tail(120)
        if len(last120) > 0:
            sma200_last120 = close.rolling(200).mean().tail(120)
            valid = (~sma200_last120.isna())
            facts["days_above_sma200_last_120"] = int(((last120 > sma200_last120) & valid).sum())

    # RSI(14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    if len(rsi.dropna()) > 0:
        facts["rsi14_last"] = float(rsi.iloc[-1])
        # previous 1–5 bars ago (use 3 bars if possible)
        prev_idx = -4 if len(rsi) >= 5 else -2
        try:
            facts["rsi14_prev"] = float(rsi.iloc[prev_idx])
        except Exception:
            facts["rsi14_prev"] = None

        r = facts["rsi14_last"]
        if r is not None:
            if r >= 70:
                facts["rsi_state"] = "overbought"
            elif r <= 30:
                facts["rsi_state"] = "oversold"
            else:
                facts["rsi_state"] = "neutral"

        if facts["rsi14_prev"] is not None and facts["rsi14_last"] is not None:
            d = facts["rsi14_last"] - facts["rsi14_prev"]
            if d > 2:
                facts["rsi_trend"] = "rising"
            elif d < -2:
                facts["rsi_trend"] = "falling"
            else:
                facts["rsi_trend"] = "flat"

    # Volatility regime
    ret = close.pct_change().dropna()
    if len(ret) >= 20:
        facts["vol_20d"] = float(ret.tail(20).std() * 100.0)
    if len(ret) >= 60:
        facts["vol_60d"] = float(ret.tail(60).std() * 100.0)
    if facts["vol_20d"] is not None and facts["vol_60d"] is not None and facts["vol_60d"] != 0:
        ratio = facts["vol_20d"] / facts["vol_60d"]
        if ratio < 0.75:
            facts["vol_regime"] = "low"
        elif ratio > 1.25:
            facts["vol_regime"] = "high"
        else:
            facts["vol_regime"] = "normal"

    # ATR% (if OHLC exists)
    if all(c in dfx.columns for c in ["high", "low", "close"]):
        high = pd.to_numeric(dfx["high"], errors="coerce")
        low = pd.to_numeric(dfx["low"], errors="coerce")
        prev_close = pd.to_numeric(dfx["close"], errors="coerce").shift(1)
        tr = pd.concat([
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        if len(atr.dropna()) > 0 and last_close:
            facts["atr_pct"] = float((atr.iloc[-1] / last_close) * 100.0)

    # Volume
    if "volume" in dfx.columns:
        vol = pd.to_numeric(dfx["volume"], errors="coerce").dropna()
        if len(vol) > 0:
            facts["vol_today"] = float(vol.iloc[-1])
        if len(vol) >= 20:
            facts["vol_avg20"] = float(vol.tail(20).mean())
        if facts["vol_today"] is not None and facts["vol_avg20"] not in (None, 0):
            x = facts["vol_today"] / facts["vol_avg20"]
            facts["volume_spike_x"] = float(x)
            facts["volume_spike"] = bool(x >= 1.8)
        if len(vol) >= 20:
            avg5 = float(vol.tail(5).mean())
            avg20 = float(vol.tail(20).mean())
            if avg20 != 0:
                if avg5 / avg20 > 1.15:
                    facts["volume_trend"] = "rising"
                elif avg5 / avg20 < 0.85:
                    facts["volume_trend"] = "falling"
                else:
                    facts["volume_trend"] = "flat"

    # Key levels: choose *nearest* meaningful support/resistance around current price
    # (Prevents absurdly distant "support" from old regimes while staying deterministic per ticker)
    last_close = facts.get("last_close")

    lookback = min(len(close), 180)
    window = close.tail(lookback)

    if last_close is not None and len(window) >= 20:
        candidates_support = []
        candidates_resistance = []

        # Recent swing extremes (more "local" and relevant)
        for n in [20, 50, 90, 120, 180]:
            if len(window) >= n:
                w = window.tail(n)
                candidates_support.append(float(w.min()))
                candidates_resistance.append(float(w.max()))

        # Robust quantiles (still useful, but not the only source)
        for q in [0.10, 0.15, 0.20, 0.25]:
            candidates_support.append(float(window.quantile(q)))
        for q in [0.75, 0.80, 0.85, 0.90]:
            candidates_resistance.append(float(window.quantile(q)))

        # De-dup + filter non-sense
        candidates_support = sorted({c for c in candidates_support if c is not None and np.isfinite(c) and c > 0})
        candidates_resistance = sorted({c for c in candidates_resistance if c is not None and np.isfinite(c) and c > 0})

        # Pick the closest support below last_close; closest resistance above last_close
        support_below = [c for c in candidates_support if c < last_close]
        resistance_above = [c for c in candidates_resistance if c > last_close]

        support = max(support_below) if support_below else (min(candidates_support) if candidates_support else None)
        resistance = min(resistance_above) if resistance_above else (max(candidates_resistance) if candidates_resistance else None)

        facts["support_level"] = float(support) if support is not None else None
        facts["resistance_level"] = float(resistance) if resistance is not None else None

        if facts["support_level"]:
            facts["distance_to_support_pct"] = float((facts["support_level"] / last_close - 1.0) * 100.0)
        if facts["resistance_level"]:
            facts["distance_to_resistance_pct"] = float((facts["resistance_level"] / last_close - 1.0) * 100.0)

    return facts


def render_chart_callouts(facts: dict) -> list:
    """Generate 3–5 deterministic callouts based on facts (no AI).
    Returns list of bullet strings."""
    if not facts or not facts.get("last_close"):
        return []

    bullets = []
    last_close = facts.get("last_close")
    sma50 = facts.get("sma50")
    sma200 = facts.get("sma200")

    if sma50 is not None and facts.get("days_above_sma50_last_60") is not None:
        if last_close > sma50 and facts["days_above_sma50_last_60"] >= 45:
            bullets.append("✅ Price has stayed above SMA50 for most of the last ~3 months — typically bullish trend behavior.")
        elif last_close < sma50:
            bullets.append("⚠️ Price is below SMA50 — short/medium-term trend is often considered weaker.")

    if sma200 is not None:
        if last_close < sma200:
            bullets.append("⚠️ Price is below SMA200 — long-term trend is often considered weaker.")
        else:
            bullets.append("✅ Price is above SMA200 — long-term trend is often considered healthier.")

    rsi = facts.get("rsi14_last")
    if rsi is not None:
        if rsi >= 70:
            bullets.append(f"⚠️ RSI is {rsi:.0f} (overbought zone) — momentum is strong but pullbacks are more common.")
        elif rsi <= 30:
            bullets.append(f"👀 RSI is {rsi:.0f} (oversold zone) — selling pressure may be stretched.")

    if facts.get("volume_spike"):
        x = facts.get("volume_spike_x")
        if x:
            bullets.append(f"✅ Volume spike: today’s volume is ~{x:.1f}× the 20-day average — moves on higher volume are usually more meaningful.")

    # Near key levels
    dtr = facts.get("distance_to_resistance_pct")
    if dtr is not None and dtr <= 3:
        lvl = facts.get("resistance_level")
        if lvl:
            bullets.append(f"👀 Price is ~{dtr:.1f}% from resistance near ${lvl:,.2f}.")

    dts = facts.get("distance_to_support_pct")
    if dts is not None and dts <= 3:
        lvl = facts.get("support_level")
        if lvl:
            bullets.append(f"👀 Price is ~{dts:.1f}% above support near ${lvl:,.2f}.")

    # Keep it tight: 3–5 bullets
    if len(bullets) > 5:
        bullets = bullets[:5]
    return bullets


def check_if_stretched_for_mean_reversion(facts: dict) -> tuple:
    """
    STEP 5: Check if price is stretched enough to warrant 'Mean reversion zone' label.
    Returns: (is_stretched: bool, direction: str)
    direction can be "up", "down", or ""
    """
    if not facts or facts.get("last_close") is None:
        return False, ""
    
    pct_above_sma50 = facts.get("pct_above_sma50")
    return_20d = facts.get("return_20d")
    rsi = facts.get("rsi14_last")
    
    # Calculate stretch metrics
    stretch_from_sma = abs(pct_above_sma50) if pct_above_sma50 is not None else 0
    stretch_from_return = abs(return_20d) if return_20d is not None else 0
    
    # Stretch criteria: must meet at least ONE of these
    is_stretched = (stretch_from_sma >= 8 or stretch_from_return >= 12)
    
    if not is_stretched:
        return False, ""
    
    # Determine direction of stretch
    if rsi is not None and return_20d is not None:
        # GUARDRAIL: If RSI ≥ 75 AND return_20d > +5% AND price > SMA50 → NOT mean reversion
        if rsi >= 75 and return_20d > 5 and pct_above_sma50 is not None and pct_above_sma50 > 0:
            return False, ""  # Too strong for mean reversion - use Overbought momentum instead
        
        # Determine if stretched up or down
        if return_20d > 0 and rsi > 55:
            return True, "up"
        elif return_20d < 0 and rsi < 45:
            return True, "down"
    
    return is_stretched, "neutral"


def generate_trader_actions(facts: dict, pattern_label: str) -> list:
    """
    STEP 6: Generate 5-7 educational bullets about what traders typically watch/do.
    Returns list of action strings.
    """
    if not facts or not facts.get("last_close"):
        return []
    
    actions = []
    rsi = facts.get("rsi14_last")
    pct_above_sma50 = facts.get("pct_above_sma50")
    pct_above_sma200 = facts.get("pct_above_sma200")
    sma50_slope = facts.get("sma50_slope")
    distance_to_resistance_pct = facts.get("distance_to_resistance_pct")
    distance_to_support_pct = facts.get("distance_to_support_pct")
    vol_spike = facts.get("volume_spike")
    vol_regime = facts.get("vol_regime")
    
    # RSI overbought
    if rsi is not None and rsi >= 70:
        actions.append("Watch for cooldown/pullback — overbought readings often precede short-term dips")
    
    # Near resistance
    if distance_to_resistance_pct is not None and distance_to_resistance_pct < 3:
        actions.append("Breakout traders wait for close ABOVE resistance + volume confirmation before entering")
    
    # Above SMA50 with rising slope
    if pct_above_sma50 is not None and pct_above_sma50 > 0 and sma50_slope is not None and sma50_slope > 0:
        actions.append("Pullback-to-SMA50 often watched as re-entry zone in uptrends (dip-buying opportunity)")
    
    # Volume spike
    if vol_spike:
        actions.append("Volume spikes make moves more 'meaningful' — suggests institutional/smart-money activity")
    
    # Below SMA200
    if pct_above_sma200 is not None and pct_above_sma200 < 0:
        actions.append("Below SMA200: many wait for reclaim before considering long positions (long-term weakness)")
    
    # Near support
    if distance_to_support_pct is not None and distance_to_support_pct < 3:
        actions.append("Support test: bounce confirms support strength; break below signals potential breakdown")
    
    # Low volatility
    if vol_regime == "low":
        actions.append("Low volatility 'squeezes' often precede larger directional moves (coiling spring effect)")
    
    # RSI oversold
    if rsi is not None and rsi <= 30:
        actions.append("Oversold conditions: contrarian traders watch for reversal signals (but downtrends can stay oversold)")
    
    return actions[:7]  # Max 7


def build_explain_chart_prompt(facts: dict, rule_based: dict, simple_mode: bool = False) -> str:
    """
    STEP 7A: Build prompt for 'Explain this chart (AI)' button.
    Returns strict JSON-only prompt for Perplexity.
    
    Args:
        facts: Technical facts dict from compute_technical_facts()
        rule_based: Dict with rule-based pattern (label, confidence, reasons, watch_level, watch_note)
        simple_mode: If True, use beginner-friendly language
    
    Returns:
        Prompt string for Perplexity API
    """
    import json
    
    # Clean facts for JSON (remove None values)
    clean_facts = {k: v for k, v in facts.items() if v is not None}
    facts_json = json.dumps(clean_facts, indent=2)
    rule_json = json.dumps(rule_based, indent=2)
    
    language_style = "simple, conversational language (like talking to a friend)" if simple_mode else "clear professional language"
    
    prompt = f"""You are a chart analysis AI assistant. Write in natural, CONVERSATIONAL language.

CRITICAL FORMATTING RULES:
1. Format ALL dollar amounts as: $XXX.XX (with $ sign and 2 decimals)
2. Format ALL percentages as: XX.XX% (with % sign and 2 decimals)
3. Format large numbers with commas: 1,234,567
4. Do NOT include fact_keys, citations, or any technical tags like [sma50] in your response
5. Write in {language_style}
6. Use ONLY the facts provided below - do NOT invent data

FACTS TO USE:
{facts_json}

PATTERN DETECTED:
{rule_json}

Return ONLY this JSON (no markdown, no code blocks):

{{
  "summary_one_liner": "One conversational sentence explaining the current situation (what's happening with this stock right now)",
  "trend": [
    "First observation about trend (where price is vs moving averages) - explain what it means",
    "Second observation about trend direction/strength - why it matters",
    "Third observation about how long trend has lasted - is it reliable?"
  ],
  "momentum": [
    "First observation about RSI (explain if momentum is strong, weak, or neutral) - what it suggests",
    "Second observation about recent price gains/losses - put in context",
    "Third observation about volume (is it high/low, what does that mean)"
  ],
  "key_levels": {{
    "support": {{"level": 123.45, "distance_pct": -2.5}},
    "resistance": {{"level": 150.00, "distance_pct": 3.2}},
    "watch_level": {{"level": 145.50, "note": "Plain English note about this level"}}
  }},
  "risk_notes": [
    "First risk to watch - explain why it's a risk",
    "Second risk - what could go wrong",
    "Third risk - what traders worry about here"
  ],
  "what_to_watch_next_5_days": [
    "First specific thing to monitor (price level, event, pattern)",
    "Second thing to watch",
    "Third thing to watch"
  ]
}}

CRITICAL: 
- NO fact_keys anywhere in output
- NO brackets like [sma50] or [rsi14_last]
- ALL numbers formatted with $, %, or commas as appropriate
- Each bullet should EXPLAIN what the fact MEANS, not just state it
- Write naturally - pretend you're texting a friend about the stock

Example GOOD bullet:
"Price is sitting at $653.06, about 2% above the 50-day average - this suggests buyers have been in control recently"

Example BAD bullet:
"The last close at 653.06 is slightly above the 50-day SMA of 643.3988 (+1.50%).[last_close][sma50][pct_above_sma50]"

Return ONLY the JSON. No other text."""

    return prompt



def build_bull_bear_prompt(facts: dict, simple_mode: bool = False) -> str:
    """
    STEP 7B: Build prompt for 'Bull vs Bear case (AI)' button.
    Returns strict JSON-only prompt for Perplexity.
    
    Args:
        facts: Technical facts dict from compute_technical_facts()
        simple_mode: If True, use beginner-friendly language
    
    Returns:
        Prompt string for Perplexity API
    """
    import json
    
    # Clean facts for JSON
    clean_facts = {k: v for k, v in facts.items() if v is not None}
    facts_json = json.dumps(clean_facts, indent=2)
    
    language_style = "simple conversational language" if simple_mode else "clear professional language"
    
    prompt = f"""You are a chart analysis AI. Present both bull and bear perspectives naturally.

CRITICAL FORMATTING:
1. Format ALL dollar amounts: $XXX.XX (with $, 2 decimals)
2. Format ALL percentages: XX.XX% (with %, 2 decimals)
3. Format large numbers with commas: 1,234,567
4. Do NOT include fact_keys, citations, or any [brackets]
5. Write in {language_style}
6. Use ONLY the facts below - no inventing data

FACTS:
{facts_json}

Return ONLY this JSON (no markdown, no code blocks):

{{
  "bull_case": [
    "First bullish point - explain what's positive and WHY it matters",
    "Second bullish point - what bulls see as good",
    "Third bullish point - what could drive price higher",
    "Fourth bullish point - additional positive factor",
    "Fifth bullish point - final bullish observation"
  ],
  "bear_case": [
    "First bearish point - explain the concern and WHY it's risky",
    "Second bearish point - what bears worry about",
    "Third bearish point - what could push price lower",
    "Fourth bearish point - additional negative factor"
  ],
  "neutral_take": "One sentence balancing both sides - what's the most likely scenario",
  "two_conditions_to_change_view": [
    "What would make you MORE bullish (specific price level or event)",
    "What would make you MORE bearish (specific price level or event)"
  ]
}}

CRITICAL:
- NO fact_keys anywhere
- NO brackets like [sma50] or [last_close]
- ALL numbers properly formatted
- Each point should EXPLAIN what the fact MEANS, not just state it
- Write conversationally - like explaining to a friend

Example GOOD bull point:
"Price is holding above the $650 level, which acted as support twice before - this shows buyers are stepping in"

Example BAD bull point:
"Price remains well above the rising long-term 200-day moving average.[last_close][sma200][pct_above_sma200]"

Return ONLY the JSON. No other text."""
    
    return prompt



def validate_ai_response(ai_output: dict, facts: dict, response_type: str = "explain") -> tuple:
    """
    STEP 7C: Validate AI response against facts.
    Checks that AI didn't invent data or leak internal tags.
    
    Args:
        ai_output: Parsed JSON from Perplexity
        facts: Original technical facts dict
        response_type: "explain" or "bull_bear"
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    if not ai_output or not isinstance(ai_output, dict):
        return False, "AI output is not a valid dict"
    
    try:
        # CRITICAL: Hard-fail if AI leaks internal fact tags like [sma50] into user-facing text
        import re, json
        def _contains_bracket_fact_tags(obj):
            if isinstance(obj, str):
                return re.search(r'\[[a-zA-Z0-9_]+\]', obj) is not None
            if isinstance(obj, list):
                return any(_contains_bracket_fact_tags(x) for x in obj)
            if isinstance(obj, dict):
                return any(_contains_bracket_fact_tags(v) for v in obj.values())
            return False

        if _contains_bracket_fact_tags(ai_output):
            return False, "AI leaked internal fact tags (e.g., [sma50]) into output text"

        # RSI consistency check DISABLED - too strict
        # (The fact-tag validation above is sufficient)

        # Check required fields exist
        if response_type == "explain":
            required = ["summary_one_liner", "trend", "momentum", "key_levels", "risk_notes"]
            for field in required:
                if field not in ai_output:
                    return False, f"Missing required field: {field}"
        
        elif response_type == "bull_bear":
            required = ["bull_case", "bear_case", "neutral_take"]
            for field in required:
                if field not in ai_output:
                    return False, f"Missing required field: {field}"
        
        return True, "OK"
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def clean_citation_tags(text: str) -> str:
    """
    Remove citation arrays and fact tags from text.
    AGGRESSIVELY removes all citation-like patterns.
    
    Args:
        text: Text that might have citation tags
    
    Returns:
        Cleaned text without citation arrays or fact tags
    """
    import re
    
    if not text or not isinstance(text, str):
        return text
    
    # Pattern 1: Remove JSON-style citations like ["key1","key2"] or ['key1','key2']
    # Match anywhere in text, not just at end
    text = re.sub(r'\[[\"\'][a-zA-Z0-9_]+[\"\'](?:\s*,\s*[\"\'][a-zA-Z0-9_]+[\"\'])*\]', '', text)
    
    # Pattern 2: Remove fact tags like [last_close][sma50][pct_above_sma50]
    # This catches multiple consecutive tags
    text = re.sub(r'(?:\[[a-zA-Z0-9_]+\])+', '', text)
    
    # Pattern 3: Remove any remaining single brackets with word inside
    text = re.sub(r'\[[a-zA-Z0-9_]+\]', '', text)
    
    # Pattern 4: Clean up any trailing punctuation issues
    text = re.sub(r'[\.,]\s*[\.,]', '.', text)  # Remove double periods/commas
    text = re.sub(r'\s+([,\.])', r'\1', text)  # Remove space before punctuation
    text = re.sub(r'\s{2,}', ' ', text)  # Remove multiple spaces
    
    # Pattern 5: Clean up ending - if sentence ends with just period and space, clean it
    text = text.strip()
    
    return text


def format_number(value, number_type="number"):
    """
    Format numbers consistently with 2 decimals, $, %, and commas.
    
    Args:
        value: Number to format
        number_type: "dollar", "percent", "number", "volume"
    
    Returns:
        Formatted string
    """
    if value is None:
        return "—"
    
    try:
        num = float(value)
        
        if number_type == "dollar":
            # Format as $XXX.XX with commas
            return f"${num:,.2f}"
        
        elif number_type == "percent":
            # Format as XX.XX%
            return f"{num:.2f}%"
        
        elif number_type == "volume":
            # Format with commas, no decimals
            return f"{int(num):,}"
        
        else:  # "number"
            # Format with commas and 2 decimals
            return f"{num:,.2f}"
    
    except (ValueError, TypeError):
        return str(value)


def detect_rule_based_pattern(facts: dict, simple_mode: bool = False) -> tuple:
    """Deterministic pattern label + confidence + reasons + watch level + watch note.
    Guardrails: avoids nonsensical labels (ex: RSI 88 shouldn't be 'mean reversion zone')."""
    if not facts or facts.get("last_close") is None:
        return ("Not enough data" if not simple_mode else "Need more data", "Low", ["Not enough price history to analyze."], None, "")

    last_close = facts["last_close"]
    sma50 = facts.get("sma50")
    sma200 = facts.get("sma200")
    rsi = facts.get("rsi14_last")
    vol_regime = facts.get("vol_regime")
    ret20 = facts.get("return_20d")
    ret60 = facts.get("return_60d")
    dtr = facts.get("distance_to_resistance_pct")
    dts = facts.get("distance_to_support_pct")
    vol_spike = facts.get("volume_spike")

    up_bias = (sma50 is not None and last_close > sma50) and (facts.get("sma50_slope") is None or facts.get("sma50_slope", 0) >= -0.2)
    down_bias = (sma50 is not None and last_close < sma50) or (sma200 is not None and last_close < sma200)

    # 1) Overbought momentum (guardrail for RSI very high)
    if rsi is not None and rsi >= 75 and up_bias and (ret20 is None or ret20 > 0):
        label = "Overbought momentum" if not simple_mode else "Running hot"
        conf = "High" if (ret20 is not None and ret20 > 5) else "Medium"
        reasons = [
            f"RSI is {rsi:.0f} (overbought) — momentum is strong.",
        ]
        if sma50 is not None:
            reasons.append("Price is above SMA50, supporting an uptrend bias.")
        if vol_spike:
            reasons.append("Move is supported by a volume spike (higher conviction).")
        watch = facts.get("sma50") or facts.get("support_level")
        note = f"Watch ${watch:,.2f} as a support area; a break below can signal cooling." if watch else "Watch support: a break below can signal cooling."
        return (label, conf, reasons[:3], watch, note)

    # 2) Volatility squeeze
    if vol_regime == "low" and (facts.get("vol_20d") is not None and facts.get("vol_60d") is not None):
        label = "Volatility squeeze" if not simple_mode else "Quiet before a move"
        conf = "Medium"
        reasons = [
            "Short-term volatility is lower than the recent baseline (compression).",
            "Compression phases often precede larger directional moves.",
        ]
        if dtr is not None and dtr <= 5:
            reasons.append("Price is sitting near resistance — breakouts can happen from tight ranges.")
        watch = facts.get("resistance_level") or (last_close * 1.03)
        note = f"Watch for a break above ${watch:,.2f} (bullish) or a drop below support." if watch else "Watch for a break above resistance or a drop below support."
        return (label, conf, reasons[:3], watch, note)

    # 3) Breakout attempt
    if dtr is not None and dtr <= 3 and (ret20 is None or ret20 >= 0) and (vol_spike or facts.get("volume_trend") == "rising"):
        label = "Breakout attempt" if not simple_mode else "Trying to break higher"
        conf = "Medium" if not vol_spike else "High"
        lvl = facts.get("resistance_level")
        reasons = [
            "Price is pressing against a nearby resistance level.",
            "Momentum is supportive (recent returns not negative).",
        ]
        if vol_spike:
            reasons.append("Volume spike increases the odds the move is real.")
        watch = lvl
        note = f"Watch ${lvl:,.2f}: a clean break/hold above can confirm breakout." if lvl else "Watch resistance: a break/hold above can confirm."
        return (label, conf, reasons[:3], watch, note)

    # 4) Breakdown risk
    if dts is not None and dts <= 3 and down_bias and (ret20 is None or ret20 <= 0):
        label = "Breakdown risk" if not simple_mode else "At risk of dropping"
        conf = "Medium"
        lvl = facts.get("support_level")
        reasons = [
            "Price is very close to a support zone.",
            "Trend bias is weaker (below key moving average(s)).",
        ]
        if rsi is not None and rsi < 40:
            reasons.append("RSI is weak, which can align with selling pressure.")
        watch = lvl
        note = f"Watch ${lvl:,.2f}: a break below can accelerate downside." if lvl else "Watch support: a break below can accelerate downside."
        return (label, conf, reasons[:3], watch, note)

    # 5) Oversold bounce zone
    if rsi is not None and rsi <= 30 and dts is not None and dts <= 6:
        label = "Oversold bounce zone" if not simple_mode else "Sold too hard"
        conf = "Medium"
        lvl = facts.get("support_level") or facts.get("sma50")
        reasons = [
            f"RSI is {rsi:.0f} (oversold) — selling may be stretched.",
            "Price is near a support area, where bounces sometimes start.",
        ]
        if vol_spike:
            reasons.append("A volume spike can indicate capitulation or a turning point.")
        watch = lvl
        note = f"Watch ${lvl:,.2f}: holding above it supports a bounce scenario." if lvl else "Watch support: holding it supports a bounce scenario."
        return (label, conf, reasons[:3], watch, note)

    # 6) Mean reversion zone (ONLY when stretched)
    is_stretched, stretch_direction = check_if_stretched_for_mean_reversion(facts)
    if is_stretched:
        if stretch_direction == "up":
            label = "Mean reversion zone" if not simple_mode else "Overextended up"
            conf = "Medium"
            reasons = [
                f"Price is stretched {facts.get('pct_above_sma50', 0):.1f}% above SMA50 (overextended).",
                f"RSI at {rsi:.0f} suggests momentum may be cooling.",
                "Mean reversion risk: stretched moves often pullback to moving averages."
            ]
            watch = facts.get("sma50") or facts.get("sma200")
            note = f"Watch ${watch:,.2f}: pullback to this level is common after overextension." if watch else "Watch for pullback to moving averages."
            return (label, conf, reasons[:3], watch, note)
        elif stretch_direction == "down":
            label = "Mean reversion zone" if not simple_mode else "Oversold bounce potential"
            conf = "Medium"
            reasons = [
                f"Price is stretched {abs(facts.get('pct_above_sma50', 0)):.1f}% below SMA50 (overextended down).",
                f"RSI at {rsi:.0f} suggests selling may be stretched.",
                "Mean reversion potential: oversold stretches often bounce back toward moving averages."
            ]
            watch = facts.get("sma50") or facts.get("support_level")
            note = f"Watch ${watch:,.2f}: bounce back toward this level is common after oversold stretch." if watch else "Watch for bounce back toward moving averages."
            return (label, conf, reasons[:3], watch, note)
    
    # 7) Range / sideways (flat movement)
    flat_sma = (facts.get("sma50_slope") is not None and abs(facts["sma50_slope"]) < 0.5)
    flat_ret = (ret20 is not None and abs(ret20) < 3) and (ret60 is None or abs(ret60) < 6)
    rsi_mid = (rsi is not None and 40 <= rsi <= 60)
    if flat_sma and flat_ret:
        if rsi_mid:
            label = "Range / sideways" if not simple_mode else "Mostly sideways"
            conf = "Medium"
            reasons = [
                "Returns are relatively flat and SMA slope is near zero (no clear trend).",
                "This often leads to mean-reversion style back-and-forth movement.",
            ]
            lvl = facts.get("support_level") or facts.get("resistance_level")
            reasons.append("Key levels tend to matter more than trend during ranges.")
            watch = lvl
            note = "Watch support/resistance boundaries — breaks can start a new trend."
            return (label, conf, reasons[:3], watch, note)
    
    # 8) Default: Uptrend / Downtrend continuation
    if up_bias and (ret20 is None or ret20 >= 0):
        label = "Uptrend continuation" if not simple_mode else "Going up steadily"
        conf = "Medium"
        reasons = ["Price is above a key moving average, supporting an uptrend bias."]
        if facts.get("sma50_slope") is not None and facts["sma50_slope"] > 0.5:
            reasons.append("SMA50 slope is rising (trend strength improving).")
        if rsi is not None and rsi < 70:
            reasons.append("RSI is not overbought, leaving room for continuation.")
        watch = facts.get("sma50") or facts.get("support_level")
        note = f"Watch ${watch:,.2f} as support; holding above it keeps the uptrend intact." if watch else "Watch support; holding keeps the uptrend intact."
        return (label, conf, reasons[:3], watch, note)
    
    # Downtrend continuation (replacing "Distribution / weakness")
    label = "Downtrend continuation" if not simple_mode else "Going down steadily"
    conf = "Medium"
    reasons = ["Price is below key moving average(s), supporting a downtrend bias."]
    if rsi is not None and rsi < 45:
        reasons.append("RSI is weak, which supports continued bearish momentum.")
    if ret20 is not None and ret20 < 0:
        reasons.append("Recent returns are negative, reinforcing downside trend.")
    watch = facts.get("support_level") or facts.get("sma50")
    note = f"Watch ${watch:,.2f}: breaking below this level can accelerate downtrend." if watch else "Watch support; breaking it can accelerate downtrend."
    return (label, conf, reasons[:3], watch, note)




def detect_chart_pattern(ticker: str, features: dict, simple_mode: bool) -> dict:
    """Use AI to detect and explain chart patterns"""
    
    if not features:
        return None
    
    # Build AI prompt for pattern detection
    if simple_mode:
        prompt = f"""You are explaining stock chart patterns to a beginner (like a 5-year-old).

Ticker: {ticker}
Current Price: ${features['current_price']}
20-day average: ${features['ma_20']} (price is {features['price_vs_ma20']}% {'above' if features['price_vs_ma20'] > 0 else 'below'})
50-day average: ${features['ma_50']} (20-day is {features['ma_20_vs_50']} 50-day)
Momentum (RSI): {features['rsi']} ({features['rsi_zone']})
Last 20 days: {features['last_20d_return']}%
Trend: {features['trend_direction']}
Volatility: {features['vol_regime']}

What pattern do you see? Choose ONE from:
- "Going up steadily"
- "Trying to break higher"
- "Bouncing in a range"
- "Getting weaker"
- "Quiet before a big move"
- "Needs to cool off"

Respond in this EXACT format:
PATTERN: [one of the patterns above]
CONFIDENCE: [High/Medium/Low]
WHY:
• [Simple reason 1 - one short sentence]
• [Simple reason 2 - one short sentence]
• [Simple reason 3 - one short sentence]
WATCH: $[price level to watch] - [what it means in simple words]

Use VERY simple language. No technical jargon."""

    else:
        prompt = f"""You are a professional technical analyst. Analyze this chart pattern:

Ticker: {ticker}
Current Price: ${features['current_price']}
MA 20: ${features['ma_20']} (price {features['price_vs_ma20']}% vs MA20)
MA 50: ${features['ma_50']} (MA20 {features['ma_20_vs_50']} MA50)
RSI: {features['rsi']} ({features['rsi_zone']})
20-day Return: {features['last_20d_return']}%
Trend: {features['trend_direction']} (slope: {features['trend_slope']}%)
Volatility: {features['vol_regime']} (20d: {features['vol_20d']}%, 60d: {features['vol_60d']}%)

Identify the most likely pattern from:
- "Uptrend continuation"
- "Breakout attempt"
- "Mean reversion zone"
- "Distribution / weakness"
- "Volatility squeeze"
- "Post-consolidation setup"

Respond in this EXACT format:
PATTERN: [one of the patterns above]
CONFIDENCE: [High/Medium/Low]
WHY:
• [Technical reason 1]
• [Technical reason 2]
• [Technical reason 3]
WATCH: $[key level] - [what confirming/breaking this level means]

Be specific and technical. Use proper terminology."""
    
    return prompt


# ============= PAGE CONTENT =============

# ============= HOMEPAGE: START HERE =============
if selected_page == "🏠 Start Here":
    # Debug status line (temporary)
    st.caption(f"🔍 Debug: onboarding_completed={st.session_state.get('onboarding_completed', False)} | setup_prompt_dismissed={st.session_state.get('setup_prompt_dismissed', False)} | logged_in={st.session_state.get('is_logged_in', False)}")
    
    # Non-blocking setup nudge card
    render_setup_nudge()
    
    # Show Mission 1 dialog if triggered
    if st.session_state.get('show_mission_1', False):
        mission_1_dialog()
    
    # Show first buy success dialog if triggered
    if st.session_state.get('show_first_buy_success', False):
        first_buy_success_dialog()
    
    # Hero Visual (H3) - Bull vs Bear theme
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
        <div style="font-size: 60px; margin-bottom: 10px;">🐂 vs 🐻</div>
        <h2 style="color: #FFFFFF; margin: 0;">Learn to Invest Like a Pro</h2>
        <p style="color: #B0B0B0; margin-top: 10px;">Understand the market. Build wealth. Avoid the traps.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Robinhood-style guidance
    st.caption("*Welcome! This is your starting point. We'll guide you through the basics of smart investing.*")
    
    # Show roast if unhinged mode is on (max 1 per session)
    roast = get_session_roast()
    if roast:
        st.info(f"🔥 *{roast}*")
    
    # ============= THE HOOK & BATTLE SCARS NARRATIVE =============
    st.markdown("""
    ### 💔 It's painful to see your portfolio down.
    
    *I'm speaking from experience.* I've lived through the Trump-era trade wars, the 2022 tech crash, and the COVID-19 collapse. 
    Investing isn't about avoiding the storm; it's about knowing **which ships won't sink.**
    
    We focus on **'High Moats'** and **'Monopolistic Power.'** I've stayed strong in winners while avoiding the traps that wiped others out.
    
    **Here is how I distinguish a Fortress from a Value Trap.**
    """)
    
    st.markdown("---")
    
    # ============= WINNER VS TRAP COMPARISON TABLE =============
    st.header("⚔️ The Winner vs. Trap Comparison")
    st.markdown("**Learn from real examples: stocks I bought vs. stocks I avoided.**")
    
    # Define the 8 stocks with their stories
    WEALTH_BUILDERS = {
        "GOOGL": "Dropped to $150 in 2025 on AI fears, but search volume and fundamentals were record-high. I bought aggressively; it's now 2x those lows.",
        "META": "The world hated the 'Metaverse' spend in 2022, but their underlying family of apps (IG/FB) remained a cash-cow with incredible operating efficiency.",
        "NFLX": "Cratered after losing subs for 2 quarters. But they had 'Pricing Power'—they launched ads and stopped account sharing, causing profits to explode.",
        "NVDA": "Dipped on DeepSeek fears, but the Jevons Paradox (efficiency increases demand) meant the need for compute was only going higher."
    }
    
    VALUE_TRAPS = {
        "AMC": "Massive debt levels and constant shareholder dilution (printing new shares) just to pay bills. A classic trap where the business serves the debt, not the owners.",
        "RIVN": "Burning over $1 Billion in cash (FCF) every single quarter for years. Without a path to self-funding, you are just funding their losses.",
        "DJT": "(Non-political analysis) A multi-billion dollar valuation for a company making only a few million in revenue. The fundamentals are too skewed to the stock price.",
        "SNAP": "Peaked at $80+ and is now below $10. I avoided it because of terrible margins and 'Insider Compensation' that ignored shareholders."
    }
    
    # Create two columns for the comparison
    col_winners, col_traps = st.columns(2)
    
    with col_winners:
        st.markdown("### 🏆 The Wealth Builders")
        st.markdown("**(I Bought the Dip)**")
        st.markdown("")
        
        for ticker, story in WEALTH_BUILDERS.items():
            logo_url = get_company_logo(ticker)
            profile = get_profile(ticker)
            company_name = profile.get('companyName', ticker) if profile else ticker
            
            # Display with logo
            if logo_url:
                st.markdown(f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: 15px; padding: 10px; background: rgba(0,200,83,0.1); border-radius: 8px; border-left: 4px solid #00C853;">
                    <img src="{logo_url}" width="40" height="40" style="border-radius: 6px; margin-right: 12px; margin-top: 2px;">
                    <div>
                        <strong style="color: #00C853;">{ticker}</strong> - {company_name}<br>
                        <span style="font-size: 0.9em;">{story}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success(f"**{ticker}**: {story}")
    
    with col_traps:
        st.markdown("### ⚠️ The Value Traps")
        st.markdown("**(I Stayed Away)**")
        st.markdown("")
        
        for ticker, story in VALUE_TRAPS.items():
            logo_url = get_company_logo(ticker)
            profile = get_profile(ticker)
            company_name = profile.get('companyName', ticker) if profile else ticker
            
            # Display with logo
            if logo_url:
                st.markdown(f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: 15px; padding: 10px; background: rgba(255,82,82,0.1); border-radius: 8px; border-left: 4px solid #FF5252;">
                    <img src="{logo_url}" width="40" height="40" style="border-radius: 6px; margin-right: 12px; margin-top: 2px;">
                    <div>
                        <strong style="color: #FF5252;">{ticker}</strong> - {company_name}<br>
                        <span style="font-size: 0.9em;">{story}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"**{ticker}**: {story}")
    
    st.markdown("---")
    
    # ============= INTERACTIVE COMPARISON SECTION =============
    st.header("📊 Compare Any Two Stocks")
    st.markdown("**Pick your own stocks to see the difference in fundamentals.**")
    
    years = st.session_state.years_of_history
    
    # Stock Picker Row
    col_pick1, col_pick2 = st.columns(2)
    with col_pick1:
        stock1 = st.text_input("📈 Good Business:", value=st.session_state.homepage_stock1, key="home_stock1").upper()
        if stock1:
            st.session_state.homepage_stock1 = stock1
    with col_pick2:
        stock2 = st.text_input("📉 Risky Business:", value=st.session_state.homepage_stock2, key="home_stock2").upper()
        if stock2:
            st.session_state.homepage_stock2 = stock2
    
    # Side-by-side Stock Charts with Logos
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        logo1 = get_company_logo(stock1)
        if logo1:
            st.markdown(f'<img src="{logo1}" width="40" style="vertical-align: middle; margin-right: 10px;"> <strong style="font-size: 1.5em;">{stock1}</strong>', unsafe_allow_html=True)
        else:
            st.markdown(f"### {stock1}")
        price1 = get_historical_price(stock1, years)
        if not price1.empty and 'price' in price1.columns:
            fig1 = px.area(price1, x='date', y='price', title=f'{stock1} Stock Price ({years}Y)')
            max_price1 = price1['price'].max()
            fig1.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0), yaxis=dict(range=[0, max_price1 * 1.1]))
            fig1.update_traces(fillcolor='rgba(0, 200, 83, 0.3)', line_color='#00C853')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning(f"No price data for {stock1}")
    
    with col_chart2:
        logo2 = get_company_logo(stock2)
        if logo2:
            st.markdown(f'<img src="{logo2}" width="40" style="vertical-align: middle; margin-right: 10px;"> <strong style="font-size: 1.5em;">{stock2}</strong>', unsafe_allow_html=True)
        else:
            st.markdown(f"### {stock2}")
        price2 = get_historical_price(stock2, years)
        if not price2.empty and 'price' in price2.columns:
            fig2 = px.area(price2, x='date', y='price', title=f'{stock2} Stock Price ({years}Y)')
            max_price2 = price2['price'].max()
            fig2.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0), yaxis=dict(range=[0, max_price2 * 1.1]))
            fig2.update_traces(fillcolor='rgba(255, 82, 82, 0.3)', line_color='#FF5252')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning(f"No price data for {stock2}")
    
    # The Lesson
    st.markdown("---")
    st.markdown("### 📈 Growth Comparison Table (CAGR)")
    st.caption(f"Comparing {years}-year Compound Annual Growth Rates")
    
    # Fetch financial data for both stocks
    income1 = get_income_statement(stock1, 'annual', min(years + 1, 30))
    income2 = get_income_statement(stock2, 'annual', min(years + 1, 30))
    cash1 = get_cash_flow(stock1, 'annual', min(years + 1, 30))
    cash2 = get_cash_flow(stock2, 'annual', min(years + 1, 30))
    
    def calc_cagr_from_df(df, column, years):
        """Calculate CAGR from dataframe"""
        if df.empty or column not in df.columns:
            return None
        df_sorted = df.sort_values('date')
        values = df_sorted[column].dropna()
        if len(values) < 2:
            return None
        start_val = values.iloc[0]
        end_val = values.iloc[-1]
        actual_years = len(values) - 1
        if actual_years <= 0:
            return None
        return calculate_cagr(start_val, end_val, actual_years)
    
    def calc_margin_change(df, numerator_col, denominator_col):
        """Calculate margin change in percentage points"""
        if df.empty or numerator_col not in df.columns or denominator_col not in df.columns:
            return None
        df_sorted = df.sort_values('date')
        if len(df_sorted) < 2:
            return None
        start_margin = df_sorted[numerator_col].iloc[0] / df_sorted[denominator_col].iloc[0] * 100 if df_sorted[denominator_col].iloc[0] != 0 else None
        end_margin = df_sorted[numerator_col].iloc[-1] / df_sorted[denominator_col].iloc[-1] * 100 if df_sorted[denominator_col].iloc[-1] != 0 else None
        if start_margin is None or end_margin is None:
            return None
        return end_margin - start_margin
    
    # Calculate metrics using CAGR
    metrics = {
        "📈 Revenue CAGR": (
            calc_cagr_from_df(income1, 'revenue', years),
            calc_cagr_from_df(income2, 'revenue', years)
        ),
        "💰 Net Income CAGR": (
            calc_cagr_from_df(income1, 'netIncome', years),
            calc_cagr_from_df(income2, 'netIncome', years)
        ),
        "💵 FCF CAGR": (
            calc_cagr_from_df(cash1, 'freeCashFlow', years),
            calc_cagr_from_df(cash2, 'freeCashFlow', years)
        ),
        "📊 Margin Change (pp)": (
            calc_margin_change(income1, 'netIncome', 'revenue'),
            calc_margin_change(income2, 'netIncome', 'revenue')
        )
    }
    
    # Display metrics table with icons
    col_metric, col_stock1, col_stock2 = st.columns([2, 1, 1])
    col_metric.markdown("**Metric**")
    col_stock1.markdown(f"**{stock1}**")
    col_stock2.markdown(f"**{stock2}**")
    
    for metric_name, (val1, val2) in metrics.items():
        col_m, col_v1, col_v2 = st.columns([2, 1, 1])
        col_m.markdown(metric_name)
        
        # Format values with color coding
        if val1 is not None:
            color1 = "green" if val1 > 0 else "red"
            col_v1.markdown(f":{color1}[{val1:+.1f}%]")
        else:
            col_v1.markdown("N/A")
        
        if val2 is not None:
            color2 = "green" if val2 > 0 else "red"
            col_v2.markdown(f":{color2}[{val2:+.1f}%]")
        else:
            col_v2.markdown("N/A")
    
    # Naman's Note - Truth Meter explanation
    st.markdown("---")
    st.markdown("""
    <div class="growth-note">
    <strong>💡 Naman's Note:</strong> I call FCF the "Truth Meter." It shows if a company is making real cash or just playing with accounting numbers. 
    If Net Income is high but FCF is low, someone is hiding something!
    </div>
    """, unsafe_allow_html=True)
    
    # Insight boxes
    col_insight1, col_insight2 = st.columns(2)
    with col_insight1:
        rev1 = metrics["📈 Revenue CAGR"][0]
        fcf1 = metrics["💵 FCF CAGR"][0]
        if rev1 is not None and rev1 > 10:
            st.success(f"**{stock1}**: Strong revenue growth ({rev1:+.1f}% CAGR) - customers want the product!")
        elif rev1 is not None and rev1 > 0:
            st.info(f"**{stock1}**: Moderate growth ({rev1:+.1f}% CAGR) - stable but not explosive")
        elif rev1 is not None:
            st.warning(f"**{stock1}**: Declining revenue ({rev1:+.1f}% CAGR) - warning sign")
        else:
            st.info(f"**{stock1}**: Revenue data not available")
    
    with col_insight2:
        rev2 = metrics["📈 Revenue CAGR"][1]
        fcf2 = metrics["💵 FCF CAGR"][1]
        if fcf2 is not None and fcf2 < -20:
            st.error(f"**{stock2}**: Burning cash ({fcf2:+.1f}% FCF CAGR) - funding their losses!")
        elif rev2 is not None and rev2 < 0:
            st.error(f"**{stock2}**: Declining revenue ({rev2:+.1f}% CAGR) - major red flag")
        elif rev2 is not None:
            st.warning(f"**{stock2}**: Revenue growth of {rev2:+.1f}% CAGR - check the fundamentals")
        else:
            st.info(f"**{stock2}**: Revenue data not available")
    
    # Next Step Button - Direct link to Risk Quiz
    st.markdown("---")
    st.markdown("### 🎯 Understand your risk tolerance")
    st.markdown("Take our quiz to understand how much volatility you're comfortable with. We'll use this to give you better warnings and guidance.")
    
    if st.button("🚀 Take the Risk Quiz →", type="primary", use_container_width=True):
        st.session_state.selected_page = "🧠 Risk Quiz"
        st.rerun()
    
    st.markdown("---")
    st.caption("💡 **Tip:** Use the Timeline picker in the sidebar to see how these metrics change over different time periods!")

# ============= BASICS PAGE =============
# IMPORTANT: This page is fully accessible WITHOUT authentication
# Progress is stored in session_state for logged-out users
# Progress is persisted to Supabase only for logged-in users
elif selected_page == "📖 Basics":
    # Initialize completed lessons set in session state
    if 'completed_lessons' not in st.session_state:
        st.session_state.completed_lessons = set()
    
    # Initialize expanded lesson tracking
    if 'expanded_lesson' not in st.session_state:
        st.session_state.expanded_lesson = None
    
    # Non-blocking setup nudge card (optional on Basics)
    render_setup_nudge()
    
    # Robinhood-style header
    _render_robinhood_header()
    
    # Profile Summary Chip
    profile = st.session_state.user_profile
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.08); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #00D9FF;">
            <p style="color: #B0B0B0; margin: 0; font-size: 0.9em;">Your Profile</p>
            <p style="color: #FFFFFF; margin: 5px 0 0 0;">
                <strong>Experience:</strong> {profile['experience_level'].title()} 
                &nbsp;&nbsp;|&nbsp;&nbsp; 
                <strong>Risk:</strong> {profile['risk_tier'].title()} 
                &nbsp;&nbsp;|&nbsp;&nbsp; 
                <strong>Learning:</strong> {profile['learning_style'].title()}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("⚙️ Update Profile", use_container_width=True):
            st.session_state.show_update_profile = True
            st.rerun()
    
    # Global progress tracking
    total_lessons = 15
    completed_count = len(st.session_state.completed_lessons)
    progress_percentage = (completed_count / total_lessons) * 100
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <p style="color: #FFFFFF; margin: 0;">You've completed {completed_count} of {total_lessons} lessons.</p>
        <div style="background: rgba(255,255,255,0.2); height: 20px; border-radius: 10px; margin-top: 10px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #00D9FF, #0099FF); height: 100%; width: {progress_percentage}%; transition: width 0.3s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Soft sign-up nudge (NON-BLOCKING) - only show for logged-out users with progress
    if not st.session_state.get('is_logged_in', False):
        if completed_count >= 3 and completed_count < total_lessons:
            st.info("💡 **Tip:** Create a free account to save your progress and resume later on any device.")
        elif completed_count == total_lessons:
            st.success("🎉 **Amazing work!** Create a free account to save your achievement and access more features.")
    
    # Robinhood-style progress header (XP / Level / Badges)
    # _render_robinhood_header()

    # Define all lessons structure
    lessons_structure = {
        "1": {
            "title": "Stocks Are Businesses",
            "lessons": [
                {"id": "1.1", "title": "What You Own When You Buy a Stock"},
                {"id": "1.2", "title": "Price ≠ Value"},
                {"id": "1.3", "title": "Why Investing Feels Scary"}
            ]
        },
        "2": {
            "title": "The Investment Thesis",
            "lessons": [
                {"id": "2.1", "title": "What a Thesis Means"},
                {"id": "2.2", "title": "When It's OK to Sell"},
                {"id": "2.3", "title": "When It's NOT OK to Sell"}
            ]
        },
        "3": {
            "title": "Valuation Matters",
            "lessons": [
                {"id": "3.1", "title": "Great Company, Bad Buy"},
                {"id": "3.2", "title": "P/E and P/S (Simple)"},
                {"id": "3.3", "title": "Using History as Guardrails"}
            ]
        },
        "4": {
            "title": "Losing Money (Risk & Psychology)",
            "lessons": [
                {"id": "4.1", "title": "Everyone Takes Losses"},
                {"id": "4.2", "title": "Cutting Losses vs Panic Selling"},
                {"id": "4.3", "title": "Hope Is Not a Strategy"}
            ]
        },
        "5": {
            "title": "Time Is the Cheat Code",
            "lessons": [
                {"id": "5.1", "title": "Time in Market > Timing"},
                {"id": "5.2", "title": "Lump Sum vs DCA"},
                {"id": "5.3", "title": "Why SPY Beats Most People"}
            ]
        }
    }
    # ========= BASICS LESSON CONTENT (Robinhood-style micro-lessons) =========
    # NOTE: This is intentionally self-contained and does NOT touch auth/portfolio math.
    LESSON_CONTENT = {
        "1.1": {
            "goal": "Understand what a share actually represents.",
            "image": "assets/lesson_ownership.png",
            "core": [
                "A stock is a tiny slice of a real business.",
                "You own a claim on future profits (and growth), not a piece of the CEO’s desk.",
                "Price moves fast. The business changes slower."
            ],
            "example": "If a company has 1,000,000 shares and you buy 10 shares → you own 0.001% of the business.",
            "mistake": "Mistake: “I bought $500 of Apple, so I own $500 of Apple’s cash.” You own shares, not the cash drawer.",
            "quiz": [
                {"q": "If profits double but the stock doesn’t move, did the business improve?", "choices": ["Yes", "No"], "a": "Yes", "why": "Business results improved even if price didn’t react yet."},
                {"q": "If the stock halves but profits stay the same, did the business automatically get worse?", "choices": ["Yes", "No"], "a": "No", "why": "Price can move for emotional reasons. Check fundamentals."}
            ],
            "action": "Pick ONE company you like and finish this sentence: “This business makes money by ________.”",
            "tldr": "You’re buying a business slice — not a lottery ticket."
        },
        "1.2": {
            "goal": "Stop confusing price with value.",
            "image": "assets/lesson_price_value.png",
            "core": [
                "Price = what someone pays today.",
                "Value = what the business is worth based on future cash it can produce.",
                "A high stock price doesn’t mean “expensive” and a low price doesn’t mean “cheap”."
            ],
            "example": "A $5 stock can be “bigger” than a $500 stock if it has way more shares. Use Market Cap for size.",
            "mistake": "Mistake: judging a stock by price instead of market cap + business quality.",
            "quiz": [
                {"q": "Which is bigger: a $5 stock or a $500 stock?", "choices": ["$5 stock", "$500 stock", "You can’t know from price alone"], "a": "You can’t know from price alone", "why": "You need shares outstanding / market cap."},
                {"q": "True or False: Price can be wrong short-term.", "choices": ["True", "False"], "a": "True", "why": "Markets are emotional in the short run."}
            ],
            "action": "Look up market cap for 3 stocks you know. Rank them from biggest to smallest.",
            "tldr": "Price is a tag. Value is the thing."
        },
        "1.3": {
            "goal": "Understand why your brain panics — and how to stay calm.",
            "image": "assets/lesson_risk.png",
            "core": [
                "Losses feel worse than gains (your brain is dramatic on purpose).",
                "Headlines are designed to grab attention, not help you invest.",
                "Rules beat vibes. Always."
            ],
            "example": "If your stock drops 10% on no real news, the business might be unchanged — but your brain screams anyway.",
            "mistake": "Mistake: checking prices all day and turning investing into a stress hobby.",
            "quiz": [
                {"q": "If your stock drops but the company grows revenue, what matters more long-term?", "choices": ["The red chart today", "The business results"], "a": "The business results", "why": "Long-term returns follow business performance."},
                {"q": "If you can’t sleep because of a stock, what’s the likely issue?", "choices": ["Too much risk for you", "Markets are broken"], "a": "Too much risk for you", "why": "Position size/risk tolerance mismatch."}
            ],
            "action": "Set a simple rule: “I check long‑term holdings once a week.”",
            "tldr": "Fear is normal. A plan makes you stable."
        },
        "2.1": {
            "goal": "Have a reason BEFORE you buy.",
            "image": "assets/lesson_thesis.png",
            "core": [
                "A thesis is your why: why the business wins, what could break it, and what would make you sell.",
                "A thesis is short. If it’s a novel, it’s not a thesis.",
                "No thesis = panic selling later."
            ],
            "example": "Template: “I’m buying ___ because ___. If ___ happens, I’m wrong. I’ll hold until ___.”",
            "mistake": "Mistake: “I bought because it was trending.” That’s not a thesis, it’s a vibe.",
            "quiz": [
                {"q": "Is “I bought because TikTok said so” a thesis?", "choices": ["Yes", "No"], "a": "No", "why": "A thesis must include business reasons and what would prove you wrong."},
                {"q": "Does a thesis help prevent panic selling?", "choices": ["Yes", "No"], "a": "Yes", "why": "It gives you rules when emotions spike."}
            ],
            "action": "Write a 2‑sentence thesis for ONE stock you own or want to own.",
            "tldr": "Reason → risk → exit plan."
        },
        "2.2": {
            "goal": "Know when selling is smart.",
            "image": "assets/lesson_sell.png",
            "core": [
                "Good reasons: thesis broke, risk too high, better opportunity, or you need cash for life.",
                "Bad reasons: headlines, a red day, or “it feels weird.”",
                "Selling should be a decision, not a reaction."
            ],
            "example": "If the company’s core product demand collapses and competitors win — your thesis might be broken.",
            "mistake": "Mistake: selling just because the chart looks scary today.",
            "quiz": [
                {"q": "If your thesis is intact but the stock is down 20%, should you auto-sell?", "choices": ["Yes", "No"], "a": "No", "why": "Re-check the business first."},
                {"q": "If the business changes permanently, should you reconsider the investment?", "choices": ["Yes", "No"], "a": "Yes", "why": "Thesis broken = reassess or exit."}
            ],
            "action": "Create one sell rule: “If ___ happens, I reassess.”",
            "tldr": "Sell rules > emotions."
        },
        "2.3": {
            "goal": "Avoid the 3 most common bad sell triggers.",
            "image": "assets/lesson_sell.png",
            "core": [
                "Bad trigger #1: selling because you’re bored.",
                "Bad trigger #2: selling because someone else got loud online.",
                "Bad trigger #3: selling just to ‘feel productive’."
            ],
            "example": "A boring stock can be a great long-term compounder. Boring is often a feature.",
            "mistake": "Mistake: confusing activity with progress.",
            "quiz": [
                {"q": "Which is a bad reason to sell?", "choices": ["Thesis broke", "You got bored", "You need rent money"], "a": "You got bored", "why": "Boredom isn’t fundamental."},
                {"q": "True/False: Doing more trades usually means better results.", "choices": ["True", "False"], "a": "False", "why": "Most people trade themselves into worse outcomes."}
            ],
            "action": "If you feel the urge to trade, wait 24 hours and write the reason first.",
            "tldr": "Less motion, more intention."
        },
        "3.1": {
            "goal": "Learn why a great company can still be a bad buy.",
            "image": "assets/lesson_price_value.png",
            "core": [
                "Quality + price paid both matter.",
                "You can overpay for an amazing business.",
                "Valuation is your guardrail against hype."
            ],
            "example": "A great phone is great… but not if it costs $50,000.",
            "mistake": "Mistake: “Great company = automatic buy.”",
            "quiz": [
                {"q": "Can a great company be a bad stock purchase?", "choices": ["Yes", "No"], "a": "Yes", "why": "Price can be too high for future returns."},
                {"q": "What matters more: company OR price?", "choices": ["Company only", "Price only", "Both"], "a": "Both", "why": "Returns depend on business + valuation."}
            ],
            "action": "Pick a company you love. Write a ‘fair price’ range you’d feel good paying.",
            "tldr": "Great business + smart price = winning combo."
        },
        "3.2": {
            "goal": "Understand P/E and P/S without finance jargon.",
            "image": "assets/lesson_thesis.png",
            "core": [
                "P/E: how many dollars investors pay for $1 of profit.",
                "P/S: how many dollars investors pay for $1 of revenue (helpful when profits are low).",
                "Compare ratios inside the same sector, not random industries."
            ],
            "example": "If P/E = 20, investors pay ~$20 for $1 of yearly profit (roughly).",
            "mistake": "Mistake: comparing a bank’s P/E to a software company’s P/E like it means the same thing.",
            "quiz": [
                {"q": "If P/E goes up but earnings don’t, what happened?", "choices": ["Stock got more expensive", "Earnings rose", "Nothing changed"], "a": "Stock got more expensive", "why": "Price rose relative to earnings."},
                {"q": "P/S is most useful when…", "choices": ["Profits are negative or tiny", "Profits are huge", "The CEO tweets"], "a": "Profits are negative or tiny", "why": "Revenue is often more stable than earnings early on."}
            ],
            "action": "Compare P/E and P/S for two companies in the SAME sector.",
            "tldr": "Ratios are context tools, not magic spells."
        },
        "3.3": {
            "goal": "Use history as guardrails (not predictions).",
            "image": "assets/lesson_time.png",
            "core": [
                "5Y/10Y averages give context: cheap vs history, normal, or expensive.",
                "History doesn’t guarantee anything — it just reduces dumb mistakes.",
                "Use it like bumpers in bowling."
            ],
            "example": "If current P/E is far above 10Y average, you may be paying for perfection.",
            "mistake": "Mistake: “Cheap vs history” = guaranteed win.",
            "quiz": [
                {"q": "Is “cheap vs history” a guarantee?", "choices": ["Yes", "No"], "a": "No", "why": "The future can differ from the past."},
                {"q": "Is it still helpful context?", "choices": ["Yes", "No"], "a": "Yes", "why": "It helps you avoid buying pure hype."}
            ],
            "action": "Add a personal rule: if valuation is ‘expensive vs history’, you need a stronger thesis.",
            "tldr": "History is a guardrail, not a crystal ball."
        },
        "4.1": {
            "goal": "Normalize losses so beginners don’t quit.",
            "image": "assets/lesson_risk.png",
            "core": [
                "Every investor takes losses. The difference is how you react.",
                "Judge yourself by process, not one outcome.",
                "Risk is the price of long-term returns."
            ],
            "example": "A -10% month is normal in stocks. The question: did your thesis change?",
            "mistake": "Mistake: thinking a loss means you’re ‘bad’ at investing.",
            "quiz": [
                {"q": "If you never take losses, what are you probably doing?", "choices": ["Learning a lot", "Taking no risk / not investing", "Winning every time"], "a": "Taking no risk / not investing", "why": "Losses are part of participation."},
                {"q": "Best goal for beginners:", "choices": ["Perfect picks", "Perfect timing", "Good decisions consistently"], "a": "Good decisions consistently", "why": "Consistency beats perfection."}
            ],
            "action": "Write: “I will judge myself by my process, not one trade.”",
            "tldr": "Losses are tuition. Don’t rage-quit school."
        },
        "4.2": {
            "goal": "Separate smart exits from emotional exits.",
            "image": "assets/lesson_sell.png",
            "core": [
                "Cut losses when the thesis breaks.",
                "Panic selling is selling because you’re scared, not because you’re right.",
                "Use a ‘thesis check’ before any sell."
            ],
            "example": "Question to ask: “Did anything change in the BUSINESS, or only the chart?”",
            "mistake": "Mistake: selling just to stop feeling uncomfortable.",
            "quiz": [
                {"q": "If the business is fine but price is down, is selling always smart?", "choices": ["Yes", "No"], "a": "No", "why": "Price can be noise."},
                {"q": "If your thesis is wrong, should you hold forever?", "choices": ["Yes", "No"], "a": "No", "why": "Learn, exit, move on."}
            ],
            "action": "Before you sell anything: write one sentence explaining why (business reason).",
            "tldr": "Feelings aren’t fundamentals."
        },
        "4.3": {
            "goal": "Replace hope with a plan.",
            "image": "assets/lesson_thesis.png",
            "core": [
                "“I hope it comes back” is not a strategy.",
                "Plans have triggers, timelines, and reasons.",
                "Your plan makes you calm during chaos."
            ],
            "example": "Plan example: “If revenue declines 2 quarters in a row, I reassess.”",
            "mistake": "Mistake: holding forever because selling would feel like admitting defeat.",
            "quiz": [
                {"q": "If you can’t explain why you own it, what should you do?", "choices": ["Buy more", "Pause and reassess", "Ignore it"], "a": "Pause and reassess", "why": "Clarity beats confusion."},
                {"q": "Hope works best with…", "choices": ["A plan", "A rumor", "A random tweet"], "a": "A plan", "why": "Plans turn hope into discipline."}
            ],
            "action": "Write: “If ___ happens, I sell or reassess.”",
            "tldr": "Hope is a feeling. Strategy is a system."
        },
        "5.1": {
            "goal": "Stop waiting for the perfect moment.",
            "image": "assets/lesson_time.png",
            "core": [
                "Timing tops/bottoms is hard (even pros miss).",
                "Consistency beats brilliance for most people.",
                "Time is your edge — let it work."
            ],
            "example": "Missing a few strong market days can crush long-term results. Consistency keeps you in the game.",
            "mistake": "Mistake: waiting for a dip forever and never starting.",
            "quiz": [
                {"q": "What’s easier: timing tops/bottoms or being consistent?", "choices": ["Timing", "Consistency"], "a": "Consistency", "why": "Consistency doesn’t require prediction."},
                {"q": "Big risk of waiting forever:", "choices": ["Missing growth", "Paying less taxes"], "a": "Missing growth", "why": "Opportunity cost is real."}
            ],
            "action": "Pick a schedule you can maintain: weekly or monthly investing.",
            "tldr": "Start > perfect start."
        },
        "5.2": {
            "goal": "Choose a plan you can stick to (emotion-proof).",
            "image": "assets/lesson_dca.png",
            "core": [
                "Lump sum: more upside if markets rise soon, but harder emotionally.",
                "DCA: smoother emotionally, reduces regret.",
                "Best plan is the one you actually follow."
            ],
            "example": "If you panic easily, DCA can keep you consistent.",
            "mistake": "Mistake: switching plans every week based on headlines.",
            "quiz": [
                {"q": "Best choice depends on…", "choices": ["Your emotions + tolerance", "A guru’s tweet"], "a": "Your emotions + tolerance", "why": "Behavior drives outcomes."},
                {"q": "Which beats doing nothing?", "choices": ["Lump sum", "DCA", "Both"], "a": "Both", "why": "Starting matters more than micro-optimizing."}
            ],
            "action": "Commit to ONE approach for 6 months. No switching.",
            "tldr": "The best strategy is the one you stick with."
        },
        "5.3": {
            "goal": "Understand the ‘default smart choice’ for most people.",
            "image": "assets/lesson_spy.png",
            "core": [
                "SPY (S&P 500) wins because it’s diversified and reduces single-stock mistakes.",
                "Most underperformance is behavior, not intelligence.",
                "If you’re unsure, broad index funds are a strong default."
            ],
            "example": "Owning many businesses reduces the odds one mistake ruins you.",
            "mistake": "Mistake: trying to outsmart the market before learning the basics.",
            "quiz": [
                {"q": "What beats most beginners: 1 stock or owning many?", "choices": ["1 stock", "Many"], "a": "Many", "why": "Diversification reduces single-company risk."},
                {"q": "Biggest investor enemy:", "choices": ["Emotion", "Math"], "a": "Emotion", "why": "Most mistakes are emotional."}
            ],
            "action": "If you’re building a plan, choose a simple ‘core’ (broad index) first.",
            "tldr": "Default smart move: diversify."
        },
    }

    MODULE_CHECKPOINTS = {
        "1": {
            "title": "Checkpoint: Business Thinking",
            "xp": 50,
            "questions": [
                {"q": "A stock represents…", "choices": ["A slice of a business", "A guaranteed return", "A company’s cash"], "a": "A slice of a business"},
                {"q": "Price is…", "choices": ["What someone pays today", "The true value", "The company’s revenue"], "a": "What someone pays today"},
                {"q": "Value is closer to…", "choices": ["Future cash power", "Today’s headline", "A vibe"], "a": "Future cash power"},
                {"q": "Fear comes from…", "choices": ["Brain wiring + uncertainty", "Markets being illegal"], "a": "Brain wiring + uncertainty"},
                {"q": "Best beginner move when scared:", "choices": ["Make rules", "Refresh the chart 50x"], "a": "Make rules"},
            ],
        },
        "2": {
            "title": "Checkpoint: Thesis + Sell Rules",
            "xp": 50,
            "questions": [
                {"q": "A thesis should include…", "choices": ["Why, what breaks it, exit", "Only the ticker"], "a": "Why, what breaks it, exit"},
                {"q": "Good reason to sell:", "choices": ["Thesis broke", "Bored"], "a": "Thesis broke"},
                {"q": "Bad reason to sell:", "choices": ["Red day panic", "Need rent money"], "a": "Red day panic"},
                {"q": "Before selling you should…", "choices": ["Do a thesis check", "Flip a coin"], "a": "Do a thesis check"},
                {"q": "More trading usually means…", "choices": ["More mistakes", "Guaranteed better returns"], "a": "More mistakes"},
            ],
        },
        "3": {
            "title": "Checkpoint: Valuation Basics",
            "xp": 50,
            "questions": [
                {"q": "Great company can be bad buy because…", "choices": ["Overpaying", "It’s illegal"], "a": "Overpaying"},
                {"q": "P/E roughly means…", "choices": ["Price per $1 profit", "Profit per $1 price"], "a": "Price per $1 profit"},
                {"q": "P/S helps when…", "choices": ["Profits are small/negative", "CEO is famous"], "a": "Profits are small/negative"},
                {"q": "History averages are…", "choices": ["Context", "Guarantees"], "a": "Context"},
                {"q": "Cheap vs history is…", "choices": ["Not a sure thing", "A sure thing"], "a": "Not a sure thing"},
            ],
        },
        "4": {
            "title": "Checkpoint: Risk Psychology",
            "xp": 50,
            "questions": [
                {"q": "Losses are…", "choices": ["Normal", "Proof you’re cursed"], "a": "Normal"},
                {"q": "Panic selling is selling because…", "choices": ["Fear", "Thesis broke"], "a": "Fear"},
                {"q": "Cutting losses is best when…", "choices": ["Thesis broke", "Chart is red"], "a": "Thesis broke"},
                {"q": "Hope becomes useful when…", "choices": ["You have a plan", "You ignore it"], "a": "You have a plan"},
                {"q": "Best metric for self-judgment:", "choices": ["Process", "One trade outcome"], "a": "Process"},
            ],
        },
        "5": {
            "title": "Checkpoint: Time + Defaults",
            "xp": 50,
            "questions": [
                {"q": "Time in market usually beats…", "choices": ["Timing", "Learning"], "a": "Timing"},
                {"q": "DCA helps mostly with…", "choices": ["Emotions", "Guaranteed returns"], "a": "Emotions"},
                {"q": "Lump sum can win when…", "choices": ["Markets rise soon", "Markets don’t exist"], "a": "Markets rise soon"},
                {"q": "SPY helps because…", "choices": ["Diversification", "Magic"], "a": "Diversification"},
                {"q": "Biggest investor enemy:", "choices": ["Emotion", "Decimals"], "a": "Emotion"},
            ],
        },
    }

    def _render_lesson_content(lesson_id: str):
        data = LESSON_CONTENT.get(lesson_id)
        if not data:
            st.info("Lesson content missing — add it to LESSON_CONTENT.")
            return

        # image (safe if missing) - compact Robinhood/Duolingo style
        img_path = data.get("image")
        if img_path and os.path.exists(img_path):
            # Wrap image in custom container for size control (ultra-compact 16vh)
            st.markdown("""
            <style>
            .lesson-image-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 10px 0;
                max-height: 16vh;
                overflow: hidden;
            }
            .lesson-image-container img {
                max-height: 16vh;
                max-width: 100%;
                width: auto;
                height: auto;
                object-fit: contain;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Render image with width parameter (no deprecation warning)
            st.image(img_path, width=None)

        st.markdown(f"**Goal:** {data.get('goal','')}")
        st.markdown("**Core idea**")
        for b in data.get("core", []):
            st.markdown(f"- {b}")

        with st.expander("Example", expanded=False):
            st.markdown(data.get("example",""))

        with st.expander("Common mistake", expanded=False):
            st.markdown(data.get("mistake",""))

        st.markdown("**Quick quiz (instant feedback)**")
        quiz = data.get("quiz", [])
        correct = 0
        for i, q in enumerate(quiz):
            key = f"quiz_{lesson_id}_{i}"
            pick = st.radio(q["q"], q["choices"], key=key, horizontal=False)
            if pick == q["a"]:
                correct += 1
        # submit
        if st.button("Check answers", key=f"check_{lesson_id}", type="secondary"):
            for i, q in enumerate(quiz):
                pick = st.session_state.get(f"quiz_{lesson_id}_{i}")
                if pick == q["a"]:
                    st.success(f"Q{i+1}: Correct — {q['why']}")
                else:
                    st.error(f"Q{i+1}: Not quite. Correct answer: **{q['a']}** — {q['why']}")
            if correct == len(quiz) and len(quiz) > 0:
                _award_xp(5, "Perfect quiz")
                _show_confetti_once(f"quiz_{lesson_id}")

        st.markdown("**One action you can do today**")
        st.info(data.get("action",""))

        st.markdown(f"**TL;DR:** {data.get('tldr','')}")

        # Mini interactive widget per lesson (lightweight + fun)
        st.markdown("**Mini tool**")
        if lesson_id in {"1.1", "1.2"}:
            shares = st.slider("How many shares do you own?", 1, 500, 10, key=f"shares_{lesson_id}")
            total = st.number_input("Total shares outstanding (rough guess is fine)", min_value=1, value=1_000_000, step=1000, key=f"out_{lesson_id}")
            pct = (shares / total) * 100.0
            st.write(f"Your ownership: **{pct:.6f}%**")
        elif lesson_id in {"2.1"}:
            st.text_input("Write a 1‑sentence thesis (just type it)", key=f"thesis_{lesson_id}", placeholder="I’m buying ___ because ___. If ___ happens, I’m wrong.")
        elif lesson_id in {"5.2"}:
            plan = st.radio("Which plan fits your personality today?", ["DCA (steady)", "Lump Sum (bold)"], key=f"plan_{lesson_id}")
            st.caption("No wrong answer — pick what you can stick to.")
        else:
            st.caption("Keep it simple: learn → quiz → one action.")

    def _render_module_checkpoint(module_num: str, module_completed: int, module_total: int):
        _ensure_basics_gamification_state()
        cp = MODULE_CHECKPOINTS.get(module_num)
        if not cp:
            return

        # Only show when lessons complete
        if module_completed < module_total:
            return

        passed = module_num in st.session_state.get("checkpoint_passed", set())

        st.markdown("---")
        st.markdown(f"## ✅ {cp['title']}")
        st.caption("5 questions. Get 4/5 to pass and earn a badge + confetti.")
        if passed:
            st.success("Checkpoint passed. Badge unlocked.")
            return

        answers = []
        for i, q in enumerate(cp["questions"]):
            answers.append(st.radio(q["q"], q["choices"], key=f"cp_{module_num}_{i}"))

        if st.button("Submit checkpoint", key=f"submit_cp_{module_num}", type="primary"):
            score = 0
            for i, q in enumerate(cp["questions"]):
                if st.session_state.get(f"cp_{module_num}_{i}") == q["a"]:
                    score += 1
            if score >= 4:
                st.success(f"Passed! Score: {score}/5")
                st.session_state.checkpoint_passed.add(module_num)
                st.session_state.basics_badges.add(module_num)
                _award_xp(int(cp.get("xp", 50)), f"Module {module_num} checkpoint")
                _show_confetti_once(f"cp_{module_num}")
                st.rerun()
            else:
                st.error(f"Score: {score}/5 — you need 4/5. Try again (no shame).")

    
    # Find first incomplete lesson
    first_incomplete = None
    for module_num in ["1", "2", "3", "4", "5"]:
        for lesson in lessons_structure[module_num]["lessons"]:
            if lesson["id"] not in st.session_state.completed_lessons:
                first_incomplete = lesson
                break
        if first_incomplete:
            break
    
    # "Continue where you left off" card
    if completed_count < total_lessons:
        # Case 1: Incomplete lessons
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 2px solid #FFD700; margin-bottom: 20px;">
            <p style="color: #B0B0B0; margin: 0;">Next up:</p>
            <h3 style="color: #FFFFFF; margin: 10px 0;">{first_incomplete["id"]} {first_incomplete["title"]}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # NO AUTHENTICATION REQUIRED - button works for everyone
        if st.button("Continue", key="continue_lesson_btn", type="primary"):
            st.session_state.expanded_lesson = first_incomplete["id"]
            st.rerun()
    else:
        # Case 2: All lessons completed
        st.markdown("""
        <div style="background: rgba(0,255,0,0.1); padding: 20px; border-radius: 15px; border: 2px solid #00FF00; margin-bottom: 20px; text-align: center;">
            <h3 style="color: #FFFFFF; margin: 0;">You've completed the Basics course 🎉</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Review lessons", key="review_lessons_btn", type="secondary"):
            st.session_state.expanded_lesson = None
            st.rerun()
    
    st.markdown("---")
    
    # Render 5 modules
    for module_num in ["1", "2", "3", "4", "5"]:
        module_data = lessons_structure[module_num]
        module_title = module_data["title"]
        module_lessons = module_data["lessons"]
        
        # Calculate module progress
        module_completed = sum(1 for lesson in module_lessons if lesson["id"] in st.session_state.completed_lessons)
        module_total = len(module_lessons)
        
        # Module header with progress
        with st.expander(f"Module {module_num}: {module_title} ({module_completed} / {module_total} completed)", 
                         expanded=True):
            
            # Render each lesson card
            for lesson in module_lessons:
                lesson_id = lesson["id"]
                lesson_title = lesson["title"]
                is_completed = lesson_id in st.session_state.completed_lessons
                is_expanded = st.session_state.expanded_lesson == lesson_id
                
                # Lesson card
                status_text = "Completed" if is_completed else "Not started"
                status_color = "#00FF00" if is_completed else "#B0B0B0"
                border_color = "#00D9FF" if is_expanded else "rgba(255,255,255,0.2)"
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; 
                            border: 2px solid {border_color}; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="color: #FFFFFF; margin: 0;">{lesson_id} {lesson_title}</h4>
                            <p style="color: {status_color}; margin: 5px 0 0 0; font-size: 0.9em;">{status_text}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Lesson controls - NO AUTHENTICATION REQUIRED
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Start lesson button - works for ALL users (logged in or out)
                    if st.button("Start lesson", key=f"start_{lesson_id}", use_container_width=True):
                        st.session_state.expanded_lesson = lesson_id
                        st.rerun()
                
                with col2:
                    # Mark complete button - works for ALL users (logged in or out)
                    if st.button("Mark complete" if not is_completed else "Completed ✓", 
                                key=f"complete_{lesson_id}", 
                                use_container_width=True,
                                disabled=is_completed):
                        st.session_state.completed_lessons.add(lesson_id)
                        _award_xp(10, f"Lesson {lesson_id} complete")
                        # Attempt Supabase persistence ONLY for logged-in users
                        # Falls back silently if user is not logged in - DOES NOT BLOCK UI
                        if st.session_state.get('is_logged_in', False):
                            try:
                                save_user_progress()
                            except:
                                pass
                        st.rerun()
                
                # Expanded lesson panel - NO AUTHENTICATION REQUIRED
                if is_expanded:
                    _render_lesson_content(lesson_id)


                    
                    # Mark complete button in expanded view - works for ALL users
                    if st.button("Mark complete", key=f"complete_expanded_{lesson_id}", type="primary"):
                        st.session_state.completed_lessons.add(lesson_id)
                        _award_xp(10, f"Lesson {lesson_id} complete")
                        st.session_state.expanded_lesson = None
                        # Attempt Supabase persistence ONLY for logged-in users
                        # Falls back silently if user is not logged in - DOES NOT BLOCK UI
                        if st.session_state.get('is_logged_in', False):
                            try:
                                save_user_progress()
                            except:
                                pass
                        st.rerun()
                
                
    # ============= MODULE CHECKPOINTS (badges + confetti) =============
    st.markdown("---")
    st.markdown("## 🧪 Module Checkpoints")
    st.caption("Finish a module’s lessons to unlock its checkpoint. Pass (4/5) to earn a badge.")

    for _m in ["1", "2", "3", "4", "5"]:
        _md = lessons_structure[_m]
        _lessons = _md["lessons"]
        _completed = sum(1 for _l in _lessons if _l["id"] in st.session_state.completed_lessons)
        _total = len(_lessons)
        _render_module_checkpoint(_m, _completed, _total)

    st.markdown("<br>", unsafe_allow_html=True)

elif selected_page == "📚 Finance 101":
    
    st.header("📚 Finance 101")
    st.caption("*Learn the language of investing through visual cards and interactive examples.*")
    
    # ============= TOP 5 METRICS SECTION (C - moved from Company Analysis) =============
    st.markdown("---")
    st.markdown("## 🏆 The 5 Metrics That Actually Matter")
    st.markdown("*These are the numbers that separate winners from losers.*")
    
    # Top 5 Metrics as visual cards (D1)
    metrics_data = [
        {"icon": "💰", "name": "FCF per Share Growth", 
         "definition": "Free cash flow divided by total shares outstanding.", 
         "why": "FCF per share accounts for dilution from stock-based comp. Total FCF can grow 20% but if shares also grow 20%, FCF/share stays flat ($1.00 → $1.00). This is the most honest growth metric.", 
         "example": "Good: Visa — FCF grows faster than shares. Bad: Snap — heavy dilution kills per-share growth"},
        
        {"icon": "⚙️", "name": "Operating Income Growth", 
         "definition": "Profit from core business before interest and taxes.", 
         "why": "Shows real operating leverage. Less noisy than net income because it excludes one-time items and financial engineering.", 
         "example": "Good: Amazon — massive operating leverage as AWS scales. Bad: WeWork — burned cash despite revenue growth"},
        
        {"icon": "📊", "name": "Gross Margin Growth", 
         "definition": "Revenue minus cost of goods sold, as a percentage.", 
         "why": "Rising gross margins indicate pricing power and efficiency. Especially critical for software (should be 70%+) and consumer brands.", 
         "example": "Good: Microsoft — software margins expand with scale. Bad: Peloton — hardware margins collapsed under competition"},
        
        {"icon": "📈", "name": "Revenue Growth", 
         "definition": "Total money coming in from customer sales.", 
         "why": "Important signal of demand, but can be 'bought' with unsustainable discounting or low-quality growth. Always check profitability too.", 
         "example": "Good: NVIDIA — revenue explosion from AI chips. Bad: Uber (early years) — grew revenue while burning billions"},
        
        {"icon": "🛡️", "name": "Quick Ratio", 
         "definition": "(Cash + receivables) / current liabilities. Excludes inventory.", 
         "why": "Measures short-term liquidity and crisis survival. Quick ratio > 1 means the company can pay bills without selling inventory. Essential for risk management.", 
         "example": "Good: Apple — ratio > 1, can survive any storm. Bad: Startups pre-profitability — often < 0.5, vulnerable to funding freezes"}
    ]
    
    # Display as vertical cards (ranked from most to least important)
    for i, metric in enumerate(metrics_data):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 4px solid #FF4444;">
            <div style="font-size: 28px; margin-bottom: 8px;">{metric['icon']}</div>
            <h4 style="color: #FFFFFF; margin: 0 0 8px 0;">#{i+1}: {metric['name']}</h4>
            <p style="color: #B0B0B0; margin: 0 0 8px 0; font-size: 14px;">{metric['definition']}</p>
            <p style="color: #FF6B6B; margin: 0 0 8px 0; font-size: 13px;"><strong>Why it matters:</strong> {metric['why']}</p>
            <p style="color: #4ECDC4; margin: 0; font-size: 12px;"><em>{metric['example']}</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Micro-quiz for Top 5 Metrics (E)
    with st.expander("📝 Quick Quiz: Test Your Knowledge"):
        quiz_answer = st.radio(
            "Which metric best accounts for shareholder dilution from stock-based compensation?",
            ["Total Free Cash Flow", "Revenue Growth", "FCF per Share", "Operating Income"],
            key="finance101_quiz1"
        )
        if st.button("Check Answer", key="check_quiz1"):
            if quiz_answer == "FCF per Share":
                st.success("Correct! FCF per share divides total FCF by shares outstanding, so you see the true per-share growth after dilution.")
            else:
                st.error("Not quite. FCF per share is the answer - it accounts for dilution, unlike total FCF which can grow while per-share value stays flat.")
    
    # ============= VISUAL DIAGRAMS (D2) =============
    st.markdown("---")
    st.markdown("## 📊 How Money Flows Through a Business")
    
    # Revenue to Profit diagram
    st.markdown("""
    <div style="background: #1a1a2e; padding: 25px; border-radius: 12px; margin-bottom: 20px;">
        <h4 style="color: #FFFFFF; text-align: center; margin-bottom: 20px;">The Profit Waterfall</h4>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="background: #4ECDC4; padding: 15px; border-radius: 8px; margin-bottom: 5px;">
                    <span style="color: #000; font-weight: bold;">Revenue</span>
                </div>
                <span style="color: #888; font-size: 12px;">$100</span>
            </div>
            <div style="color: #888; font-size: 20px;">→</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="background: #FFD93D; padding: 15px; border-radius: 8px; margin-bottom: 5px;">
                    <span style="color: #000; font-weight: bold;">Gross Profit</span>
                </div>
                <span style="color: #888; font-size: 12px;">$60 (- costs)</span>
            </div>
            <div style="color: #888; font-size: 20px;">→</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="background: #FF6B6B; padding: 15px; border-radius: 8px; margin-bottom: 5px;">
                    <span style="color: #FFF; font-weight: bold;">Operating Income</span>
                </div>
                <span style="color: #888; font-size: 12px;">$30 (- expenses)</span>
            </div>
            <div style="color: #888; font-size: 20px;">→</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="background: #9D4EDD; padding: 15px; border-radius: 8px; margin-bottom: 5px;">
                    <span style="color: #FFF; font-weight: bold;">Net Income</span>
                </div>
                <span style="color: #888; font-size: 12px;">$20 (- taxes)</span>
            </div>
            <div style="color: #888; font-size: 20px;">→</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="background: #00C853; padding: 15px; border-radius: 8px; margin-bottom: 5px;">
                    <span style="color: #000; font-weight: bold;">Free Cash Flow</span>
                </div>
                <span style="color: #888; font-size: 12px;">$15 (actual cash)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stock = slice of business diagram
    st.markdown("""
    <div style="background: #1a1a2e; padding: 25px; border-radius: 12px; margin-bottom: 20px;">
        <h4 style="color: #FFFFFF; text-align: center; margin-bottom: 15px;">What is a Stock?</h4>
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 50px;">🏢</div>
                <p style="color: #888; margin: 5px 0;">Company</p>
            </div>
            <div style="font-size: 30px; color: #888;">=</div>
            <div style="text-align: center;">
                <div style="font-size: 50px;">🍕🍕🍕🍕</div>
                <p style="color: #888; margin: 5px 0;">Millions of Slices</p>
            </div>
            <div style="font-size: 30px; color: #888;">→</div>
            <div style="text-align: center;">
                <div style="font-size: 50px;">🍕</div>
                <p style="color: #4ECDC4; margin: 5px 0; font-weight: bold;">1 Share = 1 Slice</p>
            </div>
        </div>
        <p style="color: #B0B0B0; text-align: center; margin-top: 15px; font-size: 14px;">When you buy a stock, you own a tiny piece of a real business.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk spectrum meter
    st.markdown("""
    <div style="background: #1a1a2e; padding: 25px; border-radius: 12px; margin-bottom: 20px;">
        <h4 style="color: #FFFFFF; text-align: center; margin-bottom: 15px;">Risk Spectrum</h4>
        <div style="display: flex; justify-content: space-between; align-items: center; background: linear-gradient(90deg, #00C853 0%, #FFD93D 50%, #FF4444 100%); padding: 15px; border-radius: 8px;">
            <div style="text-align: center;">
                <span style="color: #000; font-weight: bold;">Treasury Bonds</span><br>
                <span style="color: #000; font-size: 12px;">~4% return</span>
            </div>
            <div style="text-align: center;">
                <span style="color: #000; font-weight: bold;">S&P 500 ETF</span><br>
                <span style="color: #000; font-size: 12px;">~10% avg</span>
            </div>
            <div style="text-align: center;">
                <span style="color: #FFF; font-weight: bold;">Individual Stocks</span><br>
                <span style="color: #FFF; font-size: 12px;">Varies wildly</span>
            </div>
            <div style="text-align: center;">
                <span style="color: #FFF; font-weight: bold;">Meme Stocks</span><br>
                <span style="color: #FFF; font-size: 12px;">Casino 🎰</span>
            </div>
        </div>
        <p style="color: #B0B0B0; text-align: center; margin-top: 10px; font-size: 13px;">Higher potential returns = Higher risk of loss</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============= INTERACTIVE WIDGETS (D3) =============
    st.markdown("---")
    st.markdown("## 🎮 Try It: Interactive Learning")
    
    # What if price drops widget
    st.markdown("### What if the price drops?")
    drop_pct = st.slider("Simulate a price drop:", 0, 50, 20, 5, key="price_drop_slider")
    initial_value = 10000
    new_value = initial_value * (1 - drop_pct / 100)
    recovery_needed = ((initial_value / new_value) - 1) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Starting Value", f"${initial_value:,.0f}")
    with col2:
        st.metric("After Drop", f"${new_value:,.0f}", f"-{drop_pct}%")
    with col3:
        st.metric("Recovery Needed", f"+{recovery_needed:.1f}%", help="To get back to your starting value")
    
    st.caption(f"*If your portfolio drops {drop_pct}%, you need a {recovery_needed:.1f}% gain just to break even. This is why avoiding big losses matters!*")
    
    # Compound interest widget
    st.markdown("### The Power of Compounding")
    years_compound = st.slider("Years invested:", 1, 30, 10, key="compound_years")
    annual_return = st.slider("Annual return (%):", 1, 20, 8, key="compound_return")
    
    initial_invest = 10000
    final_value = initial_invest * ((1 + annual_return / 100) ** years_compound)
    total_gain = final_value - initial_invest
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Initial Investment", f"${initial_invest:,.0f}")
    with col2:
        st.metric(f"After {years_compound} Years", f"${final_value:,.0f}", f"+${total_gain:,.0f}")
    
    st.caption(f"*At {annual_return}% annual return, your money grows {final_value/initial_invest:.1f}x in {years_compound} years. Time is your biggest advantage!*")
    
    # ============= GLOSSARY SECTION =============
    st.markdown("---")
    st.markdown("## 📖 Full Glossary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Income & Cash Flow")
        for term in ["FCF After SBC", "Revenue", "Operating Income", "Net Income", "CAGR", "FCF per Share"]:
            with st.expander(term):
                st.write(GLOSSARY[term])
    
    with col2:
        st.markdown("### 📊 Valuation & Risk")
        for term in ["P/E Ratio", "P/S Ratio", "Market Cap", "Beta", "Debt-to-Equity", "Quick Ratio"]:
            with st.expander(term):
                st.write(GLOSSARY[term])


elif selected_page == "🧠 Risk Quiz":
    
    st.header("🎯 Investment Risk Analysis Quiz")
    st.markdown("### Understand your risk tolerance")
    
    st.info("💡 **This helps us understand how much volatility you're comfortable with.** We use this to give better warnings and guidance — not to block you from anything.")
    
    # Initialize session state for quiz
    if 'risk_quiz_submitted' not in st.session_state:
        st.session_state.risk_quiz_submitted = False
    
    with st.form("risk_quiz_form"):
        st.markdown("### 📊 Your Risk Tolerance")
        
        # Question 1: Worst-case drawdown tolerance
        q1 = st.radio(
            "1. If your account dropped 35% in a recession, what would you most likely do?",
            ["Sell most positions immediately",
             "Sell some to reduce stress",
             "Hold and wait it out",
             "Buy more over time"]
        )
        
        # Question 2: Volatility reality check
        q2 = st.radio(
            "2. Which feels more painful?",
            ["Losing $1,000 in a week",
             "Missing a $1,000 gain",
             "Both about the same",
             "Neither bothers me much"]
        )
        
        # Question 3: Concentration tolerance
        q3 = st.radio(
            "3. How comfortable are you with one stock being a large part of your portfolio?",
            ["Not comfortable — I want diversification",
             "A little is fine (10–20%)",
             "I'm okay with big bets (30–50%)",
             "I prefer concentrated bets (50%+)"]
        )
        
        # Question 4: Time to recover
        q4 = st.radio(
            "4. If an investment is down, how long are you willing to wait to recover?",
            ["Weeks",
             "Months",
             "1–3 years",
             "3+ years"]
        )
        
        # Question 5: Reaction under uncertainty
        q5 = st.radio(
            "5. When you see scary headlines about your holdings, you usually…",
            ["Sell quickly to avoid more loss",
             "Watch closely and feel stressed",
             "Do more research before acting",
             "Ignore headlines and stick to the plan"]
        )
        
        # Question 6: Income stability (risk capacity proxy)
        q6 = st.radio(
            "6. How stable is your income right now?",
            ["Unstable / uncertain",
             "Somewhat stable",
             "Stable",
             "Very stable with strong savings"]
        )
        
        # Question 7: Knowledge + behavior check (guardrail)
        q7 = st.radio(
            "7. Which best describes how you choose investments?",
            ["Tips / trends / social media",
             "Mostly price charts and vibes",
             "Mix of fundamentals + valuation",
             "Long-term fundamentals + discipline"]
        )
        
        submitted = st.form_submit_button("🎯 Get My Results", use_container_width=True, type="primary")
        
        if submitted:
            # Calculate risk score (1-4 points per question)
            score_map = {
                q1: {"Sell most positions immediately": 1, "Sell some to reduce stress": 2, "Hold and wait it out": 3, "Buy more over time": 4},
                q2: {"Losing $1,000 in a week": 1, "Missing a $1,000 gain": 2, "Both about the same": 3, "Neither bothers me much": 4},
                q3: {"Not comfortable — I want diversification": 1, "A little is fine (10–20%)": 2, "I'm okay with big bets (30–50%)": 3, "I prefer concentrated bets (50%+)": 4},
                q4: {"Weeks": 1, "Months": 2, "1–3 years": 3, "3+ years": 4},
                q5: {"Sell quickly to avoid more loss": 1, "Watch closely and feel stressed": 2, "Do more research before acting": 3, "Ignore headlines and stick to the plan": 4},
                q6: {"Unstable / uncertain": 1, "Somewhat stable": 2, "Stable": 3, "Very stable with strong savings": 4},
                q7: {"Tips / trends / social media": 1, "Mostly price charts and vibes": 2, "Mix of fundamentals + valuation": 3, "Long-term fundamentals + discipline": 4}
            }
            
            risk_score = sum([score_map[q][q] for q in [q1, q2, q3, q4, q5, q6, q7]])
            
            # Map score to risk tier
            if risk_score <= 12:
                risk_tier = "Conservative"
            elif risk_score <= 18:
                risk_tier = "Moderate"
            elif risk_score <= 23:
                risk_tier = "Growth"
            else:
                risk_tier = "Aggressive"
            
            # Store results in session state
            from datetime import datetime
            st.session_state.risk_tier = risk_tier
            st.session_state.risk_score = risk_score
            st.session_state.risk_quiz_completed_at = datetime.now().isoformat()
            st.session_state.risk_quiz_submitted = True
            
            # Build unified user profile
            build_user_profile()
            
            # Save to Supabase if logged in
            if st.session_state.get('is_logged_in', False):
                try:
                    save_user_progress()
                except:
                    pass  # Silent fallback to session state
            
            st.rerun()
    
    # Show results if quiz completed
    if st.session_state.get('risk_quiz_submitted', False):
        st.markdown("---")
        
        risk_tier = st.session_state.risk_tier
        risk_score = st.session_state.risk_score
        
        # Title
        st.markdown(f"## 🎯 Your Risk Style: {risk_tier}")
        
        # Color-coded tier display
        tier_colors = {
            "Conservative": "🟢",
            "Moderate": "🟡",
            "Growth": "🟠",
            "Aggressive": "🔴"
        }
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Risk Tier", f"{tier_colors.get(risk_tier, '')} {risk_tier}", f"Score: {risk_score}/28")
        
        # Interpretations (3 bullets)
        interpretations = {
            "Conservative": [
                "You prioritize capital preservation over high returns",
                "You prefer stability and are uncomfortable with large swings",
                "You likely have a shorter time horizon or lower risk capacity"
            ],
            "Moderate": [
                "You're comfortable with moderate volatility for reasonable growth",
                "You can tolerate temporary losses but want some downside protection",
                "You balance between safety and opportunity"
            ],
            "Growth": [
                "You're willing to accept significant volatility for higher returns",
                "You can handle drawdowns and stay focused on long-term goals",
                "You have strong conviction and can wait years for recovery"
            ],
            "Aggressive": [
                "You're seeking maximum returns and embrace high volatility",
                "You view market crashes as buying opportunities, not panic signals",
                "You have strong risk capacity (time, income, savings, discipline)"
            ]
        }
        
        with col2:
            st.markdown("**What this means:**")
            for bullet in interpretations.get(risk_tier, []):
                st.markdown(f"• {bullet}")
        
        st.markdown("---")
        
        # "What this affects" box (exact copy)
        st.info("""
**What this changes in the app:**
• The warnings you see (volatility + concentration)  
• How the chatbot frames risk  
• Suggested default examples in lessons  

**What this does NOT change:**
• It does not block you from anything  
• It does not place trades for you
        """)
        
        st.markdown("---")
        
        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save Results", use_container_width=True, type="primary"):
                if st.session_state.get('is_logged_in', False):
                    try:
                        save_user_progress()
                        st.success("✅ Results saved to your account!")
                    except:
                        st.warning("⚠️ Could not save to account, but results are stored in this session.")
                else:
                    st.info("💡 Create an account to save your results permanently across devices.")
        
        with col2:
            if st.button("🔄 Retake Quiz", use_container_width=True, type="secondary"):
                st.session_state.risk_quiz_submitted = False
                st.rerun()



elif selected_page == "📊 Company Analysis":
    
    # Robinhood-style guidance
    st.caption("*This page explains how this company makes money and where the risks are.*")
    
    search = st.text_input(
        "🔍 Search by Company Name or Ticker:",
        st.session_state.selected_ticker,
        help="Try: Apple, AAPL, Microsoft, TSLA, etc."
    )
    
    if search:
        ticker, company_name = smart_search_ticker(search)
        st.session_state.selected_ticker = ticker
        if ticker != search.upper():
            st.success(f"Found: {company_name} ({ticker})")
    else:
        ticker = st.session_state.selected_ticker
    
    # Show Welcome view if no ticker is selected or default AAPL
    if not ticker or ticker == "AAPL" and not search:
        st.markdown("## 👋 Welcome to Company Analysis!")
        st.markdown("Not sure where to start? Here are some popular stocks to explore:")
        
        # Starter stocks grid
        starter_stocks = [
            ("AAPL", "Apple Inc.", "Tech giant - iPhones, Macs, Services. One of the world's most valuable companies."),
            ("MSFT", "Microsoft", "Enterprise software leader - Windows, Office, Azure cloud. Steady growth + dividends."),
            ("SPY", "S&P 500 ETF", "Own a piece of 500 top US companies. The benchmark for the stock market."),
            ("GOOGL", "Alphabet (Google)", "Search, YouTube, Cloud, AI. Dominant in digital advertising.")
        ]
        
        col1, col2 = st.columns(2)
        for i, (stock_ticker, stock_name, stock_desc) in enumerate(starter_stocks):
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    st.markdown(f"### {stock_ticker}")
                    st.markdown(f"**{stock_name}**")
                    st.caption(stock_desc)
                    
                    # Get quick price info
                    try:
                        quote = get_quote(stock_ticker)
                        if quote:
                            price = quote.get('price', 0)
                            change = quote.get('changesPercentage', 0)
                            st.metric("Price", f"${price:.2f}", f"{change:+.2f}%")
                    except:
                        pass
                    
                    if st.button(f"📊 Analyze {stock_ticker}", key=f"starter_{stock_ticker}"):
                        st.session_state.selected_ticker = stock_ticker
                        st.rerun()
                    
                    st.markdown("---")
        
        st.info("💡 **Tip:** Type any company name or ticker symbol in the search box above to get started!")
        st.stop()
    
    profile = get_profile(ticker)
    has_company = profile is not None
    
    if has_company:
        company_name = profile.get('companyName', ticker)
        sector = profile.get('sector', 'N/A')
        industry = profile.get('industry', 'N/A')
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"📈 {company_name} ({ticker})")
            st.caption(f"**Sector:** {sector} | **Industry:** {industry}")
        
        with col2:
            earnings = get_earnings_calendar(ticker)
            if earnings:
                earnings_date = earnings.get('date', '')
                if earnings_date:
                    try:
                        date_obj = datetime.strptime(earnings_date, '%Y-%m-%d')
                        days_until = (date_obj - datetime.now()).days
                        
                        if days_until >= 0:
                            st.info(f"📅 **Next Earnings**\n{date_obj.strftime('%b %d, %Y')}\n({days_until} days)")
                        else:
                            st.caption(f"Last earnings: {date_obj.strftime('%b %d, %Y')}")
                    except:
                        pass
        
        description = profile.get('description', '')
        if description:
            with st.expander("ℹ️ What does this company do?"):
                st.write(description[:500] + "..." if len(description) > 500 else description)
    else:
        company_name = ticker
        sector = "Unknown"
        st.subheader(f"{ticker}")
    
    # Fit Check Panel
    render_fit_check_panel(ticker)
    
    st.markdown("---")
    
    income_df = get_income_statement(ticker, 'annual', 5)
    cash_df = get_cash_flow(ticker, 'annual', 5)
    balance_df = get_balance_sheet(ticker, 'annual', 5)
    ratios_df = get_financial_ratios(ticker, 'annual', 5)
    
    fcf_cagr = None
    if cash_df is not None and not cash_df.empty and 'freeCashFlow' in cash_df.columns:
        fcf_values = cash_df['freeCashFlow'].dropna()
        if len(fcf_values) >= 2:
            start_fcf = fcf_values.iloc[-1]
            end_fcf = fcf_values.iloc[0]
            if start_fcf > 0 and end_fcf > 0:
                years_count = len(fcf_values) - 1
                if years_count > 0:
                    fcf_cagr = calculate_cagr(start_fcf, end_fcf, years_count)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        period_type = st.radio("Time Period:", ["Annual", "Quarterly"])
        period = 'annual' if period_type == "Annual" else 'quarter'
        years = st.slider("Years of History:", 1, 30, 5)
        
        st.markdown("---")
        
        if has_company:
            st.markdown("### 🔍 Explore This Company")
            view = st.radio(
                "Choose what to analyze:",
                ["🌟 The Big Picture", "💪 Financial Health", "💰 Price & Future Value", "⚠️ Risk Report"],
                key="analysis_view_radio",
                help="Pick a category to explore different aspects of this company"
            )
            st.session_state.analysis_view = view
            st.markdown("---")
        else:
            st.info("🔍 Search for a company above to unlock analysis options!")
            view = "🌟 The Big Picture"
        
        st.markdown("### 📊 Quick Stats")
        
        if fcf_cagr:
            st.metric("FCF Growth", f"{fcf_cagr:+.1f}%",
                     help="How fast is the company's free cash flow growing?")
        
        price_data = get_historical_price(ticker, years)
        if not price_data.empty and len(price_data) > 1 and 'price' in price_data.columns:
            start_price = price_data['price'].iloc[0]
            end_price = price_data['price'].iloc[-1]
            price_growth = ((end_price - start_price) / start_price) * 100
            st.metric(f"Stock Growth ({years}Y)", f"{price_growth:+.1f}%",
                     help=f"How much has the stock price changed over {years} years?")
        
        st.markdown("---")
        
        st.markdown("### ⚠️ Health Check")
        
        de_ratio = calculate_debt_to_equity(balance_df)
        if de_ratio > 0:
            if de_ratio > 2.0:
                st.error(f"Debt Level: {de_ratio:.2f} 🔴")
                st.caption("High debt - be careful!")
            elif de_ratio > 1.0:
                st.warning(f"Debt Level: {de_ratio:.2f} 🟡")
                st.caption("Moderate debt")
            else:
                st.success(f"Debt Level: {de_ratio:.2f} 🟢")
                st.caption("Low debt - good!")
        
        qr = calculate_quick_ratio(balance_df)
        if qr > 0:
            if qr < 1.0:
                st.warning(f"Cash on Hand: {qr:.2f} 🟡")
                st.caption("Might struggle to pay bills")
            else:
                st.success(f"Cash on Hand: {qr:.2f} 🟢")
                st.caption("Can pay bills easily")


    quote = get_quote(ticker)
    ratios_ttm = get_ratios_ttm(ticker)
    
    if quote:
        price = quote.get('price', 0)
        change_pct = quote.get('changesPercentage', 0)
        market_cap = quote.get('marketCap', 0)
        
        pe = get_pe_ratio(ticker, quote, ratios_ttm, income_df)
        ps = get_ps_ratio(ticker, ratios_ttm)
        fcf_per_share = calculate_fcf_per_share(ticker, cash_df, quote)
        
        # Get price target for estimate - try consensus API first, then summary, then AI fallback
        price_target_consensus = get_price_target_consensus(ticker)
        price_target_data = get_price_target_summary(ticker)
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Current Price", f"${price:.2f}", f"{change_pct:+.2f}%")
        col2.metric("Market Cap", format_number(market_cap),
                   help=explain_metric("Market Cap", market_cap, sector))
        
        if pe < 0:
            col3.metric("P/E Ratio (TTM)", "Negative",
                       help="This company is currently losing money, so it doesn't have a P/E ratio yet. Not necessarily bad for growth companies!")
        elif pe > 0:
            col3.metric("P/E Ratio (TTM)", f"{pe:.2f}",
                       help=explain_metric("P/E Ratio", pe, sector))
        else:
            col3.metric("P/E Ratio (TTM)", "N/A",
                       help="P/E ratio not available. The company may not have reported earnings yet.")
        
        col4.metric("P/S Ratio", f"{ps:.2f}" if ps > 0 else "N/A",
                   help=explain_metric("P/S Ratio", ps, sector))
        
        col5.metric("FCF Per Share", f"${fcf_per_share:.2f}" if fcf_per_share > 0 else "N/A",
                   help="Free Cash Flow divided by shares outstanding")
        
        # Wall Street 1-Yr Price Target - try consensus API first, then summary, then AI fallback
        target_avg = None
        num_analysts = None
        
        # Try consensus API first
        if price_target_consensus:
            target_avg = price_target_consensus.get('targetConsensus', 0)
            if not target_avg or target_avg <= 0:
                target_avg = price_target_consensus.get('targetMedian', 0)
        
        # Fallback to summary API
        if (not target_avg or target_avg <= 0) and price_target_data:
            target_avg = price_target_data.get('targetConsensus', 0) or price_target_data.get('targetMean', 0) or price_target_data.get('targetMedian', 0)
            num_analysts = price_target_data.get('numberOfAnalysts', None)
        
        # Final fallback to Perplexity AI
        if not target_avg or target_avg <= 0:
            target_avg = get_ai_price_target(ticker, company_name)
        
        if target_avg and target_avg > 0 and price > 0:
            upside = ((target_avg - price) / price) * 100
            help_text = f"Wall Street consensus 12-month price target."
            if num_analysts:
                help_text += f" Based on {num_analysts} analysts."
            col6.metric("Wall St. Target", f"${target_avg:.2f}", f"{upside:+.1f}%", help=help_text)
        else:
            col6.metric("Wall St. Target", "N/A", help="No analyst price targets available")

        # Market Benchmarks & Investment Calculator - Compact Right Column
        # Create tight 2-column layout (no divider for same-level alignment)
        col_left_main, col_right_widgets = st.columns([2, 1.2], gap="small")
        
        with col_right_widgets:
            st.markdown("### 📊 Benchmarks")
            
            sp500_hist = get_historical_price("SPY", years)
            if not sp500_hist.empty and len(sp500_hist) > 1:
                sp500_start = sp500_hist['price'].iloc[0]
                sp500_end = sp500_hist['price'].iloc[-1]
                if sp500_start > 0:
                    sp500_growth = ((sp500_end - sp500_start) / sp500_start) * 100
                    period_label = f"{years}Y" if years > 1 else "1Y"
                    st.metric(f"S&P 500 ({period_label})", f"{sp500_growth:+.1f}%",
                             help=f"S&P 500 growth over the past {years} year(s)")
                else:
                    st.metric(f"S&P 500 ({years}Y)", "N/A")
            else:
                st.metric(f"S&P 500 ({years}Y)", "N/A")
            
            stock_hist = get_historical_price(ticker, years)
            if not stock_hist.empty and len(stock_hist) > 1:
                stock_start = stock_hist['price'].iloc[0]
                stock_end = stock_hist['price'].iloc[-1]
                if stock_start > 0:
                    stock_growth = ((stock_end - stock_start) / stock_start) * 100
                    period_label = f"{years}Y" if years > 1 else "1Y"
                    st.metric(f"{ticker} ({period_label})", f"{stock_growth:+.1f}%",
                             help=f"{ticker} growth over the past {years} year(s)")
                else:
                    st.metric(f"{ticker} ({years}Y)", "N/A")
            else:
                st.metric(f"{ticker} ({years}Y)", "N/A")
            st.markdown("**🏦 Treasury Rates**")
            st.caption("Safest investment. Zero risk = guaranteed returns.")
            
            # Fetch treasury rates from FMP (v4 endpoint - treasury data only available in v4)
            treasury_url = f"https://financialmodelingprep.com/api/v4/treasury?apikey={FMP_API_KEY}"
            try:
                treasury_response = requests.get(treasury_url, timeout=5)
                if treasury_response.status_code == 200:
                    treasury_data = treasury_response.json()
                    if treasury_data:
                        latest = treasury_data[0] if isinstance(treasury_data, list) else treasury_data
                        
                        col_t1, col_t2 = st.columns(2)
                        with col_t1:
                            if 'month3' in latest:
                                st.metric("3-Month", f"{latest['month3']:.2f}%")
                            if 'year2' in latest:
                                st.metric("2-Year", f"{latest['year2']:.2f}%")
                        with col_t2:
                            if 'year5' in latest:
                                st.metric("5-Year", f"{latest['year5']:.2f}%")
                            if 'year10' in latest:
                                st.metric("10-Year", f"{latest['year10']:.2f}%")
                        
                        st.caption(f"💡 Earn {latest.get('year10', 4):.2f}% risk-free with treasuries!")
            except:
                # Fallback if API fails
                st.metric("10-Year Treasury", "~4.25%")
                st.caption("Risk-free baseline return")
            
            st.markdown("---")
            st.caption("📚 *Learn about key metrics in [Finance 101](#)*")
            
        with col_left_main:
            # Stock Price Chart with Timeframe Toggles
            st.markdown(f"### {company_name} Stock Price")
            
            # Timeframe toggles
            timeframe_options = ["1D", "5D", "1M", "6M", "YTD", "1Y", "5Y"]
            selected_timeframe = st.radio(
                "Select timeframe:",
                timeframe_options,
                index=timeframe_options.index("1Y") if years == 1 else (timeframe_options.index("5Y") if years >= 5 else 4),
                horizontal=True,
                key="price_timeframe"
            )
            
            # Calculate days based on timeframe
            timeframe_days = {
                "1D": 3,  # Show last 3 days for daily data
                "5D": 7,
                "1M": 30,
                "6M": 180,
                "YTD": (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
                "1Y": 365,
                "5Y": 365 * 5
            }
            days_to_show = timeframe_days.get(selected_timeframe, 365)
            
            # Fetch price history (use max of selected timeframe or sidebar years)
            fetch_years = max(days_to_show / 365, years)
            price_history_full = get_historical_price(ticker, int(fetch_years) + 1)
            
            if not price_history_full.empty:
                # Filter to selected timeframe
                cutoff_date = datetime.now() - timedelta(days=days_to_show)
                price_history = price_history_full[price_history_full['date'] >= cutoff_date].copy()
                
                if len(price_history) < 2:
                    price_history = price_history_full.tail(3)  # Fallback to last 3 points
                
                # S&P 500 overlay toggle
                show_sp500 = st.checkbox("📊 Compare to S&P 500 (% Growth)", key="show_sp500_overlay")
                
                fig_price = go.Figure()
                
                if show_sp500 and len(price_history) > 1:
                    # Fetch SPY data for same period
                    spy_history_full = get_historical_price("SPY", int(fetch_years) + 1)
                    spy_history = spy_history_full[spy_history_full['date'] >= cutoff_date].copy()
                    
                    # Merge on date to get common dates
                    price_col = 'close' if 'close' in price_history.columns else 'price'
                    spy_col = 'close' if 'close' in spy_history.columns else 'price'
                    
                    merged = pd.merge(
                        price_history[['date', price_col]].rename(columns={price_col: 'stock_price'}),
                        spy_history[['date', spy_col]].rename(columns={spy_col: 'spy_price'}),
                        on='date',
                        how='inner'
                    ).sort_values('date')
                    
                    if len(merged) > 1:
                        # Normalize to % growth from start
                        stock_start = merged['stock_price'].iloc[0]
                        spy_start = merged['spy_price'].iloc[0]
                        
                        merged['stock_growth'] = ((merged['stock_price'] / stock_start) - 1) * 100
                        merged['spy_growth'] = ((merged['spy_price'] / spy_start) - 1) * 100
                        
                        # Add stock trace
                        fig_price.add_trace(go.Scatter(
                            x=merged['date'],
                            y=merged['stock_growth'],
                            mode='lines',
                            name=f'{ticker}',
                            line=dict(color='#9D4EDD', width=2),
                            hovertemplate='%{x}<br>' + ticker + ': %{y:.1f}%<extra></extra>'
                        ))
                        
                        # Add SPY trace
                        fig_price.add_trace(go.Scatter(
                            x=merged['date'],
                            y=merged['spy_growth'],
                            mode='lines',
                            name='S&P 500',
                            line=dict(color='#00C853', width=2, dash='dash'),
                            hovertemplate='%{x}<br>S&P 500: %{y:.1f}%<extra></extra>'
                        ))
                        
                        # Calculate Y-axis range with 5% padding
                        all_values = list(merged['stock_growth']) + list(merged['spy_growth'])
                        y_min = min(all_values)
                        y_max = max(all_values)
                        y_range = y_max - y_min if y_max != y_min else 1
                        
                        fig_price.update_layout(
                            title=f"{ticker} vs S&P 500 - Relative Performance",
                            xaxis_title="Date",
                            yaxis_title="% Growth",
                            yaxis=dict(
                                range=[y_min - y_range * 0.05, y_max + y_range * 0.05],
                                ticksuffix='%'
                            ),
                            height=350,
                            margin=dict(l=0, r=0, t=40, b=0),
                            hovermode='x unified',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                else:
                    # Regular price chart
                    price_col = 'close' if 'close' in price_history.columns else 'price'
                    
                    fig_price.add_trace(go.Scatter(
                        x=price_history['date'],
                        y=price_history[price_col],
                        mode='lines',
                        name='Price',
                        line=dict(color='#9D4EDD', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(157, 78, 221, 0.2)',
                        hovertemplate='%{x}<br>Price: $%{y:.2f}<extra></extra>'
                    ))
                    
                    # Calculate Y-axis range with 5% padding (not starting from 0)
                    y_min = price_history[price_col].min()
                    y_max = price_history[price_col].max()
                    y_range = y_max - y_min if y_max != y_min else y_max * 0.1
                    
                    fig_price.update_layout(
                        title=f"{ticker} Price History ({selected_timeframe})",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        yaxis=dict(range=[y_min - y_range * 0.05, y_max + y_range * 0.05]),
                        height=350,
                        margin=dict(l=0, r=0, t=40, b=0),
                        hovermode='x unified'
                    )
                
                st.plotly_chart(fig_price, use_container_width=True)

            # --------- Fact-based chart callouts (deterministic) ---------
            try:
                tech_facts = compute_technical_facts(price_history)
                st.session_state['pro_tech_facts'] = tech_facts
                callouts = render_chart_callouts(tech_facts)
                if callouts:
                    st.markdown("#### 📌 Chart Callouts (fact-based)")
                    for b in callouts:
                        st.write(f"- {b}")
            except Exception:
                # fail-soft: never crash Pro tab if a callout calc fails
                pass

            
            st.markdown("---")
            st.markdown("### 💰 Investment Calculator")
            st.caption("Compare your investment performance: Stock vs S&P 500 side-by-side")
            
            col_calc1, col_calc2 = st.columns(2)
            with col_calc1:
                invest_initial = st.number_input("💵 Lump Sum ($)", min_value=1, value=100, step=50, key="calc_lump")
            with col_calc2:
                invest_dca = st.number_input("📅 Bi-Weekly DCA ($)", min_value=0, value=100, step=25, key="calc_dca")
            
            calc_years = years
            price_hist = get_historical_price(ticker, calc_years)
            sp_data = get_historical_price("SPY", calc_years)
            
            if not price_hist.empty and len(price_hist) > 1:
                start_price = price_hist['price'].iloc[0]
                end_price = price_hist['price'].iloc[-1]
                
                if start_price > 0:
                    # Stock calculations
                    stock_lump = (invest_initial / start_price) * end_price
                    stock_lump_ret = ((stock_lump - invest_initial) / invest_initial) * 100
                    
                    weeks = calc_years * 52
                    payments = weeks // 2
                    avg_price = price_hist['price'].mean()
                    total_inv = invest_initial + (invest_dca * payments)
                    stock_shares = (invest_initial / start_price) + (invest_dca * payments / avg_price)
                    stock_dca = stock_shares * end_price
                    stock_dca_ret = ((stock_dca - total_inv) / total_inv) * 100 if total_inv > 0 else 0
                    
                    # S&P 500 calculations
                    sp_lump = sp_lump_ret = sp_dca_val = sp_dca_ret = 0
                    if not sp_data.empty and len(sp_data) > 1:
                        sp_start = sp_data['price'].iloc[0]
                        sp_end = sp_data['price'].iloc[-1]
                        if sp_start > 0:
                            sp_lump = (invest_initial / sp_start) * sp_end
                            sp_lump_ret = ((sp_lump - invest_initial) / invest_initial) * 100
                            sp_avg = sp_data['price'].mean()
                            sp_shares = (invest_initial / sp_start) + (invest_dca * payments / sp_avg)
                            sp_dca_val = sp_shares * sp_end
                            sp_dca_ret = ((sp_dca_val - total_inv) / total_inv) * 100 if total_inv > 0 else 0
                    
                    # Side-by-side comparison layout
                    col_stock, col_sp500 = st.columns(2)
                    
                    with col_stock:
                        st.markdown(f"#### {ticker} Performance")
                        st.metric("Lump Sum Value", f"${stock_lump:,.2f}", f"{stock_lump_ret:+.1f}%")
                        st.caption(f"${invest_initial} invested at start")
                        st.metric("DCA Value", f"${stock_dca:,.2f}", f"{stock_dca_ret:+.1f}%")
                        st.caption(f"${total_inv:,.2f} total invested")
                    
                    with col_sp500:
                        st.markdown("#### S&P 500 Benchmark")
                        st.metric("Lump Sum Value", f"${sp_lump:,.2f}", f"{sp_lump_ret:+.1f}%")
                        st.caption(f"${invest_initial} invested at start")
                        st.metric("DCA Value", f"${sp_dca_val:,.2f}", f"{sp_dca_ret:+.1f}%")
                        st.caption(f"${total_inv:,.2f} total invested")
                    
                    # Winner summary
                    st.markdown("---")
                    if stock_lump > sp_lump and stock_dca > sp_dca_val:
                        st.success(f"**Winner: {ticker}** outperformed S&P 500 in both strategies!")
                    elif sp_lump > stock_lump and sp_dca_val > stock_dca:
                        st.info(f"**Winner: S&P 500** outperformed {ticker} in both strategies")
                    else:
                        if stock_lump > sp_lump:
                            st.success(f"Lump Sum: {ticker} won by ${stock_lump - sp_lump:,.2f}")
                        else:
                            st.info(f"Lump Sum: S&P 500 won by ${sp_lump - stock_lump:,.2f}")
                        if stock_dca > sp_dca_val:
                            st.success(f"DCA: {ticker} won by ${stock_dca - sp_dca_val:,.2f}")
                        else:
                            st.info(f"DCA: S&P 500 won by ${sp_dca_val - stock_dca:,.2f}")

            
            st.markdown("---")
            
            # Coffee Comparison Calculator
            render_coffee_calculator(ticker, company_name)
            
            st.markdown("---")
            
            # Link to Financial Ratios tab
            st.info("📈 **Want to see detailed ratio analysis?** Check out the **Financial Ratios** tab in the sidebar for historical trends, S&P 500 comparisons, and more!")
            
            st.markdown("---")
            
        price_target_summary = get_price_target_summary(ticker)
        if price_target_summary:
            target_high = price_target_summary.get('targetHigh', 0)
            target_low = price_target_summary.get('targetLow', 0)
            target_avg = price_target_summary.get('targetMean', 0) or price_target_summary.get('targetMedian', 0)
            num_analysts = price_target_summary.get('numberOfAnalysts', 0)
            
            if target_avg and target_avg > 0:
                upside = ((target_avg - price) / price) * 100
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Avg Target", f"${target_avg:.2f}", f"{upside:+.1f}% upside",
                           help="Average analyst price target for next 12 months")
                if target_high > 0:
                    col2.metric("High Target", f"${target_high:.2f}",
                               help="Most bullish analyst price target")
                if target_low > 0:
                    col3.metric("Low Target", f"${target_low:.2f}",
                               help="Most bearish analyst price target")
                
                if num_analysts > 0:
                    st.caption(f"Based on {num_analysts} analysts")
        
    
    if view == "🌟 The Big Picture":
        
        income_df = get_income_statement(ticker, period, years*4 if period == 'quarter' else years)
        cash_df = get_cash_flow(ticker, period, years*4 if period == 'quarter' else years)
        balance_df = get_balance_sheet(ticker, period, years*4 if period == 'quarter' else years)
        
        # Stock chart is already shown above - removed duplicate here
        
        st.markdown(f"### 💵 {company_name} - Cash Flow Statement")
        show_why_it_matters('fcfAfterSBC')
        show_why_these_metrics("financial_statements")
        
        if not cash_df.empty:
            if 'stockBasedCompensation' in cash_df.columns and 'freeCashFlow' in cash_df.columns:
                cash_df['fcfAfterSBC'] = cash_df['freeCashFlow'] - abs(cash_df['stockBasedCompensation'])
            
            available_metrics = get_available_metrics(cash_df)
            
            if available_metrics:
                st.markdown("**📊 Select up to 3 metrics:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    metric1_display = st.selectbox(
                        "Metric 1:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'FCF After Stock Compensation'), 0),
                        key="cf_metric1"
                    )
                    metric1 = next(col for display, col in available_metrics if display == metric1_display)
                
                with col2:
                    metric2_display = st.selectbox(
                        "Metric 2:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Free Cash Flow'), min(1, len(available_metrics)-1)),
                        key="cf_metric2"
                    )
                    metric2 = next(col for display, col in available_metrics if display == metric2_display)
                
                with col3:
                    metric3_display = st.selectbox(
                        "Metric 3:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Operating Cash Flow'), min(2, len(available_metrics)-1)),
                        key="cf_metric3"
                    )
                    metric3 = next(col for display, col in available_metrics if display == metric3_display)
                
                metrics_to_plot = [metric1, metric2, metric3]
                
                # Show what these metrics mean
                with st.expander("📚 What do these metrics mean?", expanded=False):
                    for metric_display in [metric1_display, metric2_display, metric3_display]:
                        metric_key = metric_display.lower().replace(" ", "").replace("_", "")
                        explanation = get_metric_explanation(metric_key)
                        if explanation:
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* {explanation["simple"]}  
                💡 *Why it matters:* {explanation["why"]}""")
                            st.markdown("---")
                
                metric_names = [metric1_display, metric2_display, metric3_display]
                metric_names = [metric1_display, metric2_display, metric3_display]
                
                # Prepare data for chart
                plot_df = cash_df[["date"] + metrics_to_plot].copy()
                
                # Create chart with y-axis padding and growth rates
                fig, growth_rates = create_financial_chart_with_growth(
                    plot_df,
                    metrics_to_plot,
                    f"{company_name} - Cash Flow",
                    "Period",
                    "Amount ($)"
                )
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display growth rates
                    if growth_rates:
                        period_label = period_type.lower()
                        growth_text = f"**Growth over {years} {period_label} periods:**\n\n"
                        for idx, (metric_col, growth_rate) in enumerate(growth_rates.items()):
                            metric_name = metric_names[metrics_to_plot.index(metric_col)]
                            emoji = "🚀" if growth_rate > 10 else "📈" if growth_rate > 0 else "📉"
                            growth_text += f"{emoji} **{metric_name}:** {growth_rate:+.1f}%\n\n"
                        
                        st.markdown(f'<div class="growth-note">{growth_text}</div>', unsafe_allow_html=True)
                
                cols = st.columns(len(metrics_to_plot))
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    cols[i].metric(f"Latest {name}", format_number(cash_df[metric].iloc[-1]))
        else:
            st.warning("⚠️ Cash flow data not available")
        
        st.markdown("---")
        
        st.markdown(f"### 💰 {company_name} - Income Statement")
        show_why_it_matters('revenue')
        
        if not income_df.empty:
            available_metrics = get_available_metrics(income_df)
            
            if available_metrics:
                st.markdown("**📊 Select up to 3 metrics:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    metric1_display = st.selectbox(
                        "Metric 1:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Revenue'), 0),
                        key="income_metric1"
                    )
                    metric1 = next(col for display, col in available_metrics if display == metric1_display)
                
                with col2:
                    metric2_display = st.selectbox(
                        "Metric 2:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Operating Income'), min(1, len(available_metrics)-1)),
                        key="income_metric2"
                    )
                    metric2 = next(col for display, col in available_metrics if display == metric2_display)
                
                with col3:
                    metric3_display = st.selectbox(
                        "Metric 3:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Net Income'), min(2, len(available_metrics)-1)),
                        key="income_metric3"
                    )
                    metric3 = next(col for display, col in available_metrics if display == metric3_display)
                
                metrics_to_plot = [metric1, metric2, metric3]
                
                # Show what these metrics mean
                with st.expander("📚 What do these metrics mean?", expanded=False):
                    for metric_display in [metric1_display, metric2_display, metric3_display]:
                        metric_key = metric_display.lower().replace(" ", "").replace("_", "")
                        explanation = get_metric_explanation(metric_key)
                        if explanation:
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* {explanation["simple"]}  
                💡 *Why it matters:* {explanation["why"]}""")
                            st.markdown("---")
                
                metric_names = [metric1_display, metric2_display, metric3_display]
                metric_names = [metric1_display, metric2_display, metric3_display]
                
                plot_df = income_df[["date"] + metrics_to_plot].copy()
                
                fig, growth_rates = create_financial_chart_with_growth(
                    plot_df,
                    metrics_to_plot,
                    f"{company_name} - Income Statement",
                    "Period",
                    "Amount ($)"
                )
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    if growth_rates:
                        period_label = period_type.lower()
                        growth_text = f"**Growth over {years} {period_label} periods:**\n\n"
                        for idx, (metric_col, growth_rate) in enumerate(growth_rates.items()):
                            metric_name = metric_names[metrics_to_plot.index(metric_col)]
                            emoji = "🚀" if growth_rate > 10 else "📈" if growth_rate > 0 else "📉"
                            growth_text += f"{emoji} **{metric_name}:** {growth_rate:+.1f}%\n\n"
                        
                        st.markdown(f'<div class="growth-note">{growth_text}</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                cols = [col1, col2, col3]
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    cols[i].metric(f"Latest {name}", format_number(income_df[metric].iloc[-1]))
        else:
            st.warning("⚠️ Income statement not available")
        
        st.markdown("---")
        
        st.markdown(f"### 🏦 {company_name} - Balance Sheet")
        
        if not balance_df.empty:
            available_metrics = get_available_metrics(balance_df)
            
            if available_metrics:
                st.markdown("**📊 Select up to 3 metrics:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    metric1_display = st.selectbox(
                        "Metric 1:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Total Assets'), 0),
                        key="balance_metric1"
                    )
                    metric1 = next(col for display, col in available_metrics if display == metric1_display)
                
                with col2:
                    metric2_display = st.selectbox(
                        "Metric 2:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Total Liabilities'), min(1, len(available_metrics)-1)),
                        key="balance_metric2"
                    )
                    metric2 = next(col for display, col in available_metrics if display == metric2_display)
                
                with col3:
                    metric3_display = st.selectbox(
                        "Metric 3:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Shareholders Equity'), min(2, len(available_metrics)-1)),
                        key="balance_metric3"
                    )
                    metric3 = next(col for display, col in available_metrics if display == metric3_display)
                
                metrics_to_plot = [metric1, metric2, metric3]
                
                # Show what these metrics mean
                with st.expander("📚 What do these metrics mean?", expanded=False):
                    for metric_display in [metric1_display, metric2_display, metric3_display]:
                        metric_key = metric_display.lower().replace(" ", "").replace("_", "")
                        explanation = get_metric_explanation(metric_key)
                        if explanation:
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* {explanation["simple"]}  
                💡 *Why it matters:* {explanation["why"]}""")
                            st.markdown("---")
                
                metric_names = [metric1_display, metric2_display, metric3_display]
                metric_names = [metric1_display, metric2_display, metric3_display]
                
                plot_df = balance_df[["date"] + metrics_to_plot].copy()
                
                fig, growth_rates = create_financial_chart_with_growth(
                    plot_df,
                    metrics_to_plot,
                    f"{company_name} - Balance Sheet",
                    "Period",
                    "Amount ($)"
                )
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    if growth_rates:
                        period_label = period_type.lower()
                        growth_text = f"**Growth over {years} {period_label} periods:**\n\n"
                        for idx, (metric_col, growth_rate) in enumerate(growth_rates.items()):
                            metric_name = metric_names[metrics_to_plot.index(metric_col)]
                            emoji = "🚀" if growth_rate > 10 else "📈" if growth_rate > 0 else "📉"
                            growth_text += f"{emoji} **{metric_name}:** {growth_rate:+.1f}%\n\n"
                        
                        st.markdown(f'<div class="growth-note">{growth_text}</div>', unsafe_allow_html=True)
                
                cols = st.columns(len(metrics_to_plot))
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    cols[i].metric(f"Latest {name}", format_number(balance_df[metric].iloc[-1]))
        else:
            st.warning("⚠️ Balance sheet not available")
    
    elif view == "💪 Financial Health":
        st.markdown("## 💪 Financial Health")
        st.info("💡 **What is this?** See how healthy this company is financially - its profit margins, debt levels, and how it compares to others.")
        
        health_tab1, health_tab2 = st.tabs(["📈 Financial Health", "🔀 Compare Stocks"])
        
        with health_tab1:
            st.markdown("### 📈 Financial Health")
            st.caption("See how the company's key ratios compare to the S&P 500 average")
            
            ratios_df_health = get_financial_ratios(ticker, period, years*4 if period == 'quarter' else years)
            
            if ratios_df_health is not None and not ratios_df_health.empty:
                ratio_options = [
                    ("Gross Margin", "grossProfitMargin"),
                    ("Operating Margin", "operatingProfitMargin"),
                    ("Net Margin", "netProfitMargin"),
                    ("Return on Equity", "returnOnEquity"),
                    ("Return on Assets", "returnOnAssets"),
                    ("Current Ratio", "currentRatio")
                ]
                
                available_ratios = [(name, col) for name, col in ratio_options if col in ratios_df_health.columns]
                
                if available_ratios:
                    selected_ratio = st.selectbox(
                        "Select a ratio to analyze:",
                        options=[name for name, _ in available_ratios],
                        key="health_ratio_select"
                    )
                    
                    ratio_col = next(col for name, col in available_ratios if name == selected_ratio)
                    
                    fig = create_ratio_trend_chart(
                        ratios_df_health,
                        selected_ratio,
                        ratio_col,
                        f"{company_name} - {selected_ratio} Trend",
                        sector
                    )
                    
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander(f"💡 What is {selected_ratio}?"):
                        if selected_ratio in RATIO_EXPLANATIONS:
                            exp = RATIO_EXPLANATIONS[selected_ratio]
                            st.markdown(f"**What it measures:** {exp.get('what', 'N/A')}")
                            st.markdown(f"**What's good:** {exp.get('good', 'N/A')}")
                    
                    # Checkpoint Quiz (G) - P/E understanding
                    st.markdown("---")
                    render_checkpoint_quiz(
                        quiz_id="pe_ratio",
                        question="What does a high P/E ratio typically indicate?",
                        options=[
                            "The stock is cheap",
                            "Investors expect high future growth",
                            "The company has low debt",
                            "The company pays high dividends"
                        ],
                        correct_idx=1,
                        explanation="A high P/E ratio usually means investors are willing to pay more per dollar of earnings because they expect the company to grow faster in the future. However, it could also mean the stock is overvalued."
                    )
                else:
                    st.warning("No ratio data available for this company")
            else:
                st.warning("Financial ratios not available")
        
        with health_tab2:
            st.markdown("### 🔀 Compare 2 Stocks")
        st.info("💡 Compare metrics side-by-side with sector averages and explanations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stock1 = st.text_input("Stock 1:", value=ticker, key="compare_stock1")
        
        with col2:
            stock2 = st.text_input("Stock 2:", placeholder="e.g., MSFT", key="compare_stock2")
        
        if stock1 and stock2:
            quote1 = get_quote(stock1)
            quote2 = get_quote(stock2)
            profile1 = get_profile(stock1)
            profile2 = get_profile(stock2)
            ratios_ttm1 = get_ratios_ttm(stock1)
            ratios_ttm2 = get_ratios_ttm(stock2)
            cash1 = get_cash_flow(stock1, 'annual', 1)
            cash2 = get_cash_flow(stock2, 'annual', 1)
            income1 = get_income_statement(stock1, 'annual', 1)
            income2 = get_income_statement(stock2, 'annual', 1)
            balance1 = get_balance_sheet(stock1, 'annual', 1)
            balance2 = get_balance_sheet(stock2, 'annual', 1)
            
            if quote1 and quote2:
                sector1 = profile1.get('sector', 'Unknown') if profile1 else 'Unknown'
                sector2 = profile2.get('sector', 'Unknown') if profile2 else 'Unknown'
                
                st.markdown("### 📊 Side-by-Side Comparison")
                
                pe1 = get_pe_ratio(stock1, quote1, ratios_ttm1, income1)
                ps1 = get_ps_ratio(stock1, ratios_ttm1)
                fcf1 = calculate_fcf_per_share(stock1, cash1, quote1)
                de1 = calculate_debt_to_equity(balance1)
                qr1 = calculate_quick_ratio(balance1)
                beta1 = quote1.get('beta', 0)
                
                pe2 = get_pe_ratio(stock2, quote2, ratios_ttm2, income2)
                ps2 = get_ps_ratio(stock2, ratios_ttm2)
                fcf2 = calculate_fcf_per_share(stock2, cash2, quote2)
                de2 = calculate_debt_to_equity(balance2)
                qr2 = calculate_quick_ratio(balance2)
                beta2 = quote2.get('beta', 0)
                
                sector1_pe = get_industry_benchmark(sector1, 'pe')
                sector2_pe = get_industry_benchmark(sector2, 'pe')
                sector1_de = get_industry_benchmark(sector1, 'debt_to_equity')
                sector2_de = get_industry_benchmark(sector2, 'debt_to_equity')
                sector1_qr = get_industry_benchmark(sector1, 'quick_ratio')
                sector2_qr = get_industry_benchmark(sector2, 'quick_ratio')
                
                comparison_data = {
                    "Metric": ["Sector", "Price", "Market Cap", "P/E (TTM)", "P/S", "FCF/Share", "Debt/Equity", "Quick Ratio", "Beta", "Change (Today)"],
                    stock1: [
                        sector1,
                        f"${quote1.get('price', 0):.2f}",
                        format_number(quote1.get('marketCap', 0)),
                        f"{pe1:.2f}" if pe1 > 0 else "N/A",
                        f"{ps1:.2f}" if ps1 > 0 else "N/A",
                        f"${fcf1:.2f}" if fcf1 > 0 else "N/A",
                        f"{de1:.2f}" if de1 > 0 else "N/A",
                        f"{qr1:.2f}" if qr1 > 0 else "N/A",
                        f"{beta1:.2f}" if beta1 > 0 else "N/A",
                        f"{quote1.get('changesPercentage', 0):+.2f}%"
                    ],
                    stock2: [
                        sector2,
                        f"${quote2.get('price', 0):.2f}",
                        format_number(quote2.get('marketCap', 0)),
                        f"{pe2:.2f}" if pe2 > 0 else "N/A",
                        f"{ps2:.2f}" if ps2 > 0 else "N/A",
                        f"${fcf2:.2f}" if fcf2 > 0 else "N/A",
                        f"{de2:.2f}" if de2 > 0 else "N/A",
                        f"{qr2:.2f}" if qr2 > 0 else "N/A",
                        f"{beta2:.2f}" if beta2 > 0 else "N/A",
                        f"{quote2.get('changesPercentage', 0):+.2f}%"
                    ]
                }
                
                st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
                
                    
                st.markdown("### 📊 Detailed Metric Analysis")
                
                with st.expander("📈 P/E Ratio (Price-to-Earnings) - Click for explanation"):
                    pe_metric = METRIC_EXPLANATIONS.get('P/E Ratio', {})
                    st.markdown(f"**What it means:** {pe_metric.get('explanation', 'P/E ratio explanation coming soon.')}")
                    st.markdown(f"**Good range:** {pe_metric.get('good', 'Benchmark coming soon.')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{stock1}: {pe1:.2f if pe1 > 0 else 'N/A'}**")
                        if sector1_pe > 0:
                            st.markdown(f"<div class='sector-info'>📊 {sector1} avg: {sector1_pe:.1f}</div>", unsafe_allow_html=True)
                            if pe1 > 0:
                                if pe1 < sector1_pe * 0.8:
                                    st.success("✅ Trading below sector average (potentially undervalued)")
                            elif pe1 > sector1_pe * 1.2:
                                st.warning("⚠️ Trading above sector average (potentially overvalued)")
                            else:
                                st.info("➡️ In line with sector average")
                    
                    with col2:
                        st.markdown(f"**{stock2}: {pe2:.2f if pe2 > 0 else 'N/A'}**")
                        if sector2_pe > 0:
                            st.markdown(f"<div class='sector-info'>📊 {sector2} avg: {sector2_pe:.1f}</div>", unsafe_allow_html=True)
                            if pe2 > 0:
                                if pe2 < sector2_pe * 0.8:
                                    st.success("✅ Trading below sector average (potentially undervalued)")
                            elif pe2 > sector2_pe * 1.2:
                                st.warning("⚠️ Trading above sector average (potentially overvalued)")
                            else:
                                st.info("➡️ In line with sector average")
                
                with st.expander("💰 P/S Ratio (Price-to-Sales) - Click for explanation"):
                    ps_metric = METRIC_EXPLANATIONS.get('P/S Ratio', {})
                    st.markdown(f"**What it means:** {ps_metric.get('explanation', 'P/S ratio explanation coming soon.')}")
                    st.markdown(f"**Good range:** {ps_metric.get('good', 'Benchmark coming soon.')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{stock1}: {ps1:.2f if ps1 > 0 else 'N/A'}**")
                    with col2:
                        st.markdown(f"**{stock2}: {ps2:.2f if ps2 > 0 else 'N/A'}**")
                
                with st.expander("🏦 Debt-to-Equity Ratio - Click for explanation"):
                    de_metric = METRIC_EXPLANATIONS.get('Debt-to-Equity', {})
                    st.markdown(f"**What it means:** {de_metric.get('explanation', 'Debt-to-Equity explanation coming soon.')}")
                    st.markdown(f"**Good range:** {de_metric.get('good', 'Benchmark coming soon.')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{stock1}: {de1:.2f if de1 > 0 else 'N/A'}**")
                        if sector1_de > 0:
                            st.markdown(f"<div class='sector-info'>📊 {sector1} avg: {sector1_de:.2f}</div>", unsafe_allow_html=True)
                            if de1 > 0:
                                if de1 < sector1_de:
                                    st.success("✅ Lower debt than sector (less risky)")
                            elif de1 > sector1_de * 1.5:
                                st.error("🚨 Much higher debt than sector (risky)")
                            else:
                                st.warning("⚠️ Higher debt than sector average")
                    
                    with col2:
                        st.markdown(f"**{stock2}: {de2:.2f if de2 > 0 else 'N/A'}**")
                        if sector2_de > 0:
                            st.markdown(f"<div class='sector-info'>📊 {sector2} avg: {sector2_de:.2f}</div>", unsafe_allow_html=True)
                            if de2 > 0:
                                if de2 < sector2_de:
                                    st.success("✅ Lower debt than sector (less risky)")
                            elif de2 > sector2_de * 1.5:
                                st.error("🚨 Much higher debt than sector (risky)")
                            else:
                                st.warning("⚠️ Higher debt than sector average")
                
                with st.expander("💧 Quick Ratio (Liquidity) - Click for explanation"):
                    qr_metric = METRIC_EXPLANATIONS.get('Quick Ratio', {})
                    st.markdown(f"**What it means:** {qr_metric.get('explanation', 'Quick Ratio explanation coming soon.')}")
                    st.markdown(f"**Good range:** {qr_metric.get('good', 'Benchmark coming soon.')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{stock1}: {qr1:.2f if qr1 > 0 else 'N/A'}**")
                        if sector1_qr > 0:
                            st.markdown(f"<div class='sector-info'>📊 {sector1} avg: {sector1_qr:.2f}</div>", unsafe_allow_html=True)
                            if qr1 > 0:
                                if qr1 > sector1_qr:
                                    st.success("✅ Better liquidity than sector")
                            elif qr1 < 1.0:
                                st.error("🚨 Low liquidity (below 1.0)")
                            else:
                                st.warning("⚠️ Lower liquidity than sector average")
                    
                    with col2:
                        st.markdown(f"**{stock2}: {qr2:.2f if qr2 > 0 else 'N/A'}**")
                        if sector2_qr > 0:
                            st.markdown(f"<div class='sector-info'>📊 {sector2} avg: {sector2_qr:.2f}</div>", unsafe_allow_html=True)
                            if qr2 > 0:
                                if qr2 > sector2_qr:
                                    st.success("✅ Better liquidity than sector")
                            elif qr2 < 1.0:
                                st.error("🚨 Low liquidity (below 1.0)")
                            else:
                                st.warning("⚠️ Lower liquidity than sector average")
                
                with st.expander("💵 Free Cash Flow per Share - Click for explanation"):
                    fcf_metric = METRIC_EXPLANATIONS.get('FCF per Share', {})
                    st.markdown(f"**What it means:** {fcf_metric.get('explanation', 'FCF per Share explanation coming soon.')}")
                    st.markdown(f"**Good range:** {fcf_metric.get('good', 'Benchmark coming soon.')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{stock1}: ${fcf1:.2f if fcf1 > 0 else 'N/A'}**")
                        if fcf1 > 0:
                            st.success("✅ Generating positive cash flow")
                        else:
                            st.error("🚨 Burning cash (negative FCF)")
                    
                    with col2:
                        st.markdown(f"**{stock2}: ${fcf2:.2f if fcf2 > 0 else 'N/A'}**")
                        if fcf2 > 0:
                            st.success("✅ Generating positive cash flow")
                        else:
                            st.error("🚨 Burning cash (negative FCF)")
                
                with st.expander("📊 Beta (Volatility) - Click for explanation"):
                    beta_metric = METRIC_EXPLANATIONS.get('Beta', {})
                    st.markdown(f"**What it means:** {beta_metric.get('explanation', 'Beta explanation coming soon.')}")
                    st.markdown(f"**Good range:** {beta_metric.get('good', 'Benchmark coming soon.')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{stock1}: {beta1:.2f if beta1 > 0 else 'N/A'}**")
                        if beta1 > 1.5:
                            st.error("🚨 Very volatile (moves 50%+ more than market)")
                        elif beta1 > 1.0:
                            st.warning("⚠️ More volatile than market")
                        elif beta1 < 0.8:
                            st.success("✅ Defensive (less volatile than market)")
                        else:
                            st.info("➡️ Moves with market")
                    
                    with col2:
                        st.markdown(f"**{stock2}: {beta2:.2f if beta2 > 0 else 'N/A'}**")
                        if beta2 > 1.5:
                            st.error("🚨 Very volatile (moves 50%+ more than market)")
                        elif beta2 > 1.0:
                            st.warning("⚠️ More volatile than market")
                        elif beta2 < 0.8:
                            st.success("✅ Defensive (less volatile than market)")
                        else:
                            st.info("➡️ Moves with market")
                
                    
                st.markdown("### 🏆 Quick Verdict")
                
                scores = {stock1: 0, stock2: 0}
                
                if pe1 > 0 and pe2 > 0:
                    if pe1 < pe2:
                        scores[stock1] += 1
                        st.info(f"💰 **Valuation:** {stock1} is cheaper (lower P/E)")
                    else:
                        scores[stock2] += 1
                        st.info(f"💰 **Valuation:** {stock2} is cheaper (lower P/E)")
                
                if de1 > 0 and de2 > 0:
                    if de1 < de2:
                        scores[stock1] += 1
                        st.success(f"🏦 **Debt:** {stock1} has less debt")
                    else:
                        scores[stock2] += 1
                        st.success(f"🏦 **Debt:** {stock2} has less debt")
                
                if qr1 > 0 and qr2 > 0:
                    if qr1 > qr2:
                        scores[stock1] += 1
                        st.success(f"💧 **Liquidity:** {stock1} has better cash position")
                    else:
                        scores[stock2] += 1
                        st.success(f"💧 **Liquidity:** {stock2} has better cash position")
                
                if fcf1 > fcf2:
                    scores[stock1] += 1
                    st.success(f"💵 **Cash Flow:** {stock1} generates more FCF per share")
                else:
                    scores[stock2] += 1
                    st.success(f"💵 **Cash Flow:** {stock2} generates more FCF per share")
                
                winner = max(scores, key=scores.get)
                st.markdown(f"### 🎯 Winner: **{winner}** ({scores[winner]} out of 4 metrics)")
                
            else:
                st.warning("Could not fetch data for one or both stocks")
    
    elif view == "📈 Financial Health":
        st.markdown("## 📊 Financial Ratios Over Time")
        
        st.info("💡 **Why I track these ratios:** They reveal profitability (margins), efficiency (ROE/ROA/ROCE), and safety (liquidity/leverage). Together they show if a company makes money efficiently and can survive tough times.")
        
        
        col1, col2 = st.columns(2)
        with col1:
            ratio_period = st.radio("Period", ["Annual", "Quarterly"], key="ratio_period_sel")
        with col2:
            ratio_years = st.slider("Years of History", 1, 30, 5, key="ratio_years_sel")
        
        period_param = "annual" if ratio_period == "Annual" else "quarter"
        ratios_url = f"{BASE_URL}/ratios/{ticker}?period={period_param}&limit={ratio_years}&apikey={FMP_API_KEY}"
        
        try:
            response = requests.get(ratios_url, timeout=10)
            response.raise_for_status()
            ratios_data = response.json()
            ratios_df_new = pd.DataFrame(ratios_data)
            
            if not ratios_df_new.empty:
                st.markdown("### 📊 Current Ratios")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'grossProfitMargin' in ratios_df_new.columns:
                        latest = ratios_df_new['grossProfitMargin'].iloc[0] * 100
                        st.metric("Gross Margin", f"{latest:.1f}%",
                             help="Revenue minus cost of goods sold, divided by revenue")
                
                with col2:
                    if 'operatingProfitMargin' in ratios_df_new.columns:
                        latest = ratios_df_new['operatingProfitMargin'].iloc[0] * 100
                        st.metric("Operating Margin", f"{latest:.1f}%",
                             help="Operating income divided by revenue - shows efficiency")
                
                with col3:
                    if 'netProfitMargin' in ratios_df_new.columns:
                        latest = ratios_df_new['netProfitMargin'].iloc[0] * 100
                        st.metric("Net Margin", f"{latest:.1f}%",
                             help="Net income divided by revenue - bottom line profitability")
                
                    st.markdown("### 💰 Profitability Trends")
                
                st.info("**Profitability shows how much profit the company keeps from each dollar of sales. Higher margins = better pricing power and efficiency.**")
                
                
                for metric_name, metric_col in [('Gross Profit Margin', 'grossProfitMargin'), 
                                                 ('Operating Profit Margin', 'operatingProfitMargin'),
                                                 ('Net Profit Margin', 'netProfitMargin')]:
                    if metric_col in ratios_df_new.columns:
                        fig = create_ratio_trend_chart(ratios_df_new, metric_name, metric_col, 
                                                       f"{company_name} - {metric_name}", sector)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            explanation = get_metric_explanation(metric_col)
                            if explanation:
                                st.markdown(f"""<div class="metric-explain">
                            📊 **What it is:** {explanation["simple"]}  
                            💡 **Why it matters:** {explanation["why"]}
                            </div>""", unsafe_allow_html=True)
                            
                
                    st.markdown("### ⚡ Efficiency Trends")
                
                st.info("**Efficiency ratios show how well the company uses its money to generate profits. Higher returns = better management and stronger business.**")
                
                
                for metric_name, metric_col in [('Return on Equity (ROE)', 'returnOnEquity'),
                                                 ('Return on Assets (ROA)', 'returnOnAssets'),
                                                 ('Return on Capital Employed', 'returnOnCapitalEmployed')]:
                    if metric_col in ratios_df_new.columns:
                        fig = create_ratio_trend_chart(ratios_df_new, metric_name, metric_col,
                                                       f"{company_name} - {metric_name}", sector)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            explanation = get_metric_explanation(metric_col)
                            if explanation:
                                st.markdown(f"""<div class="metric-explain">
                            📊 **What it is:** {explanation["simple"]}  
                            💡 **Why it matters:** {explanation["why"]}
                            </div>""", unsafe_allow_html=True)
                            
                
                    st.markdown("### 🏦 Liquidity & Leverage Trends")
                
                st.info("**Liquidity = Can the company pay its bills? Leverage = How much debt does it have? Good liquidity + low debt = safer company.**")
                
                
                for metric_name, metric_col in [('Current Ratio', 'currentRatio'),
                                                 ('Quick Ratio', 'quickRatio'),
                                                 ('Debt to Equity', 'debtToEquity')]:
                    if metric_col in ratios_df_new.columns:
                        fig = create_ratio_trend_chart(ratios_df_new, metric_name, metric_col,
                                                       f"{company_name} - {metric_name}", sector)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            explanation = get_metric_explanation(metric_col)
                            if explanation:
                                st.markdown(f"""<div class="metric-explain">
                            📊 **What it is:** {explanation["simple"]}  
                            💡 **Why it matters:** {explanation["why"]}
                            </div>""", unsafe_allow_html=True)
                            
            else:
                st.warning("Ratio data not available for the selected period")
        except Exception as e:
            # Stop loss suggestion
            atr_estimate = (high_90d - low_90d) / 90 * 14  # Rough ATR estimate
            stop_loss = current - (2 * atr_estimate)
            
            st.info(f"💡 **Suggested Stop-Loss:** ${stop_loss:.2f} (2x ATR below current price)")
            st.caption("Stop-loss exits your position if price drops to protect capital. Adjust based on your risk tolerance.")
        
        st.markdown("---")
        st.markdown("### ⚠️ Technical Analysis Disclaimer")
        st.warning("""
**IMPORTANT:**
- Technical analysis is NOT guaranteed to predict future prices
- Past patterns do NOT ensure future results
- Always use stop-losses to limit downside
- Combine with fundamental analysis for best results
- Never invest more than you can afford to lose
- This is educational - not financial advice
        """)

    elif view == "💰 Price & Future Value":
        st.markdown("## 💰 DCF Valuation")
        st.caption("⚠️ Educational model only. Not a valuation recommendation.")
        st.info("Simplified DCF model - adjust assumptions")
        
        col1, col2 = st.columns(2)
        with col1:
            growth_rate = st.slider("Growth Rate (%/year)", 0, 50, 15)
            terminal_growth = st.slider("Terminal Growth (%)", 0, 10, 3)
        
        with col2:
            discount_rate = st.slider("Discount Rate (%)", 5, 20, 10)
            years_forecast = st.slider("Forecast Years", 5, 15, 10)
        
        if not cash_df.empty and 'freeCashFlow' in cash_df.columns:
            latest_fcf = cash_df['freeCashFlow'].iloc[-1]
            
            if latest_fcf > 0:
                pv_fcf = 0
                for year in range(1, years_forecast + 1):
                    fcf = latest_fcf * ((1 + growth_rate/100) ** year)
                    pv = fcf / ((1 + discount_rate/100) ** year)
                    pv_fcf += pv
                
                terminal_value = (latest_fcf * ((1 + growth_rate/100) ** years_forecast) * 
                            (1 + terminal_growth/100)) / ((discount_rate - terminal_growth)/100)
                pv_terminal = terminal_value / ((1 + discount_rate/100) ** years_forecast)
                
                enterprise_value = pv_fcf + pv_terminal
                
                if quote:
                    shares_float_data = get_shares_float(ticker)
                    shares = get_shares_outstanding(ticker, quote, shares_float_data)
                    
                    if shares > 0:
                        fair_value = enterprise_value / shares
                        current_price = quote.get('price', 0)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("DCF Fair Value", f"${fair_value:.2f}")
                        col2.metric("Current Price", f"${current_price:.2f}")
                        
                        if current_price > 0:
                            upside = ((fair_value - current_price) / current_price) * 100
                            col3.metric("Upside/Downside", f"{upside:+.1f}%")
                            
                            if upside > 20:
                                st.success("🚀 Potentially UNDERVALUED!")
                            elif upside < -20:
                                st.error("🚨 Potentially OVERVALUED!")
                            else:
                                st.info("✅ Fairly valued")
            else:
                st.warning("Negative FCF - DCF not applicable")
        else:
            st.warning("Cash flow data not available")
    
    elif view == "📰 Latest News":
        st.markdown(f"## 📰 Latest News for {company_name}")
        
        with st.spinner("Loading news..."):
            news = get_stock_specific_news(ticker, 12)
        
        if news:
            for article in news:
                title = article.get('title', 'No title')
                published_date = article.get('publishedDate', 'Unknown')
                text = article.get('text', '')
                url = article.get('url', '')
                site = article.get('site', 'Unknown')
                
                with st.expander(f"📰 {title}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"**Source:** {site}")
                    with col2:
                        st.caption(f"**Published:** {published_date[:10]}")
                    
                    if text:
                        st.write(text[:350] + "..." if len(text) > 350 else text)
                    
                    if url:
                        st.markdown(f"[Read full article →]({url})")
        else:
            st.info("No recent news for this ticker")
            st.caption("News available for major stocks like AAPL, TSLA, MSFT")
    
    elif view == "⚠️ Risk Report":
        st.markdown(f"## 🤖 AI Risk Profile for {company_name}")
        st.info("💡 **What is this?** Our AI analyzes news from the last 30 days to identify potential risks and opportunities. Written in simple language anyone can understand!")
        
        with st.spinner("🔍 Analyzing recent news with AI..."):
            risk_analysis = get_ai_risk_analysis(ticker, company_name)
        
        if risk_analysis:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🚩 Red Flags (Concerns)")
                st.caption("Things to watch out for")
                for i, flag in enumerate(risk_analysis.get('red_flags', []), 1):
                    st.error(f"**{i}.** {flag}")
            
            with col2:
                st.markdown("### 🟢 Green Flags (Positives)")
                st.caption("Good signs for the company")
                for i, flag in enumerate(risk_analysis.get('green_flags', []), 1):
                    st.success(f"**{i}.** {flag}")
            
            st.markdown("---")
            st.markdown("### 📊 Overall Assessment")
            overall = risk_analysis.get('overall', 'Analysis complete.')
            st.info(f"**Summary:** {overall}")
            
            with st.expander("💡 How to use this information"):
                st.markdown("""
**Remember:** This AI analysis is just ONE tool in your research toolkit!

- **Red flags don't mean "don't buy"** - they're things to research more
- **Green flags don't mean "definitely buy"** - always do more research
- **News can be wrong or misleading** - verify important claims
- **Past news doesn't predict the future** - markets change quickly

**Best Practice:** Use this alongside financial ratios, company fundamentals, and your own research!
                """)
            
            # Checkpoint Quiz (G) - Risk understanding
            st.markdown("---")
            render_checkpoint_quiz(
                quiz_id="risk_portfolio",
                question="Which portfolio is generally riskier?",
                options=[
                    "100% in one stock",
                    "50% stocks, 50% bonds",
                    "A diversified index fund (like SPY)",
                    "10 different stocks across sectors"
                ],
                correct_idx=0,
                explanation="Putting all your money in one stock is the riskiest because if that company fails, you lose everything. Diversification (spreading across many investments) reduces risk because not all investments will fail at once."
            )
        else:
            st.warning("⚠️ AI analysis is currently unavailable. This could be due to API limits or connectivity issues.")
            st.info("💡 **Tip:** Try again in a few minutes, or check the Financial Ratios and Key Metrics tabs for data-driven insights!")
    
    elif view == "📈 Investment Calculator":
        st.markdown(f"## 📈 Four Scenarios Investment Calculator")
        st.info(f"💡 **What is this?** Compare 4 different ways to invest $100 in {ticker} vs the S&P 500. See how 'Paycheck Investing' (adding $100 every 2 weeks) compares to investing all at once!")
        
        # DCA Narrative (F) - Time in market beats timing
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #00D9FF;">
            <p style="color: #00D9FF; font-weight: bold; margin: 0 0 5px 0;">💡 The Golden Rule of Investing</p>
            <p style="color: #E0E0E0; margin: 0; font-size: 14px;"><strong>Time in the market beats timing the market.</strong> Lump sum investing can look better historically, but it's rare to have a large sum available, emotionally hard to invest all at once, and not repeatable. DCA (Dollar Cost Averaging) lets you build wealth steadily with each paycheck.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Use the same years from sidebar (F - year-range correctness)
        st.caption(f"📅 Using {years}-year timeline from sidebar settings")
        
        with st.spinner(f"📊 Calculating {years}-year scenarios..."):
            results = calculate_four_scenarios(ticker, years, 100)
        
        if results and results.get("scenarios"):
            scenarios = results["scenarios"]
            
            st.markdown("### 📊 Results Comparison")
            
            cols = st.columns(4)
            scenario_keys = ["lump_stock", "lump_sp500", "dca_stock", "dca_sp500"]
            colors = ["🟣", "🟡", "🔵", "🟢"]
            
            for i, (key, color) in enumerate(zip(scenario_keys, colors)):
                if key in scenarios:
                    s = scenarios[key]
                    with cols[i]:
                        st.markdown(f"#### {color} {s['name']}")
                        st.metric("Final Value", f"${s['final_value']:,.0f}")
                        st.metric("Total Invested", f"${s['invested']:,.0f}")
                        return_pct = s.get('return_pct', 0)
                        st.metric("Return", f"{return_pct:+.1f}%")
            
            fig = create_four_scenarios_chart(results, ticker)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            with st.expander("💡 Understanding the Results", expanded=True):
                st.markdown(f"""
**What do these scenarios mean?**

- **Lump Sum {ticker}**: You invest $100 once at the start and let it grow
- **Lump Sum S&P 500**: Same $100 invested in the whole market (SPY ETF)
- **Paycheck {ticker}**: You invest $100 every 2 weeks (like from your paycheck!)
- **Paycheck S&P 500**: $100 every 2 weeks into the market

**Why Paycheck Investing often wins:**
- You invest MORE total money over time (${100 * years * 26:,} over {years} years!)
- You buy at different prices (some high, some low) - this is called "Dollar Cost Averaging"
- It's easier to save $100 per paycheck than $1,000+ all at once

**Important Notes:**
- Uses "Adjusted Close" prices (includes dividends!)
- Past performance doesn't guarantee future results
- This is for education only, not financial advice
                """)
            # Checkpoint Quiz (G) - DCA understanding
            st.markdown("---")
            render_checkpoint_quiz(
                quiz_id="dca_understanding",
                question="What does DCA (Dollar Cost Averaging) mean?",
                options=[
                    "Investing all your money at once",
                    "Investing fixed amounts at regular intervals",
                    "Only buying when prices are low",
                    "Selling when prices drop"
                ],
                correct_idx=1,
                explanation="DCA means investing a fixed amount regularly (like every paycheck), regardless of price. This reduces the impact of market timing and builds wealth steadily over time."
            )
        else:
            st.warning(f"⚠️ Could not calculate scenarios for {ticker}. Historical price data may not be available.")
            st.info("💡 **Tip:** Try a major stock like AAPL, MSFT, or GOOGL")


elif selected_page == "📊 Market Overview":
    
    st.header("📊 Market Overview")
    st.caption("*Top 100 stocks by market cap (ETFs excluded). Real-time data from FMP Stock Screener.*")
    
    # Define available sectors (FMP standard sectors)
    all_sectors = [
        "Technology", "Financial Services", "Healthcare", "Consumer Cyclical", 
        "Consumer Defensive", "Industrials", "Energy", "Materials", 
        "Real Estate", "Utilities", "Communication Services", "Other"
    ]
    
    # Sector filter (multiselect, empty by default = show all sectors)
    selected_sectors = st.multiselect(
        "Filter by sector (leave empty to show all):",
        options=all_sectors,
        default=[],  # Empty by default
        help="Select one or more sectors to filter. Leave empty to see top 100 companies across all sectors."
    )
    
    with st.spinner("Loading market data from Stock Screener API..."):
        rows = []
        market_cap_debug = []  # Track market caps for validation
        
        if selected_sectors and "Other" not in selected_sectors:
            # Load selected sectors - make one API call per sector
            st.info(f"Loading companies from {len(selected_sectors)} sector(s)...")
            
            for sector in selected_sectors:
                companies = get_companies_from_screener(sector=sector, limit=100)
                
                for company in companies:
                    ticker_sym = company.get('symbol')
                    if not ticker_sym:
                        continue
                    
                    # Get quote for additional metrics (P/E, P/S, FCF, analyst target)
                    quote = get_quote(ticker_sym)
                    
                    # Build row from screener data
                    row = {
                        "Ticker": ticker_sym,
                        "Company": company.get('companyName', ticker_sym),
                        "Sector": company.get('sector', 'Other'),
                        "Market Cap": company.get('marketCap', 0),
                        "Price": company.get('price', 0),
                        "P/E Ratio": None,
                        "P/S Ratio": None,
                        "FCF/Share": None,
                        "Dividend Yield %": None,
                        "Analyst Price Target": None,
                        "Upside/Downside %": None,
                        "AI Rating": "🔒 VIP",  # VIP placeholder
                        "Risk Score": "🔒 VIP"  # VIP placeholder
                    }
                    
                    # Track debug info for major companies
                    if ticker_sym in ['AAPL', 'MSFT', 'NVDA', 'BRK.B', 'GOOGL', 'BRK-B']:
                        market_cap_debug.append({
                            'ticker': ticker_sym,
                            'name': row["Company"],
                            'raw_market_cap': row["Market Cap"],
                            'formatted': format_number(row["Market Cap"]) if row["Market Cap"] > 0 else "N/A"
                        })
                    
                    # Get analyst price target and calculate upside/downside
                    if quote:
                        try:
                            target_data = get_price_target_consensus(ticker_sym)
                            if target_data:
                                target_price = target_data.get('targetConsensus') or target_data.get('targetMean')
                                if target_price and target_price > 0:
                                    row["Analyst Price Target"] = target_price
                                    
                                    current_price = row["Price"]
                                    if current_price and current_price > 0:
                                        upside_pct = ((target_price - current_price) / current_price) * 100
                                        row["Upside/Downside %"] = upside_pct
                        except:
                            pass  # Fail soft
                        
                        # Get additional metrics (P/E, P/S, FCF)
                        try:
                            ratios_ttm = get_ratios_ttm(ticker_sym)
                            cash_df = get_cash_flow(ticker_sym, 'annual', 1)
                            income_df = get_income_statement(ticker_sym, 'annual', 1)
                            
                            pe = get_pe_ratio(ticker_sym, quote, ratios_ttm, income_df)
                            ps = get_ps_ratio(ticker_sym, ratios_ttm)
                            fcf_per_share = calculate_fcf_per_share(ticker_sym, cash_df, quote)
                            
                            row["P/E Ratio"] = pe if pe and pe > 0 else None
                            row["P/S Ratio"] = ps if ps and ps > 0 else None
                            row["FCF/Share"] = fcf_per_share if fcf_per_share and fcf_per_share > 0 else None
                            
                            # Get dividend yield using dedicated function
                            div_yield = get_dividend_yield(ticker_sym, row["Price"])
                            if div_yield:
                                row["Dividend Yield %"] = div_yield
                        except:
                            pass  # Keep None values
                    
                    rows.append(row)
        else:
            # Default view: Load top 100 companies across all sectors
            st.info("Loading top 100 companies by market cap...")
            
            companies = get_companies_from_screener(sector=None, limit=100)
            
            # Debug: Show first few tickers
            if companies:
                debug_tickers = [c.get('symbol', 'N/A') for c in companies[:10]]
                st.caption(f"🔍 Debug: First tickers from API: {', '.join(debug_tickers)}")
            
            for company in companies:
                ticker_sym = company.get('symbol')
                if not ticker_sym:
                    continue
                
                # Get quote for additional metrics (P/E, P/S, FCF, analyst target)
                quote = get_quote(ticker_sym)
                
                # Build row from screener data
                row = {
                    "Ticker": ticker_sym,
                    "Company": company.get('companyName', ticker_sym),
                    "Sector": company.get('sector', 'Other'),
                    "Market Cap": company.get('marketCap', 0),
                    "Price": company.get('price', 0),
                    "P/E Ratio": None,
                    "P/S Ratio": None,
                    "FCF/Share": None,
                    "Dividend Yield %": None,
                    "Analyst Price Target": None,
                    "Upside/Downside %": None,
                    "AI Rating": "🔒 VIP",  # VIP placeholder
                    "Risk Score": "🔒 VIP"  # VIP placeholder
                }
                
                # Track debug info for major companies
                if ticker_sym in ['AAPL', 'MSFT', 'NVDA', 'BRK.B', 'GOOGL', 'BRK-B']:
                    market_cap_debug.append({
                        'ticker': ticker_sym,
                        'name': row["Company"],
                        'raw_market_cap': row["Market Cap"],
                        'formatted': format_number(row["Market Cap"]) if row["Market Cap"] > 0 else "N/A"
                    })
                
                # Get analyst price target and calculate upside/downside
                if quote:
                    try:
                        target_data = get_price_target_consensus(ticker_sym)
                        if target_data:
                            target_price = target_data.get('targetConsensus') or target_data.get('targetMean')
                            if target_price and target_price > 0:
                                row["Analyst Price Target"] = target_price
                                
                                current_price = row["Price"]
                                if current_price and current_price > 0:
                                    upside_pct = ((target_price - current_price) / current_price) * 100
                                    row["Upside/Downside %"] = upside_pct
                    except:
                        pass  # Fail soft
                    
                    # Get additional metrics (P/E, P/S, FCF)
                    try:
                        ratios_ttm = get_ratios_ttm(ticker_sym)
                        cash_df = get_cash_flow(ticker_sym, 'annual', 1)
                        income_df = get_income_statement(ticker_sym, 'annual', 1)
                        
                        pe = get_pe_ratio(ticker_sym, quote, ratios_ttm, income_df)
                        ps = get_ps_ratio(ticker_sym, ratios_ttm)
                        fcf_per_share = calculate_fcf_per_share(ticker_sym, cash_df, quote)
                        
                        row["P/E Ratio"] = pe if pe and pe > 0 else None
                        row["P/S Ratio"] = ps if ps and ps > 0 else None
                        row["FCF/Share"] = fcf_per_share if fcf_per_share and fcf_per_share > 0 else None
                        
                        # Get dividend yield using dedicated function
                        div_yield = get_dividend_yield(ticker_sym, row["Price"])
                        if div_yield:
                            row["Dividend Yield %"] = div_yield
                    except:
                        pass  # Keep None values
                
                rows.append(row)
        
        # Display market cap validation for known big companies
        if market_cap_debug:
            with st.expander("🔍 Market Cap Validation (Debug)"):
                st.caption("Verifying market cap accuracy for major companies:")
                for item in market_cap_debug:
                    st.write(f"**{item['ticker']}** ({item['name']}): Raw value = ${item['raw_market_cap']:,.0f} → Displays as {item['formatted']}")
                st.caption("✅ Values should match public consensus within normal vendor differences")

        
        if rows:
            df = pd.DataFrame(rows)
            
            # Sort by Market Cap descending (0 market caps go to bottom)
            df = df.sort_values('Market Cap', ascending=False).reset_index(drop=True)
            
            # Take top 100
            df = df.head(100)
            
            st.info(f"📊 Showing **{len(df)}** companies (sorted by market cap)")
            
            # Show KPI cards ONLY when exactly 1 sector selected
            if len(selected_sectors) == 1:
                st.markdown(f"### 📊 {selected_sectors[0]} Sector Metrics")
                col1, col2, col3 = st.columns(3)
                
                valid_pes = df[df['P/E Ratio'].notna()]['P/E Ratio']
                if len(valid_pes) > 0:
                    col1.metric("Avg P/E", f"{valid_pes.mean():.2f}",
                               help="Average Price-to-Earnings ratio for this sector")
                
                valid_ps = df[df['P/S Ratio'].notna()]['P/S Ratio']
                if len(valid_ps) > 0:
                    col2.metric("Avg P/S", f"{valid_ps.mean():.2f}",
                               help="Average Price-to-Sales ratio for this sector")
                
                valid_fcf = df[df['FCF/Share'].notna()]['FCF/Share']
                if len(valid_fcf) > 0:
                    col3.metric("Avg FCF/Share", f"${valid_fcf.mean():.2f}",
                               help="Average Free Cash Flow per share for this sector")
            
            # Format display dataframe
            display_df = df.copy()
            display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) and x > 0 else "—")
            display_df['Market Cap'] = display_df['Market Cap'].apply(lambda x: format_number(x) if x > 0 else "—")
            display_df['Analyst Price Target'] = display_df['Analyst Price Target'].apply(lambda x: f"${x:.2f}" if pd.notna(x) and x > 0 else "—")
            display_df['Upside/Downside %'] = display_df['Upside/Downside %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "—")
            display_df['P/E Ratio'] = display_df['P/E Ratio'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
            display_df['P/S Ratio'] = display_df['P/S Ratio'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
            display_df['FCF/Share'] = display_df['FCF/Share'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
            display_df['Dividend Yield %'] = display_df['Dividend Yield %'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) and x > 0 else "—")
            # VIP columns already have placeholders, no formatting needed
            
            # Display table with row selection enabled
            event = st.dataframe(display_df, use_container_width=True, height=600, 
                        on_select="rerun", selection_mode="single-row", key="market_overview_table")
            
            # Handle row click - navigate to Company Analysis
            if event and hasattr(event, 'selection') and event.selection.get('rows'):
                selected_row_idx = event.selection['rows'][0]
                if selected_row_idx < len(df):
                    selected_ticker = df.iloc[selected_row_idx]['Ticker']
                    st.session_state.selected_ticker = selected_ticker
                    st.session_state.selected_page = "📊 Company Analysis"
                    st.rerun()
            
            with st.expander("💡 What do these metrics mean?"):
                col1, col2 = st.columns(2)
                with col1:
                    pe_exp = METRIC_EXPLANATIONS.get("P/E Ratio", {}).get("explanation", "Price-to-Earnings ratio explanation coming soon.")
                    ps_exp = METRIC_EXPLANATIONS.get("P/S Ratio", {}).get("explanation", "Price-to-Sales ratio explanation coming soon.")
                    div_exp = "Annual dividends paid divided by stock price. A 3% yield means $3 per year for every $100 invested."
                    st.markdown(f"**P/E Ratio:** {pe_exp}")
                    st.markdown(f"**P/S Ratio:** {ps_exp}")
                    st.markdown(f"**Dividend Yield:** {div_exp}")
                with col2:
                    fcf_exp = METRIC_EXPLANATIONS.get("FCF per Share", {}).get("explanation", "Free Cash Flow per share explanation coming soon.")
                    mc_exp = METRIC_EXPLANATIONS.get("Market Cap", {}).get("explanation", "Total company value explanation coming soon.")
                    vip_exp = "🔒 AI Rating and Risk Score are VIP features. Upgrade for AI-powered insights!"
                    st.markdown(f"**FCF/Share:** {fcf_exp}")
                    st.markdown(f"**Market Cap:** {mc_exp}")
                    st.markdown(f"**VIP Features:** {vip_exp}")
            
            st.markdown("### 🔍 Analyze a Company")
            col1, col2 = st.columns([3, 1])
            with col1:
                selected = st.selectbox("Choose:", df['Ticker'].tolist(), 
                                   format_func=lambda x: f"{df[df['Ticker']==x]['Company'].values[0]} ({x})")
            with col2:
                if st.button("Analyze →", type="primary", use_container_width=True):
                    st.session_state.selected_ticker = selected
                    st.session_state.selected_page = "📊 Company Analysis"
                    st.rerun()
        else:
            st.error("❌ No rows created. This shouldn't happen!")
            st.write(f"Debug: tickers_to_load had {len(tickers_to_load)} items")
            st.write(f"Debug: selected_sectors = {selected_sectors}")
            st.write(f"Debug: rows list was empty after processing")




elif selected_page == "📈 Financial Health":
    
    st.header("📈 Financial Health - Historical Trends")
    st.markdown("**Compare company ratios to S&P 500 averages and historical benchmarks**")
    
    # Ticker search
    ratio_search = st.text_input(
        "Search by Company Name or Ticker:",
        st.session_state.selected_ticker,
        help="Enter a ticker symbol to analyze its financial ratios",
        key="ratio_search"
    )
    
    if ratio_search:
        ticker, company_name = smart_search_ticker(ratio_search)
        st.session_state.selected_ticker = ticker
    else:
        ticker = st.session_state.selected_ticker
        company_name = ticker
    
    # Sidebar settings
    with st.sidebar:
        st.markdown("### Ratio Settings")
        years = st.slider("Years of History:", 1, 10, 5, key="ratio_years")
        period = st.radio("Period:", ["Annual", "Quarterly"], key="ratio_period")
        period_type = 'annual' if period == "Annual" else 'quarter'
    
    # Fetch ratio data
    ratios_df = get_financial_ratios(ticker, period_type, years * 4 if period_type == 'quarter' else years)
    
    if not ratios_df.empty:
        st.subheader(f"{company_name} ({ticker}) - Ratio Analysis")
        
        # Fit Check Panel
        render_fit_check_panel(ticker)
        
        st.markdown("---")
        
        # S&P 500 benchmarks - PROFITABILITY FIRST, then valuation (user's "Profitability First" order)
        # Each tuple: (api_col, display_name, benchmark, comparison_type, short_desc, tooltip_definition, tooltip_example)
        all_ratios = [
            # 1. PROFITABILITY METRICS (Quality First)
            ("freeCashFlowPerShare", "FCF Per Share (Truth Meter)", 5.0, "higher_is_better", "The actual cash a company keeps after paying for everything.",
             "The actual cash a company keeps after paying for everything - salaries, rent, equipment, taxes.",
             "If a company reports $10B in profit but only has $2B in FCF, the 'profit' might be accounting tricks."),
            ("grossProfitMargin", "Gross Margin", 0.40, "higher_is_better", "Profit left after the direct cost of making the product.",
             "The percentage of revenue left after paying the direct costs of producing goods.",
             "If a company sells a shirt for $100 and it costs $40 to make, the Gross Margin is 60%."),
            ("operatingProfitMargin", "Operating Margin", 0.15, "higher_is_better", "Profit left after paying the bills (Rent, Salaries, Marketing).",
             "Profit left after paying operating expenses like rent, salaries, and marketing.",
             "A 20% operating margin means for every $100 in sales, $20 is left after paying all operating costs."),
            ("netProfitMargin", "Net Income Margin", 0.10, "higher_is_better", "The final 'Bottom Line' profit after everything, including taxes.",
             "The final profit percentage after ALL expenses including taxes and interest.",
             "A 15% net margin means the company keeps $15 for every $100 in revenue after everything is paid."),
            
            # 2. VALUATION METRICS
            ("priceEarningsRatio", "P/E Ratio", 22, "lower_is_better", "Price vs. Profit. How much you pay for $1 of earnings.",
             "A tool used to see if a stock is overvalued or undervalued by comparing its price to its profit.",
             "If a stock is $20 and the company earns $2 per share, the P/E is 10. You are paying $10 for every $1 of profit."),
            ("priceToSalesRatio", "P/S Ratio", 2.5, "lower_is_better", "Price vs. Sales. Best for checking companies that aren't profitable yet.",
             "Compares stock price to revenue - useful for companies that aren't profitable yet.",
             "A P/S of 5 means investors pay $5 for every $1 of sales the company generates."),
            ("priceToBookRatio", "P/B Ratio", 4.0, "lower_is_better", "Price vs. Assets. Compares the stock price to what the company actually owns.",
             "Compares the stock price to the company's book value (assets minus liabilities).",
             "A P/B of 2 means the stock trades at twice the value of what the company actually owns."),
            
            # 3. SAFETY METRICS
            ("debtEquityRatio", "Debt-to-Equity", 1.5, "lower_is_better", "How much debt a company uses to grow. Lower is safer.",
             "Measures how much a company is using debt to run its business compared to its own money.",
             "A ratio of 2.0 means the company has twice as much debt as it has 'own cash' (equity)."),
            ("returnOnEquity", "Return on Equity (ROE)", 0.15, "higher_is_better", "How efficiently a company uses investors' money.",
             "Shows how efficiently a company uses investors' money to generate profit.",
             "An ROE of 15% means the company generated $0.15 in profit for every $1 of shareholder money.")
        ]
        
        # ============= THE TRUTH METER (FCF vs Net Income) =============
        st.markdown("---")
        st.markdown("### 🔍 The Truth Meter: FCF vs Net Income")
        st.markdown("""
        <div class="growth-note">
        <strong>💡 Naman's Note:</strong> I call this the "Truth Meter." It shows if a company is making real cash or just playing with accounting numbers. 
        If Net Income is high but Free Cash Flow is low, someone is hiding something! Look for FCF that's close to or higher than Net Income.
        </div>
        """, unsafe_allow_html=True)
        
        # Fetch cash flow and income data for Truth Meter
        cash_flow_data = get_cash_flow(ticker, period_type, years * 4 if period_type == 'quarter' else years)
        income_data = get_income_statement(ticker, period_type, years * 4 if period_type == 'quarter' else years)
        
        if not cash_flow_data.empty and not income_data.empty:
            # Merge on date
            truth_df = pd.merge(
                cash_flow_data[['date', 'freeCashFlow']],
                income_data[['date', 'netIncome']],
                on='date',
                how='inner'
            )
            
            if not truth_df.empty and len(truth_df) > 1:
                truth_df['date'] = pd.to_datetime(truth_df['date'], errors='coerce')
                truth_df = truth_df.dropna().sort_values('date')
                
                # Create Truth Meter chart
                fig_truth = go.Figure()
                
                fig_truth.add_trace(go.Scatter(
                    x=truth_df['date'],
                    y=truth_df['netIncome'] / 1e9,
                    mode='lines+markers',
                    name='Net Income',
                    line=dict(color='#9D4EDD', width=2),
                    marker=dict(size=6)
                ))
                
                fig_truth.add_trace(go.Scatter(
                    x=truth_df['date'],
                    y=truth_df['freeCashFlow'] / 1e9,
                    mode='lines+markers',
                    name='Free Cash Flow',
                    line=dict(color='#00C853', width=2),
                    marker=dict(size=6)
                ))
                
                # Y-axis with 10% padding
                all_y = list(truth_df['netIncome'] / 1e9) + list(truth_df['freeCashFlow'] / 1e9)
                y_min, y_max = min(all_y), max(all_y)
                y_range = y_max - y_min if y_max != y_min else abs(y_max) * 0.1 or 1
                
                fig_truth.update_layout(
                    title="Net Income vs Free Cash Flow (Billions $)",
                    xaxis_title="Date",
                    yaxis_title="Amount (Billions $)",
                    yaxis=dict(range=[y_min - y_range * 0.1, y_max + y_range * 0.1]),
                    height=350,
                    margin=dict(l=0, r=0, t=40, b=0),
                    hovermode='x unified',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig_truth, use_container_width=True)
                
                # Truth Meter insight
                latest_ni = truth_df['netIncome'].iloc[-1]
                latest_fcf = truth_df['freeCashFlow'].iloc[-1]
                
                if latest_fcf > 0 and latest_ni > 0:
                    fcf_to_ni_ratio = latest_fcf / latest_ni
                    if fcf_to_ni_ratio >= 0.8:
                        st.success(f"**Truth Meter: PASS** - FCF is {fcf_to_ni_ratio:.0%} of Net Income. This company generates real cash!")
                    elif fcf_to_ni_ratio >= 0.5:
                        st.info(f"**Truth Meter: CAUTION** - FCF is {fcf_to_ni_ratio:.0%} of Net Income. Some earnings may not be cash.")
                    else:
                        st.warning(f"**Truth Meter: WARNING** - FCF is only {fcf_to_ni_ratio:.0%} of Net Income. Earnings quality may be poor.")
                elif latest_fcf < 0:
                    st.error(f"**Truth Meter: FAIL** - Negative FCF! This company is burning cash despite reported profits.")
                else:
                    st.info("**Truth Meter:** Unable to calculate - check the data above.")
        
        st.markdown("---")
        
        def create_ratio_chart_with_table(ratio_col, ratio_name, benchmark_val, comparison_type, ratios_data, description):
            """Create a ratio chart with historical benchmarking table"""
            if ratio_col not in ratios_data.columns:
                return False
            
            ratio_data = ratios_data[['date', ratio_col]].dropna()
            if len(ratio_data) == 0:
                return False
            
            # Convert date column to datetime for comparison
            ratio_data = ratio_data.copy()
            ratio_data['date'] = pd.to_datetime(ratio_data['date'], errors='coerce')
            ratio_data = ratio_data.dropna(subset=['date'])
            
            if len(ratio_data) == 0:
                return False
            
            col_chart, col_table = st.columns([2, 1])
            
            with col_chart:
                fig = go.Figure()
                
                # Add company ratio line
                fig.add_trace(go.Scatter(
                    x=ratio_data['date'],
                    y=ratio_data[ratio_col],
                    mode='lines+markers',
                    name=f'{ticker}',
                    line=dict(color='#9D4EDD', width=2),
                    marker=dict(size=6)
                ))
                
                # Add S&P 500 benchmark line
                fig.add_trace(go.Scatter(
                    x=ratio_data['date'],
                    y=[benchmark_val] * len(ratio_data),
                    mode='lines',
                    name='S&P 500 Avg',
                    line=dict(color='#00C853', width=2, dash='dash')
                ))
                
                # Y-axis with 5% padding
                all_y = list(ratio_data[ratio_col]) + [benchmark_val]
                y_min, y_max = min(all_y), max(all_y)
                y_range = y_max - y_min if y_max != y_min else abs(y_max) * 0.1 or 1
                
                fig.update_layout(
                    title=f"{ratio_name} Over Time",
                    xaxis_title="Date",
                    yaxis_title=ratio_name,
                    yaxis=dict(range=[y_min - y_range * 0.05, y_max + y_range * 0.05]),
                    height=300,
                    margin=dict(l=0, r=0, t=40, b=0),
                    hovermode='x unified',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Description
                st.caption(description)
                
                # Dynamic warning/insight box
                latest_val = ratio_data[ratio_col].iloc[-1] if len(ratio_data) > 0 else None
                if latest_val is not None:
                    if comparison_type == "lower_is_better":
                        if latest_val > benchmark_val * 1.1:
                            st.warning(f"{ticker}'s {ratio_name} ({latest_val:.2f}) is HIGHER than S&P 500 average ({benchmark_val:.2f})")
                        elif latest_val < benchmark_val * 0.9:
                            st.success(f"{ticker}'s {ratio_name} ({latest_val:.2f}) is LOWER than S&P 500 average ({benchmark_val:.2f})")
                        else:
                            st.info(f"{ticker}'s {ratio_name} ({latest_val:.2f}) is near S&P 500 average ({benchmark_val:.2f})")
                    else:
                        if latest_val > benchmark_val * 1.1:
                            st.success(f"{ticker}'s {ratio_name} ({latest_val:.2f}) is HIGHER than S&P 500 average ({benchmark_val:.2f})")
                        elif latest_val < benchmark_val * 0.9:
                            st.warning(f"{ticker}'s {ratio_name} ({latest_val:.2f}) is LOWER than S&P 500 average ({benchmark_val:.2f})")
                        else:
                            st.info(f"{ticker}'s {ratio_name} ({latest_val:.2f}) is near S&P 500 average ({benchmark_val:.2f})")
            
            with col_table:
                st.markdown("**Historical Benchmarks**")
                
                values = ratio_data[ratio_col].values
                latest_val = values[-1] if len(values) > 0 else None
                
                # Calculate stats
                period_avg = values.mean() if len(values) > 0 else None
                period_median = pd.Series(values).median() if len(values) > 0 else None
                
                # 5-year and 10-year averages (always show if data available)
                five_year_cutoff = datetime.now() - timedelta(days=5*365)
                ten_year_cutoff = datetime.now() - timedelta(days=10*365)
                
                five_year_data = ratio_data[ratio_data['date'] >= five_year_cutoff][ratio_col]
                ten_year_data = ratio_data[ratio_data['date'] >= ten_year_cutoff][ratio_col]
                
                five_year_avg = five_year_data.mean() if len(five_year_data) > 0 else None
                ten_year_avg = ten_year_data.mean() if len(ten_year_data) > 0 else None
                
                # Display metrics
                st.metric("Current", f"{latest_val:.2f}" if latest_val else "N/A")
                st.metric("5Y Average", f"{five_year_avg:.2f}" if five_year_avg else "N/A")
                st.metric("10Y Average", f"{ten_year_avg:.2f}" if ten_year_avg else "N/A")
                st.metric("Historical Median", f"{period_median:.2f}" if period_median else "N/A")
                st.metric("S&P 500 Avg", f"{benchmark_val:.2f}")
            
            return True
        
        # Display all ratio charts vertically (no sub-tabs) with hover tooltips
        charts_displayed = 0
        for ratio_tuple in all_ratios:
            ratio_col, ratio_name, benchmark_val, comparison_type, description, tooltip_def, tooltip_example = ratio_tuple
            if ratio_col in ratios_df.columns:
                # Render ratio name with hover tooltip (question mark icon)
                st.markdown(f"""
                <h3 style="color: #FFFFFF;">{ratio_name} 
                    <span class="ratio-tooltip">&#x3F;
                        <span class="tooltip-text">
                            <strong>Definition:</strong> {tooltip_def}<br><br>
                            <strong>Example:</strong> {tooltip_example}
                        </span>
                    </span>
                </h3>
                """, unsafe_allow_html=True)
                if create_ratio_chart_with_table(ratio_col, ratio_name, benchmark_val, comparison_type, ratios_df, description):
                    charts_displayed += 1
                st.markdown("---")
        
        if charts_displayed == 0:
            st.info("No ratio data available for this company")
        
        # Note: News has been moved to Market Intelligence page per page separation rules
        st.markdown("---")
        st.info("📰 **Looking for news?** Check out the **Market Intelligence** tab in the sidebar for AI-powered news analysis and market insights!")
        
        # Disclaimer at bottom of page
        st.markdown("---")
        st.caption("*Data based on historical filings; past performance does not guarantee future results. S&P 500 benchmark values are approximate averages.*")
    else:
        st.warning(f"No ratio data available for {ticker}. Try a different ticker.")
        st.info("**Tip:** Try major stocks like AAPL, MSFT, GOOGL, or AMZN")


# ============= MARKET INTELLIGENCE TAB =============
elif selected_page == "📰 Market Intelligence":
    
    st.header("Market Intelligence")
    st.markdown("**AI-Powered Market News & Analysis**")
    
    # ============= MARKET MOOD SPEEDOMETER =============
    st.markdown("---")
    st.markdown("### 📊 Market Mood Speedometer")
    
    # USE SINGLE SOURCE OF TRUTH for market sentiment - ensures sync everywhere
    sentiment_data = get_global_market_sentiment()
    sentiment_score = sentiment_data["score"]
    sentiment_label = sentiment_data["label"]
    sentiment_color = sentiment_data["color"]
    
    # Display the speedometer gauge
    col_gauge, col_labels = st.columns([2, 1])
    
    with col_gauge:
        gauge_fig = create_fear_greed_gauge(sentiment_score)
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    with col_labels:
        # Display the score prominently
        st.markdown(f'''
        <div style="padding: 20px; text-align: center;">
            <div style="font-size: 48px; font-weight: bold; color: {sentiment_color}; margin-bottom: 10px;">{sentiment_score}</div>
            <h3 style="color: {sentiment_color}; margin-bottom: 20px;">{sentiment_label}</h3>
            <div style="text-align: left; color: #FFFFFF; font-size: 14px; line-height: 2;">
                <p><span style="color: #FF4444;">0-25:</span> Extreme Fear (Market on Sale)</p>
                <p><span style="color: #FF8844;">25-45:</span> Fear</p>
                <p><span style="color: #FFFF44;">45-55:</span> Neutral (Steady)</p>
                <p><span style="color: #88FF44;">55-75:</span> Greed</p>
                <p><span style="color: #44FF44;">75-100:</span> Extreme Greed (Over-hyped)</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Ticker Search Box - accepts company names OR tickers
    st.markdown("### Search for Stock-Specific News")
    intel_input = st.text_input(
        "Enter a company name or ticker (leave empty for Magnificent 7 news):",
        "",
        placeholder="e.g., Apple, Tesla, GOOGL, Microsoft",
        key="intel_ticker_search"
    )
    
    # Resolve company name to ticker
    intel_ticker = resolve_company_to_ticker(intel_input) if intel_input.strip() else None
    
    # Show resolved ticker if different from input
    if intel_input.strip() and intel_ticker and intel_ticker.upper() != intel_input.strip().upper():
        st.caption(f"Searching for: **{intel_ticker}**")
    
    # Fit Check Panel (only if ticker selected)
    if intel_ticker:
        render_fit_check_panel(intel_ticker)
        st.markdown("---")
    
    # Function to get market news via Perplexity API
    def get_market_intelligence(ticker=None, is_mag7=False):
        """Fetch market news using Perplexity API"""
        if not PERPLEXITY_API_KEY:
            return None, "Perplexity API key not configured"
        
        try:
            if ticker and ticker.strip():
                query = f"Latest news, catalysts, and market analysis for {ticker.upper()} stock. Include recent price movements, analyst opinions, and any significant company developments. Format with clear sections and bullet points."
            elif is_mag7:
                query = """Latest news for the Magnificent 7 tech stocks (Apple, Microsoft, Google/Alphabet, Amazon, Nvidia, Meta, Tesla). 
                For each company, provide 1-2 recent headlines or developments.
                Format with clear sections:
                - Apple (AAPL)
                - Microsoft (MSFT)
                - Google (GOOGL)
                - Amazon (AMZN)
                - Nvidia (NVDA)
                - Meta (META)
                - Tesla (TSLA)
                Focus on recent price movements, earnings, product launches, and analyst opinions."""
            else:
                query = """Today's US stock market news summary. Format with clear sections:
                
                **Market Overview**
                - S&P 500 and major index performance
                
                **Interest Rates & Fed**
                - Latest Fed commentary and rate expectations
                
                **Key Earnings**
                - Notable earnings reports
                
                **Market Movers**
                - Top gaining and losing stocks
                
                Keep each section concise with bullet points."""
            
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {"role": "system", "content": "You are a financial news analyst. Provide concise, factual market updates with clear sections and bullet points. Make it easy to scan quickly."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 1500
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content, None
            else:
                return None, f"API error: {response.status_code}"
        except Exception as e:
            return None, str(e)
    
    # Fetch and display news - DEFAULT TO MAG 7 when no ticker
    with st.spinner("Fetching latest market intelligence..."):
        if intel_ticker:
            news_content, error = get_market_intelligence(intel_ticker)
        else:
            # Default to Magnificent 7 news
            news_content, error = get_market_intelligence(None, is_mag7=True)
    
    if news_content:
        if intel_ticker:
            st.markdown(f"### 📊 {intel_ticker.upper()} - Latest News & Analysis")
        else:
            st.markdown("### 🌟 Magnificent 7 - Latest News")
            st.caption("Apple, Microsoft, Google, Amazon, Nvidia, Meta, Tesla")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    border: 2px solid #00D9FF; border-radius: 15px; padding: 30px; margin: 20px 0;">
            <div style="color: #FFFFFF; font-size: 16px; line-height: 1.8;">
                {news_content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif error:
        st.warning(f"Could not fetch news: {error}")
        st.info("Try again later or check if the Perplexity API key is configured correctly.")
    
    # Also show FMP news headlines - NEVER EMPTY
    st.markdown("---")
    st.markdown("### 📰 Recent Headlines")
    
    fmp_news = []
    if intel_ticker:
        fmp_news = get_stock_specific_news(intel_ticker.upper(), 10)
    
    # If no ticker or no news found, get MAG 7 news
    if not fmp_news:
        # Fetch news for Magnificent 7 stocks
        for mag_ticker in MAG_7_TICKERS:
            try:
                ticker_news = get_stock_specific_news(mag_ticker, 2)
                if ticker_news:
                    fmp_news.extend(ticker_news)
            except:
                pass
        # Sort by date if available
        try:
            fmp_news = sorted(fmp_news, key=lambda x: x.get('publishedDate', ''), reverse=True)[:10]
        except:
            fmp_news = fmp_news[:10]
    
    # Fallback to general market news if still empty
    if not fmp_news:
        try:
            news_url = f"{BASE_URL}/news/stock-news-sentiments-rss-feed?apikey={FMP_API_KEY}"
            response = requests.get(news_url, timeout=10)
            fmp_news = response.json()[:10] if response.status_code == 200 else []
        except:
            fmp_news = []
    
    if fmp_news:
        for article in fmp_news[:10]:
            title = article.get('title', 'No title')
            published = article.get('publishedDate', '')[:10] if article.get('publishedDate') else ''
            symbol = article.get('symbol', '')
            url = article.get('url', '')
            symbol_tag = f"[{symbol}] " if symbol else ""
            if url:
                st.markdown(f"- {symbol_tag}[{title}]({url}) ({published})")
            else:
                st.markdown(f"- {symbol_tag}**{title}** ({published})")
    else:
        # All API sources failed - show honest error message (not fake headlines)
        st.warning("⚠️ Unable to load news headlines at this time. Please try again in a few moments.")
        st.caption("This can happen if the news APIs are temporarily unavailable or rate-limited.")
    
    st.markdown("---")
    st.caption("*News powered by Perplexity AI and Financial Modeling Prep. This is not financial advice.*")


elif selected_page == "👤 Naman's Portfolio":
    st.header("Naman's Portfolio")
    st.markdown("**My High-Conviction Investment Strategy**")
    
    # FREE TIER HOLDINGS ONLY - Hard data block for security (Pro/Ultimate data NOT fetched for free users)
    FREE_TIER_HOLDINGS = [
        {"ticker": "META", "name": "Meta Platforms", "sector": "Technology", "weight": 12.53},
        {"ticker": "NFLX", "name": "Netflix", "sector": "Communication Services", "weight": 11.93},
        {"ticker": "SPGI", "name": "S&P Global", "sector": "Financials", "weight": 10.53},
    ]
    
    # Initialize selected tier in session state (still needed for compatibility)
    if 'selected_tier' not in st.session_state:
        st.session_state.selected_tier = "Free"
    
    # Set access_tier for backward compatibility
    access_tier = st.session_state.selected_tier
    
    # ============= PORTFOLIO CONTENT STARTS HERE =============
    
    # ============= WAITLIST OVERLAY FOR PRO/ULTIMATE =============
    if access_tier != "Free":
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    border: 2px solid #9D4EDD; border-radius: 15px; padding: 40px; 
                    text-align: center; margin: 20px 0;">
            <h2 style="color: #9D4EDD; margin-bottom: 20px;">🔒 Naman's Pro/Ultimate Portfolio is Locked for Exclusivity</h2>
            <p style="color: #ffffff; font-size: 18px; margin-bottom: 30px;">
                Join the waitlist for the next <strong>50 spots</strong>. Get instant trade alerts and full portfolio access.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Email capture form
        st.markdown("### 📧 Join the Waitlist")
        col1, col2 = st.columns([3, 1])
        with col1:
            waitlist_email = st.text_input("Enter your email:", placeholder="your@email.com", key="waitlist_email")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Join Waitlist", key="join_waitlist"):
                if waitlist_email and "@" in waitlist_email:
                    st.success(f"You're on the list! We'll notify {waitlist_email} when spots open.")
                else:
                    st.error("Please enter a valid email address.")
        
        st.info("**Current waitlist:** 127 people ahead of you. Pro spots open monthly.")
        
    else:
        # FREE TIER - Show only the 3 free holdings (HARD DATA BLOCK - no Pro/Ultimate data fetched)
        st.markdown("---")
        st.markdown("### 📊 Portfolio Holdings (Free Preview)")
        st.info("**Free Preview:** Showing top 3 holdings only. Pro/Ultimate holdings are locked for exclusivity.")
        
        # Display FREE tier holdings only
        for i, holding in enumerate(FREE_TIER_HOLDINGS):
            logo_url = get_company_logo(holding["ticker"])
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                if logo_url:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <img src="{logo_url}" width="30" height="30" style="border-radius: 4px;">
                        <span><strong>{holding["ticker"]}</strong> - {holding["name"]}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"**{holding['ticker']}** - {holding['name']}")
            
            with col2:
                st.caption(holding["sector"])
            
            with col3:
                st.markdown(f"**{holding['weight']:.2f}%**")
            
            with col4:
                st.caption(f"#{i+1}")
        
        # Show locked indicator for remaining holdings (NO DATA - just count)
        st.markdown("---")
        st.markdown("### 🔒 10 More Holdings Locked")
        st.markdown("""
        <div style="background: #1a1a1a; border: 1px solid #333; border-radius: 10px; padding: 20px; text-align: center;">
            <p style="color: #888; font-size: 16px;">Holdings #4-13 are exclusive to Pro & Ultimate members.</p>
            <p style="color: #9D4EDD; font-size: 14px;">Join the waitlist above to unlock full portfolio access.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============= THE NAMAN ANALYSIS (Visible to ALL) =============
    st.markdown("---")
    st.markdown("## 📊 The Naman Analysis")
    st.markdown("*Detailed breakdowns of my top 3 conviction picks - visible to everyone.*")
    
    # Pick #1: META
    st.markdown("### 🏆 Pick #1: Meta Platforms (META) – The Digital Landlord")
    st.markdown("""
    **The Human Take:** People counted Meta out in 2022. They were wrong. Meta owns the most valuable "attention" on earth 
    with 3.5 billion users. They aren't just an app company; they are an AI powerhouse. They are spending $100B on AI 
    compute clusters—not because they're wasting money, but because they are building a wall so high that no competitor 
    can ever climb it.
    """)
    
    # META financials table
    meta_data = {
        "Year": ["2022", "2023", "2024"],
        "Revenue": ["$116.6B", "$134.9B", "$164.5B"],
        "Net Income": ["$23.2B", "$39.1B", "$62.4B"],
        "Op Margin %": ["24.8%", "34.7%", "42.2%"],
        "FCF": ["$50.5B", "$71.1B", "$91.3B"]
    }
    st.dataframe(pd.DataFrame(meta_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Pick #2: NFLX
    st.markdown("### 🏆 Pick #2: Netflix (NFLX) – The Predator of Streaming")
    st.markdown("""
    **The Human Take:** While everyone else is merging just to survive, Netflix is playing a different game. You hear rumors 
    about Paramount buying Warner Bros Discovery (WBD)—that's a "defensive" move because they are drowning in debt and losing 
    subs. Netflix doesn't need to merge. They have the scale moat. They are the only ones with 280M+ subs and $7B+ in free 
    cash flow to buy whatever content they want.
    
    **The Strategy:** Netflix is the "utility" of entertainment. By moving into live sports (NFL/WWE) and adding ads, they've 
    made their business recession-proof. If WBD or Paramount goes on sale, Netflix doesn't buy the company—they just wait for 
    them to fail and then buy their best shows for pennies on the dollar.
    """)
    
    # NFLX financials table
    nflx_data = {
        "Year": ["2022", "2023", "2024"],
        "Revenue": ["$31.6B", "$33.7B", "$39.0B"],
        "Net Income": ["$4.5B", "$5.4B", "$8.7B"],
        "Op Margin %": ["17.8%", "20.6%", "26.7%"],
        "FCF": ["$2.0B", "$7.3B", "$7.4B"]
    }
    st.dataframe(pd.DataFrame(nflx_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Pick #3: SPGI
    st.markdown("### 🏆 Pick #3: S&P Global (SPGI) – The Financial Toll Booth")
    st.markdown("""
    **The Human Take:** This is the ultimate "Monopoly" play. If a big company wants to borrow money, they must pay S&P Global 
    for a credit rating. It is a legal toll booth that sits in the middle of the global financial system. 80% of their revenue 
    is recurring—meaning they get paid every single year just for existing.
    """)
    
    # SPGI financials table
    spgi_data = {
        "Year": ["2021", "2022", "2023"],
        "Revenue": ["$8.3B", "$11.2B", "$12.5B"],
        "Net Income": ["$3.3B", "$3.5B", "$2.9B"],
        "FCF": ["$3.6B", "$2.6B", "$3.7B"],
        "Op Margin %": ["50.9%", "44.2%", "32.2%"]
    }
    st.dataframe(pd.DataFrame(spgi_data), use_container_width=True, hide_index=True)
    
    # ============= BECOME A VIP CTA =============
    st.markdown("---")
    st.markdown("### 👑 Want to see the full portfolio?")
    st.markdown("Unlock all holdings, advanced metrics, and exclusive investment insights with VIP access.")
    
    if st.button("👑 Become a VIP →", type="primary", use_container_width=True):
        st.session_state.selected_page = "👑 Become a VIP"
        st.rerun()
    
    st.markdown("---")
    st.caption("*Portfolio weightings as of December 2025. Subject to change based on market conditions. This is not financial advice.*")


elif selected_page == "👑 Become a VIP":
    st.header("👑 Become a VIP")
    st.markdown("**Unlock Premium Features & Exclusive Insights**")

    # --- Premium value proposition (detailed, skimmable) ---
    st.markdown(
        "Upgrade to get **AI-powered technical insights**, faster workflows, and tools that help you "
        "**understand what the chart is saying** — without pretending to give financial advice."
    )

    with st.expander("👀 Quick preview: what you’ll get", expanded=True):
        st.markdown(
            "**Pro includes:**\n"
            "- Candlestick chart + SMA50/SMA200/RSI/Volume toggles\n"
            "- **Technical Facts** summary (trend, momentum, volume, volatility, key levels)\n"
            "- **Chart Callouts** (rule-based highlights that always match the data)\n"
            "- **Pattern Detection (AI + Rules)** with confidence + key levels\n"
            "- “What traders generally do next” educational checklist\n"
            "\n"
            "**Ultimate adds:**\n"
            "- **Historical Similar Setups** (find past periods that looked like today)\n"
            "- Outcome stats (next 5D/20D returns, drawdowns, hit rate)\n"
            "- Alerts / watchlists + exportable reports (coming next)"
        )

    
    # Initialize selected tier in session state
    if 'selected_tier' not in st.session_state:
        st.session_state.selected_tier = "Free"
    
    # ============= TIERED PRICING COMPARISON TABLE =============
    st.markdown("### 🔐 Choose Your Access Tier")
    st.markdown("*All 3 tiers are always visible. Click to select your tier.*")
    
    # Create 3 columns for the tier cards
    col_free, col_pro, col_ultimate = st.columns(3)
    
    with col_free:
        # Highlight if selected
        border_color = "#00C853" if st.session_state.selected_tier == "Free" else "#333"
        shadow = "0 0 20px rgba(0,200,83,0.5)" if st.session_state.selected_tier == "Free" else "none"
        st.markdown(f"""
        <div style="background: #1a1a1a; border: 3px solid {border_color}; border-radius: 15px; 
                    padding: 20px; text-align: center; box-shadow: {shadow};">
            <h3 style="color: #00C853; margin-bottom: 10px;">Free</h3>
            <p style="color: #888; font-size: 24px; margin: 10px 0;"><strong>$0</strong>/mo</p>
            <p style="color: #FFFFFF; font-size: 14px;">Preview Access</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select Free", key="select_free_vip", use_container_width=True):
            st.session_state.selected_tier = "Free"
            st.rerun()
    
    with col_pro:
        border_color = "#9D4EDD" if st.session_state.selected_tier == "Pro" else "#333"
        shadow = "0 0 20px rgba(157,78,221,0.5)" if st.session_state.selected_tier == "Pro" else "none"
        st.markdown(f"""
        <div style="background: #1a1a1a; border: 3px solid {border_color}; border-radius: 15px; 
                    padding: 20px; text-align: center; box-shadow: {shadow};">
            <h3 style="color: #9D4EDD; margin-bottom: 10px;">Pro</h3>
            <p style="color: #888; font-size: 24px; margin: 10px 0;"><strong>$5</strong>/mo</p>
            <p style="color: #FFFFFF; font-size: 14px;">Full Portfolio Access</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select Pro", key="select_pro_vip", use_container_width=True):
            st.session_state.selected_tier = "Pro"
            st.rerun()
        
        # Deep-link demo button
        if st.button("🎯 Try Pro Demo →", key="try_pro_demo", use_container_width=True, type="secondary"):
            st.session_state.selected_page = "📊 Pro Checklist"
            if 'demo_ticker' not in st.session_state or not st.session_state.demo_ticker:
                st.session_state.demo_ticker = "NVDA"
            st.rerun()
    
    with col_ultimate:
        border_color = "#FFD700" if st.session_state.selected_tier == "Ultimate" else "#333"
        shadow = "0 0 20px rgba(255,215,0,0.5)" if st.session_state.selected_tier == "Ultimate" else "none"
        st.markdown(f"""
        <div style="background: #1a1a1a; border: 3px solid {border_color}; border-radius: 15px; 
                    padding: 20px; text-align: center; box-shadow: {shadow};">
            <h3 style="color: #FFD700; margin-bottom: 10px;">Ultimate</h3>
            <p style="color: #888; font-size: 24px; margin: 10px 0;"><strong>$10</strong>/mo</p>
            <p style="color: #FFFFFF; font-size: 14px;">VIP Access + Support</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select Ultimate", key="select_ultimate_vip", use_container_width=True):
            st.session_state.selected_tier = "Ultimate"
            st.rerun()
        
        # Deep-link demo button
        if st.button("🎯 Try Ultimate Demo →", key="try_ultimate_demo", use_container_width=True, type="secondary"):
            st.session_state.selected_page = "👑 Ultimate"
            if 'demo_ticker' not in st.session_state or not st.session_state.demo_ticker:
                st.session_state.demo_ticker = "NVDA"
            st.rerun()
    
    # Feature Comparison Table
    st.markdown("---")
    st.markdown("### What you get (by tier)")
    st.markdown("Pick a tier above, then skim what’s included below. **Everything is educational** — not financial advice.")

    col_free2, col_pro2, col_ult2 = st.columns(3)

    with col_free2:
        st.markdown(
            """
            <div style="background:#141414;border:1px solid #2a2a2a;border-radius:14px;padding:16px;min-height:420px;">
              <h3 style="color:#00C853;margin:0 0 6px 0;">Free</h3>
              <div style="color:#BBBBBB;font-size:14px;margin-bottom:10px;">Great for getting started</div>
              <ul style="color:#FFFFFF;line-height:1.6;">
                <li>Market Overview + Sector Explorer basics</li>
                <li>Company Analysis essentials</li>
                <li>Educational content + Risk Quiz</li>
              </ul>
              <div style="color:#888;font-size:12px;margin-top:12px;">
                Tip: Free stays useful — paid tiers add speed + deeper tooling.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_pro2:
        st.markdown(
            """
            <div style="background:#141414;border:2px solid #9D4EDD;border-radius:14px;padding:16px;min-height:420px;box-shadow:0 0 18px rgba(157,78,221,0.25);">
              <h3 style="color:#9D4EDD;margin:0 0 6px 0;">Pro</h3>
              <div style="color:#BBBBBB;font-size:14px;margin-bottom:10px;">For technical learners + faster decisions</div>
              <ul style="color:#FFFFFF;line-height:1.6;">
                <li><b>Pro Chart Lab</b>: candlesticks + SMA50/SMA200/RSI/Volume toggles</li>
                <li><b>Technical Facts</b>: trend regime, momentum, volume/volatility context</li>
                <li><b>Chart Callouts</b>: 3–5 grounded takeaways under every chart</li>
                <li><b>Pattern Detection (AI + Rules)</b>: label + confidence + key levels</li>
                <li><b>Next Steps Checklist</b>: “what traders generally do next” (educational)</li>
              </ul>
              <div style="color:#888;font-size:12px;margin-top:12px;">
                Designed to be <b>accurate per ticker</b> (AI is constrained to computed facts).
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_ult2:
        st.markdown(
            """
            <div style="background:#141414;border:2px solid #FFD700;border-radius:14px;padding:16px;min-height:420px;box-shadow:0 0 18px rgba(255,215,0,0.20);">
              <h3 style="color:#FFD700;margin:0 0 6px 0;">Ultimate</h3>
              <div style="color:#BBBBBB;font-size:14px;margin-bottom:10px;">For “show me the receipts” users</div>
              <ul style="color:#FFFFFF;line-height:1.6;">
                <li>Everything in <b>Pro</b></li>
                <li><b>Historical Similar Setups</b>: find past charts that looked like today</li>
                <li><b>Outcome stats</b>: typical next 5D/20D returns + drawdowns (educational)</li>
                <li><b>Backtest-style insights</b> (coming next)</li>
                <li><b>Alerts & watchlists</b> (coming next)</li>
                <li><b>Exportable reports</b> (coming next)</li>
              </ul>
              <div style="color:#888;font-size:12px;margin-top:12px;">
                Ultimate is where we add <b>history + outcomes</b>, not just interpretation.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")
    with st.expander("FAQ", expanded=False):
        st.markdown(
            "- **Is this financial advice?** No — educational only.\n"
            "- **Why AI at all?** We compute the facts first; AI is used to explain them in plain English.\n"
            "- **What’s the difference between Pro and Ultimate?** Ultimate adds historical analogs + outcome stats + alerts/exports."
        )

    
    st.markdown("---")
    
    # Set access_tier based on selected_tier
    access_tier = st.session_state.selected_tier
    
    # ============= WAITLIST OVERLAY FOR PRO/ULTIMATE =============
    if access_tier != "Free":
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    border: 2px solid #9D4EDD; border-radius: 15px; padding: 40px; 
                    text-align: center; margin: 20px 0;">
            <h2 style="color: #FFD700; margin-bottom: 20px;">🎉 Join the Waitlist</h2>
            <p style="color: #FFFFFF; font-size: 18px; margin-bottom: 30px;">
                Be among the first to access premium features when they launch!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            waitlist_email = st.text_input("Enter your email:", placeholder="your@email.com", key="waitlist_email_vip")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Join Waitlist", key="join_waitlist_vip"):
                if waitlist_email and "@" in waitlist_email:
                    st.success(f"You're on the list! We'll notify {waitlist_email} when spots open.")
                else:
                    st.error("Please enter a valid email address.")
        
        st.info("**Current waitlist:** 127 people ahead of you. Pro spots open monthly.")
    else:
        st.success("✅ You're currently on the Free tier. Enjoy exploring!")
    
    st.markdown("---")
    st.caption("*Pricing subject to change. No credit card required for waitlist. This is not financial advice.*")


elif selected_page == "📊 Pro Checklist":
    # ============= YELLOW PILL HEADER =============
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFD60A 0%, #FFA500 100%); 
                padding: 15px 25px; 
                border-radius: 15px; 
                text-align: center; 
                margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(255, 214, 10, 0.3);">
        <h2 style="margin: 0; color: #1a1a1a; font-size: 24px; font-weight: bold;">
            🟡 PRO — AI Chart Explain
        </h2>
        <p style="margin: 5px 0 0 0; color: rgba(26,26,26,0.8); font-size: 14px;">
            Pattern detection • AI analysis • 5-bullet insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("*Advanced technical analysis + fundamental screening*")
    
    # Disclaimer box (always visible)
    st.markdown("""
    <div style="background: rgba(255,165,0,0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #FFA500; margin-bottom: 20px;">
        <p style="margin: 0; color: #FFA500; font-size: 13px;">
            <strong>⚠️ Educational Only — Not Financial Advice</strong><br>
            This checklist helps you think in two lanes: (1) Business conviction and (2) Timing/momentum.<br>
            <em>Signals can conflict — that's normal.</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============= PRO USER CONTENT (NOW PUBLIC) =============
    # Note: Pro Checklist is now available to all users
    
    # Fix selectbox dropdown colors to match input styling
    st.markdown("""
    <style>
    /* STEP 1: Red dropdown theme - closed AND opened states */
    
    /* Closed state - RED like text input */
    [data-testid="stSelectbox"] > div > div {
        background-color: #FF4B4B !important;
        color: white !important;
    }
    
    /* Dropdown button/selector - RED */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #FF4B4B !important;
        color: white !important;
    }
    
    /* CRITICAL: Opened popover/menu - RED theme */
    div[data-baseweb="popover"] {
        background-color: #FF4B4B !important;
    }
    
    /* Listbox container - RED */
    div[data-baseweb="popover"] ul[role="listbox"] {
        background-color: #FF4B4B !important;
        border: none !important;
    }
    
    /* Individual options - RED background */
    div[data-baseweb="popover"] li[role="option"] {
        background-color: #FF4B4B !important;
        color: white !important;
        padding: 8px 12px !important;
    }
    
    /* Hover state - Darker red */
    div[data-baseweb="popover"] li[role="option"]:hover {
        background-color: #CC3333 !important;
        color: white !important;
    }
    
    /* Selected/active item - Deepest red */
    div[data-baseweb="popover"] li[role="option"][aria-selected="true"] {
        background-color: #AA2222 !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Menu items in general */
    [data-baseweb="menu"] {
        background-color: #FF4B4B !important;
    }
    
    [data-baseweb="menu"] li {
        background-color: #FF4B4B !important;
        color: white !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: #CC3333 !important;
    }
    
    [data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #AA2222 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Progress Bar for Investment Checklist
    if 'checklist_analyzed' not in st.session_state:
        st.session_state.checklist_analyzed = False
    
    # Use current_step/total_steps format for render_progress_bar
    checklist_current = 1 if st.session_state.checklist_analyzed else 0
    checklist_total = 1
    render_progress_bar(checklist_current, checklist_total, "Checklist Progress", disable_celebrations=True)
    
    # ============= INPUT ROW =============
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    # Use demo ticker if coming from VIP page
    default_ticker = st.session_state.get('demo_ticker', st.session_state.selected_ticker)
    
    with col1:
        ticker_check = st.text_input("Ticker or Company Name:", value=default_ticker, key="checklist_ticker")
    
    with col2:
        timeframe = st.selectbox("Timeframe", ["3M", "6M", "1Y", "2Y", "5Y"], index=2, key="checklist_timeframe")
    
    with col3:
        # Interval options based on timeframe
        if timeframe in ["3M", "6M"]:
            interval_options = ["1D"]
            default_interval = "1D"
        else:  # 1Y, 2Y, 5Y
            interval_options = ["1D", "1W"]
            default_interval = "1D"
        
        interval = st.selectbox("Interval", interval_options, index=0, key="checklist_interval")
    
    with col4:
        # ELI5 toggle
        simple_mode = st.toggle("Explain like I'm 5", value=False, key="eli5_toggle")
        analyze_button = st.button("Analyze", key="checklist_analyze", use_container_width=True)
    
    # Store simple_mode in session state for use across features
    st.session_state.simple_mode = simple_mode
    
    
    # ============= ANALYSIS SECTION =============
    if analyze_button or st.session_state.checklist_analyzed:
        st.session_state.checklist_analyzed = True
        
        # Resolve ticker
        resolved_ticker = resolve_company_to_ticker(ticker_check)
        
        if not resolved_ticker:
            st.error(f"❌ Could not find ticker: {ticker_check}")
            st.warning("Try using the exact ticker symbol (e.g., GOOGL not GOOG)")
            st.stop()
        
        ticker_check = resolved_ticker
        st.success(f"✅ Resolved to: {ticker_check}")
        
        # Get data
        quote = get_quote(ticker_check)
        
        if not quote:
            st.error(f"❌ Could not fetch data for {ticker_check}")
            st.warning("This might be due to:")
            st.write("- API rate limit")
            st.write("- Invalid ticker")
            st.write("- Network issue")
            st.stop()
        
        # Load price data early so we can show Technical Quick Guide
        timeframe_days = {
            "3M": 90,
            "6M": 180,
            "1Y": 365,
            "2Y": 730,
            "5Y": 1825
        }
        days = timeframe_days.get(timeframe, 365)
        years = days / 365.0
        price_history = get_historical_ohlc(ticker_check, years)
        
        if price_history.empty:
            st.error(f"❌ No price data available for {ticker_check}")
            st.warning("Try a different ticker or timeframe")
            st.stop()
        
        # ============= TECHNICAL QUICK GUIDE (BEFORE COMPANY NAME) =============
        st.markdown("---")
        render_technical_quick_guide(price_history, ticker_check)
        
        st.markdown("---")
        st.subheader(f"📊 {quote.get('name', ticker_check)} ({ticker_check})")
        
        # ============= CANDLESTICK CHART (Using Company Analysis proven logic) =============
        st.markdown("---")
        st.markdown("### 📈 Price Chart with Technical Indicators")
        
        # Overlay checkboxes
        col_check1, col_check2, col_check3, col_check4 = st.columns(4)
        with col_check1:
            show_sma50 = st.checkbox("SMA 50", value=True, key="show_sma50")
        with col_check2:
            show_sma200 = st.checkbox("SMA 200", value=True, key="show_sma200")
        with col_check3:
            show_rsi = st.checkbox("RSI", value=True, key="show_rsi")
        with col_check4:
            show_volume = st.checkbox("Volume", value=True, key="show_volume")
        
        # Price history already loaded earlier for Technical Quick Guide
        # Continue with chart rendering
        
        # Track what features are available for status line
        chart_features = []
        
        # Create chart (candlestick if we have OHLC, line chart if only close)
        has_ohlc = all(col in price_history.columns for col in ['open', 'high', 'low', 'close'])
        
        # Initialize num_rows (used for layout height calculation)
        num_rows = 1
        
        if has_ohlc:
            chart_features.append("OHLC")
            
            # Determine number of rows based on indicators
            num_rows = 1  # Price chart always present
            row_heights = []
            subplot_titles_list = [f'{ticker_check} Price']
            
            if show_rsi:
                num_rows += 1
                subplot_titles_list.append('RSI (14)')
            
            if show_volume and 'volume' in price_history.columns:
                num_rows += 1
                subplot_titles_list.append('Volume')
            
            # Calculate row heights
            if num_rows == 1:
                row_heights = [1.0]
            elif num_rows == 2:
                row_heights = [0.7, 0.3]
            else:  # 3 rows
                row_heights = [0.6, 0.2, 0.2]
            
            # Create candlestick chart with dynamic rows
            fig_price = make_subplots(
                rows=num_rows,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=row_heights,
                subplot_titles=tuple(subplot_titles_list)
            )
            
            # Add candlestick
            fig_price.add_trace(
                go.Candlestick(
                    x=price_history['date'],
                    open=price_history['open'],
                    high=price_history['high'],
                    low=price_history['low'],
                    close=price_history['close'],
                    name='Price',
                    increasing_line_color='#00FF00',  # GREEN for up days
                    decreasing_line_color='#FF4444'   # RED for down days
                ),
                row=1, col=1
            )
            
            # Add volume if available and requested
            if show_volume and 'volume' in price_history.columns:
                colors = ['#00FF00' if price_history['close'].iloc[i] >= price_history['open'].iloc[i] else '#FF4444' 
                          for i in range(len(price_history))]
                
                # Determine which row for volume (last row)
                volume_row = num_rows
                
                fig_price.add_trace(
                    go.Bar(
                        x=price_history['date'],
                        y=price_history['volume'],
                        name='Volume',
                        marker_color=colors,
                        opacity=0.5
                    ),
                    row=volume_row, col=1
                )
                chart_features.append("Volume")
            
        else:
            # Fallback to line chart (like Company Analysis does)
            chart_features.append("Line")
            
            fig_price = go.Figure()
            
            price_col = 'close' if 'close' in price_history.columns else 'price'
            
            fig_price.add_trace(go.Scatter(
                x=price_history['date'],
                y=price_history[price_col],
                mode='lines',
                name='Price',
                line=dict(color='#9D4EDD', width=2),
                fill='tozeroy',
                fillcolor='rgba(157, 78, 221, 0.2)',
                hovertemplate='%{x}<br>Price: $%{y:.2f}<extra></extra>'
            ))
        
        # Add SMAs (calculate manually from close prices)
        close_col = 'close' if 'close' in price_history.columns else 'price'
        
        if show_sma50 and len(price_history) >= 50:
            sma50 = price_history[close_col].rolling(window=50, min_periods=1).mean()
            sma_trace_50 = go.Scatter(
                x=price_history['date'],
                y=sma50,
                mode='lines',
                name='SMA 50',
                line=dict(color='#FFA500', width=2)
            )
            
            if has_ohlc:
                fig_price.add_trace(sma_trace_50, row=1, col=1)
            else:
                fig_price.add_trace(sma_trace_50)
            
            chart_features.append("SMA50")
        
        if show_sma200 and len(price_history) >= 200:
            sma200 = price_history[close_col].rolling(window=200, min_periods=1).mean()
            sma_trace_200 = go.Scatter(
                x=price_history['date'],
                y=sma200,
                mode='lines',
                name='SMA 200',
                line=dict(color='#9D4EDD', width=2)
            )
            
            if has_ohlc:
                fig_price.add_trace(sma_trace_200, row=1, col=1)
            else:
                fig_price.add_trace(sma_trace_200)
            
            chart_features.append("SMA200")
        
        # Add RSI (Relative Strength Index)
            if show_rsi and len(price_history) >= 14:
                # Calculate RSI
                close_col = 'close' if 'close' in price_history.columns else 'price'
                delta = price_history[close_col].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                # Determine RSI row number
                rsi_row = 2 if show_rsi else None
                if rsi_row and has_ohlc:
                    # Add RSI line
                    fig_price.add_trace(
                        go.Scatter(
                            x=price_history['date'],
                            y=rsi,
                            mode='lines',
                            name='RSI',
                            line=dict(color='#FFD700', width=2)  # Gold color
                        ),
                        row=rsi_row, col=1
                    )
                    
                    # Add overbought/oversold lines
                    fig_price.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=rsi_row, col=1)
                    fig_price.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=rsi_row, col=1)
                    
                    # Update RSI y-axis
                    fig_price.update_yaxes(title_text="RSI", range=[0, 100], row=rsi_row, col=1)
                    
                    chart_features.append("RSI")
            
            # Update layout (same as Company Analysis)
            fig_price.update_layout(
                title=f"{ticker_check} Price History ({timeframe})",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=500,  # Reduced from 700/600/500
                template='plotly_dark',
                margin=dict(l=0, r=0, t=40, b=0),
                hovermode='x unified',
                showlegend=True,
                xaxis_rangeslider_visible=False  # Hide by default, add custom range selector
            )
            
            # Add rangeslider to the BOTTOM row (where it will be visible)
            # No range selector buttons - user controls timeframe via dropdown
            if has_ohlc:
                fig_price.update_xaxes(
                    rangeslider=dict(
                        visible=True,
                        thickness=0.05,
                        bgcolor="rgba(150, 150, 150, 0.1)"
                    ),
                    row=num_rows, col=1  # Slider on bottom chart
                )
            else:
                # For line charts (no subplots), add to main axis
                fig_price.update_xaxes(
                    rangeslider=dict(
                        visible=True,
                        thickness=0.05,
                        bgcolor="rgba(150, 150, 150, 0.1)"
                    )
                )
            
            # Update axis labels based on number of rows
            if has_ohlc:
                fig_price.update_yaxes(title_text="Price ($)", row=1, col=1)
                if show_volume:
                    fig_price.update_yaxes(title_text="Volume", row=num_rows, col=1)
            
            # Display chart (same as Company Analysis)
            st.plotly_chart(fig_price, use_container_width=True)
            
            # ============= COMPACT STATUS LINE =============
            if has_ohlc:
                status_parts = [f"{feat} ✓" for feat in chart_features]
                st.success(f"✅ Chart ready: {' | '.join(status_parts)}")
            else:
                st.warning("⚠️ OHLC not available — showing line chart fallback.")
        
        # ============= CHART CALLOUTS (STEP 4) =============
        st.markdown("---")
        st.markdown("### 📌 Key Observations")
        
        # Compute technical facts if not already done
        tech_facts = compute_technical_facts(price_history)
        if 'pro_tech_facts' not in st.session_state:
            st.session_state.pro_tech_facts = tech_facts
        
        # Generate and display callouts
        callouts = render_chart_callouts(tech_facts)
        if callouts:
            for callout in callouts:
                st.markdown(f"- {callout}")
        else:
            st.caption("*Insufficient data for observations*")
        
        # ============= PATTERN DETECTION =============
        st.markdown("---")
        st.markdown("### 🔍 Pattern Detection (AI + Rules)")
        
        # Pattern detection button
        col_pattern1, col_pattern2 = st.columns([1, 3])
        with col_pattern1:
            detect_pattern_btn = st.button("🤖 Detect Pattern", key="detect_pattern_btn", use_container_width=True)
        
        with col_pattern2:
            st.caption("*AI analyzes chart patterns, momentum, and technical signals*")
        
        # Pattern detection logic
        if detect_pattern_btn or st.session_state.get('pattern_detected', False):
            st.session_state.pattern_detected = True
            
            with st.spinner("🔍 Analyzing chart pattern..."):
                # Calculate rule-based features
                features = calculate_pattern_features(price_history)
                
                if features:
                    # STEP 2: Technical Metrics with RED header
                    st.markdown("""
                    <div style="background-color: #FF4B4B; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        <h4 style="color: white; margin: 0;">📊 Technical Metrics</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("View Details", expanded=False):
                        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                        with col_f1:
                            st.metric("Current Price", f"${features['current_price']}")
                            st.caption(f"vs MA20: {features['price_vs_ma20']:+.1f}%")
                        with col_f2:
                            st.metric("RSI", f"{features['rsi']:.0f}")
                            st.caption(f"{features['rsi_zone'].capitalize()}")
                        with col_f3:
                            st.metric("20-Day Return", f"{features['last_20d_return']:+.1f}%")
                            st.caption(f"Trend: {features['trend_direction']}")
                        with col_f4:
                            st.metric("Volatility", features['vol_regime'].capitalize())
                            st.caption(f"20d: {features['vol_20d']:.1f}%")
                    
                    # Get AI pattern detection
                    simple_mode = st.session_state.get('simple_mode', False)
                    pattern_prompt = detect_chart_pattern(ticker_check, features, simple_mode)
                    
                    # Here you would call Claude API with pattern_prompt
                    # For now, we'll show a placeholder response based on rules
                    
                                        
                    # Rule-based pattern suggestion (fact-locked fallback)
                    tech_facts = st.session_state.get('pro_tech_facts') or compute_technical_facts(price_history)
                    pattern_label, confidence, reasons, watch_level, watch_note = detect_rule_based_pattern(
                        tech_facts,
                        simple_mode=simple_mode
                    )
# Display pattern result
                    st.markdown("#### 🎯 Pattern Analysis")
                    
                    # Pattern card with confidence color
                    confidence_color = {
                        'High': '#00FF00',
                        'Medium': '#FFA500', 
                        'Low': '#FF4444'
                    }
                    
                    st.markdown(f"""
                    <div style="background: rgba(50,50,50,0.5); padding: 20px; border-radius: 10px; border-left: 5px solid {confidence_color[confidence]};">
                        <h3 style="margin: 0; color: {confidence_color[confidence]};">🔍 {pattern_label}</h3>
                        <p style="margin: 5px 0; color: {confidence_color[confidence]}; font-size: 14px;">Confidence: {confidence}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**Why we think this:**")
                    for reason in reasons:
                        st.markdown(f"• {reason}")
                    
                    st.markdown(f"**🎯 Key Level to Watch:** {watch_note}")
                    
                    # Note about AI
                    if simple_mode:
                        st.info("💡 **Remember**: This is just one way to look at the chart. Always do your own research!")
                    else:
                        st.info("ℹ️ **Note**: Pattern detection combines rule-based signals with AI interpretation. Not financial advice.")
                    
                    # ============= STEP 6: WHAT TRADERS DO NEXT =============
                    st.markdown("---")
                    st.markdown("### ✅ What Traders Generally Do Next (Educational)")
                    st.caption("*Common approaches traders use when analyzing similar setups*")
                    
                    trader_actions = generate_trader_actions(tech_facts, pattern_label)
                    if trader_actions:
                        for action in trader_actions:
                            st.markdown(f"- {action}")
                    else:
                        st.caption("*Insufficient data for trader action suggestions*")
                    
                    st.caption("*📚 Educational only — not a recommendation. Always do your own research.*")
                    
                    # ============= STEP 7: AI-POWERED ANALYSIS BUTTONS =============
                    st.markdown("---")
                    st.markdown("### 🤖 AI-Powered Deep Dive (Fact-Locked)")
                    st.caption("*AI analyzes using ONLY the technical facts above — no hallucinations*")
                    
                    # Initialize session state for AI outputs
                    if 'pro_explain_ai' not in st.session_state:
                        st.session_state.pro_explain_ai = None
                    if 'pro_bull_bear_ai' not in st.session_state:
                        st.session_state.pro_bull_bear_ai = None
                    
                    # Check if Perplexity is available
                    perplexity_available = bool(os.environ.get('PERPLEXITY_API_KEY', ''))
                    
                    if not perplexity_available:
                        st.warning("⚠️ AI features require PERPLEXITY_API_KEY environment variable")
                    else:
                        col_ai1, col_ai2 = st.columns(2)
                        
                        with col_ai1:
                            explain_btn = st.button("🔍 Explain this chart (AI)", key="explain_chart_ai", use_container_width=True)
                        
                        with col_ai2:
                            bull_bear_btn = st.button("⚖️ Bull vs Bear case (AI)", key="bull_bear_ai", use_container_width=True)
                        
                        # ============= EXPLAIN CHART AI =============
                        if explain_btn:
                            # CLEAR the other AI output (toggle behavior)
                            st.session_state.pro_bull_bear_ai = None
                            
                            with st.spinner("🤖 AI analyzing chart facts..."):
                                # Build prompt
                                rule_based_dict = {
                                    "label": pattern_label,
                                    "confidence": confidence,
                                    "reasons": reasons,
                                    "watch_level": watch_level,
                                    "watch_note": watch_note
                                }
                                
                                simple_mode = st.session_state.get('simple_mode', False)
                                prompt = build_explain_chart_prompt(tech_facts, rule_based_dict, simple_mode)
                                
                                # Call Perplexity
                                ai_response = call_perplexity_json(prompt, max_tokens=2500, temperature=0.1)
                                
                                if ai_response:
                                    # Validate response
                                    is_valid, error_msg = validate_ai_response(ai_response, tech_facts, "explain")
                                    
                                    if is_valid:
                                        st.session_state.pro_explain_ai = ai_response
                                    else:
                                        st.error(f"⚠️ AI validation failed: {error_msg}")
                                        st.info("Showing rule-based analysis instead.")
                                        st.session_state.pro_explain_ai = None
                                else:
                                    st.error("⚠️ AI request failed. Try again or use rule-based analysis.")
                                    st.session_state.pro_explain_ai = None
                        
                        # ============= BULL VS BEAR AI =============
                        if bull_bear_btn:
                            # CLEAR the other AI output (toggle behavior)
                            st.session_state.pro_explain_ai = None
                            
                            with st.spinner("🤖 AI building bull/bear cases..."):
                                simple_mode = st.session_state.get('simple_mode', False)
                                prompt = build_bull_bear_prompt(tech_facts, simple_mode)
                                
                                # Call Perplexity
                                ai_response = call_perplexity_json(prompt, max_tokens=2000, temperature=0.1)
                                
                                if ai_response:
                                    # Validate response
                                    is_valid, error_msg = validate_ai_response(ai_response, tech_facts, "bull_bear")
                                    
                                    if is_valid:
                                        st.session_state.pro_bull_bear_ai = ai_response
                                    else:
                                        st.error(f"⚠️ AI validation failed: {error_msg}")
                                        st.info("Check the pattern analysis above for rule-based insights.")
                                        st.session_state.pro_bull_bear_ai = None
                                else:
                                    st.error("⚠️ AI request failed. Try again.")
                                    st.session_state.pro_bull_bear_ai = None
                        
                        # ============= DISPLAY EXPLAIN CHART AI OUTPUT =============
                        if st.session_state.pro_explain_ai:
                            st.markdown("---")
                            st.markdown("#### 🔍 AI Chart Explanation")
                            
                            output = st.session_state.pro_explain_ai
                            
                            # Summary
                            if "summary_one_liner" in output:
                                st.markdown(f"**{output['summary_one_liner']}**")
                                st.markdown("")
                            
                            # Trend
                            if "trend" in output and output["trend"]:
                                st.markdown("**📈 Trend Analysis:**")
                                for bullet in output["trend"]:
                                    clean_bullet = clean_citation_tags(bullet)
                                    st.markdown(f"- {clean_bullet}")
                                st.markdown("")
                            
                            # Momentum
                            if "momentum" in output and output["momentum"]:
                                st.markdown("**🚀 Momentum:**")
                                for bullet in output["momentum"]:
                                    clean_bullet = clean_citation_tags(bullet)
                                    st.markdown(f"- {clean_bullet}")
                                st.markdown("")
                            
                            # Key Levels
                            if "key_levels" in output:
                                st.markdown("**🎯 Key Levels:**")
                                levels = output["key_levels"]
                                
                                if "support" in levels and levels["support"].get("level"):
                                    sup_level = levels["support"]["level"]
                                    sup_dist = levels["support"].get("distance_pct", 0)
                                    st.markdown(f"- **Support:** ${sup_level:.2f} ({sup_dist:+.1f}% away)")
                                
                                if "resistance" in levels and levels["resistance"].get("level"):
                                    res_level = levels["resistance"]["level"]
                                    res_dist = levels["resistance"].get("distance_pct", 0)
                                    st.markdown(f"- **Resistance:** ${res_level:.2f} ({res_dist:+.1f}% away)")
                                
                                if "watch_level" in levels and levels["watch_level"].get("level"):
                                    watch_lvl = levels["watch_level"]["level"]
                                    watch_note = levels["watch_level"].get("note", "")
                                    st.markdown(f"- **Watch:** ${watch_lvl:.2f} — {watch_note}")
                                
                                st.markdown("")
                            
                            # Risk Notes
                            if "risk_notes" in output and output["risk_notes"]:
                                st.markdown("**⚠️ Risks to Watch:**")
                                for bullet in output["risk_notes"]:
                                    clean_bullet = clean_citation_tags(bullet)
                                    st.markdown(f"- {clean_bullet}")
                                st.markdown("")
                            
                            # What to Watch Next 5 Days
                            if "what_to_watch_next_5_days" in output and output["what_to_watch_next_5_days"]:
                                st.markdown("**👀 What to Watch (Next 5 Days):**")
                                for bullet in output["what_to_watch_next_5_days"]:
                                    clean_bullet = clean_citation_tags(bullet)
                                    st.markdown(f"- {clean_bullet}")
                            
                            st.info("✅ **Fact-locked AI**: All statements grounded in technical facts above")
                        
                        # ============= DISPLAY BULL VS BEAR AI OUTPUT =============
                        if st.session_state.pro_bull_bear_ai:
                            st.markdown("---")
                            st.markdown("####⚖️ Bull vs Bear Analysis (AI)")
                            
                            output = st.session_state.pro_bull_bear_ai
                            
                            # Bull Case
                            if "bull_case" in output and output["bull_case"]:
                                st.markdown("##### 🐂 Bull Case:")
                                for item in output["bull_case"]:
                                    # Handle both old format (dict with "point") and new format (string)
                                    if isinstance(item, dict):
                                        point = item.get("point", "")
                                    else:
                                        point = str(item)
                                    clean_point = clean_citation_tags(point)
                                    st.markdown(f"- {clean_point}")
                                st.markdown("")
                            
                            # Bear Case
                            if "bear_case" in output and output["bear_case"]:
                                st.markdown("##### 🐻 Bear Case:")
                                for item in output["bear_case"]:
                                    # Handle both old format (dict with "point") and new format (string)
                                    if isinstance(item, dict):
                                        point = item.get("point", "")
                                    else:
                                        point = str(item)
                                    clean_point = clean_citation_tags(point)
                                    st.markdown(f"- {clean_point}")
                                st.markdown("")
                            
                            # Neutral Take
                            if "neutral_take" in output:
                                clean_neutral = clean_citation_tags(output["neutral_take"])
                                st.markdown(f"**⚖️ Neutral Take:** {clean_neutral}")
                                st.markdown("")
                            
                            # Conditions to Change View
                            if "two_conditions_to_change_view" in output and output["two_conditions_to_change_view"]:
                                st.markdown("**🔄 Conditions That Would Change This View:**")
                                for cond in output["two_conditions_to_change_view"]:
                                    # Handle both old format (dict with "condition") and new format (string)
                                    if isinstance(cond, dict):
                                        condition_text = cond.get("condition", "")
                                    else:
                                        condition_text = str(cond)
                                    clean_condition = clean_citation_tags(condition_text)
                                    st.markdown(f"- {clean_condition}")
                            
                            st.info("✅ **Fact-locked AI**: All arguments based on technical facts above")
                
                else:
                    st.warning("⚠️ Not enough data to detect patterns. Try a different ticker or timeframe.")
        
        
        # ✅ Disabled celebrations (balloons/confetti) on Pro tab
        # Pro tab is a professional tool - no gamification elements
        
        # ✅ Removed Fundamental Screening from Pro (Pro is technical + AI only)
        
        # ✅ PRO CLEANUP + THEME FIX COMPLETE


# ============================================================================
# 👑 ULTIMATE TAB - PREMIUM AI-FIRST ANALYSIS
# ============================================================================

elif selected_page == "👑 Ultimate":
    # ============= PURPLE PILL HEADER =============
    st.markdown("""
    <div style="background: linear-gradient(135deg, #9D4EDD 0%, #7B2CBF 100%); 
                padding: 15px 25px; 
                border-radius: 15px; 
                text-align: center; 
                margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(157, 78, 221, 0.3);">
        <h2 style="margin: 0; color: white; font-size: 24px;">
            🟣 ULTIMATE — AI Planner + Backtest-Lite
        </h2>
        <p style="margin: 5px 0 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">
            Institutional-grade analysis • 7-10 bullet deep-dives • Premium exclusive
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("*Premium AI-powered analysis with fact-locked insights. Everything adapts to your selected ticker.*")
    
    # ============= RED THEME STYLING =============
    st.markdown("""
    <style>
    /* Red theme for Ultimate tab */
    [data-testid="stExpander"] {
        background-color: rgba(255, 75, 75, 0.1) !important;
        border: 1px solid #FF4B4B !important;
    }
    
    [data-testid="stExpander"] summary {
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Selectbox styling */
    [data-testid="stSelectbox"] > div > div {
        background-color: #FF4B4B !important;
        color: white !important;
    }
    
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #FF4B4B !important;
        color: white !important;
    }
    
    /* Dropdown menu styling */
    div[data-baseweb="popover"] {
        background-color: #FF4B4B !important;
    }
    
    div[data-baseweb="popover"] ul[role="listbox"] {
        background-color: #FF4B4B !important;
    }
    
    div[data-baseweb="popover"] li[role="option"] {
        background-color: #FF4B4B !important;
        color: white !important;
    }
    
    div[data-baseweb="popover"] li[role="option"]:hover {
        background-color: #CC3333 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ============= REUSE PRO DATA LOADING =============
    # Use exact same data loading as Pro - DO NOT DUPLICATE
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    # Use demo ticker if coming from VIP page
    default_ticker = st.session_state.get('demo_ticker', "GOOGL")
    
    with col1:
        ticker = st.text_input("Ticker", value=default_ticker, key="ultimate_ticker").upper().strip()
    
    with col2:
        timeframe_options = ["6mo", "1y", "2y", "5y"]
        timeframe = st.selectbox("Timeframe", timeframe_options, index=1, key="ultimate_timeframe")
    
    with col3:
        interval_options = ["1d", "1wk", "1mo"]
        interval = st.selectbox("Interval", interval_options, index=0, key="ultimate_interval")
    
    with col4:
        simple_mode = st.toggle("ELI5", value=False, key="ultimate_simple_mode",
                               help="Explain Like I'm 5 - simpler language")
    
    analyze_btn = st.button("🔍 Analyze", key="ultimate_analyze", use_container_width=True)
    
    # Generate cache key for this ticker/timeframe/interval combo
    cache_key = f"{ticker}|{timeframe}|{interval}"
    
    # Initialize cache if needed
    if 'ultimate_cache_key' not in st.session_state:
        st.session_state.ultimate_cache_key = None
    if 'ultimate_price_data' not in st.session_state:
        st.session_state.ultimate_price_data = None
    if 'ultimate_tech_facts' not in st.session_state:
        st.session_state.ultimate_tech_facts = None
    
    # Load data if analyze clicked OR cache invalid
    if analyze_btn or st.session_state.ultimate_cache_key != cache_key:
        with st.spinner(f"Loading {ticker} data..."):
            # Convert timeframe to years
            timeframe_to_years = {
                "6mo": 0.5,
                "1y": 1,
                "2y": 2,
                "5y": 5
            }
            years = timeframe_to_years.get(timeframe, 1)
            
            # Use correct function - get_historical_ohlc
            price_data = get_historical_ohlc(ticker, years)
            
            if price_data is not None and len(price_data) > 0:
                # Update cache
                st.session_state.ultimate_cache_key = cache_key
                st.session_state.ultimate_price_data = price_data
                
                # Compute technical facts
                tech_facts = compute_technical_facts(price_data)
                st.session_state.ultimate_tech_facts = tech_facts
                
                st.success(f"✅ Loaded {len(price_data)} data points for {ticker}")
            else:
                st.error(f"⚠️ Could not load data for {ticker}")
                st.session_state.ultimate_cache_key = None
                st.session_state.ultimate_price_data = None
                st.session_state.ultimate_tech_facts = None
    
    # Check if we have data
    if st.session_state.ultimate_price_data is None or st.session_state.ultimate_tech_facts is None:
        st.info("👆 Enter a ticker and click Analyze to start")
        st.stop()
    
    # Get cached data
    df = st.session_state.ultimate_price_data
    tech_facts = st.session_state.ultimate_tech_facts
    
    # ============= PREMIUM CANDLESTICK CHART =============
    st.markdown("---")
    st.markdown(f"### 📊 {ticker} Price Chart")
    
    # Chart setup
    price_history = df
    show_sma50 = True
    show_sma200 = True
    show_rsi = True
    show_volume = True
    
    # Check if we have OHLC data
    has_ohlc = all(col in price_history.columns for col in ['open', 'high', 'low', 'close'])
    chart_features = []
    
    if has_ohlc:
        chart_features.append("OHLC")
        
        # Determine number of rows
        num_rows = 1
        subplot_titles_list = [f'{ticker} Price']
        
        if show_rsi:
            num_rows += 1
            subplot_titles_list.append('RSI (14)')
        
        if show_volume and 'volume' in price_history.columns:
            num_rows += 1
            subplot_titles_list.append('Volume')
        
        # Calculate row heights
        if num_rows == 1:
            row_heights = [1.0]
        elif num_rows == 2:
            row_heights = [0.7, 0.3]
        else:  # 3 rows
            row_heights = [0.6, 0.2, 0.2]
        
        # Create candlestick chart
        fig_price = make_subplots(
            rows=num_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=tuple(subplot_titles_list)
        )
        
        # Add candlestick
        fig_price.add_trace(
            go.Candlestick(
                x=price_history['date'],
                open=price_history['open'],
                high=price_history['high'],
                low=price_history['low'],
                close=price_history['close'],
                name='Price',
                increasing_line_color='#00FF00',
                decreasing_line_color='#FF4444'
            ),
            row=1, col=1
        )
        
        # Add volume
        if show_volume and 'volume' in price_history.columns:
            colors = ['#00FF00' if price_history['close'].iloc[i] >= price_history['open'].iloc[i] else '#FF4444' 
                      for i in range(len(price_history))]
            
            volume_row = num_rows
            
            fig_price.add_trace(
                go.Bar(
                    x=price_history['date'],
                    y=price_history['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.5
                ),
                row=volume_row, col=1
            )
            chart_features.append("Volume")
    else:
        # Fallback line chart
        chart_features.append("Line")
        fig_price = go.Figure()
        price_col = 'close' if 'close' in price_history.columns else 'price'
        
        fig_price.add_trace(go.Scatter(
            x=price_history['date'],
            y=price_history[price_col],
            mode='lines',
            name='Price',
            line=dict(color='#9D4EDD', width=2),
            fill='tozeroy',
            fillcolor='rgba(157, 78, 221, 0.2)',
            hovertemplate='%{x}<br>Price: $%{y:.2f}<extra></extra>'
        ))
    
    # Add SMAs
    close_col = 'close' if 'close' in price_history.columns else 'price'
    
    if show_sma50 and len(price_history) >= 50:
        sma50 = price_history[close_col].rolling(window=50, min_periods=1).mean()
        sma_trace_50 = go.Scatter(
            x=price_history['date'],
            y=sma50,
            mode='lines',
            name='SMA 50',
            line=dict(color='#FFA500', width=2)
        )
        
        if has_ohlc:
            fig_price.add_trace(sma_trace_50, row=1, col=1)
        else:
            fig_price.add_trace(sma_trace_50)
        
        chart_features.append("SMA50")
    
    if show_sma200 and len(price_history) >= 200:
        sma200 = price_history[close_col].rolling(window=200, min_periods=1).mean()
        sma_trace_200 = go.Scatter(
            x=price_history['date'],
            y=sma200,
            mode='lines',
            name='SMA 200',
            line=dict(color='#9D4EDD', width=2)
        )
        
        if has_ohlc:
            fig_price.add_trace(sma_trace_200, row=1, col=1)
        else:
            fig_price.add_trace(sma_trace_200)
        
        chart_features.append("SMA200")
    
    # Add RSI
    if show_rsi and len(price_history) >= 14:
        delta = price_history[close_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        rsi_row = 2 if show_rsi else None
        if rsi_row and has_ohlc:
            fig_price.add_trace(
                go.Scatter(
                    x=price_history['date'],
                    y=rsi,
                    mode='lines',
                    name='RSI',
                    line=dict(color='#FFD700', width=2)
                ),
                row=rsi_row, col=1
            )
            
            # Add overbought/oversold lines
            fig_price.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=rsi_row, col=1)
            fig_price.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=rsi_row, col=1)
            
            fig_price.update_yaxes(title_text="RSI", range=[0, 100], row=rsi_row, col=1)
            
            chart_features.append("RSI")
    
    # Update layout
    fig_price.update_layout(
        title=f"{ticker} Price History ({timeframe})",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        template='plotly_dark',
        margin=dict(l=0, r=0, t=40, b=0),
        hovermode='x unified',
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    # Add rangeslider
    if has_ohlc:
        fig_price.update_xaxes(
            rangeslider=dict(
                visible=True,
                thickness=0.05,
                bgcolor="rgba(150, 150, 150, 0.1)"
            ),
            row=num_rows, col=1
        )
    else:
        fig_price.update_xaxes(
            rangeslider=dict(
                visible=True,
                thickness=0.05,
                bgcolor="rgba(150, 150, 150, 0.1)"
            )
        )
    
    # Update axis labels
    if has_ohlc:
        fig_price.update_yaxes(title_text="Price ($)", row=1, col=1)
        if show_volume:
            fig_price.update_yaxes(title_text="Volume", row=num_rows, col=1)
    
    # Display chart
    st.plotly_chart(fig_price, use_container_width=True)
    
    # Status line
    if has_ohlc:
        status_parts = [f"{feat} ✓" for feat in chart_features]
        st.success(f"✅ Chart ready: {' | '.join(status_parts)}")
    else:
        st.warning("⚠️ OHLC not available — showing line chart fallback.")
    
    st.markdown("---")
    
    # ============= INCLUDE PRO CONTENT (COLLAPSED) =============
    with st.expander("✅ Pro Analysis (included)", expanded=False):
        st.caption("*Standard Pro analysis is included in Ultimate - expand to view*")
        
        # Show compact Pro analysis
        st.markdown("### 📌 Key Observations")
        callouts = render_chart_callouts(tech_facts)
        for callout in callouts[:5]:  # Max 5
            st.markdown(f"- {callout}")
        
        # Pattern detection
        pattern_label, confidence, reasons, watch_level, watch_note = detect_rule_based_pattern(tech_facts, simple_mode)
        
        st.markdown("### 🔍 Pattern Detected")
        conf_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "⚪")
        st.markdown(f"**{conf_color} {pattern_label}** (Confidence: {confidence})")
        
        for reason in reasons[:3]:  # Max 3
            st.markdown(f"- {reason}")
    
    st.markdown("---")
    
    # ============= MODULE A: KEY LEVELS MAP =============
    st.markdown("### 🎯 Key Levels Map (Ultimate)")
    st.caption("*Top 3 supports and resistances derived from price history*")
    
    last_close = tech_facts.get("last_close")
    
    if last_close:
        # Compute multiple support/resistance levels
        supports = []
        resistances = []
        
        # Method 1: Swing lows/highs at different windows
        for window in [20, 50, 90]:
            if len(df) >= window:
                swing_low = df['close'].rolling(window=window, center=True).min().dropna()
                swing_high = df['close'].rolling(window=window, center=True).max().dropna()
                
                # Find recent swing lows below current price
                recent_lows = swing_low[swing_low < last_close].tail(10)
                for low in recent_lows.unique():
                    if low < last_close:
                        supports.append({"level": float(low), "source": f"Swing-{window}d"})
                
                # Find recent swing highs above current price
                recent_highs = swing_high[swing_high > last_close].tail(10)
                for high in recent_highs.unique():
                    if high > last_close:
                        resistances.append({"level": float(high), "source": f"Swing-{window}d"})
        
        # Method 2: Quantile levels
        for q, label in [(0.10, "Q10"), (0.25, "Q25"), (0.75, "Q75"), (0.90, "Q90")]:
            level = float(df['close'].quantile(q))
            if level < last_close * 0.98:
                supports.append({"level": level, "source": label})
            elif level > last_close * 1.02:
                resistances.append({"level": level, "source": label})
        
        # Method 3: Add SMA50/SMA200 if relevant
        sma50 = tech_facts.get("sma50")
        sma200 = tech_facts.get("sma200")
        
        if sma50 and abs(sma50 - last_close) / last_close < 0.10:  # Within 10%
            if sma50 < last_close:
                supports.append({"level": float(sma50), "source": "SMA50"})
            elif sma50 > last_close:
                resistances.append({"level": float(sma50), "source": "SMA50"})
        
        if sma200 and abs(sma200 - last_close) / last_close < 0.15:  # Within 15%
            if sma200 < last_close:
                supports.append({"level": float(sma200), "source": "SMA200"})
            elif sma200 > last_close:
                resistances.append({"level": float(sma200), "source": "SMA200"})
        
        # Create synthetic levels if needed
        atr_pct = tech_facts.get("atr_pct", 2.0)
        atr_decimal = atr_pct / 100.0 if atr_pct > 1 else atr_pct
        
        if len(supports) == 0:
            # At new lows - create synthetic support
            synth_dist = min(0.05, max(0.03, 2 * atr_decimal))
            supports.append({"level": last_close * (1 - synth_dist), "source": "Synthetic"})
        
        if len(resistances) == 0:
            # At new highs - create synthetic resistance
            synth_dist = min(0.05, max(0.03, 2 * atr_decimal))
            resistances.append({"level": last_close * (1 + synth_dist), "source": "Synthetic"})
        
        # Sort and deduplicate
        supports = sorted(supports, key=lambda x: x["level"], reverse=True)  # Closest first
        resistances = sorted(resistances, key=lambda x: x["level"])  # Closest first
        
        # Deduplicate levels within 1%
        def dedupe_levels(levels_list):
            if not levels_list:
                return []
            deduped = [levels_list[0]]
            for level_dict in levels_list[1:]:
                if all(abs(level_dict["level"] - d["level"]) / d["level"] > 0.01 for d in deduped):
                    deduped.append(level_dict)
            return deduped
        
        supports = dedupe_levels(supports)[:3]  # Top 3
        resistances = dedupe_levels(resistances)[:3]  # Top 3
        
        # Display as table
        import pandas as pd
        
        levels_data = []
        
        for sup in supports:
            dist_pct = ((sup["level"] - last_close) / last_close) * 100
            levels_data.append({
                "Type": "Support",
                "Level": f"${sup['level']:.2f}",
                "Distance": f"{dist_pct:+.2f}%",
                "Source": sup["source"]
            })
        
        for res in resistances:
            dist_pct = ((res["level"] - last_close) / last_close) * 100
            levels_data.append({
                "Type": "Resistance",
                "Level": f"${res['level']:.2f}",
                "Distance": f"{dist_pct:+.2f}%",
                "Source": res["source"]
            })
        
        if levels_data:
            levels_df = pd.DataFrame(levels_data)
            st.dataframe(levels_df, use_container_width=True, hide_index=True)
        else:
            st.caption("Could not compute key levels")
        
        # ============= COMPUTE NEAREST LEVELS (FOR USE IN LATER MODULES) =============
        # These are needed by Trade Plan Builder AND Scenario Simulator
        nearest_support = supports[0]["level"] if supports else last_close * 0.97
        nearest_resistance = resistances[0]["level"] if resistances else last_close * 1.03
    
    st.markdown("---")
    
    # ============= MODULE B: TRADE PLAN BUILDER =============
    st.markdown("### 📋 Trade Plan Builder (Educational)")
    st.caption("*Educational template - NOT financial advice*")
    
    col_dir, col_hor, col_risk = st.columns(3)
    
    with col_dir:
        direction = st.selectbox("Direction", ["Long", "Short"], key="ultimate_direction")
    
    with col_hor:
        horizon = st.selectbox("Horizon", ["Day", "Swing", "Position"], key="ultimate_horizon")
    
    with col_risk:
        risk_style = st.selectbox("Risk Style", ["Conservative", "Moderate", "Aggressive"], key="ultimate_risk")
    
    if st.button("🔨 Build Plan", key="build_plan"):
        # Build educational plan based on facts (using pre-computed nearest levels)
        
        st.markdown("**📊 Plan Summary:**")
        
        bullets = []
        
        if direction == "Long":
            entry_zone = f"${nearest_support:.2f} - ${last_close:.2f}"
            invalidation = f"${nearest_support * 0.985:.2f} (below nearest support)"
            target1 = f"${nearest_resistance:.2f}"
            target2 = f"${resistances[1]['level']:.2f}" if len(resistances) > 1 else f"${nearest_resistance * 1.03:.2f}"
            
            bullets.append(f"**Entry Zone:** {entry_zone} (near support)")
            bullets.append(f"**Invalidation:** Below {invalidation}")
            bullets.append(f"**Target 1 (1R):** {target1}")
            bullets.append(f"**Target 2 (2R):** {target2}")
            bullets.append(f"**Horizon:** {horizon} trade (adjust time accordingly)")
        
        else:  # Short
            entry_zone = f"${last_close:.2f} - ${nearest_resistance:.2f}"
            invalidation = f"${nearest_resistance * 1.015:.2f} (above nearest resistance)"
            target1 = f"${nearest_support:.2f}"
            target2 = f"${supports[1]['level']:.2f}" if len(supports) > 1 else f"${nearest_support * 0.97:.2f}"
            
            bullets.append(f"**Entry Zone:** {entry_zone} (near resistance)")
            bullets.append(f"**Invalidation:** Above {invalidation}")
            bullets.append(f"**Target 1 (1R):** {target1}")
            bullets.append(f"**Target 2 (2R):** {target2}")
            bullets.append(f"**Horizon:** {horizon} trade (adjust time accordingly)")
        
        for bullet in bullets[:5]:
            st.markdown(f"- {bullet}")
        
        st.info("📚 Educational template only. Not financial advice. Always do your own research.")
    
    st.markdown("---")
    
    # ============= MODULE C: HISTORICAL SIMILAR SETUPS =============
    with st.expander("📊 Historical Similar Setups (Backtest-Lite)", expanded=False):
        st.caption("*Find past dates when the setup looked similar*")
        
        if st.button("🔍 Find Similar Setups", key="find_similar"):
            with st.spinner("Analyzing historical patterns..."):
                # Compute feature vectors for all historical dates
                if len(df) < 120:
                    st.warning("Need at least 120 days of data for similarity analysis")
                else:
                    # Current setup features - handle None values safely
                    curr_pct_above_sma50 = tech_facts.get("pct_above_sma50") or 0
                    curr_pct_above_sma200 = tech_facts.get("pct_above_sma200") or 0
                    
                    current_features = {
                        "above_sma50": curr_pct_above_sma50 > 0,
                        "above_sma200": curr_pct_above_sma200 > 0,
                        "rsi_state": tech_facts.get("rsi_state", "neutral"),
                        "vol_regime": tech_facts.get("vol_regime", "medium"),
                        "dist_sma50": curr_pct_above_sma50,
                        "dist_sma200": curr_pct_above_sma200,
                        "volume_spike": tech_facts.get("volume_spike", False)
                    }
                    
                    # Compute features for historical windows
                    similar_dates = []
                    
                    for i in range(60, len(df) - 20):  # Skip last 20 days to avoid trivial matches
                        hist_slice = df.iloc[:i+1]
                        
                        if len(hist_slice) < 60:
                            continue
                        
                        # Compute features for this historical point
                        hist_facts = compute_technical_facts(hist_slice)
                        
                        # Handle None values safely
                        pct_above_sma50 = hist_facts.get("pct_above_sma50") or 0
                        pct_above_sma200 = hist_facts.get("pct_above_sma200") or 0
                        
                        hist_features = {
                            "above_sma50": pct_above_sma50 > 0,
                            "above_sma200": pct_above_sma200 > 0,
                            "rsi_state": hist_facts.get("rsi_state", "neutral"),
                            "vol_regime": hist_facts.get("vol_regime", "medium"),
                            "dist_sma50": pct_above_sma50,
                            "dist_sma200": pct_above_sma200,
                            "volume_spike": hist_facts.get("volume_spike", False)
                        }
                        
                        # Compute similarity score
                        score = 0
                        
                        if hist_features["above_sma50"] == current_features["above_sma50"]:
                            score += 1
                        if hist_features["above_sma200"] == current_features["above_sma200"]:
                            score += 1
                        if hist_features["rsi_state"] == current_features["rsi_state"]:
                            score += 2
                        if hist_features["vol_regime"] == current_features["vol_regime"]:
                            score += 1
                        if hist_features["volume_spike"] == current_features["volume_spike"]:
                            score += 1
                        
                        # Distance penalty
                        dist_penalty = abs(hist_features["dist_sma50"] - current_features["dist_sma50"]) / 10.0
                        score -= min(dist_penalty, 2)
                        
                        # Compute forward returns
                        date_idx = hist_slice.index[-1]
                        try:
                            future_5d = ((df.loc[date_idx:].iloc[5]["close"] / df.loc[date_idx]["close"]) - 1) * 100 if i + 5 < len(df) else None
                            future_20d = ((df.loc[date_idx:].iloc[20]["close"] / df.loc[date_idx]["close"]) - 1) * 100 if i + 20 < len(df) else None
                            future_60d = ((df.loc[date_idx:].iloc[60]["close"] / df.loc[date_idx]["close"]) - 1) * 100 if i + 60 < len(df) else None
                        except:
                            future_5d = future_20d = future_60d = None
                        
                        similar_dates.append({
                            "date": date_idx,
                            "score": score,
                            "fwd_5d": future_5d,
                            "fwd_20d": future_20d,
                            "fwd_60d": future_60d
                        })
                    
                    # Sort by score
                    similar_dates = sorted(similar_dates, key=lambda x: x["score"], reverse=True)[:10]
                    
                    if similar_dates:
                        st.markdown("**Top 10 Similar Historical Setups:**")
                        
                        sim_data = []
                        for match in similar_dates:
                            outcome = "Continuation" if (match["fwd_20d"] or 0) > 2 else "Reversal" if (match["fwd_20d"] or 0) < -2 else "Chop"
                            
                            sim_data.append({
                                "Date": match["date"].strftime("%Y-%m-%d") if hasattr(match["date"], "strftime") else str(match["date"]),
                                "Similarity": f"{match['score']:.1f}",
                                "+5d": f"{match['fwd_5d']:+.2f}%" if match["fwd_5d"] else "N/A",
                                "+20d": f"{match['fwd_20d']:+.2f}%" if match["fwd_20d"] else "N/A",
                                "+60d": f"{match['fwd_60d']:+.2f}%" if match["fwd_60d"] else "N/A",
                                "Outcome": outcome
                            })
                        
                        sim_df = pd.DataFrame(sim_data)
                        st.dataframe(sim_df, use_container_width=True, hide_index=True)
                        
                        st.info("📊 Historical analysis for educational purposes only")
                    else:
                        st.caption("No similar setups found in history")
    
    st.markdown("---")
    
    # ============= MODULE D: SCENARIO SIMULATOR =============
    st.markdown("### 🎲 Scenario Simulator (Bull/Base/Bear)")
    st.caption("*Three potential scenarios based on key levels and volatility*")
    
    atr_pct = tech_facts.get("atr_pct", 2.0)
    
    col_bull, col_base, col_bear = st.columns(3)
    
    with col_bull:
        st.markdown("#### 🐂 Bull Scenario")
        st.markdown(f"**Trigger:** Break above ${nearest_resistance:.2f}")
        st.markdown(f"**Expected Move:** +{atr_pct:.1f}% to +{atr_pct*2:.1f}%")
        st.markdown(f"**Invalidation:** Fails if drops below ${nearest_support:.2f}")
    
    with col_base:
        st.markdown("#### ⚖️ Base Scenario")
        st.markdown(f"**Trigger:** Range between ${nearest_support:.2f} - ${nearest_resistance:.2f}")
        st.markdown(f"**Expected Move:** ±{atr_pct*0.5:.1f}% (choppy)")
        st.markdown(f"**Invalidation:** Break either way with volume")
    
    with col_bear:
        st.markdown("#### 🐻 Bear Scenario")
        st.markdown(f"**Trigger:** Break below ${nearest_support:.2f}")
        st.markdown(f"**Expected Move:** -{atr_pct:.1f}% to -{atr_pct*2:.1f}%")
        st.markdown(f"**Invalidation:** Fails if rises above ${nearest_resistance:.2f}")
    
    st.markdown("---")
    
    # ============= MODULE E: ULTIMATE AI DEEP DIVE =============
    st.markdown("### 🤖 Ultimate AI Deep Dive (Perplexity)")
    st.caption("*AI analysis locked to technical facts - no hallucinations*")
    
    # Check if Perplexity is available
    perplexity_available = bool(os.environ.get('PERPLEXITY_API_KEY', ''))
    
    if not perplexity_available:
        st.warning("⚠️ AI features require PERPLEXITY_API_KEY environment variable")
    else:
        col_ai1, col_ai2 = st.columns(2)
        
        with col_ai1:
            trade_plan_btn = st.button("📝 Trade Plan Rationale (AI)", key="ultimate_trade_plan_ai", use_container_width=True)
        
        with col_ai2:
            change_view_btn = st.button("🔄 What Would Change View? (AI)", key="ultimate_change_view_ai", use_container_width=True)
        
        # Initialize session state
        if 'ultimate_trade_plan_ai' not in st.session_state:
            st.session_state.ultimate_trade_plan_output = None
        if 'ultimate_change_view_ai' not in st.session_state:
            st.session_state.ultimate_change_view_output = None
        
        # Build allowed fact keys list
        allowed_fact_keys = list(tech_facts.keys()) + [f"support_{i}" for i in range(1, 4)] + [f"resistance_{i}" for i in range(1, 4)]
        
        # Add support/resistance levels to facts
        for i, sup in enumerate(supports, 1):
            tech_facts[f"support_{i}"] = sup["level"]
        for i, res in enumerate(resistances, 1):
            tech_facts[f"resistance_{i}"] = res["level"]
        
        # ============= TRADE PLAN RATIONALE AI =============
        if trade_plan_btn:
            # Clear the other output
            st.session_state.ultimate_change_view_output = None
            
            with st.spinner("🤖 AI building comprehensive trade plan rationale..."):
                prompt = f"""You are an ELITE trading education AI for premium subscribers. Provide comprehensive, institutional-grade analysis.

CRITICAL FORMATTING:
1. Format ALL dollar amounts: $XXX.XX
2. Format ALL percentages: XX.XX%
3. Format ALL numbers with commas if >999
4. NO brackets like [sma50] anywhere
5. Use professional but accessible language
6. Provide 7-10 detailed bullets (this is PREMIUM)

FACTS (USE ONLY THESE):
{json.dumps({k: v for k, v in tech_facts.items() if v is not None}, indent=2)}

Return ONLY this JSON (no markdown, no code blocks):

{{
  "ticker": "{ticker}",
  "summary": "2-3 sentences providing a sophisticated overview of the current setup, market context, and what makes this particularly interesting or concerning right now",
  "bullets": [
    "Point 1: Current price action and positioning relative to key moving averages - what does this tell us about institutional sentiment?",
    "Point 2: Momentum analysis - RSI state, recent performance, and what this suggests about near-term direction",
    "Point 3: Volume analysis - what is volume telling us about conviction behind recent moves?",
    "Point 4: Volatility regime - is this a low-vol grind or high-vol environment? What does that mean for position sizing?",
    "Point 5: Key support level - where is the nearest meaningful support and why does it matter?",
    "Point 6: Key resistance level - what's the upside target and what would need to happen to reach it?",
    "Point 7: Risk/reward setup - given current positioning, what's the risk/reward profile?",
    "Point 8: Timeframe consideration - is this a day trade, swing trade, or position trade setup?",
    "Point 9: Catalyst or watch items - what events or levels should traders monitor?",
    "Point 10: Contrarian view - what's the counter-argument to this setup?"
  ],
  "fact_keys_used": ["list", "of", "fact", "keys", "used"]
}}

CRITICAL REQUIREMENTS:
- Provide 7-10 comprehensive bullets (NOT just 5)
- NO [bracket] tags anywhere
- Every bullet must cite specific numbers from facts
- All numbers properly formatted with $, %, commas
- Think like an institutional trader - what really matters?
- Consider multiple timeframes and scenarios
- Address BOTH bullish AND bearish perspectives"""

                ai_response = call_perplexity_json(prompt, max_tokens=3500, temperature=0.1)
                
                if ai_response:
                    # Validate
                    is_valid = True
                    error_msg = ""
                    
                    # Check structure
                    if not isinstance(ai_response, dict):
                        is_valid = False
                        error_msg = "Invalid JSON structure"
                    
                    # Check ticker matches
                    if is_valid and ai_response.get("ticker", "").upper() != ticker.upper():
                        is_valid = False
                        error_msg = f"Ticker mismatch: expected {ticker}, got {ai_response.get('ticker')}"
                    
                    # Check for bracket tags
                    if is_valid:
                        import re
                        all_text = json.dumps(ai_response)
                        if re.search(r'\[[a-zA-Z0-9_]+\]', all_text):
                            is_valid = False
                            error_msg = "AI output contains bracket tags"
                    
                    # For premium, allow 7-10 bullets (not just 5)
                    if is_valid and "bullets" in ai_response:
                        ai_response["bullets"] = ai_response["bullets"][:10]
                    
                    if is_valid:
                        st.session_state.ultimate_trade_plan_output = ai_response
                    else:
                        st.error(f"⚠️ AI validation failed: {error_msg}")
                        st.info("Showing rule-based rationale instead")
                        st.session_state.ultimate_trade_plan_output = None
                else:
                    st.error("⚠️ AI request failed")
                    st.session_state.ultimate_trade_plan_output = None
        
        # ============= WHAT WOULD CHANGE VIEW AI =============
        if change_view_btn:
            # Clear the other output
            st.session_state.ultimate_trade_plan_output = None
            
            with st.spinner("🤖 AI analyzing comprehensive scenario triggers..."):
                prompt = f"""You are an ELITE trading education AI for premium subscribers. Provide comprehensive scenario analysis with specific trigger conditions.

CRITICAL FORMATTING:
1. Format ALL dollar amounts: $XXX.XX
2. Format ALL percentages: XX.XX%
3. Format ALL numbers with commas if >999
4. NO brackets like [sma50] anywhere
5. Use professional but accessible language
6. Provide 7-10 detailed IF/THEN conditions (this is PREMIUM)
7. Be specific about price levels, timeframes, and follow-through

FACTS (USE ONLY THESE):
{json.dumps({k: v for k, v in tech_facts.items() if v is not None}, indent=2)}

Return ONLY this JSON (no markdown, no code blocks):

{{
  "ticker": "{ticker}",
  "summary": "2-3 sentences about the current state, key inflection points, and what would need to change to shift the narrative",
  "bullets": [
    "IF price breaks above $XXX (resistance) with volume > YYY... THEN expect move to next resistance at $ZZZ (momentum breakout scenario)",
    "IF price breaks below $XXX (support) on increasing volume... THEN expect retest of $YYY (breakdown scenario)",
    "IF RSI crosses above/below XX while price is at $YYY... THEN suggests momentum shift (divergence scenario)",
    "IF volume spikes above X% of 20-day average at current levels... THEN indicates institutional accumulation/distribution",
    "IF price consolidates between $XXX-$YYY for X+ days... THEN coiling pattern suggests directional move brewing",
    "IF SMA50 crosses above/below SMA200 (Golden/Death Cross)... THEN confirms long-term trend change",
    "IF volatility (ATR) drops below X% while at resistance... THEN suggests breakout imminent (volatility compression)",
    "IF price gaps above/below $XXX on open... THEN watch for gap fill or continuation pattern",
    "IF fails to hold $XXX support for 2+ consecutive days... THEN reassess bull case entirely",
    "IF breaks above $XXX AND holds it as support for 3+ days... THEN new higher range established"
  ],
  "fact_keys_used": ["list", "of", "fact", "keys", "used"]
}}

CRITICAL REQUIREMENTS:
- Provide 7-10 comprehensive IF/THEN conditions (NOT just 5)
- NO [bracket] tags anywhere
- Every condition must cite specific $ prices and % levels from facts
- Include BOTH bullish AND bearish triggers
- Consider volume, volatility, and time elements
- Think about what institutional traders watch
- Address multiple timeframes (intraday, swing, position)
- All numbers properly formatted with $, %, commas"""

                ai_response = call_perplexity_json(prompt, max_tokens=3500, temperature=0.1)
                
                if ai_response:
                    # Validate (same as above)
                    is_valid = True
                    error_msg = ""
                    
                    if not isinstance(ai_response, dict):
                        is_valid = False
                        error_msg = "Invalid JSON structure"
                    
                    if is_valid and ai_response.get("ticker", "").upper() != ticker.upper():
                        is_valid = False
                        error_msg = f"Ticker mismatch"
                    
                    if is_valid:
                        import re
                        all_text = json.dumps(ai_response)
                        if re.search(r'\[[a-zA-Z0-9_]+\]', all_text):
                            is_valid = False
                            error_msg = "AI output contains bracket tags"
                    
                    # For premium, allow 7-10 bullets
                    if is_valid and "bullets" in ai_response:
                        ai_response["bullets"] = ai_response["bullets"][:10]
                    
                    if is_valid:
                        st.session_state.ultimate_change_view_output = ai_response
                    else:
                        st.error(f"⚠️ AI validation failed: {error_msg}")
                        st.info("Showing rule-based conditions instead")
                        st.session_state.ultimate_change_view_output = None
                else:
                    st.error("⚠️ AI request failed")
                    st.session_state.ultimate_change_view_output = None
        
        # ============= DISPLAY TRADE PLAN RATIONALE AI =============
        if st.session_state.ultimate_trade_plan_output:
            st.markdown("---")
            st.markdown("#### 📝 Comprehensive Trade Plan Rationale (Premium AI)")
            
            output = st.session_state.ultimate_trade_plan_output
            
            if "summary" in output:
                st.markdown(f"**{output['summary']}**")
                st.markdown("")
            
            if "bullets" in output:
                st.markdown("**Institutional-Grade Analysis:**")
                for i, bullet in enumerate(output["bullets"], 1):
                    cleaned = clean_citation_tags(str(bullet))
                    st.markdown(f"{i}. {cleaned}")
            
            st.info("✅ Premium Fact-Locked AI: Comprehensive analysis grounded in technical facts • Ultimate tier exclusive")
        
        # ============= DISPLAY WHAT WOULD CHANGE VIEW AI =============
        if st.session_state.ultimate_change_view_output:
            st.markdown("---")
            st.markdown("#### 🔄 Scenario Triggers & Inflection Points (Premium AI)")
            
            output = st.session_state.ultimate_change_view_output
            
            if "summary" in output:
                st.markdown(f"**{output['summary']}**")
                st.markdown("")
            
            if "bullets" in output:
                st.markdown("**Key Conditions to Monitor:**")
                for i, bullet in enumerate(output["bullets"], 1):
                    cleaned = clean_citation_tags(str(bullet))
                    st.markdown(f"{i}. {cleaned}")
            
            st.info("✅ Premium Fact-Locked AI: Comprehensive scenario analysis • Ultimate tier exclusive")


# NEW PAPER PORTFOLIO PAGE - Section 6 Implementation
# This will replace lines 8367-8765 in the main file

elif selected_page == "💼 Paper Portfolio":
    st.header("💼 Paper Portfolio")
    st.caption("*Practice trading with fake money. Track your performance vs the market.*")
    
    # ============= INITIALIZATION =============
    # User portfolio
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'cash' not in st.session_state:
        st.session_state.cash = STARTING_CASH
    if 'transactions' not in st.session_state:
        st.session_state.transactions = []
    if 'realized_gains' not in st.session_state:
        st.session_state.realized_gains = 0.0
    if 'concentration_flags' not in st.session_state:
        st.session_state.concentration_flags = {}
    
    # Founder portfolio (now real, not hardcoded)
    if 'founder_portfolio' not in st.session_state:
        st.session_state.founder_portfolio = []
    if 'founder_cash' not in st.session_state:
        st.session_state.founder_cash = STARTING_CASH
    if 'founder_transactions' not in st.session_state:
        st.session_state.founder_transactions = []
    if 'founder_realized_gains' not in st.session_state:
        st.session_state.founder_realized_gains = 0.0
    
    # ============= LOAD TRADES FROM DATABASE =============
    # Load user trades if logged in
    user_id = st.session_state.get("user_id")
    
    if SUPABASE_ENABLED and user_id:
        # Load user portfolio trades
        db_transactions = load_trades_from_db(user_id, portfolio_type='user')
        if db_transactions:
            st.session_state.transactions = db_transactions
            
            # Recalculate cash from DB trades
            cash, _ = calculate_cash_from_db(user_id, portfolio_type='user')
            st.session_state.cash = cash
            
            # Rebuild portfolio from transactions
            st.session_state.portfolio = rebuild_portfolio_from_trades(db_transactions)
    
    # Load founder trades (public, always load)
    if SUPABASE_ENABLED:
        founder_db_transactions = load_trades_from_db(None, portfolio_type='founder')
        if founder_db_transactions:
            st.session_state.founder_transactions = founder_db_transactions
            
            # Recalculate founder cash
            founder_cash, _ = calculate_cash_from_db(None, portfolio_type='founder')
            st.session_state.founder_cash = founder_cash
            
            # Rebuild founder portfolio
            st.session_state.founder_portfolio = rebuild_portfolio_from_trades(founder_db_transactions)
    
    # Trade UI state
    if 'show_order_modal' not in st.session_state:
        st.session_state.show_order_modal = False
    if 'pending_order' not in st.session_state:
        st.session_state.pending_order = None
    
    # Check if user is founder (derived from email match)
    FOUNDER_EMAIL = (os.getenv("FOUNDER_EMAIL") or "").strip().lower()
    user_email = (st.session_state.get("user_email") or "").strip().lower()
    is_founder = bool(user_email) and (user_email == FOUNDER_EMAIL)
    
    # Update session state for consistency
    st.session_state.is_founder = is_founder
    
    # ============= HELPER FUNCTIONS =============
    def calculate_portfolio_equity(transactions, portfolio, realized_gains):
        """Calculate portfolio equity from trade history"""
        # Calculate cash from starting position and all transactions
        cash = STARTING_CASH
        
        # Process all transactions to calculate current cash
        for txn in transactions:
            if txn['type'] == 'BUY':
                cash -= txn['total']  # Subtract cost
            elif txn['type'] == 'SELL':
                cash += txn['total']  # Add proceeds
        
        # Calculate market value of current positions
        market_value = 0.0
        for pos in portfolio:
            quote = get_quote(pos['ticker'])
            if quote:
                market_value += pos['shares'] * quote.get('price', 0)
        
        # Total equity = cash + market value
        equity = cash + market_value
        
        # Total P/L = current equity - starting cash
        total_pl = equity - STARTING_CASH
        
        # YTD return percentage
        ytd_return_pct = (total_pl / STARTING_CASH * 100) if STARTING_CASH > 0 else 0.0
        
        # Handle empty portfolio case
        if not transactions:
            equity = STARTING_CASH
            ytd_return_pct = 0.0
        
        return equity, ytd_return_pct, cash, market_value
    
    def calculate_portfolio_value(portfolio, cash):
        """Calculate total portfolio value (legacy function for compatibility)"""
        total_value = cash
        for pos in portfolio:
            quote = get_quote(pos['ticker'])
            if quote:
                total_value += pos['shares'] * quote.get('price', 0)
        return total_value
    
    def get_ytd_return(current_value, starting_value=None):
        """Calculate YTD return percentage"""
        if starting_value is None:
            starting_value = STARTING_CASH
        if starting_value == 0:
            return 0.0
        return ((current_value - starting_value) / starting_value) * 100
    
    def execute_trade(action, ticker, shares, price, portfolio_type='user'):
        """
        Execute a trade with DB validation and persistence.
        CRITICAL: Validates cash from DB before inserting.
        """
        user_id = st.session_state.get("user_id")
        
        # Use DB validation (SOURCE OF TRUTH)
        success, message = validate_and_insert_trade(
            user_id=user_id,
            portfolio_type=portfolio_type,
            action=action,
            ticker=ticker,
            shares=shares,
            price=price
        )
        
        if not success:
            return False, message
        
        # If DB insert succeeded, update session state for immediate UI update
        # (This is just for real-time display; DB remains source of truth)
        if portfolio_type == 'user':
            portfolio = st.session_state.portfolio
            cash_key = 'cash'
            realized_gains_key = 'realized_gains'
        else:  # founder
            portfolio = st.session_state.founder_portfolio
            cash_key = 'founder_cash'
            realized_gains_key = 'founder_realized_gains'
        
        if action == "Buy":
            total_cost = shares * price
            
            # Update portfolio position
            existing = None
            for pos in portfolio:
                if pos['ticker'] == ticker:
                    existing = pos
                    break
            
            if existing:
                total_shares = existing['shares'] + shares
                total_cost_all = (existing['shares'] * existing['avg_price']) + total_cost
                existing['avg_price'] = total_cost_all / total_shares
                existing['shares'] = total_shares
            else:
                portfolio.append({
                    'ticker': ticker,
                    'shares': shares,
                    'avg_price': price
                })
            
            # Update cash
            st.session_state[cash_key] -= total_cost
        
        else:  # Sell
            # Find position
            pos_to_sell = None
            pos_index = None
            for i, pos in enumerate(portfolio):
                if pos['ticker'] == ticker:
                    pos_to_sell = pos
                    pos_index = i
                    break
            
            if not pos_to_sell:
                return False, "Position not found"
            
            if shares > pos_to_sell['shares']:
                return False, f"Cannot sell {shares} shares. You only have {pos_to_sell['shares']}"
            
            # Calculate proceeds and realized gain
            proceeds = shares * price
            cost_basis = shares * pos_to_sell['avg_price']
            realized_gain = proceeds - cost_basis
            
            # Update position
            if shares == pos_to_sell['shares']:
                portfolio.pop(pos_index)
            else:
                pos_to_sell['shares'] -= shares
            
            # Update cash and realized gains
            st.session_state[cash_key] += proceeds
            st.session_state[realized_gains_key] += realized_gain
        
        return True, message
    
    # ============= ORDER CONFIRMATION MODAL =============
    @st.dialog("Confirm Order", width="medium")
    def order_confirmation_modal():
        order = st.session_state.pending_order
        if not order:
            return
        
        st.markdown(f"### {order['action']} {order['ticker']}")
        
        # Order details
        st.markdown(f"""
        **Shares:** {order['shares']:.4f}  
        **Estimated Price:** ${order['price']:.2f}  
        **Estimated Total:** ${order['total']:.2f}  
        """)
        
        # Post-trade cash
        post_cash = order['post_cash']
        if post_cash < 0:
            st.error(f"⚠️ **Insufficient Funds**  \nYou need ${abs(post_cash):,.2f} more")
        else:
            st.success(f"**Remaining Cash:** ${post_cash:,.2f}")
        
        # Concentration warning
        if order['post_concentration'] > 0:
            st.info(f"**Post-trade Concentration:** {order['post_concentration']:.1f}% in {order['ticker']}")
            
            # Show personalized warning if risk quiz taken
            risk_tier = st.session_state.user_profile.get('risk_tier', 'unknown')
            if risk_tier != 'unknown':
                _, conc_msg = get_concentration_warning(order['ticker'], order['post_concentration'] / 100, risk_tier)
                if conc_msg:
                    st.warning(conc_msg)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Confirm", use_container_width=True, type="primary", disabled=(post_cash < 0)):
                success, message = execute_trade(
                    order['action'], 
                    order['ticker'], 
                    order['shares'], 
                    order['price'],
                    order['portfolio_type']
                )
                
                if success:
                    # Update concentration flags
                    if order['portfolio_type'] == 'user':
                        update_concentration_flags(st.session_state.portfolio)
                    
                    st.session_state.show_order_modal = False
                    st.session_state.pending_order = None
                    save_user_progress()
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True, type="secondary"):
                st.session_state.show_order_modal = False
                st.session_state.pending_order = None
                st.rerun()
    
    # Show modal if triggered
    if st.session_state.show_order_modal:
        order_confirmation_modal()
    
    # ============= TRADE PANEL COMPONENT =============
    def render_trade_panel(portfolio_type='user'):
        """Render the trade panel for user or founder"""
        is_founder_panel = (portfolio_type == 'founder')
        panel_title = "Trade Panel (Founder)" if is_founder_panel else "Trade Panel (User)"
        
        # Get portfolio data
        if is_founder_panel:
            portfolio = st.session_state.founder_portfolio
            cash = st.session_state.founder_cash
        else:
            portfolio = st.session_state.portfolio
            cash = st.session_state.cash
        
        st.markdown(f"### 🛒 {panel_title}")
        
        # Ticker input with name resolution
        ticker_input = st.text_input(
            "Stock (name or ticker)",
            placeholder="AAPL or Apple",
            key=f"ticker_input_{portfolio_type}"
        ).strip()
        
        if ticker_input:
            # Resolve ticker
            resolved_ticker, company_name = smart_search_ticker(ticker_input)
            
            if resolved_ticker != ticker_input.upper():
                st.caption(f"→ {company_name} ({resolved_ticker})")
            
            ticker = resolved_ticker
            
            # Get current price
            quote = get_quote(ticker)
            if not quote:
                st.error("Invalid ticker")
                return
            
            current_price = quote.get('price', 0)
            st.metric("Current Price", f"${current_price:.2f}")
            
            # Action toggle
            action = st.radio(
                "Action",
                ["Buy", "Sell"],
                horizontal=True,
                key=f"action_{portfolio_type}"
            )
            
            # Input type toggle
            input_mode = st.radio(
                "Input Mode",
                ["Shares", "Dollars"],
                horizontal=True,
                key=f"input_mode_{portfolio_type}"
            )
            
            # Quantity input
            if input_mode == "Shares":
                shares = st.number_input(
                    "Shares",
                    min_value=0.01,
                    value=1.0,
                    step=0.01,
                    key=f"shares_input_{portfolio_type}"
                )
                total_cost = shares * current_price
            else:  # Dollars
                dollars = st.number_input(
                    "Dollars",
                    min_value=1.0,
                    value=1000.0,
                    step=100.0,
                    key=f"dollars_input_{portfolio_type}"
                )
                shares = dollars / current_price
                total_cost = dollars
            
            # Live preview
            st.markdown("---")
            st.markdown("#### 📋 Preview")
            
            if action == "Buy":
                post_cash = cash - total_cost
                
                # Simulate concentration
                sim_portfolio = portfolio.copy()
                existing_pos = None
                for pos in sim_portfolio:
                    if pos['ticker'] == ticker:
                        existing_pos = pos
                        break
                
                if existing_pos:
                    existing_pos['shares'] += shares
                else:
                    sim_portfolio.append({'ticker': ticker, 'shares': shares, 'avg_price': current_price})
                
                sim_weights = compute_portfolio_concentration(sim_portfolio)
                post_concentration = sim_weights.get(ticker, 0) * 100
                
                st.info(f"""
                **Estimated Shares:** {shares:.4f}  
                **Estimated Cost:** ${total_cost:.2f}  
                **Remaining Cash:** ${post_cash:,.2f}  
                **Post-trade {ticker}:** {post_concentration:.1f}% of portfolio
                """)
                
                if post_cash < 0:
                    st.error(f"⚠️ Insufficient funds! Need ${abs(post_cash):,.2f} more")
            
            else:  # Sell
                # Check if position exists
                existing_pos = None
                for pos in portfolio:
                    if pos['ticker'] == ticker:
                        existing_pos = pos
                        break
                
                if not existing_pos:
                    st.error(f"You don't own any {ticker}")
                    return
                
                if shares > existing_pos['shares']:
                    st.error(f"Cannot sell {shares:.4f} shares. You only have {existing_pos['shares']:.4f}")
                    return
                
                proceeds = shares * current_price
                post_cash = cash + proceeds
                
                st.info(f"""
                **Selling Shares:** {shares:.4f}  
                **Estimated Proceeds:** ${proceeds:.2f}  
                **Remaining Cash:** ${post_cash:,.2f}
                """)
            
            # Review Order button
            st.markdown("---")
            
            # Prepare order data
            can_execute = True
            if action == "Buy" and total_cost > cash:
                can_execute = False
            elif action == "Sell" and (not existing_pos or shares > existing_pos['shares']):
                can_execute = False
            
            if st.button(
                "📝 Review Order",
                use_container_width=True,
                type="primary",
                key=f"review_order_{portfolio_type}",
                disabled=not can_execute
            ):
                # Store order data and show modal
                st.session_state.pending_order = {
                    'action': action,
                    'ticker': ticker,
                    'shares': shares,
                    'price': current_price,
                    'total': total_cost if action == "Buy" else proceeds,
                    'post_cash': post_cash,
                    'post_concentration': post_concentration if action == "Buy" else 0,
                    'portfolio_type': portfolio_type
                }
                st.session_state.show_order_modal = True
                st.rerun()
    
    # ============= POSITIONS TABLE COMPONENT =============
    def render_positions_table(portfolio, realized_gains, portfolio_type='user'):
        """Render positions table with realized/unrealized G/L"""
        if not portfolio:
            st.info("No positions yet. Use the trade panel to buy your first stock!")
            return
        
        # Update concentration flags
        update_concentration_flags(portfolio)
        concentration_flags = st.session_state.get('concentration_flags', {})
        
        positions_data = []
        for pos in portfolio:
            quote = get_quote(pos['ticker'])
            if quote:
                current_price = quote.get('price', 0)
                market_value = pos['shares'] * current_price
                cost_basis = pos['shares'] * pos['avg_price']
                unrealized_gain = market_value - cost_basis
                unrealized_gain_pct = (unrealized_gain / cost_basis * 100) if cost_basis > 0 else 0
                
                # Get concentration warning icon
                conc_flag = concentration_flags.get(pos['ticker'], {})
                severity = conc_flag.get('severity', 'none')
                warning_icon = "🚨" if severity == "high" else "⚠️" if severity == "warning" else ""
                
                positions_data.append({
                    '⚠': warning_icon,
                    'Ticker': pos['ticker'],
                    'Shares': f"{pos['shares']:.4f}",
                    'Avg Cost': f"${pos['avg_price']:.2f}",
                    'Price': f"${current_price:.2f}",
                    'Value': f"${market_value:,.2f}",
                    'Unrealized $': f"${unrealized_gain:,.2f}",
                    'Unrealized %': f"{unrealized_gain_pct:+.2f}%"
                })
        
        if positions_data:
            df = pd.DataFrame(positions_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if any(row['⚠'] for row in positions_data):
                st.caption("⚠️ = Concentration warning | 🚨 = High concentration risk")
            
            st.caption(f"**Total Realized G/L:** ${realized_gains:,.2f}")
    
    # ============= SECTION A: YOUR PAPER PORTFOLIO =============
    st.markdown("## 📊 Section A — Your Paper Portfolio")
    
    col_trade, col_chart = st.columns([1, 1])
    
    with col_trade:
        render_trade_panel('user')
    
    with col_chart:
        st.markdown("### 📈 YTD Performance (User)")
        
        # Calculate metrics using real equity calculation
        user_equity, user_ytd_return, user_cash, user_market_value = calculate_portfolio_equity(
            st.session_state.transactions,
            st.session_state.portfolio,
            st.session_state.realized_gains
        )
        
        # KPI card
        col1, col2, col3 = st.columns(3)
        col1.metric("Starting", f"${STARTING_CASH:,.0f}")
        col2.metric("Current", f"${user_equity:,.2f}")
        col3.metric("YTD Return", f"{user_ytd_return:+.2f}%")
        
        # Simple line chart placeholder
        # TODO: Implement actual YTD chart with historical data
        st.caption("📈 Chart: YTD performance tracking coming soon")
    
    # User positions table
    st.markdown("---")
    st.markdown("### 📋 Your Positions")
    render_positions_table(st.session_state.portfolio, st.session_state.realized_gains, 'user')
    
    # Transaction history
    with st.expander("📜 Transaction History", expanded=False):
        if st.session_state.transactions:
            for txn in reversed(st.session_state.transactions[-20:]):
                st.caption(f"{txn['date']} | {txn['type']} {txn['shares']} {txn['ticker']} @ ${txn['price']:.2f}")
        else:
            st.caption("No transactions yet")
    
    st.divider()
    
    # ============= SECTION B: FOUNDER'S PAPER PORTFOLIO =============
    st.markdown("## 👑 Section B — Founder's Paper Portfolio")
    
    if is_founder:
        # Interactive founder panel for owner
        col_trade_f, col_chart_f = st.columns([1, 1])
        
        with col_trade_f:
            render_trade_panel('founder')
        
        with col_chart_f:
            st.markdown("### 📈 YTD Performance (Founder)")
            
            # Calculate metrics using real equity calculation
            founder_equity, founder_ytd_return, founder_cash, founder_market_value = calculate_portfolio_equity(
                st.session_state.founder_transactions,
                st.session_state.founder_portfolio,
                st.session_state.founder_realized_gains
            )
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Starting", f"${STARTING_CASH:,.0f}")
            col2.metric("Current", f"${founder_equity:,.2f}")
            col3.metric("YTD Return", f"{founder_ytd_return:+.2f}%")
            
            st.caption("📈 Chart: YTD performance tracking coming soon")
        
        st.markdown("---")
        st.markdown("### 📋 Founder Positions")
        render_positions_table(st.session_state.founder_portfolio, st.session_state.founder_realized_gains, 'founder')
        
        with st.expander("📜 Founder Transaction History", expanded=False):
            if st.session_state.founder_transactions:
                for txn in reversed(st.session_state.founder_transactions[-20:]):
                    st.caption(f"{txn['date']} | {txn['type']} {txn['shares']} {txn['ticker']} @ ${txn['price']:.2f}")
            else:
                st.caption("No transactions yet")
    
    else:
        # Read-only view for non-founders
        st.info("👑 **Founder portfolio is read-only. Only the founder can trade here.**")
        
        # Show founder portfolio stats
        st.markdown("### 📈 YTD Performance (Founder)")
        
        # Calculate metrics using real equity calculation
        founder_equity, founder_ytd_return, founder_cash, founder_market_value = calculate_portfolio_equity(
            st.session_state.founder_transactions,
            st.session_state.founder_portfolio,
            st.session_state.founder_realized_gains
        )
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Starting", f"${STARTING_CASH:,.0f}")
        col2.metric("Current", f"${founder_equity:,.2f}")
        col3.metric("YTD Return", f"{founder_ytd_return:+.2f}%")
        
        st.markdown("---")
        st.markdown("### 📋 Founder Positions")
        render_positions_table(st.session_state.founder_portfolio, st.session_state.founder_realized_gains, 'founder')
        
        with st.expander("📜 Founder Transaction History", expanded=False):
            if st.session_state.founder_transactions:
                for txn in reversed(st.session_state.founder_transactions[-20:]):
                    st.caption(f"{txn['date']} | {txn['type']} {txn['shares']} {txn['ticker']} @ ${txn['price']:.2f}")
            else:
                st.caption("No transactions yet")
    
    st.divider()
    
    # ============= SECTION C: BENCHMARK & WHO'S WINNING =============
    st.markdown("## 🏆 Section C — Benchmark & Who's Winning")
    
    # SPY benchmark
    st.markdown("### 📊 SPY Benchmark")
    
    # Calculate SPY return (placeholder - would need actual SPY data)
    spy_starting = 50000.0
    spy_current = 52500.0  # Placeholder
    spy_ytd_return = get_ytd_return(spy_current, spy_starting)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("SPY Starting", f"${spy_starting:,.2f}")
    col2.metric("SPY Current", f"${spy_current:,.2f}")
    col3.metric("SPY YTD", f"{spy_ytd_return:+.2f}%")
    
    # Summary
    st.markdown("---")
    st.markdown("### 🏁 Performance Summary")
    
    # Determine leader
    performances = [
        ("User", user_ytd_return),
        ("Founder", get_ytd_return(calculate_portfolio_value(st.session_state.founder_portfolio, st.session_state.founder_cash), 50000.0)),
        ("SPY", spy_ytd_return)
    ]
    leader = max(performances, key=lambda x: x[1])
    
    st.info(f"""
    **YTD Returns:**  
    User: {user_ytd_return:+.2f}%  
    Founder: {performances[1][1]:+.2f}%  
    SPY: {spy_ytd_return:+.2f}%  
    
    **Leader:** {leader[0]} ({leader[1]:+.2f}%)
    """)
    
    st.caption("📊 Overlay chart (User vs Founder vs SPY) coming soon")
    
    # Reset option
    st.divider()
    if st.button("🔄 Reset Your Portfolio", type="secondary"):
        st.session_state.portfolio = []
        st.session_state.cash = 50000.0
        st.session_state.transactions = []
        st.session_state.realized_gains = 0.0
        st.session_state.concentration_flags = {}
        save_user_progress()
        st.success("Portfolio reset! You have $50,000 to start fresh.")
        st.rerun()
elif selected_page == "✅ Portfolio Risk Analyzer":
    st.header("📈 Portfolio Risk Analyzer")
    st.write("Deep risk analysis with AI-powered roasts 😈")
    
    st.markdown("### 📝 Enter Your Holdings")
    num_stocks = st.number_input("How many stocks in your portfolio?", 1, 20, 3)
    
    portfolio = []
    for i in range(num_stocks):
        col1, col2 = st.columns([2, 1])
        with col1:
            ticker_input = st.text_input(f"Stock {i+1} Ticker:", key=f"ticker_{i}", 
                              placeholder="e.g., AAPL")
        with col2:
            allocation = st.number_input(f"% of Portfolio:", 0, 100, 
                                    33 if i < 3 else 0, key=f"alloc_{i}")
        
        if ticker_input and allocation > 0:
            portfolio.append({"ticker": ticker_input.upper(), "allocation": allocation})
    
    if st.button("🔍 Analyze Portfolio Risk", type="primary"):
        if not portfolio:
            st.error("Please add at least one stock!")
        elif sum(p['allocation'] for p in portfolio) != 100:
            st.error(f"Allocations must sum to 100% (currently {sum(p['allocation'] for p in portfolio)}%)")
        else:
            with st.spinner("Analyzing portfolio... preparing roasts... 🔥"):
                portfolio_data = []
                total_risk_score = 0
                all_risk_factors = []
                
                for item in portfolio:
                    quote = get_quote(item['ticker'])
                    profile = get_profile(item['ticker'])
                    ratios_ttm = get_ratios_ttm(item['ticker'])
                    income_df = get_income_statement(item['ticker'], 'annual', 1)
                    balance_df = get_balance_sheet(item['ticker'], 'annual', 1)
                    cash_df = get_cash_flow(item['ticker'], 'annual', 1)
                    
                    if quote:
                        sector = profile.get('sector', 'Unknown') if profile else 'Unknown'
                        
                        pe = get_pe_ratio(item['ticker'], quote, ratios_ttm, income_df)
                        ps = get_ps_ratio(item['ticker'], ratios_ttm)
                        de_ratio = calculate_debt_to_equity(balance_df)
                        quick_ratio = calculate_quick_ratio(balance_df)
                        
                        risk_score, risk_factors = calculate_risk_score(
                            item['ticker'], quote, balance_df, cash_df, sector
                        )
                        
                        weighted_risk = risk_score * (item['allocation'] / 100)
                        total_risk_score += weighted_risk
                        
                        if risk_factors:
                            all_risk_factors.append({
                            "ticker": item['ticker'],
                            "allocation": item['allocation'],
                            "factors": risk_factors
                            })
                        
                        industry_pe = get_industry_benchmark(sector, 'pe')
                        industry_de = get_industry_benchmark(sector, 'debt_to_equity')
                        industry_qr = get_industry_benchmark(sector, 'quick_ratio')
                        
                        portfolio_data.append({
                            "ticker": item['ticker'],
                            "name": quote.get('name', item['ticker']),
                            "allocation": item['allocation'],
                            "sector": sector,
                            "beta": quote.get('beta', 1.0),
                            "pe": pe,
                            "ps": ps,
                            "de_ratio": de_ratio,
                            "quick_ratio": quick_ratio,
                            "marketCap": quote.get('marketCap', 0),
                            "risk_score": risk_score,
                            "industry_pe": industry_pe,
                            "industry_de": industry_de,
                            "industry_qr": industry_qr
                        })
                
                if portfolio_data:
                    df = pd.DataFrame(portfolio_data)
                    
                    weighted_beta = sum(row['beta'] * row['allocation']/100 for _, row in df.iterrows())
                    avg_pe = df[df['pe'] > 0]['pe'].mean() if len(df[df['pe'] > 0]) > 0 else 0
                    avg_ps = df[df['ps'] > 0]['ps'].mean() if len(df[df['ps'] > 0]) > 0 else 0
                    avg_de = df[df['de_ratio'] > 0]['de_ratio'].mean() if len(df[df['de_ratio'] > 0]) > 0 else 0
                    avg_qr = df[df['quick_ratio'] > 0]['quick_ratio'].mean() if len(df[df['quick_ratio'] > 0]) > 0 else 0
                    total_market_cap = sum(row['marketCap'] * row['allocation']/100 for _, row in df.iterrows())
                    
                    st.markdown("### 📊 Portfolio Risk Profile")
                    
                    roast = get_roast_comment(portfolio_data, total_risk_score)
                    st.markdown(f"""
                    <div class="roast-box">
                    {roast}
                    </div>
                    """, unsafe_allow_html=True)
                    
                            
                    if total_risk_score > 70:
                        st.markdown(f"""
                        <div class="risk-warning">
                        <h3>🚨 HIGH RISK PORTFOLIO</h3>
                        <p><strong>Risk Score: {total_risk_score:.0f}/100</strong></p>
                        <p>Your portfolio has significant risk factors. Consider diversifying or reducing positions.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif total_risk_score > 40:
                        st.warning(f"⚠️ **MODERATE-HIGH RISK** - Risk Score: {total_risk_score:.0f}/100")
                    elif total_risk_score > 20:
                        st.info(f"🟡 **MODERATE RISK** - Risk Score: {total_risk_score:.0f}/100")
                    else:
                        st.markdown(f"""
                        <div class="risk-good">
                        <h3>✅ LOW RISK PORTFOLIO</h3>
                        <p><strong>Risk Score: {total_risk_score:.0f}/100</strong></p>
                        <p>Your portfolio has relatively low risk factors.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                            
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Portfolio Beta", f"{weighted_beta:.2f}",
                               help=explain_metric("Beta", weighted_beta))
                    col2.metric("Avg P/E (TTM)", f"{avg_pe:.1f}" if avg_pe > 0 else "N/A",
                               help=explain_metric("P/E Ratio", avg_pe))
                    col3.metric("Avg Debt/Equity", f"{avg_de:.2f}" if avg_de > 0 else "N/A",
                               help=explain_metric("Debt-to-Equity", avg_de))
                    col4.metric("Avg Quick Ratio", f"{avg_qr:.2f}" if avg_qr > 0 else "N/A",
                               help=explain_metric("Quick Ratio", avg_qr))
                    col5.metric("Weighted Mkt Cap", format_number(total_market_cap),
                               help=explain_metric("Market Cap", total_market_cap))
                    
                            
                    if all_risk_factors:
                        st.markdown("### 🚨 Individual Stock Risk Factors")
                        for stock_risk in all_risk_factors:
                            ticker = stock_risk['ticker']
                            allocation = stock_risk['allocation']
                            factors = stock_risk['factors']
                            
                            if factors:
                                with st.expander(f"⚠️ {ticker} ({allocation}% of portfolio) - {len(factors)} risk factor(s)"):
                                    for factor in factors:
                                        st.warning(f"• {factor}")
                    
                            
                    st.markdown("### 📊 Industry Comparison")
                    
                    comparison_data = []
                    for _, row in df.iterrows():
                        comparison_data.append({
                            "Ticker": row['ticker'],
                            "Sector": row['sector'],
                            "P/E": f"{row['pe']:.1f}" if row['pe'] > 0 else "N/A",
                            "Industry P/E": f"{row['industry_pe']:.1f}" if row['industry_pe'] > 0 else "N/A",
                            "D/E": f"{row['de_ratio']:.2f}" if row['de_ratio'] > 0 else "N/A",
                            "Industry D/E": f"{row['industry_de']:.2f}" if row['industry_de'] > 0 else "N/A",
                            "Quick Ratio": f"{row['quick_ratio']:.2f}" if row['quick_ratio'] > 0 else "N/A",
                            "Industry QR": f"{row['industry_qr']:.2f}" if row['industry_qr'] > 0 else "N/A",
                            "Risk Score": f"{row['risk_score']:.0f}/100"
                        })
                    
                    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, height=300)
                    
                            
                    st.markdown("### 📉 Market Crash Scenarios")
                    
                    scenarios = [
                        {"name": "Minor Correction", "drop": -10, "desc": "Normal market volatility"},
                        {"name": "Bear Market", "drop": -20, "desc": "Significant downturn"},
                        {"name": "Market Crash", "drop": -30, "desc": "Severe recession"},
                        {"name": "Black Swan", "drop": -50, "desc": "2008-level crisis"}
                    ]
                    
                    for scenario in scenarios:
                        expected_drop = scenario['drop'] * weighted_beta
                        
                        if avg_de > 2.0:
                            expected_drop *= 1.3
                        elif avg_de > 1.5:
                            expected_drop *= 1.15
                        
                        if abs(expected_drop) > abs(scenario['drop']) * 1.2:
                            risk_level = "🔴 HIGH RISK"
                            color = "error"
                        elif abs(expected_drop) < abs(scenario['drop']) * 0.8:
                            risk_level = "🟢 LOW RISK"
                            color = "success"
                        else:
                            risk_level = "🟡 MODERATE RISK"
                            color = "info"
                        
                        with st.expander(f"{scenario['name']}: Market drops {scenario['drop']}%"):
                            st.write(f"**{scenario['desc']}**")
                            st.metric("Your Expected Loss", f"{expected_drop:.1f}%")
                            
                            if avg_de > 2.0:
                                st.warning("⚠️ High debt levels may amplify losses during crashes")
                            
                            if color == "error":
                                st.error(f"{risk_level} - Portfolio would likely drop MORE than market")
                            elif color == "success":
                                st.success(f"{risk_level} - Portfolio would likely drop LESS than market")
                            else:
                                st.info(f"{risk_level} - Portfolio would track market closely")
                    
                            
                    st.markdown("### 🎯 Diversification Analysis")
                    
                    if len(portfolio_data) < 5:
                        st.warning(f"⚠️ Only {len(portfolio_data)} stocks. Add more for diversification!")
                    elif len(portfolio_data) < 10:
                        st.info(f"✅ {len(portfolio_data)} stocks - decent diversification")
                    else:
                        st.success(f"🎉 {len(portfolio_data)} stocks - well diversified!")
                    
                    max_allocation = max(p['allocation'] for p in portfolio)
                    if max_allocation > 40:
                        st.error(f"🚨 {max_allocation}% in one stock is too concentrated!")
                    elif max_allocation > 25:
                        st.warning(f"⚠️ {max_allocation}% in one stock is somewhat concentrated")
                    else:
                        st.success(f"✅ Largest position: {max_allocation}% - good balance")
                    
                    sector_counts = df['sector'].value_counts()
                    if len(sector_counts) == 1:
                        st.error(f"🚨 All stocks in one sector - High concentration risk!")
                    elif len(sector_counts) < 3:
                        st.warning(f"⚠️ Concentrated in {len(sector_counts)} sector(s)")
                    else:
                        st.success(f"✅ Spread across {len(sector_counts)} sectors")
                    
                            
                    st.markdown("### 📊 Detailed Breakdown")
                    detail_df = df[['ticker', 'name', 'allocation', 'sector', 'beta', 'pe', 'de_ratio', 'quick_ratio', 'risk_score']].copy()
                    detail_df.columns = ['Ticker', 'Company', 'Allocation %', 'Sector', 'Beta', 'P/E', 'Debt/Equity', 'Quick Ratio', 'Risk Score']
                    st.dataframe(detail_df, use_container_width=True)
                    
                            
                    st.markdown("### 💡 Recommendations")
                    
                    recommendations = []
                    
                    if weighted_beta > 1.3:
                        recommendations.append("🎯 HIGH BETA - Add defensive stocks (utilities, consumer staples)")
                    elif weighted_beta < 0.7:
                        recommendations.append("🎯 LOW BETA - Consider growth stocks for higher returns")
                    
                    if avg_de > 2.0:
                        recommendations.append("🚨 High debt-to-equity. Reduce leveraged companies")
                    
                    if avg_qr < 1.0:
                        recommendations.append("⚠️ Low liquidity. Some companies may struggle with debts")
                    
                    if total_risk_score > 60:
                        recommendations.append("🚨 HIGH risk score. Rebalance towards stable companies")
                    
                    if len(sector_counts) < 3:
                        recommendations.append("📊 Add more sector diversification")
                    
                    if recommendations:
                        for rec in recommendations:
                            st.info(rec)
                    else:
                        st.success("✅ Portfolio looks well-balanced!")

# ============= FOUNDER TRACK RECORD (PUBLIC READ-ONLY) =============
elif selected_page == "📜 Founder Track Record":
    st.header("📜 Founder Track Record")
    st.caption("*Public, read-only view of the founder's paper trading performance.*")
    
    # ============= HELPER: GET FOUNDER DATA =============
    def get_founder_data():
        """Get founder portfolio data from session state"""
        if 'founder_portfolio' not in st.session_state:
            st.session_state.founder_portfolio = []
        if 'founder_transactions' not in st.session_state:
            st.session_state.founder_transactions = []
        if 'founder_realized_gains' not in st.session_state:
            st.session_state.founder_realized_gains = 0.0
        
        return (
            st.session_state.founder_portfolio,
            st.session_state.founder_transactions,
            st.session_state.founder_realized_gains
        )
    
    def calculate_track_record_metrics(transactions, portfolio, realized_gains):
        """Calculate all track record metrics"""
        # Calculate portfolio equity using same logic as Paper Portfolio
        cash = STARTING_CASH
        
        # Process all transactions to calculate current cash
        for txn in transactions:
            if txn['type'] == 'BUY':
                cash -= txn['total']  # Subtract cost
            elif txn['type'] == 'SELL':
                cash += txn['total']  # Add proceeds
        
        # Calculate market value of current positions
        market_value = 0.0
        unrealized_pl = 0.0
        
        for pos in portfolio:
            quote = get_quote(pos['ticker'])
            if quote:
                current_price = quote.get('price', 0)
                avg_price = pos.get('avg_price', 0)
                shares = pos.get('shares', 0)
                
                position_market_value = shares * current_price
                position_unrealized_pl = (current_price - avg_price) * shares
                
                market_value += position_market_value
                unrealized_pl += position_unrealized_pl
        
        # Total equity = cash + market value
        equity = cash + market_value
        
        # Total P/L = current equity - starting cash
        total_pl = equity - STARTING_CASH
        
        # YTD return percentage
        ytd_return_pct = (total_pl / STARTING_CASH * 100) if STARTING_CASH > 0 else 0.0
        
        # Handle empty portfolio case
        if not transactions:
            equity = STARTING_CASH
            ytd_return_pct = 0.0
            unrealized_pl = 0.0
        
        # Total P/L = realized + unrealized
        total_pl = realized_gains + unrealized_pl
        
        # Inception date = first transaction date
        inception_date = "—"
        if transactions:
            inception_date = transactions[0].get('date', '—')
        
        return {
            'equity': equity,
            'ytd_return': ytd_return_pct,
            'cash': cash,
            'market_value': market_value,
            'realized_pl': realized_gains,
            'unrealized_pl': unrealized_pl,
            'total_pl': total_pl,
            'inception_date': inception_date
        }
    
    # ============= GET DATA =============
    portfolio, transactions, realized_gains = get_founder_data()
    metrics = calculate_track_record_metrics(transactions, portfolio, realized_gains)
    
    # ============= SECTION A: HEADER SUMMARY (KPI CARDS) =============
    st.markdown("## 📊 Performance Summary")
    
    # Row 1: Core metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Inception Date", metrics['inception_date'])
    with col2:
        st.metric("Starting Capital", f"${STARTING_CASH:,.0f}")
    with col3:
        st.metric("Current Equity", f"${metrics['equity']:,.2f}")
    with col4:
        st.metric("Total Return", f"{metrics['ytd_return']:+.2f}%")
    
    # Row 2: P/L breakdown
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Realized P/L", f"${metrics['realized_pl']:,.2f}")
    with col6:
        st.metric("Unrealized P/L", f"${metrics['unrealized_pl']:,.2f}")
    with col7:
        st.metric("Total P/L", f"${metrics['total_pl']:,.2f}")
    with col8:
        st.metric("Cash", f"${metrics['cash']:,.2f}")
    
    st.markdown("---")
    
    # ============= SECTION B: CURRENT HOLDINGS =============
    st.markdown("## 📋 Current Holdings")
    
    if portfolio:
        # Calculate total portfolio value for weight calculation
        total_portfolio_value = metrics['market_value']
        
        holdings_data = []
        price_fetch_failures = []
        
        for pos in portfolio:
            ticker = pos['ticker']
            shares = pos['shares']
            avg_cost = pos['avg_price']
            
            # Get live price
            quote = get_quote(ticker)
            if quote:
                live_price = quote.get('price', 0)
                market_value = shares * live_price
                unrealized_pl = (live_price - avg_cost) * shares
                unrealized_pl_pct = ((live_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0
                portfolio_weight = (market_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
                
                holdings_data.append({
                    'Symbol': ticker,
                    'Shares': f"{shares:.4f}",
                    'Avg Cost': f"${avg_cost:.2f}",
                    'Live Price': f"${live_price:.2f}",
                    'Market Value': market_value,
                    'Market Value (formatted)': f"${market_value:,.2f}",
                    'Unrealized P/L': f"${unrealized_pl:,.2f} ({unrealized_pl_pct:+.2f}%)",
                    'Weight': f"{portfolio_weight:.2f}%"
                })
            else:
                # Price fetch failed
                price_fetch_failures.append(ticker)
                holdings_data.append({
                    'Symbol': ticker,
                    'Shares': f"{shares:.4f}",
                    'Avg Cost': f"${avg_cost:.2f}",
                    'Live Price': "—",
                    'Market Value': 0,
                    'Market Value (formatted)': "—",
                    'Unrealized P/L': "—",
                    'Weight': "—"
                })
        
        # Sort by market value descending
        holdings_data.sort(key=lambda x: x['Market Value'], reverse=True)
        
        # Remove the sort key before display
        for holding in holdings_data:
            del holding['Market Value']
        
        # Display table
        df_holdings = pd.DataFrame(holdings_data)
        st.dataframe(df_holdings, use_container_width=True, hide_index=True)
        
        # Warning for price fetch failures
        if price_fetch_failures:
            st.warning(f"⚠️ Could not fetch live prices for: {', '.join(price_fetch_failures)}")
    else:
        st.info("No holdings yet.")
    
    st.markdown("---")
    
    # ============= SECTION C: PUBLIC TRADE LEDGER =============
    st.markdown("## 📜 All Founder Trades")
    
    # CSV Export preparation
    csv_data = []
    for txn in transactions:
        # Calculate realized P/L for CSV (numeric, no currency symbols)
        realized_pl_value = 0.0
        if txn['type'] == 'SELL':
            # For now, use the total proceeds as realized P/L
            # This is approximate without tracking detailed cost basis per trade
            realized_pl_value = txn['total']
        
        csv_data.append({
            'timestamp': txn['date'],
            'symbol': txn['ticker'],
            'side': txn['type'],
            'quantity': txn['shares'],
            'price': txn['price'],
            'fees': 0.00,
            'notional': txn['total'],
            'realized_pl': realized_pl_value,
            'note': ''
        })
    
    # Create CSV DataFrame
    if csv_data:
        df_csv = pd.DataFrame(csv_data)
    else:
        # Empty DataFrame with headers only
        df_csv = pd.DataFrame(columns=[
            'timestamp', 'symbol', 'side', 'quantity', 'price', 
            'fees', 'notional', 'realized_pl', 'note'
        ])
    
    # Generate CSV in memory
    csv_string = df_csv.to_csv(index=False)
    csv_filename = f"founder_trades_{datetime.now().strftime('%Y-%m-%d')}.csv"
    
    # Download button
    st.download_button(
        label="📥 Download CSV",
        data=csv_string,
        file_name=csv_filename,
        mime="text/csv",
        help="Download complete trade history as CSV"
    )
    
    st.markdown("")  # Small spacing
    
    if transactions:
        # Build ledger table
        ledger_data = []
        
        for txn in transactions:
            # Calculate realized P/L for SELL transactions
            realized_pl_display = "—"
            if txn['type'] == 'SELL':
                # For display purposes, we can show the profit on this specific sell
                # Note: This is approximate since we're not tracking per-trade P/L
                sell_price = txn['price']
                shares_sold = txn['shares']
                total_proceeds = txn['total']
                
                # Try to find avg cost from portfolio history
                # For now, just show the total proceeds
                realized_pl_display = f"${total_proceeds:,.2f}"
            
            ledger_data.append({
                'Date/Time': txn['date'],
                'Symbol': txn['ticker'],
                'Side': txn['type'],
                'Qty': f"{txn['shares']:.4f}",
                'Price': f"${txn['price']:.2f}",
                'Fees': "$0.00",  # Add fees column (currently no fees tracked)
                'Notional': f"${txn['total']:,.2f}",
                'Realized P/L': realized_pl_display,
                'Note': "—"
            })
        
        # Display oldest to newest (or reverse for newest first)
        df_ledger = pd.DataFrame(ledger_data)
        st.dataframe(df_ledger, use_container_width=True, hide_index=True)
        
        # Last updated timestamp
        st.caption(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M PT')}*")
    else:
        st.info("No trades yet.")
    
    st.markdown("---")
    
    # ============= SECTION D: DISCLOSURE =============
    st.markdown("## ⚠️ Disclosure")
    
    with st.expander("Important Information", expanded=False):
        st.markdown("""
        **Paper Trading Disclaimer**
        
        - This is a **paper portfolio** for educational and demonstration purposes only.
        - Prices are sourced from public market data and may not reflect exact execution prices or fills.
        - All trades are timestamped and **recorded as immutable entries** once posted.
        - Past performance does not guarantee future results.
        - This is **not financial advice**. Do your own research before making investment decisions.
        
        **Data Sources**
        - Live prices: Financial Modeling Prep (FMP) API
        - Historical data: FMP Premium
        - Timezone: Pacific Time (PT)
        """)
    
    # ============= OPTIONAL: SHARE LINK =============
    st.markdown("### 🔗 Share This Track Record")
    st.code("https://your-app-url.com/?page=founder-track-record", language="text")
    st.caption("*Share this URL to give others read-only access to the founder's track record.*")


# ============= FOOTER =============
st.divider()
st.caption("💡 Investing Made Simple | FMP Premium | Real-time data")
st.caption("⚠️ Educational purposes only. Not financial advice.")
