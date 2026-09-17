#!/usr/bin/env python3
"""M2: quarterly art-inflation regressions with Newey-West (4-lag) inference."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yfinance as yf
from pandas_datareader import data as web


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / ".context" / "data" / "artk_quarterly.csv"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
HAC_LAGS = 4


def fred(series: str, start: str, end: str) -> pd.Series:
    """Fetch FRED through pandas-datareader, with FRED's keyless CSV as a retry fallback."""
    try:
        return web.DataReader(series, "fred", start, end)[series]
    except Exception as first_error:
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urlencode(
            {"id": series, "cos": "Quarterly", "coed": end, "fq": "Quarterly"}
        )
        try:
            frame = pd.read_csv(url, parse_dates=["observation_date"])
            return frame.set_index("observation_date")[series].replace(".", np.nan).astype(float)
        except Exception as fallback_error:
            raise RuntimeError(f"FRED failed for {series}: {first_error}; fallback: {fallback_error}")


def quarter_last(series: pd.Series) -> pd.Series:
    series.index = pd.to_datetime(series.index)
    return series.resample("QE").last()


def period(index: pd.Index) -> str:
    quarters = pd.DatetimeIndex(index).to_period("Q")
    return f"{quarters.min()} to {quarters.max()}"


def fmt_float(x: float | np.floating | None) -> float | None:
    return None if x is None or not np.isfinite(x) else float(x)


def regression(frame: pd.DataFrame, include_expected: bool, label: str) -> tuple[dict, object]:
    cols = ["art_nominal", "inflation", "mkt_ret"] + (["delta_expected_inflation"] if include_expected else [])
    data = frame.loc[:, cols].dropna().copy()
    xcols = ["inflation"] + (["delta_expected_inflation"] if include_expected else []) + ["mkt_ret"]
    model = sm.OLS(data["art_nominal"], sm.add_constant(data[xcols])).fit(
        cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS}
    )
    beta = model.params["inflation"]
    se = model.bse["inflation"]
    result = {
        "label": label,
        "specification": "nominal quarterly log art return = alpha + realized CPI inflation + "
        + ("change in 10Y breakeven inflation + " if include_expected else "")
        + "S&P 500 quarterly log return",
        "inflation_definition": "CPIAUCSL quarter-over-quarter log change, annualized (4 × log change)",
        "market_definition": "^GSPC quarter-over-quarter log price return",
        "beta_inflation": fmt_float(beta),
        "se_hac": fmt_float(se),
        "t_vs_0": fmt_float(beta / se),
        "t_vs_1": fmt_float((beta - 1) / se),
        "p_vs_1_two_sided": fmt_float(model.t_test("inflation = 1").pvalue),
        "ci_95_hac": [fmt_float(beta - 1.96 * se), fmt_float(beta + 1.96 * se)],
        "r2": fmt_float(model.rsquared),
        "n_obs": int(model.nobs),
        "sample_period": period(data.index),
        "real_or_nominal": "nominal",
        "hac_lags": HAC_LAGS,
        "coefficients": {name: fmt_float(value) for name, value in model.params.items()},
        "hac_standard_errors": {name: fmt_float(value) for name, value in model.bse.items()},
    }
    return result, model


def real_return_regression(frame: pd.DataFrame) -> dict:
    data = frame[["art_real", "inflation"]].dropna()
    model = sm.OLS(data["art_real"], sm.add_constant(data["inflation"])).fit(
        cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS}
    )
    beta = model.params["inflation"]
    se = model.bse["inflation"]
    return {
        "specification": "real quarterly log art return = alpha + realized CPI inflation",
        "inflation_definition": "CPIAUCSL quarter-over-quarter log change, annualized (4 × log change)",
        "beta_inflation": fmt_float(beta),
        "se_hac": fmt_float(se),
        "t_vs_0": fmt_float(beta / se),
        "r2": fmt_float(model.rsquared),
        "n_obs": int(model.nobs),
        "sample_period": period(data.index),
        "real_or_nominal": "real",
        "hac_lags": HAC_LAGS,
        "coefficients": {name: fmt_float(value) for name, value in model.params.items()},
        "hac_standard_errors": {name: fmt_float(value) for name, value in model.bse.items()},
    }


def main() -> None:
    art = pd.read_csv(DATA, parse_dates=["date"]).set_index("date")["ARTKAART"].astype(float)
    art_nominal = np.log(art).diff().rename("art_nominal")
    cpi = fred("CPIAUCSL", "1980-01-01", "2026-09-16")
    breakeven = fred("T10YIE", "2003-01-01", "2026-09-16")
    market_raw = yf.download("^GSPC", start="1980-01-01", end="2026-09-17", auto_adjust=True, progress=False)
    if market_raw.empty:
        raise RuntimeError("yfinance returned no ^GSPC observations")
    close = market_raw["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    market = np.log(quarter_last(close)).diff().rename("mkt_ret")

    inflation = (4 * np.log(quarter_last(cpi)).diff()).rename("inflation")
    expected_change = (quarter_last(breakeven).diff() / 100).rename("delta_expected_inflation")
    panel = pd.concat([art_nominal, inflation, expected_change, market], axis=1).sort_index()
    panel["art_real"] = panel["art_nominal"] - panel["inflation"]

    full, _ = regression(panel, False, "Full sample")
    plus_2003, _ = regression(panel.loc[panel.index >= "2003-01-01"], True, "2003+ with expected inflation")
    pre_2000, _ = regression(panel.loc[panel.index < "2000-01-01"], False, "Pre-2000")
    modern, _ = regression(panel.loc[panel.index >= "2000-01-01"], False, "2000+")
    high, _ = regression(panel.loc[panel["inflation"] > 0.04], False, "High inflation (>4% annualized CPI)")
    real = real_return_regression(panel)

    output = {
        "methodology": {
            "frequency": "quarterly, quarter-end aligned to ARTKAART",
            "return_convention": "log returns; inflation is annualized quarterly CPI log inflation",
            "inference": "OLS coefficients with Newey-West HAC standard errors (maxlags=4)",
            "primary_art_series": "Bloomberg ARTDAI ARTKAART",
            "data_sources": "Bloomberg ARTDAI (provided file), FRED CPIAUCSL and T10YIE, Yahoo Finance ^GSPC",
        },
        "reg_full": full,
        "reg_2003plus": plus_2003,
        "reg_pre2000": pre_2000,
        "reg_2000plus": modern,
        "reg_highinfl": high,
        "real_return_inflation_beta": real,
    }
    (OUT / "results.json").write_text(json.dumps(output, indent=2) + "\n")

    regime_names = ["Full", "Pre-2000", "2000+", "High inflation\n(>4%)"]
    regime_results = [full, pre_2000, modern, high]
    betas = np.array([r["beta_inflation"] for r in regime_results])
    ses = np.array([r["se_hac"] for r in regime_results])
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    x = np.arange(len(regime_names))
    ax.errorbar(x, betas, yerr=1.96 * ses, fmt="o", color="#12355b", ecolor="#4f7cac", capsize=5, lw=2, ms=8)
    ax.axhline(0, color="#626262", lw=1)
    ax.axhline(1, color="#b53a3a", ls="--", lw=1.5, label="Full pass-through (β = 1)")
    ax.set_xticks(x, regime_names)
    ax.set_ylabel("Inflation beta on nominal art return")
    ax.set_title("ARTKAART Inflation Beta Is Below Full Pass-Through Across Regimes")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.2)
    for i, r in enumerate(regime_results):
        ax.annotate(f"n={r['n_obs']}", (i, betas[i]), xytext=(0, 11), textcoords="offset points", ha="center", fontsize=9)
    fig.text(0.01, 0.01, "95% Newey-West HAC confidence intervals (4 lags). Source: Bloomberg ARTDAI + FRED/Yahoo, quarterly.", fontsize=8.5)
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(OUT / "inflation_beta_regimes.png", dpi=220, bbox_inches="tight")


if __name__ == "__main__":
    main()
