# CLAUDE.md — Finance Made Simple

## What this repo is
Finance Made Simple (aistockinvesting101.com) — a Streamlit-based stock analysis and investing education platform. The core application is a single large file, `FINANCE_MADE_SIMPLE.py` (~33,000+ lines). This single-file architecture is intentional. Do not propose splitting it into modules unless explicitly asked.

## Stack
- **Frontend/app:** Streamlit (single file: `FINANCE_MADE_SIMPLE.py`)
- **Data:** FMP Premium API (Financial Modeling Prep)
- **Database/auth:** Supabase (auth, watchlists, `ticker_change_log` freemium gating table)
- **Payments:** Stripe
- **AI:** OpenAI GPT-4o (Portfolio Review narratives), Anthropic API (research agent)

## NON-NEGOTIABLE workflow rules
1. **Additive only. Zero deletions.** Never delete or rewrite existing functions, blocks, or features. New functionality is added as new functions/sections. If existing behavior must change, add a new code path and leave the old one intact unless explicitly told to remove it.
2. **Copy before edit.** Before any edit session, create a timestamped backup: `cp FINANCE_MADE_SIMPLE.py FINANCE_MADE_SIMPLE_backup_$(date +%Y%m%d_%H%M).py`
3. **AST-validate before declaring done.** After every edit: `python -c "import ast; ast.parse(open('FINANCE_MADE_SIMPLE.py').read())"`. Never hand back a file that fails this.
4. **One feature per session/commit.** Ship a working module before starting the next.
5. **Never commit secrets.** API keys live in Streamlit secrets / environment variables, never in code or this repo.

## Known FMP API quirks (do not rediscover these)
- `/ratios` endpoint does NOT support `period=quarter`. For quarterly ratios, use `key-metrics` + `income-statement` endpoints and compute manually.
- Non-calendar fiscal year companies (AAPL, MSFT, NVDA, etc.) require quarter relabeling. Use the existing `_relabel_fmp_fiscal_quarters` helper — do not write a new one.
- FMP historical data has survivorship-bias limitations. Any backtest output should carry a caveat in the UI.

## Existing major modules (do not break)
- Macro Nexus screener: 22 themes, 145 tickers, exhaustion scoring (RSI, Williams %R, TD Sequential), Buy/Hold/Sell verdicts, Supabase watchlist
- Trend Change Radar: scan-mode selector (auto top-10, custom list, watchlist)
- Valuation Bands: P/E, P/S, P/FCF historical percentile classification
- Financial Ratios (quarterly via key-metrics workaround)
- Bloomberg-style dense header strip
- Freemium gating via `ticker_change_log` Supabase table
- DQ Score screener, Product Segments/KPI section, YoY/QoQ growth charts
- Portfolio Review (GPT-4o narrative), paper portfolio system

## Supabase conventions
- Production tables live in the default schema. New feature tables get clear prefixed names (e.g. `signal_log`, `signal_forward_returns`).
- Never run destructive SQL (DROP, TRUNCATE, DELETE without WHERE) without explicit confirmation.

## Style/content rules
- Never mention "AI stock investing" in any user-facing content.
- App domain is aistockinvesting101.com. Substack is namanlohia.substack.com. Never conflate them.
- UI aesthetic: dense, Bloomberg-terminal-style. Information density over whitespace.

## Current build priority
Read `TERMINAL_BUILD_SPEC.md` for the active 6-module terminal build. Modules ship in order; Module 1 (signal logging) is the foundation and must ship first.
