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
        y_range_max = max_val * 1.2 if max_val > 0 else max_val * 0.8
        y_range_min = min_val * 0.9 if min_val < 0 else 0
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Company Analysis",
    "🎯 Sector Explorer",
    "📈 Portfolio Risk Analyzer",
    "✅ Investment Checklist",
    "📚 Finance 101",
    "🎯 Risk Quiz",
    "💼 Paper Portfolio"
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
        "📉 Technical Analysis", 
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
        
        st.markdown("---")
        
        st.markdown("### 📊 Growth Metrics")
        
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
        
        st.markdown("---")
        
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
                   help="Free Cash Flow divided by shares outstanding")

        # Market Benchmarks & Investment Calculator - Compact Right Column
        # Create tight 2-column layout (no divider for same-level alignment)
        col_left_main, col_right_widgets = st.columns([2, 1.2], gap="small")
        
        with col_right_widgets:
            st.markdown("### 📊 Benchmarks")
            # S&P 500 YTD
            sp500_quote = get_quote("^GSPC")
            if sp500_quote:
                sp500_ytd = sp500_quote.get('changesPercentage', 0)
                st.metric("S&P 500 YTD", f"{sp500_ytd:+.1f}%")
            
            # Current stock YTD
            stock_quote = get_quote(ticker)
            if stock_quote:
                stock_ytd = stock_quote.get('changesPercentage', 0)
                st.metric(f"{ticker} YTD", f"{stock_ytd:+.1f}%")
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
            # Stock Price Chart
            st.markdown(f"### {company_name} Stock Price")
            price_history = get_historical_price(ticker, years)
            
            if not price_history.empty:
                fig_price = go.Figure()
                fig_price.add_trace(go.Scatter(
                    x=price_history['date'],
                    y=price_history['price'],
                    mode='lines',
                    name='Price',
                    line=dict(color='#9D4EDD', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(157, 78, 221, 0.2)'
                ))
                
                fig_price.update_layout(
                    title=f"{ticker} Price History",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=350,
                    margin=dict(l=0, r=0, t=40, b=0),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_price, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 💰 Investment Calculator")
            st.caption("See what your investment would be worth")
            
            col_calc1, col_calc2 = st.columns(2)
            with col_calc1:
                invest_initial = st.number_input("💵 Lump Sum ($)", min_value=1, value=100, step=50, key="calc_lump")
            with col_calc2:
                invest_dca = st.number_input("📅 Bi-Weekly DCA ($)", min_value=0, value=100, step=25, key="calc_dca")
            
            calc_years = years
            price_hist = get_historical_price(ticker, calc_years)
            
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
                    
                    with st.expander(f"💵 Lump Sum: ${invest_initial} → {ticker}", expanded=True):
                        st.metric("Current Value", f"${stock_lump:,.2f}", f"{stock_lump_ret:+.1f}%")
                        st.caption(f"Bought {invest_initial/start_price:.2f} shares @ ${start_price:.2f}")
                    
                    with st.expander(f"📅 DCA: ${invest_dca} bi-weekly → {ticker}", expanded=True):
                        st.metric("Current Value", f"${stock_dca:,.2f}", f"{stock_dca_ret:+.1f}%")
                        st.caption(f"Total invested: ${total_inv:,.2f} over {calc_years} years")
                    
                    st.markdown("### vs S&P 500")
                    
                    sp_data = get_historical_price("SPY", calc_years)
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
                            
                            with st.expander(f"💵 Lump Sum: ${invest_initial} → S&P 500", expanded=True):
                                st.metric("Current Value", f"${sp_lump:,.2f}", f"{sp_lump_ret:+.1f}%")
                                st.caption("S&P 500 (SPY)")
                            
                            with st.expander(f"📅 DCA: ${invest_dca} bi-weekly → S&P 500", expanded=True):
                                st.metric("Current Value", f"${sp_dca_val:,.2f}", f"{sp_dca_ret:+.1f}%")
                                st.caption(f"Total invested: ${total_inv:,.2f}")
                            
                            if stock_lump > sp_lump:
                                st.success(f"✅ Lump sum: {ticker} outperformed S&P 500 by ${stock_lump - sp_lump:,.2f} (+{stock_lump_ret - sp_lump_ret:.1f}%)")
                            else:
                                st.info(f"📊 Lump sum: S&P 500 outperformed {ticker} by ${sp_lump - stock_lump:,.2f} (+{sp_lump_ret - stock_lump_ret:.1f}%)")
                            
                            if stock_dca > sp_dca_val:
                                st.success(f"✅ DCA: {ticker} outperformed S&P 500 by ${stock_dca - sp_dca_val:,.2f} (+{stock_dca_ret - sp_dca_ret:.1f}%)")
                            else:
                                st.info(f"📊 DCA: S&P 500 outperformed {ticker} by ${sp_dca_val - stock_dca:,.2f} (+{sp_dca_ret - stock_dca_ret:.1f}%)")

            
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
        
        st.markdown("---")
        
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

    elif view == "💰 Valuation (DCF)":
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

# ============= FOOTER =============
st.divider()
st.caption("💡 Finance Made Simple | FMP Premium | Real-time data")

# ============= TAB 6: RISK ANALYSIS QUIZ =============
with tab6:
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
                ("JNJ", "Johnson & Johnson", "Healthcare giant with 60+ years of dividend growth"),
                ("PG", "Procter & Gamble", "Consumer staples, recession-resistant")
            ]
        elif risk_score <= 20:
            profile = "Moderate"
            color = "🟡"
            description = "You want balanced growth with manageable risk. Mix of stable companies and growth stocks."
            stocks = [
                ("MSFT", "Microsoft", "Tech leader with strong fundamentals and growing dividends"),
                ("V", "Visa", "Payment processor with consistent growth")
            ]
        elif risk_score <= 30:
            profile = "Growth-Oriented"
            color = "🟠"
            description = "You're comfortable with volatility for higher returns. Focus on growth stocks and emerging sectors."
            stocks = [
                ("NVDA", "NVIDIA", "AI and chip leader with explosive growth potential"),
                ("GOOGL", "Alphabet", "Dominant in search, cloud, and AI")
            ]
        else:
            profile = "Aggressive"
            color = "🔴"
            description = "You're seeking maximum returns and can handle high volatility. High-growth and speculative plays."
            stocks = [
                ("TSLA", "Tesla", "EV leader with high growth but volatile"),
                ("COIN", "Coinbase", "Crypto exposure with high risk/reward")
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
        st.success("✨ **Try our Paper Portfolio!** Practice trading with $100,000 fake money before risking real capital. Build confidence, test strategies, track performance.")
        
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

st.caption("⚠️ Educational purposes only. Not financial advice.")


# ============= TAB 7: PAPER PORTFOLIO TRACKER =============
with tab7:
    st.header("💼 Paper Portfolio Tracker")
    st.markdown("**Practice trading with fake money! Track your performance without any risk.**")
    st.caption("⚠️ Simulated trading for educational purposes only. Does not reflect real trading costs, slippage, or market conditions.")
    
    # Initialize session state for portfolio
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'cash' not in st.session_state:
        st.session_state.cash = 100000.0  # Start with $100k
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
                 f"{(total_gain_loss / 100000 * 100):+.2f}%")
        
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
        st.session_state.cash = 100000.0
        st.session_state.transactions = []
        st.success("✅ Portfolio reset! You have $100,000 to start fresh.")
        st.rerun()


# ============= FOOTER DISCLAIMER =============
st.divider()
st.markdown("---")
st.caption("""
**Disclaimer:** Finance Made Simple | FMP Premium | Real-time data  

⚠️ **IMPORTANT LEGAL DISCLAIMER:**  
This application and all content provided herein are for **educational and informational purposes ONLY**. Nothing on this platform constitutes financial advice, investment advice, trading advice, legal advice, tax advice, or any other sort of advice. You should not treat any of the app's content as a recommendation to buy, sell, or hold any security or investment.

**No Warranty:** The information is provided "as-is" without warranty of any kind. We do not guarantee the accuracy, completeness, or timeliness of any information presented.

**Investment Risks:** All investments involve risk, including the potential loss of principal. Past performance does not guarantee future results. Securities trading and investing involve substantial risk of loss.

**Not Professional Advice:** We are not registered financial advisors, brokers, or investment professionals. Always consult with qualified financial, legal, and tax professionals before making any investment decisions.

**Data Sources:** Data is sourced from Financial Modeling Prep API. We are not responsible for data accuracy or API availability.

**Paper Portfolio:** The paper portfolio feature is for educational simulation only. Results do not represent actual trading and do not reflect real market conditions, fees, or slippage.

**Your Responsibility:** You are solely responsible for your own investment decisions and their outcomes. By using this app, you acknowledge and accept these terms.

© 2024 Finance Made Simple. All rights reserved.
""")
