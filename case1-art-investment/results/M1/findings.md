ARTKAART has low measured quarterly co-movement with conventional assets, but this supports diversification more than a hedge claim. Its Pearson/Spearman correlation with S&P 500 log returns is 0.19/0.23 over 1980Q2–2026Q2 (n=185), versus a **spurious levels** correlation of 0.62 (n=186); it is −0.20/−0.22 versus IEF over 2002Q4–2026Q2 (n=95) and essentially zero versus quarterly CPI inflation (−0.003/0.04, n=185). At a 4% art allocation funded pro rata from a 60/40, art is only 2.5% of portfolio variance and the sample variance is 4.0% lower than the unmodified 60/40, but this is a small, in-sample diversification result—not proof of inflation or crash protection. The 20-quarter art/S&P correlation ranges from −0.19 to 0.61 and is 0.40 at 2008Q4, showing that the relationship is not reliably benign in stress. Verdict: **supports measured diversification, but materially weakens any claim that art is a dependable market-shock hedge.**

## Caveats

- Appraisal-based, infrequently traded art marks are smoothed and serially correlated; this can mechanically suppress measured return correlations. Thin-market noise makes the low-correlation result especially easy to overstate.
- Correlations are nominal quarterly log returns (except the 10Y series, which is a percentage-point yield change, and VIX, which is a level). They do not test liquidity, transaction costs, valuation lag, or the ability to rebalance during a shock.
- IEF constrains the 60/40 calculation to 2002Q4–2026Q2 (n=95); VNQ and home prices have shorter pairwise samples, recorded in `results.json`.
- The requested FRED gold series (`GOLDAMGBD228NLBM`) returned an FRED 404 after one retry. No substitute series was used, so gold correlations and the art/gold rolling line are intentionally absent rather than fabricated.
- ARTKIMP and ARTKPWC robustness rows use Jun/Dec semiannual returns only; ARTKSIX uses quarterly returns. ARTKONE was not used.

## For the memo

- “The oft-cited art/S&P correlation from price levels is spurious: 0.62 in levels, versus 0.19 on the relevant quarterly returns (1980Q2–2026Q2).”
- “Measured art/60–40 correlation is 0.11 over the IEF-available sample (2002Q4–2026Q2), and a 4% art sleeve lowered in-sample portfolio variance by 4.0%.”
- “Do not equate low measured correlation with crisis insurance: rolling five-year art/S&P correlation reached 0.40 at 2008Q4 and a maximum of 0.61.”
- “Because appraisals smooth art returns and sales are illiquid, the diversification estimate is likely optimistic at precisely the moments when a hedge would be needed.”
