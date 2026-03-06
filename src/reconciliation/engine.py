import pandas as pd

RATE_TOLERANCE = 0.0001
NOTIONAL_TOLERANCE = 0.01

breaks = pd.DataFrame(columns=['trade_id', 'break_type', 'severity', 'reconciled'])

# Hash lookup solution - O(n + m)
def reconcile_trades(feed_df:pd.DataFrame, ledger_df:pd.DataFrame):

    # Perform an outer merge to find matches and mismatches
    matched = pd.merge(feed_df, ledger_df, on='trade_id', suffixes=("_feed", "_ledger"), how='outer', indicator=True)
    matched_both = matched[matched["_merge"] == "both"].copy()

    # Only keep relevant columns for mismatch analysis
    if matched_both.empty:
        return pd.DataFrame(columns=["trade_id", "break_type"])

    # Calculate mismatches
    matched_both["rate_mismatch"] = (
        matched_both["rate_feed"] - matched_both["rate_ledger"]).abs() > RATE_TOLERANCE
    matched_both["notional_mismatch"] = (
        matched_both["notional_feed"] - matched_both["notional_ledger"]).abs() > NOTIONAL_TOLERANCE
    matched_both["settlement_mismatch"] = (
        matched_both["settlement_date_feed"] != matched_both["settlement_date_ledger"])
    matched_both["status_mismatch"] = (
        matched_both["status_feed"] != matched_both["status_ledger"]    )

    # Classify breaks based on mismatches
    def classify_break(row: pd.Series):
        if row["rate_mismatch"]:
            breaks.concat({
            'trade_id': row['trade_id'],
            'break_type': 'rate_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
            return "RATE_MISMATCH"

        if row["notional_mismatch"]:
            breaks.concat({
            'trade_id': row['trade_id'],
            'break_type': 'notional_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
            return "NOTIONAL_MISMATCH"

        if row["settlement_mismatch"]:
            breaks.concat({
            'trade_id': row['trade_id'],
            'break_type': 'settlement_date_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
            return "TIMING_DIFFERENCE"

        if row["status_mismatch"]:
            breaks.concat({
            'trade_id': row['trade_id'],
            'break_type': 'status_mismatch',
            'severity': 'medium',
            'reconciled': False
        })
            return "STATUS_MISMATCH"
        return None
    
    # Apply classification to each row
    matched_both["break_type"] = matched_both.apply(classify_break, axis=1)
    breaks: pd.DataFrame = matched_both[matched_both["break_type"].notna()].copy()

    return breaks
