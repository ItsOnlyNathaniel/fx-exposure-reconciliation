import logging
import requests
import requests_cache
from typing import Optional
from datetime import date, datetime
from sqlalchemy.orm import Session

from database.session import get_session
from database.models import Rates

logger = logging.getLogger(__name__)

HOST = "https://api.frankfurter.dev/v1"
LATEST = "/latest"
BASE_PARAM = "base"
TARGETS = "&symbols=GBP,AUD,EUR,CHF,JPY,CAD"

# Reusable cache session for all Frankfurter API calls
frankfurter_cache = requests_cache.CachedSession(
    "data/frankfurter/frankfurter_cache",
    backend="sqlite",
    expire_after=86400,
    allowable_codes=(200,),
)

rate_cache: dict[tuple[str, str, date], float] = {}

def get_currencies(base: str = "USD"): #-> dict:
    """
    Fetch the latest FX rates from Frankfurter against the given base currency.
    """
    url = f"{HOST}{LATEST}?{BASE_PARAM}={base}{TARGETS}" # Format the rates endpoint URL 
    if base == "EUR":
        url += '&symbols=GBP' # For EUR/GBP transactions
    try:
        response = frankfurter_cache.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.exception("Error fetching FX rates from Frankfurter", exc_info=exc)
        return None

def store_rates(rates, db: Session) -> None:
    """Persist fetched rates to SQLite."""
    try:
        fetch_date = date.fromisoformat(rates["date"])
    except ValueError:
        logger.error("Date not found: Invalid value")
    for currency, rate_value in rates["rates"].items():
        existing = db.query(Rates).filter(
            Rates.fetch_date == fetch_date,
            Rates.base_currency == rates["base"],
            Rates.target_currency == currency
        ).first()

        if not existing:
            try:
                new_rate = Rates(  # type: ignore[call-arg]
                    fetch_timestamp=datetime.utcnow(),
                    fetch_date=fetch_date,
                    base_currency=rates["base"],
                    target_currency=currency,
                    rate=rate_value,
                    source="frankfurter",
                )
                db.add(new_rate)
            except Exception as e:
                logger.error("Error %s", e)
                raise

    db.commit()


def get_rate_for_date(db: Session, base: str, target: str, as_of_date: date) -> Optional[float]:
    """Query the most recent rate <= as_of_date."""
    rate = db.query(Rates).filter(
        Rates.base_currency == base,
        Rates.target_currency == target,
        Rates.fetch_date <= as_of_date
    ).order_by(Rates.fetch_date.desc()).first()

    if rate:
        logger.info("Rate returned from cache")
        return rate.rate
    else:
        logger.info("Unable to return rate from cache")
        return None


def get_cached_rate(db: Session, base: str, target: str, as_of: date) -> Optional[float]:
    logger.info("Called get_cache_rate")
    key = (base, target, as_of)
    if key in rate_cache:
        return rate_cache[key]

    rate = get_rate_for_date(db, base, target, as_of)
    if rate is not None:
        rate_cache[key] = rate
    return rate

if __name__ == "__main__":
    print(get_currencies())
