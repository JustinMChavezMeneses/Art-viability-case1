# AGENT R1 — Desmoothing Correction + Beta (Robustness, the linchpin)

**First read `.context/agent_prompts/00_shared_context.md` in full.** Then do ONLY this model.
Output dir: `.context/outputs/R1/`.

## Question
How much of art's apparent low volatility / low correlation / high Sharpe is REAL vs a
smoothing artifact (brief Q8, and the caveat every serious art paper must answer)? Repeat-sale
auction indices are smoothed by construction — even our real Bloomberg data. If desmoothing
erases the diversification benefit, the hedge thesis is dead.

## Do
1. **Measure the smoothing:** first-order autocorrelation ρ of ARTKAART quarterly returns. A high,
   significant ρ is the smoothing signature. Report ρ and its significance.
2. **Geltner (1991/93) unsmoothing:** recover true returns via
   `r_true_t = (r_obs_t − ρ·r_obs_{t−1}) / (1 − ρ)`.
   (Optionally also an AR(1)-model variant; report both if you do.)
3. **Compare smoothed vs unsmoothed** for ARTKAART: annualized volatility, Sharpe ratio
   (excess over 3M T-bill `DTB3`), and correlation to S&P returns. Tabulate before/after. Expect
   vol UP, Sharpe DOWN, correlation UP (toward equities) after unsmoothing.
4. **Beta / systematic risk (support stat, NOT alpha-chasing):**
   - CAPM: `art_excess_ret = α + β·mkt_excess_ret + ε` (Newey-West HAC SEs) on BOTH smoothed and
     unsmoothed art returns. Report β, α, t-stats. Low β is the honest "low systematic risk" case;
     desmoothing typically raises β.
   - Fama-French 3-factor as robustness (factors via pandas_datareader `F-F_Research_Data_Factors`,
     quarterly).
5. State how much the "art diversifies" story survives desmoothing.

## results.json (suggested keys)
`rho_ar1` {value, pvalue}, `vol_smoothed`, `vol_unsmoothed`, `sharpe_smoothed`, `sharpe_unsmoothed`,
`corr_sp_smoothed`, `corr_sp_unsmoothed`, `capm_smoothed` {alpha, beta, se_hac, t}, `capm_unsmoothed`,
`ff3` {mkt_beta, smb, hml, alpha}, per-block `sample_period`/`n_obs`.

## Exhibits
- `smoothed_vs_unsmoothed.png` — bar/table chart: vol, Sharpe, S&P-correlation before vs after desmoothing.
- Optional: smoothed vs unsmoothed cumulative return paths.

## Verdict to state in findings.md
After desmoothing, does art still look like a low-vol, low-correlation diversifier — or does the
benefit shrink materially? This is the make-or-break robustness check; be blunt about which way it cuts.
