import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, Tuple
from src.enrichment.fx_rates import get_cached_rate
from src.database.session import SessionLocal as get_session

logger = logging.getLogger(__name__)

db = get_session()

def main(trades:pd.DataFrame) -> pd.DataFrame:
    """
    Calculate MTM for open/pending positions and add as 'mtm_quote_ccy' column.
    Returns the input DataFrame with new column added (NaN where not applicable).
    """
    try:
        CONFIG_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "counterparty_config.json"
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            counterparty_config = json.load(f)
        return counterparty_config
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.error("Error: ", exc_info=exc)

    open_positions = trades[trades["status"].isin(["OPEN", "PENDING"])].copy()
    open_positions["mtm_value"] = open_positions.apply(lambda row: calculate_mtm_row(row, db), axis=1)
    open_positions.apply(calculate_exposure_and_breaches)
    return open_positions(trades, counterparty_config, db)


def calculate_mtm_row(row: pd.Series, db):
    """
    Calculate mark-to-market P&L in quote currency for a single trade row.
    """
    try:
        base, quote = row["currency_pair"].split("/")
    except ValueError:
        logger.error("Invalid format")
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


def calculate_exposure_and_breaches(trades: pd.DataFrame, counterparty_limits: Dict[str, Dict], db
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    1. Compute current net exposure per counterparty (in quote ccy)
    2. Compare to configured limits and flag breaches/warnings
    Returns:
      - exposure_df: per-counterparty summary (current_exposure, limit, utilisation_pct, status)
      - breaches_df: filtered rows where status is WARNING or BREACH (for logging/alerts)
    """
    exposure_by_cp = (
        trades.groupby("counterparty")["mtm_quote_ccy"]
        .abs().sum()
        .reset_index(name="current_exposure")
    )

    # Join limits
    limits_df = pd.DataFrame.from_dict(
        counterparty_limits, orient="index"
    ).reset_index(names="counterparty")

    merged = exposure_by_cp.merge(limits_df, on="counterparty", how="left")

    # Fill missing limits with infinity or 0 (your choice)
    merged["limit_quote_ccy"] = merged["limit_quote_ccy"].fillna(float("inf"))
    merged["utilisation_pct"] = (merged["current_exposure"] / merged["limit_quote_ccy"]) * 100

    # Breach logic
    def get_status(row):
        if pd.isna(row["limit_quote_ccy"]):
            return "NO_LIMIT"
        pct = row["utilisation_pct"]
        if pct >= 120:
            return "CRITICAL"
        if pct >= 100:
            return "BREACH"
        if pct >= row.get("warning_threshold_pct", 80):
            return "WARNING"
        return "OK"

    merged["status"] = merged.apply(get_status, axis=1)

    # Breaches for logging/alerting
    breaches = merged[merged["status"].isin(["WARNING", "BREACH"])].copy()

    # Log to audit trail (pseudo-code — adapt to your SQLAlchemy models)
    # for _, row in breaches.iterrows():
    #     log_margin_event(db, row["counterparty"], row["current_exposure"], row["status"], ...)

    return merged, breaches