#!/usr/bin/env python3
"""
Epoch timestamp converter for financial data analysis.

Usage:
  python epoch_converter.py <epoch> [epoch2 epoch3 ...]

Auto-detects seconds vs milliseconds. Outputs date, time, day-of-week,
and US market context. If multiple timestamps are given, shows intervals.
"""

import sys
from datetime import datetime, timezone, timedelta

# US Eastern offset: -5 (EST) or -4 (EDT). Use fixed -4 (EDT) for April–Oct, -5 Nov–Mar.
# For precision use: pip install pytz / zoneinfo, but we keep it dependency-free.

MS_THRESHOLD = 1e10  # values > 10 billion → milliseconds

US_MARKET_OPEN_ET = 9 * 60 + 30   # 09:30 ET in minutes
US_MARKET_CLOSE_ET = 16 * 60       # 16:00 ET in minutes

# Approximate US federal holidays for 2024–2027 (YYYY-MM-DD) — enough for context checks
KNOWN_HOLIDAYS = {
    "2024-01-01", "2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27",
    "2024-06-19", "2024-07-04", "2024-09-02", "2024-11-28", "2024-12-25",
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26",
    "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25",
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-04-02", "2027-05-31",
    "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24",
}


def is_dst(dt_utc: datetime) -> bool:
    """Rough DST check: EDT (UTC-4) from second Sunday in March to first Sunday in November."""
    year = dt_utc.year
    # Second Sunday in March
    march1 = datetime(year, 3, 1, tzinfo=timezone.utc)
    dst_start = march1 + timedelta(days=(6 - march1.weekday() + 7) % 7 + 7, hours=7)
    # First Sunday in November
    nov1 = datetime(year, 11, 1, tzinfo=timezone.utc)
    dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7, hours=6)
    return dst_start <= dt_utc < dst_end


def to_et(dt_utc: datetime) -> tuple[datetime, str]:
    offset_hours = -4 if is_dst(dt_utc) else -5
    label = "EDT" if offset_hours == -4 else "EST"
    return dt_utc + timedelta(hours=offset_hours), label


def is_trading_day(dt_utc: datetime) -> tuple[bool, str]:
    et_dt, _ = to_et(dt_utc)
    day = et_dt.weekday()  # 0=Mon … 6=Sun
    date_str = et_dt.strftime("%Y-%m-%d")
    if day >= 5:
        return False, "weekend"
    if date_str in KNOWN_HOLIDAYS:
        return False, "US market holiday"
    return True, "trading day"


def last_trading_day(dt_utc: datetime) -> str:
    """Return YYYY-MM-DD of the most recent market close relative to dt_utc (ET)."""
    et_dt, _ = to_et(dt_utc)
    minutes_et = et_dt.hour * 60 + et_dt.minute
    # Start from today's ET date; if before market close, the last close was yesterday
    candidate_date = et_dt.date()
    if minutes_et < US_MARKET_CLOSE_ET:
        candidate_date -= timedelta(days=1)
    for _ in range(10):
        candidate_utc = datetime(candidate_date.year, candidate_date.month,
                                 candidate_date.day, 12, tzinfo=timezone.utc)
        is_td, _ = is_trading_day(candidate_utc)
        if is_td:
            return candidate_date.strftime("%Y-%m-%d")
        candidate_date -= timedelta(days=1)
    return candidate_date.strftime("%Y-%m-%d")


def market_session(dt_utc: datetime) -> str:
    is_td, reason = is_trading_day(dt_utc)
    if not is_td:
        return reason
    et_dt, tz_label = to_et(dt_utc)
    minutes = et_dt.hour * 60 + et_dt.minute
    if minutes < US_MARKET_OPEN_ET:
        return f"pre-market ({tz_label})"
    if minutes < US_MARKET_CLOSE_ET:
        return f"regular session ({tz_label})"
    return f"after-hours ({tz_label})"


def parse_epoch(raw: str) -> tuple[float, str]:
    val = float(raw)
    if abs(val) > MS_THRESHOLD:
        return val / 1000.0, "ms"
    return val, "s"


def format_row(epoch_str: str) -> dict:
    sec, unit = parse_epoch(epoch_str)
    dt_utc = datetime.fromtimestamp(sec, tz=timezone.utc)
    et_dt, tz_label = to_et(dt_utc)
    last_td = last_trading_day(dt_utc)
    last_td_dt = datetime.strptime(last_td, "%Y-%m-%d")
    last_td_weekday = last_td_dt.strftime("%A")
    return {
        "raw": epoch_str,
        "unit": unit,
        "utc": dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "et": et_dt.strftime(f"%Y-%m-%d %H:%M:%S {tz_label}"),
        "weekday": et_dt.strftime("%A"),
        "date_et": et_dt.strftime("%Y-%m-%d"),
        "market": market_session(dt_utc),
        "last_trading_day": f"{last_td} ({last_td_weekday})",
        "ts_seconds": sec,
    }


def human_interval(seconds: float) -> str:
    if seconds < 0:
        return f"-{human_interval(-seconds)}"
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60}s"
    if s < 86400:
        h = s // 3600
        m = (s % 3600) // 60
        return f"{h}h {m}m"
    d = s // 86400
    rem = s % 86400
    return f"{d}d {rem // 3600}h" if rem else f"{d}d"


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python epoch_converter.py <epoch> [epoch2 epoch3 ...]")
        sys.exit(1)

    rows = [format_row(a) for a in args]

    print("=" * 62)
    print("EPOCH CONVERTER")
    print("=" * 62)

    for i, r in enumerate(rows):
        print(f"\n[{i + 1}] Raw: {r['raw']}  ({r['unit']})")
        print(f"    UTC : {r['utc']}")
        print(f"    ET  : {r['et']}  ({r['weekday']})")
        print(f"    Mkt : {r['market']}")
        print(f"    Last trading day: {r['last_trading_day']}")

    if len(rows) > 1:
        print("\n--- Intervals between consecutive timestamps ---")
        for i in range(1, len(rows)):
            delta = rows[i]["ts_seconds"] - rows[i - 1]["ts_seconds"]
            print(f"  [{i}→{i+1}] {human_interval(delta)}"
                  f"  ({rows[i-1]['date_et']} → {rows[i]['date_et']})")

        first_ts = rows[0]["ts_seconds"]
        last_ts = rows[-1]["ts_seconds"]
        total = last_ts - first_ts
        print(f"\n  Total span: {human_interval(total)}")
        print(f"  First date: {rows[0]['date_et']} ({rows[0]['weekday']})")
        print(f"  Last  date: {rows[-1]['date_et']} ({rows[-1]['weekday']})")

    print("=" * 62)


if __name__ == "__main__":
    main()
