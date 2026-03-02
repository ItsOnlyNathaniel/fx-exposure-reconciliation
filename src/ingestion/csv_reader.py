import pandas as pd
import numpy as np


# Read CSV into a Pandas dataframe
df = pd.read_csv('trades.csv,', na_values=['N/A', 'missing'])

# Normalise column names 
df.columns = df.columns.str.lower().str.replace(' ', '_')
df.columns = df.columns.str.replace('(', '').str.replace(')', '')

# Parse dates consistently
df['settlement_date'] = pd.to_datetime(df['settlement_date'])
df['created_at'] = pd.to_datetime(df['created_at'])

# Handle basic data quality issues without crashing
df['notional'] = pd.to_numeric(df['notional'], errors='coerce')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
df['status'] = df['status'].str.upper()

# Validate data
if df['notional'].isnull().any():
    raise ValueError("Notional values cannot be null")
if df['rate'].isnull().any():
    raise ValueError("Rate values cannot be null")
if df['status'].isnull().any():
    raise ValueError("Status values cannot be null")