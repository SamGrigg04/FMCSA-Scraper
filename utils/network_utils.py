import requests
from requests.exceptions import RequestException

# Does a GET request and returns the parsed JSON
# Error and retry handling
def get_json(url, params=None, headers=None, timeout=30, retries=2):
    session = requests.Session()
    try:
        attempt = 0
        while True:
            try:
                response = session.get(url, params=params, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except Exception:
                if attempt >= retries: # If we run out of retries
                    raise # Raise an exception
                attempt += 1

                # back off a bit
                import time
                time.sleep(1 + attempt)
    finally:
        session.close()