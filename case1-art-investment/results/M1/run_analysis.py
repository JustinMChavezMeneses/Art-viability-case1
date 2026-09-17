"""M1: quarterly art diversification analysis.

Run from the repository root with .venv/bin/python .context/outputs/M1/run_analysis.py.
Fetches raw market/macro data directly from Yahoo Finance and FRED, then writes the
machine-readable results and the two requested publication exhibits.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ART_FILE = ROOT / ".context/data/artk_quarterly.csv"
START, END = "1980-01-01", "2026-07-01"  # Yahoo end date is exclusive
SOURCE_NOTE = "Source: Bloomberg ARTDAI + FRED/Yahoo, quarterly"


def yahoo_close(ticker: str) -> pd.Series:
    """Fetch a daily adjusted-close series, retrying once as required."""
    error = None
    for attempt in range(2):
        try:
            frame = yf.download(ticker, start=START, end=END, auto_adjust=True,
                                progress=False, threads=False)
            if frame.empty:
                raise ValueError("Yahoo returned no rows")
            if isinstance(frame.columns, pd.MultiIndex):
                series = frame["Close"].iloc[:, 0]
            else:
                series = frame["Close"]
            return series.rename(ticker)
        except Exception as exc:  # yfinance's error types vary by version
            error = exc
            if attempt == 0:
                time.sleep(1)
    raise RuntimeError(f"Yahoo {ticker}: {error}")


def fred_series(symbol: str) -> pd.Series:
    """Fetch a FRED daily/monthly series, retrying once as required."""
    error = None
    for attempt in range(2):
        try:
            frame = pdr.DataReader(symbol, "fred", START, END)
            if frame.empty:
                raise ValueError("FRED returned no rows")
            return frame[symbol].rename(symbol)
        except Exception as exc:
            error = exc
            if attempt == 0:
                time.sleep(1)
    raise RuntimeError(f"FRED {symbol}: {error}")


def q_last(series: pd.Series) -> pd.Series:
    return series.sort_index().resample("QE").last()


def log_return(levels: pd.Series) -> pd.Series:
    return np.log(levels / levels.shift(1))


def period(series: pd.Series) -> dict:
    clean = series.dropna()
    return {
        "sample_period": (f"{clean.index.min():%Y-%m-%d} to {clean.index.max():%Y-%m-%d}"
                          if not clean.empty else None),
        "n_obs": int(clean.size),
    }


def json_safe(value):
    if isinstance(value, (np.floating, float)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return value


def pairwise_matrix(frame: pd.DataFrame, method: str) -> tuple[dict, dict, dict]:
    corr = frame.corr(method=method, min_periods=3)
    nobs = pd.DataFrame(index=frame.columns, columns=frame.columns, dtype=object)
    samples = pd.DataFrame(index=frame.columns, columns=frame.columns, dtype=object)
    for col_a in frame.columns:
        for col_b in frame.columns:
            pair = frame[[col_a, col_b]].dropna()
            nobs.loc[col_a, col_b] = len(pair)
            samples.loc[col_a, col_b] = (
                f"{pair.index.min():%Y-%m-%d} to {pair.index.max():%Y-%m-%d}"
                if not pair.empty else None
            )
    return corr.to_dict(), nobs.to_dict(), samples.to_dict()


def correlation_stat(a: pd.Series, b: pd.Series, method: str = "pearson") -> dict:
    pair = pd.concat([a, b], axis=1).dropna()
    return {
        "value": float(pair.iloc[:, 0].corr(pair.iloc[:, 1], method=method)),
        **period(pair.iloc[:, 0]),
        "real_or_nominal": "nominal",
    }


def semiannual_asset_returns(levels: pd.DataFrame, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Use end-Jun/end-Dec levels to match semestral art observations; no interpolation."""
    picked = levels.reindex(dates, method=None)
    return np.log(picked / picked.shift(1))


def draw_heatmap(corr: pd.DataFrame) -> None:
    # Do not render an empty row/column when a required source failed; the omission is
    # explicitly disclosed in the source note and results metadata.
    corr = corr.dropna(axis=0, how="all").dropna(axis=1, how="all")
    labels = list(corr.columns)
    fig, ax = plt.subplots(figsize=(11.5, 9.5))
    image = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(labels)), labels, rotation=42, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr.iloc[i, j]
            if pd.notna(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8,
                        color="white" if abs(val) > 0.52 else "black")
    fig.colorbar(image, ax=ax, shrink=0.82, label="Pearson correlation")
    ax.set_title("Returns Correlation Matrix: Art's Measured Market Correlation",
                 weight="bold", pad=16)
    missing_note = (" Gold omitted: specified FRED series unavailable at retrieval."
                    if "Gold" not in labels else "")
    fig.subplots_adjust(bottom=0.20, top=0.91, right=0.90)
    fig.text(0.01, 0.025,
             SOURCE_NOTE + ". Quarterly log returns; DGS10 is quarterly yield change and VIX is level." + missing_note,
             fontsize=8, color="#444444")
    fig.savefig(OUT / "corr_heatmap.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def draw_rolling(rolling_sp: pd.Series, rolling_gold: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    ax.plot(rolling_sp.index, rolling_sp, lw=2.1, color="#1565c0", label="Art vs S&P 500")
    if rolling_gold.notna().any():
        ax.plot(rolling_gold.index, rolling_gold, lw=2.1, color="#b26a00", label="Art vs Gold")
    ax.axhline(0, color="#333333", lw=0.8)
    ax.set_ylim(-1, 1)
    ax.set_ylabel("20-quarter Pearson correlation")
    ax.set_xlabel("Quarter end")
    title = ("Five-Year Rolling Correlation: Art vs S&P 500 and Gold"
             if rolling_gold.notna().any() else "Five-Year Rolling Correlation: Art vs S&P 500")
    ax.set_title(title, weight="bold", pad=14)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    gold_note = "" if rolling_gold.notna().any() else " FRED's specified gold series was unavailable at retrieval."
    fig.subplots_adjust(bottom=0.18, top=0.90, left=0.10, right=0.98)
    fig.text(0.01, 0.025, SOURCE_NOTE + ". ARTKAART quarterly log returns; 20-quarter rolling window." + gold_note,
             fontsize=8, color="#444444")
    fig.savefig(OUT / "rolling_corr.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    art = pd.read_csv(ART_FILE, parse_dates=["date"]).set_index("date").sort_index()
    art.index = art.index.to_period("Q").to_timestamp("Q")
    failures: list[str] = []

    market = {}
    for ticker in ["^GSPC", "IEF", "VNQ"]:
        try:
            market[ticker] = q_last(yahoo_close(ticker))
        except RuntimeError as exc:
            failures.append(str(exc).split("\n", 1)[0])

    macro = {}
    for symbol in ["GOLDAMGBD228NLBM", "DGS10", "CPIAUCSL", "CSUSHPINSA", "VIXCLS"]:
        try:
            macro[symbol] = q_last(fred_series(symbol))
        except RuntimeError as exc:
            failures.append(str(exc).split("\n", 1)[0])

    if "^GSPC" not in market:
        raise RuntimeError("S&P 500 is required for M1 and could not be downloaded. " + "; ".join(failures))

    levels = pd.DataFrame(index=art.index)
    source_map = {
        "S&P 500": market.get("^GSPC"),
        "Gold": macro.get("GOLDAMGBD228NLBM"),
        "10Y Treasury yield": macro.get("DGS10"),
        "IEF": market.get("IEF"),
        "CPI": macro.get("CPIAUCSL"),
        "REITs": market.get("VNQ"),
        "Home prices": macro.get("CSUSHPINSA"),
        "VIX": macro.get("VIXCLS"),
    }
    for name, series in source_map.items():
        levels[name] = series.reindex(art.index) if series is not None else np.nan

    returns = pd.DataFrame({
        "All Traded Art": log_return(art["ARTKAART"]),
        "S&P 500": log_return(levels["S&P 500"]),
        "Gold": log_return(levels["Gold"]),
        "10Y yield change (pp)": levels["10Y Treasury yield"].diff(),
        "IEF": log_return(levels["IEF"]),
        "CPI inflation": log_return(levels["CPI"]),
        "REITs": log_return(levels["REITs"]),
        "Home prices": log_return(levels["Home prices"]),
        "VIX level": levels["VIX"],
    })
    # Restrict all calculations to the supplied ARTDAI calendar, never forward filling gaps.
    returns = returns.loc[art.index]

    pearson_dict, n_dict, samples_dict = pairwise_matrix(returns, "pearson")
    spearman_dict, _, _ = pairwise_matrix(returns, "spearman")
    pearson = pd.DataFrame(pearson_dict).reindex(index=returns.columns, columns=returns.columns)

    art_sp = correlation_stat(returns["All Traded Art"], returns["S&P 500"])
    art_sp["method"] = "Pearson quarterly log returns"
    art_sp_levels = correlation_stat(art["ARTKAART"], levels["S&P 500"])
    art_sp_levels["method"] = "Pearson quarter-end price/index levels"
    art_sp_levels["label"] = "spurious (levels)"

    rolling_sp = returns["All Traded Art"].rolling(20, min_periods=20).corr(returns["S&P 500"])
    rolling_gold = returns["All Traded Art"].rolling(20, min_periods=20).corr(returns["Gold"])

    # Use simple weights for the 60/40 portfolio, then convert the period return to a log return.
    simple_sp = np.expm1(returns["S&P 500"])
    simple_ief = np.expm1(returns["IEF"])
    simple_art = np.expm1(returns["All Traded Art"])
    diversified = pd.DataFrame({"art": simple_art, "sp": simple_sp, "ief": simple_ief}).dropna()
    base_6040 = 0.60 * diversified["sp"] + 0.40 * diversified["ief"]
    portfolio_4pct = 0.04 * diversified["art"] + 0.576 * diversified["sp"] + 0.384 * diversified["ief"]
    art_log = np.log1p(diversified["art"])
    base_log = np.log1p(base_6040)
    port_log = np.log1p(portfolio_4pct)
    art_6040 = correlation_stat(art_log, base_log)
    art_6040["method"] = "Pearson correlation: art log return vs 60/40 log return"

    covariance = np.cov(np.vstack([art_log, base_log, port_log]), ddof=1)
    variance_base = float(np.var(base_log, ddof=1))
    variance_port = float(np.var(port_log, ddof=1))
    contribution = 0.04 * float(np.cov(art_log, port_log, ddof=1)[0, 1])
    # This is the standard component contribution, whose components sum to portfolio variance.
    marginal = {
        "definition": "At 4% art, component variance contribution = w_art × Cov(r_art, r_portfolio); portfolio holds 57.6% S&P, 38.4% IEF, 4.0% art.",
        "component_variance_contribution": contribution,
        "component_share_of_portfolio_variance": contribution / variance_port,
        "portfolio_variance_at_4pct_art": variance_port,
        "base_60_40_variance": variance_base,
        "variance_change_vs_base": variance_port - variance_base,
        "variance_change_vs_base_pct": (variance_port / variance_base) - 1,
        **period(diversified["art"]),
        "real_or_nominal": "nominal",
    }

    # Robustness: ARTKSIX is quarterly; IMP/PWC have only Jun/Dec prints, so their comparator
    # returns are calculated at exactly the same semiannual dates rather than mixing frequencies.
    robustness = {}
    six_returns = log_return(art["ARTKSIX"])
    for label, series in {"ARTKSIX_quarterly": six_returns}.items():
        row = {}
        for comp in ["S&P 500", "Gold", "IEF", "CPI inflation", "REITs", "Home prices", "VIX level"]:
            row[comp] = correlation_stat(series, returns[comp])
        robustness[label] = {"frequency": "quarterly", "correlations": row}

    semi_dates = art.index[art["ARTKIMP"].notna()]
    semi_assets = semiannual_asset_returns(levels[["S&P 500", "Gold", "IEF", "CPI", "REITs", "Home prices", "VIX"]], semi_dates)
    semi_assets = semi_assets.rename(columns={"CPI": "CPI inflation"})
    for art_col in ["ARTKIMP", "ARTKPWC"]:
        art_semi = log_return(art[art_col].dropna())
        row = {}
        for comp in semi_assets.columns:
            comparator = semi_assets[comp]
            row[comp] = correlation_stat(art_semi, comparator)
        robustness[f"{art_col}_semiannual"] = {
            "frequency": "semiannual (Jun/Dec only; no forward-filled quarterly returns)",
            "correlations": row,
        }

    results = {
        "methodology": {
            "frequency": "quarterly, aligned to supplied ARTDAI quarter ends",
            "return_convention": "log returns except DGS10 (quarterly percentage-point yield change) and VIX (quarter-end level, per brief)",
            "primary_art_series": "ARTKAART / All Traded Artists",
            "data_failures_after_one_retry": failures,
        },
        "corr_returns": {
            "values": pearson_dict,
            "n_obs_by_pair": n_dict,
            "sample_period_by_pair": samples_dict,
            **period(returns["All Traded Art"]),
            "real_or_nominal": "nominal",
            "method": "Pearson",
        },
        "corr_spearman": {
            "values": spearman_dict,
            "n_obs_by_pair": n_dict,
            "sample_period_by_pair": samples_dict,
            **period(returns["All Traded Art"]),
            "real_or_nominal": "nominal",
            "method": "Spearman rank",
        },
        "art_sp_returns_corr": art_sp,
        "art_sp_levels_corr_spurious": art_sp_levels,
        "rolling_corr_sp": {
            "window_quarters": 20,
            "values": {d.strftime("%Y-%m-%d"): v for d, v in rolling_sp.dropna().items()},
            **period(rolling_sp),
            "real_or_nominal": "nominal",
        },
        "rolling_corr_gold": {
            "window_quarters": 20,
            "values": {d.strftime("%Y-%m-%d"): v for d, v in rolling_gold.dropna().items()},
            **period(rolling_gold),
            "real_or_nominal": "nominal",
        },
        "art_60_40_corr": art_6040,
        "marginal_var_contribution_4pct": marginal,
        "robustness_art_variants": robustness,
    }
    (OUT / "results.json").write_text(json.dumps(json_safe(results), indent=2) + "\n")
    draw_heatmap(pearson)
    draw_rolling(rolling_sp, rolling_gold)


if __name__ == "__main__":
    main()
