import requests
import requests_cache
from datetime import timedelta

HOST = 'https://api.frankfurter.dev/v1'
BASE_USD = '?base=USD'
LATEST = '/latest'
SYMBOLS = '&symbols='


def call_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response
    else:
        return print("Error with API call")

def format_url() -> str: # Format the URL to the currency endpoint (used in get_currencies)
    currencies_url = HOST + LATEST + BASE_USD # USD base, all currencies
      #GBP/EUR
    # TODO: Return GBP/EUR
    return currencies_url

def get_currencies():# (main) Extracts latest rates against USD

    '''
    if url in cache:
        if url.['date'].== datetime.today().strftime(%Y-%m-%d):
            use it
        else:
            see below call
    '''

    frankfurter_cache = requests_cache.install_cache(
        'frankfurter_cache',
        backend='sqlite',           # or 'memory' for dev
        expire_after=86400,         # 24 hours – safe for /latest
        allowable_codes=(200,),
    )



    response = frankfurter_cache.get(call_api(format_url()))
    if response.status_code == 200:

        return print("No cached values")
    else:
        response_currencies = call_api(format_url())
        dict_currency = response_currencies.json()
        rates = dict_currency["rates"]
        list_currency = list(dict_currency.keys())
        #return list_currency
        return (dict_currency)

# Reusable cached session for all Frankfurter API calls
frankfurter_cache = requests_cache.CachedSession(
    'frankfurter_cache',
    backend='sqlite',               # or 'memory' for dev
    expire_after=86400,             # 24 hours – safe for /latest
    allowable_codes=(200,),
)


def get_currencies():  # (main) Extracts latest rates against USD
    """Extract latest rates against USD using a cached Frankfurter session."""

    response = frankfurter_cache.get(format_url())
    if response.status_code != 200:
        print("Error with API call")
        return None

    dict_currency = response.json()
    return dict_currency


if __name__ == "__main__":
    print(get_currencies())
