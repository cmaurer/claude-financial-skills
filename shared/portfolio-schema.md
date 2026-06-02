# Portfolio Schema

Standard field names and types used across all financial skills when reading
portfolio CSV exports (Fidelity format).

## CSV Fields

| Field | Type | Notes |
|-------|------|-------|
| `Account Number` | string | Masked in exports; treat as opaque ID |
| `Account Name` | string | e.g. "Individual - TOD", "Roth IRA" |
| `Symbol` | string | Ticker; rows with `**` are non-investment (exclude) |
| `Description` | string | Full security name |
| `Quantity` | float | Shares held; may be fractional |
| `Last Price` | float | Strip `$`; `--` → 0 |
| `Last Price Change` | float | Strip `$`, `+`; `--` → 0 |
| `Current Value` | float | Strip `$`, `,`, `+`; `--` → 0 |
| `Today's Gain/Loss Dollar` | float | Strip `$`, `+`; `--` → 0 |
| `Today's Gain/Loss Percent` | float | Strip `%`, `+`; `--` → 0 |
| `Total Gain/Loss Dollar` | float | Strip `$`, `+`; `--` → 0 |
| `Total Gain/Loss Percent` | float | Strip `%`, `+`; `--` → 0 |
| `Percent Of Account` | float | Strip `%`; `--` → 0 |
| `Cost Basis Per Share` | float | Strip `$`; `--` → 0 (e.g. lots not tracked) |
| `Cost Basis Total` | float | Strip `$`, `,`; `--` → 0 |
| `Type` | string | e.g. "Cash", "Equity", "Mutual Fund", "ETF" |

## Parse Rules (apply to every skill)

```python
import pandas as pd

def load_portfolio(path):
    df = pd.read_csv(path, encoding="utf-8-sig", index_col=False)
    # Drop non-investment rows (masked symbols)
    df = df[~df["Symbol"].astype(str).str.contains(r"\*\*", na=False)]
    # Numeric cleaner
    def clean(col):
        return (df[col].astype(str)
                .str.replace(r"[\$,+%]", "", regex=True)
                .str.strip()
                .replace({"--": "0", "": "0"})
                .astype(float))
    for col in ["Current Value", "Cost Basis Total", "Quantity",
                "Last Price", "Total Gain/Loss Dollar"]:
        df[col] = clean(col)
    return df
```

## Cash Tickers

`SPAXX`, `FDRXX`, `FCASH`, `FTEXX` — tag as `asset_class = "cash"`.
Cash is excluded from stress shocks; it is treated as dry powder.

## Account Type Tags

| Account Name substring | Type |
|------------------------|------|
| `Roth` | roth_ira |
| `Traditional` / `Rollover` | trad_ira |
| `Individual` / `TOD` | taxable |
| `HSA` | hsa |
