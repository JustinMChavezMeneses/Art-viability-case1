"""Quarterly crisis event study for FIN481 Case 1, model M3.

Uses the supplied Bloomberg ARTDAI series and Yahoo Finance market series.  The
definitions below are deliberately explicit: within-window drawdowns are peak to
subsequent trough; recovery is measured from that peak forward through the last
available observation, so an unrecovered prior high remains unrecovered.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ART_PATH = ROOT / ".context/data/artk_quarterly.csv"
OUT.mkdir(parents=True, exist_ok=True)

EPISODES = {
    "japan": ("1986-03-31", "2000-12-31", "Japanese asset-bubble aftermath", "ARTKIMP"),
    "gfc2008": ("2007-12-31", "2012-12-31", "Global financial crisis", None),
    "covid2020": ("2019-12-31", "2021-12-31", "COVID shock", None),
    "infl2022": ("2021-12-31", "2024-12-31", "Inflation/rate shock", None),
}


def yf_quarterly(ticker: str, start: str = "1979-01-01") -> pd.Series:
    raw = yf.download(ticker, start=start, end="2026-10-01", auto_adjust=False,
                      progress=False, threads=False)
    if raw.empty:
        raise RuntimeError(f"Yahoo Finance returned no data for {ticker}")
    field = "Adj Close" if "Adj Close" in raw.columns.get_level_values(0) else "Close"
    value = raw[field]
    if isinstance(value, pd.DataFrame):
        value = value.iloc[:, 0]
    value.index = pd.to_datetime(value.index).tz_localize(None)
    return value.resample("QE").last().rename(ticker)


def simple_returns(levels: pd.Series) -> pd.Series:
    return levels.pct_change().replace([np.inf, -np.inf], np.nan)


def fmt_period(index: pd.DatetimeIndex) -> str:
    return f"{index.min().date()} to {index.max().date()}"


def level_summary(levels: pd.Series, start: str, end: str) -> dict:
    window = levels.loc[start:end].dropna()
    if len(window) < 2:
        return {"available": False}
    running_peak = window.cummax()
    dd = window / running_peak - 1
    trough = dd.idxmin()
    peak = window.loc[:trough].idxmax()
    max_dd = float(dd.loc[trough])
    cum_return = float(window.iloc[-1] / window.iloc[0] - 1)

    # Recovery is from the within-window peak, assessed against all later data.
    prior_peak = float(levels.loc[peak])
    later = levels.loc[peak:].dropna()
    recovered = later[later >= prior_peak]
    recovery_date = recovered.index[1] if len(recovered) > 1 else None
    # If it reattains at the very next retained observation, count it as 0 only
    # when it is the original peak; otherwise recovery uses first post-peak date.
    if recovery_date is not None:
        recovery_q = int((recovery_date.to_period("Q") - peak.to_period("Q")).n)
    else:
        recovery_q = None
    return {
        "available": True,
        "sample_period": fmt_period(window.index),
        "n_obs": int(len(window)),
        "real_or_nominal": "nominal",
        "cumulative_return": cum_return,
        "max_drawdown": max_dd,
        "peak_date": str(peak.date()),
        "trough_date": str(trough.date()),
        "recovery_quarters_from_peak": recovery_q,
        "recovery_date": str(recovery_date.date()) if recovery_date is not None else None,
        "unrecovered_through": None if recovery_date is not None else str(later.index.max().date()),
    }


def correlation_block(art_ret: pd.Series, sp_ret: pd.Series, start: str, end: str) -> dict:
    frame = pd.concat([art_ret, sp_ret], axis=1, join="inner").loc[start:end].dropna()
    return {
        "sample_period": fmt_period(frame.index),
        "n_obs": int(len(frame)),
        "real_or_nominal": "nominal log returns",
        "pearson_correlation": float(frame.iloc[:, 0].corr(frame.iloc[:, 1])),
        "definition": "quarterly log returns",
    }


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def recovery_text(summary: dict) -> str:
    if not summary.get("available"):
        return "n/a"
    if summary["recovery_quarters_from_peak"] is None:
        return f"not recovered through {summary['unrecovered_through']}"
    return f"{summary['recovery_quarters_from_peak']} quarters ({summary['recovery_date']})"


def main() -> None:
    art = pd.read_csv(ART_PATH, parse_dates=["date"]).set_index("date").sort_index()
    # Normalize to midnight quarter-end to match pandas' resampled Yahoo index.
    art.index = art.index.to_period("Q").to_timestamp(how="end").normalize()
    sp = yf_quarterly("^GSPC")
    nikkei = yf_quarterly("^N225")
    ief = yf_quarterly("IEF", "2002-01-01")

    # 60/40 is rebalanced every quarter using simple price returns (S&P 500 and
    # adjusted IEF).  It is intentionally unavailable before IEF begins in 2002.
    p6040_ret = 0.6 * simple_returns(sp) + 0.4 * simple_returns(ief)
    p6040 = (1 + p6040_ret.dropna()).cumprod().rename("60/40")

    series = {"art": art["ARTKAART"], "sp500": sp, "p6040": p6040}
    results = {
        "methodology": {
            "frequency": "quarter-end",
            "returns": "log returns for correlations; simple returns for cumulative returns and 60/40 rebalancing",
            "art_series": "ARTKAART (All Traded Artists)",
            "sp500_series": "Yahoo Finance ^GSPC price index",
            "bond_series": "Yahoo Finance IEF adjusted close; available from 2002, so 60/40 is N/A for Japan and 2008",
            "recovery_definition": "quarters from an episode's within-window high to first later re-attainment of that high; assessed through the final available observation",
            "drawdown_definition": "largest peak-to-subsequent-trough loss within each stated episode window",
        },
        "episodes": {},
    }
    for name, (start, end, label, segment) in EPISODES.items():
        block = {
            "window": f"{start} to {end}",
            "label": label,
            "art": level_summary(series["art"], start, end),
            "sp500": level_summary(series["sp500"], start, end),
            "p6040": level_summary(series["p6040"], start, end),
        }
        if segment:
            block["segment"] = level_summary(art[segment], start, end)
            block["segment_name"] = segment
        # Flat aliases keep the core comparison easy for the rejoin step to read.
        block["art_drawdown"] = block["art"].get("max_drawdown")
        block["segment_drawdown"] = block.get("segment", {}).get("max_drawdown")
        block["sp_drawdown"] = block["sp500"].get("max_drawdown")
        block["p6040_drawdown"] = block["p6040"].get("max_drawdown")
        block["recovery_quarters"] = block["art"].get("recovery_quarters_from_peak")
        results["episodes"][name] = block

    art_lr = np.log(art["ARTKAART"]).diff()
    sp_lr = np.log(sp).diff()
    crisis_windows = {
        "japan": ("1986-03-31", "1995-12-31"),
        "gfc2008": ("2008-06-30", "2009-12-31"),
        "covid2020": ("2020-03-31", "2020-12-31"),
        "infl2022": ("2022-03-31", "2024-12-31"),
    }
    correlations = {name: correlation_block(art_lr, sp_lr, *dates)
                    for name, dates in crisis_windows.items()}
    all_pairs = pd.concat([art_lr.rename("art"), sp_lr.rename("sp")], axis=1, join="inner").dropna()
    crisis_mask = pd.Series(False, index=all_pairs.index)
    for start, end in crisis_windows.values():
        crisis_mask |= (all_pairs.index >= start) & (all_pairs.index <= end)
    correlations["pooled_crises"] = {
        "sample_period": f"{all_pairs.index[crisis_mask].min().date()} to {all_pairs.index[crisis_mask].max().date()} (non-contiguous crisis windows)",
        "n_obs": int(crisis_mask.sum()),
        "real_or_nominal": "nominal log returns",
        "pearson_correlation": float(all_pairs.loc[crisis_mask, "art"].corr(all_pairs.loc[crisis_mask, "sp"])),
        "definition": "pooled quarterly log returns in the four stated crisis windows",
    }
    correlations["calm_periods"] = {
        "sample_period": f"{all_pairs.index[~crisis_mask].min().date()} to {all_pairs.index[~crisis_mask].max().date()} (excluding stated crisis windows)",
        "n_obs": int((~crisis_mask).sum()),
        "real_or_nominal": "nominal log returns",
        "pearson_correlation": float(all_pairs.loc[~crisis_mask, "art"].corr(all_pairs.loc[~crisis_mask, "sp"])),
        "definition": "quarterly log returns outside the four stated crisis windows",
    }
    # A like-for-like modern comparison avoids letting the long Japan window
    # dominate a test of the post-IEF, liquid-market era.
    modern = all_pairs.loc["2002-03-31":]
    modern_crisis = pd.Series(False, index=modern.index)
    for start, end in list(crisis_windows.values())[1:]:
        modern_crisis |= (modern.index >= start) & (modern.index <= end)
    for key, mask, definition in [
        ("modern_crises", modern_crisis, "GFC, COVID, and inflation/rate crisis windows, 2002 onward"),
        ("modern_calm", ~modern_crisis, "quarters outside those three crisis windows, 2002 onward"),
    ]:
        selected = modern.loc[mask]
        correlations[key] = {
            "sample_period": f"{selected.index.min().date()} to {selected.index.max().date()} (non-contiguous where applicable)",
            "n_obs": int(len(selected)),
            "real_or_nominal": "nominal log returns",
            "pearson_correlation": float(selected["art"].corr(selected["sp"])),
            "definition": definition,
        }
    results["corr_crisis_vs_calm"] = correlations
    # Suggested top-level aliases refer to the like-for-like post-2002 test;
    # the all-history and individual-window sensitivity results remain above.
    results["corr_crisis_vs_calm"]["crisis_corr"] = correlations["modern_crises"]["pearson_correlation"]
    results["corr_crisis_vs_calm"]["calm_corr"] = correlations["modern_calm"]["pearson_correlation"]

    # ARTKIMP is published only at June/December. Compute six-month returns on
    # the reported observations (never forward-fill it) and match Nikkei over
    # those exact same six-month intervals.
    imp_levels = art["ARTKIMP"].dropna()
    imp_lr = np.log(imp_levels).diff()
    nik_lr = np.log(nikkei.reindex(imp_levels.index)).diff()
    japan_pair = pd.concat([imp_lr.rename("impressionist"), nik_lr.rename("nikkei")], axis=1, sort=False).loc["1986-03-31":"1995-12-31"].dropna()
    results["japan_art_nikkei_corr"] = {
        "sample_period": fmt_period(japan_pair.index),
        "n_obs": int(len(japan_pair)),
        "real_or_nominal": "nominal log returns",
        "pearson_correlation": float(japan_pair.iloc[:, 0].corr(japan_pair.iloc[:, 1])),
        "definition": "ARTKIMP and Nikkei 225 quarterly log returns; ARTKIMP is semiannual, so only matched June/December observations are used",
    }
    segment_columns = {"imp": "ARTKIMP", "one": "ARTKONE", "six": "ARTKSIX"}
    results["segment_concentration"] = {}
    for key, col in segment_columns.items():
        block = level_summary(art[col], "1986-03-31", "2000-12-31")
        first = art.loc["1986-03-31":"2000-12-31", col].dropna()
        block["runup_from_first_window_observation_to_peak"] = float(
            art.loc[pd.Timestamp(block["peak_date"]), col] / first.iloc[0] - 1
        )
        results["segment_concentration"][key] = block
    results["index_blindness"] = (
        "The supplied ARTDAI history begins in 1980 and captures the Japan episode; a 2000-starting art index would exclude this crisis entirely."
    )

    with (OUT / "results.json").open("w") as f:
        json.dump(results, f, indent=2)

    # Exhibit 1: each asset indexed to the first value in its episode window.
    fig, axes = plt.subplots(2, 2, figsize=(14, 8.5), sharey=False)
    colors = {"art": "#7b2cbf", "sp": "#1d4ed8", "6040": "#059669"}
    for ax, (name, (start, end, label, _)) in zip(axes.flat, EPISODES.items()):
        for key, label2, levels in [("art", "ARTKAART", series["art"]), ("sp", "S&P 500", sp), ("6040", "60/40", p6040)]:
            values = levels.loc[start:end].dropna()
            if len(values):
                ax.plot(values.index, values / values.iloc[0] * 100, lw=2.2, label=label2, color=colors[key])
        ax.axhline(100, color="#94a3b8", lw=0.8)
        ax.set_title(label, loc="left", fontweight="bold")
        ax.set_ylabel("Indexed to 100 at window start")
        ax.xaxis.set_major_locator(mdates.YearLocator(2 if name == "japan" else 1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.grid(axis="y", alpha=.22)
        ax.legend(frameon=False, fontsize=8, loc="best")
    fig.suptitle("Art did not reliably protect against major shocks", fontsize=16, fontweight="bold", y=.98)
    fig.text(.01, .01, "Source: Bloomberg ARTDAI + Yahoo Finance, quarterly. 60/40 = quarterly-rebalanced 60% S&P 500 price return / 40% IEF adjusted return; unavailable pre-2002.", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, .95))
    fig.savefig(OUT / "crisis_drawdowns.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Exhibit 2: Japan episode—segment and equity market, all indexed in 1986Q1.
    fig, ax = plt.subplots(figsize=(12, 6.5))
    plot_series = [(art["ARTKAART"], "All traded artists", "#7b2cbf"),
                   (art["ARTKIMP"], "Impressionist", "#dc2626"),
                   (art["ARTKSIX"], "Low tier", "#f59e0b"),
                   (nikkei, "Nikkei 225", "#1d4ed8")]
    for values, label, color in plot_series:
        values = values.loc["1985-01-01":"2000-12-31"].dropna()
        values = values / values.loc[values.index >= "1986-03-31"].iloc[0] * 100
        ax.plot(values.index, values, label=label, color=color, lw=2.25)
    ax.axvspan(pd.Timestamp("1987-01-01"), pd.Timestamp("1990-12-31"), color="#fee2e2", alpha=.55, label="Japanese buying peak")
    ax.axvline(pd.Timestamp("1990-12-31"), color="#64748b", ls="--", lw=1)
    ax.text(pd.Timestamp("1990-12-31"), ax.get_ylim()[1] * .96, "1990", ha="right", va="top", color="#475569")
    ax.set_title("Japan: concentrated art-segment exposure, not a broad-market hedge", loc="left", fontsize=15, fontweight="bold")
    ax.set_ylabel("Indexed to 100 at 1986Q1 (nearest available observation)")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", alpha=.22)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.text(.01, .01, "Source: Bloomberg ARTDAI + Yahoo Finance, quarterly. ARTKIMP is semiannual (June/December); no returns are forward-filled.", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(OUT / "japan_bubble.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    ep = results["episodes"]
    jp = ep["japan"]
    lines = [
        "# M3 — Crisis / Regime Event Study",
        "",
        "ARTKAART was not a dependable shock hedge: it suffered material peak-to-trough losses in the GFC and 2022 rate shock, while Japan shows the especially severe risk of a crowded segment. Across all four non-contiguous crises (including Japan), pooled art–equity correlation was " + pct(correlations["pooled_crises"]["pearson_correlation"]) + " versus " + pct(correlations["calm_periods"]["pearson_correlation"]) + " in calm quarters; it therefore did not rise in that broad comparison. But in the like-for-like modern sample (2002 onward), it rose to " + pct(correlations["modern_crises"]["pearson_correlation"]) + " in crises versus " + pct(correlations["modern_calm"]["pearson_correlation"]) + " in calm quarters. These short-window correlations are descriptive, but the drawdowns and slow/no recoveries plainly weaken the shock-hedge leg of the thesis.",
        "",
        "## For the memo",
    ]
    for name, label in [("japan", "Japan"), ("gfc2008", "2008 GFC"), ("covid2020", "COVID"), ("infl2022", "2022 inflation/rates")]:
        x = ep[name]
        art_s = x["art"]
        lines.append(f"- **{label} ({x['window']}):** ARTKAART cumulative return {pct(art_s['cumulative_return'])}; maximum drawdown {pct(art_s['max_drawdown'])} (peak {art_s['peak_date']}, trough {art_s['trough_date']}); recovery {recovery_text(art_s)}.")
    lines += [
        f"- **Crisis correlation test:** in the modern 2002+ comparison, art–S&P quarterly log-return correlation was {pct(correlations['modern_crises']['pearson_correlation'])} in {correlations['modern_crises']['n_obs']} crisis observations versus {pct(correlations['modern_calm']['pearson_correlation'])} in {correlations['modern_calm']['n_obs']} calm observations. Adding the long Japan episode reverses the pooled comparison ({pct(correlations['pooled_crises']['pearson_correlation'])} versus {pct(correlations['calm_periods']['pearson_correlation'])}); individual windows are in `results.json`.",
        f"- **Japan crowding:** ARTKIMP ran up {pct(results['segment_concentration']['imp']['runup_from_first_window_observation_to_peak'])} then had a {pct(jp['segment']['max_drawdown'])} maximum drawdown; Tier One ran up {pct(results['segment_concentration']['one']['runup_from_first_window_observation_to_peak'])} then fell {pct(results['segment_concentration']['one']['max_drawdown'])}. ARTKSIX was far smaller (+{100 * results['segment_concentration']['six']['runup_from_first_window_observation_to_peak']:.1f}% run-up, {pct(results['segment_concentration']['six']['max_drawdown'])} drawdown), so the data show concentration rather than literally no low-tier bubble. ARTKIMP–Nikkei matched-half-year return correlation was {pct(results['japan_art_nikkei_corr']['pearson_correlation'])}. A 2000-starting art index would miss this episode entirely; the supplied ARTDAI history starts in 1980 and does not.",
        "",
        "## Caveats",
        "",
        "- ART indices are appraisal/transaction based and likely smoothed; crisis correlations and volatility can be biased downward. The multi-quarter drawdowns are less vulnerable to that issue than a single-quarter return.",
        "- ARTKIMP is semiannual, so Japan segment comparisons use only its reported observations; missing Q1/Q3 values were neither filled nor converted into quarterly returns.",
        "- The S&P comparison is the price index (^GSPC), not total return. IEF begins in 2002, so 60/40 is intentionally unavailable for Japan and the 2008 GFC rather than estimated from yields.",
        "- Episode windows are stated in `results.json`; alternative start/end dates can change cumulative returns and short-window correlations, but not the basic evidence of sizable art drawdowns.",
    ]
    (OUT / "findings.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
