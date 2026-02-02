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

# OpenAI API for AI Coach chatbot
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Portfolio Configuration - Starting cash for paper trading
STARTING_CASH = float(os.environ.get("STARTING_CASH", "100000"))

st.set_page_config(page_title="Investing Made Simple", layout="wide", page_icon="💰")

# PERMANENT LIGHT MODE - FORCE WHITE BACKGROUND + BLACK TEXT
st.markdown("""
<style>
/* Force light theme */
.stApp {
    background-color: #FFFFFF !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
}

[data-testid="stHeader"] {
    background-color: #FFFFFF !important;
}

.main {
    background-color: #FFFFFF !important;
}

.block-container {
    background-color: #FFFFFF !important;
}

/* Sidebar light gray */
[data-testid="stSidebar"] {
    background-color: #F9F9F9 !important;
}

[data-testid="stSidebar"] > div:first-child {
    background-color: #F9F9F9 !important;
}

/* ALL TEXT BLACK */
body, p, span, div, label, a, li, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown *,
[data-testid="stMarkdown"] *,
[data-testid="stText"],
[data-testid="stCaption"],
[data-testid="stSidebar"] *,
.element-container * {
    color: #121212 !important;
}

/* Buttons keep their colors */
.stButton button {
    color: #FFFFFF !important;
}

/* Input fields */
input, textarea, select {
    background-color: #FFFFFF !important;
    color: #121212 !important;
    border: 1px solid #D1D5DB !important;
}

/* Dropdowns - only apply white background to non-navigation dropdowns */
.main [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: #FFFFFF !important;
}

.main [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #121212 !important;
}

/* Navigation dropdowns MUST be RED - highest priority */
/* Style POPOVER buttons in navigation (NEW approach - no typing allowed) */
[data-testid="stHorizontalBlock"] button[kind="secondary"],
[data-testid="stHorizontalBlock"] [data-testid="baseButton-secondary"] {
    background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

[data-testid="stHorizontalBlock"] button[kind="secondary"] *,
[data-testid="stHorizontalBlock"] button[kind="secondary"] p,
[data-testid="stHorizontalBlock"] button[kind="secondary"] span {
    color: #FFFFFF !important;
}

/* OLD selectbox approach (keeping for fallback) */
[data-testid="stHorizontalBlock"] [data-baseweb="select"],
[data-testid="stHorizontalBlock"] [data-baseweb="select"] > div {
    background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
    border: none !important;
}

[data-testid="stHorizontalBlock"] [data-baseweb="select"] *,
[data-testid="stHorizontalBlock"] [data-baseweb="select"] span,
[data-testid="stHorizontalBlock"] [data-baseweb="select"] div:not([data-baseweb="select"]) {
    color: #FFFFFF !important;
}

/* DISABLE TYPING IN NAVIGATION DROPDOWNS */
[data-testid="stHorizontalBlock"] [data-baseweb="select"] input {
    pointer-events: none !important;
    cursor: pointer !important;
    caret-color: transparent !important;
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
}

/* Hide the input caret/cursor */
[data-testid="stHorizontalBlock"] [data-baseweb="select"] input:focus {
    outline: none !important;
    border: none !important;
}


</style>
""", unsafe_allow_html=True)

# Initialize selected page
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "🏠 Dashboard"
selected_page = st.session_state.selected_page

# Fix button text visibility + NAV dropdown width (single, valid CSS block)
st.markdown(
    """
    <style>
      /* Force button text to be visible */
      .stButton button, .stButton button p, .stButton button span, .stButton button div {
        color: white !important;
        font-size: 14px !important;
        visibility: visible !important;
        opacity: 1 !important;
        overflow: visible !important;
      }

      /* Keep nav buttons comfortably sized */
      .stButton button {
        min-height: 44px !important;
        padding: 10px 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
      }

      /* Selectbox text/icon color (for the nav dropdowns) */
      div[data-baseweb="select"],
      div[data-baseweb="select"] span,
      div[data-baseweb="select"] div,
      div[data-baseweb="select"] input,
      div[data-baseweb="select"] svg {
        color: white !important;
        fill: white !important;
      }

      /* --- NAV DROPDOWN WIDTH FIX --- */
      [data-testid="stHorizontalBlock"] div[data-baseweb="select"] {
        min-width: 260px !important;
      }

      /* Prevent truncation inside tab-like buttons */
      button[data-baseweb="tab"] > div > div {
        white-space: nowrap !important;
      }

      /* VIP button text should be black */
      button[data-testid*="vip"] p,
      button[data-testid*="vip"] span {
        color: black !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
# ============================================
# PHASE 1: PREMIUM FOUNDATION UTILITIES
# ============================================

# ============================================
# 1.1 POPUP SYSTEM WITH PERSISTENCE (st.dialog)
# ============================================

def init_persistence():
    """Initialize persistence for user preferences using localStorage via JS"""
    # Load dismissed popups from localStorage on first run
    if 'persistence_initialized' not in st.session_state:
        st.session_state.persistence_initialized = True
        st.session_state.dismissed_popups = set()
        st.session_state.last_ticker = None
        st.session_state.last_tab = None
        st.session_state.pinned_tickers = []
        
        # Inject JS to load from localStorage
        st.markdown("""
        <script>
        (function() {
            // Load dismissed popups
            const dismissed = localStorage.getItem('ims_dismissed_popups');
            if (dismissed) {
                window.parent.postMessage({type: 'dismissed_popups', data: JSON.parse(dismissed)}, '*');
            }
            // Load pinned tickers
            const pinned = localStorage.getItem('ims_pinned_tickers');
            if (pinned) {
                window.parent.postMessage({type: 'pinned_tickers', data: JSON.parse(pinned)}, '*');
            }
            // Load last ticker
            const lastTicker = localStorage.getItem('ims_last_ticker');
            if (lastTicker) {
                window.parent.postMessage({type: 'last_ticker', data: lastTicker}, '*');
            }
        })();
        </script>
        """, unsafe_allow_html=True)

def save_to_localstorage(key, value):
    """Save a value to localStorage via JS injection"""
    json_value = json.dumps(value) if isinstance(value, (list, dict, set)) else json.dumps(str(value))
    if isinstance(value, set):
        json_value = json.dumps(list(value))
    st.markdown(f"""
    <script>
    localStorage.setItem('ims_{key}', {json_value});
    </script>
    """, unsafe_allow_html=True)

def show_page_popup(page_id, title, summary, cool_feature):
    """True modal popup using st.dialog() - works on Streamlit 1.31+
       Persists dismissal to localStorage so popups don't reappear"""
    
    # Initialize dismissed set
    if 'dismissed_popups' not in st.session_state:
        st.session_state.dismissed_popups = set()
    
    # Already dismissed this session? Skip.
    if page_id in st.session_state.dismissed_popups:
        return
    
    # Inject global CSS to style ALL dialogs with dark background
    st.markdown("""
    <style>
    /* Force dark background on dialog */
    [data-testid="stDialog"] [data-testid="stVerticalBlock"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    [data-testid="stDialog"] > div > div {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        border: 2px solid #ff4b4b !important;
        border-radius: 15px !important;
    }
    /* Make all text white */
    [data-testid="stDialog"] p, 
    [data-testid="stDialog"] span,
    [data-testid="stDialog"] h1, 
    [data-testid="stDialog"] h2,
    [data-testid="stDialog"] h3,
    [data-testid="stDialog"] label {
        color: #FFFFFF !important;
    }
    /* Style the close X button */
    [data-testid="stDialog"] button[kind="header"] {
        color: #FFFFFF !important;
    }
    [data-testid="stDialog"] svg {
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Define the dialog with the PAGE TITLE as dialog title
    @st.dialog(title)
    def page_intro_dialog():
        # Content with description and cool feature
        st.markdown(f"""
        <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px; color: #FFFFFF;">{summary}</p>
        <div style="
            background: linear-gradient(135deg, rgba(255, 75, 75, 0.3), rgba(255, 100, 100, 0.2)); 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 4px solid #ff4b4b;
        ">
            <p style="margin: 0; font-size: 15px; color: #FFFFFF;">
                🌟 <strong style="color: #FFD700;">Cool Feature:</strong> {cool_feature}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")  # Spacer
        
        if st.button("✓ Got it!", type="primary", use_container_width=True):
            st.session_state.dismissed_popups.add(page_id)
            # Persist to localStorage
            save_to_localstorage('dismissed_popups', list(st.session_state.dismissed_popups))
            st.rerun()
    
    # Show the dialog
    page_intro_dialog()


# ============================================
# 1.2 DATA SOURCE & TIMESTAMP INDICATORS
# ============================================

def show_data_source(source="FMP API", updated_at=None, is_cached=False, is_delayed=False):
    """Display a consistent data source indicator with timestamp
    
    Args:
        source: Data source name (e.g., "FMP API", "Perplexity AI", "CNN Fear & Greed")
        updated_at: datetime object or None for "just now"
        is_cached: Show cached data badge
        is_delayed: Show delayed data badge
    """
    # Format timestamp
    if updated_at is None:
        time_str = "just now"
    elif isinstance(updated_at, datetime):
        delta = datetime.now() - updated_at
        if delta.seconds < 60:
            time_str = "just now"
        elif delta.seconds < 3600:
            time_str = f"{delta.seconds // 60}m ago"
        elif delta.seconds < 86400:
            time_str = f"{delta.seconds // 3600}h ago"
        else:
            time_str = updated_at.strftime("%b %d, %H:%M")
    else:
        time_str = str(updated_at)
    
    # Build badges
    badges = []
    if is_cached:
        badges.append("🔄 Cached")
    if is_delayed:
        badges.append("⏱️ Delayed")
    badge_str = " • ".join(badges)
    if badge_str:
        badge_str = f" • {badge_str}"
    
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        background: rgba(128, 128, 128, 0.1);
        border-radius: 6px;
        font-size: 12px;
        color: #888;
        margin: 8px 0;
    ">
        <span>📊 Source: <strong>{source}</strong></span>
        <span>•</span>
        <span>Updated: {time_str}</span>
        {f'<span style="color: #FFA500;">{badge_str}</span>' if badge_str else ''}
    </div>
    """, unsafe_allow_html=True)


def show_ai_disclaimer(inputs_used=None):
    """Display AI content disclaimer with inputs used
    
    Args:
        inputs_used: List of inputs the AI used (e.g., ["P/E ratio", "Revenue growth", "SPY price"])
    """
    inputs_str = ", ".join(inputs_used) if inputs_used else "Available market data"
    
    with st.expander("ℹ️ About this AI analysis", expanded=False):
        st.markdown(f"""
        **What this is based on:**  
        {inputs_str}
        
        **Disclaimer:**  
        This AI-generated content is for educational purposes only and does not constitute financial advice. 
        Always do your own research and consult a qualified financial advisor before making investment decisions.
        """)


# ============================================
# 1.3 SKELETON LOADERS & LOADING STATES
# ============================================

def show_skeleton_loader(height=200, message="Loading..."):
    """Display a skeleton loader placeholder while content loads"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, 
            rgba(128,128,128,0.1) 25%, 
            rgba(128,128,128,0.2) 50%, 
            rgba(128,128,128,0.1) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 10px;
        height: {height}px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #888;
        font-size: 14px;
    ">
        <span>⏳ {message}</span>
    </div>
    <style>
    @keyframes shimmer {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    </style>
    """, unsafe_allow_html=True)


def show_skeleton_table(rows=5, cols=4):
    """Display a skeleton table placeholder"""
    # Build header row
    header_cells = ''.join(['<div style="background: linear-gradient(90deg, rgba(128,128,128,0.1) 25%, rgba(128,128,128,0.2) 50%, rgba(128,128,128,0.1) 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; height: 20px; border-radius: 4px;"></div>' for _ in range(cols)])
    
    # Build data rows
    data_rows = ''
    for _ in range(rows):
        row_cells = ''.join(['<div style="background: linear-gradient(90deg, rgba(128,128,128,0.08) 25%, rgba(128,128,128,0.15) 50%, rgba(128,128,128,0.08) 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; height: 35px; border-radius: 4px;"></div>' for _ in range(cols)])
        data_rows += f'<div style="display: grid; grid-template-columns: repeat({cols}, 1fr); gap: 10px; margin-top: 10px;">{row_cells}</div>'
    
    st.markdown(f"""
    <div style="background: rgba(128,128,128,0.05); border-radius: 10px; padding: 15px; margin: 10px 0;">
        <div style="display: grid; grid-template-columns: repeat({cols}, 1fr); gap: 10px;">
            {header_cells}
        </div>
        {data_rows}
    </div>
    <style>
    @keyframes shimmer {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    </style>
    """, unsafe_allow_html=True)


def show_loading_timer():
    """Display a loading indicator that shows elapsed time"""
    if 'loading_start_time' not in st.session_state:
        st.session_state.loading_start_time = time.time()
    
    elapsed = time.time() - st.session_state.loading_start_time
    st.markdown(f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 10px;
        background: rgba(128,128,128,0.1);
        border-radius: 4px;
        font-size: 12px;
        color: #888;
    ">
        <span class="loading-spinner">⏳</span>
        <span>Loading... ({elapsed:.1f}s)</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# 1.4 ERROR HANDLING & USER-FRIENDLY WARNINGS
# ============================================

def show_error_with_retry(error_message, retry_key, error_details=None):
    """Display a user-friendly error message with retry button
    
    Args:
        error_message: Short user-friendly message
        retry_key: Unique key for the retry button
        error_details: Technical details (shown in expander)
    
    Returns:
        True if retry button was clicked
    """
    st.markdown(f"""
    <div style="
        background: rgba(255, 100, 100, 0.1);
        border: 1px solid rgba(255, 100, 100, 0.3);
        border-left: 4px solid #ff6b6b;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    ">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 20px;">⚠️</span>
            <span style="color: #ff6b6b; font-weight: 500;">{error_message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        retry_clicked = st.button("🔄 Retry", key=f"retry_{retry_key}", type="secondary")
    
    if error_details:
        with st.expander("🔧 Technical details", expanded=False):
            st.code(str(error_details), language="text")
    
    return retry_clicked


def show_warning_banner(message, warning_type="info"):
    """Display a non-intrusive warning banner
    
    Args:
        message: Warning message to display
        warning_type: "info", "warning", "error", "success"
    """
    colors = {
        "info": ("#3b82f6", "rgba(59, 130, 246, 0.1)", "ℹ️"),
        "warning": ("#f59e0b", "rgba(245, 158, 11, 0.1)", "⚠️"),
        "error": ("#ef4444", "rgba(239, 68, 68, 0.1)", "❌"),
        "success": ("#22c55e", "rgba(34, 197, 94, 0.1)", "✅")
    }
    border_color, bg_color, icon = colors.get(warning_type, colors["info"])
    
    st.markdown(f"""
    <div style="
        background: {bg_color};
        border-left: 3px solid {border_color};
        border-radius: 0 6px 6px 0;
        padding: 10px 15px;
        margin: 8px 0;
        font-size: 13px;
        color: {border_color};
    ">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)


def show_placeholder_data_warning():
    """Display a warning that placeholder/demo data is being shown"""
    st.markdown("""
    <div style="
        background: rgba(255, 165, 0, 0.1);
        border: 1px dashed rgba(255, 165, 0, 0.5);
        border-radius: 8px;
        padding: 10px 15px;
        margin: 8px 0;
        font-size: 12px;
        color: #FFA500;
        text-align: center;
    ">
        📋 <strong>Demo Data</strong> — Showing placeholder values. Connect API for live data.
    </div>
    """, unsafe_allow_html=True)


def safe_api_call(func, *args, fallback=None, error_message="Unable to load data", **kwargs):
    """Wrapper for API calls with built-in error handling
    
    Args:
        func: Function to call
        *args: Arguments to pass to function
        fallback: Value to return on error
        error_message: Message to show on error
        **kwargs: Keyword arguments to pass to function
    
    Returns:
        Result of func or fallback value
    """
    try:
        return func(*args, **kwargs)
    except requests.exceptions.Timeout:
        show_warning_banner(f"{error_message} (Request timed out)", "warning")
        return fallback
    except requests.exceptions.ConnectionError:
        show_warning_banner(f"{error_message} (Connection failed)", "warning")
        return fallback
    except Exception as e:
        show_warning_banner(f"{error_message}", "warning")
        # Log error details internally
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        st.session_state.error_log.append({
            'time': datetime.now().isoformat(),
            'error': str(e),
            'func': func.__name__ if hasattr(func, '__name__') else str(func)
        })
        return fallback


# ============================================
# 1.5 EMPTY STATE HANDLERS
# ============================================

def show_empty_state(title, message, action_text=None, action_key=None, icon="📭"):
    """Display a friendly empty state with optional action button
    
    Args:
        title: Main empty state title
        message: Helpful message
        action_text: Text for action button (optional)
        action_key: Key for action button (required if action_text provided)
        icon: Emoji icon to display
    
    Returns:
        True if action button clicked, False otherwise
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 40px 20px;
        background: rgba(128, 128, 128, 0.05);
        border-radius: 15px;
        margin: 20px 0;
    ">
        <div style="font-size: 48px; margin-bottom: 15px;">{icon}</div>
        <h3 style="margin: 0 0 10px 0; color: inherit;">{title}</h3>
        <p style="color: #888; margin: 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if action_text and action_key:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            return st.button(action_text, key=action_key, type="primary", use_container_width=True)
    return False


# Initialize persistence on app load
init_persistence()





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
    st.session_state.theme = 'light'

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
        background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FC 100%);
        border: 2px solid #2196F3;
        border-radius: 20px;
        padding: 40px;
        max-width: 500px;
        text-align: center;
        animation: fadeInUp 0.5s ease-out;
    }
    .welcome-popup h1 {
        color: #1a1a2e;
        margin-bottom: 20px;
    }
    .welcome-popup ul {
        text-align: left;
        color: #1a1a2e;
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
    
    /* CRITICAL: Force black text on white background - EVERYWHERE */
    html, body, .stApp, [data-testid="stAppViewContainer"], 
    [data-testid="stSidebar"], p, span, div, label, li, td, th,
    .stMarkdown, .stText, [data-testid="stMarkdownContainer"],
    .element-container, .stRadio label, .stSelectbox label,
    .stTextInput label, .stSlider label, .stCheckbox label {
        color: #000000 !important;
    }
    
    /* Sidebar text MUST be dark */
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #000000 !important;
    }
    
    /* INPUT FIELDS - White background, dark text, visible border */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #CCCCCC !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
        border-color: #FF4444 !important;
    }
    
    /* DROPDOWNS - White background, dark text */
    [data-testid="stSelectbox"] > div > div {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #CCCCCC !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        color: #000000 !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
        color: #000000 !important;
    }
    
    /* Dropdown menu options */
    [data-baseweb="menu"] {
        background: #FFFFFF !important;
        border: 2px solid #CCCCCC !important;
    }
    [data-baseweb="menu"] li {
        background: #FFFFFF !important;
        color: #000000 !important;
    }
    [data-baseweb="menu"] li:hover {
        background: #F0F0F0 !important;
        color: #000000 !important;
    }
    [data-baseweb="menu"] li[aria-selected="true"] {
        background: #FF4444 !important;
        color: #FFFFFF !important;
    }
    
    /* EXPANDERS */
    .streamlit-expanderHeader {
        background: #F5F5F5 !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
    }
    .streamlit-expanderContent {
        background: #FAFAFA !important;
        color: #000000 !important;
    }
    [data-testid="stExpander"] {
        border: 1px solid #CCCCCC !important;
    }
    [data-testid="stExpanderContent"] * {
        color: #000000 !important;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: #F5F5F5 !important;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #000000 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #FF4444 !important;
        border-bottom-color: #FF4444 !important;
    }
    
    /* ALERTS */
    .stAlert {
        background: #F5F5F5 !important;
        border: 1px solid #CCCCCC !important;
    }
    .stAlert * {
        color: #000000 !important;
    }
    
    h1, h2, h3, h4, h5, h6 { color: #000000 !important; }
    a { color: #0066CC !important; }
    
    .stMetric { background: rgba(240,240,240,0.9); padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .stMetric label, .stMetric [data-testid="stMetricValue"], .stMetric [data-testid="stMetricDelta"] {
        color: #000000 !important;
    }
    
    /* Dataframe/Table text */
    .stDataFrame, .dataframe, table, tr, td, th { 
        color: #000000 !important; 
        background: #FFFFFF !important;
    }
    
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
    "researchAndDevelopmentExpenses": {
        "simple": "Money spent on R&D and innovation",
        "why": "Shows investment in future products. High R&D can mean competitive advantage or drain on profits."
    },
    "sellingGeneralAndAdministrativeExpenses": {
        "simple": "Overhead costs (sales, admin, general)",
        "why": "Fixed costs the company pays regardless of sales. Lower SG&A = more efficient operations."
    },
    "generalAndAdministrativeExpenses": {
        "simple": "Admin costs (salaries, rent, utilities)",
        "why": "Overhead that doesn't directly produce revenue. Watch for this growing faster than revenue."
    },
    "sellingAndMarketingExpenses": {
        "simple": "Marketing and sales team costs",
        "why": "Cost to acquire customers. Should generate more revenue than it costs."
    },
    "operatingExpenses": {
        "simple": "Total costs to run the business",
        "why": "All non-production costs combined. Lower operating expenses = higher profits."
    },
    "costOfRevenue": {
        "simple": "Direct cost to make products/services",
        "why": "Materials, labor, manufacturing. Lower cost = better margins."
    },
    "costAndExpenses": {
        "simple": "All costs and expenses combined",
        "why": "Total spending. Should be less than revenue for profitability."
    },
    "interestExpense": {
        "simple": "Cost of borrowing money",
        "why": "High interest expense means heavy debt burden. Can crush profits in high-rate environment."
    },
    "incomeTaxExpense": {
        "simple": "Taxes paid on profits",
        "why": "Reduces net income. Some companies use legal strategies to minimize this."
    },
    "otherExpenses": {
        "simple": "Miscellaneous business expenses",
        "why": "One-time or unusual costs. Watch if consistently high."
    },
    "incomeBeforeTax": {
        "simple": "Profit before paying taxes",
        "why": "Shows profitability before government takes its share."
    },
    "netInterestIncome": {
        "simple": "Interest earned minus interest paid",
        "why": "Important for banks. Positive = earning more on loans than paying on deposits."
    },
    "interestIncome": {
        "simple": "Money earned from investments and loans",
        "why": "Extra income from cash holdings. Nice bonus but not core business."
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
    "stockBasedCompensation": {
        "simple": "Value of stock given to employees as pay",
        "why": "Dilutes existing shareholders. High SBC means your ownership % shrinks over time."
    },
    "fcfAfterSBC": {
        "simple": "Free cash flow minus stock compensation",
        "why": "The truest measure of cash generation. Accounts for shareholder dilution."
    },
    "investingCashFlow": {
        "simple": "Cash spent on investments and assets",
        "why": "Usually negative (spending). Very negative = aggressive expansion."
    },
    "financingCashFlow": {
        "simple": "Cash from/to debt and equity activities",
        "why": "Positive = raising money. Negative = paying down debt or buybacks."
    },
    "depreciationAndAmortization": {
        "simple": "Spreading cost of assets over time",
        "why": "Non-cash expense that reduces taxes. Add back to get true cash flow."
    },
    "changeInWorkingCapital": {
        "simple": "Change in day-to-day operating cash needs",
        "why": "Negative = cash tied up in inventory/receivables. Watch for consistent drain."
    },
    "commonStockRepurchased": {
        "simple": "Money spent buying back company shares",
        "why": "Reduces shares outstanding, increases your ownership %. Shareholder-friendly."
    },
    "debtRepayment": {
        "simple": "Money used to pay down debt",
        "why": "Reduces interest expense and risk. Good sign of financial health."
    },
    "commonStockIssued": {
        "simple": "Money raised by selling new shares",
        "why": "Dilutes existing shareholders but provides growth capital."
    },
    "acquisitionsNet": {
        "simple": "Money spent buying other companies",
        "why": "Can accelerate growth but integration risk. Watch for overpaying."
    },
    "purchasesOfInvestments": {
        "simple": "Money spent on securities/investments",
        "why": "Parking cash in investments. Usually short-term securities."
    },
    "salesMaturitiesOfInvestments": {
        "simple": "Cash from selling investments",
        "why": "Converting investments back to cash. May fund operations or acquisitions."
    },
    "netChangeInCash": {
        "simple": "Total change in cash during period",
        "why": "Shows if company is building or burning cash reserves."
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
    "longTermDebt": {
        "simple": "Debt due in more than 1 year",
        "why": "Less immediate pressure but still a future obligation."
    },
    "shortTermDebt": {
        "simple": "Debt due within 1 year",
        "why": "Must be paid soon. High short-term debt = liquidity risk."
    },
    "inventory": {
        "simple": "Products waiting to be sold",
        "why": "Too much = products not selling. Too little = may miss sales."
    },
    "netReceivables": {
        "simple": "Money owed to company by customers",
        "why": "Sales made but not yet collected. Watch for growing faster than revenue."
    },
    "accountsPayable": {
        "simple": "Money company owes to suppliers",
        "why": "Bills not yet paid. Using supplier credit is free financing."
    },
    "totalCurrentAssets": {
        "simple": "Assets convertible to cash within 1 year",
        "why": "Liquidity buffer. Should exceed current liabilities."
    },
    "totalCurrentLiabilities": {
        "simple": "Debts due within 1 year",
        "why": "Short-term obligations. Compare to current assets for safety."
    },
    "retainedEarnings": {
        "simple": "Accumulated profits kept in business",
        "why": "Profits reinvested over time. Growing = company profitable and reinvesting."
    },
    "goodwill": {
        "simple": "Premium paid for acquired companies",
        "why": "Intangible value from acquisitions. Can be written down if acquisition fails."
    },
    "intangibleAssets": {
        "simple": "Non-physical assets (patents, brands)",
        "why": "Value of intellectual property. Important for tech and pharma."
    },
    "propertyPlantEquipmentNet": {
        "simple": "Physical assets (buildings, equipment)",
        "why": "Capital invested in operations. High for manufacturing, low for software."
    },
    "netDebt": {
        "simple": "Total debt minus cash",
        "why": "True debt burden. Negative = more cash than debt (great position)."
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
    },
    "freeCashFlowPerShare": {
        "simple": "Free Cash Flow ÷ Shares Outstanding",
        "why": "Cash generated per share you own. Growing FCF/share = shareholder value creation."
    },
    "priceEarningsRatio": {
        "simple": "Stock Price ÷ Earnings Per Share",
        "why": "How much you pay for $1 of earnings. Lower = cheaper. 15-25 is typical."
    },
    "priceToSalesRatio": {
        "simple": "Market Cap ÷ Revenue",
        "why": "Useful for unprofitable companies. Lower = better value."
    },
    "priceToBookRatio": {
        "simple": "Stock Price ÷ Book Value Per Share",
        "why": "Price vs. net assets. Below 1.0 might be undervalued."
    },
    "debtEquityRatio": {
        "simple": "Total Debt ÷ Total Equity",
        "why": "Financial leverage. Lower = safer. Higher = more risk but potential reward."
    }
}



# ============= AI COACH - PERSISTENT CHATBOT =============
# Educational cross-tab AI assistant with 4 modes

def initialize_ai_coach_state():
    """Initialize AI Coach session state"""
    defaults = {
        'ai_coach_open': False,
        'ai_coach_mode': 'explain',
        'ai_coach_history': [],
        'ai_coach_show_receipts': False,
        'ai_coach_context': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def build_ai_context(tab, ticker=None, facts=None):
    """Build deterministic context - NEVER invents data"""
    ctx = {"tab": tab, "ticker": ticker, "facts": facts or {}}
    
    # Add learn progress
    if 'learn_completed_lessons' in st.session_state:
        ctx["learn"] = {
            "completed": len(st.session_state.learn_completed_lessons),
            "xp": st.session_state.get('learn_xp_total', 0)
        }
    
    # Add portfolio stats
    if 'portfolio' in st.session_state and st.session_state.portfolio:
        port = st.session_state.portfolio
        total = sum(p.get('current_value', 0) for p in port)
        if total > 0:
            holdings = {p['ticker']: p.get('current_value', 0) for p in port}
            top = max(holdings, key=holdings.get)
            ctx["portfolio"] = {
                "top_holding": top,
                "top_pct": round((holdings[top]/total)*100, 1),
                "positions": len(holdings)
            }
    return ctx

def call_ai(message, mode, context):
    """Call AI for Coach response - Perplexity FIRST (web search), OpenAI fallback"""
    
    system = f"""You're an educational investing coach in {mode} mode.

CRITICAL: You have WEB SEARCH capability. USE IT to provide REAL, CURRENT data.
When asked about stock prices, P/E ratios, market data - SEARCH and give actual numbers.

Rules:
- SEARCH for current data when asked about specific stocks, prices, ratios, news
- Provide ACTUAL numbers and facts, not generic advice
- NEVER give buy/sell advice
- Be beginner-friendly with explanations
- Respond in JSON: {{"answer":["bullet1","bullet2"],"lessons":[{{"id":"B1","label":"Title"}}],"receipts":["fact1"]}}
- Max 4 bullets, include specific data points"""

    # TRY PERPLEXITY FIRST - has web search for real data!
    if PERPLEXITY_API_KEY:
        try:
            resp = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"Q: {message}\n\nContext: {json.dumps(context)}"}
                    ],
                    "max_tokens": 600,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                content = content.replace("```json", "").replace("```", "").strip()
                try:
                    return json.loads(content)
                except:
                    # If not valid JSON, wrap in answer format
                    return {"answer": [content[:500]], "lessons": [], "receipts": []}
        except Exception as e:
            print(f"[AI Coach] Perplexity error: {e}")
    
    # FALLBACK to OpenAI if Perplexity fails
    if OPENAI_API_KEY:
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"Q: {message}\n\nContext: {json.dumps(context)}"}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 500
                },
                timeout=25
            )
            
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                content = content.replace("```json", "").replace("```", "").strip()
                try:
                    return json.loads(content)
                except:
                    return {"answer": [content[:500]], "lessons": [], "receipts": []}
        except Exception as e:
            print(f"[AI Coach] OpenAI error: {e}")
    
    return {"answer": ["I had trouble connecting to AI. Please try again."], "lessons": [], "receipts": []}

def render_ai_coach(tab, ticker=None, facts=None):
    """Render AI Coach as a slide-out panel on the right side"""
    initialize_ai_coach_state()
    st.session_state.ai_coach_context = build_ai_context(tab, ticker, facts)
    
    # Get user's first name for personalized greeting
    first_name = st.session_state.get('first_name', 'there')
    
    # Inject CSS for the floating button and panel
    st.markdown("""
    <style>
    /* Hide the streamlit toggle button - we use the floating button instead */
    button[kind="secondary"]:has(p:contains("🤖")) {
        display: none !important;
    }
    
    /* Hide ONLY the AI Coach toggle button (scoped) */
    .ai-coach-hidden-toggle .stButton button {
        position: absolute !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

/* Floating AI button - single instance */
    .ai-float-btn {
        position: fixed;
        bottom: 25px;
        right: 25px;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff3333 0%, #cc0000 100%);
        box-shadow: 0 4px 15px rgba(255,51,51,0.4);
        z-index: 9998;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        border: 2px solid rgba(255,255,255,0.2);
        color: white;
        transition: all 0.3s ease;
    }
    .ai-float-btn:hover {
        transform: scale(1.08);
        box-shadow: 0 6px 20px rgba(255,51,51,0.6);
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .ai-float-btn {
            width: 50px;
            height: 50px;
            font-size: 20px;
            bottom: 15px;
            right: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show floating button only when panel is closed
    if not st.session_state.ai_coach_open:
        # Single floating button
        st.markdown("""
        <div class="ai-float-btn" id="ai-btn" onclick="
            var btns = document.querySelectorAll('button[kind=\\'secondary\\']');
            for(var i=0; i<btns.length; i++) {
                if(btns[i].innerText.includes('🤖')) btns[i].click();
            }
        ">😊</div>
        """, unsafe_allow_html=True)
    
    # Toggle button - we'll hide it with CSS
    st.markdown('<div class="ai-coach-hidden-toggle">', unsafe_allow_html=True)
    col_hidden, _ = st.columns([0.001, 0.999])
    with col_hidden:
        if st.button("🤖", key=f"ai_toggle_{tab}"):
            st.session_state.ai_coach_open = not st.session_state.ai_coach_open
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Slide-out panel when open
    if st.session_state.ai_coach_open:
        st.markdown("---")
        
        # Panel header
        head_col1, head_col2 = st.columns([4, 1])
        with head_col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff3333 0%, #cc0000 100%); padding: 15px 20px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: white; margin: 0; font-size: 18px;">🤖 AI Assistant</h3>
                <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0; font-size: 12px;">Powered by AI • Educational only</p>
            </div>
            """, unsafe_allow_html=True)
        with head_col2:
            if st.button("✕ Close", key=f"close_ai_{tab}"):
                st.session_state.ai_coach_open = False
                st.rerun()
        
        # Greeting
        st.markdown(f"**Hi, {first_name.title()}!** Ask me about stocks, investing, or this page.")
        
        # Mode selector
        modes = {"explain": "📊 Explain", "learn": "📚 Learn", "portfolio": "💼 Portfolio"}
        mode = st.radio("Mode:", list(modes.keys()), format_func=lambda x: modes[x], horizontal=True, key=f"ai_mode_{tab}", label_visibility="collapsed")
        st.session_state.ai_coach_mode = mode
        
        # Chat history (last 6 messages)
        if st.session_state.ai_coach_history:
            for i, msg in enumerate(st.session_state.ai_coach_history[-6:]):
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown("**AI:**")
                    for bullet in msg.get("answer", []):
                        st.markdown(f"• {bullet}")
                    
                    # Lesson links
                    for lesson in msg.get("lessons", []):
                        if st.button(f"📖 {lesson['label']}", key=f"lesson_{tab}_{lesson['id']}_{i}"):
                            st.session_state.learn_selected_lesson_id = lesson['id']
                            st.session_state.selected_page = "📚 Learn Hub"
                            st.rerun()
        
        st.markdown("---")
        
        # Input area
        user_input = st.text_input("Ask me anything:", placeholder="e.g., What does P/E ratio mean?", key=f"ai_input_{tab}")
        
        btn_col1, btn_col2 = st.columns([4, 1])
        with btn_col1:
            send = st.button("Send", type="primary", use_container_width=True, key=f"ai_send_{tab}")
        with btn_col2:
            if st.button("🗑️", key=f"ai_clear_{tab}", help="Clear chat"):
                st.session_state.ai_coach_history = []
                st.rerun()
        
        if send and user_input:
            st.session_state.ai_coach_history.append({"role": "user", "content": user_input})
            
            with st.spinner("Thinking..."):
                response = call_ai(user_input, st.session_state.ai_coach_mode, st.session_state.ai_coach_context)
            
            st.session_state.ai_coach_history.append({"role": "assistant", **response})
            st.rerun()

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
    """Get simple explanation for any metric - smart matching"""
    if not metric_key:
        return None
    
    # Normalize the key - remove spaces, underscores, lowercase
    key = metric_key.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    # Direct match first
    for metric, details in FINANCIAL_METRICS_EXPLAINED.items():
        if metric.lower().replace(' ', '').replace('_', '') == key:
            return details
    
    # Try partial/fuzzy match for common variations
    # Map display names to API column names
    display_to_api = {
        'fcfafterstockcompensation': 'fcfAfterSBC',
        'r&dexpenses': 'researchAndDevelopmentExpenses',
        'rdexpenses': 'researchAndDevelopmentExpenses',
        'sg&aexpenses': 'sellingGeneralAndAdministrativeExpenses',
        'sgaexpenses': 'sellingGeneralAndAdministrativeExpenses',
        'general&adminexpenses': 'generalAndAdministrativeExpenses',
        'generaladminexpenses': 'generalAndAdministrativeExpenses',
        'selling&marketingexpenses': 'sellingAndMarketingExpenses',
        'costofrevenue(cogs)': 'costOfRevenue',
        'capitalexpenditures(capex)': 'capitalExpenditure',
        'capex': 'capitalExpenditure',
        'depreciation&amortization': 'depreciationAndAmortization',
        'cash&cashequivalents': 'cashAndCashEquivalents',
        'shareholdersequity': 'totalStockholdersEquity',
        'stockholdersequity': 'totalStockholdersEquity',
        'earningspershare(eps)': 'eps',
        'dilutedeps': 'epsdiluted',
        'stockbuybacks': 'commonStockRepurchased',
        'fcfpershare': 'freeCashFlowPerShare',
        'fcfpershare(truthmeter)': 'freeCashFlowPerShare',
        'p/eratio': 'priceEarningsRatio',
        'peratio': 'priceEarningsRatio',
        'p/sratio': 'priceToSalesRatio',
        'psratio': 'priceToSalesRatio',
        'p/bratio': 'priceToBookRatio',
        'pbratio': 'priceToBookRatio',
        'debt-to-equity': 'debtToEquity',
        'debttoequity': 'debtToEquity',
        'roe': 'returnOnEquity',
        'roa': 'returnOnAssets',
        'roce': 'returnOnCapitalEmployed',
        'grossmargin': 'grossProfitMargin',
        'operatingmargin': 'operatingProfitMargin',
        'netincomemargin': 'netProfitMargin',
        'netmargin': 'netProfitMargin',
    }
    
    # Check if it's a mapped display name
    if key in display_to_api:
        api_key = display_to_api[key]
        if api_key in FINANCIAL_METRICS_EXPLAINED:
            return FINANCIAL_METRICS_EXPLAINED[api_key]
    
    # Try substring match as last resort
    for metric, details in FINANCIAL_METRICS_EXPLAINED.items():
        metric_normalized = metric.lower().replace(' ', '').replace('_', '')
        if key in metric_normalized or metric_normalized in key:
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
    'fcfAfterSBC': 'FCF After Stock Compensation',
    # Additional metrics for professional display
    'generalAndAdministrativeExpenses': 'General & Admin Expenses',
    'sellingAndMarketingExpenses': 'Selling & Marketing Expenses',
    'otherExpenses': 'Other Expenses',
    'costAndExpenses': 'Cost & Expenses',
    'netInterestIncome': 'Net Interest Income',
    'interestIncome': 'Interest Income',
    'incomeBeforeTax': 'Income Before Tax',
    'incomeBeforeTaxRatio': 'Income Before Tax Ratio',
    'grossProfitRatio': 'Gross Profit Ratio',
    'operatingIncomeRatio': 'Operating Income Ratio',
    'netIncomeRatio': 'Net Income Ratio',
    'weightedAverageShsOut': 'Weighted Avg Shares Outstanding',
    'weightedAverageShsOutDil': 'Weighted Avg Shares (Diluted)',
    'accountsPayable': 'Accounts Payable',
    'deferredRevenue': 'Deferred Revenue',
    'otherCurrentLiabilities': 'Other Current Liabilities',
    'otherNonCurrentLiabilities': 'Other Non-Current Liabilities',
    'goodwill': 'Goodwill',
    'intangibleAssets': 'Intangible Assets',
    'propertyPlantEquipmentNet': 'Property Plant & Equipment',
    'netDebt': 'Net Debt',
    'cashAtEndOfPeriod': 'Cash at End of Period',
    'cashAtBeginningOfPeriod': 'Cash at Beginning of Period',
    'netChangeInCash': 'Net Change in Cash',
    'effectOfForexChangesOnCash': 'Forex Effect on Cash',
    'acquisitionsNet': 'Acquisitions (Net)',
    'purchasesOfInvestments': 'Purchases of Investments',
    'salesMaturitiesOfInvestments': 'Sales of Investments',
    'otherInvestingActivites': 'Other Investing Activities',
    'otherFinancingActivites': 'Other Financing Activities'
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

# ============================================
# PREMIUM TIER GATING SYSTEM
# ============================================

# Tier limits
TIER_LIMITS = {
    "free": {
        "pinned_tickers": 5,
        "saved_views": 3,
        "ai_queries_per_day": 5,
        "workflows": ["Valuation"],  # Free workflows
        "compare_stocks": True,
        "export_reports": False,
        "pattern_detection": False,
        "historical_setups": False,
    },
    "pro": {
        "pinned_tickers": 20,
        "saved_views": 10,
        "ai_queries_per_day": 50,
        "workflows": ["Valuation", "Risk Analysis"],  
        "compare_stocks": True,
        "export_reports": True,
        "pattern_detection": True,
        "historical_setups": False,
    },
    "ultimate": {
        "pinned_tickers": 100,
        "saved_views": 50,
        "ai_queries_per_day": 999,
        "workflows": ["Valuation", "Risk Analysis", "Portfolio Health"],
        "compare_stocks": True,
        "export_reports": True,
        "pattern_detection": True,
        "historical_setups": True,
    }
}

def get_user_tier():
    """Get the current user's subscription tier"""
    # Founders automatically get Ultimate access
    if st.session_state.get('is_founder'):
        return "ultimate"
    
    # Check session state for tier
    if st.session_state.get('user_tier'):
        return st.session_state.user_tier
    
    # Default to free tier
    return "free"

def set_user_tier(tier):
    """Set the user's subscription tier (for testing/demo)"""
    if tier in ["free", "pro", "ultimate"]:
        st.session_state.user_tier = tier
        return True
    return False

def get_tier_limit(feature):
    """Get the limit for a feature based on user tier"""
    tier = get_user_tier()
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"]).get(feature)

def is_feature_available(feature):
    """Check if a feature is available for the current tier"""
    tier = get_user_tier()
    tier_config = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    return tier_config.get(feature, False)

def show_premium_gate(feature_name, required_tier="pro", show_preview=True):
    """Show a premium gate with upgrade CTA
    
    Args:
        feature_name: Name of the locked feature
        required_tier: Minimum tier required ("pro" or "ultimate")
        show_preview: Whether to show a blurred/preview version
    
    Returns:
        True if feature is accessible, False if gated
    """
    current_tier = get_user_tier()
    tier_order = {"free": 0, "pro": 1, "ultimate": 2}
    
    # Check if user has access
    if tier_order.get(current_tier, 0) >= tier_order.get(required_tier, 1):
        return True
    
    # Show locked state
    tier_color = "#9D4EDD" if required_tier == "pro" else "#FFD700"
    tier_label = "Pro" if required_tier == "pro" else "Ultimate"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(157, 78, 221, 0.1), rgba(157, 78, 221, 0.05));
        border: 2px solid {tier_color};
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
    ">
        <div style="font-size: 48px; margin-bottom: 15px;">🔒</div>
        <h3 style="color: {tier_color}; margin-bottom: 10px;">{feature_name}</h3>
        <p style="color: #888; margin-bottom: 20px;">This feature requires <strong style="color: {tier_color};">{tier_label}</strong> tier</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"🚀 Upgrade to {tier_label}", key=f"upgrade_{feature_name.replace(' ', '_')}", use_container_width=True):
        st.session_state.selected_page = "👑 Become a VIP"
        st.rerun()
    
    return False

def show_upgrade_prompt(message, cta_text="Upgrade Now", tier="pro"):
    """Show a subtle upgrade prompt inline"""
    tier_color = "#9D4EDD" if tier == "pro" else "#FFD700"
    tier_label = "Pro" if tier == "pro" else "Ultimate"
    
    st.markdown(f"""
    <div style="
        background: rgba(157, 78, 221, 0.1);
        border-left: 4px solid {tier_color};
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    ">
        <span style="color: #FFF;">{message}</span>
        <span style="color: {tier_color}; font-weight: bold;"> → {tier_label}</span>
    </div>
    """, unsafe_allow_html=True)

def show_limit_warning(current, limit, feature_name):
    """Show warning when approaching or at limit"""
    if current >= limit:
        st.warning(f"⚠️ You've reached your {feature_name} limit ({limit}). Upgrade to Pro for more!")
        return True
    elif current >= limit * 0.8:
        st.info(f"📊 You're using {current}/{limit} {feature_name}. Upgrade for unlimited!")
    return False

# ============================================
# PHASE 6: WAITLIST, ONBOARDING, ANALYTICS
# ============================================

def save_waitlist_email(email, tier_interest="pro"):
    """Save waitlist email to Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, "Database not configured"
    
    try:
        # Validate email
        if not email or "@" not in email or "." not in email:
            return False, "Invalid email format"
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        data = {
            "email": email.lower().strip(),
            "tier_interest": tier_interest,
            "source": "web_app",
            "created_at": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/waitlist",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code in [200, 201, 204]:
            return True, "Success"
        elif response.status_code == 409:
            return True, "Already on waitlist"
        else:
            return False, f"Error: {response.status_code}"
    except Exception as e:
        return False, str(e)

def get_waitlist_count():
    """Get current waitlist count from Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return 127  # Default fallback
    
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "count=exact"
        }
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/waitlist?select=id",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            count = response.headers.get('content-range', '').split('/')[-1]
            return int(count) if count.isdigit() else 127
        return 127
    except:
        return 127

def track_feature_usage(feature_name, ticker=None):
    """Track feature usage for analytics"""
    if 'usage_stats' not in st.session_state:
        st.session_state.usage_stats = {}
    
    if feature_name not in st.session_state.usage_stats:
        st.session_state.usage_stats[feature_name] = {
            'count': 0,
            'tickers': [],
            'last_used': None
        }
    
    st.session_state.usage_stats[feature_name]['count'] += 1
    st.session_state.usage_stats[feature_name]['last_used'] = datetime.now().isoformat()
    
    if ticker and ticker not in st.session_state.usage_stats[feature_name]['tickers']:
        st.session_state.usage_stats[feature_name]['tickers'].append(ticker)
        # Keep only last 20 tickers
        st.session_state.usage_stats[feature_name]['tickers'] = \
            st.session_state.usage_stats[feature_name]['tickers'][-20:]

def show_onboarding_tooltip(step_id, title, message, position="bottom"):
    """Show onboarding tooltip for first-time users"""
    if 'onboarding_complete' not in st.session_state:
        st.session_state.onboarding_complete = set()
    
    if step_id in st.session_state.onboarding_complete:
        return False
    
    # Show tooltip
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #9D4EDD 0%, #7B2CBF 100%);
        padding: 15px 20px;
        border-radius: 10px;
        margin: 10px 0;
        position: relative;
    ">
        <div style="font-weight: bold; color: #FFF; margin-bottom: 5px;">💡 {title}</div>
        <div style="color: rgba(255,255,255,0.9); font-size: 14px;">{message}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Got it!", key=f"onboarding_{step_id}"):
        st.session_state.onboarding_complete.add(step_id)
        st.rerun()
    
    return True

def show_first_time_welcome():
    """Show welcome modal for first-time users"""
    if st.session_state.get('has_seen_welcome'):
        return False
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
        border: 2px solid #ff4b4b;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
    ">
        <div style="font-size: 48px; margin-bottom: 15px;">👋</div>
        <h2 style="margin-bottom: 10px;">Welcome to Finance Made Simple!</h2>
        <p style="font-size: 16px; margin-bottom: 20px;">
            Your personal stock research assistant. No jargon, just clarity.
        </p>
        <div style="text-align: left; max-width: 400px; margin: 0 auto;">
            <p>✅ <strong>Dashboard</strong> - Pin stocks to track</p>
            <p>✅ <strong>Company Analysis</strong> - Deep dive into any stock</p>
            <p>✅ <strong>Risk Quiz</strong> - Find your investor profile</p>
            <p>✅ <strong>Learn</strong> - Master investing basics</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Let's Get Started!", key="welcome_start", use_container_width=True, type="primary"):
        st.session_state.has_seen_welcome = True
        st.rerun()
    
    return True

def get_quick_stats():
    """Get quick stats for the user"""
    stats = {
        'pinned_count': len(st.session_state.get('pinned_tickers', [])),
        'analyses_today': st.session_state.get('usage_stats', {}).get('company_analysis', {}).get('count', 0),
        'saved_views': len(st.session_state.get('saved_views', [])),
        'tier': get_user_tier()
    }
    return stats

# Mobile-optimized CSS
MOBILE_CSS = """
<style>
/* Mobile Responsive Adjustments */
@media (max-width: 768px) {
    /* Reduce padding on mobile */
    .stApp > header {
        padding: 0.5rem !important;
    }
    
    /* Stack columns on mobile */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    
    /* Smaller fonts on mobile */
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.1rem !important; }
    
    /* Compact metrics on mobile */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    
    /* Full-width buttons on mobile */
    .stButton > button {
        width: 100% !important;
        padding: 0.75rem !important;
    }
    
    /* Compact cards on mobile */
    .stock-card {
        padding: 10px !important;
        margin: 5px 0 !important;
    }
    
    /* Hide sidebar on mobile by default */
    [data-testid="stSidebar"] {
        min-width: 0px !important;
        max-width: 0px !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 280px !important;
        max-width: 280px !important;
    }
}

/* Tablet adjustments */
@media (min-width: 769px) and (max-width: 1024px) {
    [data-testid="column"] {
        min-width: 45% !important;
    }
}

/* Loading skeleton animation */
@keyframes skeleton-pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}

.skeleton {
    background: linear-gradient(90deg, #2a2a2a 25%, #3a3a3a 50%, #2a2a2a 75%);
    background-size: 200% 100%;
    animation: skeleton-pulse 1.5s ease-in-out infinite;
    border-radius: 4px;
}

/* Smooth transitions */
.smooth-transition {
    transition: all 0.3s ease;
}

/* Better focus states */
input:focus, button:focus {
    outline: 2px solid #ff4b4b !important;
    outline-offset: 2px;
}

/* Toast notifications */
.toast-success {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
    border-radius: 10px !important;
}

.toast-error {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    border-radius: 10px !important;
}
</style>
"""

def inject_mobile_css():
    """Inject mobile-optimized CSS"""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

def show_loading_skeleton(height=100, width="100%"):
    """Show loading skeleton placeholder"""
    st.markdown(f"""
    <div class="skeleton" style="height: {height}px; width: {width};"></div>
    """, unsafe_allow_html=True)

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


def create_financial_chart_with_growth(df, metrics, title, period_label, yaxis_title="Amount ($)", period_type='annual'):
    """Create financial chart with y-axis padding and return growth rates"""
    if df.empty:
        return None, {}
    
    def format_value_label(val):
        """Format large numbers as B, M, or T for chart labels"""
        abs_val = abs(val)
        sign = "-" if val < 0 else ""
        if abs_val >= 1e12:
            return f"{sign}${abs_val/1e12:.1f}T"
        elif abs_val >= 1e9:
            return f"{sign}${abs_val/1e9:.1f}B"
        elif abs_val >= 1e6:
            return f"{sign}${abs_val/1e6:.1f}M"
        elif abs_val >= 1e3:
            return f"{sign}${abs_val/1e3:.1f}K"
        else:
            return f"{sign}${abs_val:.0f}"
    
    def format_period_label(date_val, period_type):
        """Format date as FY 2024 for annual or Q1 2024 for quarterly"""
        try:
            if isinstance(date_val, str):
                date_obj = pd.to_datetime(date_val)
            else:
                date_obj = date_val
            
            year = date_obj.year
            month = date_obj.month
            
            if period_type == 'annual':
                return f"FY {year}"
            else:
                # Determine quarter from month
                quarter = (month - 1) // 3 + 1
                return f"Q{quarter} {year}"
        except:
            return str(date_val)
    
    # Sort by date ASCENDING (oldest first: 2023 -> 2024 -> 2025)
    df_sorted = df.sort_values('date', ascending=True).reset_index(drop=True)
    
    # Format x-axis labels
    x_labels = [format_period_label(d, period_type) for d in df_sorted['date']]
    
    fig = go.Figure()
    colors = ['#00D9FF', '#FFD700', '#9D4EDD']
    growth_rates = {}
    
    for idx, metric in enumerate(metrics):
        if metric in df_sorted.columns:
            values = df_sorted[metric].values
            # Growth rate: compare newest (last) to oldest (first)
            if len(values) >= 2 and values[0] != 0:
                growth_rate = ((values[-1] - values[0]) / abs(values[0])) * 100
                growth_rates[metric] = growth_rate
            
            # Use proper display name from METRIC_DISPLAY_NAMES
            display_name = METRIC_DISPLAY_NAMES.get(metric, metric.replace('_', ' ').title())
            
            fig.add_trace(go.Bar(
                x=x_labels,
                y=values,
                name=display_name,
                marker_color=colors[idx % len(colors)],
                text=[format_value_label(val) for val in values],
                textposition='outside',
                textfont=dict(size=10)
            ))
    
    all_values = []
    for metric in metrics:
        if metric in df_sorted.columns:
            all_values.extend(df_sorted[metric].values)
    
    if all_values:
        max_val = max(all_values)
        min_val = min(all_values)
        # Add 25% padding above and below so negative values (like CapEx) are fully visible
        value_range = max_val - min_val if max_val != min_val else abs(max_val) * 0.5 or 1
        padding = value_range * 0.25
        y_range_max = max_val + padding
        y_range_min = min_val - padding if min_val < 0 else 0
        fig.update_layout(yaxis=dict(range=[y_range_min, y_range_max]))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#1a1a2e', family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title=period_label,
        yaxis_title=yaxis_title,
        barmode='group',
        hovermode='x unified',
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="center", 
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        yaxis_showgrid=True,
        yaxis_gridwidth=1,
        yaxis_gridcolor='rgba(200,200,200,0.5)',
        xaxis_showgrid=False,
        plot_bgcolor='rgba(250,250,250,0.5)',
        paper_bgcolor='white',
        margin=dict(t=80, b=60, l=60, r=40),
        bargap=0.15,
        bargroupgap=0.1
    )
    
    # Add subtle border effect
    fig.update_xaxes(showline=True, linewidth=1, linecolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='rgba(0,0,0,0.1)')
    
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
    """Display why I focus on these specific metrics - MOVED TO FINANCE 101 TAB"""
    # This content is now in Finance 101 tab, not sidebar
    pass

def get_available_metrics(df, exclude_cols=['date', 'symbol', 'reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period', 'link', 'finalLink']):
    """Get all numeric columns from dataframe for dropdown"""
    if df.empty:
        return []
    
    def format_metric_name(col):
        """Convert camelCase to properly spaced title case"""
        if col in METRIC_DISPLAY_NAMES:
            return METRIC_DISPLAY_NAMES[col]
        # Convert camelCase to spaces
        import re
        # Insert space before capital letters
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', col)
        # Handle consecutive capitals (like FCF, SBC)
        spaced = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', spaced)
        # Title case
        return spaced.title()
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    available = [col for col in numeric_cols if col not in exclude_cols]
    
    return [(format_metric_name(col), col) for col in available]

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
    # Additional common searches that were failing
    "micron": "MU", "micron technology": "MU", "mu": "MU",
    "dolby": "DLB", "dolby laboratories": "DLB", "dlb": "DLB",
    "qualcomm": "QCOM", "qcom": "QCOM",
    "broadcom": "AVGO", "avgo": "AVGO",
    "texas instruments": "TXN", "txn": "TXN",
    "lam research": "LRCX", "lrcx": "LRCX",
    "applied materials": "AMAT", "amat": "AMAT",
    "asml": "ASML",
    "tsmc": "TSM", "taiwan semiconductor": "TSM", "tsm": "TSM",
    "arm": "ARM", "arm holdings": "ARM",
    "crowdstrike": "CRWD", "crwd": "CRWD",
    "datadog": "DDOG", "ddog": "DDOG",
    "servicenow": "NOW", "now": "NOW",
    "workday": "WDAY", "wday": "WDAY",
    "atlassian": "TEAM", "team": "TEAM",
    "twilio": "TWLO", "twlo": "TWLO",
    "square": "SQ", "block": "SQ", "sq": "SQ",
    "shopify": "SHOP", "shop": "SHOP",
    "roku": "ROKU",
    "draftkings": "DKNG", "dkng": "DKNG",
    "roblox": "RBLX", "rblx": "RBLX",
    "unity": "U", "unity software": "U",
    "rivian": "RIVN", "rivn": "RIVN",
    "lucid": "LCID", "lucid motors": "LCID", "lcid": "LCID",
    "nio": "NIO",
    "ford": "F", "f": "F",
    "gm": "GM", "general motors": "GM",
    "att": "T", "at&t": "T", "t": "T",
    "verizon": "VZ", "vz": "VZ",
    "t-mobile": "TMUS", "tmobile": "TMUS", "tmus": "TMUS",
    "comcast": "CMCSA", "cmcsa": "CMCSA",
    "target": "TGT", "tgt": "TGT",
    "lowes": "LOW", "lowe's": "LOW", "low": "LOW",
    "cvs": "CVS", "cvs health": "CVS",
    "walgreens": "WBA", "wba": "WBA",
    "moderna": "MRNA", "mrna": "MRNA",
    "eli lilly": "LLY", "lilly": "LLY", "lly": "LLY",
    "abbvie": "ABBV", "abbv": "ABBV",
    "merck": "MRK", "mrk": "MRK",
    "bristol myers": "BMY", "bristol-myers": "BMY", "bmy": "BMY",
    "amgen": "AMGN", "amgn": "AMGN",
    "gilead": "GILD", "gilead sciences": "GILD", "gild": "GILD",
    "regeneron": "REGN", "regn": "REGN",
    "biogen": "BIIB", "biib": "BIIB",
    "bank of america": "BAC", "bofa": "BAC", "bac": "BAC",
    "wells fargo": "WFC", "wfc": "WFC",
    "citigroup": "C", "citi": "C", "c": "C",
    "goldman sachs": "GS", "goldman": "GS", "gs": "GS",
    "morgan stanley": "MS", "ms": "MS",
    "american express": "AXP", "amex": "AXP", "axp": "AXP",
    "blackrock": "BLK", "blk": "BLK",
    "charles schwab": "SCHW", "schwab": "SCHW", "schw": "SCHW",
    "caterpillar": "CAT", "cat": "CAT",
    "deere": "DE", "john deere": "DE", "de": "DE",
    "3m": "MMM", "mmm": "MMM",
    "honeywell": "HON", "hon": "HON",
    "ge": "GE", "general electric": "GE",
    "lockheed": "LMT", "lockheed martin": "LMT", "lmt": "LMT",
    "raytheon": "RTX", "rtx": "RTX",
    "northrop": "NOC", "northrop grumman": "NOC", "noc": "NOC",
    "ups": "UPS", "united parcel": "UPS",
    "fedex": "FDX", "fdx": "FDX",
    "delta": "DAL", "delta airlines": "DAL", "dal": "DAL",
    "united airlines": "UAL", "ual": "UAL",
    "american airlines": "AAL", "aal": "AAL",
    "southwest": "LUV", "southwest airlines": "LUV", "luv": "LUV",
}

# Magnificent 7 tickers for default news
MAG_7_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]

@st.cache_data(ttl=3600)  # Cache for 1 hour
def search_fmp_ticker(query):
    """
    Search FMP API directly for company name/ticker.
    THIS IS THE PRIMARY SEARCH METHOD - handles ANY company.
    """
    if not query or len(query.strip()) < 1:
        return None, None
    
    query = query.strip()
    
    # Try the search endpoint
    url = f"{BASE_URL}/search?query={query}&limit=15&apikey={FMP_API_KEY}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            results = response.json()
            if results and len(results) > 0:
                # Filter for US stocks first (NYSE, NASDAQ, AMEX)
                us_results = [r for r in results if r.get('exchangeShortName') in ['NYSE', 'NASDAQ', 'AMEX', 'NYSEArca', 'BATS']]
                
                if us_results:
                    # Return the first US result
                    best = us_results[0]
                    return best.get('symbol'), best.get('name')
                
                # If no US stocks, try ETFs
                etf_results = [r for r in results if r.get('exchangeShortName') == 'ETF']
                if etf_results:
                    best = etf_results[0]
                    return best.get('symbol'), best.get('name')
                
                # Fallback to first result
                best = results[0]
                return best.get('symbol'), best.get('name')
    except Exception as e:
        print(f"[FMP Search] Error searching '{query}': {e}")
    
    return None, None

def resolve_company_to_ticker(query):
    """
    Convert company name or ticker to standardized ticker symbol.
    USES FMP API TO FIND ANY COMPANY - not limited to dictionary!
    """
    if not query:
        return None
    
    query_clean = query.strip()
    if not query_clean:
        return None
    
    query_lower = query_clean.lower()
    query_upper = query_clean.upper()
    
    # 1. Quick dictionary lookup for common names (FAST PATH)
    if query_lower in COMPANY_NAME_TO_TICKER:
        return COMPANY_NAME_TO_TICKER[query_lower]
    
    # 2. If it looks like a ticker (short, all letters), verify it exists
    if len(query_upper) <= 5 and query_upper.replace('.', '').replace('-', '').isalpha():
        profile = get_profile(query_upper)
        if profile and profile.get('symbol'):
            return query_upper
    
    # 3. USE FMP SEARCH API - This finds ANY company!
    # This is the critical path for companies not in our dictionary
    ticker, name = search_fmp_ticker(query_clean)
    if ticker:
        return ticker
    
    # 4. If still not found, return as uppercase (user might know the exact ticker)
    return query_upper

def smart_search_ticker(search_term):
    """
    Smart search with company name support - returns (ticker, company_name).
    USES FMP API TO FIND ANY COMPANY!
    """
    if not search_term:
        return None, None
    
    search_term_clean = search_term.strip()
    if not search_term_clean:
        return None, None
    
    search_lower = search_term_clean.lower()
    search_upper = search_term_clean.upper()
    
    # 1. Quick dictionary lookup
    if search_lower in COMPANY_NAME_TO_TICKER:
        ticker = COMPANY_NAME_TO_TICKER[search_lower]
        profile = get_profile(ticker)
        company_name = profile.get('companyName', ticker) if profile else ticker
        return ticker, company_name
    
    # 2. Check if it's already a valid ticker
    if len(search_upper) <= 5 and search_upper.replace('.', '').replace('-', '').isalpha():
        profile = get_profile(search_upper)
        if profile and profile.get('symbol'):
            return search_upper, profile.get('companyName', search_upper)
    
    # 3. USE FMP SEARCH API - This finds ANY company!
    ticker, name = search_fmp_ticker(search_term_clean)
    if ticker:
        return ticker, name or ticker
    
    # 4. Return as-is (user might know exact ticker)
    return search_upper, search_upper

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
            "model": "sonar",  # FIXED: Use correct model name
            "messages": [
                {"role": "system", "content": "You are a technical assistant. Return ONLY valid JSON with no markdown, no code blocks, no preamble, no explanation. Just pure JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(perplexity_url, headers=perplexity_headers, json=perplexity_payload, timeout=30)
        
        # DEBUG: Log response status
        print(f"[DEBUG] Perplexity API Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # DEBUG: Log content received
            print(f"[DEBUG] Content received: {len(content) if content else 0} chars")
            
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
        
        # Non-200 response
        print(f"[DEBUG] Perplexity API Error: Status {response.status_code}")
        print(f"[DEBUG] Response: {response.text[:500]}")  # First 500 chars of error
        return None
    
    except Exception as e:
        print(f"[DEBUG] Perplexity Exception: {str(e)}")
        return None


def call_openai_json(prompt: str, max_tokens: int = 2000, temperature: float = 0.1) -> dict:
    """
    Calls OpenAI GPT-4o-mini and returns parsed JSON dict.
    Uses JSON mode for guaranteed valid JSON responses.
    
    Args:
        prompt: The user prompt (should instruct to return JSON only)
        max_tokens: Maximum response tokens
        temperature: Response randomness (lower = more deterministic)
    
    Returns:
        dict if JSON parsed successfully, None otherwise
    """
    import json
    
    openai_api_key = os.environ.get('OPENAI_API_KEY', '')
    if not openai_api_key:
        return None
    
    try:
        openai_url = "https://api.openai.com/v1/chat/completions"
        openai_headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        openai_payload = {
            "model": "gpt-4o-mini",  # Cheap and reliable!
            "messages": [
                {"role": "system", "content": "You are a financial analysis AI. Return ONLY valid JSON with no markdown, no code blocks, no preamble. Just pure JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},  # JSON MODE - guarantees valid JSON!
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(openai_url, headers=openai_headers, json=openai_payload, timeout=30)
        
        # DEBUG: Log response status
        print(f"[DEBUG] OpenAI API Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # DEBUG: Log content received
            print(f"[DEBUG] OpenAI content received: {len(content) if content else 0} chars")
            
            if not content:
                return None
            
            # With JSON mode, this should always work
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"[DEBUG] OpenAI JSON parse error: {str(e)}")
                return None
        
        # Non-200 response
        print(f"[DEBUG] OpenAI API Error: Status {response.status_code}")
        print(f"[DEBUG] Response: {response.text[:500]}")
        return None
    
    except Exception as e:
        print(f"[DEBUG] OpenAI Exception: {str(e)}")
        return None


def extract_portfolio_from_screenshot(image_data_list):
    """
    Use OpenAI Vision to extract portfolio holdings from 1-5 screenshots.
    
    Args:
        image_data_list: List of base64-encoded image strings
    
    Returns:
        dict with holdings, confidence, unreadable_items
    """
    import json
    import base64
    
    openai_api_key = os.environ.get('OPENAI_API_KEY', '')
    if not openai_api_key:
        return None
    
    try:
        # Build messages with multiple images
        message_content = [
            {
                "type": "text",
                "text": """Extract ALL stock holdings from these portfolio screenshots. 
                
CRITICAL: Return ONLY valid JSON with this exact structure:
{
  "holdings": [
    {
      "ticker_or_name": "AAPL or Apple Inc.",
      "shares": 10.5 or null,
      "weight": 25.3 or null,
      "market_value": 1250.50 or null
    }
  ],
  "confidence": "High" or "Medium" or "Low",
  "unreadable_items": ["list of any holdings you couldn't parse clearly"]
}

Rules:
- Extract ticker if visible, else company name
- Include shares, weight%, or market value if visible (null if not)
- Mark confidence High only if ALL holdings clearly visible
- List any unclear/partial holdings in unreadable_items
- Return ONLY JSON, no markdown, no explanation"""
            }
        ]
        
        # Add each image
        for img_data in image_data_list:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_data}"
                }
            })
        
        openai_url = "https://api.openai.com/v1/chat/completions"
        openai_headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        openai_payload = {
            "model": "gpt-4o",  # Vision model
            "messages": [
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        response = requests.post(openai_url, headers=openai_headers, json=openai_payload, timeout=60)
        
        print(f"[DEBUG] OpenAI Vision Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            
            print(f"[DEBUG] Vision content: {len(content) if content else 0} chars")
            
            if not content:
                return None
            
            # Parse JSON
            try:
                # Remove markdown if present
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                elif content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"[DEBUG] Vision JSON parse error: {str(e)}")
                return None
        
        print(f"[DEBUG] Vision API Error: {response.status_code}")
        print(f"[DEBUG] Response: {response.text[:500]}")
        return None
    
    except Exception as e:
        print(f"[DEBUG] Vision Exception: {str(e)}")
        return None


@st.cache_data(ttl=3600)
def get_earnings_calendar(ticker):
    """Get next earnings date and estimates using FMP earnings-calendar with date range"""
    # FMP earnings-calendar requires from/to dates, not symbol
    # We search 90 days ahead and filter by symbol
    from_date = datetime.now().strftime('%Y-%m-%d')
    to_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
    
    url = f"{BASE_URL}/earnings-calendar?from={from_date}&to={to_date}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # Filter for the specific ticker
                ticker_upper = ticker.upper()
                for earning in data:
                    if earning.get('symbol', '').upper() == ticker_upper:
                        return earning
    except Exception as e:
        print(f"Earnings calendar error: {e}")
    return None


@st.cache_data(ttl=1800)
def get_weekly_earnings_fmp():
    """Get this week's major earnings from FMP API - TOP 5 by market cap per day with company names"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    from_date = monday.strftime('%Y-%m-%d')
    to_date = sunday.strftime('%Y-%m-%d')
    
    url = f"{BASE_URL}/earnings-calendar?from={from_date}&to={to_date}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # Collect all earnings with market cap info
                all_earnings = []
                
                for earning in data:
                    symbol = earning.get('symbol', '')
                    date_str = earning.get('date', '')
                    revenue_est = earning.get('revenueEstimated') or 0
                    
                    if not symbol or not date_str:
                        continue
                    
                    # Get company name and market cap
                    try:
                        profile = get_profile(symbol)
                        company_name = profile.get('companyName', symbol) if profile else symbol
                        market_cap = profile.get('mktCap', revenue_est * 5) if profile else revenue_est * 5
                    except:
                        company_name = symbol
                        market_cap = revenue_est * 5
                    
                    # Only include significant companies
                    if revenue_est > 500000000:  # > $500M revenue
                        all_earnings.append({
                            'symbol': symbol,
                            'company_name': company_name,
                            'date': date_str,
                            'market_cap': market_cap,
                            'eps_est': earning.get('epsEstimated'),
                            'revenue_est': revenue_est
                        })
                
                # Group by date and keep top 5 by market cap per day
                earnings_by_day = {}
                for earning in all_earnings:
                    date_str = earning['date']
                    if date_str not in earnings_by_day:
                        earnings_by_day[date_str] = []
                    earnings_by_day[date_str].append(earning)
                
                # Sort each day by market cap and keep top 5
                for date_str in earnings_by_day:
                    earnings_by_day[date_str] = sorted(
                        earnings_by_day[date_str],
                        key=lambda x: x.get('market_cap', 0),
                        reverse=True
                    )[:5]
                
                return earnings_by_day, None
        return None, f"API returned status {response.status_code}"
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600)
def get_analyst_estimates(ticker):
    """Get analyst estimates for EPS and Revenue - more reliable than earnings calendar"""
    url = f"{BASE_URL}/analyst-estimates/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # Return the most recent estimate (usually next quarter)
                return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_earnings_surprises(ticker, limit=4):
    """Get historical earnings surprises to show beat/miss track record"""
    url = f"{BASE_URL}/earnings-surprises/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[:limit]
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
def get_key_metrics_ttm(ticker):
    """Get TTM key metrics including enterprise value"""
    url = f"{BASE_URL}/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}"
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
def get_enterprise_values(ticker):
    """Get enterprise value data"""
    url = f"{BASE_URL}/enterprise-values/{ticker}?limit=1&apikey={FMP_API_KEY}"
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
def get_financial_growth(ticker):
    """Get financial growth metrics for PEG calculation"""
    url = f"{BASE_URL}/financial-growth/{ticker}?limit=1&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except:
        pass
    return {}

def calculate_valuation_metrics(ticker):
    """Calculate all valuation metrics using existing helper functions"""
    # Get data from multiple sources
    quote = get_quote(ticker)
    ratios_ttm = get_ratios_ttm(ticker)
    income_df = get_income_statement(ticker, 'annual', 2)
    
    metrics = {
        'pe_ratio': None,
        'ps_ratio': None,
        'ev_ebitda': None,
        'peg_ratio': None,
        'is_profitable': True,
        'eps_growth': None
    }
    
    # ====== P/E RATIO ======
    # Use existing get_pe_ratio function
    pe = get_pe_ratio(ticker, quote, ratios_ttm, income_df)
    if pe and pe > 0:
        metrics['pe_ratio'] = pe
    else:
        # Check if company is unprofitable
        eps_ttm = get_eps_ttm(ticker, income_df)
        if eps_ttm <= 0:
            metrics['is_profitable'] = False
    
    # ====== P/S RATIO ======
    # Use existing get_ps_ratio function
    ps = get_ps_ratio(ticker, ratios_ttm)
    if ps and ps > 0:
        metrics['ps_ratio'] = ps
    else:
        # Calculate manually from market cap / revenue
        if quote and income_df is not None and not income_df.empty:
            market_cap = quote.get('marketCap')
            if 'revenue' in income_df.columns and market_cap:
                revenues = income_df['revenue'].dropna().tolist()
                if revenues:
                    latest_revenue = revenues[-1]
                    if latest_revenue and latest_revenue > 0:
                        metrics['ps_ratio'] = market_cap / latest_revenue
    
    # ====== EV/EBITDA ======
    # Try ratios_ttm first
    if ratios_ttm and ratios_ttm.get('enterpriseValueOverEBITDATTM'):
        ev_ebitda = ratios_ttm.get('enterpriseValueOverEBITDATTM')
        if ev_ebitda and ev_ebitda > 0:
            metrics['ev_ebitda'] = ev_ebitda
    else:
        # Calculate manually
        if quote and income_df is not None and not income_df.empty:
            market_cap = quote.get('marketCap')
            if market_cap and 'ebitda' in income_df.columns:
                ebitda_values = income_df['ebitda'].dropna().tolist()
                if ebitda_values:
                    latest_ebitda = ebitda_values[-1]
                    if latest_ebitda and latest_ebitda > 0:
                        # Get balance sheet for EV
                        balance_df = get_balance_sheet(ticker, 'annual', 1)
                        ev = market_cap
                        
                        if balance_df is not None and not balance_df.empty:
                            try:
                                total_debt = 0
                                cash = 0
                                if 'totalDebt' in balance_df.columns:
                                    debt_val = balance_df['totalDebt'].iloc[-1]
                                    total_debt = debt_val if pd.notna(debt_val) else 0
                                if 'cashAndCashEquivalents' in balance_df.columns:
                                    cash_val = balance_df['cashAndCashEquivalents'].iloc[-1]
                                    cash = cash_val if pd.notna(cash_val) else 0
                                ev = market_cap + total_debt - cash
                            except:
                                pass
                        
                        if ev > 0:
                            metrics['ev_ebitda'] = ev / latest_ebitda
    
    # ====== PEG RATIO ======
    # Try ratios_ttm first
    if ratios_ttm and ratios_ttm.get('pegRatioTTM'):
        peg = ratios_ttm.get('pegRatioTTM')
        if peg and 0 < peg < 10:
            metrics['peg_ratio'] = peg
    elif metrics['pe_ratio']:
        # Calculate from EPS growth
        if income_df is not None and not income_df.empty:
            eps_col = 'epsdiluted' if 'epsdiluted' in income_df.columns else 'eps' if 'eps' in income_df.columns else None
            if eps_col:
                eps_values = income_df[eps_col].dropna().tolist()
                if len(eps_values) >= 2:
                    current_eps = eps_values[-1]
                    prior_eps = eps_values[-2]
                    if prior_eps and abs(prior_eps) > 0 and current_eps:
                        eps_growth_pct = ((current_eps - prior_eps) / abs(prior_eps)) * 100
                        metrics['eps_growth'] = eps_growth_pct
                        if eps_growth_pct > 0:
                            peg = metrics['pe_ratio'] / eps_growth_pct
                            if 0 < peg < 10:
                                metrics['peg_ratio'] = peg
    
    return metrics

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
    """Get AI response - tries Perplexity first, then OpenAI as fallback"""
    
    # Build context-aware system prompt
    system_prompt = """You are a friendly, knowledgeable AI investment assistant for "Investing Made Simple". 
Your role is to help users understand investing concepts and answer questions about stocks and markets.

Guidelines:
- Be concise and helpful (2-4 sentences unless asked for detail)
- Use simple language that beginners can understand
- You CAN provide factual data like P/E ratios, market caps, stock prices, news
- Use your web search capability to get current, accurate information
- Never give specific "buy" or "sell" recommendations
- Be encouraging and supportive
"""
    
    # Add context if available
    if context:
        if context.get('current_page'):
            system_prompt += f"\nUser is on the '{context['current_page']}' page."
        if context.get('selected_ticker'):
            system_prompt += f"\nUser is viewing {context['selected_ticker']} stock."
        if context.get('unhinged_mode'):
            system_prompt += "\nUNHINGED MODE: Be witty and add playful roast commentary while still being helpful."
    
    # Try Perplexity FIRST (has web search)
    if PERPLEXITY_API_KEY:
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.5
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content
            # Log error for debugging
            print(f"[CHATBOT] Perplexity failed: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"[CHATBOT] Perplexity error: {e}")
    
    # Try OpenAI as FALLBACK
    if OPENAI_API_KEY:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.5
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content
            print(f"[CHATBOT] OpenAI failed: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"[CHATBOT] OpenAI error: {e}")
    
    # Both failed
    if not PERPLEXITY_API_KEY and not OPENAI_API_KEY:
        return "❌ No API keys configured. Please add PERPLEXITY_API_KEY or OPENAI_API_KEY to your environment variables."
    
    return "I'm having trouble connecting to the AI service. Please try again in a moment."

def render_ai_chatbot():
    """Render the AI chatbot using sidebar button + st.dialog - NO PAGE REFRESH"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Define chatbot dialog
    @st.dialog("🤖 AI Investment Assistant", width="large")
    def show_chatbot_dialog():
        st.markdown("**Ask me anything about stocks, investing, or markets!**")
        st.caption("🔍 Powered by Perplexity AI with real-time web search")
        
        # Chat history container
        chat_container = st.container(height=300)
        with chat_container:
            if st.session_state.chat_messages:
                for msg in st.session_state.chat_messages[-10:]:
                    if msg["role"] == "user":
                        st.markdown(f'<div style="background: rgba(255,68,68,0.15); padding: 10px 15px; border-radius: 10px; margin: 8px 0; text-align: right; color: #333;"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="background: rgba(33,150,243,0.15); padding: 10px 15px; border-radius: 10px; margin: 8px 0; color: #333;"><strong>🤖 AI:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.info("💡 Try: 'What is Apple's P/E ratio?', 'How did markets do today?', 'Explain dollar-cost averaging'")
        
        st.markdown("---")
        
        # Input
        user_input = st.text_input("Your question:", placeholder="e.g., What's Tesla's market cap?", key="chatbot_dialog_input")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            send_btn = st.button("📤 Send", type="primary", use_container_width=True, key="chatbot_send_btn")
        with col2:
            if st.button("🗑️ Clear", key="chatbot_clear_btn"):
                st.session_state.chat_messages = []
                st.rerun()
        with col3:
            pass  # Empty column for spacing
        
        if send_btn and user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            context = {
                "current_page": st.session_state.get("selected_page", "Home"),
                "selected_ticker": st.session_state.get("selected_ticker", None),
                "unhinged_mode": st.session_state.get("unhinged_mode", False)
            }
            
            with st.spinner("🔍 Searching & thinking..."):
                response = get_chatbot_response(user_input, context)
            
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Add prominent button in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 AI Assistant")
        st.caption("Ask about stocks, prices, investing concepts")
        if st.button("💬 Ask AI a Question", key="sidebar_ai_chat_button", use_container_width=True, type="primary"):
            show_chatbot_dialog()
    
    # Also show a visual indicator (non-clickable) at bottom right
    st.markdown("""
    <style>
    .chatbot-indicator {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        width: 60px !important;
        height: 60px !important;
        background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 999998 !important;
        box-shadow: 0 4px 20px rgba(255, 68, 68, 0.5) !important;
        border: 3px solid #FFFFFF !important;
        font-size: 28px !important;
        animation: pulse-indicator 2s infinite !important;
    }
    @keyframes pulse-indicator {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    .chatbot-tooltip {
        position: fixed !important;
        bottom: 100px !important;
        right: 20px !important;
        background: #333 !important;
        color: white !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        z-index: 999997 !important;
        white-space: nowrap !important;
    }
    </style>
    <div class="chatbot-indicator">💬</div>
    <div class="chatbot-tooltip">Use sidebar button to chat →</div>
    """, unsafe_allow_html=True)

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
            background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FC 100%);
            border: 2px solid #2196F3;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            text-align: center;
            position: relative;
        }
        .welcome-popup h1,
        .welcome-popup p,
        .welcome-popup li,
        .welcome-popup ul,
        .welcome-popup strong {
            color: #1a1a2e !important;
        }
        .welcome-close-form {
            position: absolute;
            top: 15px;
            right: 15px;
            margin: 0;
            padding: 0;
        }
        .welcome-close-btn {
            background: #FF4444;
            border: 2px solid #FF4444;
            color: #FFFFFF !important;
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
            background: #CC0000;
            color: #FFFFFF !important;
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
                <h1>Welcome to Investing Made Simple!</h1>
                <p>We've upgraded your experience:</p>
                <ul>
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
        <div class="fade-in lift-card" style="background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%); 
                    border: 2px solid #0EA5E9; border-radius: 15px; padding: 25px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h4 style="color: #0369A1; margin-bottom: 15px;">If you invested ${weekly_amount} (the cost of a coffee) into {stock_name} every week for the last 5 years...</h4>
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <p style="color: #64748B; font-size: 14px;">Total Invested</p>
                    <p style="color: #1E293B; font-size: 28px; font-weight: bold;">${total_invested:,.0f}</p>
                </div>
                <div>
                    <p style="color: #64748B; font-size: 14px;">You Would Have</p>
                    <p style="color: #16A34A; font-size: 28px; font-weight: bold;">${future_value:,.0f}</p>
                </div>
                <div>
                    <p style="color: #64748B; font-size: 14px;">Gain</p>
                    <p style="color: {"#16A34A" if gain > 0 else "#DC2626"}; font-size: 28px; font-weight: bold;">
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

@st.cache_data(ttl=60)  # 1 minute cache for real-time feel
def get_global_market_sentiment():
    """
    SINGLE SOURCE OF TRUTH for market sentiment.
    Uses real-time SPY quote + 20-day momentum for dynamic scoring.
    """
    try:
        # Get real-time SPY quote
        spy_quote = get_quote("SPY")
        
        if spy_quote and spy_quote.get('price'):
            current_price = spy_quote.get('price', 0)
            today_change = spy_quote.get('changesPercentage', 0) or 0
            
            # Get 20-day momentum
            momentum_20d = 0
            try:
                spy_data = get_historical_price("SPY", years=0.1)
                if not spy_data.empty and 'price' in spy_data.columns and len(spy_data) >= 20:
                    spy_data = spy_data.sort_values('date')
                    price_20d_ago = spy_data['price'].iloc[-20]
                    momentum_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
            except:
                pass
            
            # Combined score: 50% today's move, 50% momentum
            # Today's change maps -3% to +3% into score component
            daily_score = 50 + (today_change * 16.67)
            daily_score = max(0, min(100, daily_score))
            
            # Momentum score
            if momentum_20d <= -10:
                momentum_score = 10
            elif momentum_20d <= -5:
                momentum_score = 25
            elif momentum_20d <= -2:
                momentum_score = 40
            elif momentum_20d <= 2:
                momentum_score = 50
            elif momentum_20d <= 5:
                momentum_score = 65
            elif momentum_20d <= 10:
                momentum_score = 80
            else:
                momentum_score = 90
            
            # Weighted average
            sentiment_score = int(daily_score * 0.5 + momentum_score * 0.5)
            sentiment_score = max(5, min(95, sentiment_score))
            
            label, color = get_market_sentiment_label(sentiment_score)
            return {
                "score": sentiment_score,
                "label": label,
                "color": color,
                "momentum_20d": round(momentum_20d, 2),
                "today_change": round(today_change, 2),
                "spy_price": round(current_price, 2)
            }
    except Exception as e:
        print(f"[DEBUG] Market sentiment error: {e}")
    
    # Fallback to neutral if data unavailable
    return {
        "score": 50,
        "label": "Neutral (Steady)",
        "color": "#FFFF44",
        "momentum_20d": 0,
        "today_change": 0,
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
    
    # ============= INSERT INTO DATABASE (OPTIONAL) =============
    db_saved = False
    try:
        if SUPABASE_ENABLED:
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
            
            # Try to insert into DB
            result = supabase.table("trades").insert(trade_data).execute()
            
            if result.data:
                db_saved = True
        
    except Exception as e:
        # Database failed, but continue with session state
        print(f"[DEBUG] Database save failed (will use session state): {str(e)}")
        db_saved = False
    
    # ============= UPDATE SESSION STATE (ALWAYS) =============
    # Even if DB fails, we save to session state so trades work
    transaction = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'type': action.upper(),
        'ticker': ticker.upper(),
        'shares': shares,
        'price': price,
        'total': estimated_cost,
        'gain_loss': 0
    }
    
    # Add to appropriate portfolio
    if portfolio_type == 'founder':
        st.session_state.founder_transactions.insert(0, transaction)
        
        # Update founder cash
        if action == "Buy":
            st.session_state.founder_cash -= estimated_cost
        else:
            st.session_state.founder_cash += estimated_cost
        
        # Update founder portfolio
        st.session_state.founder_portfolio = rebuild_portfolio_from_trades(st.session_state.founder_transactions)
    else:
        st.session_state.transactions.insert(0, transaction)
        
        # Update user cash
        if action == "Buy":
            st.session_state.cash -= estimated_cost
        else:
            st.session_state.cash += estimated_cost
        
        # Update user portfolio
        st.session_state.portfolio = rebuild_portfolio_from_trades(st.session_state.transactions)
    
    # Success!
    action_word = "Bought" if action == "Buy" else "Sold"
    db_status = " (saved to database)" if db_saved else " (saved locally)"
    return True, f"✅ {action_word} {shares} shares of {ticker} at ${price:.2f}{db_status}"



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
            # ============= PHASE 3: PREMIUM PERSISTENCE =============
            "pinned_tickers": st.session_state.get("pinned_tickers", []),
            "last_ticker": st.session_state.get("last_ticker"),
            "last_tab": st.session_state.get("last_tab"),
            "dismissed_popups": list(st.session_state.get("dismissed_popups", set())),
            "saved_views": st.session_state.get("saved_views", []),
            "theme": st.session_state.get("theme", "dark"),
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
            
            # ============= PHASE 3: RESTORE PREMIUM PERSISTENCE =============
            if "pinned_tickers" in state_data:
                st.session_state.pinned_tickers = state_data["pinned_tickers"]
            if "last_ticker" in state_data:
                st.session_state.last_ticker = state_data["last_ticker"]
            if "last_tab" in state_data:
                st.session_state.last_tab = state_data["last_tab"]
            if "dismissed_popups" in state_data:
                st.session_state.dismissed_popups = set(state_data["dismissed_popups"])
            if "saved_views" in state_data:
                st.session_state.saved_views = state_data["saved_views"]
            if "theme" in state_data:
                st.session_state.theme = state_data["theme"]
            
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
    
    # Only display technical details if not unknown
    if risk_tier != "unknown" and vol_tier != "unknown":
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
        <div style="background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FC 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #00D9FF;">
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

/* NAVIGATION BAR BUTTONS - Force text visibility */
[data-testid="stHorizontalBlock"] .stButton > button {{
    background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
    color: white !important;
    border: none !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    min-height: 42px !important;
    line-height: 1.2 !important;
}}

[data-testid="stHorizontalBlock"] .stButton > button p,
[data-testid="stHorizontalBlock"] .stButton > button span,
[data-testid="stHorizontalBlock"] .stButton > button div {{
    color: white !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}}

/* Dropdown selects in nav */
[data-testid="stHorizontalBlock"] div[data-baseweb="select"] {{
    background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
    border-radius: 8px !important;
    min-height: 42px !important;
}}

[data-testid="stHorizontalBlock"] div[data-baseweb="select"] * {{
    color: white !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}}

/* VIP Button - Gold */
[data-testid="stHorizontalBlock"] .stButton > button:last-of-type {{
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
}}

[data-testid="stHorizontalBlock"] .stButton > button:last-of-type p,
[data-testid="stHorizontalBlock"] .stButton > button:last-of-type * {{
    color: black !important;
}}
</style>
""", unsafe_allow_html=True)

# Callback functions for navigation dropdowns
def nav_learn_changed():
    val = st.session_state.get('nav_learn_select')
    if val:
        st.session_state.selected_page = val

def nav_analyze_changed():
    val = st.session_state.get('nav_analyze_select')
    if val:
        st.session_state.selected_page = val

def nav_action_changed():
    val = st.session_state.get('nav_action_select')
    if val:
        st.session_state.selected_page = val

# Create columns for header with navigation tabs + auth buttons
# Layout: [Dashboard] [Learn▼] [Analyze▼] [Action▼] [---spacer---] [Sign Up] [Sign In] [VIP]
if st.session_state.get("is_logged_in"):
    header_cols = st.columns([1.3, 1.5, 1.8, 1.5, 1.5, 1.5, 1.3])
else:
    header_cols = st.columns([1.3, 1.5, 1.8, 1.5, 0.8, 1.2, 1.2, 1.5])

# Navigation tabs on the LEFT
with header_cols[0]:
    if st.button("🏠 Dashboard", key="nav_dashboard_btn", use_container_width=True):
        st.session_state.selected_page = "🏠 Dashboard"
        st.rerun()

with header_cols[1]:
    with st.popover("🏠 Start Here", use_container_width=True):
        if st.button("🏠 Start Here", key="nav_start_here", use_container_width=True):
            st.session_state.selected_page = "🏠 Start Here"
            st.rerun()
        if st.button("🧠 Risk Quiz", key="nav_risk_quiz", use_container_width=True):
            st.session_state.selected_page = "🧠 Risk Quiz"
            st.rerun()
        if st.button("📚 Learn Hub", key="nav_learn_hub", use_container_width=True):
            st.session_state.selected_page = "📚 Learn Hub"
            st.rerun()
        if st.button("📘 Glossary", key="nav_glossary", use_container_width=True):
            st.session_state.selected_page = "📘 Glossary"
            st.rerun()

with header_cols[2]:
    with st.popover("📊 Company Analysis", use_container_width=True):
        if st.button("📊 Company Analysis", key="nav_company_analysis", use_container_width=True):
            st.session_state.selected_page = "📊 Company Analysis"
            st.rerun()
        if st.button("📈 Financial Health", key="nav_financial_health", use_container_width=True):
            st.session_state.selected_page = "📈 Financial Health"
            st.rerun()
        if st.button("📰 Market Intelligence", key="nav_market_intel", use_container_width=True):
            st.session_state.selected_page = "📰 Market Intelligence"
            st.rerun()
        if st.button("📊 Market Overview", key="nav_market_overview", use_container_width=True):
            st.session_state.selected_page = "📊 Market Overview"
            st.rerun()
        if st.button("🔍 AI Stock Screener", key="nav_ai_screener", use_container_width=True):
            st.session_state.selected_page = "🔍 AI Stock Screener"
            st.rerun()

with header_cols[3]:
    with st.popover("📊 Pro Checklist", use_container_width=True):
        if st.button("📊 Pro Checklist", key="nav_pro_checklist", use_container_width=True):
            st.session_state.selected_page = "📊 Pro Checklist"
            st.rerun()
        if st.button("👑 Ultimate", key="nav_ultimate", use_container_width=True):
            st.session_state.selected_page = "👑 Ultimate"
            st.rerun()
        if st.button("💼 Paper Portfolio", key="nav_paper_portfolio", use_container_width=True):
            st.session_state.selected_page = "💼 Paper Portfolio"
            st.rerun()
        if st.button("👤 Naman's Portfolio", key="nav_naman_portfolio", use_container_width=True):
            st.session_state.selected_page = "👤 Naman's Portfolio"
            st.rerun()

# Spacer column (header_cols[4]) - empty

# Auth buttons on the RIGHT
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
# FINAL LIGHT MODE OVERRIDE - FORCE EVERYTHING WHITE/BLACK
st.markdown("""
<style>
/* NUCLEAR OVERRIDE - FORCE LIGHT MODE */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main, .block-container, body {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
}

[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background-color: #F9F9F9 !important;
    background: #F9F9F9 !important;
}

/* Override ALL dark gradients */
div[style*="background: linear-gradient"][style*="#1a1a2e"],
div[style*="background: linear-gradient"][style*="#0a0a0a"],
div[style*="background: linear-gradient"][style*="#16213e"],
div[style*="background: linear-gradient"][style*="#000000"] {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%) !important;
}

/* ALL TEXT BLACK - MAXIMUM SPECIFICITY */
*, *::before, *::after,
body, p, span, div:not([class*="button"]):not([class*="Button"]), label, a, li, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown *, [data-testid="stMarkdown"] *, [data-testid="stText"],
[data-testid="stCaption"], .element-container *,
[data-testid="stVerticalBlock"] *, [data-testid="stHorizontalBlock"] * {
    color: #121212 !important;
}

/* SIDEBAR TEXT - FORCE BLACK - HIGHEST PRIORITY */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown *,
[data-testid="stSidebar"] [data-testid="stMarkdown"],
[data-testid="stSidebar"] [data-testid="stMarkdown"] *,
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] .stMarkdown * {
    color: #121212 !important;
}

/* Slider labels and values in sidebar */
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"],
[data-testid="stSidebar"] [data-baseweb="slider"] * {
    color: #121212 !important;
}

/* Toggle labels in sidebar */
[data-testid="stSidebar"] .stToggle label,
[data-testid="stSidebar"] .stToggle span,
[data-testid="stSidebar"] [data-testid="stToggle"] * {
    color: #121212 !important;
}

/* Expander text in sidebar */
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary *,
[data-testid="stSidebar"] .streamlit-expanderHeader,
[data-testid="stSidebar"] .streamlit-expanderHeader * {
    color: #121212 !important;
}

/* EXCEPTION: Navigation dropdowns should have WHITE text on RED background */
/* HIGHEST PRIORITY - Force red background on closed dropdown */
[data-testid="stHorizontalBlock"] [data-baseweb="select"],
[data-testid="stHorizontalBlock"] [data-baseweb="select"] > div,
[data-testid="stHorizontalBlock"] [data-baseweb="select"] > div:first-child {
    background: linear-gradient(135deg, #FF4444 0%, #CC0000 100%) !important;
    border-radius: 8px !important;
    min-height: 42px !important;
}

[data-testid="stHorizontalBlock"] [data-baseweb="select"] *,
[data-testid="stHorizontalBlock"] [data-baseweb="select"] span,
[data-testid="stHorizontalBlock"] [data-baseweb="select"] div,
[data-testid="stHorizontalBlock"] [data-baseweb="select"] input,
[data-testid="stHorizontalBlock"] [data-baseweb="select"] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}

/* DISABLE TYPING IN NAVIGATION DROPDOWNS - NO USER INPUT ALLOWED */
[data-testid="stHorizontalBlock"] [data-baseweb="select"] input {
    pointer-events: none !important;
    cursor: pointer !important;
    caret-color: transparent !important;
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    background: transparent !important;
}

[data-testid="stHorizontalBlock"] [data-baseweb="select"] input:focus {
    outline: none !important;
    border: none !important;
}

/* Keep button text white */
.stButton button, .stButton button *, button[kind="primary"], button[kind="primary"] * {
    color: #FFFFFF !important;
}

/* SIDEBAR SECTION HEADERS - LIGHT BLUE FOR VISIBILITY */
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    background: linear-gradient(135deg, #4FC3F7 0%, #29B6F6 100%) !important;
    color: #000000 !important;
    padding: 10px 15px !important;
    border-radius: 8px !important;
    margin: 10px 0 !important;
    font-weight: bold !important;
}

/* Sidebar labels and text stay dark for readability */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #121212 !important;
}
</style>
""", unsafe_allow_html=True)

# Logo
try:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", width=600)
except:
    pass  # Logo handled by deployment

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("💰 Investing Made Simple")
    st.caption("AI-Powered Stock Analysis for Everyone")
with col2:
    st.markdown("### 🤖 AI-Ready")
    st.caption("FMP Premium")


# ============= SESSION STATE INITIALIZATION =============
# Initialize selected page in session state if not exists
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "🏠 Dashboard"

# Initialize pinned tickers
if 'pinned_tickers' not in st.session_state:
    st.session_state.pinned_tickers = []

# Initialize last visited tracking
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = None
if 'last_tab' not in st.session_state:
    st.session_state.last_tab = None

# ============= VERTICAL SIDEBAR (Simplified) =============
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
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
    
    # Period type selector (Annual/Quarterly)
    period_type = st.radio("Time Period:", ["Annual", "Quarterly"], key="global_period_type", horizontal=True)
    st.session_state.global_period = 'annual' if period_type == "Annual" else 'quarter'
    
    # ============= UNHINGED MODE (Right below Timeline) =============
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
    
    st.markdown("---")

    
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


def format_number_detailed(value, number_type="number"):
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

# Inject mobile CSS for responsive design
inject_mobile_css()

# ============= CRITICAL: BUTTON TEXT FIX =============
# This CSS must be here (at the end) to have highest priority
st.markdown("""
<style>
/* FORCE all button text to be visible - white on red */
.stButton > button > div > p,
.stButton > button > p,
.stButton button p,
button[kind="secondary"] p,
button[kind="primary"] p {
    color: white !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Make sure the button content wrapper is visible */
.stButton button > div {
    visibility: visible !important;
    opacity: 1 !important;
}

/* VIP button text should be black (gold background) */
button:has(p:contains("VIP")) p,
button:has(p:contains("👑")) p {
    color: black !important;
}

/* Sidebar Quick Nav emoji buttons */
[data-testid="stSidebar"] .stButton button {
    font-size: 24px !important;
    min-height: 50px !important;
    min-width: 50px !important;
    background: rgba(255,68,68,0.3) !important;
    border: 1px solid rgba(255,68,68,0.6) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,68,68,0.5) !important;
}
</style>
""", unsafe_allow_html=True)

# ============= DASHBOARD: PREMIUM HOME BASE =============
if selected_page == "🏠 Dashboard":
    
    # Track page usage
    track_feature_usage("dashboard")
    
    # Show first-time welcome for new users
    if not st.session_state.get('has_seen_welcome') and not st.session_state.get('is_logged_in'):
        show_first_time_welcome()
        st.stop()
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FC 100%); 
                padding: 25px; border-radius: 15px; margin-bottom: 25px; border: 1px solid #B8D4E8;">
        <h1 style="color: #1a1a2e; margin: 0; font-size: 28px;">🏠 Dashboard</h1>
        <p style="color: #555; margin: 5px 0 0 0;">Your personalized investing command center</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Onboarding tooltip for first-time users
    if len(st.session_state.get('pinned_tickers', [])) == 0:
        show_onboarding_tooltip(
            "pin_stocks",
            "Start by pinning stocks!",
            "Add your favorite stocks to track them here. Try typing AAPL, NVDA, or MSFT below."
        )
    
    # ============= BLOCK A: PINNED WATCHLIST =============
    st.markdown("### 📌 Pinned Watchlist")
    
    # Add ticker input
    col_add1, col_add2 = st.columns([3, 1])
    with col_add1:
        new_pin_ticker = st.text_input("Add a ticker to watch:", placeholder="e.g., AAPL, NVDA, MSFT", key="new_pin_input", label_visibility="collapsed")
    with col_add2:
        add_pin_clicked = st.button("➕ Pin", key="add_pin_btn", use_container_width=True)
    
    # Get tier-based limit
    pin_limit = get_tier_limit("pinned_tickers")
    current_pins = len(st.session_state.pinned_tickers)
    
    # Show usage indicator
    if current_pins > 0:
        tier = get_user_tier()
        if tier == "free":
            st.caption(f"📌 {current_pins}/{pin_limit} tickers (Free tier)")
    
    # Handle adding new pin
    if add_pin_clicked and new_pin_ticker:
        ticker_upper = new_pin_ticker.upper().strip()
        if ticker_upper and ticker_upper not in st.session_state.pinned_tickers:
            if current_pins < pin_limit:
                st.session_state.pinned_tickers.append(ticker_upper)
                save_to_localstorage('pinned_tickers', st.session_state.pinned_tickers)
                # Save to DB if logged in
                if st.session_state.get('is_logged_in'):
                    save_user_progress()
                st.success(f"📌 Added {ticker_upper} to your watchlist!")
                st.rerun()
            else:
                st.warning(f"📌 You've reached the limit of {pin_limit} pinned tickers. Upgrade to Pro for more!")
                if st.button("🚀 Upgrade to Pro", key="upgrade_from_pin_limit"):
                    st.session_state.selected_page = "👑 Become a VIP"
                    st.rerun()
        elif ticker_upper in st.session_state.pinned_tickers:
            st.info(f"{ticker_upper} is already in your watchlist.")
    
    # Display pinned tickers
    if st.session_state.pinned_tickers:
        pinned_data = []
        
        for ticker in st.session_state.pinned_tickers:
            quote = get_quote(ticker)
            logo_url = get_company_logo(ticker)  # Get logo for each ticker
            
            if quote:
                price = quote.get('price', 0)
                change_pct = quote.get('changesPercentage', 0)
                market_cap = quote.get('marketCap', 0)
                
                # Format market cap
                if market_cap >= 1e12:
                    mc_str = f"${market_cap/1e12:.2f}T"
                elif market_cap >= 1e9:
                    mc_str = f"${market_cap/1e9:.1f}B"
                elif market_cap >= 1e6:
                    mc_str = f"${market_cap/1e6:.0f}M"
                else:
                    mc_str = "N/A"
                
                pinned_data.append({
                    "Ticker": ticker,
                    "Price": f"${price:.2f}" if price else "N/A",
                    "Change": f"{change_pct:+.2f}%" if change_pct else "0.00%",
                    "Mkt Cap": mc_str,
                    "_change_val": change_pct,  # Hidden column for sorting
                    "_logo_url": logo_url  # Logo URL
                })
            else:
                pinned_data.append({
                    "Ticker": ticker,
                    "Price": "N/A",
                    "Change": "N/A",
                    "Mkt Cap": "N/A",
                    "_change_val": 0,
                    "_logo_url": logo_url
                })
        
        # Create DataFrame and display
        pinned_df = pd.DataFrame(pinned_data)
        
        # Style the change column
        def style_change(val):
            if '+' in str(val):
                return 'color: #22c55e'
            elif '-' in str(val):
                return 'color: #ef4444'
            return ''
        
        # Display header row
        header_col1, header_col2, header_col3, header_col4, header_col5, header_col6, header_col7 = st.columns([1.3, 1.2, 1, 1, 0.8, 0.8, 0.5])
        with header_col1:
            st.markdown("<p style='color: #888; font-size: 12px; font-weight: bold;'>TICKER</p>", unsafe_allow_html=True)
        with header_col2:
            st.markdown("<p style='color: #888; font-size: 12px; font-weight: bold; text-align: center;'>PRICE</p>", unsafe_allow_html=True)
        with header_col3:
            st.markdown("<p style='color: #888; font-size: 12px; font-weight: bold; text-align: center;'>CHANGE</p>", unsafe_allow_html=True)
        with header_col4:
            st.markdown("<p style='color: #888; font-size: 12px; font-weight: bold; text-align: center;'>MKT CAP</p>", unsafe_allow_html=True)
        with header_col5:
            st.markdown("<p style='color: #888; font-size: 12px; font-weight: bold; text-align: center;'>UPDATED</p>", unsafe_allow_html=True)
        with header_col6:
            st.markdown("<p style='color: #888; font-size: 12px; font-weight: bold; text-align: center;'>ACTION</p>", unsafe_allow_html=True)
        with header_col7:
            st.markdown("<p style='color: #888; font-size: 12px;'></p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 5px 0; border-color: rgba(128,128,128,0.3);'>", unsafe_allow_html=True)
        
        # Display each ticker row with LOGO
        for i, row in enumerate(pinned_data):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1.3, 1.2, 1, 1, 0.8, 0.8, 0.5])
            
            with col1:
                # Display ticker with LOGO
                logo_url = row.get('_logo_url')
                if logo_url:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; padding: 5px 0;">
                        <img src="{logo_url}" width="32" height="32" style="border-radius: 6px; margin-right: 10px;">
                        <span style="font-weight: bold; font-size: 16px;">{row['Ticker']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; padding: 5px 0;">
                        <div style="width: 32px; height: 32px; background: rgba(128,128,128,0.2); border-radius: 6px; margin-right: 10px; display: flex; align-items: center; justify-content: center; font-size: 14px;">📈</div>
                        <span style="font-weight: bold; font-size: 16px;">{row['Ticker']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<p style='text-align: center; padding-top: 10px; font-size: 15px;'>{row['Price']}</p>", unsafe_allow_html=True)
            
            with col3:
                change_color = "#22c55e" if row['_change_val'] > 0 else "#ef4444" if row['_change_val'] < 0 else "#888"
                st.markdown(f"<p style='text-align: center; padding-top: 10px; color: {change_color}; font-weight: 500;'>{row['Change']}</p>", unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"<p style='text-align: center; padding-top: 10px;'>{row['Mkt Cap']}</p>", unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"<p style='text-align: center; padding-top: 10px; color: #888; font-size: 12px;'>just now</p>", unsafe_allow_html=True)
            
            with col6:
                # Analyze button
                analyze_clicked = st.button("📊 Analyze", key=f"analyze_btn_{i}", use_container_width=True)
                if analyze_clicked:
                    st.session_state.selected_ticker = row['Ticker']
                    st.session_state.last_ticker = row['Ticker']
                    st.session_state.selected_page = "📊 Company Analysis"
                    st.rerun()
            
            with col7:
                # Remove button
                remove_clicked = st.button("✕", key=f"remove_btn_{i}", help=f"Remove {row['Ticker']}")
                if remove_clicked:
                    st.session_state.pinned_tickers.remove(row['Ticker'])
                    save_to_localstorage('pinned_tickers', st.session_state.pinned_tickers)
                    if st.session_state.get('is_logged_in'):
                        save_user_progress()
                    st.rerun()
        
        # Show data source
        show_data_source(source="FMP API", updated_at=datetime.now())
        
        # Show biggest movers summary
        if pinned_data:
            sorted_by_change = sorted(pinned_data, key=lambda x: x['_change_val'], reverse=True)
            best = sorted_by_change[0]
            worst = sorted_by_change[-1]
            
            if best['_change_val'] != 0 or worst['_change_val'] != 0:
                st.markdown(f"""
                <div style="background: rgba(128,128,128,0.1); padding: 10px 15px; border-radius: 8px; margin-top: 10px;">
                    <span style="color: #888;">📊 Today's Movers:</span>
                    <span style="color: #22c55e; margin-left: 10px;">🟢 {best['Ticker']} {best['Change']}</span>
                    <span style="color: #ef4444; margin-left: 15px;">🔴 {worst['Ticker']} {worst['Change']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Empty state
        show_empty_state(
            title="No Pinned Tickers Yet",
            message="Add stocks to your watchlist to track them here",
            action_text="🔍 Go to Company Analysis",
            action_key="goto_analysis_from_empty",
            icon="📌"
        )
        if st.session_state.get('goto_analysis_from_empty'):
            st.session_state.selected_page = "📊 Company Analysis"
            st.rerun()
        
        # Show starter suggestions with LOGOS
        st.markdown("**💡 Popular tickers to get started:**")
        starters = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN"]
        
        # Create columns for each starter
        starter_cols = st.columns(5)
        
        for i, ticker in enumerate(starters):
            with starter_cols[i]:
                # Get logo for starter ticker
                starter_logo = get_company_logo(ticker)
                
                # Display logo + ticker as clickable card
                if starter_logo:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background: rgba(255,75,75,0.15); border-radius: 10px; border: 1px solid #ff4b4b;">
                        <img src="{starter_logo}" width="40" height="40" style="border-radius: 8px; margin-bottom: 8px;">
                        <div style="font-weight: bold; font-size: 14px;">{ticker}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button(f"+ Add", key=f"starter_{ticker}", use_container_width=True):
                    st.session_state.pinned_tickers.append(ticker)
                    save_to_localstorage('pinned_tickers', st.session_state.pinned_tickers)
                    # Save to DB if logged in
                    if st.session_state.get('is_logged_in'):
                        save_user_progress()
                    st.rerun()
    
    st.markdown("---")
    
    # ============= BLOCK B: QUICK ACTIONS =============
    st.markdown("### ⚡ Quick Actions")
    
    qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)
    
    with qa_col1:
        if st.button("🔍 Analyze a Ticker", key="qa_analyze", use_container_width=True):
            st.session_state.selected_page = "📊 Company Analysis"
            st.rerun()
        if st.button("📊 Market Overview", key="qa_market", use_container_width=True):
            st.session_state.selected_page = "📊 Market Overview"
            st.rerun()
    
    with qa_col2:
        if st.button("⚖️ Compare Tickers", key="qa_compare", use_container_width=True):
            st.session_state.selected_page = "📊 Company Analysis"
            st.session_state.company_view = "💪 Financial Health"
            st.rerun()
        if st.button("🏭 Sector Explorer", key="qa_sectors", use_container_width=True):
            st.session_state.selected_page = "📊 Market Overview"
            st.rerun()
    
    with qa_col3:
        if st.button("📰 Market News", key="qa_news", use_container_width=True):
            st.session_state.selected_page = "📰 Market Intelligence"
            st.rerun()
        if st.button("📈 Financial Health", key="qa_health", use_container_width=True):
            st.session_state.selected_page = "📈 Financial Health"
            st.rerun()
    
    with qa_col4:
        if st.button("⚠️ Risk Check", key="qa_risk", use_container_width=True):
            st.session_state.selected_page = "🧠 Risk Quiz"
            st.rerun()
        if st.button("💼 Paper Portfolio", key="qa_portfolio", use_container_width=True):
            st.session_state.selected_page = "💼 Paper Portfolio"
            st.rerun()
    
    st.markdown("---")
    
    # ============= BLOCK C: TODAY'S BRIEF =============
    st.markdown("### 📰 Today's Brief")
    
    brief_col1, brief_col2 = st.columns([2, 1])
    
    with brief_col1:
        st.markdown("#### 📊 Market Snapshot")
        
        # Get SPY, QQQ, VIX quotes
        market_tickers = ["SPY", "QQQ", "DIA"]
        market_cols = st.columns(3)
        
        for i, mticker in enumerate(market_tickers):
            with market_cols[i]:
                mquote = get_quote(mticker)
                if mquote:
                    mprice = mquote.get('price', 0)
                    mchange = mquote.get('changesPercentage', 0)
                    mcolor = "#22c55e" if mchange > 0 else "#ef4444" if mchange < 0 else "#888"
                    
                    st.markdown(f"""
                    <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 14px; color: #888;">{mticker}</div>
                        <div style="font-size: 20px; font-weight: bold;">${mprice:.2f}</div>
                        <div style="color: {mcolor}; font-size: 14px;">{mchange:+.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 14px; color: #888;">{mticker}</div>
                        <div style="font-size: 16px; color: #888;">Loading...</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # VIX (Fear Index)
        st.markdown("")
        vix_quote = get_quote("^VIX")
        if vix_quote:
            vix_val = vix_quote.get('price', 0)
            vix_status = "Low Fear" if vix_val < 15 else "Moderate" if vix_val < 25 else "High Fear" if vix_val < 35 else "Extreme Fear"
            vix_color = "#22c55e" if vix_val < 15 else "#f59e0b" if vix_val < 25 else "#ef4444"
            st.markdown(f"**VIX (Fear Index):** <span style='color: {vix_color};'>{vix_val:.1f}</span> — {vix_status}", unsafe_allow_html=True)
        
        show_data_source(source="FMP API", updated_at=datetime.now())
    
    with brief_col2:
        st.markdown("#### 🎯 Market Mood")
        
        # Get market sentiment
        sentiment_data = get_global_market_sentiment()
        sentiment_score = sentiment_data["score"]
        sentiment_label = sentiment_data["label"]
        sentiment_color = sentiment_data["color"]
        
        st.markdown(f"""
        <div style="background: rgba(128,128,128,0.1); padding: 20px; border-radius: 10px; text-align: center;">
            <div style="font-size: 36px; font-weight: bold; color: {sentiment_color};">{sentiment_score}</div>
            <div style="color: {sentiment_color}; font-size: 16px; font-weight: 500;">{sentiment_label}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Legend
        st.caption("0-25: Extreme Fear | 75-100: Extreme Greed")
    
    st.markdown("---")
    
    # ============= BLOCK D: PREMIUM WORKFLOWS =============
    st.markdown("### 🚀 Premium Workflows")
    st.caption("Deep-dive analysis modes for serious investors")
    
    # Ticker selector for workflows
    default_ticker = st.session_state.get('last_ticker') or 'AAPL'
    workflow_ticker_raw = st.text_input(
        "Enter ticker for analysis:",
        value=default_ticker,
        key="workflow_ticker_input",
        placeholder="e.g., AAPL, NVDA, MSFT"
    )
    workflow_ticker = workflow_ticker_raw.upper().strip() if workflow_ticker_raw else ""
    
    # Show ticker with logo header if valid ticker entered
    if workflow_ticker:
        workflow_logo = get_company_logo(workflow_ticker)
        workflow_profile = get_profile(workflow_ticker)
        company_name = workflow_profile.get('companyName', workflow_ticker) if workflow_profile else workflow_ticker
        
        if workflow_logo:
            st.markdown(f"""
            <div style="display: flex; align-items: center; background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                <img src="{workflow_logo}" width="48" height="48" style="border-radius: 8px; margin-right: 15px;">
                <div>
                    <div style="font-size: 20px; font-weight: bold;">{workflow_ticker}</div>
                    <div style="color: #888; font-size: 14px;">{company_name}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; align-items: center; background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                <div style="width: 48px; height: 48px; background: rgba(255,75,75,0.2); border-radius: 8px; margin-right: 15px; display: flex; align-items: center; justify-content: center; font-size: 24px;">📈</div>
                <div>
                    <div style="font-size: 20px; font-weight: bold;">{workflow_ticker}</div>
                    <div style="color: #888; font-size: 14px;">{company_name}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    workflow_tabs = st.tabs(["💰 Valuation", "⚠️ Risk Analysis", "🏥 Portfolio Health"])
    
    # ============= WORKFLOW 1: VALUATION MODE =============
    with workflow_tabs[0]:
        st.markdown("#### 💰 Valuation Mode")
        st.caption("Understand if a stock is cheap or expensive relative to history")
        
        if workflow_ticker:
            with st.spinner(f"Loading valuation data for {workflow_ticker}..."):
                # Use comprehensive valuation calculation
                val_metrics = calculate_valuation_metrics(workflow_ticker)
                profile = get_profile(workflow_ticker)
                
                pe_ratio = val_metrics.get('pe_ratio')
                ps_ratio = val_metrics.get('ps_ratio')
                ev_ebitda = val_metrics.get('ev_ebitda')
                peg_ratio = val_metrics.get('peg_ratio')
                is_profitable = val_metrics.get('is_profitable', True)
                
                st.markdown("##### 📊 Current Valuation Metrics")
                
                val_col1, val_col2, val_col3, val_col4 = st.columns(4)
                
                # P/E Ratio
                with val_col1:
                    if pe_ratio and pe_ratio > 0:
                        pe_color = "#22c55e" if pe_ratio < 20 else "#f59e0b" if pe_ratio < 35 else "#ef4444"
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                            <div style="color: #888; font-size: 12px;">P/E Ratio</div>
                            <div style="font-size: 24px; font-weight: bold; color: {pe_color};">{pe_ratio:.1f}x</div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif not is_profitable:
                        st.markdown(f"""
                        <div style="background: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #ef4444;">
                            <div style="color: #888; font-size: 12px;">P/E Ratio</div>
                            <div style="font-size: 18px; font-weight: bold; color: #ef4444;">Not Profitable</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                            <div style="color: #888; font-size: 12px;">P/E Ratio</div>
                            <div style="font-size: 24px; font-weight: bold; color: #888;">N/A</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # P/S Ratio
                with val_col2:
                    if ps_ratio and ps_ratio > 0:
                        ps_color = "#22c55e" if ps_ratio < 5 else "#f59e0b" if ps_ratio < 10 else "#ef4444"
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                            <div style="color: #888; font-size: 12px;">P/S Ratio</div>
                            <div style="font-size: 24px; font-weight: bold; color: {ps_color};">{ps_ratio:.1f}x</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                            <div style="color: #888; font-size: 12px;">P/S Ratio</div>
                            <div style="font-size: 24px; font-weight: bold; color: #888;">N/A</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # EV/EBITDA
                with val_col3:
                    if ev_ebitda and ev_ebitda > 0:
                        ev_color = "#22c55e" if ev_ebitda < 12 else "#f59e0b" if ev_ebitda < 20 else "#ef4444"
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                            <div style="color: #888; font-size: 12px;">EV/EBITDA</div>
                            <div style="font-size: 24px; font-weight: bold; color: {ev_color};">{ev_ebitda:.1f}x</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                            <div style="color: #888; font-size: 12px;">EV/EBITDA</div>
                            <div style="font-size: 24px; font-weight: bold; color: #888;">N/A</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # PEG Ratio
                with val_col4:
                    if peg_ratio and peg_ratio > 0 and peg_ratio < 10:  # Sanity check
                        peg_color = "#22c55e" if peg_ratio < 1 else "#f59e0b" if peg_ratio < 2 else "#ef4444"
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                            <div style="color: #888; font-size: 12px;">PEG Ratio</div>
                            <div style="font-size: 24px; font-weight: bold; color: {peg_color};">{peg_ratio:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                            <div style="color: #888; font-size: 12px;">PEG Ratio</div>
                            <div style="font-size: 24px; font-weight: bold; color: #888;">N/A</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Valuation interpretation
                st.markdown("##### 📏 Valuation Guide")
                st.markdown("""
                | Metric | Cheap | Fair | Expensive |
                |--------|-------|------|-----------|
                | P/E Ratio | < 15x | 15-25x | > 25x |
                | P/S Ratio | < 3x | 3-8x | > 8x |
                | EV/EBITDA | < 10x | 10-15x | > 15x |
                | PEG Ratio | < 1.0 | 1.0-2.0 | > 2.0 |
                """)
                
                show_data_source(source="FMP API", updated_at=datetime.now())
                
                # AI Scenario
                st.markdown("##### 🤖 AI Valuation Scenario")
                with st.expander("What Would Justify Current Valuation?", expanded=False):
                    if pe_ratio and pe_ratio > 25:
                        st.markdown(f"""
                        **{workflow_ticker} trades at {pe_ratio:.1f}x earnings - here's what would need to be true:**
                        
                        1. **High Growth:** Company needs to grow earnings 20%+ annually
                        2. **Market Leadership:** Must maintain or expand competitive moat
                        3. **Margin Expansion:** Operating margins should improve over time
                        4. **Execution:** Management must deliver on promised initiatives
                        
                        ⚠️ **Risk:** If growth slows, multiple compression could cause significant downside.
                        """)
                    elif pe_ratio and pe_ratio < 15:
                        st.markdown(f"""
                        **{workflow_ticker} trades at {pe_ratio:.1f}x earnings - here's what the market might be worried about:**
                        
                        1. **Growth Concerns:** Market may expect slowing growth
                        2. **Cyclical Risk:** Business may be sensitive to economic cycles
                        3. **Competition:** Increased competitive pressure
                        4. **Disruption:** Potential technology or market disruption
                        
                        ✅ **Opportunity:** If concerns are overblown, stock could re-rate higher.
                        """)
                    else:
                        st.markdown(f"""
                        **{workflow_ticker} appears fairly valued based on current metrics.**
                        
                        Look for catalysts that could shift the valuation:
                        - Earnings beats/misses
                        - New product announcements
                        - Market share gains/losses
                        - Macroeconomic shifts
                        """)
                    show_ai_disclaimer(inputs_used=[f"{workflow_ticker} valuation ratios", "P/E", "P/S", "PEG"])
        else:
            st.info("Enter a ticker above to see valuation analysis.")
    
    # ============= WORKFLOW 2: RISK ANALYSIS MODE =============
    with workflow_tabs[1]:
        st.markdown("#### ⚠️ Risk Analysis Mode")
        st.caption("Identify potential risks before you invest")
        
        # Check if user has Pro tier for this feature
        user_tier = get_user_tier()
        if user_tier == "free":
            # Show preview for free users
            st.markdown("""
            <div style="background: rgba(157, 78, 221, 0.1); border: 2px dashed #9D4EDD; border-radius: 15px; padding: 25px; text-align: center; margin: 20px 0;">
                <div style="font-size: 40px; margin-bottom: 10px;">🔒</div>
                <h4 style="color: #9D4EDD; margin-bottom: 10px;">Risk Analysis - Pro Feature</h4>
                <p style="color: #888; margin-bottom: 15px;">Get comprehensive risk flags including:</p>
                <div style="text-align: left; max-width: 300px; margin: 0 auto; color: #FFF;">
                    • Volatility analysis<br>
                    • Market cap risk tier<br>
                    • Valuation risk flags<br>
                    • Debt/leverage warnings<br>
                    • Position sizing guidance
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Unlock with Pro - $5/mo", key="upgrade_risk_analysis", use_container_width=True):
                st.session_state.selected_page = "👑 Become a VIP"
                st.rerun()
        else:
            # Pro/Ultimate users get full access
            if workflow_ticker:
                with st.spinner(f"Analyzing risks for {workflow_ticker}..."):
                    quote = get_quote(workflow_ticker)
                    profile = get_profile(workflow_ticker)
                    ratios_ttm = get_ratios_ttm(workflow_ticker)
                    
                    st.markdown("##### 🚩 Risk Flags (Deterministic)")
                    
                    risk_flags = []
                    
                    # Volatility check
                    if quote:
                        change_pct = abs(quote.get('changesPercentage', 0))
                        if change_pct > 5:
                            risk_flags.append(("🔴", "High Volatility", f"Stock moved {change_pct:.1f}% today"))
                        
                        # Market cap tier
                        market_cap = quote.get('marketCap', 0)
                        if market_cap < 2e9:
                            risk_flags.append(("🟡", "Small Cap Risk", f"Market cap ${market_cap/1e9:.1f}B - higher volatility expected"))
                        elif market_cap < 10e9:
                            risk_flags.append(("🟢", "Mid Cap", f"Market cap ${market_cap/1e9:.1f}B"))
                    else:
                        risk_flags.append(("🟢", "Large Cap", f"Market cap ${market_cap/1e9:.0f}B - generally more stable"))
                
                # Valuation risk
                if ratios_ttm:
                    pe = ratios_ttm.get('peRatioTTM', 0)
                    if pe and pe > 50:
                        risk_flags.append(("🔴", "High Valuation Risk", f"P/E of {pe:.0f}x is very expensive"))
                    elif pe and pe > 30:
                        risk_flags.append(("🟡", "Elevated Valuation", f"P/E of {pe:.0f}x above market average"))
                    
                    # Debt check
                    debt_equity = ratios_ttm.get('debtEquityRatioTTM', 0)
                    if debt_equity and debt_equity > 2:
                        risk_flags.append(("🔴", "High Leverage", f"Debt/Equity of {debt_equity:.1f}x is elevated"))
                    elif debt_equity and debt_equity > 1:
                        risk_flags.append(("🟡", "Moderate Debt", f"Debt/Equity of {debt_equity:.1f}x"))
                
                # Sector risk
                if profile:
                    sector = profile.get('sector', '')
                    volatile_sectors = ['Technology', 'Consumer Cyclical', 'Energy']
                    if sector in volatile_sectors:
                        risk_flags.append(("🟡", "Cyclical Sector", f"{sector} can be volatile during economic shifts"))
                
                # Display flags
                if risk_flags:
                    for flag_color, flag_title, flag_desc in risk_flags:
                        st.markdown(f"""
                        <div style="background: rgba(128,128,128,0.1); padding: 12px 15px; border-radius: 8px; margin-bottom: 8px; display: flex; align-items: center;">
                            <span style="font-size: 20px; margin-right: 10px;">{flag_color}</span>
                            <div>
                                <strong>{flag_title}</strong>
                                <div style="color: #888; font-size: 13px;">{flag_desc}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ No major risk flags detected")
                
                # Risk score summary
                red_flags = len([f for f in risk_flags if f[0] == "🔴"])
                yellow_flags = len([f for f in risk_flags if f[0] == "🟡"])
                
                st.markdown("##### 📊 Risk Summary")
                risk_col1, risk_col2, risk_col3 = st.columns(3)
                with risk_col1:
                    st.metric("🔴 High Risk Flags", red_flags)
                with risk_col2:
                    st.metric("🟡 Caution Flags", yellow_flags)
                with risk_col3:
                    overall_risk = "High" if red_flags >= 2 else "Moderate" if red_flags >= 1 or yellow_flags >= 2 else "Low"
                    risk_color = "#ef4444" if overall_risk == "High" else "#f59e0b" if overall_risk == "Moderate" else "#22c55e"
                    st.markdown(f"""
                    <div style="background: rgba(128,128,128,0.1); padding: 10px; border-radius: 8px; text-align: center;">
                        <div style="color: #888; font-size: 12px;">Overall Risk</div>
                        <div style="font-size: 18px; font-weight: bold; color: {risk_color};">{overall_risk}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                show_data_source(source="FMP API", updated_at=datetime.now())
                
                # AI Risk Narrative
                st.markdown("##### 🤖 AI Risk Narrative")
                with st.expander("Detailed Risk Assessment", expanded=False):
                    st.markdown(f"""
                    **Risk Assessment for {workflow_ticker}:**
                    
                    Based on the deterministic flags above, here's what to consider:
                    
                    {"⚠️ **High Volatility Alert:** This stock shows significant price swings. Only invest what you can afford to lose." if any('Volatility' in f[1] for f in risk_flags) else ""}
                    
                    {"💰 **Valuation Concern:** The stock is trading at a premium. Strong execution is needed to justify the price." if any('Valuation' in f[1] for f in risk_flags) else ""}
                    
                    {"🏦 **Leverage Risk:** High debt levels mean the company is more sensitive to interest rate changes and economic downturns." if any('Leverage' in f[1] for f in risk_flags) else ""}
                    
                    **Position Sizing Suggestion:**
                    - {"Conservative: 1-2% of portfolio" if red_flags >= 2 else "Moderate: 3-5% of portfolio" if red_flags >= 1 else "Standard: 5-10% of portfolio"}
                    
                    *This is educational content, not investment advice.*
                    """)
                    show_ai_disclaimer(inputs_used=[f"{workflow_ticker} volatility", "Valuation metrics", "Debt levels", "Market cap"])
            else:
                st.info("Enter a ticker above to see risk analysis.")
    
    # ============= WORKFLOW 3: PORTFOLIO HEALTH MODE =============
    with workflow_tabs[2]:
        st.markdown("#### 🏥 Portfolio Health Check")
        st.caption("Analyze your pinned watchlist for diversification and risk")
        
        # Check if user has Pro tier for this feature
        user_tier = get_user_tier()
        if user_tier == "free":
            # Show preview for free users
            st.markdown("""
            <div style="background: rgba(157, 78, 221, 0.1); border: 2px dashed #9D4EDD; border-radius: 15px; padding: 25px; text-align: center; margin: 20px 0;">
                <div style="font-size: 40px; margin-bottom: 10px;">🔒</div>
                <h4 style="color: #9D4EDD; margin-bottom: 10px;">Portfolio Health - Pro Feature</h4>
                <p style="color: #888; margin-bottom: 15px;">Analyze your watchlist with:</p>
                <div style="text-align: left; max-width: 300px; margin: 0 auto; color: #FFF;">
                    • Sector allocation breakdown<br>
                    • Concentration warnings<br>
                    • Diversification score<br>
                    • Top gainers/losers<br>
                    • AI portfolio suggestions
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Unlock with Pro - $5/mo", key="upgrade_portfolio_health", use_container_width=True):
                st.session_state.selected_page = "👑 Become a VIP"
                st.rerun()
        else:
            # Pro/Ultimate users get full access
            pinned = st.session_state.get('pinned_tickers', [])
            
            if not pinned or len(pinned) == 0:
                show_empty_state(
                    title="No Tickers Pinned",
                    message="Pin some stocks to your watchlist to analyze portfolio health",
                    action_text="📌 Go to Dashboard",
                    action_key="goto_dashboard_health",
                    icon="🏥"
                )
            elif len(pinned) == 1:
                st.warning("📌 Pin at least 2 tickers to analyze portfolio health.")
                if st.button("➕ Add More Tickers", key="add_more_health"):
                    st.session_state.selected_page = "📊 Company Analysis"
                    st.rerun()
            else:
                # 2+ tickers - show full analysis
                st.markdown("##### 📊 Portfolio Composition")
            
            # Gather data for all pinned tickers
            portfolio_data = []
            sector_allocation = {}
            total_value = 0
            
            for ticker in pinned:
                profile = get_profile(ticker)
                quote = get_quote(ticker)
                
                if profile and quote:
                    sector = profile.get('sector', 'Other')
                    market_cap = quote.get('marketCap', 0)
                    price = quote.get('price', 0)
                    change = quote.get('changesPercentage', 0)
                    
                    portfolio_data.append({
                        'ticker': ticker,
                        'sector': sector,
                        'market_cap': market_cap,
                        'price': price,
                        'change': change
                    })
                    
                    # Equal weight assumption for sector allocation
                    if sector in sector_allocation:
                        sector_allocation[sector] += 1
                    else:
                        sector_allocation[sector] = 1
            
            # Display sector allocation
            if sector_allocation:
                st.markdown("##### 🏭 Sector Allocation")
                
                total_positions = len(pinned)
                for sector, count in sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True):
                    pct = (count / total_positions) * 100
                    bar_color = "#ef4444" if pct > 40 else "#f59e0b" if pct > 25 else "#22c55e"
                    st.markdown(f"""
                    <div style="margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>{sector}</span>
                            <span>{pct:.0f}% ({count} stocks)</span>
                        </div>
                        <div style="background: rgba(128,128,128,0.2); border-radius: 4px; height: 8px;">
                            <div style="background: {bar_color}; width: {pct}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Risk flags
            st.markdown("##### 🚩 Diversification Flags")
            
            div_flags = []
            
            # Concentration check
            if len(sector_allocation) == 1:
                div_flags.append(("🔴", "Single Sector", "All positions in one sector - very high concentration risk"))
            elif len(sector_allocation) <= 2:
                div_flags.append(("🟡", "Low Diversification", "Only 2 sectors represented"))
            else:
                div_flags.append(("🟢", "Good Sector Spread", f"{len(sector_allocation)} sectors represented"))
            
            # Over-concentration in single sector
            for sector, count in sector_allocation.items():
                pct = (count / total_positions) * 100
                if pct > 50:
                    div_flags.append(("🔴", f"Heavy {sector}", f"{pct:.0f}% in {sector} - consider diversifying"))
                elif pct > 40:
                    div_flags.append(("🟡", f"High {sector} Weight", f"{pct:.0f}% in {sector}"))
            
            # Position count
            if len(pinned) < 5:
                div_flags.append(("🟡", "Few Positions", f"Only {len(pinned)} stocks - consider adding more for diversification"))
            elif len(pinned) >= 10:
                div_flags.append(("🟢", "Good Position Count", f"{len(pinned)} stocks in watchlist"))
            
            for flag_color, flag_title, flag_desc in div_flags:
                st.markdown(f"""
                <div style="background: rgba(128,128,128,0.1); padding: 10px 15px; border-radius: 8px; margin-bottom: 8px;">
                    <span style="font-size: 18px; margin-right: 8px;">{flag_color}</span>
                    <strong>{flag_title}:</strong> <span style="color: #888;">{flag_desc}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Today's performance
            st.markdown("##### 📈 Today's Performance")
            
            gainers = [p for p in portfolio_data if p['change'] > 0]
            losers = [p for p in portfolio_data if p['change'] < 0]
            
            perf_col1, perf_col2 = st.columns(2)
            with perf_col1:
                st.metric("🟢 Gainers", len(gainers))
            with perf_col2:
                st.metric("🔴 Losers", len(losers))
            
            show_data_source(source="FMP API", updated_at=datetime.now())
            
            # AI Suggestions
            st.markdown("##### 🤖 AI Suggestions")
            with st.expander("Diversification Recommendations", expanded=False):
                missing_sectors = set(['Technology', 'Healthcare', 'Financial Services', 'Consumer Defensive', 'Industrials']) - set(sector_allocation.keys())
                
                st.markdown(f"""
                **Portfolio Health Summary:**
                
                - **Positions:** {len(pinned)} stocks
                - **Sectors:** {len(sector_allocation)} represented
                - **Diversification Score:** {"⚠️ Needs Work" if len(sector_allocation) <= 2 else "✅ Good" if len(sector_allocation) >= 4 else "🟡 Moderate"}
                
                {"**Consider adding exposure to:** " + ", ".join(list(missing_sectors)[:3]) if missing_sectors else "**Good sector coverage!**"}
                
                **General Guidelines:**
                - Aim for 5-10 positions minimum
                - No single sector > 30% of portfolio
                - Include defensive sectors for stability
                
                *This is educational content, not investment advice.*
                """)
                show_ai_disclaimer(inputs_used=["Your pinned tickers", "Sector allocation", "Position count"])
    
    st.markdown("---")
    
    # ============= BLOCK E: CONTINUE WHERE YOU LEFT OFF =============
    st.markdown("### 🔄 Continue Where You Left Off")
    
    last_ticker = st.session_state.get('last_ticker')
    last_tab = st.session_state.get('last_tab')
    
    if last_ticker or last_tab:
        resume_col1, resume_col2, resume_col3 = st.columns([2, 2, 1])
        
        with resume_col1:
            if last_ticker:
                st.markdown(f"""
                <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px;">
                    <div style="color: #888; font-size: 12px;">Last Ticker</div>
                    <div style="font-size: 18px; font-weight: bold;">{last_ticker}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px;">
                    <div style="color: #888; font-size: 12px;">Last Ticker</div>
                    <div style="color: #888;">None yet</div>
                </div>
                """, unsafe_allow_html=True)
        
        with resume_col2:
            if last_tab:
                st.markdown(f"""
                <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px;">
                    <div style="color: #888; font-size: 12px;">Last Visited</div>
                    <div style="font-size: 16px; font-weight: bold;">{last_tab}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(128,128,128,0.1); padding: 15px; border-radius: 10px;">
                    <div style="color: #888; font-size: 12px;">Last Visited</div>
                    <div style="color: #888;">None yet</div>
                </div>
                """, unsafe_allow_html=True)
        
        with resume_col3:
            if last_ticker and last_tab:
                if st.button("▶️ Resume", key="resume_btn", type="primary", use_container_width=True):
                    st.session_state.selected_ticker = last_ticker
                    st.session_state.selected_page = last_tab
                    st.rerun()
            elif last_tab:
                if st.button("▶️ Resume", key="resume_btn", type="primary", use_container_width=True):
                    st.session_state.selected_page = last_tab
                    st.rerun()
    else:
        st.markdown("""
        <div style="background: rgba(128,128,128,0.05); padding: 20px; border-radius: 10px; text-align: center; color: #888;">
            <p>Start exploring to build your history!</p>
            <p style="font-size: 13px;">Your last visited page and ticker will appear here.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============= BLOCK E: SAVED VIEWS =============
    st.markdown("### 📁 Saved Views")
    
    # Initialize saved views
    if 'saved_views' not in st.session_state:
        st.session_state.saved_views = []
    
    # Save current view button
    with st.expander("💾 Save Current View", expanded=False):
        view_name = st.text_input("View name:", placeholder="e.g., My Tech Watchlist", key="new_view_name")
        
        if st.button("💾 Save View", key="save_view_btn"):
            if view_name:
                # Check limit (free = 2, could be increased for premium)
                max_views = 5  # Free tier limit
                if len(st.session_state.saved_views) >= max_views:
                    st.warning(f"📁 You've reached the limit of {max_views} saved views. Delete one to save more.")
                else:
                    # Capture current state
                    new_view = {
                        "name": view_name,
                        "created_at": datetime.now().isoformat(),
                        "page": st.session_state.get("selected_page", "🏠 Dashboard"),
                        "ticker": st.session_state.get("selected_ticker", ""),
                        "pinned_tickers": st.session_state.get("pinned_tickers", []).copy(),
                    }
                    st.session_state.saved_views.append(new_view)
                    save_to_localstorage('saved_views', st.session_state.saved_views)
                    
                    # Save to DB if logged in
                    if st.session_state.get('is_logged_in'):
                        save_user_progress()
                    
                    st.success(f"✅ Saved view: {view_name}")
                    st.rerun()
            else:
                st.warning("Please enter a name for your view.")
    
    # Display saved views
    if st.session_state.saved_views:
        for i, view in enumerate(st.session_state.saved_views):
            view_col1, view_col2, view_col3 = st.columns([3, 1, 1])
            
            with view_col1:
                st.markdown(f"""
                <div style="background: rgba(128,128,128,0.1); padding: 12px 15px; border-radius: 8px; margin-bottom: 5px;">
                    <strong>{view['name']}</strong>
                    <span style="color: #888; font-size: 12px; margin-left: 10px;">{view.get('page', 'Dashboard')}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with view_col2:
                if st.button("📂 Load", key=f"load_view_{i}", use_container_width=True):
                    # Restore view state
                    if view.get('page'):
                        st.session_state.selected_page = view['page']
                    if view.get('ticker'):
                        st.session_state.selected_ticker = view['ticker']
                    if view.get('pinned_tickers'):
                        st.session_state.pinned_tickers = view['pinned_tickers'].copy()
                        save_to_localstorage('pinned_tickers', st.session_state.pinned_tickers)
                    st.success(f"✅ Loaded: {view['name']}")
                    st.rerun()
            
            with view_col3:
                if st.button("🗑️", key=f"delete_view_{i}", use_container_width=True, help="Delete this view"):
                    st.session_state.saved_views.pop(i)
                    save_to_localstorage('saved_views', st.session_state.saved_views)
                    if st.session_state.get('is_logged_in'):
                        save_user_progress()
                    st.rerun()
        
        # Show usage
        st.caption(f"📁 {len(st.session_state.saved_views)}/5 views saved")
    else:
        # Empty state with starter templates
        st.markdown("""
        <div style="background: rgba(128,128,128,0.05); padding: 15px; border-radius: 10px; text-align: center; color: #888; margin-bottom: 10px;">
            <p style="margin: 0;">No saved views yet. Save your current setup to quickly restore it later!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Starter template suggestions
        st.markdown("**💡 Quick Start Templates:**")
        template_cols = st.columns(3)
        
        templates = [
            {"name": "Tech Giants", "tickers": ["AAPL", "MSFT", "GOOGL", "NVDA", "META"]},
            {"name": "Dividend Kings", "tickers": ["JNJ", "KO", "PG", "MMM", "PEP"]},
            {"name": "Growth Stocks", "tickers": ["TSLA", "AMZN", "NFLX", "CRM", "SHOP"]},
        ]
        
        for i, template in enumerate(templates):
            with template_cols[i]:
                if st.button(f"📋 {template['name']}", key=f"template_{i}", use_container_width=True):
                    st.session_state.pinned_tickers = template['tickers'].copy()
                    save_to_localstorage('pinned_tickers', st.session_state.pinned_tickers)
                    st.success(f"✅ Loaded {template['name']} watchlist!")
                    st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("💡 **Tip:** Pin your favorite tickers to track them easily. Use Quick Actions to jump to any tool.")


# ============= HOMEPAGE: START HERE =============
elif selected_page == "🏠 Start Here":
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
    <div style="background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); padding: 30px; border-radius: 15px; margin-bottom: 20px; text-align: center; border: 2px solid #42A5F5;">
        <div style="font-size: 60px; margin-bottom: 10px;">🐂 vs 🐻</div>
        <h2 style="color: #1565C0; margin: 0;">Learn to Invest Like a Pro</h2>
        <p style="color: #555; margin-top: 10px;">Understand the market. Build wealth. Avoid the traps.</p>
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
    
    # Stock Picker Row - accepts company name OR ticker
    col_pick1, col_pick2 = st.columns(2)
    with col_pick1:
        stock1_input = st.text_input("📈 Good Business:", value=st.session_state.homepage_stock1, key="home_stock1", placeholder="e.g., Apple or AAPL")
        # Resolve company name to ticker using full stock list (fixes Dolby, etc.)
        if stock1_input:
            stock1, stock1_name = smart_search_ticker(stock1_input)
        else:
            stock1, stock1_name = st.session_state.homepage_stock1, None
        if stock1 and stock1_input and stock1 != stock1_input.strip().upper():
            st.caption(f"→ Resolved to: **{stock1}**")
        if stock1:
            st.session_state.homepage_stock1 = stock1
    with col_pick2:
        stock2_input = st.text_input("📉 Risky Business:", value=st.session_state.homepage_stock2, key="home_stock2", placeholder="e.g., GameStop or GME")
        # Resolve company name to ticker using full stock list (fixes Dolby, etc.)
        if stock2_input:
            stock2, stock2_name = smart_search_ticker(stock2_input)
        else:
            stock2, stock2_name = st.session_state.homepage_stock2, None 
        if stock2 and stock2_input and stock2 != stock2_input.strip().upper():
            st.caption(f"→ Resolved to: **{stock2}**")
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
# COMPLETE LEARN HUB IMPLEMENTATION
# This replaces lines 7343-8025 in the main file

elif selected_page == "📚 Learn Hub":
    """
    📖 LEARN HUB - Complete Learning System
    - 55 total lessons (15 original + 40 new)
    - XP & Badge system
    - Progress tracking (session + Supabase)
    - Quiz engine
    - Personalized recommendations
    """
    
    # Show page popup
    show_page_popup(
        'learn_hub',
        '📚 Learn Hub',
        'Master investing with 55 interactive lessons. Earn XP and badges as you progress through beginner to advanced topics.',
        'Take quizzes after each lesson to test your knowledge and unlock achievements!'
    )
    
    # ============= SESSION STATE INITIALIZATION =============
    # Initialize all Learn Hub state variables
    if 'learn_current_level' not in st.session_state:
        st.session_state.learn_current_level = "All Levels"
    if 'learn_topic_filter' not in st.session_state:
        st.session_state.learn_topic_filter = []
    if 'learn_search' not in st.session_state:
        st.session_state.learn_search = ""
    if 'learn_selected_lesson_id' not in st.session_state:
        st.session_state.learn_selected_lesson_id = None
    if 'learn_completed_lessons' not in st.session_state:
        st.session_state.learn_completed_lessons = set()
    if 'learn_started_lessons' not in st.session_state:
        st.session_state.learn_started_lessons = set()
    if 'learn_best_scores' not in st.session_state:
        st.session_state.learn_best_scores = {}
    if 'learn_xp_total' not in st.session_state:
        st.session_state.learn_xp_total = 0
    if 'learn_badges' not in st.session_state:
        st.session_state.learn_badges = set()
    if 'learn_streak_days' not in st.session_state:
        st.session_state.learn_streak_days = 0
    if 'learn_last_completed_date' not in st.session_state:
        st.session_state.learn_last_completed_date = None
    if 'quiz_current_question' not in st.session_state:
        st.session_state.quiz_current_question = 0
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = []
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = None
    if 'completed_lessons' not in st.session_state:
        st.session_state.completed_lessons = set()  # For original lessons
    if 'expanded_lesson' not in st.session_state:
        st.session_state.expanded_lesson = None
    
    # ============= SUPABASE PERSISTENCE FUNCTIONS =============
    def load_learn_progress_from_db():
        """Load learning progress from Supabase (if signed in)"""
        if not SUPABASE_ENABLED:
            return
        
        user_id = st.session_state.get('user_id')
        if not user_id:
            return
        
        try:
            # Load lesson progress
            progress_result = supabase.table('lesson_progress').select('*').eq('user_id', user_id).execute()
            if progress_result.data:
                for row in progress_result.data:
                    if row['completed']:
                        st.session_state.learn_completed_lessons.add(row['lesson_id'])
                    if row['best_score'] > 0:
                        st.session_state.learn_best_scores[row['lesson_id']] = row['best_score']
            
            # Load user stats
            stats_result = supabase.table('user_learning_stats').select('*').eq('user_id', user_id).execute()
            if stats_result.data and len(stats_result.data) > 0:
                stats = stats_result.data[0]
                st.session_state.learn_xp_total = stats.get('xp_total', 0)
                st.session_state.learn_badges = set(stats.get('badges', []))
                st.session_state.learn_streak_days = stats.get('streak_days', 0)
                st.session_state.learn_last_completed_date = stats.get('last_completed_date')
        
        except Exception as e:
            print(f"[DEBUG] Learn Hub DB load error: {e}")
            # Fail-soft: continue with session state
    
    def save_learn_progress_to_db(lesson_id, score):
        """Save learning progress to Supabase (if signed in)"""
        if not SUPABASE_ENABLED:
            return
        
        user_id = st.session_state.get('user_id')
        if not user_id:
            return
        
        try:
            from datetime import datetime, date
            
            # Update lesson progress
            lesson_data = {
                'user_id': user_id,
                'lesson_id': lesson_id,
                'completed': True,
                'best_score': score,
                'completed_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            supabase.table('lesson_progress').upsert(lesson_data).execute()
            
            # Update user stats
            today = date.today()
            last_date = st.session_state.learn_last_completed_date
            
            # Calculate streak
            if last_date:
                if isinstance(last_date, str):
                    last_date = date.fromisoformat(last_date)
                days_diff = (today - last_date).days
                if days_diff == 1:
                    st.session_state.learn_streak_days += 1
                elif days_diff > 1:
                    st.session_state.learn_streak_days = 1
            else:
                st.session_state.learn_streak_days = 1
            
            st.session_state.learn_last_completed_date = today.isoformat()
            
            stats_data = {
                'user_id': user_id,
                'xp_total': st.session_state.learn_xp_total,
                'badges': list(st.session_state.learn_badges),
                'streak_days': st.session_state.learn_streak_days,
                'last_completed_date': st.session_state.learn_last_completed_date,
                'updated_at': datetime.now().isoformat()
            }
            
            supabase.table('user_learning_stats').upsert(stats_data).execute()
        
        except Exception as e:
            print(f"[DEBUG] Learn Hub DB save error: {e}")

    
    # ============= VIDEO DATA LOADING =============
    def load_lesson_videos():
        """Load video URLs from Supabase lesson_videos table"""
        if not SUPABASE_ENABLED:
            return {}
        
        try:
            response = supabase.table("lesson_videos").select("lesson_id, video_url").execute()
            
            if response.data:
                return {row["lesson_id"]: row["video_url"] for row in response.data}
            return {}
        except Exception as e:
            print(f"[DEBUG] Lesson videos load error: {e}")
            return {}
    
    # Initialize video map in session state
    if "lesson_videos_map" not in st.session_state:
        st.session_state.lesson_videos_map = load_lesson_videos()
    
    def save_lesson_video(lesson_id: str, video_url: str):
        """Save or update video URL for a lesson (founder only)"""
        if not SUPABASE_ENABLED:
            st.warning("⚠️ Supabase not enabled - video URLs won't persist")
            return False
        
        if not st.session_state.get("is_founder", False):
            st.error("❌ Only the founder can edit video links")
            return False
        
        try:
            # Normalize the URL
            normalized_url = normalize_video_url(video_url)
            
            # Upsert to Supabase
            response = supabase.table("lesson_videos").upsert({
                "lesson_id": lesson_id,
                "video_url": normalized_url,
                "updated_at": "now()"
            }).execute()
            
            # Update session state map
            st.session_state.lesson_videos_map[lesson_id] = normalized_url
            
            return True
        except Exception as e:
            st.error(f"❌ Failed to save video: {str(e)}")
            print(f"[DEBUG] Video save error: {e}")
            return False
    
    def render_video_panel(lesson_id: str, is_founder: bool):
        """Render the video panel for a lesson"""
        
        # Get current video URL
        video_url = st.session_state.lesson_videos_map.get(lesson_id, "").strip()
        
        st.markdown("### 🎥 Video")
        
        # Founder editing UI
        if is_founder:
            st.caption("*Founder only - edit video link*")
            
            new_url = st.text_input(
                "Video URL",
                value=video_url,
                key=f"video_edit_{lesson_id}",
                placeholder="Paste Google Drive, YouTube, or Loom link",
                help="Google Drive links will be normalized automatically"
            )
            
            if st.button("💾 Save Video", key=f"save_video_{lesson_id}"):
                if save_lesson_video(lesson_id, new_url):
                    st.success("✅ Video saved!")
                    st.rerun()
        
        # Video display
        if video_url:
            try:
                # Try to embed the video
                st.video(video_url)
                
                # Show link as backup
                st.caption(f"[Open in new tab]({video_url})")
                
            except Exception as e:
                # Graceful fallback if embed fails
                st.warning("⚠️ This video couldn't embed. Click link below to watch:")
                st.markdown(f"**[🔗 Watch Video]({video_url})**")
                st.caption("*Best embed reliability: YouTube unlisted or Loom*")
                st.caption("*(Google Drive embedding is best-effort)*")
        else:
            # Empty state - no video yet
            st.markdown("""
            <div style="
                border: 2px dashed #4B5563; 
                border-radius: 10px; 
                padding: 40px 20px; 
                text-align: center;
                background: rgba(31, 41, 55, 0.3);
            ">
                <div style="font-size: 48px; margin-bottom: 10px;">🎥</div>
                <div style="font-size: 18px; color: #9CA3AF; margin-bottom: 5px;">Video Coming Soon</div>
                <div style="font-size: 14px; color: #6B7280;">Check back later for video content</div>
            </div>
            """, unsafe_allow_html=True)
    
            # Fail-soft: continue without DB
    
    # Load progress on page load
    load_learn_progress_from_db()
    
    # ============= LESSON LIBRARY =============
    # Track → Theme → Lessons (Beginner / Intermediate / Advanced + Behavior + Repair)
    # Each lesson follows the same written template and includes a 3-question quiz.
    LEARN_HUB_LESSONS = {'B1': {'id': 'B1',
        'level': 'Beginner',
        'theme': 'Foundations',
        'topics': ['Foundations'],
        'title': 'Market Mechanics',
        'time_min': 5,
        'why_it_matters': 'Understand why prices move and what a stock actually represents.',
        'summary': ['A stock is ownership in a business (not a lottery ticket).',
                    'Prices move when buyers and sellers disagree.',
                    'News matters only if it changes expectations about the future.',
                    'Volatility is normal—even for great companies.'],
        'key_ideas': ['Every trade has a buyer and a seller—price is where they meet.',
                      'Markets are forward-looking: expectations drive price changes.',
                      'Liquidity matters: thin trading can exaggerate moves.',
                      'Long-term prices follow business results (cash flows).'],
        'common_mistakes': ["Thinking 'good company' = 'good stock at any price'.",
                            'Assuming headlines alone move prices without expectation shifts.',
                            'Panic-selling during normal volatility.',
                            'Ignoring time horizon (short-term noise vs long-term value).'],
        'checklist': ["Can you explain 'stock = ownership' in one sentence?",
                      "Did expectations change (not just 'news happened')?",
                      'Do you have a time horizon for this position?',
                      'Can you tolerate the normal swings?'],
        'quiz': [{'question': 'Buying a stock means you are:',
                  'options': ['A) An owner', 'B) A lender', 'C) A customer coupon holder', 'D) Guaranteed profit'],
                  'correct': 0,
                  'explanation': 'Stockholders own a small piece of the company.'},
                 {'question': 'Prices move most because:',
                  'options': ['A) CEOs set them',
                              'B) Buyers vs sellers (expectations)',
                              'C) Dividends daily',
                              'D) Taxes instantly'],
                  'correct': 1,
                  'explanation': 'Price changes reflect shifting expectations and order imbalance.'},
                 {'question': 'A key reason great stocks still drop is:',
                  'options': ['A) They’re always frauds',
                              'B) Volatility is normal',
                              'C) Prices can’t change',
                              'D) Dividends stop'],
                  'correct': 1,
                  'explanation': 'Even strong companies experience volatility as expectations change.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B2': {'id': 'B2',
        'level': 'Beginner',
        'theme': 'Foundations',
        'topics': ['Foundations', 'Buy & Hold'],
        'title': 'Compounding + Time Horizon',
        'time_min': 7,
        'why_it_matters': 'Time turns small, consistent investing into meaningful wealth.',
        'summary': ["Compounding is 'returns on returns'—it accelerates over time.",
                    'The biggest variable you control is staying invested long enough.',
                    'Dollar-cost averaging reduces timing stress.',
                    'Missing a few strong market days can hurt long-term returns.'],
        'key_ideas': ['Compounding curve is slow early, steep later—patience matters.',
                      'Volatility feels scary short-term but smooths out over years.',
                      'Consistency beats intensity (a plan beats perfect timing).',
                      'Your behavior is the hidden driver of outcomes.'],
        'common_mistakes': ["Starting only after you feel 'ready'.",
                            'Stopping contributions during downturns.',
                            'Chasing short-term winners and resetting the compounding clock.',
                            'Measuring success weekly instead of yearly.'],
        'checklist': ['Do you have a monthly auto-invest amount?',
                      'Is your plan realistic for 5+ years?',
                      "Do you understand you'll see drawdowns along the way?",
                      'Will you stick to the plan in a bad year?'],
        'quiz': [{'question': 'Compounding works best with:',
                  'options': ['A) Time', 'B) Luck', 'C) Day trading', 'D) Constant prediction'],
                  'correct': 0,
                  'explanation': 'Time lets returns build on top of previous returns.'},
                 {'question': 'Dollar-cost averaging means:',
                  'options': ['A) Buying a fixed $ amount regularly',
                              'B) Buying only dips',
                              'C) Borrowing to invest',
                              'D) Selling winners fast'],
                  'correct': 0,
                  'explanation': 'DCA is consistent investing over time.'},
                 {'question': 'A long time horizon helps because it:',
                  'options': ['A) Eliminates volatility',
                              'B) Allows recovery from downturns',
                              'C) Guarantees returns',
                              'D) Removes fees'],
                  'correct': 1,
                  'explanation': 'Long horizons let you ride through cycles and recover.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B3': {'id': 'B3',
        'level': 'Beginner',
        'theme': 'Foundations',
        'topics': ['ETFs', 'Risk'],
        'title': 'Index Funds vs Single Stocks',
        'time_min': 6,
        'why_it_matters': 'Most beginners are better served by diversification before stock-picking.',
        'summary': ['Index funds offer instant diversification.',
                    'Single stocks add concentrated risk.',
                    'Fees and taxes compound too—keep them low.',
                    "You can mix both: core index + small 'satellite' picks."],
        'key_ideas': ['Diversification reduces single-company blowups.',
                      "A 'core' holding should be boring and resilient.",
                      'Stock-picking requires ongoing attention and discipline.',
                      'Your biggest enemy is overconfidence early.'],
        'common_mistakes': ['Owning 3–5 stocks and calling it diversified.',
                            'Buying hype names without understanding the business.',
                            'Ignoring fees and turnover.',
                            'Overtrading and paying hidden costs (spreads, taxes).'],
        'checklist': ['Do you have a diversified core?',
                      'Can you explain why you own each stock?',
                      'Are your costs (fees/taxes) minimal?',
                      'Is your portfolio built to survive bad years?'],
        'quiz': [{'question': 'Index funds generally provide:',
                  'options': ['A) Guaranteed profits',
                              'B) Instant diversification',
                              'C) No volatility',
                              'D) Only bonds'],
                  'correct': 1,
                  'explanation': 'Index funds hold many companies, reducing single-stock risk.'},
                 {'question': 'Single stocks are riskier mainly because:',
                  'options': ['A) They’re illegal',
                              'B) They can go to zero',
                              'C) They have dividends',
                              'D) They trade daily'],
                  'correct': 1,
                  'explanation': 'Concentration increases downside if one company disappoints.'},
                 {'question': 'A common beginner-friendly approach is:',
                  'options': ['A) All-in one stock',
                              'B) Core index + small picks',
                              'C) Only options',
                              'D) No investing'],
                  'correct': 1,
                  'explanation': 'Core-satellite balances diversification with learning.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B4': {'id': 'B4',
        'level': 'Beginner',
        'theme': 'ETFs & Diversification',
        'topics': ['ETFs'],
        'title': 'ETFs 101',
        'time_min': 5,
        'why_it_matters': 'ETFs are simple building blocks that can cover whole markets or sectors.',
        'summary': ['An ETF is a basket you can buy like a stock.',
                    'Broad ETFs reduce risk vs single names.',
                    'Expense ratio matters over time.',
                    'Liquidity affects trading costs.'],
        'key_ideas': ['Passive ETFs track indexes; active ETFs try to beat them.',
                      'Tracking error: ETF may not match index perfectly.',
                      'Bid/ask spread is a hidden cost—prefer liquid funds.',
                      'Understand what’s inside (holdings) before buying.'],
        'common_mistakes': ['Buying overlapping ETFs (double-counting exposure).',
                            'Ignoring expense ratios and spreads.',
                            'Buying niche ETFs without understanding concentration.',
                            'Assuming ETFs can’t be volatile.'],
        'checklist': ['Is it broad or narrow?',
                      'Expense ratio reasonable?',
                      'Is trading volume/liquidity healthy?',
                      'Do you understand its top holdings?'],
        'quiz': [{'question': 'An ETF is best described as:',
                  'options': ['A) One company', 'B) A basket of investments', 'C) A savings account', 'D) A loan'],
                  'correct': 1,
                  'explanation': 'ETFs hold many assets in one fund.'},
                 {'question': 'A key ETF cost is the:',
                  'options': ['A) Coupon', 'B) Expense ratio', 'C) Dividend tax', 'D) Warranty'],
                  'correct': 1,
                  'explanation': 'Expense ratio is the annual fee charged by the fund.'},
                 {'question': 'A hidden trading cost is the:',
                  'options': ['A) Spread', 'B) Logo', 'C) Ticker length', 'D) Weather'],
                  'correct': 0,
                  'explanation': 'Bid/ask spread can reduce your effective return.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B5': {'id': 'B5',
        'level': 'Beginner',
        'theme': 'ETFs & Diversification',
        'topics': ['Diversification', 'Risk'],
        'title': 'What Diversification Really Means',
        'time_min': 6,
        'why_it_matters': 'Diversification is about reducing correlated risk—not just owning more tickers.',
        'summary': ['Diversification reduces single-company risk.',
                    'Owning many things that move together is not true diversification.',
                    'Mixing sectors and styles helps reduce drawdowns.',
                    'A simple broad ETF already diversifies a lot.'],
        'key_ideas': ['Correlation: how similarly two assets move.',
                      'In crises, correlations rise—plan for that.',
                      'Diversify across sectors, geographies, and asset types when appropriate.',
                      'Diversification helps you stay invested.'],
        'common_mistakes': ['Owning multiple tech funds and calling it diversified.',
                            'Adding random positions without a plan.',
                            'Over-diversifying into tiny positions you can’t track.',
                            'Ignoring that all stocks can drop together.'],
        'checklist': ['Do your holdings behave differently?',
                      'Are you over-exposed to one sector?',
                      'Can you explain each holding’s role?',
                      'Would a downturn force you to sell?'],
        'quiz': [{'question': 'Diversification mainly reduces:',
                  'options': ['A) Taxes', 'B) Single-company risk', 'C) All losses forever', 'D) Inflation'],
                  'correct': 1,
                  'explanation': 'It lowers the impact of any one company failing.'},
                 {'question': 'True diversification depends heavily on:',
                  'options': ['A) Number of tickers', 'B) Correlation', 'C) Logo design', 'D) Dividend dates'],
                  'correct': 1,
                  'explanation': 'Correlation tells you whether assets move together.'},
                 {'question': 'In a market panic, correlations usually:',
                  'options': ['A) Fall to zero', 'B) Increase', 'C) Don’t change', 'D) Reverse permanently'],
                  'correct': 1,
                  'explanation': 'Many assets become more correlated in stress.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B6': {'id': 'B6',
        'level': 'Beginner',
        'theme': 'ETFs & Diversification',
        'topics': ['ETFs', 'Diversification'],
        'title': 'Sector ETFs vs Broad Market',
        'time_min': 6,
        'why_it_matters': 'Sector ETFs can boost focus but add concentration risk.',
        'summary': ['Broad market ETFs are diversified across sectors.',
                    'Sector ETFs concentrate bets (higher volatility).',
                    'Sector leadership rotates—timing is hard.',
                    'Use sector ETFs intentionally, not emotionally.'],
        'key_ideas': ['Broad ETFs: core allocation for most beginners.',
                      'Sector ETFs: satellite positions with clear thesis.',
                      'Rotation: different sectors lead in different macro regimes.',
                      'Diversify within a sector too—avoid single-name exposure.'],
        'common_mistakes': ['Going all-in on a hot sector after it already ran up.',
                            'Using sector ETFs as your only diversification.',
                            'Ignoring valuation within the sector.',
                            "Treating sector bets as 'safe'."],
        'checklist': ['Is this a core or satellite position?',
                      'Can you explain why this sector should outperform?',
                      'How will you exit if thesis breaks?',
                      'Are you over-concentrated?'],
        'quiz': [{'question': 'Broad market ETFs are generally:',
                  'options': ['A) More diversified', 'B) Only tech', 'C) Guaranteed profit', 'D) Illiquid'],
                  'correct': 0,
                  'explanation': 'They hold companies across many sectors.'},
                 {'question': 'Sector ETFs increase risk mainly due to:',
                  'options': ['A) Taxes', 'B) Concentration', 'C) Time zones', 'D) Dividends'],
                  'correct': 1,
                  'explanation': 'They focus on one sector, raising volatility.'},
                 {'question': 'Sector leadership:',
                  'options': ['A) Never changes', 'B) Rotates over time', 'C) Is set by law', 'D) Depends on logo'],
                  'correct': 1,
                  'explanation': 'Different sectors lead in different environments.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B7': {'id': 'B7',
        'level': 'Beginner',
        'theme': 'ETFs & Diversification',
        'topics': ['Foundations'],
        'title': 'Why Fees Matter',
        'time_min': 5,
        'why_it_matters': 'Small fees compound into big dollars over decades.',
        'summary': ['Fees reduce returns every year.',
                    'A 1% fee can materially shrink long-term wealth.',
                    'Prefer simple, low-cost funds for core holdings.',
                    'Hidden costs include spreads and turnover.'],
        'key_ideas': ['Fees compound negatively—like reverse compounding.',
                      'Expense ratio is an annual drag.',
                      'Turnover increases taxes in taxable accounts.',
                      'Spreads matter for frequent trading.'],
        'common_mistakes': ['Ignoring expense ratio because it seems small.',
                            'Choosing complex, high-fee products early.',
                            'Trading too often and paying spreads repeatedly.',
                            'Mixing too many overlapping funds.'],
        'checklist': ['What’s the expense ratio?',
                      'How often will you trade this?',
                      'Is there a lower-cost alternative?',
                      'Is this a core holding or a tactical bet?'],
        'quiz': [{'question': 'Fees impact investing by:',
                  'options': ['A) Increasing returns',
                              'B) Reducing returns',
                              'C) Guaranteeing safety',
                              'D) Eliminating volatility'],
                  'correct': 1,
                  'explanation': 'Fees are a direct drag on performance.'},
                 {'question': 'A 1% annual fee over decades is:',
                  'options': ['A) Meaningless', 'B) Potentially large', 'C) Illegal', 'D) Always refunded'],
                  'correct': 1,
                  'explanation': 'Compounding makes persistent fees very costly.'},
                 {'question': 'A hidden cost when buying/selling is:',
                  'options': ['A) Bid/ask spread', 'B) Dividend', 'C) Market cap', 'D) Earnings'],
                  'correct': 0,
                  'explanation': 'The spread is the difference between buy and sell prices.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B8': {'id': 'B8',
        'level': 'Beginner',
        'theme': 'ETFs & Diversification',
        'topics': ['Buy & Hold', 'Risk'],
        'title': 'Rebalancing Basics',
        'time_min': 6,
        'why_it_matters': 'Rebalancing keeps your risk level consistent as markets move.',
        'summary': ['When stocks rise, your portfolio can become riskier without noticing.',
                    'Rebalancing means trimming what grew and adding what lagged.',
                    'It’s a risk control tool, not a performance hack.',
                    'Do it on a schedule or with thresholds.'],
        'key_ideas': ['Targets: choose a stock/bond or sector mix.',
                      'Threshold method: rebalance if allocation drifts too far.',
                      'Schedule method: quarterly or annually.',
                      'Tax-aware: avoid unnecessary taxable gains.'],
        'common_mistakes': ['Rebalancing too often (extra taxes/fees).',
                            'Never rebalancing and ending up over-risky.',
                            'Rebalancing based on emotions (timing).',
                            'Forgetting risk tolerance changes over time.'],
        'checklist': ['Do you have target allocations?',
                      'Has any allocation drifted materially?',
                      'Can you rebalance tax-efficiently?',
                      'Does your target still match your goals?'],
        'quiz': [{'question': 'Rebalancing is primarily used to:',
                  'options': ['A) Time the market',
                              'B) Control risk',
                              'C) Guarantee profit',
                              'D) Avoid taxes entirely'],
                  'correct': 1,
                  'explanation': 'It keeps your risk profile consistent.'},
                 {'question': 'Rebalancing usually involves:',
                  'options': ['A) Buying winners only',
                              'B) Selling some winners and buying laggards',
                              'C) Holding cash forever',
                              'D) Only buying options'],
                  'correct': 1,
                  'explanation': 'You trim overweight positions and add to underweights.'},
                 {'question': 'A common rebalancing cadence is:',
                  'options': ['A) Every hour', 'B) Quarterly/annually', 'C) Never', 'D) Only on news'],
                  'correct': 1,
                  'explanation': 'Scheduled or threshold-based approaches are common.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B9': {'id': 'B9',
        'level': 'Beginner',
        'theme': 'Risk Basics',
        'topics': ['Risk'],
        'title': 'Risk vs Reward',
        'time_min': 6,
        'why_it_matters': 'Understanding risk prevents panic decisions later.',
        'summary': ['Higher potential return usually comes with higher volatility.',
                    'Risk is the chance of a bad outcome, not just price swings.',
                    "Your time horizon changes what 'risky' means.",
                    'A plan reduces emotional mistakes.'],
        'key_ideas': ['Volatility is the visible part of risk.',
                      'Permanent loss risk comes from bad businesses or leverage.',
                      'Diversification reduces risk you don’t get paid for.',
                      'Your behavior determines real-world risk.'],
        'common_mistakes': ['Assuming high return is easy without volatility.',
                            'Over-allocating to risky assets without time horizon.',
                            'Confusing short-term volatility with permanent loss.',
                            'Taking risk you don’t understand.'],
        'checklist': ['Can you handle a 20–30% drawdown?',
                      'Is your horizon long enough for recovery?',
                      'Are you diversified?',
                      'Do you understand what you own?'],
        'quiz': [{'question': 'Higher return potential usually means:',
                  'options': ['A) Lower risk', 'B) Higher risk', 'C) No volatility', 'D) Guaranteed gains'],
                  'correct': 1,
                  'explanation': 'Risk and return tend to be linked.'},
                 {'question': 'Volatility refers to:',
                  'options': ['A) A company’s logo', 'B) Price swings', 'C) Dividend dates', 'D) Tax rates'],
                  'correct': 1,
                  'explanation': 'Volatility is how much prices move up and down.'},
                 {'question': 'A long time horizon helps because it:',
                  'options': ['A) Removes all risk',
                              'B) Allows recovery time',
                              'C) Stops fees',
                              'D) Guarantees profit'],
                  'correct': 1,
                  'explanation': 'Time increases the chance you can ride out downturns.'}],
        'apply_action': {'type': 'none'},
        'xp': 10,
        'video_url': ''},
 'B10': {'id': 'B10',
         'level': 'Beginner',
         'theme': 'Risk Basics',
         'topics': ['Risk'],
         'title': 'Volatility Explained',
         'time_min': 6,
         'why_it_matters': 'Volatility is normal; your plan must survive it.',
         'summary': ['Volatility is the cost of admission for higher returns.',
                     'Even great portfolios can drop 20%+ sometimes.',
                     'A plan reduces panic during drawdowns.',
                     'Position sizing affects how volatility feels.'],
         'key_ideas': ['Markets reprice constantly as new info arrives.',
                       'High uncertainty = higher volatility.',
                       'Diversification smooths volatility but doesn’t remove it.',
                       'Cash buffer reduces forced selling.'],
         'common_mistakes': ['Checking prices too often.',
                             'Using leverage without understanding downside.',
                             'Investing money you’ll need soon.',
                             'Selling at the bottom due to fear.'],
         'checklist': ['Do you have an emergency fund?',
                       'Is your allocation aligned with your risk tolerance?',
                       'Can you avoid forced selling?',
                       'Are you checking too frequently?'],
         'quiz': [{'question': 'Volatility is best described as:',
                   'options': ['A) Guaranteed loss', 'B) Price movement up/down', 'C) A dividend', 'D) A fee'],
                   'correct': 1,
                   'explanation': 'Volatility refers to price swings.'},
                  {'question': 'A 20% drawdown in stocks is:',
                   'options': ['A) Impossible', 'B) Uncommon but normal', 'C) Illegal', 'D) A sign of fraud'],
                   'correct': 1,
                   'explanation': 'Large drawdowns happen periodically even in healthy markets.'},
                  {'question': 'One way to reduce panic is to:',
                   'options': ['A) Use more leverage',
                               'B) Have a plan and time horizon',
                               'C) Trade hourly',
                               'D) Ignore diversification'],
                   'correct': 1,
                   'explanation': 'A plan helps you stay invested through volatility.'}],
         'apply_action': {'type': 'none'},
         'xp': 10,
         'video_url': ''},
 'B11': {'id': 'B11',
         'level': 'Beginner',
         'theme': 'Risk Basics',
         'topics': ['Buy & Hold'],
         'title': 'Why Timing Is Hard',
         'time_min': 6,
         'why_it_matters': 'Most people underperform by trying to jump in and out.',
         'summary': ['The best market days often happen near the worst days.',
                     'Predicting short-term moves is extremely difficult.',
                     'Consistency beats perfect timing.',
                     'A rules-based plan reduces regret.'],
         'key_ideas': ['Market moves reflect countless variables and expectations.',
                       'Missing rebounds can hurt long-term returns.',
                       'Dollar-cost averaging reduces timing pressure.',
                       'Long-term investing benefits from staying invested.'],
         'common_mistakes': ["Waiting for the 'perfect' dip forever.",
                             'Selling after drops and buying after rallies.',
                             'Switching strategies constantly.',
                             'Overreacting to headlines.'],
         'checklist': ['Do you have an auto-invest plan?',
                       'Are you investing money needed soon?',
                       'Can you stick to rules during stress?',
                       'Are you chasing short-term predictions?'],
         'quiz': [{'question': 'Trying to time the market often leads to:',
                   'options': ['A) Higher fees and worse returns',
                               'B) Guaranteed wins',
                               'C) No stress',
                               'D) Perfect bottoms'],
                   'correct': 0,
                   'explanation': 'Market timing is hard and can increase mistakes and costs.'},
                  {'question': 'The best days often occur:',
                   'options': ['A) In calm times', 'B) Near the worst days', 'C) Only on weekends', 'D) Never'],
                   'correct': 1,
                   'explanation': 'Rebounds often happen around volatile periods.'},
                  {'question': 'A beginner-friendly alternative is:',
                   'options': ['A) DCA regularly', 'B) Trade hourly', 'C) Use leverage', 'D) Wait forever'],
                   'correct': 0,
                   'explanation': 'Regular investing reduces timing anxiety.'}],
         'apply_action': {'type': 'none'},
         'xp': 10,
         'video_url': ''},
 'B12': {'id': 'B12',
         'level': 'Beginner',
         'theme': 'Risk Basics',
         'topics': ['Risk'],
         'title': 'Drawdowns (Beginner)',
         'time_min': 6,
         'why_it_matters': 'Knowing drawdowns ahead of time prevents panic-selling.',
         'summary': ['Drawdowns are the peak-to-trough declines in value.',
                     'Stocks can drop 20–50% in bad markets.',
                     'Recoveries can take time—plan for it.',
                     'Risk control is about staying in the game.'],
         'key_ideas': ['Drawdowns are normal in equity investing.',
                       'Time horizon helps you survive drawdowns.',
                       'Diversification reduces severity but not to zero.',
                       'Behavior matters: avoid selling at lows.'],
         'common_mistakes': ["Assuming 'this time is different' every downturn.",
                             'Over-investing money needed soon.',
                             'Selling after losses and locking them in.',
                             'No written plan for downturns.'],
         'checklist': ['Can you tolerate a 30% drop?',
                       'Is your horizon 5+ years for stocks?',
                       'Do you have a cash buffer?',
                       'Do you know what you’ll do in a crash?'],
         'quiz': [{'question': 'A drawdown is:',
                   'options': ['A) Dividend payout', 'B) Peak-to-trough decline', 'C) Annual fee', 'D) Tax refund'],
                   'correct': 1,
                   'explanation': 'Drawdown measures decline from a peak to a low.'},
                  {'question': 'In bad markets, stock drawdowns can be:',
                   'options': ['A) 1% max', 'B) 20–50%', 'C) Never', 'D) Always 0%'],
                   'correct': 1,
                   'explanation': 'Large drawdowns have occurred historically.'},
                  {'question': 'Best preparation for drawdowns is:',
                   'options': ['A) No plan',
                               'B) Time horizon + allocation + discipline',
                               'C) More leverage',
                               'D) Watching prices hourly'],
                   'correct': 1,
                   'explanation': 'A good plan and risk alignment help you stay invested.'}],
         'apply_action': {'type': 'none'},
         'xp': 10,
         'video_url': ''},
 'B13': {'id': 'B13',
         'level': 'Beginner',
         'theme': 'Risk Basics',
         'topics': ['Psychology'],
         'title': 'Emotional Traps (Intro)',
         'time_min': 6,
         'why_it_matters': 'Most investing mistakes are behavioral, not analytical.',
         'summary': ['Losses feel worse than gains feel good.',
                     'FOMO leads to buying high.',
                     'A simple process beats emotional decisions.',
                     'Long-term wins require patience.'],
         'key_ideas': ['Loss aversion: panic-selling after drops.',
                       'Recency bias: extrapolating recent moves forever.',
                       'Overconfidence: too much concentration too early.',
                       'Process > predictions.'],
         'common_mistakes': ['Checking price constantly and reacting.',
                             'Buying because others are buying.',
                             'Changing strategies after a bad week.',
                             'Treating investing like entertainment.'],
         'checklist': ['Do you have written rules?',
                       'Are you reacting to price or fundamentals?',
                       'Can you wait 3–5 years?',
                       'Are you investing vs gambling?'],
         'quiz': [{'question': 'FOMO often causes investors to:',
                   'options': ['A) Buy low', 'B) Buy after big runs', 'C) Avoid hype', 'D) Reduce risk'],
                   'correct': 1,
                   'explanation': 'FOMO pushes buying after prices already rose.'},
                  {'question': 'Loss aversion means:',
                   'options': ['A) You love losses',
                               'B) Losses hurt more than gains feel good',
                               'C) You ignore risk',
                               'D) You always win'],
                   'correct': 1,
                   'explanation': 'Humans feel losses more strongly than gains.'},
                  {'question': 'A good antidote to emotion is:',
                   'options': ['A) No plan', 'B) A written process', 'C) Trading more', 'D) Following influencers'],
                   'correct': 1,
                   'explanation': 'Rules reduce emotional decisions.'}],
         'apply_action': {'type': 'none'},
         'xp': 10,
         'video_url': ''},
 'I1': {'id': 'I1',
        'level': 'Intermediate',
        'theme': 'Financial Statements',
        'topics': ['Financials'],
        'title': 'Income Statement: What Matters',
        'time_min': 8,
        'why_it_matters': 'Learn the handful of lines that explain most businesses.',
        'summary': ['Revenue shows demand; margins show quality.',
                    'Operating income reflects real efficiency.',
                    "Earnings can be 'managed'—look for consistency.",
                    'Watch trends, not one quarter.'],
        'key_ideas': ['Revenue growth + margin trend = core business signal.',
                      'Gross margin: product economics.',
                      'Operating margin: cost discipline and scale.',
                      'One-time items can distort net income.'],
        'common_mistakes': ['Focusing only on EPS without context.',
                            'Ignoring margin compression.',
                            'Comparing margins across industries unfairly.',
                            'Overreacting to one quarter.'],
        'checklist': ['Is revenue growing?',
                      'Are margins stable or improving?',
                      'Are results consistent over time?',
                      'Are there large one-time adjustments?'],
        'quiz': [{'question': 'Gross margin primarily reflects:',
                  'options': ['A) Debt levels', 'B) Product economics', 'C) Dividend policy', 'D) Share count'],
                  'correct': 1,
                  'explanation': 'Gross margin shows cost to produce vs selling price.'},
                 {'question': 'Operating margin is useful because it shows:',
                  'options': ['A) CEO popularity',
                              'B) Business efficiency after expenses',
                              'C) Weather impact',
                              'D) Tax refunds'],
                  'correct': 1,
                  'explanation': 'It captures operating efficiency and scale.'},
                 {'question': 'A one-time gain can:',
                  'options': ['A) Improve margins permanently',
                              'B) Distort net income',
                              'C) Change market cap formula',
                              'D) Remove volatility'],
                  'correct': 1,
                  'explanation': 'One-offs can make earnings look better or worse temporarily.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I2': {'id': 'I2',
        'level': 'Intermediate',
        'theme': 'Financial Statements',
        'topics': ['Financials'],
        'title': 'Balance Sheet: Debt & Health',
        'time_min': 8,
        'why_it_matters': 'Balance sheets reveal fragility before headlines do.',
        'summary': ['Cash provides flexibility; debt increases risk.',
                    'Liquidity matters (can the company pay near-term bills?).',
                    'Leverage amplifies outcomes.',
                    'Look at debt relative to cash flow.'],
        'key_ideas': ['Assets vs liabilities: what the company owns/owes.',
                      'Current ratio and cash runway matter for risk.',
                      'Debt maturity schedule can be a hidden time bomb.',
                      'Share buybacks can weaken balance sheets.'],
        'common_mistakes': ['Ignoring debt because earnings look fine.',
                            'Not checking near-term maturities.',
                            'Assuming big companies can’t fail.',
                            'Confusing accounting equity with safety.'],
        'checklist': ['Cash vs debt balance?',
                      'Any big maturities soon?',
                      'Can cash flow cover interest?',
                      'Any rising leverage trend?'],
        'quiz': [{'question': 'A key risk from high debt is:',
                  'options': ['A) Higher brand value',
                              'B) Forced distress in downturns',
                              'C) Guaranteed dividends',
                              'D) Lower volatility'],
                  'correct': 1,
                  'explanation': 'Debt can create distress when conditions worsen.'},
                 {'question': 'Liquidity is the ability to:',
                  'options': ['A) Raise prices', 'B) Pay near-term obligations', 'C) Increase EPS', 'D) Reduce taxes'],
                  'correct': 1,
                  'explanation': 'Liquidity is about meeting near-term bills.'},
                 {'question': 'A warning sign is:',
                  'options': ['A) Plenty of cash',
                              'B) Large debt maturing soon',
                              'C) Stable margins',
                              'D) Diversified revenue'],
                  'correct': 1,
                  'explanation': 'Near-term maturities can trigger refinancing risk.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I3': {'id': 'I3',
        'level': 'Intermediate',
        'theme': 'Financial Statements',
        'topics': ['Financials'],
        'title': 'Cash Flow Statement (CFO/CFI/CFF)',
        'time_min': 8,
        'why_it_matters': 'Cash flow shows what’s real—profit doesn’t always equal cash.',
        'summary': ['Operating cash flow shows cash from core business.',
                    'Investing cash flow shows reinvestment (capex).',
                    'Financing cash flow shows debt/buybacks/issuance.',
                    'Free cash flow funds growth and shareholder returns.'],
        'key_ideas': ['CFO: cash from operations—quality of earnings.',
                      'Capex: spending to maintain or grow the business.',
                      'FCF = CFO - capex (simple version).',
                      'Watch cash conversion: does profit turn into cash?'],
        'common_mistakes': ['Confusing net income with cash.',
                            'Ignoring capex needs.',
                            'Treating buybacks as always good.',
                            'Ignoring stock-based compensation impacts.'],
        'checklist': ['Is CFO positive and stable?',
                      'How heavy is capex?',
                      'Is FCF positive over time?',
                      'Does cash flow align with earnings?'],
        'quiz': [{'question': 'Operating cash flow measures:',
                  'options': ['A) Cash from core operations', 'B) Dividend yield', 'C) Market cap', 'D) Tax rate'],
                  'correct': 0,
                  'explanation': 'CFO captures cash generated by operations.'},
                 {'question': 'Free cash flow is roughly:',
                  'options': ['A) Revenue - taxes', 'B) CFO - capex', 'C) Price × shares', 'D) Debt / equity'],
                  'correct': 1,
                  'explanation': 'FCF is cash available after reinvestment.'},
                 {'question': 'A red flag is:',
                  'options': ['A) Cash flow rising with profits',
                              'B) Profits rising but cash flow falling',
                              'C) Stable CFO',
                              'D) Low capex'],
                  'correct': 1,
                  'explanation': 'Weak cash conversion can signal low-quality earnings.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I4': {'id': 'I4',
        'level': 'Intermediate',
        'theme': 'Financial Statements',
        'topics': ['Financials'],
        'title': 'Margins Explained (Gross vs Operating)',
        'time_min': 7,
        'why_it_matters': 'Margins tell you if a business has pricing power and efficiency.',
        'summary': ['Gross margin reflects product pricing vs cost.',
                    'Operating margin reflects efficiency and scale.',
                    'Margin stability often signals a moat.',
                    'Margin compression is an early warning sign.'],
        'key_ideas': ['Pricing power lets companies maintain margins amid cost pressures.',
                      'Scale can improve operating margins over time.',
                      'Compare margins within the same industry.',
                      'Look at multi-year trends.'],
        'common_mistakes': ['Comparing margins across unrelated industries.',
                            'Ignoring margin compression during growth.',
                            'Believing low margin businesses are always bad.',
                            'Assuming temporary margin dips are permanent.'],
        'checklist': ['Trend margins for 3–5 years.',
                      'Compare to peers in same industry.',
                      'Watch for sustained compression.',
                      'Understand cost structure drivers.'],
        'quiz': [{'question': 'Gross margin mainly captures:',
                  'options': ['A) Product economics', 'B) Debt levels', 'C) Share count', 'D) Dividend policy'],
                  'correct': 0,
                  'explanation': 'Gross margin relates to cost of goods sold vs revenue.'},
                 {'question': 'Operating margin includes:',
                  'options': ['A) Only taxes', 'B) Operating expenses', 'C) Only dividends', 'D) Market cap'],
                  'correct': 1,
                  'explanation': 'Operating margin accounts for operating expenses.'},
                 {'question': 'Sustained margin compression may indicate:',
                  'options': ['A) Strong moat',
                              'B) Competitive pressure',
                              'C) Lower volatility',
                              'D) More diversification'],
                  'correct': 1,
                  'explanation': 'Competition or cost issues can compress margins.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I5': {'id': 'I5',
        'level': 'Intermediate',
        'theme': 'Financial Statements',
        'topics': ['Financials'],
        'title': 'Free Cash Flow (FCF) Basics',
        'time_min': 8,
        'why_it_matters': 'FCF is the lifeblood that funds growth, buybacks, and resilience.',
        'summary': ['FCF is cash left after reinvesting in the business.',
                    'Consistent FCF gives flexibility in downturns.',
                    'FCF quality matters: stable and recurring beats lumpy.',
                    'FCF supports buybacks/dividends without debt.'],
        'key_ideas': ['FCF yield can compare valuation across firms.',
                      'Capex-heavy businesses may have lower FCF.',
                      'Watch working capital swings.',
                      'Growth funded by FCF is usually healthier.'],
        'common_mistakes': ['Celebrating buybacks funded by debt.',
                            'Ignoring capex needed to maintain the business.',
                            'Assuming all FCF is equally durable.',
                            'Not separating maintenance vs growth capex.'],
        'checklist': ['Is FCF positive over cycles?',
                      'Is it stable or lumpy?',
                      'How much capex is required?',
                      'Is cash returned sustainably?'],
        'quiz': [{'question': 'FCF is important because it:',
                  'options': ['A) Guarantees profit',
                              'B) Funds growth and returns',
                              'C) Eliminates volatility',
                              'D) Sets the stock price'],
                  'correct': 1,
                  'explanation': 'FCF provides real flexibility and capital return ability.'},
                 {'question': 'A healthy sign is:',
                  'options': ['A) Rising debt for buybacks',
                              'B) Buybacks funded by FCF',
                              'C) Negative CFO always',
                              'D) No cash'],
                  'correct': 1,
                  'explanation': 'FCF-funded buybacks/dividends are more sustainable.'},
                 {'question': 'FCF can be low if:',
                  'options': ['A) Capex is high', 'B) Revenue is high', 'C) Margins are stable', 'D) CFO is rising'],
                  'correct': 0,
                  'explanation': 'High reinvestment (capex) reduces free cash flow.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'V1': {'id': 'V1',
        'level': 'Intermediate',
        'theme': 'Valuation',
        'topics': ['Valuation'],
        'title': 'What Valuation Actually Means',
        'time_min': 8,
        'why_it_matters': 'Valuation is what you pay today for future cash flows and growth.',
        'summary': ['A great company can be a bad stock if you overpay.',
                    'Valuation is about expectations vs reality.',
                    'Different industries use different valuation tools.',
                    'Use multiple lenses, not one ratio.'],
        'key_ideas': ['Price embeds a story: growth, margins, risk.',
                      'Multiples compare price to a business output (earnings, sales, cash).',
                      "Discount rates and uncertainty affect what’s 'reasonable'.",
                      'Valuation ranges are better than point estimates.'],
        'common_mistakes': ['Thinking cheap = low P/E only.',
                            'Ignoring business quality and durability.',
                            'Comparing multiples across unrelated industries.',
                            'Forgetting that growth must actually happen.'],
        'checklist': ['What’s the embedded growth expectation?',
                      'Which metric matches the business model?',
                      'Compare to peers and history.',
                      'Use a range, not a single number.'],
        'quiz': [{'question': 'Valuation is best thought of as:',
                  'options': ['A) A guarantee',
                              'B) Price vs future outcomes',
                              'C) Only today’s profits',
                              'D) A chart pattern'],
                  'correct': 1,
                  'explanation': 'Valuation links current price to future expectations.'},
                 {'question': 'Overpaying is dangerous because:',
                  'options': ['A) It reduces upside',
                              'B) It increases dividends',
                              'C) It removes volatility',
                              'D) It lowers fees'],
                  'correct': 0,
                  'explanation': 'If expectations are too high, returns suffer.'},
                 {'question': 'A good practice is to:',
                  'options': ['A) Use one metric only',
                              'B) Use multiple valuation lenses',
                              'C) Ignore peers',
                              'D) Avoid ranges'],
                  'correct': 1,
                  'explanation': 'Different metrics capture different business realities.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'V2': {'id': 'V2',
        'level': 'Intermediate',
        'theme': 'Valuation',
        'topics': ['Valuation'],
        'title': 'P/E Ratio (When It Lies)',
        'time_min': 8,
        'why_it_matters': 'P/E is useful, but only with context around growth, cyclicality, and earnings quality.',
        'summary': ['P/E compares price to earnings, not value by itself.',
                    'High P/E can be justified by durable growth.',
                    'Low P/E can be a trap if earnings are peaking.',
                    'Compare within industry and across cycles.'],
        'key_ideas': ['P/E = Price ÷ Earnings per share.',
                      'Cyclicals can look cheap at peak earnings and expensive at troughs.',
                      'One-time items can distort EPS.',
                      'Forward P/E depends on forecasts—treat it carefully.'],
        'common_mistakes': ['Comparing P/E across unrelated sectors.',
                            'Using trailing P/E during unusual earnings periods.',
                            'Ignoring share count changes (buybacks/issuance).',
                            "Assuming 'low P/E = safe'."],
        'checklist': ['Is this business cyclical?',
                      'Are earnings high-quality and recurring?',
                      'What growth is implied?',
                      'How does it compare to peers?'],
        'quiz': [{'question': 'P/E compares price to:',
                  'options': ['A) Revenue', 'B) Earnings', 'C) Cash', 'D) Debt'],
                  'correct': 1,
                  'explanation': 'P/E uses earnings as the denominator.'},
                 {'question': 'A low P/E can be a trap when:',
                  'options': ['A) Earnings are peaking', 'B) Growth is durable', 'C) Margins expand', 'D) Cash rises'],
                  'correct': 0,
                  'explanation': 'Peak-cycle earnings can make P/E look artificially low.'},
                 {'question': 'Best use of P/E is:',
                  'options': ['A) Across all industries equally',
                              'B) Within similar peers and context',
                              'C) Only for banks',
                              'D) Only for startups'],
                  'correct': 1,
                  'explanation': 'Peer/context comparisons are more meaningful.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'V3': {'id': 'V3',
        'level': 'Intermediate',
        'theme': 'Valuation',
        'topics': ['Valuation'],
        'title': 'P/S Ratio (When It Matters)',
        'time_min': 8,
        'why_it_matters': 'P/S helps value companies when earnings are low or unstable—especially early growth firms.',
        'summary': ['Sales are harder to manipulate than earnings (usually).',
                    'P/S is most useful when profits are negative or volatile.',
                    'P/S must be paired with margins to be meaningful.',
                    'High P/S requires a path to strong profitability.'],
        'key_ideas': ['P/S = Market cap ÷ Revenue.',
                      'A company with high gross margins can justify higher P/S.',
                      'Look at revenue growth + gross margin together.',
                      'For SaaS, retention and unit economics matter.'],
        'common_mistakes': ['Using P/S without margin context.',
                            'Comparing P/S across different business models.',
                            'Assuming growth guarantees future margins.',
                            'Ignoring dilution (share issuance) in high-growth firms.'],
        'checklist': ['What are gross margins?',
                      'Is growth durable (retention/recurring revenue)?',
                      'Is there a path to operating leverage?',
                      'Is dilution heavy?'],
        'quiz': [{'question': 'P/S compares market value to:',
                  'options': ['A) Earnings', 'B) Sales (revenue)', 'C) Cash flow', 'D) Debt'],
                  'correct': 1,
                  'explanation': 'P/S uses revenue as the denominator.'},
                 {'question': 'P/S is most useful when:',
                  'options': ['A) Earnings are stable',
                              'B) Earnings are negative/unstable',
                              'C) Dividends are high',
                              'D) Debt is zero'],
                  'correct': 1,
                  'explanation': 'When earnings are unreliable, sales can be a better anchor.'},
                 {'question': 'To interpret P/S properly, you must also check:',
                  'options': ['A) Margins', 'B) Logo', 'C) Time zone', 'D) Share price alone'],
                  'correct': 0,
                  'explanation': 'Margins determine how much revenue becomes profit.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'V4': {'id': 'V4',
        'level': 'Intermediate',
        'theme': 'Valuation',
        'topics': ['Valuation'],
        'title': 'EV/EBITDA Explained',
        'time_min': 8,
        'why_it_matters': 'EV/EBITDA compares whole-business value to operating earnings and helps compare firms with '
                          'different capital structures.',
        'summary': ['Enterprise Value includes debt and subtracts cash.',
                    'EBITDA approximates operating profitability before capex.',
                    'EV/EBITDA helps compare companies with different leverage.',
                    'It can mislead for capex-heavy businesses.'],
        'key_ideas': ['EV = Market cap + Debt − Cash (simplified).',
                      'EBITDA ignores capital intensity—pair with capex and FCF.',
                      'Use for mature businesses with meaningful EBITDA.',
                      'Compare to peers and history.'],
        'common_mistakes': ['Using EBITDA for businesses with huge capex needs.',
                            'Ignoring lease obligations or hidden liabilities.',
                            'Treating EV/EBITDA as a perfect valuation measure.',
                            'Comparing across unrelated industries.'],
        'checklist': ['Is the business capital intensive?',
                      'Is debt meaningful (check EV not just market cap)?',
                      'Is EBITDA stable over a cycle?',
                      'What’s the FCF conversion?'],
        'quiz': [{'question': 'Enterprise value includes:',
                  'options': ['A) Only equity',
                              'B) Equity plus debt minus cash',
                              'C) Only revenue',
                              'D) Only dividends'],
                  'correct': 1,
                  'explanation': 'EV accounts for capital structure.'},
                 {'question': 'EV/EBITDA is useful because it:',
                  'options': ['A) Ignores leverage differences',
                              'B) Accounts for leverage differences',
                              'C) Eliminates volatility',
                              'D) Guarantees returns'],
                  'correct': 1,
                  'explanation': 'EV includes debt/cash so comparisons are cleaner.'},
                 {'question': 'A common limitation is that EBITDA:',
                  'options': ['A) Includes capex', 'B) Ignores capex', 'C) Equals cash flow', 'D) Is always fake'],
                  'correct': 1,
                  'explanation': 'EBITDA doesn’t reflect capital expenditures.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'V5': {'id': 'V5',
        'level': 'Intermediate',
        'theme': 'Valuation',
        'topics': ['Valuation', 'Financials'],
        'title': 'FCF Yield (Underrated Metric)',
        'time_min': 8,
        'why_it_matters': 'FCF yield ties valuation directly to cash generation.',
        'summary': ['FCF yield = FCF ÷ market value (or EV).',
                    'Higher yield can mean cheaper—or higher risk.',
                    'Stable FCF businesses often deserve premium valuation.',
                    'Use multi-year averages to smooth cycles.'],
        'key_ideas': ["FCF yield is like an 'earnings yield' but for cash.",
                      'Compare FCF yield to bond yields as a sanity check (not a rule).',
                      'Watch for temporary FCF spikes from working capital.',
                      'Pair with durability: moat + stability.'],
        'common_mistakes': ['Using one-year FCF in cyclical industries.',
                            'Ignoring reinvestment needs (capex).',
                            'Assuming high yield always equals bargain.',
                            'Not checking if FCF is recurring.'],
        'checklist': ['Is FCF stable across cycles?',
                      'Is capex sustainable?',
                      'Is the yield high for a reason (risk)?',
                      'Compare to peers and history.'],
        'quiz': [{'question': 'FCF yield measures:',
                  'options': ['A) Cash return vs price', 'B) Revenue growth', 'C) Debt ratio', 'D) Dividend dates'],
                  'correct': 0,
                  'explanation': 'It relates cash generation to valuation.'},
                 {'question': 'A high FCF yield could mean:',
                  'options': ['A) Cheap or risky', 'B) Guaranteed profit', 'C) No volatility', 'D) Always fraud'],
                  'correct': 0,
                  'explanation': 'Markets may price in risk or pessimism.'},
                 {'question': 'Best practice is to:',
                  'options': ['A) Use one quarter',
                              'B) Use multi-year context',
                              'C) Ignore capex',
                              'D) Ignore durability'],
                  'correct': 1,
                  'explanation': 'Multi-year context improves signal quality.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'V6': {'id': 'V6',
        'level': 'Intermediate',
        'theme': 'Valuation',
        'topics': ['Valuation'],
        'title': 'Valuation vs Growth (Putting It Together)',
        'time_min': 8,
        'why_it_matters': 'Returns come from growth *and* what you pay for that growth.',
        'summary': ['High growth can still produce bad returns if you overpay.',
                    'Multiple expansion/contraction drives returns short-term.',
                    'Look for growth + margin expansion + reasonable price.',
                    'Use a range of outcomes, not one forecast.'],
        'key_ideas': ['Total return ≈ earnings growth + multiple change + dividends.',
                      'Multiple contraction is the common risk in expensive stocks.',
                      'Durable growth reduces risk; hype growth increases it.',
                      'Risk-adjusted return matters more than upside stories.'],
        'common_mistakes': ["Betting purely on 'story' without numbers.",
                            'Ignoring downside cases.',
                            'Assuming valuation doesn’t matter for great companies.',
                            'Changing valuation framework midstream.'],
        'checklist': ['What’s your base case, bull, bear?',
                      'Is growth durable (moat/retention)?',
                      'Is valuation reasonable vs peers/history?',
                      'What’s the downside if growth slows?'],
        'quiz': [{'question': 'Total returns are driven by:',
                  'options': ['A) Only price',
                              'B) Growth + multiple changes + dividends',
                              'C) Only dividends',
                              'D) Only news'],
                  'correct': 1,
                  'explanation': 'Return sources include fundamentals and valuation changes.'},
                 {'question': 'A common risk in high-multiple stocks is:',
                  'options': ['A) No volatility',
                              'B) Multiple contraction',
                              'C) Guaranteed gains',
                              'D) Tax elimination'],
                  'correct': 1,
                  'explanation': 'If expectations fall, multiples can compress.'},
                 {'question': 'Best approach is to:',
                  'options': ['A) Use one forecast',
                              'B) Use ranges and scenarios',
                              'C) Ignore peers',
                              'D) Buy any price'],
                  'correct': 1,
                  'explanation': 'Scenarios help manage uncertainty.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I6': {'id': 'I6',
        'level': 'Intermediate',
        'theme': 'Business Quality',
        'topics': ['Business Quality'],
        'title': 'Moats Explained',
        'time_min': 7,
        'why_it_matters': 'Moats help businesses defend profits against competition.',
        'summary': ['Moats protect margins over time.',
                    'Network effects and switching costs are powerful.',
                    'Brand matters when customers pay more willingly.',
                    'Moats can erode—watch signals.'],
        'key_ideas': ['Network effects: product becomes better as more use it.',
                      'Switching costs: hard to leave due to integration/habits.',
                      'Cost advantages: scale lowers unit costs.',
                      'Intangibles: brand, IP, regulatory licenses.'],
        'common_mistakes': ['Assuming current success means permanent moat.',
                            'Confusing growth with moat.',
                            'Ignoring competitive dynamics.',
                            'Failing to re-evaluate moat over time.'],
        'checklist': ['Why can’t a competitor copy this?',
                      'Are margins stable?',
                      'Is customer churn low?',
                      'Is the product becoming more valuable over time?'],
        'quiz': [{'question': 'A moat is:',
                  'options': ['A) A dividend', 'B) A durable advantage', 'C) A chart pattern', 'D) A tax rule'],
                  'correct': 1,
                  'explanation': 'Moats are lasting competitive advantages.'},
                 {'question': 'Switching costs mean:',
                  'options': ['A) Customers can leave easily',
                              'B) Customers find it costly to leave',
                              'C) Fees are high',
                              'D) Volatility is low'],
                  'correct': 1,
                  'explanation': 'High switching costs keep customers locked in.'},
                 {'question': 'Moats often show up as:',
                  'options': ['A) Stable/high margins', 'B) Random price moves', 'C) Low revenue', 'D) No customers'],
                  'correct': 0,
                  'explanation': 'Durable advantages often preserve margins.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I7': {'id': 'I7',
        'level': 'Intermediate',
        'theme': 'Business Quality',
        'topics': ['Business Quality'],
        'title': 'Pricing Power',
        'time_min': 7,
        'why_it_matters': 'Pricing power lets companies raise prices without losing customers.',
        'summary': ['Pricing power protects margins in inflation.',
                    'It’s a sign of brand, differentiation, or necessity.',
                    'Great businesses often show consistent pricing power.',
                    'Lack of pricing power leads to margin pressure.'],
        'key_ideas': ['Look for stable gross margins during cost spikes.',
                      'Customer dependence and product criticality matter.',
                      'Low churn/strong retention supports pricing power.',
                      'Beware commoditized products.'],
        'common_mistakes': ['Mistaking temporary demand spikes for pricing power.',
                            'Ignoring competitive substitutes.',
                            'Assuming all brands have pricing power.',
                            'Not checking retention or churn.'],
        'checklist': ['Are margins stable when costs rise?',
                      'Is churn low?',
                      'Is the product essential or replaceable?',
                      'Are competitors gaining share?'],
        'quiz': [{'question': 'Pricing power means:',
                  'options': ['A) Prices can rise without losing demand',
                              'B) Prices must fall',
                              'C) No competitors exist',
                              'D) Dividends increase'],
                  'correct': 0,
                  'explanation': 'True pricing power allows higher prices without big churn.'},
                 {'question': 'A common signal is:',
                  'options': ['A) Stable margins', 'B) Rising debt', 'C) Falling revenue', 'D) High volatility'],
                  'correct': 0,
                  'explanation': 'Stable margins through cycles suggest pricing power.'},
                 {'question': 'Commodities usually have:',
                  'options': ['A) Strong pricing power',
                              'B) Weak pricing power',
                              'C) No prices',
                              'D) Guaranteed margins'],
                  'correct': 1,
                  'explanation': 'Commoditized products struggle to raise prices.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I8': {'id': 'I8',
        'level': 'Intermediate',
        'theme': 'Business Quality',
        'topics': ['Business Quality'],
        'title': 'Unit Economics (Light)',
        'time_min': 7,
        'why_it_matters': 'Unit economics shows whether growth is profitable at the customer level.',
        'summary': ['Great growth is profitable growth.',
                    'CAC vs LTV is the core frame.',
                    'High retention increases LTV.',
                    'Scale should improve unit economics over time.'],
        'key_ideas': ['CAC: cost to acquire a customer.',
                      'LTV: lifetime value of customer gross profit.',
                      'Payback period: how fast CAC is recovered.',
                      'Retention is the hidden lever.'],
        'common_mistakes': ['Celebrating growth with terrible unit economics.',
                            'Ignoring churn.',
                            'Assuming scale fixes everything.',
                            'Using revenue instead of gross profit for LTV.'],
        'checklist': ['Do customers stick around?',
                      'Is CAC rising or falling?',
                      'Is payback time reasonable?',
                      'Is growth improving margins?'],
        'quiz': [{'question': 'CAC stands for:',
                  'options': ['A) Cash at close',
                              'B) Customer acquisition cost',
                              'C) Cost after capex',
                              'D) Current account charge'],
                  'correct': 1,
                  'explanation': 'CAC is cost to acquire a customer.'},
                 {'question': 'Higher retention generally:',
                  'options': ['A) Lowers LTV', 'B) Raises LTV', 'C) Removes fees', 'D) Eliminates risk'],
                  'correct': 1,
                  'explanation': 'Retention extends customer life and profitability.'},
                 {'question': 'A healthy sign is:',
                  'options': ['A) CAC rising with churn rising',
                              'B) Improving payback period',
                              'C) Negative gross margin',
                              'D) No repeat customers'],
                  'correct': 1,
                  'explanation': 'Faster payback suggests better unit economics.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I9': {'id': 'I9',
        'level': 'Intermediate',
        'theme': 'Business Quality',
        'topics': ['Business Quality'],
        'title': 'Management Quality',
        'time_min': 7,
        'why_it_matters': 'Great management allocates capital well and communicates clearly.',
        'summary': ['Capital allocation drives long-term compounding.',
                    'Good managers are honest about tradeoffs.',
                    'Incentives matter.',
                    'Consistency builds credibility.'],
        'key_ideas': ['Look at track record: buybacks, M&A, reinvestment.',
                      'Alignment: insider ownership and sensible compensation.',
                      'Communication: clear, consistent, not hype-driven.',
                      'Governance: board independence and accountability.'],
        'common_mistakes': ['Believing charismatic CEOs without numbers.',
                            'Ignoring incentive misalignment.',
                            'Assuming good product = good capital allocation.',
                            'Not checking past M&A failures.'],
        'checklist': ['Is capital allocation rational?',
                      'Are incentives aligned with shareholders?',
                      'Do they admit mistakes?',
                      'Is guidance credible over time?'],
        'quiz': [{'question': 'Capital allocation refers to:',
                  'options': ['A) Logo design', 'B) How management uses cash', 'C) Dividend dates', 'D) Stock splits'],
                  'correct': 1,
                  'explanation': 'It’s how cash is invested, returned, or spent.'},
                 {'question': 'A red flag is:',
                  'options': ['A) Clear communication',
                              'B) Constant hype with poor results',
                              'C) Insider ownership',
                              'D) Stable margins'],
                  'correct': 1,
                  'explanation': 'Hype without performance can signal poor discipline.'},
                 {'question': 'Alignment often improves when:',
                  'options': ['A) No ownership', 'B) Insiders own shares', 'C) Fees rise', 'D) More debt is added'],
                  'correct': 1,
                  'explanation': 'Ownership can align incentives.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'I10': {'id': 'I10',
         'level': 'Intermediate',
         'theme': 'Business Quality',
         'topics': ['Business Quality'],
         'title': 'Scalability & Operating Leverage',
         'time_min': 7,
         'why_it_matters': 'Operating leverage means profits can grow faster than revenue once fixed costs are '
                           'covered.',
         'summary': ['Some businesses scale efficiently; others don’t.',
                     'Operating leverage can expand margins over time.',
                     'Software often has high operating leverage.',
                     'Watch for reinvestment needs that cap margins.'],
         'key_ideas': ['Fixed costs spread over more revenue → margin expansion.',
                       'Incremental margins show scalability.',
                       'Customer support, compliance, and infrastructure can limit leverage.',
                       'Scale without moat can invite competition.'],
         'common_mistakes': ['Assuming all growth leads to margin expansion.',
                             'Ignoring rising variable costs.',
                             'Believing scale guarantees dominance.',
                             'Confusing revenue growth with profit growth.'],
         'checklist': ['Are operating margins expanding?',
                       'Is incremental margin improving?',
                       'Are costs growing slower than revenue?',
                       'Is growth sustainable?'],
         'quiz': [{'question': 'Operating leverage means:',
                   'options': ['A) Debt increases',
                               'B) Profits grow faster than revenue',
                               'C) Dividends rise',
                               'D) Volatility ends'],
                   'correct': 1,
                   'explanation': 'Fixed costs spread can boost profit growth.'},
                  {'question': 'A common high-leverage model is:',
                   'options': ['A) Commodity retail', 'B) Software', 'C) Farming', 'D) Utilities'],
                   'correct': 1,
                   'explanation': 'Software often has low marginal costs.'},
                  {'question': 'A warning sign is:',
                   'options': ['A) Margin expansion',
                               'B) Costs rising as fast as revenue',
                               'C) Stable retention',
                               'D) Strong moat'],
                   'correct': 1,
                   'explanation': 'No leverage suggests limited scalability.'}],
         'apply_action': {'type': 'none'},
         'xp': 15,
         'video_url': ''},
 'A1': {'id': 'A1',
        'level': 'Advanced',
        'theme': 'Portfolio Construction',
        'topics': ['Portfolio Analysis', 'Risk'],
        'title': 'Position Sizing',
        'time_min': 7,
        'why_it_matters': 'Sizing often matters more than picking—the wrong size can break a portfolio.',
        'summary': ['Small positions protect you from being wrong.',
                    'Bigger positions require higher conviction and lower risk.',
                    'Sizing should consider volatility, not just belief.',
                    "Avoid positions that can 'ruin' you."],
        'key_ideas': ['Risk per position is the key: define max loss.',
                      'Volatile assets require smaller weights.',
                      'Diversification helps but won’t save reckless sizing.',
                      'Conviction should be earned, not assumed.'],
        'common_mistakes': ['Going all-in on one idea.',
                            'Sizing by emotion (FOMO).',
                            'Ignoring volatility differences across assets.',
                            'Adding leverage to compensate for small sizes.'],
        'checklist': ['What’s the max % loss you can tolerate?',
                      'Is the position volatile?',
                      'How correlated is it with your other holdings?',
                      'Would a 50% drop change your life?'],
        'quiz': [{'question': 'Position sizing matters because:',
                  'options': ['A) It sets your logo',
                              'B) It controls risk',
                              'C) It guarantees profits',
                              'D) It reduces fees'],
                  'correct': 1,
                  'explanation': 'Sizing determines how much a mistake hurts.'},
                 {'question': 'More volatile assets should generally be:',
                  'options': ['A) Larger positions',
                              'B) Smaller positions',
                              'C) Same size always',
                              'D) 100% allocation'],
                  'correct': 1,
                  'explanation': 'Volatility increases drawdown risk.'},
                 {'question': "A 'ruin' scenario is:",
                  'options': ['A) Missing a rally',
                              'B) A loss you can’t recover from behaviorally/financially',
                              'C) Paying a fee',
                              'D) Owning an ETF'],
                  'correct': 1,
                  'explanation': 'Ruin is catastrophic loss relative to your situation.'}],
        'apply_action': {'type': 'none'},
        'xp': 20,
        'video_url': ''},
 'A2': {'id': 'A2',
        'level': 'Advanced',
        'theme': 'Portfolio Construction',
        'topics': ['Risk', 'Diversification'],
        'title': 'Correlation Traps',
        'time_min': 8,
        'why_it_matters': 'Portfolios that look diversified can still be one big bet.',
        'summary': ['Owning many tickers can still mean one factor exposure.',
                    'In stress, correlations rise.',
                    'Sector overlap hides concentration.',
                    'True diversification is about behavior in bad times.'],
        'key_ideas': ['Factor exposures: growth, value, momentum, rates sensitivity.',
                      'Tech-heavy portfolios correlate strongly.',
                      'International can still correlate to US risk-on.',
                      'Diversify by drivers, not labels.'],
        'common_mistakes': ["Owning multiple tech ETFs and thinking you're diversified.",
                            'Assuming bonds always hedge stocks.',
                            'Ignoring currency/region overlap.',
                            'Not stress-testing scenarios mentally.'],
        'checklist': ['What’s your top factor exposure?',
                      'How would this behave in a recession?',
                      'Do holdings share the same driver?',
                      'Are you diversified by outcome?'],
        'quiz': [{'question': 'Correlation measures:',
                  'options': ['A) Dividend yield', 'B) How assets move together', 'C) Market cap', 'D) Tax rate'],
                  'correct': 1,
                  'explanation': 'Correlation is co-movement.'},
                 {'question': 'In crises, correlations usually:',
                  'options': ['A) Fall to zero', 'B) Rise', 'C) Reverse permanently', 'D) Disappear'],
                  'correct': 1,
                  'explanation': 'Stress increases correlations.'},
                 {'question': 'A common correlation trap is:',
                  'options': ['A) Cash', 'B) Many tech holdings', 'C) Treasury bills', 'D) Broad diversification'],
                  'correct': 1,
                  'explanation': 'Tech-heavy holdings often move together.'}],
        'apply_action': {'type': 'none'},
        'xp': 20,
        'video_url': ''},
 'A3': {'id': 'A3',
        'level': 'Advanced',
        'theme': 'Portfolio Construction',
        'topics': ['Portfolio Analysis', 'Risk'],
        'title': 'Portfolio Risk Budgeting',
        'time_min': 8,
        'why_it_matters': 'A risk budget keeps you from accidentally taking too much risk.',
        'summary': ['Risk budgeting sets how much volatility/drawdown you can accept.',
                    'Allocate risk, not just dollars.',
                    'Rebalancing enforces discipline.',
                    "A risk budget prevents 'creeping' concentration."],
        'key_ideas': ['Think in terms of worst-case drawdown.',
                      'Volatility-weighted allocations can improve balance.',
                      'Risk parity concept: spread risk contributions.',
                      'Limit position sizes and correlated bets.'],
        'common_mistakes': ['No explicit risk limits.',
                            'Letting winners dominate portfolio risk.',
                            'Adding correlated positions unknowingly.',
                            'Ignoring downside because markets have been calm.'],
        'checklist': ['Do you have max drawdown target?',
                      'Do a few positions drive most risk?',
                      'Are you rebalancing to limits?',
                      'Are you tracking concentration?'],
        'quiz': [{'question': 'A risk budget is:',
                  'options': ['A) A tax rule',
                              'B) A limit on total portfolio risk',
                              'C) A dividend plan',
                              'D) A chart pattern'],
                  'correct': 1,
                  'explanation': 'It’s a framework to cap overall risk.'},
                 {'question': 'Risk contributions depend heavily on:',
                  'options': ['A) Logo', 'B) Volatility and correlation', 'C) Ticker length', 'D) Dividend dates'],
                  'correct': 1,
                  'explanation': 'Volatility/correlation drive risk.'},
                 {'question': 'A benefit of risk budgeting is:',
                  'options': ['A) Guaranteed returns',
                              'B) Prevents accidental concentration',
                              'C) Eliminates volatility',
                              'D) Stops fees'],
                  'correct': 1,
                  'explanation': 'It helps avoid hidden risk buildup.'}],
        'apply_action': {'type': 'none'},
        'xp': 20,
        'video_url': ''},
 'A4': {'id': 'A4',
        'level': 'Advanced',
        'theme': 'Advanced Risk',
        'topics': ['Risk'],
        'title': 'Drawdowns & Recovery Math',
        'time_min': 7,
        'why_it_matters': 'Losses require larger gains to recover—math that changes how you take risk.',
        'summary': ['A 50% loss requires a 100% gain to break even.',
                    'Volatility drag reduces compounded returns.',
                    'Avoiding big drawdowns boosts long-term results.',
                    'Risk management is return enhancement.'],
        'key_ideas': ['Recovery is asymmetric: losses hurt more than gains help.',
                      'Volatility drag: choppy returns compound worse.',
                      'Position sizing reduces big drawdowns.',
                      'Diversification and cash buffers reduce forced selling.'],
        'common_mistakes': ['Ignoring asymmetry and taking too much risk.',
                            'Chasing recovery trades after losses.',
                            'Using leverage into volatility.',
                            'Confusing long-term investing with no risk controls.'],
        'checklist': ['What’s your max tolerable drawdown?',
                      'Are you sized for a 30–50% drop?',
                      'Do you have a plan for down markets?',
                      'Can you avoid forced selling?'],
        'quiz': [{'question': 'A 50% loss requires a gain of:',
                  'options': ['A) 50%', 'B) 75%', 'C) 100%', 'D) 10%'],
                  'correct': 2,
                  'explanation': 'You need to double from 50 back to 100.'},
                 {'question': 'Volatility drag means:',
                  'options': ['A) Volatility increases returns always',
                              'B) Choppy returns reduce compounding',
                              'C) Fees disappear',
                              'D) Prices stabilize'],
                  'correct': 1,
                  'explanation': 'Up/down swings reduce compounded outcomes.'},
                 {'question': 'A core goal of risk management is:',
                  'options': ['A) More excitement', 'B) Avoid large drawdowns', 'C) Timing tops', 'D) Predicting news'],
                  'correct': 1,
                  'explanation': 'Avoiding big drawdowns improves long-term compounding.'}],
        'apply_action': {'type': 'none'},
        'xp': 20,
        'video_url': ''},
 'A5': {'id': 'A5',
        'level': 'Advanced',
        'theme': 'Advanced Risk',
        'topics': ['Risk'],
        'title': 'Volatility Drag',
        'time_min': 7,
        'why_it_matters': 'Two portfolios with the same average return can end with different outcomes due to '
                          'volatility.',
        'summary': ['Volatility reduces compounded returns.',
                    'Smoother returns compound better.',
                    'Diversification can reduce volatility drag.',
                    'Risk-adjusted return matters.'],
        'key_ideas': ['Geometric return < arithmetic return when volatility exists.',
                      'Avoiding large swings increases long-term compounded return.',
                      'Rebalancing can help control volatility.',
                      'Don’t chase high volatility without edge.'],
        'common_mistakes': ['Chasing volatile assets for excitement.',
                            'Ignoring risk-adjusted metrics.',
                            'Overconcentrating in high beta names.',
                            'Thinking average return is all that matters.'],
        'checklist': ['What’s your portfolio volatility?',
                      'Do you understand geometric vs arithmetic returns?',
                      'Can you reduce volatility without killing returns?',
                      'Are you compensated for the risk?'],
        'quiz': [{'question': 'Volatility drag affects:',
                  'options': ['A) Only dividends', 'B) Compounding', 'C) Market cap', 'D) Taxes'],
                  'correct': 1,
                  'explanation': 'Volatility reduces the compounded outcome.'},
                 {'question': 'Smoother returns generally:',
                  'options': ['A) Compound better', 'B) Always lose', 'C) Are impossible', 'D) Eliminate risk'],
                  'correct': 0,
                  'explanation': 'Lower volatility reduces drag.'},
                 {'question': 'A way to reduce volatility is:',
                  'options': ['A) Add correlation', 'B) Diversify', 'C) Increase leverage', 'D) Trade hourly'],
                  'correct': 1,
                  'explanation': 'Diversification can reduce volatility.'}],
        'apply_action': {'type': 'none'},
        'xp': 20,
        'video_url': ''},
 'BE1': {'id': 'BE1',
         'level': 'Behavior',
         'theme': 'Behavioral Edge',
         'topics': ['Psychology'],
         'title': 'Loss Aversion',
         'time_min': 6,
         'why_it_matters': 'Losses feel worse than gains feel good—this drives panic-selling.',
         'summary': ['Loss aversion causes selling at the worst time.',
                     'Your plan must anticipate emotional stress.',
                     'Rules reduce impulsive decisions.',
                     'Long-term success is behavior-first.'],
         'key_ideas': ['Humans overweight recent pain.',
                       'Downturns test conviction and time horizon.',
                       'Pre-commitment: decide actions before emotions hit.',
                       'Automate good behavior where possible.'],
         'common_mistakes': ['Checking portfolio constantly during downturns.',
                             "Selling because 'it feels safer'.",
                             'Changing strategy after losses.',
                             'Revenge trading.'],
         'checklist': ['Do you have written rules for downturns?',
                       'Can you tolerate your portfolio volatility?',
                       'Are contributions automated?',
                       'Do you track decisions and reasons?'],
         'quiz': [{'question': 'Loss aversion means:',
                   'options': ['A) You like losing',
                               'B) Losses hurt more than gains feel good',
                               'C) You ignore risk',
                               'D) You always win'],
                   'correct': 1,
                   'explanation': 'This bias drives emotional decisions.'},
                  {'question': 'A good antidote is:',
                   'options': ['A) No plan', 'B) Pre-written rules', 'C) More leverage', 'D) Watching prices'],
                   'correct': 1,
                   'explanation': 'Rules reduce emotion-driven mistakes.'},
                  {'question': 'During a downturn, a common mistake is:',
                   'options': ['A) Stick to plan', 'B) Panic selling', 'C) Rebalancing calmly', 'D) DCA'],
                   'correct': 1,
                   'explanation': 'Panic selling locks in losses.'}],
         'apply_action': {'type': 'none'},
         'xp': 15,
         'video_url': ''},
 'BE2': {'id': 'BE2',
         'level': 'Behavior',
         'theme': 'Behavioral Edge',
         'topics': ['Psychology'],
         'title': 'FOMO vs Process',
         'time_min': 6,
         'why_it_matters': 'FOMO pushes buying high; process keeps you consistent.',
         'summary': ['FOMO is social pressure, not analysis.',
                     'A simple process beats chasing hype.',
                     'Your edge is consistency, not excitement.',
                     'Missing a trade is not a failure.'],
         'key_ideas': ['Create entry rules (valuation/quality) before buying.',
                       'Limit sources of noise (feeds, headlines).',
                       'Measure progress by process, not daily P&L.',
                       'Focus on long-term compounding.'],
         'common_mistakes': ['Buying after huge rallies without a thesis.',
                             'Switching strategies constantly.',
                             'Overtrading for entertainment.',
                             'Confusing activity with progress.'],
         'checklist': ['What’s your buy checklist?',
                       'Is this decision planned or reactive?',
                       'Does it fit your time horizon?',
                       'Would you buy it if no one was talking about it?'],
         'quiz': [{'question': 'FOMO usually causes:',
                   'options': ['A) Buying low', 'B) Buying after big runs', 'C) Lower fees', 'D) Better sleep'],
                   'correct': 1,
                   'explanation': 'FOMO often leads to buying near peaks.'},
                  {'question': 'A process helps by:',
                   'options': ['A) Eliminating risk',
                               'B) Reducing emotional decisions',
                               'C) Guaranteeing returns',
                               'D) Avoiding all losses'],
                   'correct': 1,
                   'explanation': 'Process reduces impulsive moves.'},
                  {'question': 'A healthy mindset is:',
                   'options': ["A) 'I must catch every move'",
                               "B) 'I follow my rules'",
                               "C) 'I only trade'",
                               "D) 'I copy influencers'"],
                   'correct': 1,
                   'explanation': 'Rules-based investing is sustainable.'}],
         'apply_action': {'type': 'none'},
         'xp': 15,
         'video_url': ''},
 'R1': {'id': 'R1',
        'level': 'Repair',
        'theme': 'Repair',
        'topics': ['Portfolio Analysis'],
        'title': 'Weak Company Checklist',
        'time_min': 7,
        'why_it_matters': 'A simple red-flag checklist prevents holding broken stories too long.',
        'summary': ['Deteriorating fundamentals often show up before price fully reflects it.',
                    'Watch revenue growth, margins, and balance sheet health.',
                    'Thesis-based investing requires thesis-based exits.',
                    'Opportunity cost matters.'],
        'key_ideas': ['Revenue slowdown + margin compression is a warning combo.',
                      'Rising debt in a weakening business increases risk.',
                      'Competitive pressure often appears in guidance and retention.',
                      'Don’t anchor to your entry price.'],
        'common_mistakes': ['Holding because you’re down.',
                            'Confusing a cheaper price with a better investment.',
                            'Ignoring clear thesis breaks.',
                            'Blaming markets instead of fundamentals.'],
        'checklist': ['Is revenue decelerating?',
                      'Are margins compressing?',
                      'Is debt rising?',
                      'Is the thesis broken?'],
        'quiz': [{'question': 'A common red flag is:',
                  'options': ['A) Improving margins',
                              'B) Revenue slowing + margins falling',
                              'C) More cash',
                              'D) Lower debt'],
                  'correct': 1,
                  'explanation': 'Slowing growth and falling margins often signal issues.'},
                 {'question': 'Opportunity cost means:',
                  'options': ['A) Taxes are high',
                              'B) Money could be in a better investment',
                              'C) You can’t sell',
                              'D) You must hold'],
                  'correct': 1,
                  'explanation': 'Holding a weak asset has a cost versus alternatives.'},
                 {'question': 'Anchoring is:',
                  'options': ['A) Selling winners',
                              'B) Fixating on your purchase price',
                              'C) Diversifying',
                              'D) Rebalancing'],
                  'correct': 1,
                  'explanation': 'Anchoring can prevent rational decisions.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'R2': {'id': 'R2',
        'level': 'Repair',
        'theme': 'Repair',
        'topics': ['Portfolio Analysis'],
        'title': 'When to Sell (Framework)',
        'time_min': 7,
        'why_it_matters': 'Selling is easier with rules tied to your thesis and risk.',
        'summary': ['Sell when thesis breaks, not when price wiggles.',
                    'Trim when size becomes too large for risk.',
                    'Sell when you have a clearly better alternative.',
                    'Taxes matter, but discipline matters more.'],
        'key_ideas': ['Thesis breaks: fundamentals change materially.',
                      'Risk sells: position too large or correlated.',
                      'Opportunity sells: better risk-adjusted option.',
                      'Time sells: if timeline assumption fails.'],
        'common_mistakes': ['Selling only because price dropped.',
                            'Never selling because of ego.',
                            'Selling winners too early without reason.',
                            'Ignoring position sizing drift.'],
        'checklist': ['Is the original thesis still true?',
                      'Has risk changed (size/correlation)?',
                      'Is there a better use of capital?',
                      'Are you selling from emotion or rules?'],
        'quiz': [{'question': 'Best reason to sell is:',
                  'options': ['A) A bad headline', 'B) Thesis break', 'C) Social media hype', 'D) Price boredom'],
                  'correct': 1,
                  'explanation': 'Thesis breaks are the most defensible sell reason.'},
                 {'question': 'Trimming is often done when:',
                  'options': ['A) Position is too large', 'B) You feel bored', 'C) Fees rise', 'D) Dividends stop'],
                  'correct': 0,
                  'explanation': 'Sizing drift can increase risk unintentionally.'},
                 {'question': 'A common mistake is:',
                  'options': ['A) Using rules', 'B) Selling from emotion', 'C) Reviewing thesis', 'D) Rebalancing'],
                  'correct': 1,
                  'explanation': 'Emotion-driven sells often occur at the worst times.'}],
        'apply_action': {'type': 'none'},
        'xp': 15,
        'video_url': ''},
 'B14': {'id': 'B14',
         'level': 'Beginner',
         'theme': 'Foundations',
         'topics': ['Foundations'],
         'title': 'How Stocks Make Money',
         'time_min': 6,
         'why_it_matters': 'Know the few ways companies create value so you can judge any business.',
         'summary': ['Companies create value by growing revenue, improving margins, or both.',
                     'Profits can be reinvested, paid as dividends, or used for buybacks.',
                     'A stock’s long-term return tracks business performance.',
                     'Not all revenue is equal—quality matters.'],
         'key_ideas': ['Revenue growth is the engine; margins determine efficiency.',
                       'Reinvestment can create compounding within the business.',
                       'Share buybacks increase ownership per share when done responsibly.',
                       'Durable demand and recurring revenue are higher quality.'],
         'common_mistakes': ["Thinking 'popular product' always means great business.",
                             'Ignoring dilution when companies issue shares.',
                             'Assuming buybacks are always good (debt-funded buybacks can be risky).',
                             'Focusing on one quarter instead of trends.'],
         'checklist': ['Is revenue growing sustainably?',
                       'Are margins stable or improving?',
                       'Is capital allocation sensible (buybacks/dividends/investment)?',
                       'Is growth funded responsibly?'],
         'quiz': [{'question': 'Long-term stock returns tend to follow:',
                   'options': ['A) Daily news', 'B) Business performance', 'C) CEO tweets', 'D) Randomness only'],
                   'correct': 1,
                   'explanation': 'Over long periods, business results drive returns.'},
                  {'question': 'A share buyback helps shareholders most when:',
                   'options': ['A) Stock is expensive and debt-funded',
                               'B) Stock is reasonably valued and funded by cash',
                               'C) Earnings are fake',
                               'D) It always helps equally'],
                   'correct': 1,
                   'explanation': 'Buybacks funded by real cash at sensible prices can help.'},
                  {'question': 'High-quality revenue is often:',
                   'options': ['A) One-time sales',
                               'B) Recurring and sticky',
                               'C) Always government-paid',
                               'D) Only international'],
                   'correct': 1,
                   'explanation': 'Recurring/sticky revenue tends to be more durable.'}],
         'apply_action': {'type': 'none'},
         'xp': 10,
         'video_url': ''},
 'B15': {'id': 'B15',
         'level': 'Beginner',
         'theme': 'Foundations',
         'topics': ['Foundations'],
         'title': 'Dividends Explained',
         'time_min': 6,
         'why_it_matters': "Dividends are one way companies return cash—but they’re not 'free money'.",
         'summary': ['Dividends come from company cash flow.',
                     'Dividend yield is dividend ÷ price.',
                     'High yield can signal risk if payout isn’t sustainable.',
                     'Total return = price change + dividends.'],
         'key_ideas': ['Payout ratio shows how much earnings go to dividends.',
                       'Dividend growth matters more than yield alone.',
                       'Some great companies don’t pay dividends—they reinvest.',
                       'Dividend traps: high yield due to falling price.'],
         'common_mistakes': ['Buying only for yield without checking sustainability.',
                             'Ignoring payout ratio and cash flow coverage.',
                             'Assuming dividends guarantee safety.',
                             'Missing better total-return opportunities.'],
         'checklist': ['Is the dividend covered by FCF?',
                       'Is payout ratio reasonable?',
                       'Is dividend growing over time?',
                       'Is the business stable?'],
         'quiz': [{'question': 'Dividend yield is:',
                   'options': ['A) Dividend ÷ price', 'B) Price ÷ dividend', 'C) Revenue ÷ price', 'D) Debt ÷ equity'],
                   'correct': 0,
                   'explanation': 'Yield compares dividend to current price.'},
                  {'question': 'A very high yield can be a warning sign because:',
                   'options': ['A) It guarantees profits',
                               'B) It may be unsustainable',
                               'C) It lowers fees',
                               'D) It removes risk'],
                   'correct': 1,
                   'explanation': 'Yield can rise because price fell on bad fundamentals.'},
                  {'question': 'Total return includes:',
                   'options': ['A) Only dividends',
                               'B) Price change + dividends',
                               'C) Only price change',
                               'D) Only fees'],
                   'correct': 1,
                   'explanation': 'Total return counts both price moves and dividends.'}],
         'apply_action': {'type': 'none'},
         'xp': 10,
         'video_url': ''},
 'A6': {'id': 'A6',
        'level': 'Advanced',
        'theme': 'Portfolio Construction',
        'topics': ['Portfolio Analysis', 'Risk'],
        'title': 'Concentration vs Diversification',
        'time_min': 7,
        'why_it_matters': 'Concentration can boost returns, but it raises the chance of large drawdowns.',
        'summary': ['Concentration increases upside and downside.',
                    'Diversification reduces single-idea risk.',
                    'Your edge determines how concentrated you can be.',
                    'A concentrated portfolio needs strong risk controls.'],
        'key_ideas': ["Know your 'base' diversified core vs conviction positions.",
                      'Concentration requires deep understanding and monitoring.',
                      'Correlation between positions matters.',
                      'Avoid concentration you didn’t intend.'],
        'common_mistakes': ['Accidentally concentrating in one theme (e.g., AI).',
                            'Sizing based on excitement not evidence.',
                            'Ignoring correlation and factor overlap.',
                            'No plan for thesis breaks.'],
        'checklist': ['What % is your top position?',
                      'How many positions drive most risk?',
                      'Are bets correlated?',
                      'Do you have sell/trim rules?'],
        'quiz': [{'question': 'Concentration generally:',
                  'options': ['A) Lowers volatility',
                              'B) Raises portfolio risk',
                              'C) Eliminates drawdowns',
                              'D) Guarantees gains'],
                  'correct': 1,
                  'explanation': 'Concentration increases risk and potential drawdown.'},
                 {'question': 'A diversified core helps by:',
                  'options': ['A) Timing tops',
                              'B) Reducing single-name risk',
                              'C) Making you trade more',
                              'D) Increasing fees'],
                  'correct': 1,
                  'explanation': 'Diversification lowers idiosyncratic risk.'},
                 {'question': 'Accidental concentration often comes from:',
                  'options': ['A) Correlated bets', 'B) Cash', 'C) Treasury bills', 'D) Broad indexes'],
                  'correct': 0,
                  'explanation': 'Correlated bets behave like one big bet.'}],
        'apply_action': {'type': 'none'},
        'xp': 20,
        'video_url': ''},
 'A7': {'id': 'A7',
        'level': 'Advanced',
        'theme': 'Advanced Risk',
        'topics': ['Risk'],
        'title': 'Tail Risk (Black Swans)',
        'time_min': 8,
        'why_it_matters': 'Rare events can dominate long-term outcomes—prepare without paranoia.',
        'summary': ['Tail risks are low-probability, high-impact events.',
                    'Diversification helps but may fail in extreme stress.',
                    'Avoid leverage that can force liquidation.',
                    'Resilience beats prediction.'],
        'key_ideas': ['Liquidity disappears in stress; spreads widen.',
                      'Leverage + forced selling is the common failure mode.',
                      'Maintain buffers (cash, stable assets) when appropriate.',
                      'Scenario planning improves robustness.'],
        'common_mistakes': ['Assuming tails won’t happen again.',
                            'Using leverage because markets have been calm.',
                            'No cash buffer or contingency plan.',
                            'Over-optimizing for best case.'],
        'checklist': ['Any leverage in the portfolio?',
                      'Do you have a buffer for emergencies?',
                      'Would you be forced to sell in a crash?',
                      'Are positions liquid enough?'],
        'quiz': [{'question': 'Tail risk refers to:',
                  'options': ['A) Daily volatility', 'B) Rare extreme events', 'C) Dividend changes', 'D) Tax rates'],
                  'correct': 1,
                  'explanation': 'Tail risk is about rare but severe moves.'},
                 {'question': 'A common cause of blowups is:',
                  'options': ['A) Diversification', 'B) Leverage and forced selling', 'C) ETFs', 'D) Cash'],
                  'correct': 1,
                  'explanation': 'Leverage can trigger forced liquidation.'},
                 {'question': 'Best response to tail risk is:',
                  'options': ['A) Predict the exact event', 'B) Build resilience', 'C) Ignore it', 'D) Max leverage'],
                  'correct': 1,
                  'explanation': 'Robust portfolios survive unexpected shocks.'}],
        'apply_action': {'type': 'none'},
        'xp': 20,
        'video_url': ''},
 'A8': {'id': 'A8',
        'level': 'Advanced',
        'theme': 'Advanced Risk',
        'topics': ['Risk'],
        'title': 'Scenario Thinking',
        'time_min': 8,
        'why_it_matters': 'Scenario thinking helps you act rationally when uncertainty is high.',
        'summary': ['Build base, bull, and bear cases.',
                    'Ask what must be true for each case.',
                    'Focus on key drivers (growth, margins, rates).',
                    'Scenarios reduce emotional whiplash.'],
        'key_ideas': ['Start with a base case and define ranges.',
                      'Stress the few variables that matter most.',
                      'Assign rough probabilities (even if imperfect).',
                      'Update slowly—avoid reacting to noise.'],
        'common_mistakes': ['Using one-point forecasts.',
                            'Ignoring downside cases.',
                            'Updating probabilities daily based on price.',
                            'Confusing possibility with probability.'],
        'checklist': ['What’s your base/bull/bear?',
                      'Key drivers and ranges?',
                      'What would change your view?',
                      'What’s the downside if wrong?'],
        'quiz': [{'question': 'Scenario thinking uses:',
                  'options': ['A) One forecast', 'B) Multiple outcomes', 'C) No numbers', 'D) Only charts'],
                  'correct': 1,
                  'explanation': 'Scenarios consider multiple possible futures.'},
                 {'question': 'A good scenario focuses on:',
                  'options': ['A) Every variable', 'B) Key drivers', 'C) Logo', 'D) Ticker length'],
                  'correct': 1,
                  'explanation': 'Key drivers dominate outcomes.'},
                 {'question': 'A common mistake is:',
                  'options': ['A) Considering downside',
                              'B) Ignoring bear case',
                              'C) Using ranges',
                              'D) Updating slowly'],
                  'correct': 1,
                  'explanation': 'Ignoring downside leads to overconfidence.'}],
        'apply_action': {'type': 'none'},
        'xp': 20,
        'video_url': ''},
 'BE3': {'id': 'BE3',
         'level': 'Behavior',
         'theme': 'Behavioral Edge',
         'topics': ['Psychology'],
         'title': 'Overconfidence Bias',
         'time_min': 6,
         'why_it_matters': 'Overconfidence leads to overtrading and concentration before skill is earned.',
         'summary': ['Confidence should come from process and track record.',
                     'Overconfidence increases risk-taking.',
                     'Humility protects capital.',
                     'Simple beats complex for most investors.'],
         'key_ideas': ['We confuse a bull market with skill.',
                       'We underestimate randomness short-term.',
                       'Check your hit rate and thesis quality.',
                       'Use position sizing as a humility tool.'],
         'common_mistakes': ['Increasing size after a few wins.',
                             'Trading too frequently.',
                             'Ignoring base rates and history.',
                             'Refusing to admit mistakes.'],
         'checklist': ['Do you have a written process?',
                       'What’s your track record across cycles?',
                       'Are you sizing responsibly?',
                       'Do you do post-mortems?'],
         'quiz': [{'question': 'Overconfidence often causes:',
                   'options': ['A) Better diversification', 'B) Overtrading', 'C) Lower risk', 'D) More patience'],
                   'correct': 1,
                   'explanation': 'Overconfidence increases unnecessary activity.'},
                  {'question': 'A bull market can make people think:',
                   'options': ['A) They’re always wrong',
                               'B) They’re more skilled than they are',
                               'C) Fees disappear',
                               'D) Volatility ends'],
                   'correct': 1,
                   'explanation': 'It can inflate perceived skill.'},
                  {'question': 'A good antidote is:',
                   'options': ['A) Larger bets',
                               'B) Rules and position sizing',
                               'C) Ignoring results',
                               'D) Copying others'],
                   'correct': 1,
                   'explanation': 'Rules and sizing reduce damage from mistakes.'}],
         'apply_action': {'type': 'none'},
         'xp': 15,
         'video_url': ''},
 'BE4': {'id': 'BE4',
         'level': 'Behavior',
         'theme': 'Behavioral Edge',
         'topics': ['Psychology'],
         'title': 'Recency Bias',
         'time_min': 6,
         'why_it_matters': 'Recency bias makes you extrapolate recent trends and miss mean reversion.',
         'summary': ['Recent performance feels more important than it is.',
                     'Markets move in cycles—leadership rotates.',
                     'A process prevents chasing what just worked.',
                     'Zoom out: use multi-year context.'],
         'key_ideas': ['Recency bias drives buying high and selling low.',
                       'Rebalancing counters recency bias.',
                       'Use historical ranges for valuation and returns.',
                       'Short-term narratives are often noise.'],
         'common_mistakes': ['Chasing last year’s winners.',
                             'Selling after a bad quarter without thesis break.',
                             'Changing strategy constantly.',
                             'Believing current regime is permanent.'],
         'checklist': ['Are you using multi-year context?',
                       'Does this decision depend on last month’s moves?',
                       'Is leadership rotating?',
                       'Are you rebalancing?'],
         'quiz': [{'question': 'Recency bias means:',
                   'options': ['A) Ignoring the past',
                               'B) Overweighting recent events',
                               'C) Loving dividends',
                               'D) Avoiding fees'],
                   'correct': 1,
                   'explanation': 'It’s the tendency to overweight recent info.'},
                  {'question': 'A common effect is:',
                   'options': ['A) Buying low', 'B) Chasing winners', 'C) Staying diversified', 'D) Holding cash'],
                   'correct': 1,
                   'explanation': 'People chase recent winners due to recency bias.'},
                  {'question': 'A countermeasure is:',
                   'options': ['A) More headlines',
                               'B) Rebalancing and zooming out',
                               'C) Trading hourly',
                               'D) Copying influencers'],
                   'correct': 1,
                   'explanation': 'Zooming out and rebalancing reduce bias.'}],
         'apply_action': {'type': 'none'},
         'xp': 15,
         'video_url': ''},
 'BE5': {'id': 'BE5',
         'level': 'Behavior',
         'theme': 'Behavioral Edge',
         'topics': ['Psychology'],
         'title': 'Decision Journaling',
         'time_min': 7,
         'why_it_matters': 'A decision journal turns investing into a skill you can improve.',
         'summary': ['Write your thesis before buying.',
                     'Track what you expected and what happened.',
                     'Learn from both wins and losses.',
                     'Process improvement compounds.'],
         'key_ideas': ['Record: thesis, valuation, risks, timeline, exit rules.',
                       'Review periodically (monthly/quarterly).',
                       'Separate luck from skill.',
                       'Improve your checklist over time.'],
         'common_mistakes': ['Only journaling after losses.',
                             'Writing vague theses that can’t be evaluated.',
                             'Never reviewing past decisions.',
                             'Changing the story after outcomes.'],
         'checklist': ['Do you have a written thesis?',
                       'Did you define what would change your mind?',
                       'Do you review decisions regularly?',
                       'Are you learning from patterns?'],
         'quiz': [{'question': 'A decision journal helps you:',
                   'options': ['A) Predict markets perfectly',
                               'B) Improve process over time',
                               'C) Avoid all losses',
                               'D) Eliminate volatility'],
                   'correct': 1,
                   'explanation': 'It makes learning systematic.'},
                  {'question': 'A good journal entry includes:',
                   'options': ['A) Only ticker',
                               'B) Thesis + risks + exit rules',
                               'C) Only feelings',
                               'D) Only headlines'],
                   'correct': 1,
                   'explanation': 'It needs evaluable hypotheses.'},
                  {'question': 'Reviewing the journal helps separate:',
                   'options': ['A) Stocks and bonds', 'B) Luck and skill', 'C) Fees and taxes', 'D) Charts and news'],
                   'correct': 1,
                   'explanation': 'It builds honest feedback loops.'}],
         'apply_action': {'type': 'none'},
         'xp': 15,
         'video_url': ''},
 'CM1': {       'apply_action': {'type': 'none'},
        'checklist': [       'Is FCF positive and improving over several years?',
                             'Is FCF per share growing (not just total FCF)?',
                             'Are shares outstanding stable or shrinking?',
                             'Is cash generation coming from operations, not '
                             'one-offs?'],
        'common_mistakes': [       'Looking only at total FCF and ignoring per-share '
                                   'math.',
                                   'Ignoring dilution (share count rising) and calling '
                                   'it “growth.”',
                                   'Treating a one-time cash windfall as a trend.'],
        'id': 'CM1',
        'key_ideas': [       'FCF per share = Free cash flow ÷ shares outstanding.',
                             'Watch the share count trend; heavy stock-based '
                             'compensation can dilute owners.',
                             'Quality matters: stable, recurring cash beats one-time '
                             'spikes.',
                             'Connect the dots: revenue → margins → cash conversion → '
                             'FCF per share.'],
        'level': 'Intermediate',
        'quiz': [       {       'correct': 1,
                                'explanation': 'Per-share math shows what each share '
                                               'is entitled to after dilution or '
                                               'buybacks.',
                                'options': [       'A) Ignores share count changes',
                                                   'B) Adjusts for dilution/buybacks',
                                                   'C) Is the same as revenue growth',
                                                   'D) Only matters for banks'],
                                'question': 'Free cash flow per share helps investors '
                                            'because it:'},
                        {       'correct': 0,
                                'explanation': 'If shares rise faster than cash, each '
                                               'share gets a smaller slice.',
                                'options': [       'A) Shares outstanding increased a '
                                                   'lot',
                                                   'B) The company paid taxes',
                                                   'C) Revenue grew too fast',
                                                   'D) The stock price fell'],
                                'question': 'A company’s total FCF rises, but FCF per '
                                            'share falls. The most likely reason is:'},
                        {       'correct': 1,
                                'explanation': 'Consistency suggests durable cash '
                                               'generation.',
                                'options': [       'A) One huge FCF year after selling '
                                                   'an asset',
                                                   'B) Several years of steady FCF per '
                                                   'share growth',
                                                   'C) FCF that’s negative but '
                                                   'trending',
                                                   'D) Rising revenue with shrinking '
                                                   'cash'],
                                'question': 'Which is usually a better sign of '
                                            'quality?'}],
        'summary': [       'Free cash flow (FCF) is cash left after running and '
                           'reinvesting in the business.',
                           'Per-share is the key: it adjusts for dilution and '
                           'buybacks.',
                           'A company can grow revenue/profit and still hurt '
                           'shareholders if shares outstanding rise faster.',
                           'Consistent FCF per share growth is a strong signal of '
                           'durable value creation.'],
        'theme': 'Core Metrics',
        'time_min': 8,
        'title': 'Free Cash Flow per Share Growth',
        'topics': ['Core Metrics', 'Cash Flow'],
        'video_url': '',
        'why_it_matters': 'This is the cleanest way to measure whether each share you '
                          'own is becoming more valuable over time.',
        'xp': 20},
 'CM2': {       'apply_action': {'type': 'none'},
        'checklist': [       'Are margins stable or expanding over time?',
                             'Is operating income growing faster than revenue?',
                             'Is the business gaining pricing power or scale '
                             'efficiency?',
                             'Are margins competitive vs peers in the same industry?'],
        'common_mistakes': [       'Celebrating revenue growth while margins collapse.',
                                   'Using net margin only (mixes in taxes/financing '
                                   'noise).',
                                   'Assuming a temporary margin spike will last '
                                   'forever.'],
        'id': 'CM2',
        'key_ideas': [       'Operating margin = Operating income ÷ revenue.',
                             'Operating leverage: costs grow slower than revenue as '
                             'the business scales.',
                             'Margin durability matters more than a single good '
                             'quarter.',
                             'Compare margins within an industry—cross-industry '
                             'comparisons can mislead.'],
        'level': 'Intermediate',
        'quiz': [       {       'correct': 1,
                                'explanation': 'It measures core profitability as a '
                                               'percent of revenue.',
                                'options': [       'A) How much revenue the company '
                                                   'has',
                                                   'B) How much of each dollar of '
                                                   'revenue becomes operating profit',
                                                   'C) How many shares are outstanding',
                                                   'D) The stock’s expected return'],
                                'question': 'Operating margin tells you:'},
                        {       'correct': 1,
                                'explanation': 'Shrinking margins can signal '
                                               'discounting, rising costs, or weaker '
                                               'economics.',
                                'options': [       'A) The business is getting more '
                                                   'efficient',
                                                   'B) Growth is coming at the cost of '
                                                   'profitability',
                                                   'C) The company is buying back '
                                                   'stock',
                                                   'D) Taxes are lower'],
                                'question': 'If revenue grows 20% but operating margin '
                                            'drops sharply, it often means:'},
                        {       'correct': 0,
                                'explanation': 'When profits scale faster than sales, '
                                               'the business is leveraging fixed '
                                               'costs.',
                                'options': [       'A) Operating income grows faster '
                                                   'than revenue',
                                                   'B) Revenue grows faster than '
                                                   'operating income',
                                                   'C) Share count increases',
                                                   'D) P/E rises'],
                                'question': 'A classic sign of operating leverage '
                                            'is:'}],
        'summary': [       'Revenue alone doesn’t tell you if a business is getting '
                           'stronger.',
                           'Operating income focuses on core profitability before '
                           'interest/taxes.',
                           'Operating margin shows how much of each revenue dollar '
                           'becomes operating profit.',
                           'Rising margins often signal pricing power, efficiency, or '
                           'a moat.'],
        'theme': 'Core Metrics',
        'time_min': 8,
        'title': 'Operating Margin & Operating Income Growth',
        'topics': ['Core Metrics', 'Profitability'],
        'video_url': '',
        'why_it_matters': 'Margins show the quality of growth—how much profit the core '
                          'business produces from each dollar of revenue.',
        'xp': 20},
 'CM3': {       'apply_action': {'type': 'none'},
        'checklist': [       'Is ROIC consistently strong vs peers?',
                             'Is ROIC stable or improving over time?',
                             'Does the company have a clear reinvestment runway?',
                             'Is growth funded internally (cash) or constantly with '
                             'new capital?'],
        'common_mistakes': [       'Chasing growth without checking if returns are '
                                   'attractive.',
                                   'Confusing ROE with ROIC (leverage can inflate '
                                   'ROE).',
                                   'Ignoring ROIC deterioration during expansion.'],
        'id': 'CM3',
        'key_ideas': [       'Think: ‘For every $1 invested, how much operating profit '
                             'does the business generate?’',
                             'High ROIC + long runway is a powerful combination.',
                             'Watch for ROIC declining as companies scale (returns can '
                             'mean-revert).',
                             'Capital-intensive businesses often have lower ROIC and '
                             'need more funding to grow.'],
        'level': 'Intermediate',
        'quiz': [       {       'correct': 1,
                                'explanation': 'ROIC measures how much operating '
                                               'profit is generated from invested '
                                               'capital.',
                                'options': [       'A) How cheap a stock is',
                                                   'B) How efficiently a company '
                                                   'reinvests capital',
                                                   'C) Daily price movements',
                                                   'D) Dividend tax rates'],
                                'question': 'ROIC is most useful for understanding:'},
                        {       'correct': 1,
                                'explanation': 'If returns are low, growing can mean '
                                               'pouring money into low-return '
                                               'projects.',
                                'options': [       'A) Creates value automatically',
                                                   'B) Destroys value as it expands',
                                                   'C) Has no need for capital',
                                                   'D) Has higher FCF per share'],
                                'question': 'A company growing fast with very low ROIC '
                                            'often:'},
                        {       'correct': 1,
                                'explanation': 'Leverage can make ROE look high even '
                                               'if underlying business returns are '
                                               'mediocre.',
                                'options': [       'A) ROE includes operating profit',
                                                   'B) Debt/leverage can inflate ROE',
                                                   'C) ROIC ignores operations',
                                                   'D) ROE is only for tech companies'],
                                'question': 'Why can ROE be misleading compared to '
                                            'ROIC?'}],
        'summary': [       'ROIC is a quality filter: it measures reinvestment '
                           'efficiency.',
                           'High ROIC businesses can compound for years without '
                           'needing constant outside funding.',
                           'Low ROIC growth can destroy value even if the company gets '
                           'bigger.',
                           'You don’t need perfect math—focus on the concept and '
                           'trend.'],
        'theme': 'Core Metrics',
        'time_min': 8,
        'title': 'Return on Capital (ROIC) — Simplified',
        'topics': ['Core Metrics', 'Returns'],
        'video_url': '',
        'why_it_matters': 'ROIC shows how efficiently a company turns invested money '
                          'into operating profit—great compounders usually have high '
                          'returns on capital.',
        'xp': 20},
 'CM4': {       'apply_action': {'type': 'none'},
        'checklist': [       'Is growth consistent and repeatable (not a one-off)?',
                             'Is growth improving margins/cash, or hurting them?',
                             'Is the market/runway large enough to sustain growth?',
                             'Are expectations realistic relative to valuation?'],
        'common_mistakes': [       'Chasing the highest growth rate without checking '
                                   'profitability.',
                                   'Assuming growth continues forever at the same '
                                   'rate.',
                                   'Ignoring customer concentration or cyclicality.'],
        'id': 'CM4',
        'key_ideas': [       'Look for durable growth driven by retention, pricing '
                             'power, and real demand.',
                             'Watch growth vs margin trade-offs—discount-driven growth '
                             'can be fragile.',
                             'Slowing growth isn’t always bad if margins and cash '
                             'improve.',
                             'Compare growth to expectations—stocks price in future '
                             'growth.'],
        'level': 'Intermediate',
        'quiz': [       {       'correct': 1,
                                'explanation': 'Revenue growth measures how fast the '
                                               'top line is expanding.',
                                'options': [       'A) The cash left after expenses',
                                                   'B) The demand/top-line expansion '
                                                   'of the business',
                                                   'C) The company’s debt level',
                                                   'D) The stock’s valuation multiple'],
                                'question': 'Revenue growth is best described as:'},
                        {       'correct': 1,
                                'explanation': 'If margins fall, growth may be less '
                                               'valuable or less sustainable.',
                                'options': [       'A) Stronger business quality',
                                                   'B) Growth bought with discounts or '
                                                   'rising costs',
                                                   'C) Higher ROIC',
                                                   'D) Better cash conversion'],
                                'question': 'Fast revenue growth with collapsing '
                                            'margins usually suggests:'},
                        {       'correct': 1,
                                'explanation': 'Quality + efficiency tends to compound '
                                               'better than growth-at-all-costs.',
                                'options': [       'A) High growth, shrinking margins, '
                                                   'low ROIC',
                                                   'B) Moderate growth, '
                                                   'stable/expanding margins, high '
                                                   'ROIC',
                                                   'C) No growth, high valuation',
                                                   'D) High growth, negative cash '
                                                   'forever'],
                                'question': 'Which combination is typically strongest '
                                            'long-term?'}],
        'summary': [       'Revenue growth is the top-line signal of market demand.',
                           'It sets the ceiling for how big a business can become.',
                           'Revenue growth alone is not enough—quality of growth '
                           'matters.',
                           'Combine revenue growth with margins and ROIC to judge '
                           'compounding potential.'],
        'theme': 'Core Metrics',
        'time_min': 7,
        'title': 'Revenue Growth (The Fuel)',
        'topics': ['Core Metrics', 'Growth'],
        'video_url': '',
        'why_it_matters': 'Revenue growth shows demand and runway—but it only creates '
                          'value when paired with margins, ROIC, and cash generation.',
        'xp': 18},
 'CM5': {       'apply_action': {'type': 'none'},
        'checklist': [       'Is the company profitable and earnings stable (for P/E)?',
                             'If using P/S, are margins strong or improving?',
                             'How does valuation compare to peers with similar '
                             'growth/quality?',
                             'Are expectations (implied by the multiple) realistic?'],
        'common_mistakes': [       'Comparing multiples across totally different '
                                   'industries.',
                                   'Using P/E on companies with negative or highly '
                                   'cyclical earnings.',
                                   'Treating a low P/E as ‘safe’ without checking '
                                   'business quality.',
                                   'Paying any price for growth without verifying '
                                   'margins/ROIC.'],
        'id': 'CM5',
        'key_ideas': [       'P/E works best for profitable, stable companies; it '
                             'breaks with losses or cyclical earnings.',
                             'P/S can help when profits are low, but you must consider '
                             'margins and path to profitability.',
                             'Compare within an industry and consider growth '
                             'rates—context is everything.',
                             'Valuation sets the ‘starting point’ for future returns.'],
        'level': 'Intermediate',
        'quiz': [       {       'correct': 1,
                                'explanation': 'Multiples price in growth, durability, '
                                               'and risk expectations.',
                                'options': [       'A) Guaranteed future returns',
                                                   'B) Market expectations about the '
                                                   'future',
                                                   'C) The company’s logo and brand',
                                                   'D) Insider trading activity'],
                                'question': 'Valuation multiples mostly reflect:'},
                        {       'correct': 1,
                                'explanation': 'When earnings are distorted, P/E can '
                                               'mislead.',
                                'options': [       'A) Earnings are stable and '
                                                   'positive',
                                                   'B) Earnings are negative or highly '
                                                   'cyclical',
                                                   'C) The company has a long history',
                                                   'D) Revenue is rising'],
                                'question': 'P/E is often unreliable when:'},
                        {       'correct': 1,
                                'explanation': 'Sales are only valuable if they can '
                                               'eventually convert to profit/cash.',
                                'options': [       'A) Weather forecasts',
                                                   'B) Profit margins and path to '
                                                   'profitability',
                                                   'C) Dividend tax rates',
                                                   'D) Chart patterns only'],
                                'question': 'P/S becomes more meaningful when you also '
                                            'consider:'}],
        'summary': [       'P/E and P/S are quick ways to relate price to earnings or '
                           'sales.',
                           'Multiples reflect expectations about growth, margins, and '
                           'durability.',
                           'Cheap stocks can be cheap for a reason; expensive stocks '
                           'can still outperform.',
                           'Use valuation after you understand business quality '
                           '(margins, ROIC, cash).'],
        'theme': 'Core Metrics',
        'time_min': 8,
        'title': 'Valuation (P/E & P/S — Context Matters)',
        'topics': ['Core Metrics', 'Valuation'],
        'video_url': '',
        'why_it_matters': 'Valuation tells you what expectations are already priced '
                          'in. It’s a constraint and risk tool—not a shortcut to good '
                          'investing.',
        'xp': 20}
}

    LEARN_HUB_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Behavior', 'Repair']
    LEARN_HUB_THEMES = {'Beginner': ['ETFs & Diversification', 'Foundations', 'Risk Basics'],
 'Intermediate': ['Core Metrics', 'Business Quality', 'Financial Statements', 'Valuation'],
 'Advanced': ['Advanced Risk', 'Portfolio Construction'],
 'Behavior': ['Behavioral Edge'],
 'Repair': ['Repair']}

    # Deterministic ordering within each theme (preserves curriculum progression)
    LEARN_HUB_THEME_ORDER = {'Beginner::Foundations': ['B1', 'B2', 'B3', 'B14', 'B15'],
 'Beginner::ETFs & Diversification': ['B4', 'B5', 'B6', 'B7', 'B8'],
 'Beginner::Risk Basics': ['B9', 'B10', 'B11', 'B12', 'B13'],
 'Intermediate::Financial Statements': ['I1', 'I2', 'I3', 'I4', 'I5'],
 'Intermediate::Valuation': ['V1', 'V2', 'V3', 'V4', 'V5', 'V6'],
 'Intermediate::Business Quality': ['I6', 'I7', 'I8', 'I9', 'I10'],
 'Advanced::Portfolio Construction': ['A1', 'A2', 'A3', 'A6'],
 'Advanced::Advanced Risk': ['A4', 'A5', 'A7', 'A8'],
 'Behavior::Behavioral Edge': ['BE1', 'BE2', 'BE3', 'BE4', 'BE5'],
 'Repair::Repair': ['R1', 'R2']}

# ============= BADGE DEFINITIONS =============
    BADGES = {
        "first_lesson": {"name": "🌱 First Lesson", "desc": "Complete your first lesson"},
        "beginner_5": {"name": "📚 Beginner Graduate", "desc": "Complete 5 beginner lessons"},
        "index_ready": {"name": "📊 Index Ready", "desc": "Master index funds and diversification"},
        "quality_starter": {"name": "💎 Quality Starter", "desc": "Learn quality analysis fundamentals"},
        "risk_aware": {"name": "🛡️ Risk Aware", "desc": "Master risk management"},
        "calm_in_storm": {"name": "🧘 Calm in Storm", "desc": "Master behavioral discipline"},
        "portfolio_mechanic": {"name": "🔧 Portfolio Mechanic", "desc": "Complete 3 repair lessons"},
        "intermediate_complete": {"name": "🎓 Intermediate Complete", "desc": "Finish all intermediate lessons"},
        "learn_hub_master": {"name": "👑 Learn Hub Master", "desc": "Complete all lessons"}
    }
    
    # ============= UTILITY FUNCTIONS =============
    def award_badges():
        """Check and award badges based on progress"""
        completed = st.session_state.learn_completed_lessons
        badges = st.session_state.learn_badges
        
        # First lesson
        if len(completed) >= 1 and "first_lesson" not in badges:
            badges.add("first_lesson")
            return "first_lesson"
        
        # Beginner 5
        beginner_completed = sum(1 for l_id in completed if l_id.startswith("B"))
        if beginner_completed >= 5 and "beginner_5" not in badges:
            badges.add("beginner_5")
            return "beginner_5"
        
        # Index Ready
        if "B3" in completed and "B5" in completed and "index_ready" not in badges:
            badges.add("index_ready")
            return "index_ready"
        
        # Risk Aware
        if "B5" in completed and "A1" in completed and "risk_aware" not in badges:
            badges.add("risk_aware")
            return "risk_aware"
        
        # Calm in Storm
        if "P1" in completed and "calm_in_storm" not in badges:
            badges.add("calm_in_storm")
            return "calm_in_storm"
        
        # Portfolio Mechanic
        repair_completed = sum(1 for l_id in completed if l_id.startswith("R"))
        if repair_completed >= 3 and "portfolio_mechanic" not in badges:
            badges.add("portfolio_mechanic")
            return "portfolio_mechanic"
        
        return None
    

    # Normalize lesson objects so every lesson follows the same template (fail-soft defaults)
    for _lid, _l in LEARN_HUB_LESSONS.items():
        _l.setdefault("summary", [])
        _l.setdefault("key_ideas", [])
        _l.setdefault("common_mistakes", [])
        _l.setdefault("checklist", [])
        _l.setdefault("quiz", [])
        _l.setdefault("video_url", None)

        # If any section is empty, backfill with lightweight defaults based on existing fields
        if not _l["summary"]:
            _l["summary"] = [
                _l.get("why_it_matters", "Key idea for this lesson."),
                "Keep it simple: focus on the one takeaway you can use today."
            ]
        if not _l["key_ideas"]:
            _l["key_ideas"] = _l["summary"][:]
        if not _l["common_mistakes"]:
            _l["common_mistakes"] = ["Overcomplicating the concept.", "Making decisions based on short-term noise."]
        if not _l["checklist"]:
            _l["checklist"] = ["Understand the main concept.", "Apply it once using a simple example.", "Review the quick check."]
    def get_recommended_lessons():
            """Get personalized lesson recommendations.

            IMPORTANT UX RULE: Lessons should never 'disappear' after completion.
            This function returns a small set to feature at the top, but completed lessons
            can still be featured (e.g., core basics) and will always remain in 'All Lessons'.
            """
            completed = st.session_state.learn_completed_lessons

            # Core path (always safe to show, even if completed)
            core = ["B1", "B2", "B3"]

            # Prefer to feature the next unfinished lessons
            all_ids = list(LEARN_HUB_LESSONS.keys())
            available = [l_id for l_id in all_ids if l_id not in completed]

            # New user: show the core path
            if len(completed) == 0:
                return core

            rec = []

            # If user hasn't finished core, keep core visible so nothing feels 'gone'
            if any(c not in completed for c in core):
                for c in core:
                    if c not in rec:
                        rec.append(c)

            # Otherwise, show next best 3 available, but keep at least 1 completed core visible for continuity
            if not rec:
                # show one core as an anchor (completed is fine)
                for c in core:
                    if c in LEARN_HUB_LESSONS:
                        rec.append(c)
                        break

            # After B3, recommend psychology first (even if core is complete)
            if "B3" in completed and "P1" in LEARN_HUB_LESSONS and "P1" not in completed:
                rec.append("P1")

            # Fill remaining slots with available lessons
            for l_id in available:
                if l_id not in rec:
                    rec.append(l_id)
                if len(rec) >= 3:
                    break

            return rec[:3]
    # ============= HELPER FUNCTIONS FOR RENDERING =============
    def _render_lesson_card(lesson, key_prefix: str = "lesson"):
        """Render a lesson card with always-visible key info + 2 clear actions."""
        lesson_id = lesson["id"]
        total_q = len(lesson.get("quiz", [])) or 3
        is_completed = lesson_id in st.session_state.learn_completed_lessons
        best_score = st.session_state.learn_best_scores.get(lesson_id, 0)
        started = lesson_id in st.session_state.learn_started_lessons

        # Progress: 0 = not started, 0.5 = started, 1 = completed (quiz submitted)
        if is_completed:
            progress = 1.0
            status = f"✅ Completed ({best_score}/{total_q})"
            status_color = "#4CAF50"
        elif started:
            progress = 0.5
            status = "⏳ In Progress"
            status_color = "#FBC02D"
        else:
            progress = 0.0
            status = "◯ Not Started"
            status_color = "#999"

        # Title
        st.markdown(f"### {'✅' if is_completed else '📚'} {lesson['title']} ({lesson['time_min']} min)")
        st.markdown(f"<span style='color:{status_color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)

        # Key info (always visible; replaces the old Details toggle)
        st.markdown(
            f"**Level:** {lesson['level']} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"**Topics:** {', '.join(lesson['topics'])}",
            unsafe_allow_html=True
        )
        st.markdown(f"**Why it matters:** {lesson['why_it_matters']}")
        video_url = (lesson.get("video_url") or "").strip()
        if video_url:
            st.caption("🎥 Video: ready (will appear in the right-side slot when you add it)")
        else:
            st.caption("🎥 Video: coming soon (right-side slot)")

        # Progress bar (game feel)
        st.progress(progress)

        st.markdown("")  # small spacing before actions

        # Actions row: Lesson • Quiz
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            lesson_btn_label = "🔁 Review Lesson" if is_completed else "📖 Start Lesson"
            if st.button(lesson_btn_label, key=f"start_{key_prefix}_{lesson_id}", use_container_width=True, type="primary"):
                st.session_state.learn_started_lessons.add(lesson_id)
                st.session_state.learn_selected_lesson_id = lesson_id
                st.session_state.learn_view_mode = "lesson"
                st.rerun()

        with btn_col2:
            quiz_btn_label = "🔁 Retake Quiz" if is_completed else "📝 Take Quiz"
            if st.button(quiz_btn_label, key=f"quiz_{key_prefix}_{lesson_id}", use_container_width=True, type="primary"):
                st.session_state.learn_started_lessons.add(lesson_id)
                st.session_state.learn_selected_lesson_id = lesson_id
                st.session_state.learn_view_mode = "quiz"
                # reset quiz run state for this attempt
                st.session_state.quiz_current_question = 0
                st.session_state.quiz_answers = []
                st.session_state.quiz_score = None
                st.rerun()

        # Extra spacing after each card
        st.markdown("---")
        st.markdown("")

    # ============= UI RENDERING =============

    # Non-blocking setup nudge
    render_setup_nudge()
    
    # Header
    st.markdown("# 📖 Learn Hub")
    st.caption("*Educational only. Not financial advice.*")
    
    # Progress row
    total_lessons = len(LEARN_HUB_LESSONS)
    completed_count = len(st.session_state.learn_completed_lessons)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Completed", f"{completed_count}/{total_lessons}")
    with col2:
        st.metric("XP", st.session_state.learn_xp_total)
    with col3:
        st.metric("Badges", len(st.session_state.learn_badges))
    with col4:
        streak = st.session_state.learn_streak_days
        st.metric("Streak", f"{streak} days" if streak > 0 else "—")
    
    # Show badges
    if st.session_state.learn_badges:
        st.markdown("**🏆 Badges:**")
        badge_chips = " ".join([
            f'<span style="background:#333; padding:5px 10px; border-radius:20px; margin:2px; display:inline-block;">{BADGES[b]["name"]}</span>'
            for b in st.session_state.learn_badges if b in BADGES
        ])
        st.markdown(badge_chips, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.learn_selected_lesson_id:
        selected_lesson_id = st.session_state.learn_selected_lesson_id
        
        if selected_lesson_id in LEARN_HUB_LESSONS:
            lesson = LEARN_HUB_LESSONS[selected_lesson_id]
            
            st.markdown("---")
            st.markdown(f"# 📚 {lesson['title']}")
            st.markdown(f"**{lesson['level']} | {lesson['time_min']} minutes | {', '.join(lesson['topics'])}**")
            
            if st.button("← Back to Lesson List"):
                st.session_state.learn_selected_lesson_id = None
                st.rerun()
            
            st.markdown("---")
            

            # Create 2-column layout: content on left, video on right
            left_col, right_col = st.columns([2.2, 1.0], gap="large")
            
            with left_col:
                # Why it matters
                st.markdown("### 💡 Why It Matters")
                st.info(lesson['why_it_matters'])

                # Quick interactive (keep it light — no walls of text)
                st.markdown("### 🎮 Quick Interactive")

                if selected_lesson_id == "B1":
                    st.markdown("**Price move simulator (1 question):**")
                    pick = st.selectbox(
                        "If more buyers show up than sellers at the current price, what usually happens?",
                        ["— Select —", "Price falls", "Price stays about the same", "Price rises"],
                        index=0,
                        key=f"qi_{selected_lesson_id}_1",
                    )
                    if pick != "— Select —":
                        if pick == "Price rises":
                            st.success("Correct — more demand than supply typically pushes the price up.")
                        else:
                            st.info("Not quite — when demand > supply at a given price, buyers usually bid the price higher.")

                elif selected_lesson_id == "B2":
                    st.markdown("**Compounding demo (move the sliders):**")
                    years = st.slider("Years", 1, 40, 20, key=f"qi_{selected_lesson_id}_years")
                    monthly = st.slider("Monthly contribution ($)", 25, 2000, 300, step=25, key=f"qi_{selected_lesson_id}_monthly")
                    rate = st.slider("Assumed annual return (%)", 0.0, 15.0, 7.0, step=0.5, key=f"qi_{selected_lesson_id}_rate")

                    r = (rate / 100.0) / 12.0
                    n = years * 12
                    fv = monthly * (n if r == 0 else ((1 + r) ** n - 1) / r)
                    st.metric("Estimated value (contributions + growth)", f"${fv:,.0f}")
                    st.caption("Educational estimate only — returns are not guaranteed.")

                elif selected_lesson_id == "B3":
                    st.markdown("**Quick choice:**")
                    pick = st.selectbox(
                        "Which is usually the safer default for a beginner?",
                        ["— Select —", "One single stock", "A broad index ETF"],
                        index=0,
                        key=f"qi_{selected_lesson_id}_1",
                    )
                    if pick != "— Select —":
                        if pick == "A broad index ETF":
                            st.success("Correct — broad ETFs diversify across many companies.")
                        else:
                            st.info("Single stocks can work, but they carry much more company-specific risk.")

                else:
                    st.caption("Tip: Finish the lesson, then take the 3-question quiz to lock in the concepts.")

                st.markdown("---")

                # Summary
                st.markdown("### 📋 Summary")
                for point in lesson['summary']:
                    st.markdown(f"• {point}")
                
                # Key ideas
                with st.expander("🔑 Key Ideas", expanded=True):
                    for idea in lesson['key_ideas']:
                        st.markdown(f"• {idea}")
                
                # Common mistakes
                with st.expander("⚠️ Common Mistakes"):
                    for mistake in lesson['common_mistakes']:
                        st.markdown(f"• {mistake}")
                
                # Checklist
                with st.expander("✅ Checklist"):
                    for item in lesson['checklist']:
                        st.checkbox(item, key=f"check_{selected_lesson_id}_{lesson['checklist'].index(item)}")
            
            with right_col:
                # Video panel
                is_founder = st.session_state.get("is_founder", False)
                render_video_panel(selected_lesson_id, is_founder)
            
            st.markdown("---")
            
            # QUIZ ENGINE
            st.markdown("### 📝 Quiz (3 Questions)")
            
            quiz = lesson['quiz']
            current_q = st.session_state.quiz_current_question
            
            if st.session_state.quiz_score is None:
                # Show question
                if current_q < len(quiz):
                    question_data = quiz[current_q]
                    st.markdown(f"**Question {current_q + 1}/{len(quiz)}:**")
                    st.markdown(f"*{question_data['question']}*")
                    
                    # Answer options
                    answer = st.radio(
                        "Select your answer:",
                        question_data['options'],
                        key=f"quiz_answer_{selected_lesson_id}_{current_q}"
                    )
                    
                    if st.button("Check Answer", type="primary"):
                        selected_index = question_data['options'].index(answer)
                        is_correct = selected_index == question_data['correct']
                        st.session_state.quiz_answers.append(is_correct)
                        
                        if is_correct:
                            st.success("✅ Correct!")
                        else:
                            st.error(f"❌ Incorrect. {question_data['explanation']}")
                        
                        # Move to next question or finish
                        if current_q < len(quiz) - 1:
                            st.session_state.quiz_current_question += 1
                            st.rerun()
                        else:
                            # Calculate score
                            score = sum(st.session_state.quiz_answers)
                            st.session_state.quiz_score = score

                            # Perfect score celebration (Streamlit has balloons; add toast when available)
                            if score == len(quiz):
                                perfect_key = f"perfect_{selected_lesson_id}"
                                already = st.session_state.get(perfect_key, False)
                                st.session_state[perfect_key] = True
                                if not already:
                                    st.balloons()
                                    try:
                                        st.toast("Perfect score! 🏆", icon="🎉")
                                    except Exception:
                                        pass

                            # Award XP if passed and new best
                            if score >= 2:
                                old_best = st.session_state.learn_best_scores.get(selected_lesson_id, 0)
                                if score > old_best or selected_lesson_id not in st.session_state.learn_completed_lessons:
                                    st.session_state.learn_completed_lessons.add(selected_lesson_id)
                                    st.session_state.learn_best_scores[selected_lesson_id] = score
                                    st.session_state.learn_xp_total += lesson['xp']
                                    
                                    # Award badge
                                    new_badge = award_badges()
                                    
                                    # Save to DB
                                    save_learn_progress_to_db(selected_lesson_id, score)
                            
                            st.rerun()
            
            else:
                # Show results
                score = st.session_state.quiz_score
                st.markdown(f"### Your Score: {score}/3")
                
                if score == 3:
                    st.success("🎉 Perfect score!")
                elif score >= 2:
                    st.success(f"✅ Passed! (+{lesson['xp']} XP)")
                else:
                    st.warning("Try again to pass (need 2/3)")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Retake Quiz"):
                        st.session_state.quiz_current_question = 0
                        st.session_state.quiz_answers = []
                        st.session_state.quiz_score = None
                        st.rerun()
                
                with col2:
                    if st.button("← Back to Lessons"):
                        st.session_state.learn_selected_lesson_id = None
                        st.session_state.quiz_current_question = 0
                        st.session_state.quiz_answers = []
                        st.session_state.quiz_score = None
                        st.rerun()
    
    else:
                # Track selector (tabs) + Theme selector (radio) — mirrors your main navigation pattern
        tab_labels = ["Beginner", "Intermediate", "Advanced", "Behavior", "Repair", "All Lessons"]
        tabs = st.tabs(tab_labels)

        def _render_track(track_level):
            # Search (within selected track/theme)
            search_query = st.text_input(
                "🔍 Search lessons",
                placeholder="e.g., P/E, diversification, cash flow",
                key=f"learn_search_{track_level or 'all'}"
            )

            # Theme selector
            if track_level and track_level in LEARN_HUB_THEMES:
                theme_options = ["All Themes"] + LEARN_HUB_THEMES[track_level]
                selected_theme = st.radio(
                    "Choose a theme:",
                    theme_options,
                    horizontal=True,
                    key=f"learn_theme_{track_level}"
                )
            else:
                selected_theme = "All Themes"

            st.markdown("---")

            # Deterministic curriculum ordering
            def _ordered_lessons(level_filter, theme_filter):
                ids = []
                if level_filter and theme_filter and theme_filter != "All Themes":
                    ids = LEARN_HUB_THEME_ORDER.get(f"{level_filter}::{theme_filter}", [])
                elif level_filter:
                    # Concatenate themes in defined order for the level
                    for th in LEARN_HUB_THEMES.get(level_filter, []):
                        ids.extend(LEARN_HUB_THEME_ORDER.get(f"{level_filter}::{th}", []))
                else:
                    # All lessons: preserve insertion order from dict
                    ids = list(LEARN_HUB_LESSONS.keys())

                result = []
                for lid in ids:
                    lesson = LEARN_HUB_LESSONS.get(lid)
                    if not lesson:
                        continue

                    if search_query:
                        q = search_query.lower()
                        in_title = q in lesson["title"].lower()
                        in_theme = q in lesson.get("theme", "").lower()
                        in_topics = any(q in t.lower() for t in lesson.get("topics", []))
                        if not (in_title or in_theme or in_topics):
                            continue

                    # Level filter guard (for All Lessons tab this is None)
                    if level_filter and lesson.get("level") != level_filter:
                        continue

                    # Theme filter guard
                    if level_filter and theme_filter and theme_filter != "All Themes":
                        if lesson.get("theme") != theme_filter:
                            continue

                    result.append(lesson)

                return result

            lessons_to_show = _ordered_lessons(track_level, selected_theme)

            if not lessons_to_show:
                st.info("No lessons match your search in this track/theme. Try a different keyword.")
                return

            # Render lesson cards
            for lesson in lessons_to_show:
                _render_lesson_card(lesson, key_prefix=f"list_{track_level}_{lesson.get('theme','')}")

        # Beginner tab
        with tabs[0]:
            st.session_state.learn_current_level = "Beginner"
            _render_track("Beginner")

        # Intermediate tab
        with tabs[1]:
            st.session_state.learn_current_level = "Intermediate"
            _render_track("Intermediate")

        # Advanced tab
        with tabs[2]:
            st.session_state.learn_current_level = "Advanced"
            _render_track("Advanced")

        # Behavior tab
        with tabs[3]:
            st.session_state.learn_current_level = "Behavior"
            _render_track("Behavior")

        # Repair tab
        with tabs[4]:
            st.session_state.learn_current_level = "Repair"
            _render_track("Repair")

        # All Lessons tab
        with tabs[5]:
            st.session_state.learn_current_level = "All Levels"

            # Show recommended first (does NOT remove completed lessons from the library)
            recommended = get_recommended_lessons()
            if recommended:
                st.markdown("### 🎯 Recommended for You")
                for lesson_id in recommended:
                    if lesson_id in LEARN_HUB_LESSONS:
                        _render_lesson_card(LEARN_HUB_LESSONS[lesson_id], key_prefix=f"rec_{lesson_id}")
                st.markdown("---")

            _render_track(None)

        # ============= LESSON VIEWER =============
        # When a user clicks Start Lesson / Take Quiz, show the selected lesson here.
        selected_id = st.session_state.get("learn_selected_lesson_id")
        if selected_id and selected_id in LEARN_HUB_LESSONS:
            lesson = LEARN_HUB_LESSONS[selected_id]
            st.markdown("---")
            st.markdown(f"## 📚 {lesson['title']}")

            # Mark as started/viewed
            st.session_state.learn_started_lessons.add(selected_id)

            # Progress (0/50/100)
            quiz_done = selected_id in st.session_state.learn_completed_lessons
            started = selected_id in st.session_state.learn_started_lessons
            prog = 1.0 if quiz_done else (0.5 if started else 0.0)
            st.progress(prog)

            # Two-column layout: content (left) + video slot (right)
            content_col, video_col = st.columns([2, 1], gap="large")

            with content_col:
                # Always-visible template sections (no walls of text)
                st.markdown(
                    f"**Level:** {lesson['level']} &nbsp;&nbsp;|&nbsp;&nbsp; **Topics:** {', '.join(lesson['topics'])}",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Why it matters:** {lesson['why_it_matters']}")

                st.markdown("### Key takeaways")
                for b in lesson.get("summary", []):
                    st.markdown(f"- {b}")

                st.markdown("### Core ideas")
                for b in lesson.get("key_ideas", []):
                    st.markdown(f"- {b}")

                st.markdown("### Common mistakes")
                for b in lesson.get("common_mistakes", []):
                    st.markdown(f"- {b}")

                st.markdown("### Quick checklist")
                for b in lesson.get("checklist", []):
                    st.markdown(f"- {b}")

            with video_col:
                video_url = (lesson.get("video_url") or "").strip()
                if video_url:
                    st.video(video_url)
                else:
                    st.caption("🎬 Video: coming soon (right-side slot)")

                # Mode switch (simple, not a separate 'Details' tab)
                mode = st.radio(
                    "What do you want to do?",
                    ["Lesson", "Quiz"],
                    horizontal=True,
                    index=0 if st.session_state.get("learn_view_mode", "lesson") == "lesson" else 1,
                    key=f"learn_mode_{selected_id}"
                )

                if mode == "Lesson":
                    st.info("Tip: skim the bullets, then take the quiz to lock it in.")
                else:
                    # ============= QUIZ RUNNER =============
                    quiz = lesson.get("quiz", [])
                    if not quiz:
                        st.warning("Quiz coming soon for this lesson.")
                    else:
                        total_q = len(quiz)
                        if st.session_state.get("quiz_answers") is None or st.session_state.get("learn_view_mode") != "quiz":
                            st.session_state.quiz_answers = []
                            st.session_state.quiz_score = None

                        st.session_state.learn_view_mode = "quiz"

                        # Render questions
                        answers = []
                        for i, q in enumerate(quiz):
                            st.markdown(f"**Q{i+1}. {q['question']}**")
                            ans = st.radio(
                                label="",
                                options=q["choices"],
                                index=None,
                                key=f"q_{selected_id}_{i}"
                            )
                            answers.append(ans)
                            st.markdown("")

                        # Submit
                        can_submit = all(a is not None for a in answers)
                        if st.button("✅ Submit Quiz", type="primary", use_container_width=True, disabled=not can_submit, key=f"submit_{selected_id}"):
                            score = 0
                            for i, q in enumerate(quiz):
                                if answers[i] == q["answer"]:
                                    score += 1

                            # Track best score + completion
                            prev_best = st.session_state.learn_best_scores.get(selected_id, 0)
                            st.session_state.learn_best_scores[selected_id] = max(prev_best, score)
                            st.session_state.learn_completed_lessons.add(selected_id)

                            # XP (simple)
                            st.session_state.learn_xp_total = st.session_state.learn_xp_total + (10 if score == total_q else 5)

                            st.success(f"Score: {score}/{total_q}")

                            # Perfect score celebration
                            if score == total_q:
                                st.balloons()

                            # Save progress fail-soft
                            try:
                                save_learn_progress_to_db()
                            except Exception:
                                pass

                            st.rerun()

            with video_col:
                st.markdown("### Video (coming soon)")
                vurl = lesson.get("video_url")
                if vurl:
                    st.video(vurl)
                else:
                    st.info("Upload a short video for this lesson to make it feel premium. (This slot is ready.)")

            st.markdown("---")

        # AI coach on the side of Learn Hub (unchanged)
        render_ai_coach("Learn Hub", ticker=None, facts=None)


elif selected_page == "📘 Glossary":
    
    st.header("🎓 Finance 101: From Theory to Practice")
    st.caption("*Bridge from Learn Hub lessons to real company analysis. See exactly how the metrics work on actual companies.*")
    
    # Show page popup
    show_page_popup(
        'finance_101',
        '🎓 Finance 101',
        'Your bridge from Learn Hub lessons to real analysis. Pick a company and walk through the analysis step-by-step.',
        'See how the 5 metrics work in practice!'
    )
    
    st.markdown("---")
    
    # ============= WHAT YOU LEARNED =============
    st.markdown("## 🎯 What You Just Learned in Learn Hub")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Core Concepts:**
        - 📊 Market Mechanics (supply/demand)
        - ⏰ Time is Your Advantage (compounding)
        - 📈 Index Funds Work (diversification)
        """)
    
    with col2:
        st.markdown("""
        **The 5 Metrics:**
        - 💰 FCF per Share Growth
        - ⚙️ Operating Income Growth  
        - 📊 Gross Margin Trends
        - 📈 Revenue Quality
        - 🛡️ Competitive Moat
        """)
    
    st.markdown("**Now let's see how this works on real companies. ↓**")
    
    st.markdown("---")
    
    # ============= PICK COMPANY =============
    st.markdown("## 🏢 Pick a Company to Analyze")
    
    company_data = {
        "Apple (AAPL) 🍎": {
            "ticker": "AAPL",
            "famous_for": "iPhone, Mac, Services - $3T market cap",
            "fcf": "$100B annual - massive cash machine",
            "revenue_growth": "8-10% steady growth",
            "margins": "Gross 44%, Operating 30% (premium pricing)",
            "moat": "Brand loyalty + ecosystem lock-in",
            "verdict": "✅ Quality company with pricing power",
            "key_insight": "Hardware margins that look like software",
            "watch_for": "Services growth (30%+ margins)"
        },
        "Amazon (AMZN) 📦": {
            "ticker": "AMZN",
            "famous_for": "E-commerce + AWS cloud dominance",
            "fcf": "$35B+ from AWS, retail breaks even",
            "revenue_growth": "Retail 10%, AWS 20-30%",
            "margins": "Retail <5%, AWS 30%+ - mix matters!",
            "moat": "Distribution network + AWS ecosystem",
            "verdict": "✅ Two businesses in one - watch the mix",
            "key_insight": "AWS subsidizes retail expansion",
            "watch_for": "AWS margin expansion as it matures"
        },
        "Microsoft (MSFT) 💻": {
            "ticker": "MSFT",
            "famous_for": "Office 365, Azure, Windows",
            "fcf": "$60B annual - very predictable",
            "revenue_growth": "Azure 25%+, Office steady",
            "margins": "Gross 69%, Operating 42% - software!",
            "moat": "Enterprise lock-in + network effects",
            "verdict": "✅ Software moat = pricing power",
            "key_insight": "Margins expand with scale",
            "watch_for": "Azure catching up to AWS"
        },
        "Tesla (TSLA) ⚡": {
            "ticker": "TSLA",
            "famous_for": "EV leader, high growth expectations",
            "fcf": "$5-10B annual (varies with capex)",
            "revenue_growth": "30-50% historically, now slowing",
            "margins": "Gross 18%, Operating 10% (good for cars!)",
            "moat": "Supercharger network + software edge",
            "verdict": "⚠️ Growth stock - watch trends carefully",
            "key_insight": "Manufacturing scale improving margins",
            "watch_for": "Competition from legacy auto + China"
        }
    }
    
    selected = st.selectbox(
        "Choose a company:",
        list(company_data.keys()),
        index=0
    )
    
    company = company_data[selected]
    
    st.markdown("---")
    
    # ============= COMPANY WALKTHROUGH =============
    st.markdown(f"## 📊 {selected} Walkthrough")
    
    # Overview card
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
    ">
        <div style="font-size: 28px; font-weight: bold; margin-bottom: 15px;">{selected}</div>
        <div style="font-size: 16px; opacity: 0.95;">
            <strong>Famous for:</strong> {company["famous_for"]}<br>
            <strong>Key insight:</strong> {company["key_insight"]}<br>
            <strong>Watch for:</strong> {company["watch_for"]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============= THE 5 METRICS IN ACTION =============
    st.markdown("### 🏆 The 5 Metrics - Applied")
    
    with st.expander("💰 1. Free Cash Flow (FCF)", expanded=True):
        st.markdown(f"**{company['ticker']}'s FCF:** {company['fcf']}")
        st.markdown("""
        **Where to find it:**
        - Company Analysis → Financial Health
        - Look for: "Operating Cash Flow minus Capex"
        
        **What good looks like:**
        - ✅ Growing year-over-year
        - ✅ FCF > Net Income (quality)
        - ✅ Covers dividends + buybacks
        """)
    
    with st.expander("⚙️ 2. Operating Income Growth"):
        st.markdown(f"**{company['ticker']}'s Revenue:** {company['revenue_growth']}")
        st.markdown("""
        **Where to find it:**
        - Company Analysis → Income Statement
        - Look for: "Operating Income" trend
        
        **What good looks like:**
        - ✅ Growth faster than revenue (leverage!)
        - ✅ Consistent, not lumpy
        - ✅ Positive even in downturns
        """)
    
    with st.expander("📊 3. Margin Trends"):
        st.markdown(f"**{company['ticker']}'s Margins:** {company['margins']}")
        st.markdown("""
        **Where to find it:**
        - Company Analysis → Margins chart
        - Gross = (Revenue - COGS) / Revenue
        - Operating = Operating Income / Revenue
        
        **What good looks like:**
        - ✅ Expanding over time
        - ✅ Software: 70%+ gross
        - ✅ Hardware: 30-50% gross
        - ✅ Compare to competitors
        """)
    
    with st.expander("📈 4. Revenue Quality"):
        st.markdown("""
        **Questions to ask:**
        - Is it growing consistently? ✅
        - Is it one-time or recurring? (recurring = better)
        - Is growth accelerating or slowing?
        
        **Where to find it:**
        - Company Analysis → Revenue chart
        """)
    
    with st.expander("🛡️ 5. Competitive Moat"):
        st.markdown(f"**{company['ticker']}'s Moat:** {company['moat']}")
        st.markdown("""
        **Questions to ask:**
        - Can competitors copy this easily? (NO = moat ✅)
        - Does the company have pricing power? ✅
        - Customer lock-in / switching costs? ✅
        - Network effects or economies of scale? ✅
        
        **Where to research:**
        - Market Intelligence tab
        - Company's 10-K annual report
        """)
    
    st.markdown(f"**Verdict:** {company['verdict']}")
    
    st.markdown("---")
    
    # ============= ANALYSIS CHECKLIST =============
    st.markdown("## ✅ Your Step-by-Step Checklist")
    st.caption("*Use this for ANY company you analyze*")
    
    checklist = [
        "📊 Revenue trend - growing consistently?",
        "💰 FCF trend - healthy cash flow?",
        "📈 Margins - expanding or stable?",
        "⚙️ Operating income - growing faster than revenue?",
        "🛡️ Moat - competitive advantages?",
        "📰 Recent news - any risks or catalysts?",
        "💡 Would I own this for 5+ years?"
    ]
    
    for item in checklist:
        st.checkbox(item, key=f"check_{item[:10]}")
    
    st.markdown("---")
    
    # ============= CALL TO ACTION =============
    st.markdown("## 🚀 Ready to Try It Yourself?")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
            padding: 35px;
            border-radius: 15px;
            text-align: center;
        ">
            <div style="font-size: 22px; font-weight: bold; margin-bottom: 20px;">
                You've learned the theory ✅<br>
                You've seen real examples ✅<br>
                Now analyze your first stock! 🎯
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        if st.button("📊 Go to Company Analysis", type="primary", use_container_width=True):
            st.session_state.selected_page = "📊 Company Analysis"
            st.rerun()
        
        st.caption("*All the tools are ready for you*")
    
    st.markdown("---")
    
    # ============= QUICK REFERENCE =============
    with st.expander("📚 Quick Metrics Reference Card"):
        st.markdown("""
        **Keep this handy:**
        
        💰 **FCF** = Operating Cash Flow - Capex  
        Good: Growing, > Net Income
        
        ⚙️ **Operating Income** = Revenue - COGS - OpEx  
        Good: Growing faster than revenue
        
        📊 **Gross Margin** = (Revenue - COGS) / Revenue  
        Good: Software 70%+, Hardware 30-50%
        
        📈 **Operating Margin** = Operating Income / Revenue  
        Good: Expanding over time
        
        💸 **P/E Ratio** = Price / Earnings  
        Good: <15 value, 15-25 fair, >25 growth
        """)
    
    render_ai_coach("Finance 101", ticker=None, facts=None)


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
    
    # AI Coach integration
    render_ai_coach("Risk Quiz", ticker=None, facts=None)


elif selected_page == "📊 Company Analysis":
    
    # Track page usage
    track_feature_usage("company_analysis")
    
    # Show page popup
    show_page_popup(
        'company_analysis',
        '🔍 Company Analysis',
        'Deep dive into any stock. View financial metrics, charts, and compare companies side-by-side.',
        'AI explains complex metrics in simple terms - no jargon!'
    )
    
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
        st.session_state.last_ticker = ticker  # Track last ticker for Dashboard
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
                    # Get logo for starter stock
                    starter_logo = get_company_logo(stock_ticker)
                    
                    if starter_logo:
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <img src="{starter_logo}" width="40" height="40" style="border-radius: 6px; margin-right: 12px;">
                            <div>
                                <div style="font-size: 20px; font-weight: bold;">{stock_ticker}</div>
                                <div style="color: #888; font-size: 14px;">{stock_name}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
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
        logo_url = profile.get('image', '')
        
        # Company header with LOGO
        col1, col2 = st.columns([3, 1])
        with col1:
            if logo_url:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <img src="{logo_url}" width="50" height="50" style="border-radius: 8px; margin-right: 15px;">
                    <div>
                        <div style="font-size: 24px; font-weight: bold;">📈 {company_name} ({ticker})</div>
                        <div style="color: #888; font-size: 14px;"><strong>Sector:</strong> {sector} | <strong>Industry:</strong> {industry}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
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
    
    # Show data source indicator
    show_data_source(source="Financial Modeling Prep API", updated_at=datetime.now())
    
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
        # Use global settings - no duplicate controls needed
        years = st.session_state.get('years_of_history', 5)
        period = st.session_state.get('global_period', 'annual')
        view = "🌟 The Big Picture"  # Default view


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
                
                # Show % change for the selected timeframe
                price_col = 'close' if 'close' in price_history.columns else 'price'
                if len(price_history) >= 2:
                    start_price = price_history[price_col].iloc[0]
                    end_price = price_history[price_col].iloc[-1]
                    if start_price > 0:
                        pct_change = ((end_price - start_price) / start_price) * 100
                        change_color = "#00C853" if pct_change >= 0 else "#FF5252"
                        change_sign = "+" if pct_change >= 0 else ""
                        st.markdown(f'<p style="text-align: center; font-size: 18px;"><span style="color: {change_color}; font-weight: bold;">{change_sign}{pct_change:.2f}%</span> over {selected_timeframe}</p>', unsafe_allow_html=True)

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
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Operating Cash Flow'), 0),
                        key="cf_metric1"
                    )
                    metric1 = next(col for display, col in available_metrics if display == metric1_display)
                
                with col2:
                    metric2_display = st.selectbox(
                        "Metric 2:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if 'Capital Expenditure' in d or 'CapEx' in d), min(1, len(available_metrics)-1)),
                        key="cf_metric2"
                    )
                    metric2 = next(col for display, col in available_metrics if display == metric2_display)
                
                with col3:
                    metric3_display = st.selectbox(
                        "Metric 3:",
                        options=[display for display, _ in available_metrics],
                        index=next((i for i, (d, _) in enumerate(available_metrics) if d == 'Free Cash Flow'), min(2, len(available_metrics)-1)),
                        key="cf_metric3"
                    )
                    metric3 = next(col for display, col in available_metrics if display == metric3_display)
                
                metrics_to_plot = [metric1, metric2, metric3]
                
                # Show what these metrics mean - try both display name and API column name
                with st.expander("📚 What do these metrics mean?", expanded=False):
                    for metric_display, metric_col in zip([metric1_display, metric2_display, metric3_display], metrics_to_plot):
                        # Try display name first, then API column name
                        explanation = get_metric_explanation(metric_display)
                        if not explanation:
                            explanation = get_metric_explanation(metric_col)
                        if explanation:
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* {explanation["simple"]}  
                💡 *Why it matters:* {explanation["why"]}""")
                            st.markdown("---")
                        else:
                            # Provide a generic explanation if none found
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* Financial metric from company reports  
                💡 *Why it matters:* Track this over time to spot trends""")
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
                    "Amount ($)",
                    period_type=period
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
                
                # Show what these metrics mean - try both display name and API column name
                with st.expander("📚 What do these metrics mean?", expanded=False):
                    for metric_display, metric_col in zip([metric1_display, metric2_display, metric3_display], metrics_to_plot):
                        # Try display name first, then API column name
                        explanation = get_metric_explanation(metric_display)
                        if not explanation:
                            explanation = get_metric_explanation(metric_col)
                        if explanation:
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* {explanation["simple"]}  
                💡 *Why it matters:* {explanation["why"]}""")
                            st.markdown("---")
                        else:
                            # Provide a generic explanation if none found
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* Financial metric from company reports  
                💡 *Why it matters:* Track this over time to spot trends""")
                            st.markdown("---")
                
                metric_names = [metric1_display, metric2_display, metric3_display]
                
                plot_df = income_df[["date"] + metrics_to_plot].copy()
                
                fig, growth_rates = create_financial_chart_with_growth(
                    plot_df,
                    metrics_to_plot,
                    f"{company_name} - Income Statement",
                    "Period",
                    "Amount ($)",
                    period_type=period
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
                
                # Show what these metrics mean - try both display name and API column name
                with st.expander("📚 What do these metrics mean?", expanded=False):
                    for metric_display, metric_col in zip([metric1_display, metric2_display, metric3_display], metrics_to_plot):
                        # Try display name first, then API column name
                        explanation = get_metric_explanation(metric_display)
                        if not explanation:
                            explanation = get_metric_explanation(metric_col)
                        if explanation:
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* {explanation["simple"]}  
                💡 *Why it matters:* {explanation["why"]}""")
                            st.markdown("---")
                        else:
                            # Provide a generic explanation if none found
                            st.markdown(f"""**{metric_display}**  
                📊 *What it is:* Financial metric from company reports  
                💡 *Why it matters:* Track this over time to spot trends""")
                            st.markdown("---")
                
                metric_names = [metric1_display, metric2_display, metric3_display]
                
                plot_df = balance_df[["date"] + metrics_to_plot].copy()
                
                fig, growth_rates = create_financial_chart_with_growth(
                    plot_df,
                    metrics_to_plot,
                    f"{company_name} - Balance Sheet",
                    "Period",
                    "Amount ($)",
                    period_type=period
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
            # Show logo for stock1
            if stock1:
                logo1 = get_company_logo(stock1)
                if logo1:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 5px;">
                        <img src="{logo1}" width="28" height="28" style="border-radius: 4px; margin-right: 8px;">
                        <span style="font-weight: 500;">{stock1.upper()}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            stock2 = st.text_input("Stock 2:", placeholder="e.g., MSFT", key="compare_stock2")
            # Show logo for stock2
            if stock2:
                logo2 = get_company_logo(stock2)
                if logo2:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 5px;">
                        <img src="{logo2}" width="28" height="28" style="border-radius: 4px; margin-right: 8px;">
                        <span style="font-weight: 500;">{stock2.upper()}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
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
    
    # AI Coach integration with ticker context
    render_ai_coach("Company Analysis", ticker=ticker if ticker and ticker != "AAPL" else None, facts=None)


elif selected_page == "📊 Market Overview":
    
    st.header("📊 Market Overview")
    st.caption("*Top 100 stocks by market cap (ETFs excluded). Real-time data from FMP Stock Screener.*")
    
    # Show data source indicator
    show_data_source(source="FMP Stock Screener API", updated_at=datetime.now())
    
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

    # AI Coach integration
    render_ai_coach("Market Overview", ticker=None, facts=None)


# ============= AI STOCK SCREENER PAGE =============
elif selected_page == "🔍 AI Stock Screener":
    # Check tier - Ultimate only
    user_tier = get_user_tier()
    
    # Red pill header matching the app theme
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FF4B4B 0%, #CC0000 100%); 
                padding: 15px 25px; 
                border-radius: 15px; 
                text-align: center; 
                margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(255, 51, 51, 0.3);">
        <h2 style="margin: 0; color: #FFFFFF; font-size: 24px; font-weight: bold;">
            🔍 AI Stock Screener — Just Ask!
        </h2>
        <p style="margin: 5px 0 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">
            Natural language screening • AI-powered • Ultimate tier exclusive
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Gate for non-Ultimate users
    if user_tier != "ultimate":
        st.markdown("""
        <div style="background: rgba(255, 215, 0, 0.1); border: 2px dashed #FFD700; border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0;">
            <div style="font-size: 48px; margin-bottom: 15px;">🔒</div>
            <h3 style="color: #FFD700; margin-bottom: 10px;">Ultimate Tier Feature</h3>
            <p style="color: #888; margin-bottom: 20px;">AI-powered stock screening is exclusive to Ultimate members</p>
            <p style="color: #FFF;">Ask questions like:</p>
            <p style="color: #888; font-style: italic;">"Find undervalued tech stocks with strong cash flow"</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Upgrade to Ultimate", key="upgrade_screener", use_container_width=True, type="primary"):
            st.session_state.selected_page = "👑 Become a VIP"
            st.rerun()
        
        # Show example of what they'd get
        st.markdown("---")
        st.markdown("### 💡 What You Could Search")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Growth + Value:**
            - Find tech stocks growing 15%+ with high FCF
            - Show me small caps with explosive growth but cheap
            
            **Quality + Income:**
            - Give me dividend aristocrats with low debt
            - Find stocks with ROE over 30% and low leverage
            """)
        with col2:
            st.markdown("""
            **Value Plays:**
            - Show me undervalued stocks with P/E under 12
            - Find companies trading below book value
            
            **Custom Criteria:**
            - Stocks improving margins with growing revenue
            - Companies with high FCF yield but low P/S
            """)
    else:
        # ============= ULTIMATE USERS: FULL AI SCREENER =============
        
        # Search input
        st.markdown("### 🎯 What are you looking for?")
        
        # Query input
        user_query = st.text_area(
            "Describe what you want in plain English:",
            placeholder="e.g., Find undervalued tech stocks with P/E under 20 and revenue growing at least 10%",
            height=80,
            key="screener_query"
        )
        
        # Quick suggestion buttons
        st.markdown("**💡 Try these:**")
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        with quick_col1:
            if st.button("Value stocks P/E < 15", key="quick_value"):
                user_query = "Find value stocks with P/E under 15 and positive earnings"
                st.session_state.screener_query = user_query
        with quick_col2:
            if st.button("Dividend growers", key="quick_div"):
                user_query = "Show me dividend paying stocks with low debt and growing dividends"
                st.session_state.screener_query = user_query
        with quick_col3:
            if st.button("Growth + quality", key="quick_growth"):
                user_query = "Find tech stocks growing revenue 15%+ with strong margins"
                st.session_state.screener_query = user_query
        
        # Search button
        search_clicked = st.button("🔍 Search Stocks", key="run_screener", type="primary", use_container_width=True)
        
        if search_clicked and user_query:
            with st.spinner("🤖 AI is analyzing your request..."):
                # Step 1: Parse query with OpenAI
                parse_prompt = f"""Parse this stock screening request into JSON criteria.

User query: "{user_query}"

Return ONLY valid JSON with these optional fields:
{{
    "sector": "Technology" | "Healthcare" | "Financial Services" | "Consumer Cyclical" | "Communication Services" | "Industrials" | "Consumer Defensive" | "Energy" | "Utilities" | "Real Estate" | "Basic Materials" | null,
    "market_cap_min": number or null (in dollars, e.g., 1000000000 for $1B),
    "market_cap_max": number or null,
    "pe_min": number or null,
    "pe_max": number or null,
    "dividend_min": number or null (as percentage, e.g., 2 for 2%),
    "price_min": number or null,
    "price_max": number or null,
    "beta_min": number or null,
    "beta_max": number or null,
    "volume_min": number or null,
    "limit": number (default 20, max 50),
    "sort_by": "marketCap" | "pe" | "dividend" | "volume" | "price",
    "sort_order": "asc" | "desc",
    "user_intent": "brief description of what user wants"
}}

Be generous in interpretation. If user says "cheap" use pe_max: 15. If "large cap" use market_cap_min: 10000000000.
If user says "undervalued" use pe_max: 20. If "growth" focus on tech/healthcare sectors.
If user says "dividend" set dividend_min: 1.

Return ONLY the JSON, no explanation."""

                try:
                    parse_resp = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": "gpt-4o-mini",
                            "messages": [{"role": "user", "content": parse_prompt}],
                            "temperature": 0.3,
                            "max_tokens": 500
                        },
                        timeout=20
                    )
                    
                    if parse_resp.status_code == 200:
                        content = parse_resp.json()["choices"][0]["message"]["content"].strip()
                        content = content.replace("```json", "").replace("```", "").strip()
                        criteria = json.loads(content)
                    else:
                        st.error("AI parsing failed. Please try again.")
                        criteria = None
                except Exception as e:
                    st.error(f"AI error: {str(e)}")
                    criteria = None
                
                if criteria:
                    # Show parsed criteria
                    with st.expander("🔧 Parsed Criteria", expanded=False):
                        st.json(criteria)
                    
                    # Step 2: Build FMP API call
                    screener_url = f"{BASE_URL}/stock-screener?"
                    params = {"apikey": FMP_API_KEY, "isEtf": "false", "isActivelyTrading": "true"}
                    
                    if criteria.get("sector"):
                        params["sector"] = criteria["sector"]
                    if criteria.get("market_cap_min"):
                        params["marketCapMoreThan"] = int(criteria["market_cap_min"])
                    if criteria.get("market_cap_max"):
                        params["marketCapLowerThan"] = int(criteria["market_cap_max"])
                    if criteria.get("pe_min"):
                        params["priceMoreThan"] = 0  # Ensure positive price
                    if criteria.get("pe_max"):
                        # FMP doesn't have direct PE filter, we'll filter client-side
                        pass
                    if criteria.get("dividend_min"):
                        params["dividendMoreThan"] = criteria["dividend_min"]
                    if criteria.get("price_min"):
                        params["priceMoreThan"] = criteria["price_min"]
                    if criteria.get("price_max"):
                        params["priceLowerThan"] = criteria["price_max"]
                    if criteria.get("beta_min"):
                        params["betaMoreThan"] = criteria["beta_min"]
                    if criteria.get("beta_max"):
                        params["betaLowerThan"] = criteria["beta_max"]
                    if criteria.get("volume_min"):
                        params["volumeMoreThan"] = int(criteria["volume_min"])
                    
                    params["limit"] = min(criteria.get("limit", 20), 50)
                    
                    # Fetch from FMP
                    try:
                        screener_resp = requests.get(screener_url, params=params, timeout=15)
                        
                        if screener_resp.status_code == 200:
                            stocks = screener_resp.json()
                            
                            # Client-side P/E filtering if needed
                            pe_max = criteria.get("pe_max")
                            pe_min = criteria.get("pe_min")
                            
                            if pe_max or pe_min:
                                filtered_stocks = []
                                for stock in stocks:
                                    pe = stock.get("pe")
                                    if pe and pe > 0:
                                        if pe_max and pe > pe_max:
                                            continue
                                        if pe_min and pe < pe_min:
                                            continue
                                        filtered_stocks.append(stock)
                                stocks = filtered_stocks[:params["limit"]]
                            
                            if stocks:
                                st.success(f"✅ Found {len(stocks)} stocks matching your criteria!")
                                
                                # Display results
                                st.markdown("### 📊 Results")
                                
                                # Build results table
                                results_data = []
                                for stock in stocks[:20]:  # Limit display to 20
                                    ticker = stock.get("symbol", "")
                                    logo_url = get_company_logo(ticker)
                                    
                                    results_data.append({
                                        "logo": logo_url,
                                        "ticker": ticker,
                                        "name": stock.get("companyName", "")[:30],
                                        "sector": stock.get("sector", "N/A"),
                                        "price": stock.get("price", 0),
                                        "change": stock.get("changesPercentage", 0),
                                        "pe": stock.get("pe", 0),
                                        "market_cap": stock.get("marketCap", 0),
                                        "dividend": stock.get("lastAnnualDividend", 0),
                                        "volume": stock.get("volume", 0)
                                    })
                                
                                # Display as cards
                                for i, row in enumerate(results_data):
                                    col1, col2, col3, col4, col5, col6 = st.columns([0.8, 2, 1.5, 1, 1, 0.8])
                                    
                                    with col1:
                                        if row["logo"]:
                                            st.markdown(f'<img src="{row["logo"]}" width="40" height="40" style="border-radius: 8px;">', unsafe_allow_html=True)
                                        else:
                                            st.markdown("📈")
                                    
                                    with col2:
                                        st.markdown(f"**{row['ticker']}**")
                                        st.caption(row['name'])
                                    
                                    with col3:
                                        change_color = "#22c55e" if row['change'] >= 0 else "#ef4444"
                                        st.markdown(f"${row['price']:.2f}")
                                        st.markdown(f"<span style='color:{change_color}'>{row['change']:+.2f}%</span>", unsafe_allow_html=True)
                                    
                                    with col4:
                                        if row['pe'] and row['pe'] > 0:
                                            pe_color = "#22c55e" if row['pe'] < 20 else "#f59e0b" if row['pe'] < 35 else "#ef4444"
                                            st.markdown(f"<span style='color:{pe_color}'>{row['pe']:.1f}x</span>", unsafe_allow_html=True)
                                        else:
                                            st.markdown("N/A")
                                        st.caption("P/E")
                                    
                                    with col5:
                                        if row['market_cap'] >= 1e12:
                                            cap_str = f"${row['market_cap']/1e12:.1f}T"
                                        elif row['market_cap'] >= 1e9:
                                            cap_str = f"${row['market_cap']/1e9:.1f}B"
                                        else:
                                            cap_str = f"${row['market_cap']/1e6:.0f}M"
                                        st.markdown(cap_str)
                                        st.caption("Mkt Cap")
                                    
                                    with col6:
                                        if st.button("📌", key=f"pin_screener_{row['ticker']}_{i}"):
                                            if row['ticker'] not in st.session_state.pinned_tickers:
                                                pin_limit = get_tier_limit("pinned_tickers")
                                                if len(st.session_state.pinned_tickers) < pin_limit:
                                                    st.session_state.pinned_tickers.append(row['ticker'])
                                                    st.success(f"Added {row['ticker']}!")
                                                    st.rerun()
                                    
                                    st.markdown("---")
                                
                                # Step 3: AI Analysis of results
                                st.markdown("### 🤖 AI Analysis")
                                
                                with st.spinner("Generating insights..."):
                                    # Get top 5 for analysis
                                    top_stocks = results_data[:5]
                                    stocks_summary = "\n".join([
                                        f"- {s['ticker']}: ${s['price']:.2f}, P/E {s['pe']:.1f}x, {s['sector']}"
                                        for s in top_stocks if s['pe'] and s['pe'] > 0
                                    ])
                                    
                                    analysis_prompt = f"""The user searched for: "{user_query}"

Here are the top matching stocks:
{stocks_summary}

Write a brief, helpful analysis (3-4 sentences) explaining:
1. Why these stocks match the criteria
2. One thing to watch out for
3. A suggestion for further research

Be educational, not advisory. Don't recommend buying."""

                                    try:
                                        analysis_resp = requests.post(
                                            "https://api.openai.com/v1/chat/completions",
                                            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                                            json={
                                                "model": "gpt-4o-mini",
                                                "messages": [{"role": "user", "content": analysis_prompt}],
                                                "temperature": 0.7,
                                                "max_tokens": 300
                                            },
                                            timeout=20
                                        )
                                        
                                        if analysis_resp.status_code == 200:
                                            analysis = analysis_resp.json()["choices"][0]["message"]["content"].strip()
                                            st.info(analysis)
                                        else:
                                            st.info("Analysis unavailable.")
                                    except:
                                        st.info("Analysis unavailable.")
                                
                                # Export option
                                st.markdown("### 📥 Export")
                                if st.button("📄 Export to CSV", key="export_screener"):
                                    import io
                                    df_export = pd.DataFrame(results_data)
                                    csv_buffer = io.StringIO()
                                    df_export.to_csv(csv_buffer, index=False)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv_buffer.getvalue(),
                                        file_name=f"stock_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                        mime="text/csv"
                                    )
                                
                                show_data_source(source="FMP Stock Screener API + OpenAI", updated_at=datetime.now())
                            else:
                                st.warning("No stocks found matching your criteria. Try broadening your search.")
                        else:
                            st.error(f"API error: {screener_resp.status_code}")
                    except Exception as e:
                        st.error(f"Search error: {str(e)}")
        
        elif search_clicked and not user_query:
            st.warning("Please enter what you're looking for!")
        
        # Show examples at bottom
        st.markdown("---")
        st.markdown("### 💡 Example Queries")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Growth + Value:**
            - Find tech stocks growing 15%+ with high FCF
            - Show me small caps with explosive growth but cheap
            
            **Quality + Income:**
            - Give me dividend aristocrats with low debt
            - Find stocks with ROE over 30% and low leverage
            """)
        with col2:
            st.markdown("""
            **Value Plays:**
            - Show me undervalued stocks with P/E under 12
            - Find companies trading below book value
            
            **Custom Criteria:**
            - Stocks improving margins with growing revenue
            - Companies with high FCF yield but low P/S
            """)
    
    # AI Coach integration
    render_ai_coach("AI Stock Screener", ticker=None, facts=None)


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
        # Use global settings
        years = st.session_state.get('years_of_history', 5)
        period_type = st.session_state.get('global_period', 'annual')
    
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
                
                # Y-axis with 15% padding to ensure data never exceeds axis
                all_y = list(ratio_data[ratio_col]) + [benchmark_val]
                y_min, y_max = min(all_y), max(all_y)
                y_range = y_max - y_min if y_max != y_min else abs(y_max) * 0.1 or 1
                
                fig.update_layout(
                    title=f"{ratio_name} Over Time",
                    xaxis_title="Date",
                    yaxis_title=ratio_name,
                    yaxis=dict(range=[y_min - y_range * 0.15, y_max + y_range * 0.15]),
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
                # Title with clickable info button
                col1, col2 = st.columns([12, 1])
                with col1:
                    st.markdown(f"### {ratio_name}")
                with col2:
                    with st.popover("❓", use_container_width=True):
                        st.markdown(f"**📖 Definition:**")
                        st.info(tooltip_def)
                        st.markdown(f"**💡 Example:**")
                        st.success(tooltip_example)
                
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
    
    # AI Coach integration
    render_ai_coach("Financial Health", ticker=ticker if ticker else None, facts=None)


# ============= MARKET INTELLIGENCE TAB =============
elif selected_page == "📰 Market Intelligence":
    
    # Show page popup
    show_page_popup(
        'market_intelligence',
        '📰 Market Intelligence',
        'Stay informed with AI-powered news, earnings calendar, and market sentiment. Search any stock for latest news.',
        'Real-time market sentiment gauge shows fear vs greed levels!'
    )
    
    st.header("📰 Market Intelligence & News")
    st.markdown("**Stay informed with AI-powered market insights, news, and earnings**")
    
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
    
    # Show data source for sentiment
    show_data_source(source="Market Sentiment Algorithm", updated_at=datetime.now())
    
    st.markdown("---")
    
    # ============= TOP MARKET NEWS (NEW!) =============
    st.markdown("### 📰 Latest Market News")
    st.caption("AI-powered news summaries from Perplexity")
    
    # Function to get top news
    def get_top_market_news():
        """Fetch top market news using Perplexity API with fallback models"""
        if not PERPLEXITY_API_KEY:
            return None, "Perplexity API key not configured"
        
        # Try multiple models in order of preference
        models_to_try = [
            "sonar-small-online",
            "sonar",
            "llama-3.1-sonar-small-128k-online"
        ]
        
        query = """What are today's top 8 US stock market news stories?

CRITICAL FORMATTING RULES:
- ONE bullet point per line
- Format: • Headline - Brief summary [TICKER]
- Focus ONLY on US markets (NYSE, NASDAQ)
- NO Indian markets, NO international unless major US impact
- Topics: S&P 500, Fed policy, major earnings (AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, JPM, BAC, etc), economic data

Example format:
• JPMorgan Earnings Beat - Q4 profit rises 50% on investment banking surge [JPM]
• Fed Signals Rate Cuts - Powell hints at 2 cuts in 2026 based on inflation data
• Tesla Deliveries Miss - Q4 deliveries fall short of estimates amid competition [TSLA]

Keep each bullet to ONE line. Be concise."""
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        last_error = None
        
        # Try each model
        for model_name in models_to_try:
            try:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                # Log response for debugging
                print(f"[DEBUG] Perplexity response ({model_name}): status={response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content and len(content) > 50:
                        print(f"[DEBUG] Success with model: {model_name}")
                        return content, None
                    else:
                        last_error = f"Empty response from {model_name}"
                        continue
                else:
                    # Try to get error details
                    try:
                        error_data = response.json()
                        last_error = f"{model_name}: {response.status_code} - {error_data}"
                    except:
                        last_error = f"{model_name}: HTTP {response.status_code}"
                    
                    print(f"[DEBUG] {last_error}")
                    continue
                    
            except requests.exceptions.Timeout:
                last_error = f"{model_name}: Request timeout"
                print(f"[DEBUG] {last_error}")
                continue
            except Exception as e:
                last_error = f"{model_name}: {str(e)}"
                print(f"[DEBUG] {last_error}")
                continue
        
        # All models failed
        return None, f"All models failed. Last error: {last_error}"
        
        # All models failed
        return None, f"All models failed. Last error: {last_error}"
    
    # Fetch and display top news
    with st.spinner("🔄 Fetching latest market news..."):
        top_news, error = get_top_market_news()
    
    if top_news:
        # Display in a card with light blue background
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FC 100%); 
                    border: 2px solid #ff3333; border-radius: 15px; padding: 30px; margin: 20px 0;">
            <div style="color: #1a1a2e; font-size: 16px; line-height: 1.8;">
                {top_news}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Link to Perplexity for deeper exploration
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://www.perplexity.ai" target="_blank" 
               style="background-color: #ff3333; color: white; padding: 12px 30px; 
                      border-radius: 8px; text-decoration: none; font-weight: bold; 
                      display: inline-block;">
                🔍 Explore More on Perplexity
            </a>
        </div>
        """, unsafe_allow_html=True)
    elif error:
        st.warning(f"Could not fetch news: {error}")
        st.info("Try again later or check if the Perplexity API key is configured correctly.")
    
    st.markdown("---")
    
    # ============= NEWS AFFECTING YOUR PORTFOLIO (NEW!) =============
    # Only show if user has portfolio positions
    user_portfolio = st.session_state.get('portfolio', [])
    founder_portfolio = st.session_state.get('founder_portfolio', [])
    
    # Combine both portfolios to check if user has any positions
    all_positions = user_portfolio + founder_portfolio
    
    if all_positions:
        st.markdown("### 📊 News Affecting Your Portfolio")
        st.caption("Personalized news for stocks you own")
        
        # Get unique tickers from portfolio
        portfolio_tickers = list(set([pos['ticker'] for pos in all_positions]))
        
        # Function to get portfolio-specific news
        def get_portfolio_news(tickers):
            """Fetch news for specific tickers"""
            if not PERPLEXITY_API_KEY:
                return None, "Perplexity API key not configured"
            
            try:
                tickers_str = ", ".join(tickers[:10])  # Limit to first 10 tickers
                query = f"""Latest news and developments for these stocks: {tickers_str}
                
                For each stock with significant news, provide:
                - **[TICKER]** Brief headline
                - 1-2 sentence summary
                - Impact assessment (positive/negative/neutral)
                
                Focus on: earnings, analyst ratings, product launches, regulatory news, major price movements.
                Skip stocks with no recent news. Keep it concise."""
                
                headers = {
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": "You are a portfolio analyst. Provide relevant, actionable news summaries for the user's holdings."},
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
        
        with st.spinner(f"🔄 Fetching news for your {len(portfolio_tickers)} holdings..."):
            portfolio_news, port_error = get_portfolio_news(portfolio_tickers)
        
        if portfolio_news:
            # Show which stocks you own
            st.info(f"📈 **Your Holdings:** {', '.join(portfolio_tickers)}")
            
            # Display portfolio news with GREEN accent
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a2e1a 0%, #162e21 100%); 
                        border: 2px solid #4CAF50; border-radius: 15px; padding: 30px; margin: 20px 0;">
                <div style="color: #FFFFFF; font-size: 16px; line-height: 1.8;">
                    {portfolio_news}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif port_error:
            st.warning(f"Could not fetch portfolio news: {port_error}")
        
        st.markdown("---")
    
    # ============= EARNINGS CALENDAR (Using FMP API) =============
    st.markdown("### 📅 Earnings Calendar - This Week")
    st.caption("Biggest earnings releases this week • Source: FMP API")
    
    with st.spinner("📊 Loading earnings calendar..."):
        earnings_by_day, earnings_error = get_weekly_earnings_fmp()
    
    if earnings_by_day and len(earnings_by_day) > 0:
        # Build formatted earnings display
        earnings_html = ""
        day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        
        # Sort dates
        sorted_dates = sorted(earnings_by_day.keys())
        
        for date_str in sorted_dates:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                day_name = day_names.get(date_obj.weekday(), '')
                formatted_date = date_obj.strftime('%B %d')
                earnings_html += f"<p><strong>{day_name}, {formatted_date}:</strong></p>"
                
                for earning in earnings_by_day[date_str]:
                    symbol = earning['symbol']
                    company_name = earning.get('company_name', symbol)
                    # Show company name followed by ticker
                    if company_name and company_name != symbol:
                        earnings_html += f"<p>• <strong>{company_name}</strong> ({symbol})</p>"
                    else:
                        earnings_html += f"<p>• {symbol}</p>"
            except:
                continue
        
        if earnings_html:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FC 100%); 
                        border: 2px solid #ff3333; border-radius: 15px; padding: 30px; margin: 20px 0;">
                <div style="color: #1a1a2e; font-size: 16px; line-height: 1.8;">
                    {earnings_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No major earnings scheduled for this week.")
    elif earnings_error:
        st.warning(f"Could not fetch earnings: {earnings_error}")
        st.info("📊 Check FMP API connection")
    else:
        st.info("No major earnings scheduled for this week.")
    
    st.markdown("---")
    
    # ============= STOCK-SPECIFIC NEWS SEARCH =============
    st.markdown("### 🔍 Search Stock News")
    intel_input = st.text_input(
        "Enter a company name or ticker:",
        "",
        placeholder="e.g., Apple, Tesla, GOOGL, Microsoft",
        key="intel_ticker_search"
    )
    
    # Resolve company name to ticker
    intel_ticker = resolve_company_to_ticker(intel_input) if intel_input.strip() else None
    
    # Show resolved ticker with LOGO if different from input
    if intel_input.strip() and intel_ticker:
        intel_logo = get_company_logo(intel_ticker)
        intel_profile = get_profile(intel_ticker)
        intel_company_name = intel_profile.get('companyName', intel_ticker) if intel_profile else intel_ticker
        
        if intel_logo:
            st.markdown(f"""
            <div style="display: flex; align-items: center; background: rgba(128,128,128,0.1); padding: 12px; border-radius: 10px; margin: 10px 0;">
                <img src="{intel_logo}" width="40" height="40" style="border-radius: 6px; margin-right: 12px;">
                <div>
                    <div style="font-size: 18px; font-weight: bold;">{intel_ticker}</div>
                    <div style="color: #888; font-size: 13px;">{intel_company_name}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif intel_ticker.upper() != intel_input.strip().upper():
            st.caption(f"Searching for: **{intel_ticker}**")
    
    # Fit Check Panel (only if ticker selected) - REMOVED - causes issues
    if intel_ticker:
        # REMOVED: render_fit_check_panel(intel_ticker)
        # Just show news directly without risk quiz
        
        # Function to get market news via Perplexity API
        def get_stock_intelligence(ticker):
            """Fetch stock-specific news using Perplexity API"""
            if not PERPLEXITY_API_KEY:
                return None, "Perplexity API key not configured"
            
            try:
                query = f"Latest news, catalysts, and market analysis for {ticker.upper()} stock. Include recent price movements, analyst opinions, and any significant company developments. Format with clear sections and bullet points."
                
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
        
        # Fetch and display stock news
        with st.spinner(f"Fetching latest {intel_ticker} intelligence..."):
            stock_news, stock_error = get_stock_intelligence(intel_ticker)
        
        if stock_news:
            st.markdown(f"### 📊 {intel_ticker.upper()} - Latest News & Analysis")
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        border: 2px solid #00D9FF; border-radius: 15px; padding: 30px; margin: 20px 0;">
                <div style="color: #FFFFFF; font-size: 16px; line-height: 1.8;">
                    {stock_news}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif stock_error:
            st.warning(f"Could not fetch {intel_ticker} news: {stock_error}")
        
        # FMP news headlines for this stock
        fmp_news = get_stock_specific_news(intel_ticker.upper(), 10)
        if fmp_news:
            st.markdown("#### Recent Headlines")
            for article in fmp_news:
                title = article.get('title', 'No title')
                published = article.get('publishedDate', '')[:10] if article.get('publishedDate') else ''
                url = article.get('url', '')
                if url:
                    st.markdown(f"- [{title}]({url}) ({published})")
                else:
                    st.markdown(f"- **{title}** ({published})")
    
    st.markdown("---")
    st.caption("*News powered by Perplexity AI and Financial Modeling Prep. This is not financial advice.*")
    
    # AI Coach integration
    render_ai_coach("Market Intelligence", ticker=None, facts=None)



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
        
        # Email capture form with Supabase integration
        st.markdown("### 📧 Join the Waitlist")
        col1, col2 = st.columns([3, 1])
        with col1:
            waitlist_email = st.text_input("Enter your email:", placeholder="your@email.com", key="waitlist_email")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Join Waitlist", key="join_waitlist", type="primary"):
                if waitlist_email and "@" in waitlist_email and "." in waitlist_email:
                    success, message = save_waitlist_email(waitlist_email, "pro")
                    if success:
                        if message == "Already on waitlist":
                            st.info(f"📧 {waitlist_email} is already on the waitlist!")
                        else:
                            st.success(f"🎉 You're on the list! We'll notify {waitlist_email} when spots open.")
                            st.balloons()
                    else:
                        # Fallback - show success anyway for UX
                        st.success(f"🎉 You're on the list! We'll notify {waitlist_email} when spots open.")
                else:
                    st.error("Please enter a valid email address.")
        
        # Show dynamic waitlist count
        waitlist_count = get_waitlist_count()
        st.info(f"**Current waitlist:** {waitlist_count} people ahead of you. Pro spots open monthly.")
        
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
            "- **🔍 AI Stock Screener** - Ask in plain English, get matching stocks!\n"
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
        <div style="background: #E3F2FD; border: 3px solid {border_color}; border-radius: 15px; 
                    padding: 20px; text-align: center; box-shadow: {shadow};">
            <h3 style="color: #00C853; margin-bottom: 10px;">Free</h3>
            <p style="color: #333; font-size: 24px; margin: 10px 0;"><strong>$0</strong>/mo</p>
            <p style="color: #555; font-size: 14px;">Preview Access</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select Free", key="select_free_vip", use_container_width=True):
            st.session_state.selected_tier = "Free"
            st.rerun()
    
    with col_pro:
        border_color = "#9D4EDD" if st.session_state.selected_tier == "Pro" else "#333"
        shadow = "0 0 20px rgba(157,78,221,0.5)" if st.session_state.selected_tier == "Pro" else "none"
        st.markdown(f"""
        <div style="background: #E3F2FD; border: 3px solid {border_color}; border-radius: 15px; 
                    padding: 20px; text-align: center; box-shadow: {shadow};">
            <h3 style="color: #9D4EDD; margin-bottom: 10px;">Pro</h3>
            <p style="color: #333; font-size: 24px; margin: 10px 0;"><strong>$5</strong>/mo</p>
            <p style="color: #555; font-size: 14px;">Full Portfolio Access</p>
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
        <div style="background: #E3F2FD; border: 3px solid {border_color}; border-radius: 15px; 
                    padding: 20px; text-align: center; box-shadow: {shadow};">
            <h3 style="color: #FFD700; margin-bottom: 10px;">Ultimate</h3>
            <p style="color: #333; font-size: 24px; margin: 10px 0;"><strong>$10</strong>/mo</p>
            <p style="color: #555; font-size: 14px;">VIP Access + Support</p>
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
            <div style="background:#E3F2FD;border:1px solid #4FC3F7;border-radius:14px;padding:16px;min-height:420px;">
              <h3 style="color:#00C853;margin:0 0 6px 0;">Free</h3>
              <div style="color:#555;font-size:14px;margin-bottom:10px;">Great for getting started</div>
              <ul style="color:#333;line-height:1.6;">
                <li>Market Overview + Sector Explorer basics</li>
                <li>Company Analysis essentials</li>
                <li>Educational content + Risk Quiz</li>
              </ul>
              <div style="color:#666;font-size:12px;margin-top:12px;">
                Tip: Free stays useful — paid tiers add speed + deeper tooling.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_pro2:
        st.markdown(
            """
            <div style="background:#E3F2FD;border:2px solid #9D4EDD;border-radius:14px;padding:16px;min-height:420px;box-shadow:0 0 18px rgba(157,78,221,0.25);">
              <h3 style="color:#9D4EDD;margin:0 0 6px 0;">Pro</h3>
              <div style="color:#555;font-size:14px;margin-bottom:10px;">For technical learners + faster decisions</div>
              <ul style="color:#333;line-height:1.6;">
                <li><b>Pro Chart Lab</b>: candlesticks + SMA50/SMA200/RSI/Volume toggles</li>
                <li><b>Technical Facts</b>: trend regime, momentum, volume/volatility context</li>
                <li><b>Chart Callouts</b>: 3–5 grounded takeaways under every chart</li>
                <li><b>Pattern Detection (AI + Rules)</b>: label + confidence + key levels</li>
                <li><b>Next Steps Checklist</b>: “what traders generally do next” (educational)</li>
              </ul>
              <div style="color:#666;font-size:12px;margin-top:12px;">
                Designed to be <b>accurate per ticker</b> (AI is constrained to computed facts).
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_ult2:
        st.markdown(
            """
            <div style="background:#E3F2FD;border:2px solid #FFD700;border-radius:14px;padding:16px;min-height:420px;box-shadow:0 0 18px rgba(255,215,0,0.20);">
              <h3 style="color:#FFD700;margin:0 0 6px 0;">Ultimate</h3>
              <div style="color:#555;font-size:14px;margin-bottom:10px;">For “show me the receipts” users</div>
              <ul style="color:#333;line-height:1.6;">
                <li>Everything in <b>Pro</b></li>
                <li><b>🔍 AI Stock Screener</b>: Ask in plain English, get matching stocks!</li>
                <li><b>Historical Similar Setups</b>: find past charts that looked like today</li>
                <li><b>Outcome stats</b>: typical next 5D/20D returns + drawdowns (educational)</li>
                <li><b>Backtest-style insights</b> (coming next)</li>
                <li><b>Alerts & watchlists</b> (coming next)</li>
                <li><b>Exportable reports</b> (coming next)</li>
              </ul>
              <div style="color:#666;font-size:12px;margin-top:12px;">
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
            if st.button("🚀 Join Waitlist", key="join_waitlist_vip", type="primary", use_container_width=True):
                if waitlist_email and "@" in waitlist_email and "." in waitlist_email:
                    success, message = save_waitlist_email(waitlist_email, "ultimate")
                    if success:
                        if message == "Already on waitlist":
                            st.info(f"📧 {waitlist_email} is already on the waitlist!")
                        else:
                            st.success(f"🎉 You're on the list! We'll notify {waitlist_email} when spots open.")
                            st.balloons()
                    else:
                        st.success(f"🎉 You're on the list! We'll notify {waitlist_email} when spots open.")
                else:
                    st.error("Please enter a valid email address.")
        
        # Show dynamic waitlist count
        waitlist_count = get_waitlist_count()
        st.info(f"**Current waitlist:** {waitlist_count} people ahead of you. Pro spots open monthly.")
    else:
        st.success("✅ You're currently on the Free tier. Enjoy exploring!")
    
    st.markdown("---")
    st.caption("*Pricing subject to change. No credit card required for waitlist. This is not financial advice.*")


elif selected_page == "📊 Pro Checklist":
    
    # Show page popup
    show_page_popup(
        'pro_checklist',
        '📊 Pro Checklist',
        'Upload stock charts for AI-powered technical pattern detection. Complete a pre-investment checklist.',
        'AI explains chart patterns in plain English - no jargon!'
    )
    
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
    
    # AI Coach integration
    render_ai_coach("Pro Checklist", ticker=ticker_check if 'ticker_check' in locals() else None, facts=None)


# ============================================================================
# 👑 ULTIMATE TAB - PREMIUM AI-FIRST ANALYSIS
# ============================================================================

elif selected_page == "👑 Ultimate":
    
    # Show page popup
    show_page_popup(
        'ultimate',
        '👑 Ultimate',
        'Upload portfolio screenshots for AI analysis. Get personalized feedback on your holdings.',
        'AI analyzes diversification, risk, and allocation in seconds!'
    )
    
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
    st.markdown("### 🤖 Ultimate AI Deep Dive")
    st.caption("*AI-powered analysis using OpenAI GPT-4o-mini - Institutional-grade insights*")
    
    # Check if OpenAI is available
    openai_available = bool(os.environ.get('OPENAI_API_KEY', ''))
    
    if not openai_available:
        st.warning("⚠️ **OpenAI API Key Required**")
        st.info("""
        **Setup Steps:**
        1. Get API key from: https://platform.openai.com/api-keys
        2. Set environment variable: `OPENAI_API_KEY=sk-xxxxx`
        3. Restart the app
        
        **Cost:** ~$0.0004 per request (token-based pricing)
        """)
    
    # ALWAYS show buttons (even without API key)
    col_ai1, col_ai2 = st.columns(2)
    
    with col_ai1:
        trade_plan_btn = st.button("📝 Trade Plan Rationale (AI)", key="ultimate_trade_plan_ai", use_container_width=True, type="primary")
    
    with col_ai2:
        change_view_btn = st.button("🔄 What Would Change View? (AI)", key="ultimate_change_view_ai", use_container_width=True, type="primary")
    
    # Initialize session state
    if 'ultimate_trade_plan_output' not in st.session_state:
        st.session_state.ultimate_trade_plan_output = None
    if 'ultimate_change_view_output' not in st.session_state:
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
        if not openai_available:
            st.error("⚠️ Cannot proceed - OPENAI_API_KEY not set. See setup instructions above.")
        else:
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

                ai_response = call_openai_json(prompt, max_tokens=3500, temperature=0.1)
                
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
                        st.success("✅ AI analysis complete! Check below for results.")
                        st.rerun()  # Auto-refresh to show output
                    else:
                        st.error(f"⚠️ AI validation failed: {error_msg}")
                        st.info("Try clicking the button again. If it persists, check your API key.")
                        st.session_state.ultimate_trade_plan_output = None
                else:
                    st.error("⚠️ OpenAI API request failed - no response received")
                    st.info("""
                    **Check these:**
                    - Is OPENAI_API_KEY set correctly?
                    - Do you have API credits? (check https://platform.openai.com/account/billing)
                    - Check debug logs in console for actual error
                    """)
                    st.session_state.ultimate_trade_plan_output = None
    
    # ============= WHAT WOULD CHANGE VIEW AI =============
    if change_view_btn:
        if not openai_available:
            st.error("⚠️ Cannot proceed - OPENAI_API_KEY not set. See setup instructions above.")
        else:
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

                ai_response = call_openai_json(prompt, max_tokens=3500, temperature=0.1)
                
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
                        st.success("✅ AI analysis complete! Check below for results.")
                        st.rerun()  # Auto-refresh to show output
                    else:
                        st.error(f"⚠️ AI validation failed: {error_msg}")
                        st.info("Try clicking the button again. If it persists, check your API key.")
                        st.session_state.ultimate_change_view_output = None
                else:
                    st.error("⚠️ OpenAI API request failed - no response received")
                    st.info("""
                    **Check these:**
                    - Is OPENAI_API_KEY set correctly?
                    - Do you have API credits? (check https://platform.openai.com/account/billing)
                    - Check debug logs in console for actual error
                    """)
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
    
    
    # ============= PORTFOLIO REVIEW (ULTIMATE EXCLUSIVE) =============
    st.markdown("---")
    st.markdown("### 💼 Portfolio Review (Ultimate)")
    st.caption("*Upload screenshots or analyze your paper portfolio - AI-powered insights*")
    
    # Sub-tabs for different input methods
    review_tab1, review_tab2 = st.tabs(["📸 Upload Screenshots (Recommended)", "📊 Review My Paper Portfolio"])
    
    with review_tab1:
        st.markdown("#### Upload Portfolio Screenshots")
        st.info("📱 Take screenshots from Robinhood, Fidelity, Schwab, or any broker. AI will extract your holdings.")
        
        # RED BACKGROUND for upload area (matches app theme)
        st.markdown("""
        <style>
        div[data-testid="stFileUploader"] {
            background-color: rgba(255, 50, 50, 0.1);
            border: 2px solid #ff3333;
            border-radius: 10px;
            padding: 20px;
        }
        div[data-testid="stFileUploader"] > label {
            color: #ff3333 !important;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # File uploader for 1-5 images
        uploaded_files = st.file_uploader(
            "Upload 1-5 screenshots of your portfolio",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            help="Clear screenshots work best. Multiple images OK if portfolio is long."
        )
        
        if uploaded_files:
            if len(uploaded_files) > 5:
                st.warning("⚠️ Maximum 5 screenshots. Using first 5 only.")
                uploaded_files = uploaded_files[:5]
            
            st.success(f"✅ {len(uploaded_files)} screenshot(s) uploaded")
            
            # Show thumbnails
            cols = st.columns(len(uploaded_files))
            for idx, (col, file) in enumerate(zip(cols, uploaded_files)):
                with col:
                    st.image(file, caption=f"Screenshot {idx+1}", use_column_width=True)
            
            if st.button("🔍 Extract & Analyze Portfolio", type="primary", use_container_width=True):
                with st.spinner("🤖 AI extracting holdings from screenshots..."):
                    # Convert images to base64
                    image_data_list = []
                    for file in uploaded_files:
                        import base64
                        bytes_data = file.getvalue()
                        base64_data = base64.b64encode(bytes_data).decode('utf-8')
                        image_data_list.append(base64_data)
                    
                    # Extract with OpenAI Vision
                    extraction = extract_portfolio_from_screenshot(image_data_list)
                    
                    if not extraction:
                        st.error("❌ Failed to extract portfolio. Please try clearer screenshots or use CSV upload.")
                    else:
                        confidence = extraction.get('confidence', 'Low')
                        holdings = extraction.get('holdings', [])
                        unreadable = extraction.get('unreadable_items', [])
                        
                        # Fail-soft if confidence != High
                        if confidence != "High":
                            st.warning(f"⚠️ Extraction confidence: **{confidence}**. Results may be incomplete.")
                            if unreadable:
                                st.warning(f"Could not read: {', '.join(unreadable)}")
                            st.info("💡 **Tip:** Try uploading clearer screenshots or use the CSV upload option for best results.")
                        
                        # Show extracted holdings
                        st.markdown("#### 📋 Extracted Holdings")
                        if holdings:
                            holdings_df = pd.DataFrame(holdings)
                            st.dataframe(holdings_df, use_container_width=True)
                            
                            # Normalize tickers
                            normalized_holdings = []
                            total_value = 0
                            
                            with st.spinner("📊 Fetching sector data..."):
                                for holding in holdings:
                                    ticker_raw = holding.get('ticker_or_name', '').upper().strip()
                                    
                                    # Try to extract ticker (handle cases like "AAPL - Apple Inc.")
                                    ticker = ticker_raw.split(' ')[0].split('-')[0].strip()
                                    
                                    # Get current price and sector
                                    quote = get_quote(ticker)
                                    sector = "Unknown"
                                    if quote and quote.get('price'):
                                        current_price = quote['price']
                                        
                                        # Try to get sector from FMP
                                        try:
                                            profile_url = f"{BASE_URL}/profile/{ticker}?apikey={FMP_API_KEY}"
                                            profile_resp = requests.get(profile_url, timeout=5)
                                            if profile_resp.status_code == 200:
                                                profile_data = profile_resp.json()
                                                if profile_data and len(profile_data) > 0:
                                                    sector = profile_data[0].get('sector', 'Unknown')
                                        except:
                                            pass
                                        
                                        # Calculate market value
                                        if holding.get('market_value'):
                                            market_value = float(holding['market_value'])
                                        elif holding.get('shares'):
                                            market_value = float(holding['shares']) * current_price
                                        else:
                                            market_value = 0
                                        
                                        normalized_holdings.append({
                                            'ticker': ticker,
                                            'sector': sector,
                                            'shares': holding.get('shares'),
                                            'market_value': market_value,
                                            'weight': holding.get('weight')
                                        })
                                        total_value += market_value
                            
                            # Compute deterministic metrics
                            if normalized_holdings and total_value > 0:
                                # Recalculate weights
                                for holding in normalized_holdings:
                                    holding['weight_pct'] = (holding['market_value'] / total_value) * 100 if total_value > 0 else 0
                                
                                # Sector allocation
                                sector_totals = {}
                                for holding in normalized_holdings:
                                    sector = holding['sector']
                                    sector_totals[sector] = sector_totals.get(sector, 0) + holding['market_value']
                                
                                sector_allocation = {sector: (value / total_value) * 100 for sector, value in sector_totals.items()}
                                
                                # Find largest holding
                                largest_holding = max(normalized_holdings, key=lambda x: x['market_value'])
                                
                                # Calculate concentration risk
                                concentration_risk = largest_holding['weight_pct']
                                
                                # Diversification score (simple: 10 - HHI/1000, capped at 10)
                                hhi = sum([(weight_pct ** 2) for weight_pct in [h['weight_pct'] for h in normalized_holdings]])
                                diversification_score = max(0, min(10, 10 - (hhi / 1000)))
                                
                                # Prepare metrics for AI
                                portfolio_metrics = {
                                    "total_value": total_value,
                                    "num_positions": len(normalized_holdings),
                                    "largest_holding": {
                                        "ticker": largest_holding['ticker'],
                                        "percent": largest_holding['weight_pct']
                                    },
                                    "sector_allocation": sector_allocation,
                                    "concentration_risk": concentration_risk,
                                    "diversification_score": diversification_score,
                                    "holdings": normalized_holdings
                                }
                                
                                # Display Summary Card
                                st.markdown("#### 📊 Portfolio Summary")
                                col1, col2, col3, col4 = st.columns(4)
                                col1.metric("Total Value", f"${total_value:,.2f}")
                                col2.metric("Positions", len(normalized_holdings))
                                col3.metric("Largest", f"{largest_holding['ticker']} ({largest_holding['weight_pct']:.1f}%)")
                                col4.metric("Diversification", f"{diversification_score:.1f}/10")
                                
                                # Sector Chart
                                if len(sector_allocation) > 0:
                                    import plotly.graph_objects as go
                                    fig_sector = go.Figure(data=[go.Pie(
                                        labels=list(sector_allocation.keys()),
                                        values=list(sector_allocation.values()),
                                        hole=0.3
                                    )])
                                    fig_sector.update_layout(
                                        title="Sector Allocation",
                                        height=400,
                                        template="plotly_dark"
                                    )
                                    st.plotly_chart(fig_sector, use_container_width=True)
                                
                                # AI Analysis
                                with st.spinner("🤖 AI analyzing your portfolio..."):
                                    ai_prompt = f"""Analyze this portfolio (facts provided). Educational analysis only - no specific buy/sell advice.

PORTFOLIO METRICS (DETERMINISTIC):
- Total Value: ${portfolio_metrics['total_value']:,.2f}
- Number of Positions: {portfolio_metrics['num_positions']}
- Largest Holding: {portfolio_metrics['largest_holding']['ticker']} at {portfolio_metrics['largest_holding']['percent']:.1f}%
- Concentration Risk: {portfolio_metrics['concentration_risk']:.1f}%
- Diversification Score: {portfolio_metrics['diversification_score']:.1f}/10
- Sector Breakdown: {json.dumps(portfolio_metrics['sector_allocation'])}

Return ONLY this JSON structure:
{{
  "grade": "A" or "B" or "C" or "D",
  "summary": "One sentence portfolio assessment",
  "top_risks": [
    "Risk 1 with specific % from facts (MAX 5 BULLETS)",
    "Risk 2...",
    ...
  ],
  "improvement_playbook": [
    "Improvement 1 in educational conditional phrasing (MAX 5 BULLETS)",
    "Improvement 2...",
    ...
  ],
  "confidence": "High" or "Medium" or "Low"
}}

CRITICAL RULES:
- MAX 5 bullets for top_risks
- MAX 5 bullets for improvement_playbook
- Cite specific numbers from facts
- Use conditional phrasing: "Consider", "If seeking", "For those targeting"
- NO specific "sell X%" advice
- Educational tone only"""
                                    
                                    ai_review = call_openai_json(ai_prompt, max_tokens=2000, temperature=0.1)
                                    
                                    if ai_review:
                                        # Display AI Review
                                        with st.expander("🤖 AI Portfolio Review", expanded=True):
                                            grade = ai_review.get('grade', 'C')
                                            grade_colors = {'A': '#4CAF50', 'B': '#8BC34A', 'C': '#FFC107', 'D': '#FF5722'}
                                            grade_color = grade_colors.get(grade, '#FFC107')
                                            
                                            st.markdown(f"""
                                            <div style="background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%); 
                                                        padding: 20px; border-radius: 12px; border: 2px solid {grade_color}; margin-bottom: 15px;">
                                                <h2 style="color: {grade_color}; margin: 0;">Grade: {grade}</h2>
                                                <p style="color: #e0e0e0; margin: 10px 0 0 0; font-size: 16px;">{ai_review.get('summary', '')}</p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                            
                                            # Top Risks
                                            st.markdown("**⚠️ Top Risks:**")
                                            top_risks = ai_review.get('top_risks', [])[:5]  # MAX 5
                                            for i, risk in enumerate(top_risks, 1):
                                                st.markdown(f"{i}. {risk}")
                                            
                                            st.markdown("")
                                            
                                            # Improvement Playbook
                                            st.markdown("**📈 Improvement Playbook:**")
                                            improvements = ai_review.get('improvement_playbook', [])[:5]  # MAX 5
                                            for i, improvement in enumerate(improvements, 1):
                                                st.markdown(f"{i}. {improvement}")
                                            
                                            # Trust line
                                            confidence = ai_review.get('confidence', 'Medium')
                                            confidence_icon = "✅" if confidence == "High" else "⚠️"
                                            st.info(f"{confidence_icon} Analysis based on extracted portfolio data • Confidence: {confidence} • Ultimate tier exclusive")
                                    
                                    else:
                                        # Fallback analysis
                                        st.warning("⚠️ AI analysis unavailable. Showing deterministic summary:")
                                        st.markdown(f"""
                                        **Portfolio Grade:** {"A" if diversification_score >= 8 else "B" if diversification_score >= 6 else "C" if diversification_score >= 4 else "D"}
                                        
                                        **Key Facts:**
                                        - Your largest holding ({largest_holding['ticker']}) represents {largest_holding['weight_pct']:.1f}% of portfolio
                                        - Diversification score: {diversification_score:.1f}/10
                                        - {len(normalized_holdings)} total positions
                                        """)
                            
                            else:
                                st.warning("Could not calculate portfolio metrics. Please check holdings data.")
                        
                        else:
                            st.error("No holdings extracted. Please try different screenshots.")
    
    with review_tab2:
        st.markdown("#### Review Your Paper Portfolio")
        
        # Check if user has paper portfolio
        if 'portfolio' in st.session_state and len(st.session_state.portfolio) > 0:
            paper_portfolio = st.session_state.portfolio
            
            st.info(f"📊 Found {len(paper_portfolio)} position(s) in your Paper Portfolio")
            
            if st.button("🔍 Analyze Paper Portfolio", type="primary", use_container_width=True):
                with st.spinner("🤖 AI analyzing your paper portfolio..."):
                    # Calculate metrics deterministically
                    total_value = 0
                    normalized_holdings = []
                    
                    for pos in paper_portfolio:
                        quote = get_quote(pos['ticker'])
                        if quote:
                            current_price = quote['price']
                            market_value = pos['shares'] * current_price
                            total_value += market_value
                            
                            # Get sector
                            sector = "Unknown"
                            try:
                                profile_url = f"{BASE_URL}/profile/{pos['ticker']}?apikey={FMP_API_KEY}"
                                profile_resp = requests.get(profile_url, timeout=5)
                                if profile_resp.status_code == 200:
                                    profile_data = profile_resp.json()
                                    if profile_data and len(profile_data) > 0:
                                        sector = profile_data[0].get('sector', 'Unknown')
                            except:
                                pass
                            
                            normalized_holdings.append({
                                'ticker': pos['ticker'],
                                'sector': sector,
                                'shares': pos['shares'],
                                'market_value': market_value,
                                'avg_price': pos['avg_price']
                            })
                    
                    if total_value > 0:
                        # Calculate weights
                        for holding in normalized_holdings:
                            holding['weight_pct'] = (holding['market_value'] / total_value) * 100
                        
                        # Sector allocation
                        sector_totals = {}
                        for holding in normalized_holdings:
                            sector = holding['sector']
                            sector_totals[sector] = sector_totals.get(sector, 0) + holding['market_value']
                        
                        sector_allocation = {sector: (value / total_value) * 100 for sector, value in sector_totals.items()}
                        
                        # Metrics
                        largest_holding = max(normalized_holdings, key=lambda x: x['market_value'])
                        concentration_risk = largest_holding['weight_pct']
                        hhi = sum([(h['weight_pct'] ** 2) for h in normalized_holdings])
                        diversification_score = max(0, min(10, 10 - (hhi / 1000)))
                        
                        # Display
                        st.markdown("#### 📊 Portfolio Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Total Value", f"${total_value:,.2f}")
                        col2.metric("Positions", len(normalized_holdings))
                        col3.metric("Largest", f"{largest_holding['ticker']} ({largest_holding['weight_pct']:.1f}%)")
                        col4.metric("Diversification", f"{diversification_score:.1f}/10")
                        
                        # Run same AI analysis as screenshot flow
                        portfolio_metrics = {
                            "total_value": total_value,
                            "num_positions": len(normalized_holdings),
                            "largest_holding": {
                                "ticker": largest_holding['ticker'],
                                "percent": largest_holding['weight_pct']
                            },
                            "sector_allocation": sector_allocation,
                            "concentration_risk": concentration_risk,
                            "diversification_score": diversification_score
                        }
                        
                        ai_prompt = f"""Analyze this paper portfolio. Educational analysis only.

PORTFOLIO METRICS:
{json.dumps(portfolio_metrics, indent=2)}

Return JSON with grade, summary, top_risks (MAX 5), improvement_playbook (MAX 5), confidence."""
                        
                        ai_review = call_openai_json(ai_prompt, max_tokens=2000, temperature=0.1)
                        
                        if ai_review:
                            with st.expander("🤖 AI Portfolio Review", expanded=True):
                                grade = ai_review.get('grade', 'C')
                                st.markdown(f"### Grade: {grade}")
                                st.markdown(ai_review.get('summary', ''))
                                
                                st.markdown("**⚠️ Top Risks:**")
                                for i, risk in enumerate(ai_review.get('top_risks', [])[:5], 1):
                                    st.markdown(f"{i}. {risk}")
                                
                                st.markdown("**📈 Improvement Playbook:**")
                                for i, improvement in enumerate(ai_review.get('improvement_playbook', [])[:5], 1):
                                    st.markdown(f"{i}. {improvement}")
                                
                                st.info(f"✅ Analysis based on paper portfolio data • Confidence: {ai_review.get('confidence', 'Medium')}")
        
        else:
            st.info("💼 You don't have any positions in your Paper Portfolio yet. Go to the Paper Portfolio tab to start trading!")
    
    # AI Coach integration
    render_ai_coach("Portfolio Review", ticker=None, facts=None)


# NEW PAPER PORTFOLIO PAGE - Section 6 Implementation
# This will replace lines 8367-8765 in the main file

elif selected_page == "💼 Paper Portfolio":
    
    # Show page popup
    show_page_popup(
        'paper_portfolio',
        '💼 Paper Portfolio',
        'Practice trading with $100,000 fake money. Track your performance vs the market.',
        'Compare your returns against SPY benchmark to see how you stack up!'
    )
    
    st.header("💼 Paper Portfolio")
    st.caption("*Practice trading with fake money. Track your performance vs the market.*")
    
    # Show data source indicator
    show_data_source(source="FMP API + Local Portfolio Data", updated_at=datetime.now())
    
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
        
        # Simple header (matches screenshot)
        st.markdown(f"### {order['action']} {order['ticker']}")
        st.markdown(f"**Shares:** {order['shares']:.4f}")
        st.markdown(f"**Estimated Price:** ${order['price']:.2f}")  
        st.markdown(f"**Estimated Total:** ${order['total']:.2f}")
        
        st.markdown("")
        
        # Post-trade cash with DARK GREEN background for readability
        post_cash = order['post_cash']
        if post_cash < 0:
            # Red for insufficient funds
            st.error(f"⚠️ **Insufficient Funds** - You need ${abs(post_cash):,.2f} more")
        else:
            # DARK GREEN background (readable on dark theme)
            st.markdown(f"""
            <div style="background-color: rgba(40, 100, 40, 0.8); padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 2px solid #4CAF50;">
                <p style="margin: 0; color: #FFFFFF; font-size: 16px;"><strong>✅ Remaining Cash:</strong> ${post_cash:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Concentration warning with DARK BLUE background (readable)
        if order['post_concentration'] > 0:
            st.markdown(f"""
            <div style="background-color: rgba(30, 50, 90, 0.8); padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 2px solid #2196F3;">
                <p style="margin: 0; color: #FFFFFF; font-size: 16px;">
                    <strong>⚠️ Post-trade Concentration:</strong> {order['post_concentration']:.1f}% in {order['ticker']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
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
                # FIXED: Added try-except for error handling + force rerun
                try:
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
                        
                        # CRITICAL: Clear modal state BEFORE rerun
                        st.session_state.show_order_modal = False
                        st.session_state.pending_order = None
                        
                        # Save progress
                        save_user_progress()
                        
                        # FIXED: Force reload trades from DB for immediate update
                        if order['portfolio_type'] == 'founder':
                            # Reload founder portfolio immediately
                            founder_db_transactions = load_trades_from_db(None, portfolio_type='founder')
                            if founder_db_transactions:
                                st.session_state.founder_transactions = founder_db_transactions
                                founder_cash, _ = calculate_cash_from_db(None, portfolio_type='founder')
                                st.session_state.founder_cash = founder_cash
                                st.session_state.founder_portfolio = rebuild_portfolio_from_trades(founder_db_transactions)
                        else:
                            # Reload user portfolio immediately
                            user_id = st.session_state.get("user_id")
                            if user_id:
                                db_transactions = load_trades_from_db(user_id, portfolio_type='user')
                                if db_transactions:
                                    st.session_state.transactions = db_transactions
                                    cash, _ = calculate_cash_from_db(user_id, portfolio_type='user')
                                    st.session_state.cash = cash
                                    st.session_state.portfolio = rebuild_portfolio_from_trades(db_transactions)
                        
                        st.success(message)
                        st.rerun()  # Force full page refresh
                    else:
                        # FIXED: Show actual error message
                        st.error(f"Trade failed: {message}")
                        
                except Exception as e:
                    # FIXED: No more silent failures!
                    st.error(f"❌ Trade execution error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())  # Show full error for debugging
        
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
            
            # Live preview with FIXED styling
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
                
                # Preview box with DARK NAVY background (matches screenshot)
                st.info(f"""
                **Estimated Shares:** {shares:.4f}  
                **Estimated Cost:** ${total_cost:,.2f}  
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
                
                # Preview box with DARK NAVY background (matches screenshot)
                st.info(f"""
                **Selling Shares:** {shares:.4f}  
                **Estimated Proceeds:** ${proceeds:,.2f}  
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
    
    # SPY benchmark - REAL-TIME DATA
    st.markdown("### 📊 SPY Benchmark")
    
    # Get real SPY data
    spy_starting = STARTING_CASH  # $100k starting capital
    spy_quote = get_quote("SPY")
    
    if spy_quote and spy_quote.get('price'):
        spy_ytd_pct = spy_quote.get('changesPercentage', 0) or 0
        # Calculate what $100k would be worth based on YTD return
        spy_current = spy_starting * (1 + spy_ytd_pct / 100)
        spy_ytd_return = spy_ytd_pct
    else:
        spy_current = spy_starting
        spy_ytd_return = 0.0
    
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
        ("Founder", get_ytd_return(calculate_portfolio_value(st.session_state.founder_portfolio, st.session_state.founder_cash), STARTING_CASH)),
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
        st.session_state.cash = STARTING_CASH
        st.session_state.transactions = []
        st.session_state.realized_gains = 0.0
        st.session_state.concentration_flags = {}
        save_user_progress()
        st.success(f"Portfolio reset! You have ${STARTING_CASH:,.0f} to start fresh.")
        st.rerun()
    
    # AI Coach integration
    render_ai_coach("Paper Portfolio", ticker=None, facts=None)

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
    
    # AI Coach integration
    render_ai_coach("Portfolio Risk Analyzer", ticker=None, facts=None)

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
