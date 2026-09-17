# AGENT M3 — Crisis / Regime Event Study (incl. Japanese asset bubble)

**First read `.context/agent_prompts/00_shared_context.md` in full**, and also read
`.context/data/japan_bubble_facts.md`. Then do ONLY this model. Output dir: `.context/outputs/M3/`.

## Question
How does art behave in shocks — does it hedge, or do correlations spike exactly when you need
diversification (brief Q6/Q8/Q9)? Raw data preview: 2008 −35%, 2020 −5%, 2022 −24%, Japan −56%
(broad) / −65% (Impressionist) / −88% (Tier One).

## Episodes (four)
1. **Japanese asset bubble ~1986–1998** — THE crowded-trade case (Q9). Use `ARTKIMP` (Impressionist,
   the segment Japanese capital piled into) + `ARTKAART`, vs **Nikkei 225 (`^N225`)**. Confirm the
   real peak/trough (broad peak ≈1989Q4, trough ≈1995Q3; Impressionist deeper). Report the −%,
   recovery time, and that **low-tier `ARTKSIX` had NO bubble** — proof the mania was concentrated.
2. **2008 GFC** — art vs S&P vs 60/40; note art's lag (peaked 2008Q2, not late 2007).
3. **2020 COVID** — art vs S&P.
4. **2022 inflation/rate shock** — art vs S&P vs 60/40; the −24% lagged bleed into 2024.

## Do
1. For each episode: cumulative return, **max drawdown**, and **recovery time** for ARTKAART (and the
   relevant segment) vs S&P and vs a 60/40 (0.6·S&P+0.4·IEF, or bond-yield proxy pre-2002).
2. **Black-swan correlation test (Q8):** compute art–equity return correlation **inside crisis windows**
   vs **calm periods**. Does it JUMP in crises (hedge fails when needed)? This is the core M3 result.
3. Japan crowded-trade quantification: ARTKIMP run-up and crash magnitudes, art-vs-Nikkei correlation
   during 1986–1995, and the segment concentration (IMP/Tier-One crashed, ARTKSIX did not).
4. Note the **index-blindness point (Q8):** any index starting at 2000 would miss Japan entirely — but
   OUR data starts 1980, so we can actually show it. Say so.

## results.json (suggested keys)
`episodes` {japan, gfc2008, covid2020, infl2022} each {art_drawdown, segment_drawdown, sp_drawdown,
p6040_drawdown, recovery_quarters, window}, `corr_crisis_vs_calm` {crisis_corr, calm_corr},
`japan_art_nikkei_corr`, `segment_concentration` {imp, one, six}, per-block `sample_period`.

## Exhibits
- `crisis_drawdowns.png` — indexed art vs S&P vs 60/40 across the four episodes (small multiples or overlay).
- `japan_bubble.png` — ARTKIMP vs Nikkei, 1985–2000, marked peak/trough.

## Verdict to state in findings.md
Does art hedge shocks, or do correlations spike in crises (Q8) and is the downside worst exactly
where the money concentrated (Q9)? This is likely the paper's load-bearing section — it is most
robust to smoothing (multi-quarter windows). State support/weaken/kill for the shock-hedge leg.
