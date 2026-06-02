---
name: portfolio-stress-test
description: >
  Run a comprehensive portfolio stress test covering historical crash scenarios
  (2008 GFC, 2020 COVID, 2022 rate shock, dot-com bust), hypothetical scenarios
  (rate shock, stagflation, AI bubble burst, EM/Japan crisis), single-position
  concentration sensitivity, Monte Carlo retirement simulation, and
  sequence-of-returns risk analysis. Use this skill whenever the user asks to
  "stress test the portfolio", "stress test", "run stress scenarios", "how would
  my portfolio do in a crash", "what if the market drops 40%", "recession impact",
  "tail risk analysis", "worst-case portfolio", "sequence of returns risk",
  "Monte Carlo simulation", "retirement survival probability", or any request
  involving portfolio resilience, downside scenarios, or crisis modeling. Also
  trigger when the user asks "how much could I lose", "what is my downside",
  or "can my portfolio survive a bear market". Always run this skill rather than
  estimating scenario outcomes from memory.
---

# Portfolio Stress Test Skill

Produces a six-section stress test report using the current Fidelity portfolio CSV
and a Python script that handles asset-class mapping, scenario shocks, position-level
detail, concentration sensitivity, Monte Carlo simulation, and retirement risk analysis.

---

## Step 1 — Load Portfolio Data

Read the most recent `/mnt/project/Portfolio_Positions_[DateStamp].csv` with
`utf-8-sig` encoding and `index_col=False` (required — the Fidelity CSV has a trailing
column that causes pandas to silently use Account Number as the row index if this flag
is omitted, corrupting all column reads).

**Parse rules:**
- Exclude rows where `Symbol` contains `**` (non-investment masked rows)
- Keep cash rows (`SPAXX`, `FDRXX`, `FCASH`, `FTEXX`) but tag as `asset_class = "cash"`
- Clean `Current Value` — strip `$`, `,`, `+`; treat `"--"` and blank as 0
- Compute `Weight = Current Value / Total Portfolio Value`
- Cash is excluded from stress shocks (it absorbs shocks as an opportunity fund)

**Also collect user inputs** needed for Monte Carlo (ask if not provided):
- `--retirement-year` (default: 2033)
- `--annual-spend` (annual retirement spending in dollars; 0 = not provided, skip SWR check)

---

## Step 2 — Run the Stress Test Script

Install dependencies and run:

```bash
pip install numpy pandas --break-system-packages -q

python /home/claude/portfolio-stress-test/scripts/stress_test.py \
  --portfolio /mnt/project/Portfolio_Positions_[latest].csv \
  --retirement-year 2033 \
  --annual-spend 120000 \
  --risk-free-rate 0.0525
```

The script produces six labeled sections (A–F) plus a findings summary.
Copy the full output into the analysis verbatim — do not paraphrase or summarize
the tables; they carry specific numbers the user needs.

---

## Step 3 — Interpret & Flag

After the script output, add a 4–6 sentence interpretation layer. Cover:

1. **Worst-case dollar loss** — what the GFC scenario implies in absolute terms
   and whether the portfolio survives retirement on Monte Carlo median
2. **Bond cushion gap** — if fixed income is below target (18%), quantify how much
   additional downside protection would come from completing the AGG/VCIT build-out
3. **Tech concentration** — AAPL + GOOGL + AMZN as % of portfolio; flag if combined
   weight > 12% (which it typically is); AI/Tech bubble scenario is the primary
   idiosyncratic tail risk for this portfolio
4. **Sequence-of-returns verdict** — given the retirement year and annual spend,
   is the Monte Carlo showing a ruin probability below 5%? Below 1%? Flag clearly.
5. **Cash deployment optionality** — cash positions are not subject to shocks;
   confirm they represent dry powder for Volatility Protocol deployment

---

## Step 4 — Elevate Flags to Section 18 (If Part of a Full Daily Report)

When this skill runs as part of the daily market analysis, elevate these findings
to Section 18 (Risk Factors & Recommended Actions):

| Condition | Flag |
|-----------|------|
| GFC scenario loss > 45% | 🔴 "Portfolio −$Xk in GFC scenario; accelerate bond build-out" |
| Monte Carlo p10 < $500K at retirement | 🔴 "Bear-case retirement shortfall; review spending assumptions" |
| Tech concentration > 12% of portfolio | 🟡 "Tech concentration risk: AAPL trim pending addresses this" |
| Monte Carlo ruin probability > 5% | 🔴 "Sequence-of-returns risk elevated; spending flexibility required" |
| AI/Tech bubble scenario > 18% loss | 🟡 "AI capex bubble tail risk: −$Xk; monitor AAPL/GOOGL guidance" |

---

## Scenario Library

The script includes 10 scenarios across two categories. All shocks are peak-to-trough.

### Historical Scenarios

| Scenario | S&P Shock | Bonds | EM | Tech | Notes |
|----------|-----------|-------|----|------|-------|
| 2008–2009 GFC | −57% | +5% | −61% | −52% | Credit crisis; most severe modern drawdown |
| 2020 COVID Crash | −34% | +2% | −31% | −28% | Fastest bear market; V-shaped recovery |
| 2022 Rate Shock | −19% | −13% | −20% | −33% | First year stocks AND bonds both fell >10% since 1969 |
| 2000–2002 Dot-Com | −49% | +30% | −28% | −78% | Tech-specific; bonds were true refuge |

### Hypothetical Scenarios

| Scenario | Equity | Bonds | EM | Tech | Key Driver |
|----------|--------|-------|----|------|------------|
| Mild Recession (−25%) | −25% | +4% | −28% | −28% | Growth scare |
| Severe Recession (−40%) | −40% | +8% | −45% | −45% | Deep contraction |
| Rate Shock +300 bps | −20% | −18% | −22% | −25% | Inflation reacceleration |
| Stagflation | −30% | −12% | −20% | −38% | Fed constrained |
| AI/Tech Bubble Burst | −20% | +3% | −15% | −50% | Capex disappointment |
| EM / Japan Crisis | −8% | +2% | −35% | −10% | BoJ reversal + EM outflows |

---

## Asset Class Mapping

The script classifies tickers automatically. Key mappings:

| Asset Class | Tickers |
|-------------|---------|
| `us_equity` | IVV, SPY, DIA, VTI, VINIX, FOCSX, VFIAX |
| `tech` | AAPL, GOOGL, AMZN, MSFT, NVDA, META, QQQ |
| `intl_developed` | IDEV, EFA, VEA, IDV |
| `japan` | EWJ, DXJ |
| `emerging_market` | VWO, IEMG, EEM |
| `em_bond` | EMHY, EMB |
| `high_div_eq` | VYM, RDVI, SCHD, DVY |
| `us_bond_agg` | AGG, BND |
| `corp_bond_ig` | VCIT, LQD, FBND, IGIB |
| `muni_bond` | FMUB, MUB, HYD, VTEB |
| `healthcare` | VHT, XLV |
| `biotech` | XBI, IBB |
| `target_date` | ITDC, and any ticker with "TARGET", "LIFEPATH", "2035" in description |
| `cash` | SPAXX, FDRXX, FCASH, FTEXX |

Unknown tickers default to `us_equity`. To add new tickers, edit the
ticker sets in `classify_ticker()` in `scripts/stress_test.py`.

---

## Monte Carlo Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| Annual return assumption | 7.0% | Moderate balanced portfolio long-run |
| Annual volatility | 12.0% | Historical balanced portfolio σ |
| Simulations | 5,000 | Sufficient for stable percentile estimates |
| Model | Lognormal | Daily returns → annual compounding |
| Withdrawals | User-provided `--annual-spend` | Applied at end of each simulated year |

**Outputs:**
- Percentile fan: p10, p25, p50, p75, p90 terminal values
- Ruin probability (portfolio reaches $0 before retirement year)
- Post-crash recovery paths: same simulation starting from the GFC-stressed value

**4% Rule context:** If `--annual-spend` is provided, the script reports the
Safe Withdrawal Rate (SWR = spend ÷ current portfolio value) and flags if it
exceeds 4% (caution), 5% (elevated risk), or 6%+ (critical).

---

## Output Format

The skill always produces this structure:

```
## Portfolio Stress Test — [Date]

[Script output: Sections A–F verbatim]

### Interpretation
[4–6 sentences: worst-case implications, bond gap, tech concentration,
Monte Carlo verdict, cash optionality]

### Section 18 Flags (if in full daily report)
[Flagged items per the threshold table above]
```

---

## Notes & Edge Cases

- **Script location:** `/home/claude/portfolio-stress-test/scripts/stress_test.py`
  The script persists in the Claude container for the session. If it is not found
  (new session), copy it from the skill path or recreate it — the full source is
  embedded in this skill's `scripts/` directory.
- **Cash exclusion:** Cash positions (FDRXX, SPAXX) are correctly excluded from
  shock calculations. Their $value appears in asset class summary but receives 0%
  shock. This is intentional — cash is the Volatility Protocol reserve.
- **Portfolio total:** The script reports investable assets (excluding cash).
  The "true" total appears in the CSV header row (all accounts summed).
- **Total portfolio context:** The stress test operates on the most recent CSV.
  If the user asks "how does this compare to last month?", load the prior snapshot
  CSV and run a comparison — the script accepts any portfolio CSV.
- **Custom scenarios:** If the user requests a specific scenario (e.g., "what if
  tech drops 60%?"), construct the shock dict manually and run `run_scenario()`
  from the script's functions directly via a one-off Python snippet.
- **`index_col=False` is mandatory:** Fidelity CSVs have trailing commas that
  cause pandas to silently misread columns if this parameter is omitted.
