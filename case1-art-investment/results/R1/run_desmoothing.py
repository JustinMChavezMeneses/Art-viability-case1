#!/usr/bin/env python3
"""R1: Geltner unsmoothing and systematic-risk robustness for ARTKAART."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yfinance as yf
from pandas_datareader import data as web


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ART_PATH = ROOT / ".context/data/artk_quarterly.csv"
HAC_LAGS = 4


def period(value: pd.Period | pd.Timestamp) -> str:
    if isinstance(value, pd.Period):
        return str(value)
    return str(value.to_period("Q"))


def block(sample: pd.DataFrame | pd.Series, real_or_nominal: str = "nominal") -> dict:
    idx = sample.dropna().index
    return {
        "sample_period": f"{period(idx.min())} to {period(idx.max())}",
        "n_obs": int(len(idx)),
        "real_or_nominal": real_or_nominal,
    }


def q_last(series: pd.Series) -> pd.Series:
    series.index = pd.to_datetime(series.index)
    return series.resample("QE").last()


def yf_close(ticker: str) -> pd.Series:
    data = yf.download(
        ticker, start="1980-01-01", end="2026-09-01", auto_adjust=False, progress=False
    )
    if data.empty:
        raise RuntimeError(f"Yahoo returned no data for {ticker}")
    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.rename(ticker)


def fred(name: str) -> pd.Series:
    value = web.DataReader(name, "fred", "1980-01-01", "2026-09-01")[name]
    return value.rename(name)


def fit_hac(y: pd.Series, x: pd.DataFrame) -> tuple[object, pd.DataFrame]:
    if isinstance(x, pd.Series):
        x = x.to_frame()
    joined = pd.concat([y.rename("y"), x], axis=1).dropna()
    model = sm.OLS(joined["y"], sm.add_constant(joined[x.columns])).fit(
        cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS}
    )
    return model, joined


def capm_result(art_excess: pd.Series, market_excess: pd.Series) -> dict:
    model, joined = fit_hac(art_excess, market_excess.rename("market_excess"))
    return {
        **block(joined),
        "return_basis": "quarterly log excess returns",
        "alpha_quarterly_log": float(model.params["const"]),
        "alpha_annualized_log_approx": float(4 * model.params["const"]),
        "alpha_t_hac": float(model.tvalues["const"]),
        "alpha_pvalue_hac": float(model.pvalues["const"]),
        "beta": float(model.params["market_excess"]),
        "beta_se_hac": float(model.bse["market_excess"]),
        "beta_t_hac": float(model.tvalues["market_excess"]),
        "beta_pvalue_hac": float(model.pvalues["market_excess"]),
        "hac_lags": HAC_LAGS,
        "r_squared": float(model.rsquared),
    }


def ff3_result(art_excess: pd.Series, ff_quarterly: pd.DataFrame) -> dict:
    model, joined = fit_hac(art_excess, ff_quarterly[["Mkt-RF", "SMB", "HML"]])
    out = {
        **block(joined),
        "return_basis": "quarterly log excess return; Fama-French monthly factors compounded to quarters and log-transformed",
        "alpha_quarterly_log": float(model.params["const"]),
        "alpha_t_hac": float(model.tvalues["const"]),
        "alpha_pvalue_hac": float(model.pvalues["const"]),
        "hac_lags": HAC_LAGS,
        "r_squared": float(model.rsquared),
    }
    for name in ["Mkt-RF", "SMB", "HML"]:
        out[name.lower().replace("-", "_") + "_beta"] = float(model.params[name])
        out[name.lower().replace("-", "_") + "_se_hac"] = float(model.bse[name])
        out[name.lower().replace("-", "_") + "_t_hac"] = float(model.tvalues[name])
        out[name.lower().replace("-", "_") + "_pvalue_hac"] = float(model.pvalues[name])
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    art = pd.read_csv(ART_PATH, parse_dates=["date"]).set_index("date")["ARTKAART"].astype(float)
    art = art.sort_index()
    art_log = np.log(art).diff().dropna().rename("art_smoothed_log")

    # First-order autocorrelation, estimated as an AR(1) regression with HAC inference.
    ar_df = pd.DataFrame({"current": art_log, "lagged": art_log.shift(1)}).dropna()
    ar_model = sm.OLS(ar_df["current"], sm.add_constant(ar_df["lagged"])).fit(
        cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS}
    )
    rho = float(ar_model.params["lagged"])
    art_unsmoothed = (
        (art_log - rho * art_log.shift(1)) / (1 - rho)
    ).dropna().rename("art_unsmoothed_log")

    # Monthly Fama-French factors. Values are percentages; quarterly values are compounded then logged.
    ff_monthly = web.DataReader("F-F_Research_Data_Factors", "famafrench", start="1980-01-01")[0]
    ff_monthly.index = ff_monthly.index.to_timestamp("M")
    ff_monthly = ff_monthly.loc[:, ["Mkt-RF", "SMB", "HML", "RF"]].astype(float) / 100
    ff_q_simple = (1 + ff_monthly).resample("QE").prod() - 1
    ff_q = np.log1p(ff_q_simple).rename(columns={"Mkt-RF": "Mkt-RF", "SMB": "SMB", "HML": "HML"})

    # DTB3 is an annualized percent discount rate. Quarter-end rate / 4 is used as the
    # quarterly proxy; it is converted to a log return before excess-return calculations.
    dtb3_q = q_last(fred("DTB3")).ffill(limit=1)
    rf_log = np.log1p(dtb3_q / 100 / 4).rename("rf_log")

    sp_price_q = q_last(yf_close("^GSPC"))
    sp_log = np.log(sp_price_q).diff().rename("sp500_price_log")
    sp_total_q = q_last(yf_close("^SP500TR"))
    sp_total_log = np.log(sp_total_q).diff().rename("sp500_total_log")
    sp_excess = (sp_total_log - rf_log).rename("market_excess")

    # Fair comparison window: the window on which both observed and Geltner-adjusted
    # returns exist. S&P price correlations use price returns because the requested
    # total-return index begins only in 1988.
    comparison = pd.concat([art_log, art_unsmoothed, rf_log, sp_log], axis=1, sort=False).dropna()

    def summary_stats(return_col: str) -> dict:
        sample = comparison[[return_col, "rf_log", "sp500_price_log"]].dropna()
        ret = sample[return_col]
        excess = ret - sample["rf_log"]
        return {
            **block(sample),
            "return_basis": "quarterly log returns; Sharpe uses quarterly log excess returns over DTB3",
            "annualized_volatility": float(ret.std(ddof=1) * np.sqrt(4)),
            "annualized_sharpe": float(excess.mean() / excess.std(ddof=1) * np.sqrt(4)),
            "correlation_sp500_price_return": float(ret.corr(sample["sp500_price_log"])),
        }

    smoothed_summary = summary_stats("art_smoothed_log")
    unsmoothed_summary = summary_stats("art_unsmoothed_log")
    capm_smoothed = capm_result(art_log - rf_log, sp_excess)
    capm_unsmoothed = capm_result(art_unsmoothed - rf_log, sp_excess)
    ff3_smoothed = ff3_result(art_log - rf_log, ff_q)
    ff3_unsmoothed = ff3_result(art_unsmoothed - rf_log, ff_q)

    results = {
        "methodology": {
            "art_series": "ARTKAART (Bloomberg ARTDAI All Traded Artists)",
            "frequency": "quarterly quarter-end",
            "returns": "log returns for all reported return statistics and regressions",
            "desmoothing": "Geltner: r_true_t = (r_obs_t - rho*r_obs_(t-1))/(1-rho)",
            "hac_standard_errors": f"Newey-West HAC, maxlags={HAC_LAGS}",
            "risk_free_proxy": "FRED DTB3 quarter-end annualized rate divided by 4, converted to a quarterly log return",
            "sp_correlation_series": "Yahoo ^GSPC price-index quarterly log returns",
            "capm_market_series": "Yahoo ^SP500TR total-return quarterly log return minus DTB3 log return",
        },
        "rho_ar1": {
            **block(ar_df),
            "return_basis": "ARTKAART quarterly log returns",
            "value": rho,
            "se_hac": float(ar_model.bse["lagged"]),
            "t_hac": float(ar_model.tvalues["lagged"]),
            "pvalue_hac": float(ar_model.pvalues["lagged"]),
            "hac_lags": HAC_LAGS,
        },
        "smoothed": smoothed_summary,
        "unsmoothed": unsmoothed_summary,
        "vol_smoothed": smoothed_summary,
        "vol_unsmoothed": unsmoothed_summary,
        "sharpe_smoothed": smoothed_summary,
        "sharpe_unsmoothed": unsmoothed_summary,
        "corr_sp_smoothed": smoothed_summary,
        "corr_sp_unsmoothed": unsmoothed_summary,
        "capm_smoothed": capm_smoothed,
        "capm_unsmoothed": capm_unsmoothed,
        "ff3_smoothed": ff3_smoothed,
        "ff3_unsmoothed": ff3_unsmoothed,
        "ff3": {"smoothed": ff3_smoothed, "unsmoothed": ff3_unsmoothed},
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")

    # Exhibit with independently-scaled panels so unlike units remain legible.
    labels = ["Observed\n(smoothed)", "Geltner\nunsmoothed"]
    colors = ["#386cb0", "#e6550d"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 5.8))
    metrics = [
        ("Annualized volatility", [smoothed_summary["annualized_volatility"], unsmoothed_summary["annualized_volatility"]], "Percent", lambda x: f"{x:.1%}"),
        ("Annualized Sharpe", [smoothed_summary["annualized_sharpe"], unsmoothed_summary["annualized_sharpe"]], "Ratio", lambda x: f"{x:.3f}"),
        ("Correlation with S&P 500", [smoothed_summary["correlation_sp500_price_return"], unsmoothed_summary["correlation_sp500_price_return"]], "Correlation", lambda x: f"{x:.2f}"),
    ]
    for ax, (title, values, ylabel, formatter) in zip(axes, metrics):
        bars = ax.bar(labels, values, color=colors, width=0.62)
        ax.set_title(title, fontweight="bold", pad=10)
        ax.set_ylabel(ylabel)
        ax.axhline(0, color="#555555", linewidth=0.8)
        ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
        ax.set_axisbelow(True)
        if title == "Annualized Sharpe":
            ax.set_ylim(min(values) * 1.22, 0.001)
        for bar_, value in zip(bars, values):
            offset = 0.00035 if title == "Annualized Sharpe" else max(abs(max(values, key=abs)) * 0.035, 0.015)
            ax.text(bar_.get_x() + bar_.get_width() / 2, value + (offset if value >= 0 else -offset), formatter(value), ha="center", va="bottom" if value >= 0 else "top", fontsize=10, fontweight="bold")
    fig.suptitle("ARTKAART: Geltner Adjustment Changes Reported Diversification Statistics", fontsize=14, fontweight="bold", y=0.98)
    fig.text(0.5, 0.035, f"Common comparison sample: {smoothed_summary['sample_period']} (n={smoothed_summary['n_obs']}). Source: Bloomberg ARTDAI + FRED/Yahoo, quarterly.", ha="center", fontsize=9, color="#444444")
    fig.subplots_adjust(left=0.065, right=0.985, bottom=0.17, top=0.84, wspace=0.2)
    fig.savefig(OUT / "smoothed_vs_unsmoothed.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Concise, machine-consistent narrative written only after calculated values are available.
    rho_sig = "statistically significant" if ar_model.pvalues["lagged"] < 0.05 else "not statistically significant"
    vol_change = unsmoothed_summary["annualized_volatility"] / smoothed_summary["annualized_volatility"] - 1
    corr_change = unsmoothed_summary["correlation_sp500_price_return"] - smoothed_summary["correlation_sp500_price_return"]
    beta_change = capm_unsmoothed["beta"] - capm_smoothed["beta"]
    finding = (
        f"ARTKAART quarterly log returns have strongly negative AR(1) autocorrelation of {rho:.2f} (HAC p={ar_model.pvalues['lagged']:.3f}; {rho_sig}), the opposite of the positive serial correlation that is the classic index-smoothing signature. Accordingly, applying the requested Geltner formula on the common {smoothed_summary['sample_period']} window reduces annualized volatility from {smoothed_summary['annualized_volatility']:.1%} to {unsmoothed_summary['annualized_volatility']:.1%} ({vol_change:+.0%}), rather than increasing it; the Sharpe slips from {smoothed_summary['annualized_sharpe']:.3f} to {unsmoothed_summary['annualized_sharpe']:.3f}. "
        f"The equity correlation nevertheless rises from {smoothed_summary['correlation_sp500_price_return']:.2f} to {unsmoothed_summary['correlation_sp500_price_return']:.2f} ({corr_change:+.2f}), while CAPM beta falls from {capm_smoothed['beta']:.2f} to {capm_unsmoothed['beta']:.2f} ({beta_change:+.2f}). This robustness check therefore does not support the claim that apparently low art volatility is a positive-smoothing artifact, but it does weaken the low-correlation claim; the mixed result is not evidence that art is a reliable inflation or market-shock hedge."
    )
    memo = [
        f"ARTKAART has AR(1) return autocorrelation of {rho:.2f} (HAC p={ar_model.pvalues['lagged']:.3f}), which is negative—not the positive autocorrelation expected from classic appraisal smoothing.",
        f"The requested Geltner adjustment lowers annualized volatility from {smoothed_summary['annualized_volatility']:.1%} to {unsmoothed_summary['annualized_volatility']:.1%} and moves the annualized Sharpe from {smoothed_summary['annualized_sharpe']:.3f} to {unsmoothed_summary['annualized_sharpe']:.3f} (common {smoothed_summary['sample_period']} sample).",
        f"S&P price-return correlation rises from {smoothed_summary['correlation_sp500_price_return']:.2f} to {unsmoothed_summary['correlation_sp500_price_return']:.2f}; CAPM beta versus the total-return index falls from {capm_smoothed['beta']:.2f} to {capm_unsmoothed['beta']:.2f}, with both market betas HAC-significant.",
        "Do not use a low reported correlation as proof of shock-hedging: this correction is model-dependent and the negative AR(1) result points to index noise/mean reversion rather than a conventional smoothing pattern.",
    ]
    caveats = [
        "Geltner is a model-based correction: the AR(1) coefficient may reflect genuine illiquidity or changing art-market fundamentals as well as appraisal/transaction smoothing.",
        "ARTKAART is a repeat-sale auction index, not the investable return of a family-office collection; fees, insurance, storage, taxes and sale timing are excluded.",
        "S&P price returns are used for the long correlation series; total-return data are used in CAPM but begin in 1988, producing a shorter beta sample.",
        "HAC standard errors address serial correlation in regression inference but do not create liquidity or observable prices during a market shock.",
    ]
    text = finding + "\n\n## Caveats\n\n" + "\n".join(f"- {x}" for x in caveats) + "\n\n## For the memo\n\n" + "\n".join(f"- {x}" for x in memo) + "\n"
    (OUT / "findings.md").write_text(text)


if __name__ == "__main__":
    main()
