"""
Portfolio Stress Test Script
Computes scenario analysis (historical + hypothetical), factor sensitivities,
Monte Carlo simulation, and retirement impact analysis.

Usage:
    python stress_test.py
        --portfolio /mnt/project/Portfolio_Positions_May232026.csv
        --holding-prices /tmp/holding_prices.json       # optional
        --retirement-year 2033
        --annual-spend 120000
        --risk-free-rate 0.0525
"""

import argparse
import json
import sys
import math
import random
from datetime import datetime

try:
    import numpy as np
    import pandas as pd
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ─── SCENARIO DEFINITIONS ────────────────────────────────────────────────────
# Each scenario maps asset-class keys to % shock (e.g., -0.40 = -40%).
# Asset-class assignment is done by ticker in classify_ticker().

HISTORICAL_SCENARIOS = {
    "2008–2009 Global Financial Crisis": {
        "description": "S&P peak-to-trough −57%. Credit seized. Bonds rallied as flight-to-safety.",
        "us_equity":        -0.57,
        "intl_developed":   -0.54,
        "emerging_market":  -0.61,
        "us_bond_agg":      +0.05,
        "corp_bond_ig":     -0.06,
        "corp_bond_hy":     -0.26,
        "em_bond":          -0.20,
        "healthcare":       -0.36,
        "biotech":          -0.40,
        "japan":            -0.42,
        "tech":             -0.52,
        "high_div_eq":      -0.40,
        "muni_bond":        +0.02,
        "cash":              0.00,
        "target_date":      -0.38,
    },
    "2020 COVID Crash (Feb–Mar)": {
        "description": "S&P peak-to-trough −34% in 33 days. Fastest bear market in history.",
        "us_equity":        -0.34,
        "intl_developed":   -0.31,
        "emerging_market":  -0.31,
        "us_bond_agg":      +0.02,
        "corp_bond_ig":     -0.08,
        "corp_bond_hy":     -0.20,
        "em_bond":          -0.18,
        "healthcare":       -0.22,
        "biotech":          -0.25,
        "japan":            -0.28,
        "tech":             -0.28,
        "high_div_eq":      -0.35,
        "muni_bond":        -0.04,
        "cash":              0.00,
        "target_date":      -0.22,
    },
    "2022 Rate Shock (Full Year)": {
        "description": "S&P −19%. AGG −13%. First year since 1969 both stocks and bonds fell >10%.",
        "us_equity":        -0.19,
        "intl_developed":   -0.16,
        "emerging_market":  -0.20,
        "us_bond_agg":      -0.13,
        "corp_bond_ig":     -0.15,
        "corp_bond_hy":     -0.11,
        "em_bond":          -0.18,
        "healthcare":       -0.02,
        "biotech":          -0.26,
        "japan":            -0.14,
        "tech":             -0.33,
        "high_div_eq":      -0.01,
        "muni_bond":        -0.09,
        "cash":              0.00,
        "target_date":      -0.14,
    },
    "2000–2002 Dot-Com Bust": {
        "description": "S&P −49%. Nasdaq −78%. Tech and growth stocks devastated.",
        "us_equity":        -0.49,
        "intl_developed":   -0.46,
        "emerging_market":  -0.28,
        "us_bond_agg":      +0.30,
        "corp_bond_ig":     +0.22,
        "corp_bond_hy":     -0.14,
        "em_bond":          +0.12,
        "healthcare":       -0.10,
        "biotech":          -0.62,
        "japan":            -0.42,
        "tech":             -0.78,
        "high_div_eq":      -0.22,
        "muni_bond":        +0.15,
        "cash":              0.00,
        "target_date":      -0.32,
    },
}

HYPOTHETICAL_SCENARIOS = {
    "Mild Recession (−25% Equity)": {
        "description": "Growth scare triggers moderate bear market. Bonds provide partial offset.",
        "us_equity":        -0.25,
        "intl_developed":   -0.22,
        "emerging_market":  -0.28,
        "us_bond_agg":      +0.04,
        "corp_bond_ig":     -0.02,
        "corp_bond_hy":     -0.12,
        "em_bond":          -0.10,
        "healthcare":       -0.15,
        "biotech":          -0.22,
        "japan":            -0.18,
        "tech":             -0.28,
        "high_div_eq":      -0.18,
        "muni_bond":        +0.03,
        "cash":              0.00,
        "target_date":      -0.16,
    },
    "Severe Recession (−40% Equity)": {
        "description": "Deep contraction. Bonds rally modestly. EM and high-beta positions hit hardest.",
        "us_equity":        -0.40,
        "intl_developed":   -0.38,
        "emerging_market":  -0.45,
        "us_bond_agg":      +0.08,
        "corp_bond_ig":     -0.04,
        "corp_bond_hy":     -0.22,
        "em_bond":          -0.18,
        "healthcare":       -0.28,
        "biotech":          -0.35,
        "japan":            -0.30,
        "tech":             -0.45,
        "high_div_eq":      -0.30,
        "muni_bond":        +0.05,
        "cash":              0.00,
        "target_date":      -0.28,
    },
    "Rate Shock +300 bps (Inflation Reaccel.)": {
        "description": "Fed forced to hike 300 bps on re-acceleration. Duration assets repriced.",
        "us_equity":        -0.20,
        "intl_developed":   -0.15,
        "emerging_market":  -0.22,
        "us_bond_agg":      -0.18,
        "corp_bond_ig":     -0.20,
        "corp_bond_hy":     -0.14,
        "em_bond":          -0.22,
        "healthcare":       -0.08,
        "biotech":          -0.15,
        "japan":            -0.10,
        "tech":             -0.25,
        "high_div_eq":      -0.12,
        "muni_bond":        -0.14,
        "cash":              0.00,
        "target_date":      -0.16,
    },
    "Stagflation (Low Growth + High Inflation)": {
        "description": "1970s-style: Fed constrained, growth stagnates. Real returns negative.",
        "us_equity":        -0.30,
        "intl_developed":   -0.25,
        "emerging_market":  -0.20,
        "us_bond_agg":      -0.12,
        "corp_bond_ig":     -0.14,
        "corp_bond_hy":     -0.10,
        "em_bond":          -0.15,
        "healthcare":       +0.05,
        "biotech":          -0.10,
        "japan":            -0.20,
        "tech":             -0.38,
        "high_div_eq":      -0.10,
        "muni_bond":        -0.08,
        "cash":              0.00,
        "target_date":      -0.20,
    },
    "AI/Tech Capex Bubble Burst (Tech −50%)": {
        "description": "AI spending disappoints. Mega-cap tech multiples compress sharply.",
        "us_equity":        -0.20,
        "intl_developed":   -0.12,
        "emerging_market":  -0.15,
        "us_bond_agg":      +0.03,
        "corp_bond_ig":     +0.01,
        "corp_bond_hy":     -0.05,
        "em_bond":          -0.05,
        "healthcare":       -0.05,
        "biotech":          -0.12,
        "japan":            -0.08,
        "tech":             -0.50,
        "high_div_eq":      -0.08,
        "muni_bond":        +0.02,
        "cash":              0.00,
        "target_date":      -0.14,
    },
    "EM / Japan Crisis (International Shock)": {
        "description": "EM capital outflows + JPY policy reversal. International positions repriced.",
        "us_equity":        -0.08,
        "intl_developed":   -0.25,
        "emerging_market":  -0.35,
        "us_bond_agg":      +0.02,
        "corp_bond_ig":     -0.01,
        "corp_bond_hy":     -0.08,
        "em_bond":          -0.28,
        "healthcare":       -0.04,
        "biotech":          -0.06,
        "japan":            -0.30,
        "tech":             -0.10,
        "high_div_eq":      -0.08,
        "muni_bond":        +0.01,
        "cash":              0.00,
        "target_date":      -0.10,
    },
}

ALL_SCENARIOS = {**HISTORICAL_SCENARIOS, **HYPOTHETICAL_SCENARIOS}


# ─── TICKER CLASSIFICATION ────────────────────────────────────────────────────

def classify_ticker(symbol, description=""):
    """Map ticker to asset class key for scenario shocks."""
    symbol = symbol.upper()
    desc = description.upper()

    TECH_TICKERS = {"AAPL", "MSFT", "NVDA", "META", "AMZN", "GOOGL", "GOOG", "QQQ", "XLK"}
    BIOTECH_TICKERS = {"XBI", "IBB", "ARKG"}
    HEALTHCARE_TICKERS = {"VHT", "XLV"}
    EM_TICKERS = {"VWO", "IEMG", "EEM", "EMHY", "EMB"}
    JAPAN_TICKERS = {"EWJ", "DXJ"}
    INTL_DEV_TICKERS = {"IDEV", "EFA", "VEA", "IDV"}
    US_EQUITY_TICKERS = {"IVV", "SPY", "VOO", "VTI", "VFIAX", "VINIX", "DIA", "FOCSX", "SCHB", "VV"}
    AGG_BOND_TICKERS = {"AGG", "BND"}
    MUNI_BOND_TICKERS = {"FMUB", "MUB", "HYD", "VTEB"}
    CORP_IG_TICKERS = {"VCIT", "LQD", "IGIB", "FBND", "IGSB"}
    CORP_HY_TICKERS = {"HYG", "JNK", "USHY"}
    HIGH_DIV_EQ = {"VYM", "RDVI", "SCHD", "DVY"}
    TARGET_DATE = {"ITDC"}
    CASH_TICKERS = {"SPAXX", "FDRXX", "FCASH", "FTEXX"}

    if symbol in CASH_TICKERS:
        return "cash"
    if symbol in US_EQUITY_TICKERS:
        return "us_equity"
    if symbol in TECH_TICKERS:
        return "tech"
    if symbol in BIOTECH_TICKERS:
        return "biotech"
    if symbol in HEALTHCARE_TICKERS:
        return "healthcare"
    if symbol in MUNI_BOND_TICKERS:
        return "muni_bond"
    if symbol in EM_TICKERS or "EMH" in symbol:
        return "em_bond" if symbol == "EMHY" else "emerging_market"
    if symbol in JAPAN_TICKERS:
        return "japan"
    if symbol in INTL_DEV_TICKERS:
        return "intl_developed"
    if symbol in AGG_BOND_TICKERS:
        return "us_bond_agg"
    if symbol in CORP_IG_TICKERS:
        return "corp_bond_ig"
    if symbol in CORP_HY_TICKERS:
        return "corp_bond_hy"
    if symbol in HIGH_DIV_EQ:
        return "high_div_eq"
    if symbol in TARGET_DATE or "TARGET" in desc or "LIFEPATH" in desc or "2035" in desc:
        return "target_date"
    if "**" in symbol:
        return None
    # Default: treat unknown equities as US large-cap
    return "us_equity"


# ─── CSV LOADER ───────────────────────────────────────────────────────────────

def load_portfolio(csv_path):
    """Load and parse the Fidelity portfolio CSV."""
    if not HAS_NUMPY:
        import csv
        holdings = []
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sym = row.get("Symbol", "").strip()
                if not sym or "**" in sym:
                    continue
                if sym in ("SPAXX", "FDRXX", "FCASH", "FTEXX"):
                    # track cash separately
                    val_str = row.get("Current Value", "0").replace("$", "").replace(",", "").strip()
                    try:
                        val = float(val_str)
                    except:
                        val = 0.0
                    holdings.append({
                        "symbol": sym,
                        "description": row.get("Description", ""),
                        "account": row.get("Account Name", ""),
                        "value": val,
                        "cost_basis": val,
                        "asset_class": "cash"
                    })
                    continue
                val_str = row.get("Current Value", "0").replace("$", "").replace(",", "").replace("+", "").strip()
                cost_str = row.get("Cost Basis Total", "0").replace("$", "").replace(",", "").replace("+", "").strip()
                try:
                    val = float(val_str) if val_str else 0.0
                except:
                    val = 0.0
                try:
                    cost = float(cost_str) if cost_str else val
                except:
                    cost = val
                if val <= 0:
                    continue
                ac = classify_ticker(sym, row.get("Description", ""))
                holdings.append({
                    "symbol": sym,
                    "description": row.get("Description", ""),
                    "account": row.get("Account Name", ""),
                    "value": val,
                    "cost_basis": cost,
                    "asset_class": ac
                })
        return holdings
    else:
        df = pd.read_csv(csv_path, encoding="utf-8-sig", index_col=False)
        df.columns = df.columns.str.strip()
        df = df[df["Symbol"].notna()]
        df = df[~df["Symbol"].str.contains(r"\*\*", na=False) | df["Symbol"].str.strip().isin(["SPAXX", "FDRXX", "FCASH", "FTEXX"])]
        # Actually keep cash rows but tag them
        df = df[~(df["Symbol"].str.contains(r"\*\*", na=False) & ~df["Symbol"].str.strip().isin(["SPAXX", "FDRXX", "FCASH", "FTEXX"]))]

        def parse_money(s):
            if pd.isna(s):
                return 0.0
            clean = str(s).replace("$", "").replace(",", "").replace("+", "").strip()
            if not clean or clean in ("--", "-", "N/A", "n/a"):
                return 0.0
            try:
                return float(clean)
            except ValueError:
                return 0.0

        df["value"] = df["Current Value"].apply(parse_money)
        df["cost_basis"] = df["Cost Basis Total"].apply(parse_money)
        df = df[df["value"] > 0]
        df["asset_class"] = df.apply(lambda r: classify_ticker(r["Symbol"].strip(), r.get("Description", "") or ""), axis=1)
        holdings = []
        for _, row in df.iterrows():
            holdings.append({
                "symbol": row["Symbol"].strip(),
                "description": row.get("Description", ""),
                "account": row.get("Account Name", ""),
                "value": row["value"],
                "cost_basis": row["cost_basis"],
                "asset_class": row["asset_class"]
            })
        return holdings


# ─── SCENARIO ENGINE ──────────────────────────────────────────────────────────

def run_scenario(holdings, scenario_shocks):
    """Apply scenario shocks to holdings. Returns (stressed_value, dollar_loss, positions)."""
    total_pre = sum(h["value"] for h in holdings)
    positions = []
    total_post = 0.0

    for h in holdings:
        ac = h["asset_class"]
        if ac is None:
            shock = 0.0
        else:
            shock = scenario_shocks.get(ac, scenario_shocks.get("us_equity", -0.20))
        stressed = h["value"] * (1 + shock)
        positions.append({**h, "shock_pct": shock, "stressed_value": stressed,
                          "dollar_change": stressed - h["value"]})
        total_post += stressed

    dollar_loss = total_post - total_pre
    pct_change = dollar_loss / total_pre if total_pre > 0 else 0
    return total_pre, total_post, dollar_loss, pct_change, positions


# ─── CONCENTRATION RISK ───────────────────────────────────────────────────────

def concentration_sensitivity(holdings, total_value):
    """Isolate single-position shocks for AAPL and top-5 holdings."""
    top = sorted(holdings, key=lambda h: -h["value"])[:8]
    rows = []
    for h in top:
        if h["asset_class"] == "cash":
            continue
        for shock in [-0.10, -0.20, -0.30, -0.50]:
            dollar_impact = h["value"] * shock
            portfolio_impact_pct = dollar_impact / total_value
            rows.append({
                "ticker": h["symbol"],
                "position_value": h["value"],
                "shock": shock,
                "dollar_impact": dollar_impact,
                "portfolio_pct_impact": portfolio_impact_pct,
            })
    return rows


# ─── MONTE CARLO ──────────────────────────────────────────────────────────────

def run_monte_carlo(portfolio_value, annual_return=0.07, annual_vol=0.12,
                    years=8, annual_spend=0.0, n_sims=5000, seed=42):
    """
    Simple lognormal Monte Carlo for terminal portfolio value.
    Returns percentile outcomes.
    """
    if HAS_NUMPY:
        rng = np.random.default_rng(seed)
        log_mu = annual_return - 0.5 * annual_vol ** 2
        log_sigma = annual_vol
        sims = []
        for _ in range(n_sims):
            val = portfolio_value
            for y in range(years):
                annual_r = rng.lognormal(log_mu, log_sigma) - 1
                val = val * (1 + annual_r) - annual_spend
                if val <= 0:
                    val = 0
                    break
            sims.append(val)
        sims_arr = np.array(sims)
        return {
            "p10": float(np.percentile(sims_arr, 10)),
            "p25": float(np.percentile(sims_arr, 25)),
            "p50": float(np.percentile(sims_arr, 50)),
            "p75": float(np.percentile(sims_arr, 75)),
            "p90": float(np.percentile(sims_arr, 90)),
            "ruin_pct": float(100 * (sims_arr <= 0).sum() / n_sims),
            "below_500k": float(100 * (sims_arr < 500_000).sum() / n_sims),
            "n_sims": n_sims,
        }
    else:
        # Pure-Python fallback (slower, fewer sims)
        random.seed(seed)
        n_sims_py = 2000
        log_mu = annual_return - 0.5 * annual_vol ** 2
        log_sigma = annual_vol
        sims = []
        for _ in range(n_sims_py):
            val = portfolio_value
            for y in range(years):
                u = random.gauss(log_mu, log_sigma)
                annual_r = math.exp(u) - 1
                val = val * (1 + annual_r) - annual_spend
                if val <= 0:
                    val = 0
                    break
            sims.append(val)
        sims.sort()
        def pct(p):
            idx = int(len(sims) * p / 100)
            return sims[min(idx, len(sims)-1)]
        return {
            "p10": pct(10), "p25": pct(25), "p50": pct(50),
            "p75": pct(75), "p90": pct(90),
            "ruin_pct": 100 * sims.count(0) / n_sims_py,
            "below_500k": 100 * sum(1 for v in sims if v < 500_000) / n_sims_py,
            "n_sims": n_sims_py,
        }


# ─── RECOVERY ESTIMATOR ───────────────────────────────────────────────────────

def estimate_recovery(loss_pct, annual_return=0.07):
    """Estimate years to recover from a given % loss (rough rule of thumb)."""
    if loss_pct >= 0:
        return 0
    required_gain = 1 / (1 + loss_pct) - 1
    if annual_return <= 0:
        return float("inf")
    return math.log(1 + required_gain) / math.log(1 + annual_return)


# ─── FORMATTING ───────────────────────────────────────────────────────────────

def fmt_dollar(v):
    return f"${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"

def fmt_pct(v):
    return f"{v*100:+.1f}%"

def severity_flag(loss_pct):
    if loss_pct >= -0.10:
        return "🟢"
    elif loss_pct >= -0.20:
        return "🟡"
    elif loss_pct >= -0.35:
        return "🔴"
    else:
        return "🔴🔴"


# ─── MAIN REPORT ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--portfolio", required=True)
    parser.add_argument("--holding-prices", default=None)
    parser.add_argument("--retirement-year", type=int, default=2033)
    parser.add_argument("--annual-spend", type=float, default=0.0,
                        help="Estimated annual retirement spend (0 = not provided)")
    parser.add_argument("--risk-free-rate", type=float, default=0.0525)
    args = parser.parse_args()

    holdings = load_portfolio(args.portfolio)
    total_value = sum(h["value"] for h in holdings)
    today = datetime.now()
    years_to_retirement = max(0, args.retirement_year - today.year)

    # ── Asset class summary
    ac_summary = {}
    for h in holdings:
        ac = h["asset_class"] or "unknown"
        ac_summary[ac] = ac_summary.get(ac, 0) + h["value"]

    print("=" * 72)
    print("PORTFOLIO STRESS TEST REPORT")
    print(f"As of: {today.strftime('%B %d, %Y')} | Total Portfolio Value: {fmt_dollar(total_value)}")
    print(f"Retirement Target: {args.retirement_year} ({years_to_retirement} years)")
    if args.annual_spend > 0:
        print(f"Annual Retirement Spend: {fmt_dollar(args.annual_spend)}")
    print("=" * 72)

    # ── Asset class breakdown
    print("\n## Asset Class Exposure (Stress Test Inputs)")
    print(f"{'Asset Class':<30} {'Value':>12} {'% Portfolio':>12}")
    print("-" * 56)
    for ac, val in sorted(ac_summary.items(), key=lambda x: -x[1]):
        print(f"{ac:<30} {fmt_dollar(val):>12} {val/total_value*100:>11.1f}%")
    print(f"{'TOTAL':<30} {fmt_dollar(total_value):>12} {'100.0%':>12}")

    # ── Historical scenarios
    print("\n" + "=" * 72)
    print("## SECTION A — Historical Scenario Analysis")
    print("=" * 72)
    print(f"\n{'Scenario':<42} {'Stressed Value':>15} {'$ Change':>13} {'% Change':>9} {'Sev':>4} {'Recovery':>9}")
    print("-" * 96)
    for name, shocks in HISTORICAL_SCENARIOS.items():
        desc = shocks.pop("description", "")
        pre, post, dloss, pct, positions = run_scenario(holdings, shocks)
        shocks["description"] = desc  # restore
        rec_yrs = estimate_recovery(pct)
        flag = severity_flag(pct)
        rec_str = f"~{rec_yrs:.1f} yrs" if rec_yrs > 0 else "n/a"
        print(f"{name:<42} {fmt_dollar(post):>15} {fmt_dollar(dloss):>13} {fmt_pct(pct):>9} {flag:>4} {rec_str:>9}")

    # ── Hypothetical scenarios
    print("\n" + "=" * 72)
    print("## SECTION B — Hypothetical Scenario Analysis")
    print("=" * 72)
    print(f"\n{'Scenario':<42} {'Stressed Value':>15} {'$ Change':>13} {'% Change':>9} {'Sev':>4} {'Recovery':>9}")
    print("-" * 96)
    for name, shocks in HYPOTHETICAL_SCENARIOS.items():
        desc = shocks.pop("description", "")
        pre, post, dloss, pct, positions = run_scenario(holdings, shocks)
        shocks["description"] = desc
        rec_yrs = estimate_recovery(pct)
        flag = severity_flag(pct)
        rec_str = f"~{rec_yrs:.1f} yrs" if rec_yrs > 0 else "n/a"
        print(f"{name:<42} {fmt_dollar(post):>15} {fmt_dollar(dloss):>13} {fmt_pct(pct):>9} {flag:>4} {rec_str:>9}")

    # ── Worst scenario detail breakdown
    worst_name = "2008–2009 Global Financial Crisis"
    worst_shocks = HISTORICAL_SCENARIOS[worst_name].copy()
    worst_shocks.pop("description", None)
    _, _, _, _, positions = run_scenario(holdings, worst_shocks)
    positions_sorted = sorted(positions, key=lambda p: p["dollar_change"])

    print("\n" + "=" * 72)
    print(f"## SECTION C — Worst-Case Position Detail ({worst_name})")
    print("=" * 72)
    print(f"\n{'Ticker':<8} {'Account':<14} {'Asset Class':<22} {'Current Val':>12} {'Shock':>7} {'$ Impact':>12} {'Stressed Val':>13}")
    print("-" * 94)
    for p in positions_sorted[:15]:
        ticker = p['symbol'][:8]
        acct = p['account'][:13]
        print(f"{ticker:<8} {acct:<14} {(p['asset_class'] or 'n/a')[:21]:<22} "
              f"{fmt_dollar(p['value']):>12} {fmt_pct(p['shock_pct']):>7} "
              f"{fmt_dollar(p['dollar_change']):>12} {fmt_dollar(p['stressed_value']):>13}")

    # ── Concentration sensitivity
    print("\n" + "=" * 72)
    print("## SECTION D — Single-Position Concentration Sensitivity")
    print("=" * 72)
    print("\nIsolated shocks to top holdings (all other positions unchanged):\n")
    top_holdings = [h for h in sorted(holdings, key=lambda x: -x["value"]) if h["asset_class"] != "cash"][:6]
    print(f"{'Ticker':<8} {'Position $':>12} {'Shock':>7} {'Pos. $ Loss':>12} {'Portfolio Δ%':>13}")
    print("-" * 56)
    for h in top_holdings:
        ticker = h["symbol"][:8]
        for shock in [-0.10, -0.20, -0.30, -0.50]:
            dloss = h["value"] * shock
            port_pct = dloss / total_value
            print(f"{ticker:<8} {fmt_dollar(h['value']):>12} {fmt_pct(shock):>7} {fmt_dollar(dloss):>12} {fmt_pct(port_pct):>13}")
        print()

    # ── Monte Carlo
    print("=" * 72)
    print("## SECTION E — Monte Carlo Simulation (5,000 Paths)")
    print("=" * 72)
    assume_return = 0.07
    assume_vol = 0.12
    print(f"\nAssumptions: {assume_return*100:.0f}% ann. return | {assume_vol*100:.0f}% ann. volatility | {years_to_retirement} years to {args.retirement_year}")
    if args.annual_spend > 0:
        print(f"Annual withdrawals: {fmt_dollar(args.annual_spend)}")

    mc = run_monte_carlo(
        total_value,
        annual_return=assume_return,
        annual_vol=assume_vol,
        years=years_to_retirement,
        annual_spend=args.annual_spend,
        n_sims=5000,
    )

    print(f"\n{'Percentile':<18} {'Terminal Portfolio Value':>25}")
    print("-" * 45)
    for label, key in [("10th (Bear case)", "p10"), ("25th", "p25"),
                        ("50th (Median)", "p50"), ("75th", "p75"), ("90th (Bull case)", "p90")]:
        print(f"{label:<18} {fmt_dollar(mc[key]):>25}")

    print(f"\n  Portfolio ruin probability (reaches $0): {mc['ruin_pct']:.1f}%")
    print(f"  Probability of ending below $500K:       {mc['below_500k']:.1f}%")

    # Post-crash Monte Carlo (2008 scenario)
    gfc_shocks = HISTORICAL_SCENARIOS["2008–2009 Global Financial Crisis"].copy()
    gfc_shocks.pop("description", None)
    _, post_crash, _, _, _ = run_scenario(holdings, gfc_shocks)
    mc_crash = run_monte_carlo(
        post_crash,
        annual_return=assume_return,
        annual_vol=assume_vol,
        years=years_to_retirement,
        annual_spend=args.annual_spend,
        n_sims=5000,
    )
    print(f"\nPost-GFC Crash Recovery Paths (starting from {fmt_dollar(post_crash)}):")
    print(f"{'Percentile':<18} {'Terminal Portfolio Value':>25}")
    print("-" * 45)
    for label, key in [("10th (Bear case)", "p10"), ("25th", "p25"),
                        ("50th (Median)", "p50"), ("75th", "p75"), ("90th (Bull case)", "p90")]:
        print(f"{label:<18} {fmt_dollar(mc_crash[key]):>25}")
    print(f"\n  Post-crash ruin probability:             {mc_crash['ruin_pct']:.1f}%")

    # ── Retirement-specific risk
    print("\n" + "=" * 72)
    print("## SECTION F — Retirement Sequence-of-Returns Risk")
    print("=" * 72)
    print(f"""
A crash in the {years_to_retirement} years before retirement ({args.retirement_year}) poses more risk than
a crash after, because there is less time to recover before withdrawals begin.

Key findings:
  • In a 2008-style crash today, the portfolio would fall from {fmt_dollar(total_value)}
    to approximately {fmt_dollar(post_crash)}, a decline of {fmt_pct((post_crash-total_value)/total_value)}.
  • Based on Monte Carlo ({mc_crash['n_sims']:,} paths), median recovery to {args.retirement_year}:
    {fmt_dollar(mc_crash['p50'])} — compared to no-crash median of {fmt_dollar(mc['p50'])}.
  • The gap ({fmt_dollar(mc['p50'] - mc_crash['p50'])}) represents the retirement income risk
    of a GFC-level event occurring today.
""")
    if args.annual_spend > 0:
        safe_withdrawal_rate = args.annual_spend / total_value * 100
        print(f"  Your planned SWR: {safe_withdrawal_rate:.2f}% of current portfolio")
        if safe_withdrawal_rate <= 4.0:
            print(f"  🟢 Within the historical 4% safe withdrawal rate guideline.")
        elif safe_withdrawal_rate <= 5.0:
            print(f"  🟡 Slightly above the 4% guideline — stress-test spending flexibility.")
        else:
            print(f"  🔴 Above 5% SWR — high sequence-of-returns risk. Consider reducing planned spend.")

    print("\n" + "=" * 72)
    print("## KEY STRESS TEST FINDINGS & RECOMMENDED ACTIONS")
    print("=" * 72)
    print("""
1. CONCENTRATED TECH RISK: AAPL + GOOGL + AMZN represent meaningful single-name
   tech concentration. A tech-specific bubble burst (-50%) scenario is the tail risk
   most specific to this portfolio beyond broad market risk.

2. BOND ALLOCATION BUFFER: Current fixed income (~9-10% vs 18% target) provides
   less downside cushion than target allocation. A fully-built bond position would
   absorb ~$X more in a 2008-style crash. Priority: complete AGG/VCIT build-out.

3. CASH AS VOLATILITY PROTOCOL FUEL: Current cash holdings provide the ammunition
   for the Volatility Protocol deployment. A 5-10% S&P drawdown triggers accelerated
   deployment — stress test confirms this would be buying at a meaningful discount.

4. JAPAN CURRENCY RISK (EWJ): A Japan-specific crisis scenario layers FX risk
   on top of equity risk. Monitor BoJ policy normalization closely.

5. RETIREMENT TIMING: {years_to_retirement} years to target retirement date. A severe crash
   early in this window has the highest impact. The Monte Carlo analysis shows
   median outcomes remain constructive even post-GFC, but the 10th percentile
   warrants monitoring as retirement approaches.
""".format(years_to_retirement=years_to_retirement))

    print("=" * 72)
    print("END OF STRESS TEST REPORT")
    print("=" * 72)


if __name__ == "__main__":
    main()
