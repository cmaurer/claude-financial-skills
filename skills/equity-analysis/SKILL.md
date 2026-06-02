---
name: equity-analysis
description: >
  Run a comprehensive equity analysis on a single stock, covering valuation
  (DCF, comps, EV/EBITDA), quality (ROIC, FCF margin, balance sheet),
  growth (revenue CAGR, TAM), moat assessment, and a buy/hold/sell verdict
  with price target. Trigger when the user asks to "analyze [ticker]",
  "research [company]", "what do you think of [stock]", "is [ticker] a good
  buy", or any request for equity due diligence on a named company.
---

# Equity Analysis Skill

Produces an institutional-grade single-stock research note.

---

## Step 1 — Gather Data

Use the financial news MCP tools and web search to collect:

- Latest earnings (EPS, revenue, guidance)
- Analyst consensus price target and rating distribution
- Key valuation multiples: P/E, EV/EBITDA, P/FCF, P/S
- Balance sheet: net debt/EBITDA, current ratio
- Growth metrics: 3-year revenue CAGR, forward revenue growth estimate
- Insider and institutional ownership changes (last quarter)

---

## Step 2 — Valuation

Run a simplified DCF in Python:
- Base case: consensus revenue growth tapering to 3% terminal; EBIT margin at
  analyst consensus; WACC from sector average
- Bull / Bear cases: ±20% on growth and margin assumptions
- Output: implied price range across all three cases

---

## Step 3 — Quality Scorecard

Score 1–5 on each dimension (5 = best):

| Dimension | Signal | Score |
|-----------|--------|-------|
| Profitability | ROIC vs WACC spread | |
| FCF Quality | FCF / Net Income ratio | |
| Balance Sheet | Net debt / EBITDA | |
| Capital Allocation | Buyback yield + dividend | |
| Management | Guidance accuracy (last 4 quarters) | |

---

## Step 4 — Moat Assessment

Classify as: **Wide / Narrow / None**

Evaluate: switching costs, network effects, cost advantage, intangibles,
efficient scale. Cite specific evidence (e.g., gross margin trend, churn data).

---

## Step 5 — Verdict

State: **Buy / Hold / Sell** with a 12-month price target and confidence level.

Format: `[TICKER] — [Verdict] | Target: $X | Confidence: High/Medium/Low`

Justify in 3–4 sentences covering valuation, quality, and key risk.

---

## References

See `references/stocks.md`, `references/etfs.md`, `references/mutual-funds.md`
for sector benchmarks and comparable company sets.
