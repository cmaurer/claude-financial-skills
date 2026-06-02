---
name: investment-scorecard
description: >
  Score a potential investment on a structured rubric covering valuation,
  quality, momentum, risk, and fit with the existing portfolio. Outputs a
  numeric score (0–100), letter grade, and buy/pass recommendation with
  supporting rationale. Trigger when the user asks "should I buy [ticker]",
  "score [investment]", "is [ticker] worth adding", or wants a structured
  framework for evaluating a new position.
---

# Investment Scorecard Skill

Produces a structured 0–100 score across five dimensions, a letter grade,
and a clear buy/pass recommendation.

---

## Scoring Rubric

Each dimension is scored 0–20. Total = sum across all five.

### 1. Valuation (0–20)

| Score | Criteria |
|-------|----------|
| 18–20 | Trading at >30% discount to intrinsic value; clear margin of safety |
| 14–17 | Modestly undervalued or fairly valued with strong growth |
| 10–13 | Fair value; no meaningful discount |
| 5–9 | Slightly overvalued; growth must execute perfectly |
| 0–4 | Significantly overvalued; speculative |

### 2. Quality (0–20)

Score based on: ROIC vs WACC, FCF margin, balance sheet leverage, moat width.
Use thresholds from `references/portfolio-schema.md` quality table.

| Score | Criteria |
|-------|----------|
| 18–20 | Wide moat, ROIC >20%, FCF margin >20%, net debt <1x EBITDA |
| 14–17 | Narrow moat, solid profitability, manageable leverage |
| 10–13 | No clear moat, adequate profitability |
| 5–9 | Cyclical or leveraged; quality concerns |
| 0–4 | Distressed or structurally impaired |

### 3. Momentum (0–20)

Based on price momentum (3m, 6m, 12m), earnings revision trend, and
analyst estimate changes (last 90 days).

| Score | Criteria |
|-------|----------|
| 18–20 | Strong price + earnings momentum; positive revisions |
| 14–17 | Neutral-to-positive momentum |
| 10–13 | Mixed signals |
| 5–9 | Negative momentum; estimate cuts |
| 0–4 | Breaking down; consensus deteriorating |

### 4. Risk (0–20)

Lower risk = higher score. Evaluate: volatility (beta), sector concentration
in existing portfolio, balance sheet risk, regulatory/litigation overhang.

| Score | Criteria |
|-------|----------|
| 18–20 | Low beta, no concentration risk, clean balance sheet |
| 14–17 | Moderate risk, manageable |
| 10–13 | Some concentration or leverage risk |
| 5–9 | Elevated risk; requires position sizing discipline |
| 0–4 | High risk; binary outcome or structural problem |

### 5. Portfolio Fit (0–20)

Does adding this position improve diversification, fill a gap, or align with
the current strategy? Penalize if it increases existing tech/sector concentration.

| Score | Criteria |
|-------|----------|
| 18–20 | Fills a gap; reduces concentration; aligns with strategy |
| 14–17 | Additive without increasing concentration |
| 10–13 | Neutral fit |
| 5–9 | Minor overlap with existing positions |
| 0–4 | Increases already-elevated concentration; misaligned |

---

## Grade Scale

| Score | Grade | Recommendation |
|-------|-------|----------------|
| 85–100 | A | Strong Buy — size to full target |
| 70–84 | B | Buy — initiate at half position |
| 55–69 | C | Watch — revisit on pullback or catalyst |
| 40–54 | D | Pass — not compelling at current price |
| 0–39 | F | Avoid — thesis broken or deeply overvalued |

---

## Output Format

```
## Investment Scorecard — [TICKER] — [Date]

| Dimension | Score | Notes |
|-----------|-------|-------|
| Valuation | X/20 | ... |
| Quality | X/20 | ... |
| Momentum | X/20 | ... |
| Risk | X/20 | ... |
| Portfolio Fit | X/20 | ... |
| **Total** | **X/100** | **Grade: X** |

**Recommendation:** [Buy / Watch / Pass / Avoid]
**Suggested Position Size:** [% of portfolio or $ amount]

[3–4 sentence rationale covering the key drivers of the score and the
primary risk to the thesis.]
```
