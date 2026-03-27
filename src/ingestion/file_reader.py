import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.models import Trades, TradeSide, TradeStatus

BASE_PATH = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_PATH / "data" / "synthetic"
logger = logging.getLogger(__name__)

def read_json():
    ledger_path = DATA_PATH / datetime.today().strftime("internal_ledger_%Y-%m-%d.json")
    try:
        json = pd.read_json(ledger_path, convert_dates=False)
        logger.info("Read in internal_ledger.json successfully")
        return json
    except FileNotFoundError:
        logger.error("JSON File not found")
    

def read_csv():
    feed_path = DATA_PATH / datetime.today().strftime("bank_feed_%Y-%m-%d.csv")
    try:
        csv = pd.read_csv(feed_path)
        logger.info("Read in bank_feed.csv successfully")
        return csv
    except FileNotFoundError:
        logger.error("CSV file not found")


def parse(df: pd.DataFrame):
    # Normalise column names 
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df.columns = df.columns.str.replace('(', '').str.replace(')', '')

    try:
    # Parse dates consistently
        df['settlement_date'] = pd.to_datetime(df['settlement_date'], errors='coerce')
        df['created_at'] = pd.to_datetime(df['created_at'])

    # Handle basic data quality issues without crashing
        df['notional'] = pd.to_numeric(df['notional'], errors='coerce')
        df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
        df['status'] = df['status'].str.upper()

    # Optimize memory usage by converting to appropriate data types
        df['currency_pair'] = df['currency_pair'].astype('category')
        df['counterparty'] = df['counterparty'].astype('category')
        df['status'] = df['status'].astype('category')
    except ValueError as e:
        logger.error("Invalid field %s", e, exc_info=True)

    # Validate data
    if df['notional'].isnull().any():
        raise ValueError("Notional values cannot be null")
    if df['rate'].isnull().any():
        raise ValueError("Rate values cannot be null")
    if df['status'].isnull().any():
        raise ValueError("Status values cannot be null")
    
    logger.info("DataFrame parsed successfully")
    return df

def store_trades(df: pd.DataFrame, db: Session) -> None:
    """
    Persist normalised trades into the `trades` table, avoiding duplicates.
    """
    for _, row in df.iterrows():
        try:    
            # Ensure we have a proper datetime for settlement_date
            settlement_dt = row["settlement_date"]
            if isinstance(settlement_dt, str):
                settlement_dt = datetime.fromisoformat(settlement_dt)
        except ValueError as e:
            logger.error("Invalid settlement date %s", e)

        # Map status string to TradeStatus enum
        status_str = str(row["status"]).upper()
        try:
            status_enum = TradeStatus[status_str]
        except KeyError:
            logger.error("Unknown status")
            # Skip unknown statuses rather than failing the whole batch
            continue

        currency_pair = str(row["currency_pair"])
        base_ccy, quote_ccy = (None, None)
        if "/" in currency_pair:
            base_ccy, quote_ccy = currency_pair.split("/", 1)

        existing = (
            db.query(Trades)
            .filter(
                Trades.settlement_date == settlement_dt,
                Trades.currency_pair == currency_pair,
                Trades.notional == row["notional"],
                Trades.rate == row["rate"],
                Trades.status == status_enum,
            )
            .first()
        )

        if existing:
            continue
        try:
            new_trade = Trades(  # type: ignore[call-arg]
                # Counterparty linking can be wired up later; for now we
                # default to 0 to satisfy the non-nullable FK.
                counterparty_id=0,
                settlement_date=settlement_dt,
                side=TradeSide.BUY,
                currency_pair=currency_pair,
                base_currency=base_ccy,
                quote_currency=quote_ccy,
                notional=row["notional"],
                rate=row["rate"],
                status=status_enum,
            )
            db.add(new_trade)
        except Exception as e:
            logger.error("Error %s", e)
            raise


    db.commit()