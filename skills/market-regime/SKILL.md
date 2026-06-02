---
name: market-regime
description: >
  Identify the current market regime (risk-on, risk-off, stagflation,
  late-cycle, early recovery, etc.) using macro indicators, credit spreads,
  yield curve shape, and momentum signals. Output a regime label, confidence
  level, and positioning implications. Trigger when the user asks "what regime
  are we in", "what does the macro environment look like", "should I be
  risk-on or risk-off", "how should I position given the current market",
  or any question about the macro backdrop and its implications for
  asset allocation.
---

# Market Regime Skill

Classifies the current market environment and translates it into
actionable portfolio tilts.

---

## Step 1 — Collect Macro Signals

Gather current readings for:

| Signal | Source | Regime Implication |
|--------|--------|--------------------|
| Yield curve (2s10s) | Fed / Treasury | Inverted = late cycle / recession risk |
| Credit spreads (IG/HY) | FRED / Bloomberg | Widening = risk-off |
| ISM Manufacturing PMI | ISM | <50 = contraction |
| ISM Services PMI | ISM | <50 = contraction |
| Unemployment trend | BLS | Rising = deteriorating |
| CPI YoY | BLS | >4% = inflation regime |
| Fed Funds trajectory | FOMC dots | Hiking = tightening cycle |
| VIX level | CBOE | >25 = elevated fear |
| S&P 500 vs 200-day MA | Price data | Below = bearish trend |
| Dollar (DXY) trend | — | Rising = EM/commodity headwind |

---

## Step 2 — Classify Regime

Map signals to one of six regimes:

| Regime | Key Signals | Asset Class Winners |
|--------|-------------|---------------------|
| **Early Recovery** | PMI bottoming, curve steepening, spreads tight | Cyclicals, Small-cap, EM |
| **Mid-Cycle Expansion** | PMI 50–60, curve normal, low vol | Broad equities, Quality |
| **Late Cycle** | PMI peaking, curve flattening, HY tight | Value, Energy, Short duration |
| **Risk-Off / Slowdown** | PMI <50, curve inverted, VIX rising | Treasuries, Gold, Low-vol equity |
| **Inflation / Stagflation** | CPI >4%, PMI weak, curve flat | Commodities, TIPS, Energy, Short duration |
| **Recession** | PMI <48, spreads wide, unemployment rising | Cash, Long Treasuries, Gold |

Assign a **primary regime** and a **confidence level** (High/Medium/Low)
based on how many signals align.

---

## Step 3 — Positioning Implications

For the identified regime, output a positioning tilt table:

| Asset Class | Current Weight | Tilt | Rationale |
|-------------|----------------|------|-----------|
| US Equity | X% | Overweight / Neutral / Underweight | |
| Intl Developed | X% | | |
| Emerging Markets | X% | | |
| US Bonds (Agg) | X% | | |
| Corp Bonds (IG) | X% | | |
| Cash | X% | | |
| Real Assets | X% | | |

Use the user's actual portfolio weights if a CSV is available;
otherwise use a generic balanced portfolio as baseline.

---

## Step 4 — Regime Change Triggers

List 3–5 specific data points that would signal a regime shift:
- e.g., "ISM Manufacturing crossing back above 50 for two consecutive months"
- e.g., "2s10s un-inverting while unemployment ticks above 4.5%"

---

## Output Format

```
## Market Regime — [Date]

**Current Regime:** [Label] | **Confidence:** [High/Medium/Low]

### Signal Dashboard
[table from Step 1 with current values filled in]

### Positioning Tilts
[table from Step 3]

### Regime Change Triggers
- [trigger 1]
- [trigger 2]
- [trigger 3]

### Summary
[2–3 sentences: what the regime means for the next 3–6 months and
the single most important risk to watch]
```
