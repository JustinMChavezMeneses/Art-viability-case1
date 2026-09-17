# Case 1: Art as an Investment — Master Plan (v1 — CONFIRMED)

> Status: CONFIRMED by MD (Sep 16). §2 Locked Decisions approved. Now in build.
> This is a plan document, not the paper. Paper format = LaTeX/Overleaf.
> Day-1 flag: Artprice100 shows ~0.88 corr to S&P 500 on LEVELS — a spurious-trend artifact.
> M1 must redo on RETURNS; the levels-vs-returns gap is itself a paper point.
> DATA UPGRADE (Sep 16): primary series is now Bloomberg ARTDAI ARTKAART — REAL quarterly USD,
> 1980–2025 (~180 obs). Chart-read caveat RETIRED; M1/M2 give real point estimates. Japan bubble
> is now a REAL event study (+162% 1985→90, −38% 1990→94). Smoothing caveat STILL applies (R1 essential).

- **Course:** FA26_FIN_680_3238 — Case 1: Art as an Investment
- **Due:** Sep 21, 2026, 6:30 PM (**5 days out** — today is Sep 16)
- **Managing Partner (designated):** the MD (you)
- **Deliverables:** (1) 5–7pp holistic memo + exhibits (≤7pp hard cap); (2) short cold-call deck
- **Team:** 3 humans running parallel research; plan is written as if solo-MD-driven

---

## 1. Thesis (evidence-led, falsifiable)

**Working thesis (NOT locked to YES):**
For a UHNW **family office**, a small satellite allocation to blue-chip art (~1–5%)
may be defensible **as an inflation and market-shock hedge — not as a return engine.**
Art is expected to *underperform* equities on raw return; its seat is earned (if at all)
through low correlation, inflation tracking, and shock resilience.

This is willing to land on:
- **YES, with strict caveats** (vehicle, sizing, 10yr+ hold, family-office-only), or
- **NO** (if the hedge benefit disappears once we correct for index smoothing / survivorship).

The evidence decides. The smoothing correction (R1) is the make-or-break test.

Maps holistically to brief Q1–Q10; heaviest on Q6 (illiquidity), Q7 (correlation),
Q8 (black-swan correlations hidden by smoothed indices), Q9 (crowded trade).

## 2a. Preliminary findings from REAL data (Sep 16 — art-only, nominal, still smoothed)

These are raw characterizations of `artk_quarterly.csv`, NOT the formal model results (which
need the market/macro data). They already lean against the naive hedge thesis:

1. **Return:** broad art (ARTKAART) = **4.1%/yr nominal** over 1980–2026 (~1%/yr real) vs S&P ~11%.
   Confirms "not a return engine."
2. **Japan bubble (Q9):** crash scaled WITH prestige — Tier One −88%, Impressionist −65%, broad −56%,
   low tier NO bubble. Concentrated crowded trade in top/Impressionist works.
3. **Recent shocks challenge the hedge legs:** 2008 GFC broad art −35% (< equities' −57%, lagged =
   partial cushion, not immunity); **2022 inflation/rate shock −24%** (art FELL during high inflation →
   undercuts inflation-hedge leg; behaves like long-duration risk asset).
4. **"Blue-chip = safe" is backwards:** Tier One = 98% annualized vol, thin market → cautionary exhibit.
5. **Emerging thesis read:** inflation-hedge looks like a LONG-AVERAGES ARTIFACT (British Rail 1974–99 era)
   that fails the modern regime = exactly Q8. Leaning toward NO / narrowly-qualified-YES. Evidence decides
   once M1/M2/M3 run with market data.

## 2. Locked Decisions (CONFIRM / VETO before build)

| # | Decision | Choice |
|---|----------|--------|
| Persona | Investor type | **UHNW family office** — only persona where contrarian-YES survives |
| Sizing | Allocation tested | **1–5% satellite**, overlaid on a 60/40 base |
| Anchor | Primary art index | **Bloomberg ARTDAI `ARTKAART` (All Traded Artists)** — REAL quarterly USD data, 1980–2025 (~180 obs). Confirmed Sep 16. Supersedes MM European. Export → `data/artk_quarterly.csv`. |
| Segments | Cross-check indices | `ARTKIMP` (Impressionist/Modern — Japan segment, SEMIANNUAL), `ARTKPWC` (Post-War/Contemporary, SEMIANNUAL), `ARTKSIX` (low tier — no Japan bubble, concentration proof). `ARTKONE` (Tier One) DEMOTED to cautionary exhibit: 98% annualized vol, thin market, not a clean modeling input. All rebased to 100 at 1980. Data: `data/artk_quarterly.csv`. |
| Robust | Minor cross-check | MM European chart-reads (`data/art_index.csv`), demoted; Artprice100 headline stats qualitative |
| Frequency | Sample | **QUARTERLY**, quarter-end, 1980–2025 (~180 obs). Resample all market/macro series to quarter-end. Small-sample constraint LIFTED. |
| Japan | 1985–95 | **NOW A REAL EVENT STUDY** — ARTKAART shows +162% (1985→1990) then −38% (1990→1994). ARTKIMP more extreme. Real data in `artk_quarterly.csv`; narrative facts still in `data/japan_bubble_facts.md`. |
| Caveat | Smoothing | STILL APPLIES — auction indices are smoothed by construction. Real Bloomberg data != unsmoothed. R1 desmoothing remains essential. |
| Benchmark | Opportunity cost | **60/40 base portfolio**, tested with vs. without art sleeve (overlay framing) |
| Rigor | Depth | **Medium** — thesis-driven 3+1 models. ~180 quarterly obs now support real point estimates; keep models parsimonious, don't over-engineer just because n grew. |

## 3. Models (3 core + 1 robustness) — one parallel agent each

### M1 — Correlation & Diversification Matrix
- **Inputs:** art returns vs S&P500, gold, 10Y Treasury, CPI, real estate (REIT + Case-Shiller), VIX
- **Method:** full-period correlation matrix + rolling (e.g. 5yr) correlations; diversification ratio
- **Tests:** Q7 — is art actually uncorrelated / a diversifier?
- **Output:** `outputs/M1/results.json` (corr matrix, rolling series), `figure` (heatmap + rolling plot), `findings.md`

### M2 — Inflation-Hedge Regression
- **Inputs:** real & nominal art returns; CPI YoY (primary), 10Y breakeven surprise (2003+); market return control
- **Method:** OLS with robust (HC) SEs; report inflation beta, R²; small-sample caveats explicit
- **Tests:** Q1/Q5 — does art track or beat inflation? (British Rail precedent)
- **Output:** regression table, inflation-beta figure, findings

### M3 — Crisis / Regime Event Study (incl. Japanese asset bubble)
- **Inputs:** art vs 60/40 vs S&P around: **Japanese asset bubble (~1986–1991 run-up + collapse)**,
  2008 GFC, 2020 COVID, 2022 inflation/rate shock (NBER + defined windows)
- **Japan bubble sub-study (REQUIRED, MD directive):**
  - Ref: https://en.wikipedia.org/wiki/Japanese_asset_price_bubble
  - The art-market-specific crash: Japanese buyers were the crowded trade in Impressionist/
    Post-Impressionist work (Yasuda *Sunflowers* ~$39.9M 1987; Saito *Dr. Gachet* $82.5M +
    Renoir *Bal du moulin* $78.1M, May 1990 peak), then collapse into mid-90s with the Nikkei.
  - **Data implication:** Artprice100 starts in 2000 and CANNOT see this crash → this sub-study
    must use **Mei-Moses (1950+)**. The anchor index's blindness to it IS the Q8 evidence.
  - Directly evidences **Q9 (crowded trade)** and **Q8 (black-swan correlations hidden by
    indices / long averages)** — the two hardest questions in the brief.
- **Method:** event-window cumulative returns, max drawdown, recovery time; correlation *in crisis*
  vs normal; for Japan, art-index drawdown & recovery vs Nikkei
- **Tests:** Q6/Q8/Q9 — does art hold up in shocks, or do correlations spike / crowds evaporate
  exactly when the hedge is needed?
- **Output:** event-window table (4 episodes), drawdown comparison, crisis-vs-normal correlation, findings

### R1 — Smoothing Correction + Beta (Robustness, the linchpin)
- **Inputs:** Artprice100 series
- **Method:** Geltner-style AR(1) desmoothing → re-estimate art volatility & correlation on unsmoothed returns;
  CAPM / Fama-French beta regression as a "low systematic risk" support stat (not alpha-chasing)
- **Tests:** Q8 — how much of art's low vol / low correlation is real vs. a reporting artifact?
- **Output:** smoothed-vs-unsmoothed vol & corr table, beta table, findings

**Portfolio overlay (rejoin step, done by MD after M1–M3):**
60/40 vs 58/38/4-art (and a 2% variant) — Δ drawdown in each crisis window, Δ real return in
inflation regimes, return give-up. This is the opportunity-cost answer (Q5).

**Cut (documented as "further work," not run):** cointegration/Granger UHNW→art;
wealth-share regression. Reason: demand-side, not hedge-thesis; fragile at n≈25.

## 4. Data Spine (shared, built Day 1)

- `.context/data/art_index.csv` — hand-transcribed: Artprice100 annual (2000+), Mei-Moses annual
  (**extend back to ~1985 to cover the Japan bubble for M3**), Contemporary annual.
  Source: Artprice report / Mei-Moses / brief sources. ~30 min transcription.
- **Scriptable market/macro (agents pull directly):**

  | Series | Source | Ticker / ID |
  |--------|--------|-------------|
  | S&P 500 | yfinance | `^GSPC` (price) / FRED `SP500` |
  | Gold | yfinance | `GLD` or `GC=F` |
  | 10Y Treasury yield | FRED | `DGS10`; total-return proxy `TLT` (yfinance) |
  | CPI | FRED | `CPIAUCSL` (→ YoY) |
  | 10Y breakeven inflation | FRED | `T10YIE` (2003+) |
  | Real estate | FRED `CSUSHPINSA` (Case-Shiller) / yfinance `VNQ` (REIT) | |
  | VIX | yfinance `^VIX` / FRED `VIXCLS` | |
  | Nikkei 225 (for Japan bubble, M3) | yfinance | `^N225` |
  | Fama-French factors | Kenneth French library (`pandas_datareader`) | |
  | Recession dates | FRED | `USREC` |

- **Bloomberg / PitchBook (MD-only, manual):** cross-check art-fund track records (Masterworks,
  Fine Art Group, Artemundi) for the qualitative section; fill any series free sources lack →
  transcribe into the spine. Agents do NOT touch Bloomberg (terminal-bound, not parallel-scriptable).

## 5. Parallel-Agent Contract (so results rejoin cleanly)

Every model agent:
1. Reads the **same** `.context/data/art_index.csv` and the **same** ticker list above.
2. Uses the **same** conventions: annual year-end frequency, 2000–2024 window, real = nominal − CPI YoY,
   log returns for stats.
3. Writes to `.context/outputs/<M#>/` with a fixed schema:
   - `results.json` — the key numbers (so the rejoin step can machine-read them)
   - `figure.(png|pdf)` — one publication-quality exhibit
   - `findings.md` — ≤1 paragraph finding + explicit caveats
4. Gets a tight, self-contained prompt (one model, compact output) — **written in Phase build, not now.**

**Usage-limit note (MD flagged):** don't fan out all 6 at once. Priority order = M1, M2, M3 first
(the thesis spine), then R1. Keep prompts lean; each agent does ONE model and returns compact output.

## 6. Phase Timeline (Sep 16 → 21, due 6:30 PM Sep 21)

| Date | Phase | Output | Status |
|------|-------|--------|--------|
| **Sep 16 (today)** | Lock plan + build REAL data spine + write agent prompts | plan confirmed, `artk_quarterly.csv`, 4 agent prompts | **DONE — ahead of schedule** (spine is real Bloomberg data, not chart-reads) |
| Sep 17 | Launch model agents M1→M3, then R1 | `outputs/*/` populated | next |
| Sep 18 | Rejoin + analyze; run 60/40 portfolio overlay | thesis verdict (YES-caveats / NO), exhibit set | **Verdict gate** |
| Sep 19 | Draft LaTeX memo (5–7pp) from findings | memo v1 | |
| Sep 20 | Build deck; internal review | deck v1 + review notes | |
| Sep 21 | Polish, exhibits, buffer | final memo + deck | Due 6:30 PM |

Note: Day-1 scope grew (real Bloomberg data replaced chart-reads, prompts written same day), so we
enter Sep 17 with the data foundation already solid — buffer gained.

## 7. Open items for MD

- [x] **BLOOMBERG DATA UPGRADE (CONFIRMED Sep 16):** ARTDAI ARTKAART = REAL quarterly USD, inception
      3/31/1980, ~180 obs. Verified via sample points (1980=119.68, 1985=154.69, 1990=404.73 peak,
      1994=249.82, 1996=275.15, 2020=573.52) — genuine variation, Japan bubble visible. NOT back-padding.
- [x] **EXPORT FULL SET (DONE Sep 16):** 5 tickers merged → `data/artk_quarterly.csv` (186 quarterly rows
      1980Q1–2026Q2; IMP/PWC semiannual). Six sample points reproduced exactly. Findings in §2a. Parser: /tmp/parse_artk.py.
- [x] **4 agent prompts WRITTEN (Sep 16):** `.context/agent_prompts/` — `00_shared_context.md`,
      `M1_correlation.md`, `M2_inflation.md`, `M3_event_study.md`, `R1_desmoothing.md`, `README.md`.
      Each: reads quarterly spine, pulls own FRED/yfinance data, writes `outputs/<M#>/` fixed schema.
- [x] **Agents ran + REJOINED (Sep 16):** M1 (diversification: small/fragile), M2 (inflation hedge:
      KILLED), M3 (shock hedge: weak; Japan −56%/−65%/−88%; modern crisis corr 0.30 vs calm 0.10),
      R1 (AR(1) = −0.62, NEGATIVE not smoothed; low-corr partly noise; CAPM β 0.22–0.37, α≈0).
      Overlay: 4% art sleeve = do-nothing (return −0.09pp, vol −0.19pp, DD +0.1pp). Results in `outputs/`.
- [x] **VERDICT: NO** — art does not earn its seat as an inflation or shock hedge for a UHNW family
      office. Narrow caveat: ≤2% justifiable only on non-financial (consumption/prestige) grounds, 10yr+
      hold, via a diversified fund not single works. Evidence-led, contrarian to opening lean.
- [x] **LaTeX memo DRAFTED (Sep 16):** `.context/paper/case1_memo.tex` (holistic, evidence-led NO) +
      `paper/exhibits/` (5 PNGs). Lints clean (braces balanced, no unescaped chars, images linked).
      Compile on Overleaf. Overlay table + Table 1 embedded.
- [ ] **NEXT — MD: compile on Overleaf, check ≤7 pages** (drop ex5 if over), fill [MD]/[Name] placeholders.
- [ ] **THEN — build the cold-call deck** from the memo's 5 exhibits + recommendation.
- [ ] **DES checks (for citation, non-blocking):** ARTDAI provider/methodology (repeat-sale? which houses?),
      base date/value, whether pre-1996 is back-computed history, whether Q1/Q3 are interpolated vs Q2/Q4 auction seasons.
- [ ] **DEFERRED — Artprice100 report cross-check:** only if Bloomberg ARTK* falls through. Known % points
      in `art_index.csv` notes (2000 +10.9%, 2020 +1.8%, 2021 +36%, 2023 +1.55%, 2024 -8.3%, 2025 +11.2%).
- [x] §2 Locked Decisions confirmed (Sep 16).
- [x] Primary index = MM European (Option 2), data filled in `art_index.csv` (chart-read approx, refine if a table surfaces).
- [x] Japan bubble = episode study, facts in `japan_bubble_facts.md`.
