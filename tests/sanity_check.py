import pandas as pd
from pathlib import Path

base = Path("data/synthetic")
feed = pd.read_csv(base / "bank_feed_2026-03-06.csv")          # choose the date you actually use
ledger = pd.read_json(base / "internal_ledger_2026-03-06.json")

merged = feed.merge(ledger, on="trade_id", suffixes=("_bank", "_ledger"))
print(((merged["notional_bank"] != merged["notional_ledger"]) |
       (merged["rate_bank"] != merged["rate_ledger"]) |
       (merged["settlement_date_bank"] != merged["settlement_date_ledger"]) |
       (merged["status_bank"] != merged["status_ledger"])).any())