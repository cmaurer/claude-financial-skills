---
name: market-breadth
description: >
  Compute market breadth from S&P 500 constituent prices — % of stocks above 50/200-day moving
  averages, advance-decline ratio and cumulative A/D, McClellan Oscillator, equal-weight vs
  cap-weight spread, and an automated Bearish Breadth Divergence check. ALWAYS use this skill
  for "market breadth", "breadth", "A/D ratio", "advance decline", "percent above 200-day",
  "$SPXA200R", "$SPXA50R", "McClellan", "breadth divergence", "is the rally broad", "how many
  stocks are participating", "is this megacap-driven", or "market internals". Also trigger
  automatically for Section 2 or Section 19 Layer 2 of a daily/weekly market analysis, and for
  Dashboard 1A Panel D or 1C. Prefer this over web search — keyword searches for breadth index
  values return stale articles, not live numbers. Do NOT use for NYSE/Nasdaq new highs-lows,
  which need the full multi-thousand-name universe from barchart.com.
---
 
# Market Breadth
 
Breadth indicators are arithmetic over a known universe. There is no reason to source them
from prose. This skill computes them from constituent closes, which is both fresher and more
granular than the web sources previously used — and it surfaces one number no external source
publishes conveniently: the **equal-weight vs cap-weight spread**, which tells you whether an
index move was broad or megacap-driven.
 
## Scope
 
**Authoritative here:** % above 50/200-day MA · A/D ratio and cumulative A/D · McClellan
Oscillator · equal- vs cap-weight spread · SPX RSI/MACD/MA position · divergence verdict.
 
**Not authoritative here:** NYSE and Nasdaq new highs-lows. The script prints an
S&P-500-only proxy so the divergence check has an input, but it covers 500 names over a
252-day window — barchart.com covers thousands. If the new-highs/lows figure matters to the
conclusion, fetch it separately and say which source you used.
 
## Workflow
 
### 1. Check the cache first
 
Derived breadth is cached like any other computed output:
 
```
cache_get("derived:breadth")                                  # TTL 3600
timeseries_get("derived:breadth_pct200ma", start, end)        # history
```
 
On a fresh hit within the hour, use it and skip the run. The raw constituent download does
not persist between sessions — only the derived values do — so a cache hit saves the whole
~60-second rebuild.
 
### 2. Run the script
 
```bash
pip install yfinance pandas --break-system-packages -q
 
python scripts/compute_breadth.py                      # latest close
python scripts/compute_breadth.py --asof 2026-08-21    # specific date
```
 
Useful flags: `--save-prices px.csv` then `--prices-cache px.csv` to re-run at several dates
without re-downloading; `--json-only` for machine-readable output; `--json-out path` to write
the payload to disk.
 
Takes ~60s on a cold run (500 tickers × ~18 months; measured, not estimated).
`--lookback-days` defaults to 560, which leaves enough runway for a clean 200-day MA; don't
lower it below ~400.
 
### 3. Store the results
 
Immediately after the run, before moving on:
 
```
cache_set("derived:breadth", <json payload>, 3600)
timeseries_store("derived:breadth_pct200ma", [{"date": as_of, "value": pct_above_200ma}], as_of, as_of)
timeseries_store("derived:breadth_ad_ratio",  [{"date": as_of, "value": ad_ratio}], as_of, as_of)
```
 
The timeseries stores are what build a breadth *history* over sessions. Without them each run
is a standalone snapshot and trend questions stay unanswerable.
 
### 4. Interpret
 
Thresholds for % above 200-day MA: **>60% bull · 40–60% neutral · <40% warning · <30% bear**.
A/D ratio: **>1.5 healthy · 1.0–1.5 neutral · <1.0 deteriorating**.
 
The script runs the four-criterion Bearish Breadth Divergence check automatically and returns
a verdict. **Two or more criteria met = flag it in Section 18** as a risk item. One criterion
alone is noise — the cumulative A/D criterion in particular trips on a one-day lag between the
price peak and the A/D peak, which is not a real divergence.
 
## Reading the concentration spread
 
This is the line to lead with when the index moved meaningfully.
 
- **Spread strongly positive** (equal-weight beat cap-weight): the move was megacap-driven and
  the average company did better than the headline suggests. On a down week this is
  reassuring — the decline was concentrated, not systemic.
- **Spread strongly negative**: a handful of large names are carrying the index while the
  median company lags. This is the configuration that precedes breadth-led breakdowns.
- **Spread near zero**: broad participation, no concentration story.
The sign is what matters, not whether the week was up or down. A +86bp spread on a −1.43%
index week means the same thing structurally as +82bp on a +0.36% week: megacaps drove it.
 
## Caveats to carry into any writeup
 
Three limitations are baked into the method and the script labels each in its output. Repeat
them when the number is load-bearing:
 
1. **Cumulative A/D level is meaningless** — it's a running sum seeded at the download start
   date, so it will differ between runs with different lookbacks. Only its direction and its
   relationship to its own recent peak carry information. Never compare the level to a
   published Summation Index.
2. **Survivorship bias** — today's constituents are applied backward through history, so names
   that dropped out of the index are missing. This biases % -above-MA mildly optimistic.
3. **Highs/lows are a proxy** — see Scope above.
## Output format
 
Report the block as a compact table rather than pasting raw script output. Include: % above
50/200-day MA with prior-week comparison, A/D ratio with the 5-day series, McClellan
Oscillator, cumulative A/D direction, the equal-vs-cap spread in basis points, SPX RSI/MACD
and MA position, then the divergence verdict with the criteria that tripped. State the
universe size and as-of date.
 
## Failure modes
 
- **Constituent fetch fails**: the script tries two sources and exits if both fail. Wikipedia
  is deliberately not among them — it returns HTTP 403 to sandboxed requests. If both sources
  are down, say so rather than falling back to a stale web-searched value.
- **Fewer than ~450 usable tickers**: a data problem, not a market signal. Note it.
- **Recent IPOs/additions** lack 200 days of history and are excluded from the MA
  calculations by `dropna(thresh=250)`. The denominator is per-day valid names, so this
  doesn't distort the percentage.