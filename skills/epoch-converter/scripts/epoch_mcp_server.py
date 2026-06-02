#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["fastmcp"]
# ///
"""
MCP server for Claude Desktop — exposes epoch_convert as a tool.
Run via:  uvx fastmcp run epoch_mcp_server.py
"""

from fastmcp import FastMCP
from datetime import datetime, timezone, timedelta

mcp = FastMCP("epoch-converter")

MS_THRESHOLD = 1e10
US_MARKET_OPEN_ET = 9 * 60 + 30
US_MARKET_CLOSE_ET = 16 * 60

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


def _is_dst(dt_utc: datetime) -> bool:
    year = dt_utc.year
    march1 = datetime(year, 3, 1, tzinfo=timezone.utc)
    dst_start = march1 + timedelta(days=(6 - march1.weekday() + 7) % 7 + 7, hours=7)
    nov1 = datetime(year, 11, 1, tzinfo=timezone.utc)
    dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7, hours=6)
    return dst_start <= dt_utc < dst_end


def _to_et(dt_utc: datetime) -> tuple[datetime, str]:
    offset = -4 if _is_dst(dt_utc) else -5
    label = "EDT" if offset == -4 else "EST"
    return dt_utc + timedelta(hours=offset), label


def _is_trading_day(dt_utc: datetime) -> bool:
    et_dt, _ = _to_et(dt_utc)
    return et_dt.weekday() < 5 and et_dt.strftime("%Y-%m-%d") not in KNOWN_HOLIDAYS


def _market_session(dt_utc: datetime) -> str:
    et_dt, tz = _to_et(dt_utc)
    if et_dt.weekday() >= 5:
        return "weekend"
    if et_dt.strftime("%Y-%m-%d") in KNOWN_HOLIDAYS:
        return "US market holiday"
    m = et_dt.hour * 60 + et_dt.minute
    if m < US_MARKET_OPEN_ET:
        return f"pre-market ({tz})"
    if m < US_MARKET_CLOSE_ET:
        return f"regular session ({tz})"
    return f"after-hours ({tz})"


def _last_trading_day(dt_utc: datetime) -> str:
    et_dt, _ = _to_et(dt_utc)
    minutes = et_dt.hour * 60 + et_dt.minute
    candidate = et_dt.date()
    if minutes < US_MARKET_CLOSE_ET:
        candidate -= timedelta(days=1)
    for _ in range(10):
        probe = datetime(candidate.year, candidate.month, candidate.day,
                         12, tzinfo=timezone.utc)
        if _is_trading_day(probe):
            return candidate.strftime("%Y-%m-%d")
        candidate -= timedelta(days=1)
    return candidate.strftime("%Y-%m-%d")


def _human_interval(seconds: float) -> str:
    if seconds < 0:
        return f"-{_human_interval(-seconds)}"
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60}s"
    if s < 86400:
        return f"{s // 3600}h {(s % 3600) // 60}m"
    d, rem = divmod(s, 86400)
    return f"{d}d" if not rem else f"{d}d {rem // 3600}h"


def _convert_one(raw: str) -> dict:
    val = float(raw)
    unit = "ms" if abs(val) > MS_THRESHOLD else "s"
    sec = val / 1000.0 if unit == "ms" else val
    dt_utc = datetime.fromtimestamp(sec, tz=timezone.utc)
    et_dt, tz_label = _to_et(dt_utc)
    last_td = _last_trading_day(dt_utc)
    last_td_weekday = datetime.strptime(last_td, "%Y-%m-%d").strftime("%A")
    return {
        "raw": raw,
        "unit": unit,
        "ts_seconds": sec,
        "utc": dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "et": et_dt.strftime(f"%Y-%m-%d %H:%M:%S {tz_label}"),
        "date_et": et_dt.strftime("%Y-%m-%d"),
        "weekday": et_dt.strftime("%A"),
        "market_session": _market_session(dt_utc),
        "last_trading_day": f"{last_td} ({last_td_weekday})",
    }


@mcp.tool()
def epoch_convert(timestamps: list[str]) -> str:
    """
    Convert one or more Unix epoch timestamps (seconds or milliseconds) to
    human-readable dates with US Eastern time, day-of-week, market session
    status (pre-market / regular session / after-hours / weekend / holiday),
    and the most recent market close date. When multiple timestamps are given,
    also shows intervals between consecutive values so you can confirm whether
    a series is daily, intraday, or has gaps.

    Args:
        timestamps: List of epoch values as strings, e.g. ["1779768000"] or
                    ["1748822400000", "1748908800000"]. Mix of seconds and
                    milliseconds is fine — each is detected independently.
    """
    rows = [_convert_one(t) for t in timestamps]
    lines = ["EPOCH CONVERTER", "=" * 60]

    for i, r in enumerate(rows):
        lines.append(f"\n[{i+1}] {r['raw']}  ({r['unit']})")
        lines.append(f"    UTC : {r['utc']}")
        lines.append(f"    ET  : {r['et']}  ({r['weekday']})")
        lines.append(f"    Mkt : {r['market_session']}")
        lines.append(f"    Last trading day: {r['last_trading_day']}")

    if len(rows) > 1:
        lines.append("\n--- Intervals ---")
        for i in range(1, len(rows)):
            delta = rows[i]["ts_seconds"] - rows[i-1]["ts_seconds"]
            lines.append(f"  [{i}→{i+1}] {_human_interval(delta)}"
                         f"  ({rows[i-1]['date_et']} → {rows[i]['date_et']})")
        total = rows[-1]["ts_seconds"] - rows[0]["ts_seconds"]
        lines.append(f"\n  Span : {_human_interval(total)}")
        lines.append(f"  First: {rows[0]['date_et']} ({rows[0]['weekday']})")
        lines.append(f"  Last : {rows[-1]['date_et']} ({rows[-1]['weekday']})")

    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
