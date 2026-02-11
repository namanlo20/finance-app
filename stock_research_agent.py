"""
Stock Research AI Agent - Starter Template
==========================================
An AI agent that autonomously researches stocks using OpenAI function calling + FMP API.
Built for integration into Investing Made Simple (aistockinvesting101.com).

Setup:
    pip install openai requests
    
    Set environment variables:
        OPENAI_API_KEY=your_openai_key
        FMP_API_KEY=your_fmp_key

Usage:
    python stock_research_agent.py
    
    Or import and use in your Streamlit app:
        from stock_research_agent import StockResearchAgent
        agent = StockResearchAgent()
        result = agent.research("Is NVDA overvalued?")
"""

import os
import json
import requests
from datetime import datetime, timedelta
from openai import OpenAI

# ============================================================
# CONFIG - Replace with your keys or use environment variables
# ============================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key-here")
FMP_API_KEY = os.getenv("FMP_API_KEY", "your-fmp-key-here")
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# OpenAI model - gpt-4o is best for function calling, gpt-3.5-turbo is cheaper
MODEL = "gpt-4o"

client = OpenAI(api_key=OPENAI_API_KEY)


# ============================================================
# TOOLS - These are the functions the AI agent can call
# ============================================================

def get_stock_quote(ticker: str) -> dict:
    """Get current stock price, change, volume, market cap."""
    try:
        url = f"{FMP_BASE_URL}/quote/{ticker.upper()}?apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data:
            return {"error": f"No data found for {ticker}"}
        q = data[0]
        return {
            "ticker": q.get("symbol"),
            "name": q.get("name"),
            "price": q.get("price"),
            "change_pct": round(q.get("changesPercentage", 0), 2),
            "day_high": q.get("dayHigh"),
            "day_low": q.get("dayLow"),
            "volume": q.get("volume"),
            "market_cap": q.get("marketCap"),
            "pe_ratio": q.get("pe"),
            "year_high": q.get("yearHigh"),
            "year_low": q.get("yearLow"),
            "avg_volume": q.get("avgVolume"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_financial_ratios(ticker: str) -> dict:
    """Get key financial ratios: P/E, P/B, ROE, debt/equity, margins."""
    try:
        url = f"{FMP_BASE_URL}/ratios-ttm/{ticker.upper()}?apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data:
            return {"error": f"No ratios found for {ticker}"}
        r = data[0]
        return {
            "ticker": ticker.upper(),
            "pe_ratio_ttm": round(r.get("peRatioTTM", 0), 2),
            "pb_ratio_ttm": round(r.get("priceToBookRatioTTM", 0), 2),
            "ps_ratio_ttm": round(r.get("priceToSalesRatioTTM", 0), 2),
            "roe_ttm": round(r.get("returnOnEquityTTM", 0) * 100, 2),
            "roa_ttm": round(r.get("returnOnAssetsTTM", 0) * 100, 2),
            "debt_to_equity": round(r.get("debtEquityRatioTTM", 0), 2),
            "current_ratio": round(r.get("currentRatioTTM", 0), 2),
            "gross_margin": round(r.get("grossProfitMarginTTM", 0) * 100, 2),
            "net_margin": round(r.get("netProfitMarginTTM", 0) * 100, 2),
            "dividend_yield": round(r.get("dividendYieldTTM", 0) * 100, 2),
        }
    except Exception as e:
        return {"error": str(e)}


def get_income_statement(ticker: str, period: str = "annual", limit: int = 4) -> dict:
    """Get income statement data: revenue, earnings, growth trends."""
    try:
        url = f"{FMP_BASE_URL}/income-statement/{ticker.upper()}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data:
            return {"error": f"No income data for {ticker}"}
        
        results = []
        for stmt in data:
            results.append({
                "date": stmt.get("date"),
                "revenue": stmt.get("revenue"),
                "gross_profit": stmt.get("grossProfit"),
                "operating_income": stmt.get("operatingIncome"),
                "net_income": stmt.get("netIncome"),
                "eps": stmt.get("eps"),
                "revenue_growth": round(stmt.get("revenueGrowth", 0) if stmt.get("revenueGrowth") else 0, 4),
            })
        
        # Calculate YoY growth if we have multiple periods
        if len(results) >= 2:
            latest_rev = results[0]["revenue"]
            prev_rev = results[1]["revenue"]
            if prev_rev and prev_rev > 0:
                results[0]["yoy_revenue_growth_pct"] = round((latest_rev - prev_rev) / prev_rev * 100, 2)
        
        return {"ticker": ticker.upper(), "period": period, "statements": results}
    except Exception as e:
        return {"error": str(e)}


def get_company_profile(ticker: str) -> dict:
    """Get company description, sector, industry, CEO, employees."""
    try:
        url = f"{FMP_BASE_URL}/profile/{ticker.upper()}?apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data:
            return {"error": f"No profile found for {ticker}"}
        p = data[0]
        return {
            "ticker": p.get("symbol"),
            "name": p.get("companyName"),
            "description": p.get("description", "")[:500],  # Truncate to save tokens
            "sector": p.get("sector"),
            "industry": p.get("industry"),
            "ceo": p.get("ceo"),
            "employees": p.get("fullTimeEmployees"),
            "country": p.get("country"),
            "exchange": p.get("exchangeShortName"),
            "ipo_date": p.get("ipoDate"),
            "website": p.get("website"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_stock_news(ticker: str, limit: int = 5) -> dict:
    """Get latest news articles about a stock."""
    try:
        url = f"{FMP_BASE_URL}/stock_news?tickers={ticker.upper()}&limit={limit}&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data:
            return {"error": f"No news found for {ticker}"}
        
        articles = []
        for article in data[:limit]:
            articles.append({
                "title": article.get("title"),
                "source": article.get("site"),
                "date": article.get("publishedDate", "")[:10],
                "summary": article.get("text", "")[:200],
                "url": article.get("url"),
            })
        return {"ticker": ticker.upper(), "articles": articles}
    except Exception as e:
        return {"error": str(e)}


def get_analyst_estimates(ticker: str) -> dict:
    """Get analyst price targets and consensus estimates."""
    try:
        url = f"{FMP_BASE_URL}/analyst-estimates/{ticker.upper()}?limit=1&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        # Also get price target consensus
        url2 = f"{FMP_BASE_URL}/price-target-consensus/{ticker.upper()}?apikey={FMP_API_KEY}"
        resp2 = requests.get(url2, timeout=10)
        target_data = resp2.json()
        
        result = {"ticker": ticker.upper()}
        
        if data:
            est = data[0]
            result.update({
                "estimated_revenue_avg": est.get("estimatedRevenueAvg"),
                "estimated_eps_avg": est.get("estimatedEpsAvg"),
                "estimated_eps_high": est.get("estimatedEpsHigh"),
                "estimated_eps_low": est.get("estimatedEpsLow"),
            })
        
        if target_data:
            t = target_data[0]
            result.update({
                "target_high": t.get("targetHigh"),
                "target_low": t.get("targetLow"),
                "target_consensus": t.get("targetConsensus"),
                "target_median": t.get("targetMedian"),
            })
        
        return result
    except Exception as e:
        return {"error": str(e)}


def compare_stocks(tickers: list) -> dict:
    """Compare key metrics across multiple stocks (up to 5)."""
    try:
        comparisons = []
        for ticker in tickers[:5]:
            quote = get_stock_quote(ticker)
            ratios = get_financial_ratios(ticker)
            if "error" not in quote and "error" not in ratios:
                comparisons.append({
                    "ticker": ticker.upper(),
                    "price": quote.get("price"),
                    "market_cap": quote.get("market_cap"),
                    "pe_ratio": ratios.get("pe_ratio_ttm"),
                    "ps_ratio": ratios.get("ps_ratio_ttm"),
                    "roe": ratios.get("roe_ttm"),
                    "net_margin": ratios.get("net_margin"),
                    "debt_to_equity": ratios.get("debt_to_equity"),
                })
        return {"comparison": comparisons}
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# TOOL DEFINITIONS - This tells OpenAI what tools are available
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_quote",
            "description": "Get current stock price, daily change, volume, market cap, P/E ratio, and 52-week range. Use this for current pricing and basic market data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, NVDA, TSLA)"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_ratios",
            "description": "Get trailing twelve month financial ratios: P/E, P/B, P/S, ROE, ROA, margins, debt/equity, dividend yield. Use for valuation and financial health analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_income_statement",
            "description": "Get income statement data including revenue, earnings, EPS, and growth trends over multiple periods. Use for understanding revenue/earnings trajectory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "period": {"type": "string", "enum": ["annual", "quarter"], "description": "Annual or quarterly data"},
                    "limit": {"type": "integer", "description": "Number of periods to retrieve (default 4)"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_profile",
            "description": "Get company overview: description, sector, industry, CEO, employee count, IPO date. Use when you need context about what the company does.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_news",
            "description": "Get latest news articles about a stock. Use for recent catalysts, events, or sentiment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "limit": {"type": "integer", "description": "Number of articles (default 5)"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_analyst_estimates",
            "description": "Get Wall Street analyst price targets and earnings estimates. Use for understanding market expectations and upside/downside potential.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_stocks",
            "description": "Compare key financial metrics across multiple stocks side by side. Use when asked to compare or choose between stocks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ticker symbols to compare (max 5)"
                    }
                },
                "required": ["tickers"]
            }
        }
    },
]

# Map function names to actual Python functions
TOOL_FUNCTIONS = {
    "get_stock_quote": get_stock_quote,
    "get_financial_ratios": get_financial_ratios,
    "get_income_statement": get_income_statement,
    "get_company_profile": get_company_profile,
    "get_stock_news": get_stock_news,
    "get_analyst_estimates": get_analyst_estimates,
    "compare_stocks": compare_stocks,
}


# ============================================================
# THE AGENT - This is the core loop
# ============================================================

class StockResearchAgent:
    """
    AI-powered stock research agent using OpenAI function calling.
    
    How it works:
    1. User asks a question (e.g., "Is NVDA overvalued?")
    2. Agent sends question to OpenAI with available tools
    3. OpenAI decides which tools to call (may call multiple!)
    4. Agent executes those tool calls (FMP API requests)
    5. Agent sends results back to OpenAI
    6. OpenAI synthesizes everything into a research response
    7. If OpenAI needs more data, it calls more tools (loop continues)
    
    The agent can handle up to 10 rounds of tool calls per query.
    """
    
    def __init__(self, model: str = MODEL, verbose: bool = False):
        self.model = model
        self.verbose = verbose
        self.system_prompt = """You are a senior equity research analyst AI assistant built into the "Investing Made Simple" platform. Your job is to help beginner-to-intermediate investors understand stocks through clear, data-driven analysis.

When a user asks about a stock or investing topic:

1. GATHER DATA: Use your tools to pull relevant data. Always get at least the quote and ratios. For deeper questions, also pull income statements, company profile, news, and analyst targets.

2. ANALYZE: Look at the data holistically:
   - Valuation: Is the P/E, P/S, P/B reasonable vs. sector averages?
   - Growth: Is revenue/earnings growing? Accelerating or decelerating?
   - Profitability: Are margins strong and improving?
   - Financial health: Is debt manageable?
   - Sentiment: What does recent news suggest?
   - Analyst view: What do price targets imply?

3. RESPOND: Give a clear, structured analysis that includes:
   - Quick summary (bullish/bearish/neutral with 1-2 sentence thesis)
   - Key metrics with context (don't just list numbers — explain what they mean)
   - Bull case vs. bear case
   - What to watch going forward
   
Keep language accessible — explain jargon when you use it. Be opinionated but balanced. Always note this is educational, not financial advice.

IMPORTANT: Do NOT make up data. Only use data from your tool calls. If a tool returns an error, say so."""

    def research(self, query: str) -> str:
        """
        Run the agent on a user query. Returns the final analysis string.
        
        This is the main method you'll call from your Streamlit app:
            agent = StockResearchAgent()
            result = agent.research("Is NVDA overvalued compared to AMD?")
            st.markdown(result)
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query},
        ]
        
        # Agent loop - keeps going until OpenAI gives a final text response
        max_rounds = 10
        for round_num in range(max_rounds):
            if self.verbose:
                print(f"\n--- Agent Round {round_num + 1} ---")
            
            # Call OpenAI
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",  # Let the model decide when to use tools
            )
            
            message = response.choices[0].message
            
            # If no tool calls, we have our final answer
            if not message.tool_calls:
                if self.verbose:
                    print("Agent finished - returning final response")
                return message.content
            
            # Process tool calls
            messages.append(message)  # Add assistant's tool call message
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                if self.verbose:
                    print(f"  Calling: {func_name}({func_args})")
                
                # Execute the function
                if func_name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[func_name](**func_args)
                else:
                    result = {"error": f"Unknown function: {func_name}"}
                
                if self.verbose:
                    print(f"  Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })
        
        return "Agent reached maximum rounds without completing. Please try a simpler question."

    def research_stream(self, query: str):
        """
        Streaming version - yields chunks as they come in.
        
        Use this for a better UX in Streamlit:
            agent = StockResearchAgent()
            with st.chat_message("assistant"):
                response = st.write_stream(agent.research_stream("Analyze AAPL"))
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query},
        ]
        
        max_rounds = 10
        for round_num in range(max_rounds):
            # First, non-streaming call to check for tool use
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            
            message = response.choices[0].message
            
            # If no tool calls, stream the final response
            if not message.tool_calls:
                stream = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOLS,
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            
            # Process tool calls (same as non-streaming)
            messages.append(message)
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                # Show user what's happening
                yield f"\n🔍 *Fetching {func_name.replace('_', ' ')}...*\n"
                
                if func_name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[func_name](**func_args)
                else:
                    result = {"error": f"Unknown function: {func_name}"}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })


# ============================================================
# STREAMLIT INTEGRATION EXAMPLE
# ============================================================

STREAMLIT_EXAMPLE = """
# ===========================================
# HOW TO ADD THIS TO YOUR STREAMLIT APP
# ===========================================
#
# In your FINANCE_FINAL_COMPLETE.py, add this to your AI Screener section:
#
# from stock_research_agent import StockResearchAgent
#
# def show_ai_screener():
#     st.header("🤖 AI Stock Research Agent")
#     st.caption("Ask anything about stocks — the AI will research it for you")
#     
#     # Initialize agent (do this once)
#     if "agent" not in st.session_state:
#         st.session_state.agent = StockResearchAgent()
#     
#     # Chat history
#     if "agent_messages" not in st.session_state:
#         st.session_state.agent_messages = []
#     
#     # Display chat history
#     for msg in st.session_state.agent_messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])
#     
#     # User input
#     if prompt := st.chat_input("e.g., Is NVDA overvalued? Compare AAPL vs MSFT"):
#         # Show user message
#         st.session_state.agent_messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)
#         
#         # Get agent response (streaming)
#         with st.chat_message("assistant"):
#             response = st.write_stream(st.session_state.agent.research_stream(prompt))
#         
#         st.session_state.agent_messages.append({"role": "assistant", "content": response})
#
# ===========================================
"""


# ============================================================
# MAIN - Run standalone for testing
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Stock Research AI Agent")
    print("  Type 'quit' to exit")
    print("=" * 60)
    
    agent = StockResearchAgent(verbose=True)
    
    # Example queries to try:
    # - "Is NVDA overvalued?"
    # - "Compare AAPL vs MSFT vs GOOGL"
    # - "Give me a bull and bear case for TSLA"
    # - "What's happening with PLTR lately?"
    # - "Should a beginner invest in AMD or INTC?"
    
    while True:
        query = input("\n📊 Ask about any stock: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not query:
            continue
        
        print("\n🤖 Researching...\n")
        result = agent.research(query)
        print(result)
