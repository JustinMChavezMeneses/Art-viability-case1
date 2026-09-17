# M3 — Crisis / Regime Event Study

ARTKAART was not a dependable shock hedge: it suffered material peak-to-trough losses in the GFC and 2022 rate shock, while Japan shows the especially severe risk of a crowded segment. Across all four non-contiguous crises (including Japan), pooled art–equity correlation was 14.9% versus 21.6% in calm quarters; it therefore did not rise in that broad comparison. But in the like-for-like modern sample (2002 onward), it rose to 30.2% in crises versus 10.5% in calm quarters. These short-window correlations are descriptive, but the drawdowns and slow/no recoveries plainly weaken the shock-hedge leg of the thesis.

## For the memo
- **Japan (1986-03-31 to 2000-12-31):** ARTKAART cumulative return 137.3%; maximum drawdown -56.0% (peak 1989-12-31, trough 1995-09-30); recovery 40 quarters (1999-12-31).
- **2008 GFC (2007-12-31 to 2012-12-31):** ARTKAART cumulative return -22.5%; maximum drawdown -35.1% (peak 2008-06-30, trough 2009-03-31); recovery not recovered through 2026-06-30.
- **COVID (2019-12-31 to 2021-12-31):** ARTKAART cumulative return 6.6%; maximum drawdown -14.5% (peak 2019-12-31, trough 2020-06-30); recovery 4 quarters (2020-12-31).
- **2022 inflation/rates (2021-12-31 to 2024-12-31):** ARTKAART cumulative return -24.8%; maximum drawdown -25.4% (peak 2021-12-31, trough 2024-09-30); recovery not recovered through 2026-06-30.
- **Crisis correlation test:** in the modern 2002+ comparison, art–S&P quarterly log-return correlation was 30.2% in 23 crisis observations versus 10.5% in 75 calm observations. Adding the long Japan episode reverses the pooled comparison (14.9% versus 21.6%); individual windows are in `results.json`.
- **Japan crowding:** ARTKIMP ran up 479.1% then had a -65.1% maximum drawdown; Tier One ran up 671.1% then fell -88.2%. ARTKSIX was far smaller (+102.5% run-up, -37.2% drawdown), so the data show concentration rather than literally no low-tier bubble. ARTKIMP–Nikkei matched-half-year return correlation was 27.3%. A 2000-starting art index would miss this episode entirely; the supplied ARTDAI history starts in 1980 and does not.

## Caveats

- ART indices are appraisal/transaction based and likely smoothed; crisis correlations and volatility can be biased downward. The multi-quarter drawdowns are less vulnerable to that issue than a single-quarter return.
- ARTKIMP is semiannual, so Japan segment comparisons use only its reported observations; missing Q1/Q3 values were neither filled nor converted into quarterly returns.
- The S&P comparison is the price index (^GSPC), not total return. IEF begins in 2002, so 60/40 is intentionally unavailable for Japan and the 2008 GFC rather than estimated from yields.
- Episode windows are stated in `results.json`; alternative start/end dates can change cumulative returns and short-window correlations, but not the basic evidence of sizable art drawdowns.
