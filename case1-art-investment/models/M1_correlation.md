# AGENT M1 — Correlation & Diversification Matrix

**First read `.context/agent_prompts/00_shared_context.md` in full.** Then do ONLY this model.
Output dir: `.context/outputs/M1/`.

## Question
Is art actually uncorrelated with other assets — i.e. does it diversify a portfolio? This is
brief Q7. The naive claim "art has ~0.88 correlation to the S&P" is a LEVELS artifact; the real
test is on quarterly returns.

## Do
1. Build quarterly **log returns** for `ARTKAART` (primary). Also compute for `ARTKIMP`,
   `ARTKPWC` (semiannual — use semiannual returns, note it), and `ARTKSIX` as robustness rows.
2. Assemble quarterly returns / changes for: S&P 500 (`^GSPC`), gold (`GOLDAMGBD228NLBM`),
   10Y yield **change** (`DGS10`), bond proxy (`IEF`/`TLT`), CPI inflation (`CPIAUCSL` QoQ),
   REITs (`VNQ`), home prices (`CSUSHPINSA`), VIX **level** (`VIXCLS`).
3. **Full-sample Pearson + Spearman correlation matrix on RETURNS.** Report both. Use max overlap
   per pair and record n for each.
4. **Contrast exhibit:** also compute art-vs-S&P correlation on price LEVELS and label it
   "spurious (levels)". Put the levels number next to the returns number so the gap is the story.
5. **Rolling 20-quarter (5yr) correlation** of ARTKAART returns vs S&P and vs gold — plot it. Show
   whether correlation rises in/after crises (foreshadows M3's black-swan test).
6. **Diversification math:** correlation of ARTKAART returns to a 60/40 (0.6·S&P + 0.4·IEF) return
   series; and art's marginal contribution to 60/40 portfolio variance at a 4% art weight.

## results.json (suggested keys)
`corr_returns` (matrix), `corr_spearman`, `art_sp_returns_corr`, `art_sp_levels_corr_spurious`,
`rolling_corr_sp` (date→value), `art_60_40_corr`, `marginal_var_contribution_4pct`, per-block
`sample_period`/`n_obs`/`real_or_nominal`.

## Exhibits
- `corr_heatmap.png` — returns correlation matrix.
- `rolling_corr.png` — 5yr rolling art-vs-S&P and art-vs-gold.

## Verdict to state in findings.md
Does art diversify (low returns correlation) — and how much of any "low correlation" could be
**smoothing + thin-market noise biasing correlation toward zero** rather than a genuine hedge?
Flag that explicitly; it is the crux M1 must not oversell.
