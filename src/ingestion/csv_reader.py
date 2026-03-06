import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, timedelta

# Read CSV into a Pandas dataframe
def read_csv():
    yesterday = date.today() - timedelta(days=1)
    BASE_PATH = Path(__file__).resolve().parents[2]
    DATA_PATH = BASE_PATH / "data" / "synthetic"
    feed_path = DATA_PATH / yesterday.strftime("bank_feed_%Y-%m-%d.csv")
    df = pd.read_csv(feed_path)

    return df

#print(df.head(10))
def parse_csv(df: pd.DataFrame):
    # Normalise column names 
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df.columns = df.columns.str.replace('(', '').str.replace(')', '')

    # Parse dates consistently
    df['settlement_date'] = pd.to_datetime(df['settlement_date'], errors='coerce')
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Handle basic data quality issues without crashing
    df['notional'] = pd.to_numeric(df['notional'], errors='coerce')
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df['status'] = df['status'].str.upper()

    #
    df['currency_pair'] = df['currency_pair'].astype('category')
    df['counterparty'] = df['counterparty'].astype('category')
    df['status'] = df['status'].astype('category')

    # Validate data
    if df['notional'].isnull().any():
        raise ValueError("Notional values cannot be null")
    if df['rate'].isnull().any():
        raise ValueError("Rate values cannot be null")
    if df['status'].isnull().any():
        raise ValueError("Status values cannot be null")

    return df