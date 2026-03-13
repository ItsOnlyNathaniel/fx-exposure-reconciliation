import requests
import requests_cache
from typing import Optional
from datetime import date, datetime
from sqlalchemy.orm import Session

from database.session import get_session
from database.models import Rates

HOST = "https://api.frankfurter.dev/v1"
LATEST = "/latest"
BASE_PARAM = "base"
TARGETS = "&symbols=GBP,AUD,EUR,CHF,JPY,CAD"

db = get_session()

# Reusable cache session for all Frankfurter API calls
frankfurter_cache = requests_cache.CachedSession(
    "frankfurter_cache",
    backend="sqlite",
    expire_after=86400,
    allowable_codes=(200,),
)

rate_cache: dict[tuple[str, str, date], float] = {}

# requests_cache.install_cache('api_cache', expire_after=timedelta(days=1))

def get_currencies(base: str = "USD"): #-> dict:
    """
    Fetch the latest FX rates from Frankfurter against the given base currency.
    """
    url = f"{HOST}{LATEST}?{BASE_PARAM}={base}{TARGETS}" # Format the rates endpoint URL 
    if base == "EUR":
        url += '&symbols=GBP' # For EUR/GBP transactions
    else:
        pass
    #response = requests.get(url)
    response = frankfurter_cache.get(url)
    if response.status_code == 200:
        response.raise_for_status()
        rates = response.json()
        return rates
    else:
        print("Error with API call")
        return None


def store_rates(rates, db: Session) -> None:
    """Persist fetched rates to SQLite."""
    fetch_date = date.fromisoformat(rates["date"])
    for currency, rate_value in rates["rates"].items():
        existing = db.query(Rates).filter(
            Rates.fetch_date == fetch_date,
            Rates.base_currency == rates["base"],
            Rates.target_currency == currency
        ).first()

        if not existing:
            new_rate = Rates(  # type: ignore[call-arg]
                fetch_timestamp=datetime.utcnow(),
                fetch_date=fetch_date,
                base_currency=rates["base"],
                target_currency=currency,
                rate=rate_value,
                source="frankfurter",
            )
            db.add(new_rate)

    db.commit()


def get_rate_for_date(
    db: Session,
    base: str,
    target: str,
    as_of_date: date
) -> Optional[float]:
    """Query the most recent rate <= as_of_date."""
    rate = db.query(Rates).filter(
        Rates.base_currency == base,
        Rates.target_currency == target,
        Rates.fetch_date <= as_of_date
    ).order_by(Rates.fetch_date.desc()).first()

    return rate.rate if rate else None


def get_cached_rate(db: Session, base: str, target: str, as_of: date) -> Optional[float]:
    key = (base, target, as_of)
    if key in rate_cache:
        return rate_cache[key]

    rate = get_rate_for_date(db, base, target, as_of)
    if rate is not None:
        rate_cache[key] = rate
    return rate




if __name__ == "__main__":
    print(get_currencies())


