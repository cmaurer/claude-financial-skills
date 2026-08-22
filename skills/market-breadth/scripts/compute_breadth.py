#!/usr/bin/env python3
"""
compute_breadth.py — Market breadth computed directly from S&P 500 constituents.
 
Replaces keyword web-search for the mechanical breadth indicators, which return
stale article text rather than live values. Emits a human-readable report plus a
JSON payload for `cache_set("derived:breadth", ...)` and a timeseries array for
`timeseries_store("derived:breadth_pct200ma", ...)`.
 
Scope note: this script is authoritative for % above MA, advance/decline,
McClellan Oscillator, and the equal- vs cap-weight spread. It is NOT authoritative
for NYSE/Nasdaq new highs-lows — that needs the full multi-thousand-name universe
(barchart.com). The highs/lows printed here are an S&P-500-only proxy, labeled
as such.
 
Usage:
    python compute_breadth.py                          # full run, latest close
    python compute_breadth.py --asof 2026-08-21        # as of a specific date
    python compute_breadth.py --json-only              # machine-readable only
    python compute_breadth.py --prices-cache px.csv    # reuse a prior download
"""
 
import argparse
import io
import json
import sys
import urllib.request
import warnings
from datetime import timedelta
 
warnings.filterwarnings("ignore")
 
try:
    import pandas as pd
    import yfinance as yf
except ImportError:
    sys.exit("Missing deps. Run: pip install yfinance pandas --break-system-packages -q")
 
 
# Constituent list sources, tried in order. Wikipedia is deliberately NOT first:
# it returns HTTP 403 to non-browser user agents from most sandboxes.
CONSTITUENT_SOURCES = [
    "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv",
    "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv",
]
 
 
def fetch_constituents(verbose=True):
    """Return list of S&P 500 tickers, yfinance-normalized (BRK.B -> BRK-B)."""
    for url in CONSTITUENT_SOURCES:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            txt = urllib.request.urlopen(req, timeout=30).read().decode()
            t = pd.read_csv(io.StringIO(txt))
            col = next(c for c in t.columns if c.lower() in ("symbol", "ticker"))
            syms = [str(s).replace(".", "-") for s in t[col].dropna().tolist()]
            if len(syms) > 400:
                if verbose:
                    print(f"[constituents] {len(syms)} tickers from {url.split('/')[2]}",
                          file=sys.stderr)
                return syms
        except Exception as e:
            if verbose:
                print(f"[constituents] failed {url.split('/')[2]}: {type(e).__name__}",
                      file=sys.stderr)
    sys.exit("Could not fetch S&P 500 constituent list from any source.")
 
 
def download_prices(syms, start, end, verbose=True):
    """Batch-download adjusted closes. Drops tickers with sparse history."""
    if verbose:
        print(f"[download] {len(syms)} tickers {start} -> {end} ...", file=sys.stderr)
    d = yf.download(syms, start=start, end=end, auto_adjust=True, progress=False)["Close"]
    before = d.shape[1]
    d = d.dropna(axis=1, thresh=250)
    if verbose:
        print(f"[download] {d.shape[1]}/{before} tickers usable, {d.shape[0]} sessions",
              file=sys.stderr)
    return d
 
 
def rsi(series, n=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    dn = -delta.clip(upper=0)
    rs = up.ewm(alpha=1 / n, adjust=False).mean() / dn.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + rs)
 
 
def macd_hist(series, fast=12, slow=26, sig=9):
    m = series.ewm(span=fast, adjust=False).mean() - series.ewm(span=slow, adjust=False).mean()
    return m - m.ewm(span=sig, adjust=False).mean()
 
 
def compute(d, spx, asof=None):
    """Compute the full breadth block. Returns a dict."""
    if asof:
        t = pd.Timestamp(asof)
        d = d.loc[d.index <= t]
        spx = spx.loc[spx.index <= t]
    asof_ts = d.index[-1]
 
    # Prior-week anchor: last session at least 5 calendar days back
    prior_idx = d.index[d.index <= asof_ts - timedelta(days=5)]
    prior_ts = prior_idx[-1] if len(prior_idx) else d.index[0]
 
    ma50, ma200 = d.rolling(50).mean(), d.rolling(200).mean()
    valid = d.notna().sum(axis=1)
    pct50 = (d > ma50).sum(axis=1) / valid * 100
    pct200 = (d > ma200).sum(axis=1) / valid * 100
 
    r = d.pct_change()
    adv, dec = (r > 0).sum(axis=1), (r < 0).sum(axis=1)
    ad_ratio = adv / dec.replace(0, 1)
    cum_ad = (adv - dec).cumsum()
 
    # Ratio-adjusted McClellan: net advances normalized by total issues, so the
    # oscillator is comparable across periods even as issue counts drift.
    net_norm = (adv - dec) / (adv + dec).replace(0, 1) * 1000
    mcc = net_norm.ewm(span=19, adjust=False).mean() - net_norm.ewm(span=39, adjust=False).mean()
 
    # Equal- vs cap-weight: the single most informative line in this block.
    wk = (d.loc[asof_ts] / d.loc[prior_ts] - 1) * 100
    ew_ret = float(wk.mean())
    cw_ret = float((spx.loc[asof_ts] / spx.loc[prior_ts] - 1) * 100)
 
    # S&P-500-only highs/lows PROXY. Not comparable to barchart NYSE/Nasdaq figures.
    hi = d.rolling(252, min_periods=200).max()
    lo = d.rolling(252, min_periods=200).min()
    nh = int((d.loc[asof_ts] >= hi.loc[asof_ts] * 0.999).sum())
    nl = int((d.loc[asof_ts] <= lo.loc[asof_ts] * 1.001).sum())
 
    last5 = d.index[-5:]
    nh5 = [int((d.loc[x] >= hi.loc[x] * 0.999).sum()) for x in last5]
    nl5 = [int((d.loc[x] <= lo.loc[x] * 1.001).sum()) for x in last5]
 
    spx_rsi = float(rsi(spx).loc[asof_ts])
    spx_macd = float(macd_hist(spx).loc[asof_ts])
    spx_macd_prior = float(macd_hist(spx).loc[prior_ts])
    spx_ma50 = float(spx.rolling(50).mean().loc[asof_ts])
    spx_ma200 = float(spx.rolling(200).mean().loc[asof_ts])
    ma200_slope = float(spx.rolling(200).mean().loc[asof_ts]
                        - spx.rolling(200).mean().iloc[-21]) if len(spx) > 221 else float("nan")
 
    ad5 = [round(float(ad_ratio.loc[x]), 2) for x in last5]
 
    out = {
        "as_of": str(asof_ts.date()),
        "prior_week": str(prior_ts.date()),
        "universe": f"{int(valid.loc[asof_ts])} S&P 500 constituents",
        "pct_above_50ma": round(float(pct50.loc[asof_ts]), 1),
        "pct_above_50ma_prior_wk": round(float(pct50.loc[prior_ts]), 1),
        "pct_above_200ma": round(float(pct200.loc[asof_ts]), 1),
        "pct_above_200ma_prior_wk": round(float(pct200.loc[prior_ts]), 1),
        "ad_ratio": round(float(ad_ratio.loc[asof_ts]), 2),
        "ad_ratio_last5": ad5,
        "ad_ratio_5d_avg": round(sum(ad5) / len(ad5), 2),
        "cum_ad_line": int(cum_ad.loc[asof_ts]),
        "cum_ad_peak": int(cum_ad.max()),
        "cum_ad_peak_date": str(cum_ad.idxmax().date()),
        "mcclellan_osc": round(float(mcc.loc[asof_ts]), 1),
        "mcclellan_osc_prior_wk": round(float(mcc.loc[prior_ts]), 1),
        "members_up": int((wk > 0).sum()),
        "members_total": int(wk.notna().sum()),
        "median_member_return": round(float(wk.median()), 2),
        "equal_weight_return": round(ew_ret, 2),
        "cap_weight_return": round(cw_ret, 2),
        "ew_cw_spread_bp": round((ew_ret - cw_ret) * 100),
        "spx_rsi14": round(spx_rsi, 1),
        "spx_macd_hist": round(spx_macd, 2),
        "spx_macd_hist_prior_wk": round(spx_macd_prior, 2),
        "spx_close": round(float(spx.loc[asof_ts]), 2),
        "spx_vs_50ma": "ABOVE" if spx.loc[asof_ts] > spx_ma50 else "BELOW",
        "spx_vs_200ma": "ABOVE" if spx.loc[asof_ts] > spx_ma200 else "BELOW",
        "spx_ma50": round(spx_ma50, 2),
        "spx_ma200": round(spx_ma200, 2),
        "spx_ma200_slope_20d": round(ma200_slope, 2),
        "new_highs_proxy": nh,
        "new_lows_proxy": nl,
        "_proxy_caveat": "highs/lows are S&P-500-only over a 252d window; use barchart.com for NYSE/Nasdaq",
        "_survivorship_caveat": "current constituents applied historically; mildly optimistic bias in %-above-MA",
        "_cum_ad_caveat": "cumulative A/D is seeded at the download start date; only its DIRECTION is meaningful, not its level",
        "source": "computed from S&P 500 constituent closes via yfinance",
    }
 
    # ---- Bearish Breadth Divergence: 4-criterion check ----
    ad_trend = ad5[-1] < ad5[0] and sum(ad5[-2:]) / 2 < sum(ad5[:2]) / 2
    lows_beat_highs = sum(1 for a, b in zip(nh5, nl5) if b > a) >= 3
    pct200_weak = out["pct_above_200ma"] < out["pct_above_200ma_prior_wk"] and out["pct_above_200ma"] < 55
    ad_not_confirming = cum_ad.loc[asof_ts] < cum_ad.max() and cum_ad.idxmax() < asof_ts
 
    crit = {
        "1_ad_deteriorating_5plus_sessions": bool(ad_trend),
        "2_new_lows_exceed_highs_3of5": bool(lows_beat_highs),
        "3_pct_above_200ma_declining_toward_50": bool(pct200_weak),
        "4_cum_ad_not_confirming_price_high": bool(ad_not_confirming),
    }
    met = sum(crit.values())
    out["divergence_criteria"] = crit
    out["divergence_criteria_met"] = met
    out["divergence_triggered"] = met >= 2
    out["divergence_verdict"] = (
        f"TRIGGERED ({met}/4)" if met >= 2 else f"not triggered ({met}/4)"
    )
    return out
 
 
def render(o):
    """Human-readable report block."""
    L = []
    A = L.append
    A(f"MARKET BREADTH  |  as of {o['as_of']}  (prior week: {o['prior_week']})")
    A(f"Universe: {o['universe']}")
    A("")
    A("--- TREND PARTICIPATION ---")
    A(f"  % above 50-day MA    {o['pct_above_50ma']:>6.1f}%   (prior wk {o['pct_above_50ma_prior_wk']:.1f}%)")
    A(f"  % above 200-day MA   {o['pct_above_200ma']:>6.1f}%   (prior wk {o['pct_above_200ma_prior_wk']:.1f}%)")
    A(f"     thresholds: >60% bull · <40% warning · <30% bear")
    A("")
    A("--- ADVANCE / DECLINE ---")
    A(f"  A/D ratio (latest)   {o['ad_ratio']:>6.2f}   last 5: {o['ad_ratio_last5']}")
    A(f"  A/D 5-day average    {o['ad_ratio_5d_avg']:>6.2f}   (>1.5 healthy · <1.0 deteriorating)")
    A(f"  Cumulative A/D       {o['cum_ad_line']:>6d}   peak {o['cum_ad_peak']} on {o['cum_ad_peak_date']}")
    A(f"     note: level is seed-dependent — read direction only")
    A(f"  McClellan Oscillator {o['mcclellan_osc']:>+6.1f}   (prior wk {o['mcclellan_osc_prior_wk']:+.1f})")
    A("")
    A("--- CONCENTRATION (equal- vs cap-weight) ---")
    A(f"  Equal-weight member return   {o['equal_weight_return']:>+6.2f}%")
    A(f"  Cap-weight index return      {o['cap_weight_return']:>+6.2f}%")
    A(f"  Spread                       {o['ew_cw_spread_bp']:>+6d} bp")
    lead = ("average member outpaced the index — move was megacap-driven, "
            "breadth HEALTHIER than the headline") if o["ew_cw_spread_bp"] > 25 else (
        ("index outpaced the average member — megacaps carrying it, "
         "breadth WEAKER than the headline") if o["ew_cw_spread_bp"] < -25
        else "broad participation; little concentration effect")
    A(f"  -> {lead}")
    A(f"  Members up: {o['members_up']}/{o['members_total']}  median {o['median_member_return']:+.2f}%")
    A("")
    A("--- INDEX TECHNICALS ---")
    A(f"  SPX close {o['spx_close']}   50dMA {o['spx_ma50']} ({o['spx_vs_50ma']})   200dMA {o['spx_ma200']} ({o['spx_vs_200ma']})")
    A(f"  200dMA slope (20d)   {o['spx_ma200_slope_20d']:+.2f}")
    A(f"  RSI(14)  {o['spx_rsi14']:.1f}    MACD hist {o['spx_macd_hist']:+.2f} (prior wk {o['spx_macd_hist_prior_wk']:+.2f})")
    A("")
    A("--- NEW HIGHS / LOWS (S&P 500 PROXY ONLY) ---")
    A(f"  highs {o['new_highs_proxy']}  lows {o['new_lows_proxy']}")
    A(f"  NOT comparable to barchart NYSE/Nasdaq figures — fetch those separately if needed")
    A("")
    A("--- BEARISH BREADTH DIVERGENCE CHECK ---")
    for k, v in o["divergence_criteria"].items():
        A(f"  [{'X' if v else ' '}] {k.split('_', 1)[1].replace('_', ' ')}")
    A(f"  VERDICT: {o['divergence_verdict']}   (2+ of 4 = flag in Section 18)")
    return "\n".join(L)
 
 
def main():
    p = argparse.ArgumentParser(description="Compute S&P 500 market breadth")
    p.add_argument("--asof", help="YYYY-MM-DD; defaults to latest close")
    p.add_argument("--lookback-days", type=int, default=560,
                   help="calendar days of history (need ~400 for a clean 200d MA)")
    p.add_argument("--json-only", action="store_true")
    p.add_argument("--json-out", help="write JSON payload to this path")
    p.add_argument("--prices-cache", help="CSV of constituent closes to reuse instead of downloading")
    p.add_argument("--save-prices", help="save downloaded closes to this CSV")
    args = p.parse_args()
 
    end = (pd.Timestamp(args.asof) if args.asof else pd.Timestamp.today()) + timedelta(days=1)
    start = end - timedelta(days=args.lookback_days)
 
    if args.prices_cache:
        d = pd.read_csv(args.prices_cache, index_col=0, parse_dates=True)
    else:
        syms = fetch_constituents()
        d = download_prices(syms, start.date().isoformat(), end.date().isoformat())
        if args.save_prices:
            d.to_csv(args.save_prices)
 
    spx = yf.download("^GSPC", start=start.date().isoformat(),
                      end=end.date().isoformat(), auto_adjust=True, progress=False)["Close"]
    spx = spx.iloc[:, 0] if isinstance(spx, pd.DataFrame) else spx
 
    o = compute(d, spx, args.asof)
 
    if not args.json_only:
        print(render(o))
        print("\n" + "=" * 60 + "\nJSON payload for cache_set('derived:breadth', ..., 3600):\n")
    print(json.dumps(o, indent=2))
 
    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(o, f, indent=2)
 
 
if __name__ == "__main__":
    main()