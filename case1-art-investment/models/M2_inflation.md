# AGENT M2 — Inflation-Hedge Regression

**First read `.context/agent_prompts/00_shared_context.md` in full.** Then do ONLY this model.
Output dir: `.context/outputs/M2/`.

## Question
Does art track or beat inflation — is it an inflation hedge (brief Q1/Q5)? The British Rail
precedent says yes for 1974–99; the raw data says art FELL 24% during the 2022 inflation shock.
Test whether the hedge is real or a **long-averages artifact** that fails in the modern regime.

## Do
1. Quarterly nominal ARTKAART return; CPI inflation (`CPIAUCSL` QoQ, annualized); real art return =
   nominal − inflation.
2. **Core regression (Newey-West HAC SEs, ~4 lags):**
   `nominal_art_ret_t = α + β1·inflation_t + β2·Δexpected_inflation_t + β3·mkt_ret_t + ε`
   - `inflation` = realized CPI. `Δexpected_inflation` = change in 10Y breakeven `T10YIE` (2003+ only —
     run a full-sample version without it, and a 2003+ version with it). `mkt_ret` = S&P return control.
   - **Hedge test:** H0 that art fully passes through inflation ⇒ β1 = 1 on nominal returns. Report the
     Wald test / t-stat against 1, not just against 0.
3. Also regress **real** art return on inflation (β<0 ⇒ art loses real value when inflation rises).
4. **Regime split — the key test:** run the regression on **pre-2000** vs **2000–2026** subsamples
   (and optionally high-inflation quarters, CPI>4% annualized, vs low). Report whether the inflation
   beta collapses in the modern subsample. That collapse = the "long-averages artifact" evidence (Q8).
5. Report β1, HAC t-stats, R², n, and the H0:β1=1 result for every spec.

## results.json (suggested keys)
`reg_full` {beta_inflation, se_hac, t_vs_0, t_vs_1, r2, n}, `reg_2003plus`, `reg_pre2000`,
`reg_2000plus`, `reg_highinfl`, `real_return_inflation_beta`, per-block `sample_period`/`real_or_nominal`.

## Exhibits
- `inflation_beta_regimes.png` — inflation beta (with HAC CI bars) across full / pre-2000 / modern / high-infl.
- Optional scatter: quarterly art real return vs inflation, with fit line.

## Verdict to state in findings.md
Is the inflation-hedge claim supported full-sample but broken in the modern regime? Say plainly
whether M2 supports, weakens, or kills the inflation-hedge leg of the thesis. Note the ~180-obs
sample is now adequate, but smoothing still inflates autocorrelation — hence HAC SEs.
