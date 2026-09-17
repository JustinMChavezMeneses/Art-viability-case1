# SHARED CONTEXT — read first (all model agents)

You are one of four parallel analysis agents for FIN Case 1 "Art as an Investment."
You run ONE model, in your own Conductor workspace, and write structured output that the
Managing Partner rejoins with the other three. Do NOT write the paper or deck. Do NOT
editorialize beyond your `findings.md`. Your job: correct numbers + one clean exhibit.

## Thesis you are testing (evidence-led, may land NO)
For a UHNW family office, is a small (1–5%) satellite allocation to art defensible as an
**inflation and market-shock hedge — NOT a return engine**? Preliminary raw-data read leans
AGAINST the hedge (art fell −24% in the 2022 inflation shock, −35% in 2008). Let your numbers
speak. Do not force a YES.

## REQUIRED INPUT (must exist in this workspace)
`.context/data/artk_quarterly.csv` — Bloomberg ARTDAI art indices, quarter-end, USD, rebased 100 at 1980.
Columns: `date, ARTKAART, ARTKIMP, ARTKONE, ARTKPWC, ARTKSIX`.
- **ARTKAART** = All Traded Artists = PRIMARY art series. Quarterly, 1980Q1–2026Q2 (186 obs).
- ARTKSIX = low tier (quarterly). ARTKIMP (Impressionist), ARTKPWC (Contemporary) are **SEMIANNUAL**
  (Jun/Dec only, ~93 obs) — blanks in Q1/Q3 are expected; do NOT forward-fill returns across them.
- **ARTKONE (Tier One) is a CAUTIONARY EXHIBIT, not an input** — 98% annualized vol, thin market. Use
  only to illustrate masterpiece noise, never as the return series in a regression/correlation.
If this file is missing, STOP and ask the MD to copy it from the main workspace. Do not fabricate it.

## Environment setup (run once)
```bash
python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet pandas numpy statsmodels scipy matplotlib yfinance pandas_datareader
```
All packages ship prebuilt macOS wheels (no compiler / no Xcode license needed). If a network
fetch fails, retry once, then REPORT the failure in findings.md — never silently pad or invent data.

## Market / macro data (fetch yourself; keyless)
Use `pandas_datareader` for FRED + Fama-French (no API key), `yfinance` for markets. Fetch daily/monthly,
then **resample to quarter-end (`'QE'`) last value**. State the exact sample period you actually used
per test (series start dates differ).

| Need | Source | Symbol | Starts |
|------|--------|--------|--------|
| S&P 500 (price) | yfinance | `^GSPC` | 1980 |
| S&P 500 total return | yfinance | `^SP500TR` | 1988 |
| Gold (USD/oz) | FRED | `GOLDAMGBD228NLBM` | 1968 |
| 10Y Treasury yield | FRED | `DGS10` | 1962 |
| Bond total-return proxy | yfinance | `IEF` (2002+), `TLT` (2002+) | 2002 |
| CPI (headline) | FRED | `CPIAUCSL` | 1947 |
| 10Y breakeven inflation | FRED | `T10YIE` | 2003 |
| Home prices | FRED | `CSUSHPINSA` (Case-Shiller) | 1987 |
| REITs | yfinance | `VNQ` | 2004 |
| VIX | FRED | `VIXCLS` | 1990 |
| Nikkei 225 | yfinance | `^N225` | 1980s |
| Fama-French factors | pandas_datareader | `F-F_Research_Data_Factors` (famafrench) | 1926 |
| Recession flag | FRED | `USREC` | 1854 |

## Conventions (identical across all four agents — do not deviate)
- **Frequency:** quarterly, quarter-end. Align everything to art's quarter-end dates.
- **Returns:** quarterly **log returns** for statistics; simple returns where compounding/interpretation needs it (label which).
- **Real vs nominal:** real return = nominal art return − CPI inflation over the same quarter. **Label every number real or nominal.**
- **Autocorrelation:** art returns are smoothed → serially correlated. Use **Newey-West / HAC SEs** in every regression (lags≈4). Never plain OLS SEs.
- **Levels vs returns:** correlations/regressions on RETURNS, never price levels (levels give a spurious ~0.88 trend correlation — you may report that ONCE as a contrast, clearly labeled "spurious levels correlation").
- Round sensibly; keep full precision in `results.json`.

## Output schema (write to `.context/outputs/<YOUR_MODEL>/`)
1. `results.json` — all key numbers (so the rejoin step machine-reads them). Include a `sample_period`,
   `n_obs`, and `real_or_nominal` field on every stat block.
2. One or two `*.png` exhibits — publication quality (titled, labeled axes, legend, source note
   "Source: Bloomberg ARTDAI + FRED/Yahoo, quarterly"). Save the plotting script too.
3. `findings.md` — ≤ 1 paragraph plain-English finding + a bulleted **caveats** list + 2–4 **"for the memo"**
   bullets the MD can lift. State whether your result supports, weakens, or kills the hedge thesis.

## Hard rules
- Never fabricate, pad, or forward-fill missing data to make a series look complete. Report gaps.
- State the actual sample period and n for every statistic.
- Smoothing bias and thin-market noise are REAL — flag when they could be driving your result.
- If a result contradicts the thesis, say so plainly. Contrarian evidence is the point.
