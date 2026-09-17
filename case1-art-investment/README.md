# Case 1: Art as an Investment

FIN 680 Case 1 — an evidence-led analysis of whether a UHNW single-family office should hold art
as an inflation and market-shock hedge. **Verdict: No.**

## Finding
Across 46 years of quarterly data (Bloomberg ARTDAI art indices, 1980–2026) plus FRED/Yahoo market
data, art fails both hedge claims: the inflation-hedge beta is ~0 and its *real* return falls when
inflation rises; it drew down 25–56% in every major crisis with 5–16 year recoveries; and at a
realistic 4% weight it changes a 60/40 portfolio by <0.2 pp on return, volatility, or drawdown.
The 1980s Japanese bubble shows the tail risk is a crowded trade — the crash scaled *with* prestige
(broad −56%, Impressionist −65%, Tier One −88%).

## Layout
- `memo/` — the investment memo (`case1_memo.tex`, LaTeX/Overleaf) + `exhibits/` (5 figures).
- `data/` — `artk_quarterly.csv` (Bloomberg ARTDAI, quarterly, rebased 100 at 1980) + Japan-bubble facts.
- `models/` — the four scoped analysis specs (M1 correlation, M2 inflation, M3 event study, R1 desmoothing).
- `results/` — each model's `findings.md`, `results.json`, figures, and run script; plus the 60/40 overlay.
- `master_plan.md` — the full project plan and decision log.

## Reproduce
Each `results/<M#>/*.py` builds its own venv-installable stack (pandas, numpy, statsmodels, yfinance,
pandas_datareader, matplotlib) and reads `data/artk_quarterly.csv`. Market/macro series are pulled
keyless from FRED + Yahoo Finance.

## Data note
Art indices are Bloomberg ARTDAI (repeat-sale auction indices); the derived quarterly CSV is included
for reproducibility. Raw Bloomberg exports are omitted. Results are directional given index smoothing,
survivorship, and ~25% round-trip auction costs — all discussed in the memo's limitations.
