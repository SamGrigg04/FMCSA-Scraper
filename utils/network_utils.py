import requests
from requests.exceptions import RequestException


def get_json(url, params=None, headers=None, timeout=30, retries=2):
    """
    Do a GET request and return parsed JSON.
    - handles non-200 errors
    - retries if needed with a linear backoff
    """
    session = requests.Session()
    try:
        attempt = 0
        while True:
            try:
                response = session.get(url, params=params, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except RequestException:
                if attempt >= retries: # If we run out of retries
                    raise # Raise an exception
                attempt += 1

                # back off a bit
                import time
                time.sleep(1 + attempt)
    finally:
        session.close()