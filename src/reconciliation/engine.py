import pandas as pd
from pathlib import Path

# Read in the data relative to project root
BASE_PATH = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_PATH / "data" / "synthetic"

feed_path = DATA_PATH / "bank_feed.csv"
ledger_path = DATA_PATH / "internal_ledger.json"

feed_df = pd.read_csv(feed_path)
ledger_df = pd.read_json(ledger_path)

print(feed_df.head())
print(ledger_df.head())

breaks = pd.DataFrame(columns=['trade_id', 'break_type', 'severity', 'reconciled'])
'''
# O(n * m) solution
for index, row in feed_df.iterrows():
    trade_id = row['trade_id']
    counterparty = row['counterparty']
    currency_pair = row['currency_pair']
    notional = row['notional']
    rate = row['rate']
    settlement_date = row['settlement_date']
    status = row['status']
    created_at = row['created_at']

    for index, row in ledger_df.iterrows():
        ledger_trade_id = row['trade_id']
        ledger_counterparty = row['counterparty']
        ledger_currency_pair = row['currency_pair']
        ledger_notional = row['notional']
        ledger_rate = row['rate']
        ledger_settlement_date = row['settlement_date']
        ledger_status = row['status']
        ledger_created_at = row['created_at']
'''

# Hash lookup solution - O(n + m)
def reconcile_trades(feed_df, ledger_df):

    RATE_TOLERANCE = 0.0001
    NOTIONAL_TOLERANCE = 0.01

    matched = pd.merge(ledger_df, feed_df, on='trade_id', suffixes=("_bank", "_ledger"), how='outer', indicator=True)
    matched_both = matched[matched["_merge"] == "both"].copy()

    if matched_both.empty:
        return pd.DataFrame(columns=["trade_id", "break_type"])

    matched_both["rate_mismatch"] = (
        matched_both["rate_feed"] - matched_both["rate_ledger"]).abs() > RATE_TOLERANCE
    matched_both["notional_mismatch"] = (
        matched_both["notional_amount_feed"] - matched_both["notional_amount_ledger"]).abs() > NOTIONAL_TOLERANCE
    matched_both["settlement_mismatch"] = (
        matched_both["settlement_date_bank"] != matched_both["settlement_date_ledger"])
    matched_both["status_mismatch"] = (
        matched_both["status"] != matched_both["status_ledger"]    )

    def classify_break(row: pd.Series):
        if row["rate_mismatch"]:
            breaks.append({
            'trade_id': row['trade_id'],
            'break_type': 'rate_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
            return "RATE_MISMATCH"

        if row["notional_mismatch"]:
            breaks.append({
            'trade_id': row['trade_id'],
            'break_type': 'notional_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
            return "NOTIONAL_MISMATCH"

        if row["settlement_mismatch"]:
            breaks.append({
            'trade_id': row['trade_id'],
            'break_type': 'settlement_date_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
            return "TIMING_DIFFERENCE"

        if row["status_mismatch"]:
            breaks.append({
            'trade_id': row['trade_id'],
            'break_type': 'status_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
            return "STATUS_MISMATCH"
        return None

    matched_both["break_type"] = matched_both.apply(classify_break, axis=1)
    breaks = matched_both[matched_both["break_type"].notna()].copy()
    return breaks



'''
# Match trades by trade_id, diff on value fields
def match_trades(trade_id, ledger_trade_id):    
    if trade_id == ledger_trade_id:
        return True
    elif trade_id != ledger_trade_id:
        breaks.append({
            'trade_id': trade_id,
            'break_type': 'trade_id_mismatch',
            'severity': 'high',
            'reconciled': False
        })
        return False

def rate_mismatch(feed_df, ledger_df):
    if rate == ledger_rate: 
        return True
    else:
        breaks.append({
            'trade_id': trade_id,
            'break_type': 'rate_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
        return False

def settlement_date_mismatch(feed_df, ledger_df):
    if settlement_date == ledger_settlement_date:
        return True
    else:
        breaks.append({
            'trade_id': trade_id,
            'break_type': 'settlement_date_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
        return False

def status_mismatch(feed_df, ledger_df):
    if status == ledger_status:
        return True
    else:
        breaks.append({
            'trade_id': trade_id,
            'break_type': 'status_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
        return False

def notional_mismatch(feed_df, ledger_df):
    if notional == ledger_notional:
        return True
    else:
        breaks.append({
            'trade_id': trade_id,
            'break_type': 'notional_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
        return False
'''