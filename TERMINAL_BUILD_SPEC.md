# TERMINAL_BUILD_SPEC.md — Finance Made Simple Terminal Build

## Goal
Add 6 modules to `FINANCE_MADE_SIMPLE.py` that turn the app from a signal display into a probability engine: every signal gets logged, backtested, and shown with its measured historical base rates (win rate, median forward return, worst case), styled as a dense Bloomberg-style terminal.

## Ground rules (also in CLAUDE.md — both apply)
- Additive only. Never delete or rewrite existing functions. New code = new functions/sections.
- Backup before every session: `cp FINANCE_MADE_SIMPLE.py FINANCE_MADE_SIMPLE_backup_$(date +%Y%m%d_%H%M).py`
- AST-validate after every edit. Never finish a session with a file that fails `ast.parse`.
- Build modules IN ORDER. Each must run end-to-end in `streamlit run` before starting the next.
- All new Supabase tables prefixed `term_`. Never run destructive SQL without explicit confirmation.
- Every backtest panel must display a caveat: "Backtests use FMP EOD data and may contain survivorship bias. Past base rates are not guarantees."
- No API keys in code. Use existing Streamlit secrets pattern.
- New UI uses the design system in Module 0. Do NOT restyle existing tabs unless explicitly asked.

## Module 0 — Bloomberg design system (build first, same session as Module 1)
A reusable theming layer all new modules use.
- `inject_terminal_css()`: dark panel styling — background #0d0f12, panel borders #2a2e35, monospace numerals, amber #f5a623 accents, green #34d399 positive, red #f87171 negative, muted labels #6b7280, light text #e8eaed. Scoped CSS classes (prefix `.term-`) so existing app styling is untouched.
- Component functions: `term_header_strip(ticker, metrics: dict)`, `term_panel(title, badge=None)` context wrapper, `term_dense_table(df)`, `term_stat(label, value, color_logic)`.
- Dense layout: tight padding, 11-13px type, function-key style tab chips.

## Module 1 — Signal logging + forward returns (foundation)
**Purpose:** every signal the app generates becomes a logged, verifiable record.
- Supabase tables:
  - `term_signal_log`: id, ts, ticker, module (macro_nexus | trend_radar | manual), signal_type, score, verdict, price_at_signal, regime_trend, regime_vol, meta jsonb
  - `term_signal_returns`: signal_id FK, ret_1d, ret_5d, ret_20d, ret_60d, filled_at
- Hook (additively) into Macro Nexus verdict generation and Trend Change Radar output: when a verdict is computed, insert a row. Wrap in try/except so logging failure never breaks the UI.
- `fill_forward_returns()` function: finds rows with unfilled returns whose horizon has elapsed, fetches FMP EOD prices, computes returns. Expose as a button in a new "Signal Ledger" tab + write a standalone `scripts/fill_returns.py` for later cron use.
- Signal Ledger tab UI: dense table of logged signals with filled returns, summary stats per signal_type (count, win rate, avg/median return per horizon).

## Module 2 — Historical base-rate engine (the core)
**Purpose:** answer "when this setup occurred historically, what happened next?"
- For a given ticker + setup definition, scan 10-15 years of FMP EOD history and find all dates where the setup condition was true. Compute forward returns (5d/20d/60d) from each occurrence.
- Setup definitions (config-driven, dict/YAML-style like the existing Macro Nexus agent config): RSI thresholds, Williams %R, valuation band percentile (reuse existing Valuation Bands logic), combinations (AND of conditions).
- Output stats: n occurrences, win rate, median return, mean return, 25th/75th percentile, worst case, best case — per horizon.
- Pooled mode: run the same setup across all 145 Macro Nexus tickers and aggregate.
- Cache results in Supabase `term_base_rates` (setup_hash, ticker, horizon, stats jsonb, computed_at) — recompute only if stale > 7 days.
- UI: "Base Rates" panel on the ticker page using term_panel: "This setup occurred N times since YYYY. 20d median: +X%, win rate Y%, worst: -Z%." Plus distribution strip (quartiles).
- Integrate into Macro Nexus: next to each Buy/Hold/Sell verdict, show that signal's measured base rate (from Module 1 live data when n is sufficient, else Module 2 backtest).

## Module 3 — Regime filter
**Purpose:** the same signal behaves differently in different markets; split all stats by regime.
- Trend regime: SPY above/below 200-day MA → "Uptrend"/"Downtrend".
- Vol regime: VIX percentile over trailing 2 years → "Low vol" (<50th) / "High vol" (>=50th).
- `get_current_regime()` cached daily; stamp onto every new signal log row (Module 1 columns already exist).
- Module 2 base-rate engine gains a regime split: stats shown blended AND split by the 4 regime combinations.
- UI: regime badge in the terminal header strip; regime-split rows in base-rate panels.

## Module 4 — Earnings event studies
**Purpose:** per-ticker post-earnings behavior patterns.
- Use FMP earnings calendar + historical EOD. For each past earnings date (last 12-16 quarters): surprise %, day-after move, 5d and 20d drift.
- Stats: avg absolute earnings-day move, % of beats followed by positive 20d drift, % of misses followed by negative drift.
- Reuse `_relabel_fmp_fiscal_quarters` for any fiscal labeling. Do not write a new relabeler.
- UI: "Earnings Lab" panel — next earnings countdown in header strip, historical reaction table, drift stats.

## Module 5 — Cross-sectional momentum ranking
**Purpose:** systematic momentum screen across the full universe.
- 12-1 momentum: trailing 12-month return excluding most recent month, computed weekly for all Macro Nexus tickers (and watchlist).
- Rank into deciles within the full universe and within each of the 22 themes.
- Cache in `term_momentum_ranks` (ticker, asof, mom_12_1, decile_universe, decile_theme).
- UI: "Momentum" tab — sortable dense table, top-decile highlight, each ticker page shows its momentum decile in the header strip.

## Module 6 — Macro surprise / prediction-market divergence panel
**Purpose:** compare historical macro surprise patterns against market-implied odds.
- FMP economics endpoints: for CPI, NFP, GDP, Fed decisions — pull history of consensus vs actual; compute surprise distribution (e.g., "CPI below consensus 7 of last 12 prints").
- Kalshi public API integration (new, isolated module `kalshi_client` functions): fetch implied probabilities for matching event contracts. Read-only. No trading endpoints. API base: https://api.elections.kalshi.com/trade-api/v2 (verify current docs at build time).
- UI: "Macro Edge" tab — upcoming events calendar, historical surprise stats per indicator, Kalshi implied odds side-by-side, divergence highlight when historical base rate and implied odds differ by a configurable threshold.
- Prominent caveat: informational only, not trading advice; verify Kalshi terms of service before any automation beyond read-only display.

## Session plan
1. Session 1: Module 0 + Module 1 (schema SQL provided to user to run in Supabase SQL editor first, then code)
2. Sessions 2-3: Module 2
3. Session 4: Module 3
4. Session 5: Module 4
5. Session 6: Module 5
6. Sessions 7-8: Module 6

## Definition of done (each module)
- AST passes; `streamlit run FINANCE_MADE_SIMPLE.py` launches with no new errors
- New tab/panel renders with real data for at least 3 test tickers (AAPL, NVDA, CRWD — covers non-calendar fiscal years)
- No existing feature visually or functionally changed
- Commit message: `terminal: module N — <name>`
