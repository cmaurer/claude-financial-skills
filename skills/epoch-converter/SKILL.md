---
name: epoch-converter
description: >
  Convert Unix epoch timestamps (seconds or milliseconds) to human-readable dates,
  US Eastern time, day-of-week, market session status, and last trading day.
  Also shows intervals between multiple timestamps. Use this skill IMMEDIATELY
  whenever you encounter epoch timestamps in financial data (CSV files, API
  responses, time-series data, chart data) and need to know what date or time
  period the data represents. Trigger phrases: "what date is this timestamp",
  "convert epoch", "what does this timestamp mean", "when is this bar", or
  any time you find yourself doing calendar math from an epoch value. Always
  run this skill rather than computing dates manually.
---

# Epoch Converter Skill

Converts Unix epoch timestamps to dates instantly. Handles both second-precision
and millisecond-precision epochs, outputs US Eastern time with DST, market session
status, and intervals between multiple timestamps.

---

## When to Use

Run this skill **at the first appearance** of any epoch timestamp in financial data.
Do **not** attempt to convert epoch timestamps by mental arithmetic — that wastes
tokens and produces errors. Call this script and use its output.

Common sources of epoch timestamps in this project:
- Fidelity / brokerage export CSVs with time-series price data
- Yahoo Finance / Polygon API responses
- Chart data arrays where the first column is a timestamp

---

## Step 1 — Identify the Timestamps

Collect all epoch values you need to understand. Typical cases:

- **Single timestamp**: verify the date a data file or bar represents
- **First and last bar**: determine the date range of a time series
- **All bars in a series**: detect gaps or confirm trading-day alignment

---

## Step 2 — Run the Converter

```bash
python /home/claude/epoch-converter/scripts/epoch_converter.py <epoch1> [epoch2 epoch3 ...]
```

Pass up to ~20 timestamps in one call. The script auto-detects seconds vs milliseconds
(values > 10,000,000,000 are treated as milliseconds).

**Example — single timestamp:**
```bash
python /home/claude/epoch-converter/scripts/epoch_converter.py 1779768000
```

**Example — date range check:**
```bash
python /home/claude/epoch-converter/scripts/epoch_converter.py 1748649600 1748908800 1748995200 1749081600 1749168000
```

---

## Step 3 — Interpret the Output

The script outputs for each timestamp:

| Field | Meaning |
|-------|---------|
| `UTC` | The timestamp in UTC |
| `ET` | US Eastern time (auto EDT/EST based on DST) |
| `Weekday` | Day of week in ET |
| `Mkt` | Market session: `regular session`, `pre-market`, `after-hours`, `weekend`, or `US market holiday` |
| `Last trading day` | Most recent market close date prior to this timestamp |

When multiple timestamps are passed, intervals between consecutive bars are shown —
use this to confirm whether a series contains daily, hourly, or intraday bars, and to
spot missing trading days (gaps > 1d on weekdays signal a holiday or missing data).

---

## Precision Rules

| Epoch value range | Interpretation | Covers |
|-------------------|----------------|--------|
| < 10,000,000,000 | Seconds | 1970 – ~2286 |
| ≥ 10,000,000,000 | Milliseconds | 1970 – ~2286 |

When in doubt about precision, run the converter — the output date will reveal if the
wrong unit was assumed (a millisecond value treated as seconds gives a date in 1970).

---

## Common Patterns in Fidelity / Price Data

- **Bar timestamps at midnight UTC** = the prior trading day's close in US Eastern time.
  For example, `2026-05-27 00:00 UTC` = `2026-05-26 20:00 EDT` → the May 26 close.
- **Gaps of 3 days** (Friday → Monday) are normal trading-day intervals; gaps of 4 days
  indicate a Monday holiday.
- **First bar in a downloaded CSV** may be one day earlier than the visible date on the
  chart due to timezone offset — always convert to ET before interpreting.
