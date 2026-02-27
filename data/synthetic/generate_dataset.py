#Imports
import random
import json
import csv
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()


CURRENCY_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "GBP/EUR"]
COUNTERPARTIES = ["Barclays PLC", "Deutsche Bank AG", "HSBC Holdings", "Societe Generale", "BNP Paribas"]
STATUSES = ["OPEN", "SETTLED", "PENDING"]

def generate_base_trades(n):
    trades = []
    for _ in range(n):
        notional = round(random.uniform(10_000,5_000_000), 2)
        trade_date = fake.date_between(start_date="-30d", end_date="today")
        trades.append({
            "trade_id": fake.uuid4(),
            "counterparty": random.choice(COUNTERPARTIES),
            "currency_pair": random.choice(CURRENCY_PAIRS),
            "notional": notional,
            "rate": rate,
            "settlement_date": (trade_date + timedelta(days=2)).isoformat(),
            "status": random.choice(STATUSES),
            "created_at": datetime.now().isoformat()
        })
    return trades

def apply_notional_mismatches(trade, pct=0.05):
    if random.random() < pct:
        trade["notional"] = round(trade["notional"] * random.uniform(0.95, 1.05), 2)
    return trade
    

def apply_rate_mismatches(trade, pct=0.03):
    if random.random() < pct:
        trade["rate"] = round(trade["rate"] * random.uniform(0.98, 1.02), 6)
    return trade
    

def apply_settlement_mismatches(trade, pct=0.03):
    if random.random() < pct:
        original = datetime.fromisoformat(trade["settlement_date"])
        trade["settlement_date"] = (original + timedelta(days=random.choice([-1, 1]))).isoformat()
    return trade
    

def remove_random_trades(trades, pct=0.02):
    return [t for t in trades if random.random() > pct]
    

def add_extra_trades(trades, pct=0.02):
    extras = []
    for trade in trades:
        if random.random() < pct:
            dupe = trade.copy()
            dupe["trade_id"] = fake.uuid4()  # new ID so it looks like a ghost trade
            extras.append(dupe)
    return trades + extras
    

def generate_ledger_feed(base_trades: list[dict]) -> list[dict]:
    """Apply all distortions to produce the internal ledger variant."""
    ledger = []
    for trade in base_trades:
        t = trade.copy()
        t = apply_notional_mismatches(t)
        t = apply_rate_mismatches(t)
        t = apply_settlement_mismatches(t)
        ledger.append(t)
    ledger = remove_random_trades(ledger)
    ledger = add_extra_trades(ledger)
    return ledger


def write_csv(trades: list[dict], filepath: str) -> None:
    if not trades:
        return
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=trades[0].keys())
        writer.writeheader()
        writer.writerows(trades)


def write_json(trades: list[dict], filepath: str) -> None:
    with open(filepath, "w") as f:
        json.dump(trades, f, indent=2)


if __name__ == "__main__":
    random.seed(42)  # reproducible breaks for demos

    base_trades = generate_base_trades(200)

    # Bank feed — clean source of truth
    write_csv(base_trades, "data/synthetic/bank_feed.csv")

    # Internal ledger — distorted variant
    ledger = generate_ledger_feed(base_trades)
    write_json(ledger, "data/synthetic/internal_ledger.json")

    print(f"Generated {len(base_trades)} base trades → bank_feed.csv")
    print(f"Generated {len(ledger)} ledger trades → internal_ledger.json")