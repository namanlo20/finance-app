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

# API Keys - Use environment variables (set these in Render dashboard)
# FMP_API_KEY: Your Financial Modeling Prep API key
# PERPLEXITY_API_KEY: Your Perplexity API key for AI risk analysis
FMP_API_KEY = os.environ.get("FMP_API_KEY", "")
BASE_URL = "https://financialmodelingprep.com/stable"

# AI Configuration - Perplexity API for risk analysis
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
USE_AI_ANALYSIS = bool(PERPLEXITY_API_KEY)

st.set_page_config(page_title="Investing Made Simple", layout="wide", page_icon="💰")

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
    
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; }
    a { color: #00D9FF !important; }
    
    .stMetric { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; }
    .stMetric label, .stMetric [data-testid="stMetricValue"], .stMetric [data-testid="stMetricDelta"] {
        color: #FFFFFF !important;
    }
    
    /* Dataframe/Table text */
    .stDataFrame, .dataframe, table, tr, td, th { color: #FFFFFF !important; }
    
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
    if metric_name not in METRIC_EXPLANATIONS:
        return ""
    
    exp = METRIC_EXPLANATIONS[metric_name]
    explanation = f"**{exp['short']}**\n\n{exp['explanation']}\n\n✅ {exp['good']}"
    
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
    url = f"https://financialmodelingprep.com/stable/price-target-consensus?symbol={ticker}&apikey={FMP_API_KEY}"
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

# ============= FOUR SCENARIOS INVESTMENT CALCULATOR =============
@st.cache_data(ttl=3600)
def get_historical_adjusted_prices(ticker, years=10):
    """Get historical adjusted close prices for accurate return calculations including dividends"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={FMP_API_KEY}"
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

# ============= SIGN UP POPUP =============
def show_signup_popup():
    """Show sign up popup when triggered - HTML overlay with Streamlit form"""
    if st.session_state.show_signup_popup:
        # Check if popup was closed via X button
        close_param = st.query_params.get("close_signup")
        if isinstance(close_param, (list, tuple)):
            close_param = close_param[0] if close_param else None
        
        if close_param == "1":
            st.session_state.show_signup_popup = False
            if "close_signup" in st.query_params:
                del st.query_params["close_signup"]
            st.rerun()
        
        # Create centered popup container
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Popup styling
            st.markdown('''
            <style>
            .signup-popup-container {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border: 2px solid #FF4444;
                border-radius: 20px;
                padding: 40px;
                margin-top: 100px;
                position: relative;
            }
            </style>
            ''', unsafe_allow_html=True)
            
            st.markdown('<div class="signup-popup-container">', unsafe_allow_html=True)
            
            # Close button form
            st.markdown('''
            <form method="get" style="position: absolute; top: 15px; right: 15px; margin: 0; padding: 0;">
                <button type="submit" name="close_signup" value="1" 
                        style="background: transparent; border: 2px solid #FF4444; color: #FF4444;
                        font-size: 20px; width: 35px; height: 35px; border-radius: 50%;
                        cursor: pointer; transition: all 0.3s ease;">×</button>
            </form>
            ''', unsafe_allow_html=True)
            
            st.markdown("<h2 style='color: #FF4444; text-align: center; margin-bottom: 10px;'>📝 Create Your Account</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #FFFFFF; text-align: center; margin-bottom: 20px;'>Join Investing Made Simple today!</p>", unsafe_allow_html=True)
            
            # Streamlit form
            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email Address", placeholder="john@example.com")
                phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
                age = st.number_input("Age", min_value=18, max_value=120, value=25)
                password = st.text_input("Create Password", type="password", placeholder="Enter a strong password")
                password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
                
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if submitted:
                    # Validation
                    if not all([name, email, phone, password, password_confirm]):
                        st.error("❌ Please fill in all fields")
                    elif password != password_confirm:
                        st.error("❌ Passwords don't match")
                    elif len(password) < 8:
                        st.error("❌ Password must be at least 8 characters")
                    elif "@" not in email or "." not in email:
                        st.error("❌ Please enter a valid email address")
                    else:
                        # Sign up with Supabase
                        if SUPABASE_ENABLED:
                            try:
                                # Create user with Supabase Auth
                                response = supabase.auth.sign_up({
                                    "email": email,
                                    "password": password,
                                    "options": {
                                        "data": {
                                            "name": name,
                                            "phone": phone,
                                            "age": age
                                        }
                                    }
                                })
                                
                                if response.user:
                                    st.success("✅ Account created successfully! Please check your email to verify.")
                                    st.balloons()
                                    st.session_state.show_signup_popup = False
                                    st.rerun()
                                else:
                                    st.error("❌ Error creating account. Please try again.")
                            except Exception as e:
                                error_msg = str(e)
                                if "already registered" in error_msg.lower():
                                    st.error("❌ This email is already registered. Please sign in instead.")
                                else:
                                    st.error(f"❌ Error: {error_msg}")
                        else:
                            st.error("❌ Authentication service not available. Please contact support.")
            
            st.markdown('</div>', unsafe_allow_html=True)


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
def render_progress_bar(current_step, total_steps, section_name):
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
    
    if progress >= 100:
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

# ============= STATE =============
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "GOOGL"

if 'years_of_history' not in st.session_state:
    st.session_state.years_of_history = 5

if 'homepage_stock1' not in st.session_state:
    st.session_state.homepage_stock1 = "GOOGL"

if 'homepage_stock2' not in st.session_state:
    st.session_state.homepage_stock2 = "AMC"

# ============= SUPABASE CONFIGURATION =============
# Read from environment variables for security (set in Render dashboard)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://gtrtubywtlexgekfqill.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd0cnR1Ynl3dGxleGdla2ZxaWxsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU3ODIzMjIsImV4cCI6MjA1MTM1ODMyMn0.ZziAh5dfith28xppSOv8_g_MOaJAgZQ")

# Initialize Supabase client
try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_ENABLED = True
except ImportError:
    SUPABASE_ENABLED = False
    st.warning("⚠️ Supabase not installed. Run: pip install supabase --break-system-packages")

# ============= SIGN UP POPUP STATE =============
if 'show_signup_popup' not in st.session_state:
    st.session_state.show_signup_popup = False

# ============= TOP NAVIGATION BUTTONS =============
# Initialize button click states
if 'signup_clicked' not in st.session_state:
    st.session_state.signup_clicked = False
if 'vip_clicked' not in st.session_state:
    st.session_state.vip_clicked = False

# Check if frozen buttons were clicked via query params
signup_param = st.query_params.get("signup_clicked")
if isinstance(signup_param, (list, tuple)):
    signup_param = signup_param[0] if signup_param else None
if signup_param == "1":
    st.session_state.show_signup_popup = True
    if "signup_clicked" in st.query_params:
        del st.query_params["signup_clicked"]
    st.rerun()

vip_param = st.query_params.get("vip_clicked")
if isinstance(vip_param, (list, tuple)):
    vip_param = vip_param[0] if vip_param else None
if vip_param == "1":
    st.session_state.selected_page = "👑 Become a VIP"
    if "vip_clicked" in st.query_params:
        del st.query_params["vip_clicked"]
    st.rerun()

# FROZEN TOP BAR
st.markdown(f"""
<div style="position: fixed; top: 0; right: 0; left: 0; z-index: 9999999; 
            background: {'#000000' if st.session_state.theme == 'dark' else '#FFFFFF'}; 
            padding: 10px 20px; display: flex; justify-content: flex-end; gap: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
    <button onclick="window.location.href='?signup_clicked=1'" 
            style="background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%); 
            color: white; padding: 10px 24px; border-radius: 8px; border: none;
            font-weight: bold; cursor: pointer;">📝 Sign Up</button>
    <button onclick="alert('Sign In coming soon!')" 
            style="background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%); 
            color: white; padding: 10px 24px; border-radius: 8px; border: none;
            font-weight: bold; cursor: pointer;">🔐 Sign In</button>
    <button onclick="window.location.href='?vip_clicked=1'" 
            style="background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%); 
            color: white; padding: 10px 24px; border-radius: 8px; border: none;
            font-weight: bold; cursor: pointer;">👑 Become a VIP</button>
</div>
""", unsafe_allow_html=True)

# Add spacing
st.markdown("<div style='margin-bottom: 80px;'></div>", unsafe_allow_html=True)

# ============= LIVE TICKER BAR =============
render_live_ticker_bar()

# ============= WELCOME POPUP FOR FIRST-TIME USERS =============
show_welcome_popup()

# ============= SIGN UP POPUP =============
show_signup_popup()

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
            "📈 Financial Ratios",
            "📰 Market Intelligence",
            "🌍 Sector Explorer"
        ]
        for tool in analysis_tools:
            if st.button(tool, key=f"btn_{tool}", use_container_width=True):
                st.session_state.selected_page = tool
                st.rerun()
    
    # 3. THE ACTION GROUP
    with st.expander("### 3. 🎯 The Action Group", expanded=False):
        st.caption("Track your progress")
        action_tools = [
            "📋 Investment Checklist",
            "💼 Paper Portfolio",
            "👤 Naman's Portfolio"
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
    
    # Calculate a simple Fear & Greed proxy based on S&P 500 momentum
    try:
        spy_data = get_historical_price("SPY", 1)
        if not spy_data.empty and 'price' in spy_data.columns and len(spy_data) >= 20:
            spy_data = spy_data.sort_values('date')
            current_price = spy_data['price'].iloc[-1]
            price_20d_ago = spy_data['price'].iloc[-20] if len(spy_data) >= 20 else spy_data['price'].iloc[0]
            price_50d_ago = spy_data['price'].iloc[-50] if len(spy_data) >= 50 else spy_data['price'].iloc[0]
            
            # Calculate momentum (20-day return)
            momentum_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
            
            # Map momentum to Fear/Greed scale (0-100)
            if momentum_20d <= -10:
                sentiment_score = max(0, 20 + momentum_20d)
                sentiment_label = "Extreme Fear"
                sentiment_color = "#FF0000"
            elif momentum_20d <= -5:
                sentiment_score = 20 + (momentum_20d + 10) * 4
                sentiment_label = "Fear"
                sentiment_color = "#FF6B6B"
            elif momentum_20d <= 5:
                sentiment_score = 40 + (momentum_20d + 5) * 2
                sentiment_label = "Neutral"
                sentiment_color = "#FFD700"
            elif momentum_20d <= 10:
                sentiment_score = 60 + (momentum_20d - 5) * 4
                sentiment_label = "Greed"
                sentiment_color = "#90EE90"
            else:
                sentiment_score = min(100, 80 + (momentum_20d - 10) * 2)
                sentiment_label = "Extreme Greed"
                sentiment_color = "#00C853"
            
            # Display gauge
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                <div style="font-size: 2em; font-weight: bold; color: {sentiment_color};">{sentiment_score:.0f}</div>
                <div style="font-size: 1.2em; color: {sentiment_color};">{sentiment_label}</div>
                <div style="font-size: 0.8em; margin-top: 5px;">S&P 500 20-day: {momentum_20d:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("Based on S&P 500 momentum. Not financial advice.")
        else:
            st.info("Market data loading...")
    except Exception as e:
        st.caption("Market sentiment unavailable")
    
    st.markdown("---")
    
    if 'analysis_view' not in st.session_state:
        st.session_state.analysis_view = "🌟 The Big Picture"
    
    
    # ============= TOGGLE THEME AT BOTTOM OF SIDEBAR =============
    st.markdown("---")
    if st.button("🌓 Toggle Theme", key="sidebar_theme_toggle", use_container_width=True):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

# ============= PAGE CONTENT =============

# ============= HOMEPAGE: START HERE =============
if selected_page == "🏠 Start Here":
    # Progress Bar for Start Here page
    if 'start_here_progress' not in st.session_state:
        st.session_state.start_here_progress = 0
    
    # Calculate progress based on sections viewed
    progress_items = ['viewed_narrative', 'viewed_comparison', 'viewed_truth_meter', 'viewed_next_steps']
    completed = sum(1 for item in progress_items if st.session_state.get(item, False))
    total_steps = len(progress_items)
    
    # Only show confetti once per session
    if 'start_here_confetti_shown' not in st.session_state:
        st.session_state.start_here_confetti_shown = False
    
    render_progress_bar(completed, total_steps, "Start Here Journey")
    
    # Mark narrative as viewed
    st.session_state.viewed_narrative = True
    
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
    st.markdown("### 🎯 Ready to discover your investor profile?")
    st.markdown("Take our quick quiz to find stocks that match your risk tolerance.")
    
    if st.button("🚀 Take the Risk Quiz →", type="primary", use_container_width=True):
        st.session_state.selected_page = "🧠 Risk Quiz"
        st.rerun()
    
    st.markdown("---")
    st.caption("💡 **Tip:** Use the Timeline picker in the sidebar to see how these metrics change over different time periods!")

elif selected_page == "📚 Finance 101":
    st.header("📚 Finance 101")
    st.write("Learn key financial terms")
    
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
    st.markdown("**Discover your investor profile and get personalized stock suggestions!**")
    
    st.info("💡 Answer these questions to understand your risk tolerance and investment style. You'll get 1-2 FREE stock recommendations based on your profile!")
    
    # Initialize session state for quiz
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    
    with st.form("risk_quiz_form"):
        st.markdown("### 📊 Your Investment Profile")
        
        # Question 1: Investment Goal
        q1 = st.radio(
            "1. What's your primary investment goal?",
            ["Preserve capital (safety first)", 
             "Generate steady income (dividends/interest)",
             "Balanced growth and income",
             "Aggressive growth (maximize returns)",
             "Speculative gains (high risk, high reward)"]
        )
        
        # Question 2: Time Horizon
        q2 = st.radio(
            "2. How long do you plan to hold investments?",
            ["Less than 1 year",
             "1-3 years",
             "3-5 years", 
             "5-10 years",
             "10+ years (long-term)"]
        )
        
        # Question 3: Market Drop Reaction
        q3 = st.radio(
            "3. If your portfolio dropped 20% in a month, you would:",
            ["Sell everything immediately (too stressful)",
             "Sell some to reduce risk",
             "Hold and wait for recovery",
             "Buy more (it's on sale!)",
             "Go all-in with more money"]
        )
        
        # Question 4: Risk Comfort
        q4 = st.radio(
            "4. Maximum portfolio loss you can tolerate in a year:",
            ["0-5% (very low risk)",
             "5-10% (low risk)",
             "10-20% (moderate risk)",
             "20-30% (high risk)",
             "30%+ (very high risk)"]
        )
        
        # Question 5: Investment Knowledge
        q5 = st.radio(
            "5. Your investment knowledge level:",
            ["Beginner (just starting)",
             "Basic (understand stocks/bonds)",
             "Intermediate (can read financial statements)",
             "Advanced (active trader)",
             "Expert (professional level)"]
        )
        
        # Question 6: Income Stability
        q6 = st.radio(
            "6. Your income situation:",
            ["Unstable or uncertain",
             "Stable but limited",
             "Stable with some savings",
             "Very stable with good savings",
             "Multiple income streams + significant savings"]
        )
        
        # Question 7: Age
        q7 = st.radio(
            "7. Your age / investment timeline:",
            ["Under 25 (40+ years to retirement)",
             "25-35 (30-40 years to retirement)",
             "35-50 (15-30 years to retirement)",
             "50-60 (5-15 years to retirement)",
             "60+ (in or near retirement)"]
        )
        
        # Question 8: Emergency Fund
        q8 = st.radio(
            "8. Do you have an emergency fund (3-6 months expenses)?",
            ["No emergency fund",
             "1-2 months saved",
             "3-6 months saved",
             "6-12 months saved",
             "12+ months saved"]
        )
        
        # Question 9: Investment Goal
        q9 = st.radio(
            "9. Your primary investment goal:",
            ["Short-term profit (< 1 year)",
             "Save for major purchase (house, car)",
             "Build wealth over time",
             "Retirement savings",
             "Generate passive income (dividends)"]
        )
        
        # Question 10: Sector Preference
        q10 = st.radio(
            "10. Preferred investment style:",
            ["Individual stocks only",
             "Mix of stocks and ETFs",
             "Mostly ETFs for diversification",
             "Index funds (S&P 500, Total Market)",
             "Bonds and treasuries for safety"]
        )
        
        submitted = st.form_submit_button("🎯 Get My Results & Stock Picks!", use_container_width=True)
        
        if submitted:
            st.session_state.quiz_submitted = True
            
            # Calculate risk score
            scores = {
                q1: [0, 1, 2, 3, 4],
                q2: [0, 1, 2, 3, 4],
                q3: [0, 1, 2, 3, 4],
                q4: [0, 1, 2, 3, 4],
                q5: [0, 1, 2, 3, 4],
                q6: [0, 1, 2, 3, 4],
                q7: [4, 3, 2, 1, 0],  # Younger = more risk capacity
                q8: [0, 1, 2, 3, 4],  # More savings = more risk capacity
                q9: [0, 1, 2, 3, 4],  # Different goals have different risk needs
                q10: [4, 3, 2, 1, 0]  # Stocks = higher risk, bonds = lower
            }
            
            risk_score = sum([scores[q][i] for q, options in [(q1, q1), (q2, q2), (q3, q3), (q4, q4), (q5, q5), (q6, q6)] 
                            for i, opt in enumerate([
                            ["Preserve capital (safety first)", "Generate steady income (dividends/interest)", "Balanced growth and income", "Aggressive growth (maximize returns)", "Speculative gains (high risk, high reward)"],
                            ["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "10+ years (long-term)"],
                            ["Sell everything immediately (too stressful)", "Sell some to reduce risk", "Hold and wait for recovery", "Buy more (it's on sale!)", "Go all-in with more money"],
                            ["0-5% (very low risk)", "5-10% (low risk)", "10-20% (moderate risk)", "20-30% (high risk)", "30%+ (very high risk)"],
                            ["Beginner (just starting)", "Basic (understand stocks/bonds)", "Intermediate (can read financial statements)", "Advanced (active trader)", "Expert (professional level)"],
                            ["Unstable or uncertain", "Stable but limited", "Stable with some savings", "Very stable with good savings", "Multiple income streams + significant savings"]
                            ]) if options[i] == q])
    
    if st.session_state.quiz_submitted:
        st.markdown("---")
        st.markdown("## 🎯 Your Results")
        st.caption("⚠️ Educational purposes only. Not personalized financial advice.")
        
        # Determine risk profile
        if risk_score <= 10:
            profile = "Conservative"
            color = "🟢"
            description = "You prefer safety and stability. Focus on dividend stocks, bonds, and blue-chip companies."
            stocks = [
                ("JNJ", "Johnson & Johnson", "We chose this because it's a stable 'Blue Chip' company. JNJ has paid dividends for 60+ consecutive years and sells essential healthcare products that people need regardless of the economy. Perfect for investors who prioritize safety over growth."),
                ("PG", "Procter & Gamble", "We chose this because it sells everyday essentials (Tide, Pampers, Gillette) that people buy in good times and bad. This 'recession-resistant' business model means steady profits even during market downturns - ideal for conservative investors.")
            ]
        elif risk_score <= 20:
            profile = "Moderate"
            color = "🟡"
            description = "You want balanced growth with manageable risk. Mix of stable companies and growth stocks."
            stocks = [
                ("MSFT", "Microsoft", "We chose this because it combines growth potential with stability. Microsoft dominates enterprise software (Office, Azure cloud), pays growing dividends, and has a fortress balance sheet. It offers upside while being less volatile than pure growth stocks."),
                ("V", "Visa", "We chose this because it profits from every card swipe without taking credit risk (banks do). As digital payments grow globally, Visa benefits from a 'toll booth' business model - consistent growth with lower risk than most tech stocks.")
            ]
        elif risk_score <= 30:
            profile = "Growth-Oriented"
            color = "🟠"
            description = "You're comfortable with volatility for higher returns. Focus on growth stocks and emerging sectors."
            stocks = [
                ("NVDA", "NVIDIA", "We chose this because you can handle volatility for higher returns. NVIDIA dominates AI chips - the 'picks and shovels' of the AI gold rush. High growth potential but expect 30-50% swings. Only for investors comfortable with roller coaster rides."),
                ("GOOGL", "Alphabet", "We chose this because it dominates search (90% market share), YouTube, and is a major cloud player. Strong cash generation funds AI investments. More stable than pure growth plays but still offers significant upside for growth-oriented investors.")
            ]
        else:
            profile = "Aggressive"
            color = "🔴"
            description = "You're seeking maximum returns and can handle high volatility. High-growth and speculative plays."
            stocks = [
                ("TSLA", "Tesla", "We chose this because you're seeking maximum returns and can handle extreme volatility. Tesla is a high-conviction bet on EVs, energy storage, and AI robotics. Can double or halve in a year - only for investors with strong stomachs and long time horizons."),
                ("COIN", "Coinbase", "We chose this because you want crypto exposure through a regulated company. Coinbase profits when crypto trading volume is high. Extremely volatile - can move 10%+ in a day. Only for aggressive investors who understand they could lose significant capital.")
            ]
        
        # Display profile
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Your Risk Profile", f"{color} {profile}", f"Score: {risk_score}/40")
        with col2:
            st.info(description)
        
        st.markdown("---")
        st.markdown("### 🎁 Your FREE Stock Recommendations")
        st.warning("⚠️ These are educational examples based on your risk profile, NOT personalized investment recommendations. Always do your own research and consult a financial advisor.")
        
        for ticker, name, reason in stocks:
            with st.expander(f"✨ {ticker} - {name}", expanded=True):
                st.markdown(f"**Why this fits your profile:**  \n{reason}")
                
                # Quick stats
                try:
                    quote = get_quote(ticker)
                    if quote:
                        price = quote.get('price', 0)
                        change_pct = quote.get('changesPercentage', 0)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Price", f"${price:.2f}")
                        col2.metric("Change", f"{change_pct:+.2f}%")
                        
                        # Get PE ratio
                        income_df = get_income_statement(ticker, 'annual', 1)
                        if not income_df.empty and 'eps' in income_df.columns:
                            eps = income_df['eps'].iloc[-1]
                            if eps > 0:
                                pe = price / eps
                            col3.metric("P/E Ratio", f"{pe:.1f}")
                        
                        st.markdown(f"[📊 View Full Analysis](/?ticker={ticker})")
                except:
                    st.markdown(f"[📊 Analyze {ticker}](/?ticker={ticker})")
        
        
        
        st.markdown("---")
        st.markdown("### 📦 Recommended ETFs for Your Profile")
        st.info("⚠️ Educational suggestions only. ETFs provide instant diversification. Not personalized advice.")
        
        # ETF recommendations based on profile
        if risk_score <= 10:
            etfs = [
                ("BND", "Vanguard Total Bond Market", "Safe bonds with ~4-5% yield"),
                ("SCHD", "Schwab US Dividend Equity", "High-quality dividend stocks"),
                ("JEPI", "JPMorgan Equity Premium Income", "Income-focused with downside protection")
            ]
        elif risk_score <= 20:
            etfs = [
                ("VOO", "Vanguard S&P 500", "Classic diversified S&P 500 index"),
                ("VTI", "Vanguard Total Stock Market", "Entire U.S. stock market"),
                ("SCHD", "Schwab US Dividend Equity", "Quality dividend growth")
            ]
        elif risk_score <= 30:
            etfs = [
                ("QQQ", "Invesco QQQ", "Nasdaq 100 tech growth"),
                ("VUG", "Vanguard Growth", "U.S. growth stocks"),
                ("SCHG", "Schwab U.S. Large-Cap Growth", "Growth-focused")
            ]
        else:
            etfs = [
                ("ARKK", "ARK Innovation", "Disruptive innovation (high risk)"),
                ("TQQQ", "ProShares UltraPro QQQ", "3x leveraged Nasdaq (very risky)"),
                ("SOXL", "Direxion Semiconductor Bull 3X", "3x leveraged chips (extreme risk)")
            ]
        
        for ticker_etf, name, reason in etfs:
            with st.expander(f"📦 {ticker_etf} - {name}"):
                st.markdown(f"**Why:** {reason}")
                try:
                    quote_etf = get_quote(ticker_etf)
                    if quote_etf:
                        price_etf = quote_etf.get('price', 0)
                        change_etf = quote_etf.get('changesPercentage', 0)
                        st.metric("Price", f"${price_etf:.2f}", f"{change_etf:+.2f}%")
                except:
                    pass
        
        st.markdown("---")
        st.markdown("### 🎮 Want to Practice First?")
        st.success("✨ **Try our Paper Portfolio!** Practice trading with $10,000 fake money before risking real capital. Build confidence, test strategies, track performance.")
        
        if st.button("🚀 Start Paper Trading Now", use_container_width=True, type="primary"):
            st.info("👉 Click the **'💼 Paper Portfolio'** tab above to get started!")
        
        st.caption("⚠️ Paper trading doesn't reflect real costs, slippage, or emotions. But it's a great way to learn!")

        st.markdown("---")
        st.markdown("### 🔒 Want More?")
        st.warning("""
**Upgrade to Premium for:**
- 10+ personalized stock picks for your profile
- AI-powered portfolio optimization
- Real-time risk monitoring
- Sector-specific recommendations
- Rebalancing alerts
        """)
        
        if st.button("🚀 Upgrade to Premium", use_container_width=True):
            st.balloons()
            st.success("Premium features coming soon! 🎉")




elif selected_page == "📊 Company Analysis":
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
            
            # Fetch treasury rates from FMP
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
            st.markdown("### 🏆 My Top 5 Metrics")
            
            with st.expander("#1: Net Income Growth"):
                st.caption("Bottom line profit. If this isn't growing, nothing else matters.")
            
            with st.expander("#2: Operating Income Growth"):
                st.caption("Shows if the core business is healthy, before financial engineering.")
            
            with st.expander("#3: Free Cash Flow Growth"):
                st.caption("Cash is king. A company can manipulate earnings, but cash flow doesn't lie.")
            
            with st.expander("#4: Revenue Growth"):
                st.caption("Top line tells you if customers want the product.")
            
            with st.expander("#5: Quick Ratio Growth"):
                st.caption("Can they handle a crisis? Rising liquidity = safety.")

            st.markdown("---")
            
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
        
        health_tab1, health_tab2 = st.tabs(["📈 Financial Ratios", "🔀 Compare Stocks"])
        
        with health_tab1:
            st.markdown("### 📈 Financial Ratios")
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
                    st.markdown(f"**What it means:** {METRIC_EXPLANATIONS['P/E Ratio']['explanation']}")
                    st.markdown(f"**Good range:** {METRIC_EXPLANATIONS['P/E Ratio']['good']}")
                    
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
                    st.markdown(f"**What it means:** {METRIC_EXPLANATIONS['P/S Ratio']['explanation']}")
                    st.markdown(f"**Good range:** {METRIC_EXPLANATIONS['P/S Ratio']['good']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{stock1}: {ps1:.2f if ps1 > 0 else 'N/A'}**")
                    with col2:
                        st.markdown(f"**{stock2}: {ps2:.2f if ps2 > 0 else 'N/A'}**")
                
                with st.expander("🏦 Debt-to-Equity Ratio - Click for explanation"):
                    st.markdown(f"**What it means:** {METRIC_EXPLANATIONS['Debt-to-Equity']['explanation']}")
                    st.markdown(f"**Good range:** {METRIC_EXPLANATIONS['Debt-to-Equity']['good']}")
                    
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
                    st.markdown(f"**What it means:** {METRIC_EXPLANATIONS['Quick Ratio']['explanation']}")
                    st.markdown(f"**Good range:** {METRIC_EXPLANATIONS['Quick Ratio']['good']}")
                    
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
                    st.markdown(f"**What it means:** {METRIC_EXPLANATIONS['FCF per Share']['explanation']}")
                    st.markdown(f"**Good range:** {METRIC_EXPLANATIONS['FCF per Share']['good']}")
                    
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
                    st.markdown(f"**What it means:** {METRIC_EXPLANATIONS['Beta']['explanation']}")
                    st.markdown(f"**Good range:** {METRIC_EXPLANATIONS['Beta']['good']}")
                    
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
    
    elif view == "📈 Financial Ratios":
        st.markdown("## 📊 Financial Ratios Over Time")
        
        st.info("💡 **Why I track these ratios:** They reveal profitability (margins), efficiency (ROE/ROA/ROCE), and safety (liquidity/leverage). Together they show if a company makes money efficiently and can survive tough times.")
        
        
        col1, col2 = st.columns(2)
        with col1:
            ratio_period = st.radio("Period", ["Annual", "Quarterly"], key="ratio_period_sel")
        with col2:
            ratio_years = st.slider("Years of History", 1, 30, 5, key="ratio_years_sel")
        
        period_param = "annual" if ratio_period == "Annual" else "quarter"
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?period={period_param}&limit={ratio_years}&apikey={FMP_API_KEY}"
        
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
        else:
            st.warning("⚠️ AI analysis is currently unavailable. This could be due to API limits or connectivity issues.")
            st.info("💡 **Tip:** Try again in a few minutes, or check the Financial Ratios and Key Metrics tabs for data-driven insights!")
    
    elif view == "📈 Investment Calculator":
        st.markdown(f"## 📈 Four Scenarios Investment Calculator")
        st.info(f"💡 **What is this?** Compare 4 different ways to invest $100 in {ticker} vs the S&P 500. See how 'Paycheck Investing' (adding $100 every 2 weeks) compares to investing all at once!")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            years = st.slider("Investment Timeline (Years):", 1, 10, 5, help="How many years to simulate")
        
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
        else:
            st.warning(f"⚠️ Could not calculate scenarios for {ticker}. Historical price data may not be available.")
            st.info("💡 **Tip:** Try a major stock like AAPL, MSFT, or GOOGL")


elif selected_page == "🌍 Sector Explorer":
    st.header("🎯 Sector Explorer")
    
    # Default to Technology sector
    sector_list = list(SECTORS.keys())
    default_sector_idx = sector_list.index("💻 Technology") if "💻 Technology" in sector_list else 0
    selected_sector = st.selectbox("Choose sector:", sector_list, index=default_sector_idx)
    sector_info = SECTORS[selected_sector]
    st.info(f"**{selected_sector}** - {sector_info['desc']}")
    
    with st.spinner("Loading sector data..."):
        rows = []
        for ticker_sym in sector_info['tickers']:
            quote = get_quote(ticker_sym)
            ratios_ttm = get_ratios_ttm(ticker_sym)
            cash_df = get_cash_flow(ticker_sym, 'annual', 1)
            income_df = get_income_statement(ticker_sym, 'annual', 1)
            
            if quote:
                pe = get_pe_ratio(ticker_sym, quote, ratios_ttm, income_df)
                ps = get_ps_ratio(ticker_sym, ratios_ttm)
                fcf_per_share = calculate_fcf_per_share(ticker_sym, cash_df, quote)
                
                rows.append({
                    "Ticker": ticker_sym,
                    "Company": quote.get('name', ticker_sym),
                    "Price": quote.get('price', 0),
                    "Change %": quote.get('changesPercentage', 0),
                    "Market Cap": quote.get('marketCap', 0),
                    "P/E": pe,
                    "P/S": ps,
                    "FCF/Share": fcf_per_share
                })
        
        if rows:
            df = pd.DataFrame(rows)
            df = df.sort_values('Market Cap', ascending=False)
            
            col1, col2, col3 = st.columns(3)
            
            valid_pes = df[df['P/E'] > 0]['P/E']
            if len(valid_pes) > 0:
                col1.metric("📊 Sector Avg P/E", f"{valid_pes.mean():.2f}",
                           help="Average Price-to-Earnings ratio for this sector")
            
            valid_ps = df[df['P/S'] > 0]['P/S']
            if len(valid_ps) > 0:
                col2.metric("📊 Sector Avg P/S", f"{valid_ps.mean():.2f}",
                           help="Average Price-to-Sales ratio for this sector")
            
            valid_fcf = df[df['FCF/Share'] > 0]['FCF/Share']
            if len(valid_fcf) > 0:
                col3.metric("📊 Sector Avg FCF/Share", f"${valid_fcf.mean():.2f}",
                           help="Average Free Cash Flow per share for this sector")
            
            st.markdown("**📊 Sector Companies** (hover over metrics for explanations)")
            
            display_df = df.copy()
            display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
            display_df['Change %'] = display_df['Change %'].apply(lambda x: f"{x:+.2f}%")
            display_df['Market Cap'] = display_df['Market Cap'].apply(format_number)
            display_df['P/E'] = display_df['P/E'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
            display_df['P/S'] = display_df['P/S'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
            display_df['FCF/Share'] = display_df['FCF/Share'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            with st.expander("💡 What do these metrics mean?"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**P/E Ratio:** " + METRIC_EXPLANATIONS["P/E Ratio"]["explanation"])
                    st.markdown("**P/S Ratio:** " + METRIC_EXPLANATIONS["P/S Ratio"]["explanation"])
                with col2:
                    st.markdown("**FCF/Share:** " + METRIC_EXPLANATIONS["FCF per Share"]["explanation"])
                    st.markdown("**Market Cap:** " + METRIC_EXPLANATIONS["Market Cap"]["explanation"])
            
            st.markdown("### 🔍 Analyze a Company")
            col1, col2 = st.columns([3, 1])
            with col1:
                selected = st.selectbox("Choose:", df['Ticker'].tolist(), 
                                   format_func=lambda x: f"{df[df['Ticker']==x]['Company'].values[0]} ({x})")
            with col2:
                if st.button("Analyze →", type="primary", use_container_width=True):
                    st.session_state.selected_ticker = selected
                    st.rerun()


elif selected_page == "📈 Financial Ratios":
    st.header("📈 Financial Ratios - Historical Trends")
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
        
        # Market Intelligence Section
        st.markdown("---")
        st.markdown("### Market Intelligence")
        st.caption("AI-powered news summary for this stock")
        
        # Fetch 10 news stories
        news = get_stock_specific_news(ticker, 10)
        if news:
            st.markdown("**Latest Headlines:**")
            for article in news[:10]:
                title = article.get('title', 'No title')
                published = article.get('publishedDate', '')[:10]
                url = article.get('url', '')
                if url:
                    st.markdown(f"- [{title}]({url}) ({published})")
                else:
                    st.markdown(f"- **{title}** ({published})")
            
            # AI Summary using Perplexity (if API key available)
            perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY', '')
            if perplexity_api_key:
                try:
                    headlines_text = " | ".join([a.get('title', '') for a in news[:5]])
                    
                    perplexity_url = "https://api.perplexity.ai/chat/completions"
                    perplexity_headers = {
                        "Authorization": f"Bearer {perplexity_api_key}",
                        "Content-Type": "application/json"
                    }
                    perplexity_payload = {
                        "model": "sonar",
                        "messages": [
                            {"role": "system", "content": "You are a financial analyst. Summarize the news in 2 sentences for a beginner investor."},
                            {"role": "user", "content": f"Summarize these headlines about {ticker} ({company_name}): {headlines_text}"}
                        ],
                        "max_tokens": 150
                    }
                    
                    response = requests.post(perplexity_url, headers=perplexity_headers, json=perplexity_payload, timeout=10)
                    if response.status_code == 200:
                        ai_summary = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
                        if ai_summary:
                            st.success(f"**AI Bottom Line:** {ai_summary}")
                        else:
                            st.info(f"**Quick Take:** {ticker} has been in the news recently. Check the headlines above for details.")
                    else:
                        st.info(f"**Quick Take:** {ticker} has been in the news recently. Check the headlines above for details.")
                except:
                    st.info(f"**Quick Take:** {ticker} has been in the news recently. Check the headlines above for details.")
            else:
                st.info(f"**Quick Take:** {ticker} has been in the news recently. Check the headlines above for details.")
        else:
            st.info(f"No recent news found for {ticker}")
        
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
    
    # Calculate Fear & Greed score based on S&P 500 momentum
    try:
        spy_data = get_historical_price("SPY", 1)
        if not spy_data.empty and 'price' in spy_data.columns and len(spy_data) >= 20:
            spy_data = spy_data.sort_values('date')
            current_price = spy_data['price'].iloc[-1]
            price_20d_ago = spy_data['price'].iloc[-20] if len(spy_data) >= 20 else spy_data['price'].iloc[0]
            
            # Calculate momentum (20-day return)
            momentum_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
            
            # Map momentum to Fear/Greed scale (0-100)
            if momentum_20d <= -10:
                sentiment_score = 10
            elif momentum_20d <= -5:
                sentiment_score = 30
            elif momentum_20d <= 0:
                sentiment_score = 45
            elif momentum_20d <= 5:
                sentiment_score = 55
            elif momentum_20d <= 10:
                sentiment_score = 70
            else:
                sentiment_score = 90
        else:
            sentiment_score = 50
    except:
        sentiment_score = 50
    
    # Display the speedometer gauge
    col_gauge, col_labels = st.columns([2, 1])
    
    with col_gauge:
        gauge_fig = create_fear_greed_gauge(sentiment_score)
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    with col_labels:
        label, color = get_market_sentiment_label(sentiment_score)
        st.markdown(f'''
        <div style="padding: 20px; text-align: center;">
            <h3 style="color: {color}; margin-bottom: 20px;">{label}</h3>
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
    
    # Ticker Search Box
    st.markdown("### Search for Stock-Specific News")
    intel_ticker = st.text_input(
        "Enter a ticker symbol (leave empty for general market news):",
        "",
        placeholder="e.g., AAPL, TSLA, GOOGL",
        key="intel_ticker_search"
    )
    
    # Function to get market news via Perplexity API
    def get_market_intelligence(ticker=None):
        """Fetch market news using Perplexity API"""
        if not PERPLEXITY_API_KEY:
            return None, "Perplexity API key not configured"
        
        try:
            if ticker and ticker.strip():
                query = f"Latest news, catalysts, and market analysis for {ticker.upper()} stock. Include recent price movements, analyst opinions, and any significant company developments."
            else:
                query = "Today's US stock market news summary: S&P 500 performance, interest rates, inflation data, major earnings reports, and key market movers."
            
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {"role": "system", "content": "You are a financial news analyst. Provide concise, factual market updates in bullet points. Focus on actionable insights for investors."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 1000
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
    
    # Fetch and display news
    with st.spinner("Fetching latest market intelligence..."):
        news_content, error = get_market_intelligence(intel_ticker if intel_ticker.strip() else None)
    
    if news_content:
        if intel_ticker and intel_ticker.strip():
            st.markdown(f"### 📊 {intel_ticker.upper()} - Latest News & Analysis")
        else:
            st.markdown("### 📈 General Market News")
        
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
    
    # Also show FMP news headlines if available
    st.markdown("---")
    st.markdown("### 📰 Recent Headlines")
    
    if intel_ticker and intel_ticker.strip():
        fmp_news = get_stock_specific_news(intel_ticker.upper(), 10)
    else:
        # Get general market news from FMP
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
            url = article.get('url', '')
            if url:
                st.markdown(f"- [{title}]({url}) ({published})")
            else:
                st.markdown(f"- **{title}** ({published})")
    else:
        st.info("No recent headlines available.")
    
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
    
    # Feature Comparison Table
    st.markdown("---")
    st.markdown("### Feature Comparison")
    
    # Create feature comparison table with HTML for better styling
    st.markdown("""
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <thead>
            <tr style="background: #1a1a1a;">
                <th style="padding: 15px; text-align: left; border-bottom: 2px solid #333; color: #FFFFFF;">Feature</th>
                <th style="padding: 15px; text-align: center; border-bottom: 2px solid #333; color: #00C853;">Free</th>
                <th style="padding: 15px; text-align: center; border-bottom: 2px solid #333; color: #9D4EDD;">Pro</th>
                <th style="padding: 15px; text-align: center; border-bottom: 2px solid #333; color: #FFD700;">Ultimate</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background: #0a0a0a;">
                <td style="padding: 12px; border-bottom: 1px solid #222; color: #FFFFFF;">Basic Ratios</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #00C853; font-size: 20px;">&#10003;</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #00C853; font-size: 20px;">&#10003;</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #00C853; font-size: 20px;">&#10003;</td>
            </tr>
            <tr style="background: #1a1a1a;">
                <td style="padding: 12px; border-bottom: 1px solid #222; color: #FFFFFF;">Trade Alerts</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #FF4444; font-size: 20px;">&#10007;</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #00C853; font-size: 20px;">&#10003;</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #00C853; font-size: 20px;">&#10003;</td>
            </tr>
            <tr style="background: #0a0a0a;">
                <td style="padding: 12px; border-bottom: 1px solid #222; color: #FFFFFF;">Naman's Portfolio</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #FF4444; font-size: 20px;">&#10007;</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #00C853; font-size: 20px;">&#10003;</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #00C853; font-size: 20px;">&#10003;</td>
            </tr>
            <tr style="background: #1a1a1a;">
                <td style="padding: 12px; border-bottom: 1px solid #222; color: #FFFFFF;">1-on-1 Support</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #FF4444; font-size: 20px;">&#10007;</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #FF4444; font-size: 20px;">&#10007;</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #222; color: #00C853; font-size: 20px;">&#10003;</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)
    
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


elif selected_page == "📋 Investment Checklist":
    st.header("Investment Checklist")
    
    # Progress Bar for Investment Checklist
    if 'checklist_analyzed' not in st.session_state:
        st.session_state.checklist_analyzed = False
    
    # Use current_step/total_steps format for render_progress_bar
    checklist_current = 1 if st.session_state.checklist_analyzed else 0
    checklist_total = 1
    render_progress_bar(checklist_current, checklist_total, "Checklist Progress")
    
    st.write("Quick check before investing")
    
    ticker_check = st.text_input("Enter ticker:", value=st.session_state.selected_ticker, key="checklist_ticker")
    
    if st.button("Analyze", key="checklist_analyze"):
        st.session_state.checklist_analyzed = True
        quote = get_quote(ticker_check)
        ratios = get_financial_ratios(ticker_check, 'annual', 1)
        cash = get_cash_flow(ticker_check, 'annual', 1)
        balance = get_balance_sheet(ticker_check, 'annual', 1)
        ratios_ttm = get_ratios_ttm(ticker_check)
        income_df = get_income_statement(ticker_check, 'annual', 1)
        
        if quote:
            st.subheader(f"📊 {quote.get('name', ticker_check)} ({ticker_check})")
            
            checks = []
            
            if not ratios.empty and 'netProfitMargin' in ratios.columns:
                margin = ratios['netProfitMargin'].iloc[-1]
                checks.append(("✅ Profitable (>10% margin)" if margin > 0.1 else "❌ Low profitability", margin > 0.1))
            
            if not cash.empty and 'freeCashFlow' in cash.columns:
                fcf = cash['freeCashFlow'].iloc[-1]
                checks.append(("✅ Positive free cash flow" if fcf > 0 else "❌ Negative FCF", fcf > 0))
            
            pe = get_pe_ratio(ticker_check, quote, ratios_ttm, income_df)
            if 0 < pe < 30:
                checks.append(("✅ Reasonable P/E (<30)", True))
            elif pe > 30:
                checks.append(("⚠️ High P/E (>30)", False))
            
            mcap = quote.get('marketCap', 0)
            checks.append(("✅ Large cap (>$10B)" if mcap > 10e9 else "⚠️ Small/mid cap", mcap > 10e9))
            
            de_ratio = calculate_debt_to_equity(balance)
            if de_ratio > 0:
                checks.append(("✅ Low debt (D/E < 1.0)" if de_ratio < 1.0 else "⚠️ High debt (D/E > 1.0)", de_ratio < 1.0))
            
            qr = calculate_quick_ratio(balance)
            if qr > 0:
                checks.append(("✅ Good liquidity (QR > 1.0)" if qr > 1.0 else "⚠️ Low liquidity (QR < 1.0)", qr > 1.0))
            
            for check, passed in checks:
                if passed:
                    st.success(check)
                else:
                    st.warning(check)
            
            passed_count = sum(1 for _, p in checks if p)
            total = len(checks)
            
            st.metric("Score", f"{passed_count}/{total}")
            
            if passed_count >= total * 0.75:
                st.success("🎉 Strong candidate!")
            elif passed_count >= total * 0.5:
                st.info("🤔 Mixed signals")
            else:
                st.error("🚨 Many red flags")


elif selected_page == "💼 Paper Portfolio":
    st.header("💼 My Portfolio")
    st.markdown("**Track your practice portfolio and analyze its risk profile.**")
    
    portfolio_tab1, portfolio_tab2 = st.tabs(["📊 Portfolio Tracker", "⚠️ Risk Analyzer"])
    
    with portfolio_tab1:
        st.markdown("### 📊 Paper Portfolio Tracker")
        st.caption("⚠️ Simulated trading for educational purposes only. Does not reflect real trading costs, slippage, or market conditions.")
    
    # Initialize session state for portfolio
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'cash' not in st.session_state:
        st.session_state.cash = 10000.0  # Start with $10k
    if 'transactions' not in st.session_state:
        st.session_state.transactions = []
    
    # Sidebar for adding positions
    with st.sidebar:
        st.markdown("### 📊 Portfolio Summary")
        
        # Calculate total value
        total_value = st.session_state.cash
        total_gain_loss = 0
        
        for position in st.session_state.portfolio:
            quote = get_quote(position['ticker'])
            if quote:
                current_price = quote.get('price', 0)
                position_value = position['shares'] * current_price
                total_value += position_value
                
                cost_basis = position['shares'] * position['avg_price']
                total_gain_loss += (position_value - cost_basis)
        
        st.metric("Portfolio Value", f"${total_value:,.2f}")
        st.metric("Cash Available", f"${st.session_state.cash:,.2f}")
        st.metric("Total Gain/Loss", f"${total_gain_loss:,.2f}", 
                 f"{(total_gain_loss / 10000 * 100):+.2f}%")
        
        st.markdown("---")
        st.markdown("### 🆕 Add Position")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main portfolio view
        if not st.session_state.portfolio:
            st.info("👋 Your portfolio is empty! Use the sidebar to add your first position.")
        else:
            st.markdown("### 📈 Your Positions")
            
            for i, position in enumerate(st.session_state.portfolio):
                ticker = position['ticker']
                shares = position['shares']
                avg_price = position['avg_price']
                
                # Get current price
                quote = get_quote(ticker)
                if quote:
                    current_price = quote.get('price', 0)
                    change_pct = quote.get('changesPercentage', 0)
                    
                    current_value = shares * current_price
                    cost_basis = shares * avg_price
                    gain_loss = current_value - cost_basis
                    gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
                    
                    with st.expander(f"**{ticker}** - {shares} shares", expanded=True):
                        col_a, col_b, col_c, col_d = st.columns(4)
                        
                        col_a.metric("Current Price", f"${current_price:.2f}", f"{change_pct:+.2f}%")
                        col_b.metric("Avg Cost", f"${avg_price:.2f}")
                        col_c.metric("Value", f"${current_value:,.2f}")
                        col_d.metric("Gain/Loss", f"${gain_loss:,.2f}", f"{gain_loss_pct:+.2f}%")
                        
                        col_x, col_y = st.columns(2)
                        
                        with col_x:
                            if st.button(f"📊 Analyze {ticker}", key=f"analyze_{ticker}_{i}"):
                                st.session_state.selected_ticker = ticker
                            st.rerun()
                        
                        with col_y:
                            if st.button(f"💰 Sell All", key=f"sell_{ticker}_{i}", type="secondary"):
                                # Sell position
                                sale_value = shares * current_price
                                st.session_state.cash += sale_value
                                
                                # Add transaction
                            st.session_state.transactions.append({
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                'type': 'SELL',
                                'ticker': ticker,
                                'shares': shares,
                                'price': current_price,
                                'total': sale_value,
                                'gain_loss': gain_loss
                            })
                                
                            # Remove position
                            st.session_state.portfolio.pop(i)
                            st.success(f"✅ Sold {shares} shares of {ticker} for ${sale_value:,.2f}")
                            st.rerun()
    
    with col2:
        st.markdown("### 🛒 Buy Stock")
        
        buy_ticker = st.text_input("Ticker Symbol", placeholder="AAPL", key="buy_ticker_input").upper()
        
        if buy_ticker:
            quote = get_quote(buy_ticker)
            if quote:
                current_price = quote.get('price', 0)
                st.metric("Current Price", f"${current_price:.2f}")
                
                buy_shares = st.number_input("Shares to Buy", min_value=1, value=10, step=1)
                total_cost = buy_shares * current_price
                
                st.info(f"**Total Cost:** ${total_cost:,.2f}")
                
                if total_cost > st.session_state.cash:
                    st.error(f"❌ Insufficient funds! You need ${total_cost - st.session_state.cash:,.2f} more.")
                else:
                    if st.button("✅ Buy", use_container_width=True, type="primary"):
                        # Check if we already own this stock
                        existing = None
                        for pos in st.session_state.portfolio:
                            if pos['ticker'] == buy_ticker:
                                existing = pos
                            break
                        
                        if existing:
                            # Update existing position (average down/up)
                            total_shares = existing['shares'] + buy_shares
                            total_cost_all = (existing['shares'] * existing['avg_price']) + total_cost
                            new_avg = total_cost_all / total_shares
                            
                            existing['shares'] = total_shares
                            existing['avg_price'] = new_avg
                        else:
                            # Add new position
                            st.session_state.portfolio.append({
                            'ticker': buy_ticker,
                            'shares': buy_shares,
                            'avg_price': current_price
                            })
                        
                        # Deduct cash
                        st.session_state.cash -= total_cost
                        
                        # Add transaction
                        st.session_state.transactions.append({
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'type': 'BUY',
                            'ticker': buy_ticker,
                            'shares': buy_shares,
                            'price': current_price,
                            'total': total_cost
                        })
                        
                        st.success(f"✅ Bought {buy_shares} shares of {buy_ticker}!")
                        st.rerun()
            else:
                st.error("❌ Invalid ticker symbol")
    
    # Transaction history
    if st.session_state.transactions:
        st.markdown("---")
        st.markdown("### 📜 Transaction History")
        
        with st.expander("View All Transactions", expanded=False):
            for i, txn in enumerate(reversed(st.session_state.transactions[-20:])):  # Last 20
                type_emoji = "🟢" if txn['type'] == 'BUY' else "🔴"
                gain_loss_text = f" | Gain/Loss: ${txn['gain_loss']:,.2f}" if 'gain_loss' in txn else ""
                
                st.markdown(f"{type_emoji} **{txn['type']}** {txn['shares']} {txn['ticker']} @ ${txn['price']:.2f} = ${txn['total']:,.2f}{gain_loss_text}")
                st.caption(f"{txn['date']}")
                if i < len(st.session_state.transactions) - 1:
                    st.markdown("---")
    
    # Performance chart
    st.divider()
    st.markdown("### 📊 Performance Tracking")
    st.info("💡 **Coming Soon:** Interactive performance charts showing your portfolio value over time!")
    
    # Reset portfolio option
    if st.button("🔄 Reset Portfolio (Start Over)", type="secondary"):
        st.session_state.portfolio = []
        st.session_state.cash = 10000.0
        st.session_state.transactions = []
        st.success("✅ Portfolio reset! You have $10,000 to start fresh.")
        st.rerun()


# ============= FOOTER DISCLAIMER =============
    st.divider()
    st.markdown("---")
    st.caption("""
    **Disclaimer:** Investing Made Simple | FMP Premium | Real-time data  

    ⚠️ **IMPORTANT LEGAL DISCLAIMER:**  
    This application and all content provided herein are for **educational and informational purposes ONLY**. Nothing on this platform constitutes financial advice, investment advice, trading advice, legal advice, tax advice, or any other sort of advice. You should not treat any of the app's content as a recommendation to buy, sell, or hold any security or investment.

    **No Warranty:** The information is provided "as-is" without warranty of any kind. We do not guarantee the accuracy, completeness, or timeliness of any information presented.

    **Investment Risks:** All investments involve risk, including the potential loss of principal. Past performance does not guarantee future results. Securities trading and investing involve substantial risk of loss.

    **Not Professional Advice:** We are not registered financial advisors, brokers, or investment professionals. Always consult with qualified financial, legal, and tax professionals before making any investment decisions.

    **Data Sources:** Data is sourced from Financial Modeling Prep API. We are not responsible for data accuracy or API availability.

    **Paper Portfolio:** The paper portfolio feature is for educational simulation only. Results do not represent actual trading and do not reflect real market conditions, fees, or slippage.

    **Your Responsibility:** You are solely responsible for your own investment decisions and their outcomes. By using this app, you acknowledge and accept these terms.

    © 2024 Investing Made Simple. All rights reserved.
    """)

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


# ============= FOOTER =============
st.divider()
st.caption("💡 Investing Made Simple | FMP Premium | Real-time data")
st.caption("⚠️ Educational purposes only. Not financial advice.")
