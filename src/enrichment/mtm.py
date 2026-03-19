import pandas as pd
from typing import Dict, Tuple
from src.enrichment.fx_rates import get_cached_rate
from src.database.session import SessionLocal as get_session

db = get_session()

def main(trades:pd.DataFrame) -> pd.DataFrame:
    """
    Calculate MTM for open/pending positions and add as 'mtm_quote_ccy' column.
    Returns the input DataFrame with new column added (NaN where not applicable).
    """
    open_positions = trades[trades["status"].isin(["OPEN", "PENDING"])].copy()
    open_positions["mtm_value"] = open_positions.apply(lambda row: calculate_mtm_row(row, db), axis=1)


def calculate_mtm_row(row: pd.Series, db):
    """
    Calculate mark-to-market P&L in quote currency for a single trade row.
    """
    try:
        base, quote = row["currency_pair"].split("/")
    except ValueError:
        return None

    rate = get_cached_rate(db, base, quote, row["settlement_date"].date())
    if rate is None:
        return None
    
    notional = row["notional"]
    trade_rate = row["trade_rate"]
    current_value = notional * rate

    if row["side"].upper() == "BUY":
        original_value = notional * trade_rate
        mtm = current_value - original_value
    elif row["side"].upper() == "SELL":
        mtm = notional * (trade_rate - rate)
    else:
        return None
    return round(mtm, 2)

