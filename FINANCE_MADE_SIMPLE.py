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
FMP_API_KEY = "9rZXN8pHaPyiCjFHWCVBxQmyzftJbRrj"
BASE_URL = "https://financialmodelingprep.com/stable"

# AI Configuration (set to True when you get Perplexity API key)
USE_AI_ANALYSIS = False
PERPLEXITY_API_KEY = ""  # Add your key here when ready

st.set_page_config(page_title="Finance Made Simple", layout="wide", page_icon="💰")

# ============= DARK/LIGHT MODE =============
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# ============= THEME STYLING =============
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    h1, h2, h3 { color: white !important; }
    .stMetric { background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; }
    .why-box { 
        background: rgba(255,255,255,0.1); 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #00D9FF;
        margin: 10px 0;
    }
    .personal-budget {
        background: rgba(255,215,0,0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
    }
    .risk-warning {
        background: rgba(255,0,0,0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF0000;
    }
    .risk-good {
        background: rgba(0,255,0,0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00FF00;
    }
    .roast-box {
        background: rgba(255,100,100,0.2);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FF6B6B;
        margin: 15px 0;
        font-size: 1.1em;
    }
    .metric-explain {
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        font-size: 0.9em;
        border-left: 3px solid #00D9FF;
    }
    .sector-info {
        background: rgba(255,215,0,0.15);
        padding: 8px;
        border-radius: 6px;
        margin: 3px 0;
        font-size: 0.85em;
        border-left: 3px solid #FFD700;
    }
    .growth-note {
        background: rgba(0,255,150,0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00FF96;
        margin: 10px 0;
        font-size: 1em;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    h1, h2, h3 { color: #1e1e1e !important; }
    .stMetric { background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .why-box { 
        background: rgba(255,255,255,0.9); 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #00D9FF;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .personal-budget {
        background: rgba(255,235,180,0.9);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-warning {
        background: rgba(255,200,200,0.9);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF0000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-good {
        background: rgba(200,255,200,0.9);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00FF00;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .roast-box {
        background: rgba(255,220,220,0.9);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FF6B6B;
        margin: 15px 0;
        font-size: 1.1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .metric-explain {
        background: rgba(240,248,255,0.95);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        font-size: 0.9em;
        border-left: 3px solid #00D9FF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .sector-info {
        background: rgba(255,250,205,0.95);
        padding: 8px;
        border-radius: 6px;
        margin: 3px 0;
        font-size: 0.85em;
        border-left: 3px solid #FFD700;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .growth-note {
        background: rgba(200,255,220,0.95);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00DD88;
        margin: 10px 0;
        font-size: 1em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    p, div, span, li { color: #1e1e1e !important; }
    </style>
    """, unsafe_allow_html=True)

# ============= METRIC EXPLANATIONS (FOR TOOLTIPS) =============
METRIC_EXPLANATIONS = {
    "P/E Ratio": {
        "short": "Price divided by Earnings (TTM)",
        "explanation": "How much you pay for $1 of earnings. Lower = cheaper. Tech average: 25 | Value stocks: 15",
        "good": "15-25 is reasonable | >40 is expensive | <10 might be undervalued or troubled"
    },
    "P/S Ratio": {
        "short": "Price divided by Sales",
        "explanation": "How much you pay for $1 of revenue. Useful when company isn't profitable yet.",
        "good": "Tech: 5-10 | Retail: 0.5-2 | Lower = better value"
    },
    "Debt-to-Equity": {
        "short": "Total Debt ÷ Shareholder Equity",
        "explanation": "Measures financial leverage. High debt = risky during recessions.",
        "good": "<1.0 = Low debt (good) | 1-2 = Moderate | >2.0 = High risk"
    },
    "Quick Ratio": {
        "short": "(Current Assets - Inventory) ÷ Current Liabilities",
        "explanation": "Can the company pay short-term bills without selling inventory?",
        "good": ">1.5 = Excellent liquidity | 1.0-1.5 = Good | <1.0 = Potential cash problems"
    },
    "FCF per Share": {
        "short": "Free Cash Flow ÷ Shares Outstanding",
        "explanation": "Real cash generated per share you own. Unlike earnings, FCF can't be manipulated easily.",
        "good": "Positive = good | Growing FCF/share = excellent | Negative = burning cash"
    },
    "Market Cap": {
        "short": "Total value of all shares",
        "explanation": "Stock price × shares outstanding. Shows company size.",
        "good": ">$200B = Mega cap | $10-200B = Large cap | <$2B = Small cap (risky)"
    },
    "Beta": {
        "short": "Stock volatility vs S&P 500",
        "explanation": "Measures how much stock moves relative to market.",
        "good": "<0.8 = Defensive | 1.0 = Moves with market | >1.3 = High volatility"
    }
}

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
    """
    Create a financial chart with proper y-axis padding and return growth rates for each metric
    """
    if df.empty:
        return None, {}
    
    # Reverse dataframe to show oldest to newest (left to right)
    df_reversed = df.iloc[::-1].reset_index(drop=True)
    
    # Create figure
    fig = go.Figure()
    
    # Color scheme
    colors = ['#00D9FF', '#FFD700', '#9D4EDD']
    
    growth_rates = {}
    
    # Add traces for each metric
    for idx, metric in enumerate(metrics):
        if metric in df_reversed.columns:
            values = df_reversed[metric].values
            
            # Calculate growth rate
            if len(values) >= 2 and values[0] != 0:
                growth_rate = ((values[-1] - values[0]) / abs(values[0])) * 100
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
    
    # Calculate y-axis range with 20% padding above the max value
    all_values = []
    for metric in metrics:
        if metric in df_reversed.columns:
            all_values.extend(df_reversed[metric].values)
    
    if all_values:
        max_val = max(all_values)
        min_val = min(all_values)
        
        # Add 20% padding above max value
        y_range_max = max_val * 1.2 if max_val > 0 else max_val * 0.8
        y_range_min = min_val * 0.9 if min_val < 0 else 0
        
        fig.update_layout(
            yaxis=dict(range=[y_range_min, y_range_max])
        )
    
    fig.update_layout(
        title=title,
        xaxis_title=period_label,
        yaxis_title=yaxis_title,
        barmode='group',
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig, growth_rates

def create_ratio_trend_chart(df, metric_name, metric_column, title):
    """
    Create a line chart showing the trend of a financial ratio over time
    """
    if df.empty or metric_column not in df.columns:
        return None
    
    # Reverse to show oldest to newest
    df_reversed = df.iloc[::-1].reset_index(drop=True)
    
    # Convert ratio values to percentage if needed
    values = df_reversed[metric_column].values
    
    # Determine if we should show as percentage
    if 'margin' in metric_column.lower() or 'return' in metric_column.lower():
        values = values * 100
        y_suffix = '%'
    else:
        y_suffix = ''
    
    fig = go.Figure()
    
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
    
    # Calculate growth
    if len(values) >= 2 and values[0] != 0:
        growth = ((values[-1] - values[0]) / abs(values[0])) * 100
        
        # Add annotation showing growth
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
        hovermode='x unified'
    )
    
    return fig

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

@st.cache_data(ttl=1800)
def get_stock_specific_news(ticker, limit=10):
    """Get STOCK-SPECIFIC news - FIXED"""
    url = f"{BASE_URL}/stock_news?tickers={ticker}&limit={limit}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            filtered = []
            for article in data:
                title = article.get('title', '').upper()
                text = article.get('text', '').upper()
                symbol = article.get('symbol', '').upper()
                
                if ticker.upper() in title or ticker.upper() in text or symbol == ticker.upper():
                    filtered.append(article)
            
            return filtered[:limit]
    except:
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
    st.session_state.selected_ticker = "AAPL"

# ============= HEADER =============
col1, col2, col3 = st.columns([4, 1, 1])
with col1:
    st.title("💰 Finance Made Simple")
    st.caption("AI-Powered Stock Analysis for Everyone")
with col2:
    st.markdown("### 🤖 AI-Ready")
    st.caption("FMP Premium")
with col3:
    if st.button("🌓 Toggle Theme"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

# ============= TABS =============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Company Analysis",
    "🎯 Sector Explorer",
    "📈 Portfolio Risk Analyzer",
    "✅ Investment Checklist",
    "📚 Finance 101"
])

# ============= TAB 2: SECTOR EXPLORER (WITH TOOLTIPS) =============
with tab2:
    st.header("🎯 Sector Explorer")
    
    selected_sector = st.selectbox("Choose sector:", list(SECTORS.keys()))
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

# ============= TAB 3: PORTFOLIO RISK ANALYZER =============
with tab3:
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
                    
                    st.divider()
                    
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
                    
                    st.divider()
                    
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
                    
                    st.divider()
                    
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
                    
                    st.divider()
                    
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
                    
                    st.divider()
                    
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
                    
                    st.divider()
                    
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
                    
                    st.divider()
                    
                    st.markdown("### 📊 Detailed Breakdown")
                    detail_df = df[['ticker', 'name', 'allocation', 'sector', 'beta', 'pe', 'de_ratio', 'quick_ratio', 'risk_score']].copy()
                    detail_df.columns = ['Ticker', 'Company', 'Allocation %', 'Sector', 'Beta', 'P/E', 'Debt/Equity', 'Quick Ratio', 'Risk Score']
                    st.dataframe(detail_df, use_container_width=True)
                    
                    st.divider()
                    
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

# ============= TAB 4: INVESTMENT CHECKLIST =============
with tab4:
    st.header("✅ Investment Checklist")
    st.write("Quick check before investing")
    
    ticker_check = st.text_input("Enter ticker:", value=st.session_state.selected_ticker, key="checklist_ticker")
    
    if st.button("Analyze", key="checklist_analyze"):
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
            
            st.divider()
            st.metric("Score", f"{passed_count}/{total}")
            
            if passed_count >= total * 0.75:
                st.success("🎉 Strong candidate!")
            elif passed_count >= total * 0.5:
                st.info("🤔 Mixed signals")
            else:
                st.error("🚨 Many red flags")

# ============= TAB 5: FINANCE 101 =============
with tab5:
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

# ============= TAB 1: COMPANY ANALYSIS - PART 1 (HEADER + SIDEBAR) =============
with tab1:
    search = st.text_input(
        "🔍 Search by Company Name or Ticker:",
        st.session_state.selected_ticker,
        help="Try: Apple, AAPL, Microsoft, TSLA, etc."
    )
    
    if search:
        ticker, company_name = smart_search_ticker(search)
        st.session_state.selected_ticker = ticker
        if ticker != search.upper():
            st.success(f"✅ Found: {company_name} ({ticker})")
    else:
        ticker = st.session_state.selected_ticker
    
    profile = get_profile(ticker)
    if profile:
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
    
    view = st.radio("Choose View:", [
        "📊 Key Metrics", 
        "🔀 Compare 2 Stocks",
        "📈 Financial Ratios", 
        "💰 Valuation (DCF)", 
        "📰 Latest News"
    ], horizontal=True)
    
    income_df = get_income_statement(ticker, 'annual', 5)
    cash_df = get_cash_flow(ticker, 'annual', 5)
    balance_df = get_balance_sheet(ticker, 'annual', 5)
    ratios_df = get_financial_ratios(ticker, 'annual', 5)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        period_type = st.radio("Time Period:", ["Annual", "Quarterly"])
        period = 'annual' if period_type == "Annual" else 'quarter'
        years = st.slider("Years of History:", 1, 30, 5)
        
        st.divider()
        
        st.markdown("### 📊 Market Benchmarks")
        
        treasury_rates = get_treasury_rates()
        sp500_ytd = get_sp500_performance()
        
        if treasury_rates.get('10Y', 0) > 0:
            st.metric("🏦 10Y Treasury (Risk-Free)", f"{treasury_rates['10Y']:.2f}%",
                     help="10-year US Treasury yield - the 'risk-free' rate investors use as baseline")
        
        if sp500_ytd != 0:
            st.metric("📈 S&P 500 YTD", f"{sp500_ytd:+.1f}%",
                     help="S&P 500 year-to-date return - benchmark for US stock market")
        
        price_data_ytd = get_historical_price(ticker, 1)
        if not price_data_ytd.empty and len(price_data_ytd) > 1:
            try:
                current_year = datetime.now().year
                price_data_ytd['year'] = pd.to_datetime(price_data_ytd['date']).dt.year
                ytd_data = price_data_ytd[price_data_ytd['year'] == current_year]
                
                if len(ytd_data) > 1:
                    price_col = 'close' if 'close' in ytd_data.columns else 'price'
                    
                    start_price = ytd_data[price_col].iloc[0]
                    latest_price = ytd_data[price_col].iloc[-1]
                    
                    if start_price > 0:
                        stock_ytd = ((latest_price - start_price) / start_price) * 100
                        st.metric(f"🎯 {ticker} YTD", f"{stock_ytd:+.1f}%",
                                 help=f"{ticker} year-to-date return")
            except:
                pass
        
        st.divider()
        
        st.markdown("### 📈 Growth Metrics")
        
        if not income_df.empty:
            revenue_cagr = calculate_growth_rate(income_df, 'revenue', years)
            if revenue_cagr:
                st.metric("Revenue CAGR", f"{revenue_cagr:+.1f}%",
                         help=f"Compound Annual Growth Rate over {years} years")
            
            if 'netIncome' in income_df.columns:
                profit_cagr = calculate_growth_rate(income_df, 'netIncome', years)
                if profit_cagr:
                    st.metric("Profit CAGR", f"{profit_cagr:+.1f}%",
                             help=f"Net income growth rate over {years} years")
        
        if not cash_df.empty and 'freeCashFlow' in cash_df.columns:
            fcf_cagr = calculate_growth_rate(cash_df, 'freeCashFlow', years)
            if fcf_cagr:
                st.metric("FCF CAGR", f"{fcf_cagr:+.1f}%",
                         help=f"Free cash flow growth rate over {years} years")
        
        price_data = get_historical_price(ticker, years)
        if not price_data.empty and len(price_data) > 1 and 'price' in price_data.columns:
            start_price = price_data['price'].iloc[0]
            end_price = price_data['price'].iloc[-1]
            price_growth = ((end_price - start_price) / start_price) * 100
            st.metric(f"Stock Growth ({years}Y)", f"{price_growth:+.1f}%",
                     help=f"Total stock price return over {years} years")
        
        st.divider()
        
        st.markdown("### ⚠️ Risk Indicators")
        
        de_ratio = calculate_debt_to_equity(balance_df)
        if de_ratio > 0:
            if de_ratio > 2.0:
                st.error(f"D/E: {de_ratio:.2f} 🔴")
                st.caption("High debt risk")
            elif de_ratio > 1.0:
                st.warning(f"D/E: {de_ratio:.2f} 🟡")
                st.caption("Moderate debt")
            else:
                st.success(f"D/E: {de_ratio:.2f} 🟢")
                st.caption("Low debt")
        
        qr = calculate_quick_ratio(balance_df)
        if qr > 0:
            if qr < 1.0:
                st.warning(f"Quick Ratio: {qr:.2f} 🟡")
                st.caption("Low liquidity")
            else:
                st.success(f"Quick Ratio: {qr:.2f} 🟢")
                st.caption("Good liquidity")


    quote = get_quote(ticker)
    ratios_ttm = get_ratios_ttm(ticker)
    
    if quote:
        price = quote.get('price', 0)
        change_pct = quote.get('changesPercentage', 0)
        market_cap = quote.get('marketCap', 0)
        
        pe = get_pe_ratio(ticker, quote, ratios_ttm, income_df)
        ps = get_ps_ratio(ticker, ratios_ttm)
        fcf_per_share = calculate_fcf_per_share(ticker, cash_df, quote)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Current Price", f"${price:.2f}", f"{change_pct:+.2f}%")
        col2.metric("Market Cap", format_number(market_cap),
                   help=explain_metric("Market Cap", market_cap, sector))
        
        col3.metric("P/E Ratio (TTM)", f"{pe:.2f}" if pe > 0 else "N/A",
                   help=explain_metric("P/E Ratio", pe, sector))
        
        col4.metric("P/S Ratio", f"{ps:.2f}" if ps > 0 else "N/A",
                   help=explain_metric("P/S Ratio", ps, sector))
        
        col5.metric("FCF Per Share", f"${fcf_per_share:.2f}" if fcf_per_share > 0 else "N/A",
                   help=explain_metric("FCF per Share", fcf_per_share, sector))
        
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
        
        st.divider()
    
    # ============= TAB 1 VIEWS START HERE =============
    
    if view == "📊 Key Metrics":
        
        income_df = get_income_statement(ticker, period, years*4 if period == 'quarter' else years)
        cash_df = get_cash_flow(ticker, period, years*4 if period == 'quarter' else years)
        balance_df = get_balance_sheet(ticker, period, years*4 if period == 'quarter' else years)
        
        st.markdown(f"### 📈 {company_name} - Stock Price ({years} Years)")
        price_data = get_historical_price(ticker, years)
        if not price_data.empty and 'price' in price_data.columns:
            
            fig = px.area(price_data, x='date', y='price', 
                         title=f'{company_name} Stock Price')
            fig.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis_title="",
                yaxis_title="Price ($)",
                showlegend=False,
                margin=dict(l=20, r=20, t=60, b=20),
                hoverlabel=dict(bgcolor="white", font_size=12, font_color="black")
            )
            fig.update_traces(fillcolor='rgba(157, 78, 221, 0.3)', line_color='#9D4EDD', line_width=2)
            fig.update_yaxes(rangemode='tozero')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Stock price data not available")
        
        st.divider()
        
        st.markdown(f"### 💵 {company_name} - Cash Flow Statement")
        show_why_it_matters('fcfAfterSBC')
        
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
                metric_names = [metric1_display, metric2_display, metric3_display]
                
                plot_df = cash_df[['date'] + metrics_to_plot].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y-%m' if period == 'quarter' else '%Y')
                
                fig = go.Figure()
                colors = ['#9D4EDD', '#00D9FF', '#FF69B4']
                
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    fig.add_trace(go.Bar(
                        x=plot_df['date'],
                        y=plot_df[metric],
                        name=name,
                        marker_color=colors[i % len(colors)]
                    ))
                
                fig.update_layout(
                    title=f"{company_name} - Cash Flow",
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="Period",
                    yaxis_title="Amount ($)",
                    margin=dict(l=20, r=20, t=60, b=20),
                    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig.update_yaxes(rangemode='tozero')
                st.plotly_chart(fig, use_container_width=True)
                
                cols = st.columns(len(metrics_to_plot))
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    cols[i].metric(f"Latest {name}", format_number(cash_df[metric].iloc[-1]))
        else:
            st.warning("⚠️ Cash flow data not available")
        
        st.divider()
        
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
                metric_names = [metric1_display, metric2_display, metric3_display]
                
                plot_df = income_df[['date'] + metrics_to_plot].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y-%m' if period == 'quarter' else '%Y')
                
                fig = go.Figure()
                colors = ['#00D9FF', '#FFD700', '#9D4EDD']
                
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    fig.add_trace(go.Bar(
                        x=plot_df['date'],
                        y=plot_df[metric],
                        name=name,
                        marker_color=colors[i % len(colors)]
                    ))
                
                fig.update_layout(
                    title=f"{company_name} - Income Statement",
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="Period",
                    yaxis_title="Amount ($)",
                    margin=dict(l=20, r=20, t=60, b=20),
                    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig.update_yaxes(rangemode='tozero')
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                cols = [col1, col2, col3]
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    cols[i].metric(f"Latest {name}", format_number(income_df[metric].iloc[-1]))
        else:
            st.warning("⚠️ Income statement not available")
        
        st.divider()
        
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
                metric_names = [metric1_display, metric2_display, metric3_display]
                
                plot_df = balance_df[['date'] + metrics_to_plot].copy()
                plot_df['date'] = plot_df['date'].dt.strftime('%Y-%m' if period == 'quarter' else '%Y')
                
                fig = go.Figure()
                colors = ['#00D9FF', '#FF6B6B', '#FFD700']
                
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    fig.add_trace(go.Bar(
                        x=plot_df['date'],
                        y=plot_df[metric],
                        name=name,
                        marker_color=colors[i % len(colors)]
                    ))
                
                fig.update_layout(
                    title=f"{company_name} - Balance Sheet",
                    height=400,
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="Period",
                    yaxis_title="Amount ($)",
                    margin=dict(l=20, r=20, t=60, b=20),
                    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig.update_yaxes(rangemode='tozero')
                st.plotly_chart(fig, use_container_width=True)
                
                cols = st.columns(len(metrics_to_plot))
                for i, (metric, name) in enumerate(zip(metrics_to_plot, metric_names)):
                    cols[i].metric(f"Latest {name}", format_number(balance_df[metric].iloc[-1]))
        else:
            st.warning("⚠️ Balance sheet not available")
    
    elif view == "🔀 Compare 2 Stocks":
        st.markdown("## 🔀 Compare 2 Stocks")
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
                
                st.divider()
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
                
                st.divider()
                
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
                
                st.divider()
                
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
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            ratio_period = st.radio("Period", ["Annual", "Quarterly"], key="ratio_period_select")
                        
                        with col2:
                            ratio_years = st.slider("Years of History", 1, 30, 5, key="ratio_years_select")
                        
                        # Fetch ratios data
                        period_param = "annual" if ratio_period == "Annual" else "quarter"
                        ratios_url = f"{BASE_URL}/ratios/{ticker}?period={period_param}&limit={ratio_years}&apikey={FMP_API_KEY}"
                        
                        try:
                            response = requests.get(ratios_url, timeout=10)
                            response.raise_for_status()
                            ratios_data = response.json()
                            ratios_df_fetched = pd.DataFrame(ratios_data)
                            
                            if not ratios_df_fetched.empty:
                                st.markdown("### 📊 Current Ratios")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if 'grossProfitMargin' in ratios_df_fetched.columns:
                                        latest = ratios_df_fetched['grossProfitMargin'].iloc[0] * 100
                                        st.metric("Gross Margin", f"{latest:.1f}%",
                                                 help="Revenue minus cost of goods sold, divided by revenue")
                                
                                with col2:
                                    if 'operatingProfitMargin' in ratios_df_fetched.columns:
                                        latest = ratios_df_fetched['operatingProfitMargin'].iloc[0] * 100
                                        st.metric("Operating Margin", f"{latest:.1f}%",
                                                 help="Operating income divided by revenue - shows efficiency")
                                
                                with col3:
                                    if 'netProfitMargin' in ratios_df_fetched.columns:
                                        latest = ratios_df_fetched['netProfitMargin'].iloc[0] * 100
                                        st.metric("Net Margin", f"{latest:.1f}%",
                                                 help="Net income divided by revenue - bottom line profitability")
                                
                                st.divider()
                                
                                # Profitability Trends
                                st.markdown("### 💰 Profitability Trends")
                                
                                profitability_metrics = [
                                    ('Gross Profit Margin', 'grossProfitMargin'),
                                    ('Operating Profit Margin', 'operatingProfitMargin'),
                                    ('Net Profit Margin', 'netProfitMargin')
                                ]
                                
                                for metric_name, metric_col in profitability_metrics:
                                    if metric_col in ratios_df_fetched.columns:
                                        fig = create_ratio_trend_chart(ratios_df_fetched, metric_name, metric_col, 
                                                                       f"{company_name} - {metric_name}")
                                        if fig:
                                            st.plotly_chart(fig, use_container_width=True)
                                
                                st.divider()
                                
                                # Efficiency Trends
                                st.markdown("### ⚡ Efficiency Trends")
                                
                                efficiency_metrics = [
                                    ('Return on Equity (ROE)', 'returnOnEquity'),
                                    ('Return on Assets (ROA)', 'returnOnAssets'),
                                    ('Return on Capital Employed', 'returnOnCapitalEmployed')
                                ]
                                
                                for metric_name, metric_col in efficiency_metrics:
                                    if metric_col in ratios_df_fetched.columns:
                                        fig = create_ratio_trend_chart(ratios_df_fetched, metric_name, metric_col,
                                                                       f"{company_name} - {metric_name}")
                                        if fig:
                                            st.plotly_chart(fig, use_container_width=True)
                                
                                st.divider()
                                
                                # Liquidity & Leverage Trends
                                st.markdown("### 🏦 Liquidity & Leverage Trends")
                                
                                financial_health_metrics = [
                                    ('Current Ratio', 'currentRatio'),
                                    ('Quick Ratio', 'quickRatio'),
                                    ('Debt to Equity', 'debtToEquity')
                                ]
                                
                                for metric_name, metric_col in financial_health_metrics:
                                    if metric_col in ratios_df_fetched.columns:
                                        fig = create_ratio_trend_chart(ratios_df_fetched, metric_name, metric_col,
                                                                       f"{company_name} - {metric_name}")
                                        if fig:
                                            st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("Ratio data not available for the selected period")
                        except Exception as e:
                            st.error(f"Could not fetch ratio data: {str(e)}")
                        
                    elif view == "💰 Valuation (DCF)":
        st.markdown("## 💰 DCF Valuation")
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

# ============= FOOTER =============
st.divider()
st.caption("💡 Finance Made Simple | FMP Premium | Real-time data")
st.caption("⚠️ Educational purposes only. Not financial advice.")
