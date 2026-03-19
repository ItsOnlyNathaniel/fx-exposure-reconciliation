#Imports
import random
import json
import csv
from datetime import datetime, timedelta
from faker import Faker
from pathlib import Path

fake = Faker()


CURRENCY_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "GBP/EUR"]
PAIR_RATE_RANGES = {
    "EUR/USD": (1.04, 1.12),
    "GBP/USD": (1.24, 1.32),
    "USD/JPY": (145.0, 155.0),
    "USD/CHF": (0.87, 0.93),
    "AUD/USD": (0.60, 0.68),
    "USD/CAD": (1.34, 1.42),
    "GBP/EUR": (1.14, 1.22),}
COUNTERPARTIES = ["Barclays PLC", "Deutsche Bank AG", "HSBC Holdings", "Societe Generale", "BNP Paribas"]
STATUSES = ["OPEN", "SETTLED", "PENDING"]

def generate_base_trades(n):
    trades = []
    for _ in range(n):
        notional = round(random.uniform(10_000,5_000_000), 2)
        trade_date = fake.date_between(start_date="-30d", end_date="+5d")
        settlement_date = (trade_date + timedelta(days=2))

        currency_pair = random.choice(CURRENCY_PAIRS)
        low,high = PAIR_RATE_RANGES[currency_pair]
        rate=round(random.uniform(low,high), 6)
        pair_compact = currency_pair.replace("/", "")
        base_currency = pair_compact[:3]
        quote_currency = pair_compact[3:6]

        trades.append({
            "trade_id": fake.uuid4(),
            "counterparty": random.choice(COUNTERPARTIES),
            "currency_pair": currency_pair,
            "base_currency": base_currency,
            "quote_currency": quote_currency,
            "notional": notional,
            "rate": rate,
            "trade_date": trade_date.isoformat(),
            "settlement_date": settlement_date.isoformat(),
            "status":assign_status(settlement_date.isoformat()),
            "created_at": datetime.now().isoformat()
        })
    return trades

def assign_status(settlement_date: str):
    settlement = datetime.fromisoformat(settlement_date)
    today = datetime.today()
    if settlement < today:
        return random.choice(["SETTLED", "FAILED"])
    elif settlement == today:
        return "PENDING"
    else:
        return random.choice(["OPEN", "PENDING"])

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

    BASE_PATH = Path(__file__).resolve().parent
    file_name= datetime.today().strftime('bank_feed_%Y-%m-%d.csv')
    with open(BASE_PATH / file_name, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=trades[0].keys())
        writer.writeheader()
        writer.writerows(trades)


def write_json(trades: list[dict], filepath: str) -> None:
    BASE_PATH = Path(__file__).resolve().parent
    file_name= datetime.today().strftime('internal_ledger_%Y-%m-%d.json')
    with open(BASE_PATH / file_name, "w") as f:
        json.dump(trades, f, indent=2)


def main():
    random.seed(42)  # reproducible breaks for demos

    base_trades = generate_base_trades(800)

    # Bank feed — clean source of truth
    write_csv(base_trades, "data/synthetic/bank_feed.csv")

    # Internal ledger — distorted variant
    ledger = generate_ledger_feed(base_trades)
    write_json(ledger, "data/synthetic/internal_ledger.json")

    print(f"Generated {len(base_trades)} base trades → bank_feed.csv")
    print(f"Generated {len(ledger)} ledger trades → internal_ledger.json")

if __name__ == "__main__":
    main()