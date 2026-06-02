# Investment Scorecard Skill

Produces a structured 7-step scorecard for any individual stock. Each step is rated 1–10, 
weighted by importance, and combined into a total score with a clear investment decision.
The framework emphasizes qualitative judgment alongside quantitative data — think like a 
disciplined fundamental investor, not a quant screener.

## References

https://investimate.substack.com/p/my-complete-stock-analysis-framework

---

## Before You Start

Pull the following context in parallel before scoring. You need real data, not guesses.

**Data to gather upfront:**
- Current stock price, market cap, EV (market cap + total debt − cash)
- Trailing 12M and 5-year revenue, net income, free cash flow
- Gross margin, operating margin, net margin trends (5-year)
- Return on Invested Capital (ROIC) — 5-year trend
- Balance sheet: total debt, cash, goodwill, debt/EBITDA
- Forward P/E, EV/EBIT (trailing and 5-year average), FCF yield
- Recent news, management changes, analyst sentiment
- Glassdoor rating and recent employee review themes (web search: "[company] Glassdoor reviews [year]")
- Founder/insider ownership % and recent Form 4 activity

Use the Massive Market Data MCP, AlphaVantage, FRED, and web search as needed.
If equity-analysis has already been run for this ticker in this session, reuse its data rather than re-fetching.

---

## Step 1 — Business Model & Industry Attractiveness (HIGH WEIGHT)

**The core question:** Can you explain how this company makes money to a non-investor in two sentences? If not, that's a signal.

**Evaluate:**
- **Revenue clarity:** Where does money come from? How predictable and recurring is it?
- **Industry structure:** Competitive intensity (Porter-style), barriers to entry, supplier/buyer power
- **Market trajectory:** Secular growth, cyclical, or in structural decline?
- **Business model elegance:** Simple + durable beats complex + fragile every time

**Scoring guide:**
| Score | Meaning |
|-------|---------|
| 9–10 | Simple model, dominant position, growing market, high barriers |
| 7–8 | Clear model, good positioning, some competitive pressure |
| 5–6 | Understandable but commoditized or in a challenged market |
| 3–4 | Complex, competitive, or structurally declining industry |
| 1–2 | Opaque model, no clear differentiation, shrinking TAM |

**Step 1 Score: ___/10**

---

## Step 2 — Management Quality & Competitive Moat (HIGH WEIGHT)

**Two sub-scores averaged together.**

### 2A — Management Quality

**Evaluate:**
- **Founder-led or founder DNA?** Founders with meaningful ownership stakes think like owners, not tenants. Big plus.
- **Capital allocation track record:** Has management created or destroyed value over 5–10 years? ROIC trend is the truth-teller.
- **Insider ownership %:** Meaningful skin in the game (>5% for large-cap, >15% for small/mid)?
- **Employee sentiment:** Check Glassdoor — high ratings (4.0+), CEO approval >80%, stable trend. Low or deteriorating scores are a yellow flag.
- **Communication quality:** Are earnings calls / investor letters clear, honest, and consistent? Do they admit mistakes?

### 2B — Moat Analysis

Classify the primary moat type (pick the dominant one):

| Moat Type | Description | Examples |
|-----------|-------------|---------|
| **Network effects** | Product gets better/stickier as more users join | Visa, MSFT Office, Meta |
| **Switching costs** | Painful or expensive to leave | Salesforce, Adobe, Oracle |
| **Cost advantage** | Structurally lower costs through scale or IP | Costco, TSMC, Amazon logistics |
| **Intangibles** | Brands, patents, licenses, regulatory moats | LVMH, J&J, Verisign |
| **Efficient scale** | Natural monopoly dynamics in small markets | Waste Management, pipelines |
| **No moat** | Competing on price alone; easily disintermediated | — |

**Moat durability check:** High and consistent gross margins (>40% for software, >30% for consumer) + rising ROIC = real pricing power. Declining gross margins + falling ROIC = moat erosion.

**Step 2 Score: ___/10** (average of 2A and 2B)

---

## Step 3 — Financial Health & Capital Allocation (MEDIUM WEIGHT)

**Balance sheet health:**
- Debt/EBITDA: <2x is conservative; >4x raises concern (industry-adjusted)
- Goodwill as % of total assets: Elevated goodwill means acquisition-heavy history — watch for impairments
- Interest coverage (EBIT/interest expense): Should comfortably exceed 3x
- Cash runway: How many quarters can they operate without external capital if revenue stops?

**Capital allocation quality:**
Management has four options for generated cash. The right choice depends on context — reward them for choosing wisely, penalize for mismatches:

| Action | When it's smart | When it's a red flag |
|--------|----------------|---------------------|
| Reinvest in business | ROIC > WACC, growing market | ROIC < WACC, no growth left |
| Pay dividends | Mature, stable FCF, limited growth | Starving growth to maintain payout |
| Buy back shares | Stock clearly undervalued | Buying back at peak; levering up to do it |
| Acquire | Accretive, strategic, disciplined price | Empire building; goodwill pile-up |

**ROIC trend is the verdict:** Rising ROIC over 5 years = excellent allocation. Flat or falling ROIC despite acquisitions = value destruction.

**Step 3 Score: ___/10**

---

## Step 4 — Profitability & Cash Generation (HIGH WEIGHT)

**Key principle:** Earnings are an opinion; cash flow is a fact. A business that consistently converts reported profits into free cash flow is telling you the truth about its economics.

**Metrics to evaluate:**
- **FCF/Net Income ratio:** Should be close to 1.0 (or above). Persistently below 0.7 signals aggressive accounting or capex-heavy model.
- **Margin trend:** Are gross, operating, and net margins stable or expanding? Compression needs explanation.
- **Cash conversion cycle:** For product businesses — is working capital efficient?
- **Dividend quality (if applicable):** Payout ratio sustainable? FCF coverage of dividend >1.5x?

**Quality indicators to check:**
- Non-cash charges (D&A as % of capex): large gaps can signal accounting vs. economic mismatch
- Accounts receivable growing faster than revenue? (potential pull-forward)
- Inventory building faster than revenue? (potential demand problem)

**Step 4 Score: ___/10**

---

## Step 5 — Growth Track Record & Sustainability (MEDIUM WEIGHT)

**Historical record (past 5–10 years):**
- Revenue CAGR: Consistent or lumpy? Organic or acquisition-driven?
- EPS CAGR: Growing faster or slower than revenue? (margin expansion vs. buyback math vs. dilution)
- ROIC trend: Rising = quality compounder; falling = growth at the expense of returns

**Sustainability assessment:**
Real growth vs. manufactured growth:

| Real Growth | Warning Signs |
|-------------|--------------|
| Organic revenue expansion | Revenue growth via acquisitions, accounting changes |
| Market share gains in growing market | Share gains in shrinking market |
| Expanding into new geographies/verticals | Entering unrelated businesses (conglomerate risk) |
| Network effects reinforcing position | One-time tailwinds (stimulus, pandemic pull-forward) |

**Forward sustainability signals:**
- Expanding TAM with clear runway?
- Product innovation pipeline visible?
- Pricing power demonstrated (can they raise prices without losing volume)?
- International expansion early innings or tapped out?

**Step 5 Score: ___/10**

---

## Step 6 — Risk Assessment & Future Outlook (HIGH WEIGHT)

**Risk radar — evaluate each category:**

| Risk Type | Questions to ask |
|-----------|-----------------|
| **Technology disruption** | Could AI, software, or a platform player make this business obsolete in 10 years? |
| **Competitive entry** | Are well-funded competitors (Big Tech, private equity-backed) entering? |
| **Regulatory / political** | Antitrust exposure? Healthcare pricing reform? Environmental liability? |
| **Economic cyclicality** | What happened to revenue and margins in 2008, 2020? How bad was it? |
| **Concentration risk** | Top 3 customers > 30% of revenue? Single geography > 70%? Key-person dependency? |
| **Balance sheet fragility** | Can they service debt through a 30% revenue decline? |

**The black swan test:** If this company faced its single worst plausible outcome (key customer loss, major litigation, recession + credit crunch, disruptive technology), would it survive and recover? Strong businesses have multiple layers of protection.

**Future outlook:**
- Is the competitive position strengthening, holding, or eroding?
- Management's stated strategy — does it make sense given the competitive landscape?
- Industry tailwinds or headwinds over the next 3–5 years?

**Step 6 Score: ___/10**

---

## Step 7 — Valuation: Three-Pillar Approach (MEDIUM WEIGHT)

Don't just look up one multiple. Use all three pillars — they answer different questions and together give a complete picture.

### Pillar 1: Reverse DCF — What Is the Market Pricing In?

Instead of forecasting the future, work backwards from the current stock price.

**Method:**
1. Take current EV and FCF
2. Assume your required return rate (10–12% is reasonable for individual investors)
3. Solve for the implied FCF growth rate the stock price requires to justify that return

Then ask: **Is that implied growth rate realistic given this company's actual competitive position?**

- Market pricing in 20% growth for a company in a mature, slow-growing industry? Red flag — overvalued.
- Market pricing in 5% growth for a dominant company in a fast-expanding market? Green flag — potential opportunity.

### Pillar 2: FCF Yield — Are You Getting Paid?

```
FCF Yield = Trailing Free Cash Flow ÷ Enterprise Value
```

| FCF Yield | Signal |
|-----------|--------|
| 8%+ | High cash generation relative to price — attractive |
| 5–8% | Reasonable; check growth to justify premium |
| 3–5% | Modest; must have strong growth or moat to justify |
| <3% | Low yield — needs extraordinary growth or quality |

FCF yield is harder to game than P/E. Compare to the company's own 5-year average FCF yield — is the current yield high or low by historical standards?

### Pillar 3: EV/EBIT — Operating Efficiency, Capital-Structure Neutral

```
EV/EBIT = Enterprise Value ÷ Operating Income (EBIT)
```

Preferred over P/E because it:
- Removes the distortion of different capital structures (debt levels)
- Excludes one-time items and financial engineering
- Represents what a real acquirer would evaluate

**Compare on three axes:**
1. Current EV/EBIT vs. company's own 5-year average (premium or discount to self?)
2. Current EV/EBIT vs. direct industry peers
3. Current EV/EBIT vs. S&P 500 median (~17–19x in most cycles)

**Pillar alignment check:**
- All 3 signal attractive → strong valuation case
- 2 of 3 → worth deeper look; add to watch list
- 1 of 3 → likely wait for a better entry point

**Step 7 Score: ___/10**

---

## Scan mode (batch use)

When invoked with "scan mode" or as part of a batch by an orchestrator, skip
the narrative and widget entirely. Output ONLY this JSON object and nothing else
— no preamble, no markdown fences, no explanation:

{
  "ticker": "AAPL",
  "company": "Apple Inc.",
  "price": 312.00,
  "market_cap_b": 4580,
  "scores": {
    "step1_business_model": 9,
    "step2_management_moat": 8,
    "step3_financial_health": 8,
    "step4_profitability": 9,
    "step5_growth": 7,
    "step6_risk": 6,
    "step7_valuation": 4
  },
  "weighted_total": 7.4,
  "verdict": "WATCH LIST",
  "top_flags": [
    "FCF yield 2.86% — below floor",
    "CEO transition risk (Ternus, Sept 2026)",
    "DOJ antitrust trial 2027"
  ],
  "data_gaps": []
}

The weighted_total must use the same formula as full mode:
HIGH steps (1,2,4,6) × 1.5, MEDIUM steps (3,5,7) × 1.0, divided by 9, ×10.

---

## Final Scorecard Output

After completing all 7 steps, produce the scorecard in this exact format:

```
═══════════════════════════════════════════════════════
  INVESTMENT SCORECARD — [TICKER] / [COMPANY NAME]
  Analysis Date: [DATE]
═══════════════════════════════════════════════════════

STEP                              WEIGHT    SCORE
─────────────────────────────────────────────────────
Step 1: Business Model            HIGH      __ /10
Step 2: Management & Moat         HIGH      __ /10
Step 3: Financial Health          MEDIUM    __ /10
Step 4: Profitability & FCF       HIGH      __ /10
Step 5: Growth Track Record       MEDIUM    __ /10
Step 6: Risk Assessment           HIGH      __ /10
Step 7: Valuation                 MEDIUM    __ /10
─────────────────────────────────────────────────────
WEIGHTED TOTAL SCORE                        __ /10

VERDICT: [STRONG BUY / WATCH LIST / CONDITIONAL / PASS]
═══════════════════════════════════════════════════════
```

**Weighted total calculation:**
- HIGH weight steps (1, 2, 4, 6): each counts 1.5x
- MEDIUM weight steps (3, 5, 7): each counts 1.0x
- Total = (sum of HIGH scores × 1.5 + sum of MEDIUM scores × 1.0) ÷ (4×1.5 + 3×1.0) × 10

**Verdict thresholds:**
| Score | Verdict |
|-------|---------|
| 8.0–10 | 🟢 STRONG BUY — High quality at attractive valuation |
| 6.0–7.9 | 🟡 WATCH LIST — Good company; wait for better price or confirm thesis |
| 4.0–5.9 | 🟠 CONDITIONAL — Significant issues; deeper analysis needed before considering |
| < 4.0 | 🔴 PASS — Too many red flags; better opportunities exist |

---

## After the Scorecard

Always close with three things:

1. **The Bull Case in one sentence** — what has to go right for this to be a great investment
2. **The Bear Case in one sentence** — what single risk would most likely derail the thesis
3. **The Trigger** — what specific data point or event would move this from Watch List to Buy, or confirm the Pass decision

---

## Tone and Style

- Score honestly — a 10 is extremely rare; most quality businesses score 6–8
- Every score should be accompanied by a 2–3 sentence rationale explaining why
- Flag data gaps explicitly rather than papering over them with assumptions
- If a step is genuinely ambiguous or data is missing, score conservatively and note the uncertainty
- This is a judgment framework, not a mechanical screener — use it like a disciplined analyst, not a formula